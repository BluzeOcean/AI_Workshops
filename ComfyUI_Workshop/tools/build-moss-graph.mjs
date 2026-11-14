#!/usr/bin/env node
/**
 * build-moss-graph.mjs - emit an API-format ComfyUI graph for the MOSS-Image
 * t2i workflow, without opening the ComfyUI frontend.
 *
 * WHY A GENERATOR INSTEAD OF HAND-EDITED JSON
 * ------------------------------------------
 * The canvas workflow (`moss_image_t2i_bbox_8_steps.json`) is in FRONTEND
 * format: node ids, link ids, widget arrays, canvas positions. The server
 * only accepts API format: a flat map of node id -> {class_type, inputs},
 * where inputs are either literals or ["sourceNodeId", outputIndex].
 *
 * This script is the SOURCE OF TRUTH for the graph. Edit it here, re-run it,
 * and the JSON it writes is always consistent. A hand-edited 50 KB
 * single-line workflow JSON is not reviewable and drifts silently.
 *
 * WHAT IT REPRODUCES (from the user's canvas workflow, verified 2026-11-13)
 *   UNETLoader            moss_image_sft_bf16.safetensors
 *   LoraLoader            MOSS-Image-8-step\lora.safetensors  (model+clip, 1.0)
 *   CLIPLoader            qwen3.5_9b_bf16.safetensors  type=moss_image
 *   VAELoader             flux2-vae.safetensors
 *   SkipLayerGuidanceDiTSimple  single_layers=22, 0 -> 0.5
 *   KSampler              8 steps, cfg 2.5, er_sde / simple, denoise 1
 *
 * IMPROVEMENTS OVER THE RAW CANVAS WORKFLOW
 *   1. The canvas chain CreateBoundingBoxes -> MOSSImageLayoutPrompt ->
 *      PreviewAny -> CLIPTextEncode.text is a NO-OP for plain t2i, because
 *      the canvas has zero boxes. Here the boxes can be supplied as data
 *      (--layout), which turns the graph into a layout-controlled render:
 *      explicit placement of backdrop and subject, and a `character` label
 *      for the subject box.
 *   2. PreviewAny is a pure passthrough in API format, so it is dropped and
 *      the layout prompt feeds CLIPTextEncode directly.
 *   3. Resolution, seed and filename_prefix are parameters, not canvas state.
 *
 * USAGE
 *   node build-moss-graph.mjs --prompt "..." --out graph.json
 *   node build-moss-graph.mjs --prompt "..." --out graph.json --layout layout.json
 *   node build-moss-graph.mjs --prompt "..." --out graph.json --width 960 --height 1280 --seed 42
 *
 * Then run it:
 *   node D:\ComfyUI\harness\comfyctl.mjs submit graph.json
 */

import { writeFileSync, readFileSync } from 'node:fs'
import path from 'node:path'

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
const argv = process.argv.slice(2)
const arg = (name, fallback = null) => {
  const i = argv.indexOf(`--${name}`)
  if (i === -1) return fallback
  const v = argv[i + 1]
  if (v === undefined || v.startsWith('--')) return true
  return v
}

const prompt   = arg('prompt')
const outPath  = arg('out', 'moss-graph.json')
const layoutIn = arg('layout')
const width    = Number(arg('width', 960))
const height   = Number(arg('height', 1280))
const seed     = Number(arg('seed', Math.floor(Math.random() * 2 ** 48)))
const prefix   = arg('prefix', 'moss_asset')
const negative = arg('negative', '')
const steps    = Number(arg('steps', 8))
const cfg      = Number(arg('cfg', 2.5))

if (!prompt || prompt === true) {
  console.error('usage: build-moss-graph.mjs --prompt "..." --out graph.json [--layout layout.json]')
  process.exitCode = 1
  console.log(buildHelp())
} else {
  const graph = buildGraph({ prompt, width, height, seed, prefix, negative, steps, cfg, layout: loadLayout(layoutIn) })
  writeFileSync(outPath, JSON.stringify(graph, null, 2), 'utf8')
  console.log(`wrote ${outPath}`)
  console.log(`  ${Object.keys(graph).length} nodes | ${width}x${height} | seed ${seed} | prefix "${prefix}"`)
  const hasBoxes = graph['13'].inputs.bboxes
  console.log(`  layout boxes: ${hasBoxes ? 'yes' : 'none'}`)
}

function buildHelp() {
  return [
    'build-moss-graph.mjs - API-format graph for the MOSS-Image t2i workflow',
    '',
    '  --prompt <text>      required',
    '  --out <file>         default moss-graph.json',
    '  --layout <file>      JSON with {boxes:[{x,y,w,h,desc,type}], characterBoxes:[n]}',
    '                      x/y/w/h are FRACTIONS 0..1 of the canvas',
    '  --width <px>         default 960',
    '  --height <px>        default 1280',
    '  --seed <n>           default random',
    '  --prefix <name>      filename prefix for SaveImage',
    '  --negative <text>    default empty',
    '  --steps <n>          default 8',
    '  --cfg <f>            default 2.5',
  ].join('\n')
}

function loadLayout(p) {
  if (!p || p === true) return null
  const raw = readFileSync(p, 'utf8')
  return JSON.parse(raw)
}

// ---------------------------------------------------------------------------
// Graph
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

/** Fraction box -> the element shape CreateBoundingBoxes actually accepts. */
function toElement(box) {
  const el = {
    bbox: fracToBbox(box),
    type: box.type === 'text' ? 'text' : 'obj',
    desc: box.desc ?? '',
  }
  if (box.type === 'text') el.text = box.text ?? ''
  if (box.palette) el.color_palette = box.palette
  return el
}

function buildGraph({ prompt, width, height, seed, prefix, negative, steps, cfg, layout }) {
  const g = {
    // --- models -----------------------------------------------------------
    '1': {
      class_type: 'UNETLoader',
      inputs: { unet_name: 'moss_image_sft_bf16.safetensors', weight_dtype: 'default' },
    },
    '3': {
      class_type: 'CLIPLoader',
      inputs: { clip_name: 'qwen3.5_9b_bf16.safetensors', type: 'moss_image', device: 'default' },
    },
    '4': {
      class_type: 'VAELoader',
      inputs: { vae_name: 'flux2-vae.safetensors' },
    },
    '16': {
      class_type: 'LoraLoader',
      inputs: {
        lora_name: 'MOSS-Image-8-step\\lora.safetensors',
        strength_model: 1.0,
        strength_clip: 1.0,
        model: ['1', 0],
        clip: ['3', 0],
      },
    },
    '2': {
      class_type: 'SkipLayerGuidanceDiTSimple',
      inputs: {
        double_layers: '',
        single_layers: '22',
        start_percent: 0,
        end_percent: 0.5,
        model: ['16', 0],
      },
    },

    // --- layout -----------------------------------------------------------
    // '13' -> '12' -> '5'.text
    //
    // editor_state is a BOUNDING_BOXES (list) input. ComfyUI's validator
    // treats ANY list as a node link, so a literal list must be wrapped:
    //   editor_state: { "__value__": [] }
    // A bare [] is rejected with
    //   "Bad linked input, must be a length-2 list of [node_id, slot_index]"
    //
    // The boxes themselves must be ELEMENTS - {"bbox":[y0,x0,y1,x1]} in 0..1000
    // with Y FIRST - because a plain {x,y,width,height} box carries no caption
    // and the caption is the whole point of a layout box.
    '13': {
      class_type: 'CreateBoundingBoxes',
      inputs: {
        width,
        height,
        editor_state: { __value__: [] },
        bboxes: layout && layout.boxes && layout.boxes.length
          ? JSON.stringify(layout.boxes.map(toElement))
          : '',
      },
    },
    '12': {
      class_type: 'MOSSImageLayoutPrompt',
      inputs: {
        prompt,
        element: ['13', 2],
        width,
        height,
        character_boxes: layout && layout.characterBoxes
          ? layout.characterBoxes.join(',')
          : '',
      },
    },

    // --- conditioning -----------------------------------------------------
    '5': {
      class_type: 'CLIPTextEncode',
      inputs: { text: ['12', 0], clip: ['16', 1] },
    },
    '6': {
      class_type: 'CLIPTextEncode',
      inputs: { text: negative, clip: ['16', 1] },
    },

    // --- sampling ---------------------------------------------------------
    '7': {
      class_type: 'EmptyFlux2LatentImage',
      inputs: { width, height, batch_size: 1 },
    },
    '8': {
      class_type: 'KSampler',
      inputs: {
        seed,
        steps,
        cfg,
        sampler_name: 'er_sde',
        scheduler: 'simple',
        denoise: 1,
        model: ['2', 0],
        positive: ['5', 0],
        negative: ['6', 0],
        latent_image: ['7', 0],
      },
    },
    '9': {
      class_type: 'VAEDecode',
      inputs: { samples: ['8', 0], vae: ['4', 0] },
    },
    '10': {
      class_type: 'SaveImage',
      inputs: { filename_prefix: prefix, images: ['9', 0] },
    },
  }
  return g
}
