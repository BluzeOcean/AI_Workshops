#!/usr/bin/env node
/**
 * build-moss-edit-set.mjs - emit ONE API-format ComfyUI graph that renders a SET of
 * VARIATIONS OF A REFERENCE IMAGE with MOSS-Image + the MOSS-Image edit LoRA.
 *
 * WHY THIS EXISTS
 * ---------------
 * The plain t2i chain (build-moss-set.mjs) can only ever build a machine from
 * words. Asking it for "the same model as this picture" produces a machine that
 * merely LOOKS like the picture in one attribute - round 07 copied the palette,
 * round 08 copied the art style, round 09 copied the design by hand - and the
 * user rejected all three with "not the sample".
 *
 * MOSS-Image ships an instruction-edit LoRA and ComfyUI has native support for
 * it (PR #17296, in ComfyUI >= 0.42.1):
 *
 *   TextEncodeMOSSImageEdit  - encodes an edit instruction TOGETHER WITH the
 *                              reference image; the reference reaches the DiT as
 *                              reference latents.
 *   LoraLoaderModelOnly     - loads the edit LoRA on the diffusion model.
 *
 * With that, the reference image is the actual source of the design, and the
 * prompt says what to CHANGE. That is a different mechanism from prompting.
 *
 * THE GRAPH (shared nodes - loaded once for the whole set)
 *   UNETLoader                moss_image_sft_bf16.safetensors
 *   LoraLoaderModelOnly       MOSS-Image-Edit\moss_image_edit_lora_rank_64_bf16.safetensors
 *   CLIPLoader                qwen3.5_9b_bf16.safetensors  type=moss_image
 *   VAELoader                 flux2-vae.safetensors
 *   SkipLayerGuidanceDiTSimple  single_layers 22, 0 -> 1
 *   LoadImage                 the reference
 *   ImageScaleToTotalPixels   scale to the target size, aligned to 16 px
 *   GetImageSize              -> EmptyFlux2LatentImage (output == reference size)
 *   TextEncodeMOSSImageEdit   NEGATIVE
 *   then one branch per concept:
 *     TextEncodeMOSSImageEdit (positive) -> KSampler -> VAEDecode -> SaveImage
 *
 * THREE THINGS THAT WILL BREAK THIS IF YOU GET THEM WRONG
 *   1. THE REFERENCE AND THE OUTPUT MUST BE THE SAME SIZE. The edit LoRA was
 *      trained with source and target at one size; with a smaller reference the
 *      scene zooms out and the edit fails. Hence ImageScaleToTotalPixels +
 *      GetImageSize driving the latent, rather than a fixed latent size.
 *   2. THE INSTRUCTION MUST FOLLOW THE TRAINING PHRASING. The LoRA was
 *      trained on "Change only the X to Y. Keep <list> unchanged." - describe
 *      ONLY the change, then list what must survive it.
 *   3. edit_format MUST MATCH THE LORA. "Moss-Image-Edit" for the chinoll /
 *      Comfy-Org rehost; "ai-toolkit" or "ai-toolkit (kv_cache off)" for LoRAs
 *      trained with ai-toolkit. The format decides where the reference lands in
 *      the token stream - wrong format = no reference at all.
 *
 * USAGE
 *   node build-moss-edit-set.mjs --recipe <recipe.json> --out <graph.json>
 *
 * Then:
 *   node D:\ComfyUI\harness\comfyctl.mjs submit <graph.json>
 */

import { writeFileSync, readFileSync } from 'node:fs'

const argv = process.argv.slice(2)
const arg = (name, fallback = null) => {
  const i = argv.indexOf(`--${name}`)
  if (i === -1) return fallback
  const v = argv[i + 1]
  if (v === undefined || v.startsWith('--')) return true
  return v
}

const recipePath = arg('recipe')
const outPath = arg('out', 'moss-edit-set.json')

if (!recipePath || recipePath === true) {
  console.error('usage: build-moss-edit-set.mjs --recipe <recipe.json> --out <graph.json>')
  process.exitCode = 1
} else {
  const recipe = JSON.parse(readFileSync(recipePath, 'utf8'))
  const graph = buildEditSet(recipe)
  writeFileSync(outPath, JSON.stringify(graph, null, 2), 'utf8')
  // The sidecar name must NEVER equal the graph name.
  const metaPath = outPath.endsWith('.json')
    ? outPath.replace(/\.json$/, '.meta.json')
    : `${outPath}.meta.json`
  writeFileSync(metaPath, JSON.stringify({
    recipe: recipePath,
    reference: recipe.reference,
    concepts: recipe.concepts.length,
    width: recipe.width ?? 960,
    height: recipe.height ?? 1280,
    steps: recipe.steps ?? 30,
    cfg: recipe.cfg ?? 4.0,
    sampler: recipe.sampler ?? 'euler',
    scheduler: recipe.scheduler ?? 'normal',
    edit_format: recipe.edit_format ?? 'Moss-Image-Edit',
    prefix: recipe.prefix ?? 'moss_edit',
    nodes: Object.keys(graph).length,
    seeds: recipe.concepts.map((c) => ({ name: c.name, seed: c.seed })),
  }, null, 2), 'utf8')
  console.log(`wrote ${outPath}`)
  console.log(`  ${recipe.concepts.length} concepts | ${recipe.width ?? 960}x${recipe.height ?? 1280} | ${Object.keys(graph).length} nodes`)
  console.log(`  reference: ${recipe.reference}`)
  for (const c of recipe.concepts) {
    console.log(`   - ${c.name}  seed ${c.seed}`)
  }
}

// ---------------------------------------------------------------------------

function buildEditSet(recipe) {
  const W = recipe.width ?? 960
  const H = recipe.height ?? 1280
  const steps = recipe.steps ?? 30
  const cfg = recipe.cfg ?? 4.0
  const sampler = recipe.sampler ?? 'euler'
  const scheduler = recipe.scheduler ?? 'normal'
  const editFormat = recipe.edit_format ?? 'Moss-Image-Edit'
  const imageStrength = recipe.image_strength ?? 1.0
  const negative = recipe.negative ?? 'nsfw, worst quality, bad anatomy, watermark, jpeg artifact'
  const prefix = recipe.prefix ?? 'moss_edit'

  // The reference and the output MUST be the same size. ImageScaleToTotalPixels
  // scales to `megapixels` and then snaps to multiples of `resolution_steps`.
  // Solving megapixels from the TARGET size makes a source of the target size
  // come out of the node unchanged.
  const megapixels = recipe.megapixels ?? (W * H) / (1024 * 1024)
  const resolutionSteps = recipe.resolution_steps ?? 16

  const g = {
    // --- models ------------------------------------------------------------
    '1': {
      class_type: 'UNETLoader',
      inputs: { unet_name: recipe.unet ?? 'moss_image_sft_bf16.safetensors', weight_dtype: 'default' },
    },
    '2': {
      class_type: 'LoraLoaderModelOnly',
      inputs: {
        lora_name: recipe.lora ?? 'MOSS-Image-Edit\\moss_image_edit_lora_rank_64_bf16.safetensors',
        strength_model: 1.0,
        model: ['1', 0],
      },
    },
    '3': {
      class_type: 'CLIPLoader',
      inputs: { clip_name: recipe.clip ?? 'qwen3.5_9b_bf16.safetensors', type: 'moss_image', device: 'default' },
    },
    '4': {
      class_type: 'VAELoader',
      inputs: { vae_name: recipe.vae ?? 'flux2-vae.safetensors' },
    },
    '5': {
      class_type: 'SkipLayerGuidanceDiTSimple',
      inputs: { double_layers: '', single_layers: '22', start_percent: 0, end_percent: 1, model: ['2', 0] },
    },

    // --- the reference -----------------------------------------------------
    // LoadImage resolves "name.png [output]" against the ComfyUI OUTPUT
    // directory and "name.png [input]" against the INPUT directory, so a
    // reference that already lives in the destination can be used without
    // copying it into the input folder.
    '6': {
      class_type: 'LoadImage',
      inputs: { image: recipe.reference },
    },
    '7': {
      class_type: 'ImageScaleToTotalPixels',
      inputs: {
        image: ['6', 0],
        upscale_method: 'lanczos',
        megapixels,
        resolution_steps: resolutionSteps,
      },
    },
    '8': {
      class_type: 'GetImageSize',
      inputs: { image: ['7', 0] },
    },
    '9': {
      class_type: 'EmptyFlux2LatentImage',
      inputs: { width: ['8', 0], height: ['8', 1], batch_size: 1 },
    },

    // --- one shared negative ------------------------------------------------
    // The reference goes into the negative too, so CFG compares like with like.
    '10': {
      class_type: 'TextEncodeMOSSImageEdit',
      inputs: {
        clip: ['3', 0],
        prompt: negative,
        vae: ['4', 0],
        edit_format: editFormat,
        'images.image_0': ['7', 0],
        image_strength: imageStrength,
      },
    },
  }

  // --- per-concept reference overrides --------------------------------------
  // A concept may name its own reference with "reference": "<file> [output]".
  //
  // WHY THIS EXISTS: the magnitude of the edit decides how much of the
  // reference survives. A surface edit (a new livery) or a single-part edit (swap
  // one weapon) keeps the reference almost intact. A STRUCTURAL edit - sweeping the
  // dorsal fins back, replacing a limb - is the one most likely to make the model
  // redraw the whole machine, and then the new design is its own, not the
  // reference's. When the target structure is far from the reference's, point the
  // concept at a reference that ALREADY has that structure, and the model edits a
  // near-match instead of inventing one.
  //
  // The flip side: never point an edit at a reference and ask for something the
  // reference ALREADY IS. r04_02 is a bipedal mech, and an instruction to "make it
  // stand on two legs instead of four" left the model with no edit to make, so it
  // invented a new machine.
  //
  // Each override gets its own scale + size + latent chain, so its output size
  // follows its own reference.
  const refChains = new Map([[recipe.reference, { scale: '7', size: '8', latent: '9' }]])
  let chainId = 300

  const chainFor = (ref) => {
    if (refChains.has(ref)) return refChains.get(ref)
    const load = String(chainId++)
    const scale = String(chainId++)
    const size = String(chainId++)
    const latent = String(chainId++)
    g[load] = { class_type: 'LoadImage', inputs: { image: ref } }
    g[scale] = {
      class_type: 'ImageScaleToTotalPixels',
      inputs: { image: [load, 0], upscale_method: 'lanczos', megapixels, resolution_steps: resolutionSteps },
    }
    g[size] = { class_type: 'GetImageSize', inputs: { image: [scale, 0] } }
    g[latent] = { class_type: 'EmptyFlux2LatentImage', inputs: { width: [size, 0], height: [size, 1], batch_size: 1 } }
    const chain = { scale, size, latent }
    refChains.set(ref, chain)
    return chain
  }

  // --- one branch per concept ----------------------------------------------
  recipe.concepts.forEach((c, i) => {
    const b = 100 + i * 10
    const chain = chainFor(c.reference ?? recipe.reference)

    g[String(b + 0)] = {
      class_type: 'TextEncodeMOSSImageEdit',
      inputs: {
        clip: ['3', 0],
        prompt: c.instruction,
        vae: ['4', 0],
        edit_format: editFormat,
        // The autogrow slot is image_0, NOT image_1. ComfyUI's autogrow
        // template numbers its slots from 0 and min=1 makes slot 0 REQUIRED:
        // posting only images.image_1 is rejected with
        //   required_input_missing / "image_0" / input_name "images.image_0"
        // and the whole graph is refused before anything runs.
        'images.image_0': [chain.scale, 0],
        image_strength: imageStrength,
      },
    }
    g[String(b + 1)] = {
      class_type: 'KSampler',
      inputs: {
        seed: c.seed,
        steps, cfg,
        sampler_name: sampler,
        scheduler,
        denoise: 1,
        model: ['5', 0],
        positive: [String(b + 0), 0],
        negative: ['10', 0],
        latent_image: [chain.latent, 0],
      },
    }
    g[String(b + 2)] = {
      class_type: 'VAEDecode',
      inputs: { samples: [String(b + 1), 0], vae: ['4', 0] },
    }
    g[String(b + 3)] = {
      class_type: 'SaveImage',
      inputs: { filename_prefix: `${prefix}_${c.name}`, images: [String(b + 2), 0] },
    }
  })

  // The graph dict must contain NOTHING but node entries - ComfyUI's server
  // iterates every value and reads "class_type" from it.
  return g
}
