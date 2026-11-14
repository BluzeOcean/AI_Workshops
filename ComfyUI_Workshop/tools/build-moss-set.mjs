#!/usr/bin/env node
/**
 * build-moss-set.mjs - emit ONE API-format ComfyUI graph that renders a SET of
 * concept images from the MOSS-Image model, in a single submission.
 *
 * WHY ONE GRAPH FOR THE WHOLE SET
 * --------------------------------
 * The UNET, the LoRA, the CLIP and the VAE are shared nodes, so ComfyUI loads
 * them once. Ten KSampler branches then run back to back against the same
 * loaded model. Ten separate submissions would reload a 9.7 GB UNET and a
 * 1.1 GB LoRA ten times.
 *
 * Each concept gets its own:
 *   - prompt (the layout summary caption)
 *   - layout boxes (where the subject sits in the frame)
 *   - seed
 *   - filename prefix (so the files are named, not numbered)
 *   - optional styleSuffix override (the shared one is used otherwise)
 *
 * Everything else - model, sampler settings, negative prompt, latent - is
 * shared, so the whole set stays visually consistent, which is the point of a
 * concept set.
 *
 * USAGE
 *   node build-moss-set.mjs --recipe .vault\recipes\<file>.json --out work\set.json
 *
 * Then:
 *   node D:\ComfyUI\harness\comfyctl.mjs submit work\set.json
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
const outPath    = arg('out', 'moss-set.json')

if (!recipePath || recipePath === true) {
  console.error('usage: build-moss-set.mjs --recipe <recipe.json> --out <graph.json>')
  process.exitCode = 1
} else {
  const recipe = JSON.parse(readFileSync(recipePath, 'utf8'))
  const graph = buildSet(recipe)
  writeFileSync(outPath, JSON.stringify(graph, null, 2), 'utf8')
  // Sidecar metadata - the graph file itself must hold node entries only.
  //
  // The sidecar name must NEVER equal the graph name. A plain
  // outPath.replace(/\.json$/, '.meta.json') silently returns outPath unchanged
  // when the output path does not end in ".json" (e.g. "set.json.graph"), and the
  // metadata write then OVERWRITES the graph with a 373-byte sidecar. The submit
  // then fails with a confusing error that looks like a ComfyUI problem.
  const metaPath = outPath.endsWith('.json')
    ? outPath.replace(/\.json$/, '.meta.json')
    : `${outPath}.meta.json`
  writeFileSync(metaPath, JSON.stringify({
    recipe: recipePath,
    concepts: recipe.concepts.length,
    width: recipe.width ?? 960,
    height: recipe.height ?? 1280,
    steps: recipe.steps ?? 8,
    cfg: recipe.cfg ?? 2.5,
    prefix: recipe.prefix ?? 'moss_asset',
    nodes: Object.keys(graph).length,
    seeds: recipe.concepts.map((c) => ({ name: c.name, seed: c.seed })),
  }, null, 2), 'utf8')
  console.log(`wrote ${outPath}`)
  console.log(`  ${recipe.concepts.length} concepts | ${recipe.width ?? 960}x${recipe.height ?? 1280} | ${Object.keys(graph).length} nodes`)
  for (const c of recipe.concepts) {
    console.log(`   - ${c.name}  seed ${c.seed}`)
  }
}

// ---------------------------------------------------------------------------

/**
 * Convert a human-readable fraction box {x,y,w,h} (0..1) into the element
 * bbox the node wants: [y0, x0, y1, x1] in 0..1000, Y FIRST.
 */
function fracToBbox(box) {
  const g = (v) => Math.max(0, Math.min(1000, Math.round(v * 1000)))
  const x0 = g(box.x ?? 0)
  const y0 = g(box.y ?? 0)
  const x1 = g((box.x ?? 0) + (box.w ?? 0))
  const y1 = g((box.y ?? 0) + (box.h ?? 0))
  return [Math.min(y0, y1), Math.min(x0, x1), Math.max(y0, y1), Math.max(x0, x1)]
}

/**
 * Join prompt layers into one clean paragraph.
 *
 * The HEAD (shared prefix + the concept itself) is one grammatical unit and
 * must not be split: "A concept-art study of" + "a six-legged walker" is a
 * sentence, and putting a period between them gives
 * "A concept-art study of. a six-legged walker".
 *
 * Every layer after the head is a separate clause and gets exactly one
 * separator. The shared styleSuffix starts with a period, so a leading one is
 * stripped to avoid "readable text.. Standing on ...".
 */
function joinLayers(head, ...parts) {
  let out = String(head ?? '').trim()
  for (const raw of parts) {
    if (!raw) continue
    let s = String(raw).trim()
    if (!s) continue
    if (out && !/[.!?]$/.test(out)) out += '.'
    s = s.replace(/^[.\s]+/, '')
    out += ' ' + s
  }
  return out
}

function buildSet(recipe) {  const W = recipe.width ?? 960
  const H = recipe.height ?? 1280
  const steps = recipe.steps ?? 8
  const cfg = recipe.cfg ?? 2.5
  const negative = recipe.negative ?? ''
  const prefix = recipe.prefix ?? 'moss_asset'

  // ---- shared nodes -------------------------------------------------------
  const g = {
    '1': { class_type: 'UNETLoader', inputs: { unet_name: 'moss_image_sft_bf16.safetensors', weight_dtype: 'default' } },
    '3': { class_type: 'CLIPLoader', inputs: { clip_name: 'qwen3.5_9b_bf16.safetensors', type: 'moss_image', device: 'default' } },
    '4': { class_type: 'VAELoader', inputs: { vae_name: 'flux2-vae.safetensors' } },
    '16': {
      class_type: 'LoraLoader',
      inputs: {
        lora_name: 'MOSS-Image-8-step\\lora.safetensors',
        strength_model: 1.0, strength_clip: 1.0,
        model: ['1', 0], clip: ['3', 0],
      },
    },
    '2': {
      class_type: 'SkipLayerGuidanceDiTSimple',
      inputs: { double_layers: '', single_layers: '22', start_percent: 0, end_percent: 0.5, model: ['16', 0] },
    },
    // one shared negative conditioning and one shared empty latent
    '6': { class_type: 'CLIPTextEncode', inputs: { text: negative, clip: ['16', 1] } },
    '7': { class_type: 'EmptyFlux2LatentImage', inputs: { width: W, height: H, batch_size: 1 } },
  }

  // ---- one branch per concept --------------------------------------------
  recipe.concepts.forEach((c, i) => {
    const b = 100 + i * 10
    // Box captions may be written as the tokens BACKDROP / SUBJECT, which are
    // filled in from the recipe. That keeps ten sets of boxes readable instead
    // of repeating the same backdrop caption ten times.
    //
    // Recipes are written in human fractions {x,y,w,h} (0..1). The node wants
    // ELEMENTS: {"bbox":[y0,x0,y1,x1]} in 0..1000 with y FIRST. The node
    // detects the format itself: a dict with a 4-number "bbox" is an element,
    // a dict with x/y/width/height is a plain box (and carries no caption,
    // so the caption would be silently lost).
    const boxes = (c.layout?.boxes ?? []).map((box) => {
      const desc = box.desc === 'BACKDROP'
        ? (recipe.backdropDesc ?? box.desc)
        : box.desc === 'SUBJECT'
          ? (c.subject ?? c.prompt)
          : box.desc
      const el = {
        bbox: fracToBbox(box),
        type: box.type === 'text' ? 'text' : 'obj',
        desc,
      }
      if (box.type === 'text') el.text = box.text ?? ''
      if (box.palette) el.color_palette = box.palette
      return el
    })
    const chars = c.layout?.characterBoxes ?? []

    g[String(b + 0)] = {
      class_type: 'CreateBoundingBoxes',
      inputs: {
        width: W, height: H,
        // A list literal MUST be wrapped as {"__value__": [...]}. ComfyUI's
        // validator treats ANY list as a node link, so a bare [] is read as a
        // malformed link and rejected with
        //   "Bad linked input, must be a length-2 list of [node_id, slot_index]"
        // The wrapper is the documented way to pass a literal list to a
        // list-typed input (see ComfyUI execution.py, validate_inputs).
        editor_state: { __value__: [] },
        bboxes: boxes.length ? JSON.stringify(boxes) : '',
      },
    }
    g[String(b + 1)] = {
      class_type: 'MOSSImageLayoutPrompt',
      inputs: {
        // Prompt = shared prefix + the concept itself + its rune layer +
        // the shared rune style + the shared style tail.
        // Keeping the layers separate is what makes a round-over-round
        // comparison honest: only the layer that changed actually changed.
        // The prefix and the concept form ONE head - they are not separated.
        prompt: joinLayers(
          `${(recipe.promptPrefix ?? '').trim()} ${(c.prompt ?? '').trim()}`,
          c.runes,
          recipe.runeStyle,
          // A concept may override the shared styleSuffix. This is how a probe
          // renders several variants of ONE concept in a single submission
          // (one model load) with the wording as the only variable. A recipe
          // with no per-concept styleSuffix behaves exactly as before.
          c.styleSuffix ?? recipe.styleSuffix,
        ),
        element: [String(b + 0), 2],
        width: W, height: H,
        character_boxes: chars.join(','),
      },
    }
    g[String(b + 2)] = {
      class_type: 'CLIPTextEncode',
      inputs: { text: [String(b + 1), 0], clip: ['16', 1] },
    }
    g[String(b + 3)] = {
      class_type: 'KSampler',
      inputs: {
        seed: c.seed,
        steps, cfg,
        sampler_name: 'er_sde', scheduler: 'simple', denoise: 1,
        model: ['2', 0],
        positive: [String(b + 2), 0],
        negative: ['6', 0],
        latent_image: ['7', 0],
      },
    }
    g[String(b + 4)] = {
      class_type: 'VAEDecode',
      inputs: { samples: [String(b + 3), 0], vae: ['4', 0] },
    }
    g[String(b + 5)] = {
      class_type: 'SaveImage',
      inputs: { filename_prefix: `${prefix}_${c.name}`, images: [String(b + 4), 0] },
    }
  })

  // NOTE: the graph dict must contain NOTHING but node entries.
  // ComfyUI's server.py does `for node_id, node_struct in prompt.items()` and
  // then `"class_type" not in node_struct` on every value - so a stray
  // metadata key (a number, a string) crashes the request with
  // "TypeError: argument of type 'int' is not iterable" and a bare 500.
  // Metadata goes to a sidecar file instead.
  return g
}
