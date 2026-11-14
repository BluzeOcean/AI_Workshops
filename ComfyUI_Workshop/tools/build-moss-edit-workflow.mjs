// Build a SIMPLE ComfyUI canvas workflow for the MOSS image-EDIT path.
//
// One reference image in, one prompt in, one image out:
//
//   LoadImage -> ImageScaleToTotalPixels -> GetImageSize -> EmptyFlux2LatentImage
//   UNET -> EditLoRA -> SkipLayerGuidance -> KSampler -> VAEDecode -> SaveImage
//   CLIP/VAE + PROMPT + NEGATIVE (both TextEncodeMOSSImageEdit, both carrying the reference)
//
// The canvas format has three traps that silently break a workflow in the UI:
//   1. a node's `inputs` array must list EVERY slot the frontend builds, in order -
//      including OPTIONAL slots (vae) and autogrow growth slots (images.image_1).
//      Leave one out and every link below it lands on the wrong input.
//   2. `widgets_values` is POSITIONAL and must match the frontend's widget order.
//      A KSampler's seed carries a `control_after_generate` widget right after it.
//   3. a link's dstSlot is an INDEX into the node's real slot list.
//
// `work/validate-canvas.mjs` checks all three against the live node schema.
//
// Usage:
//   node tools\build-moss-edit-workflow.mjs --recipe <recipe.json> \
//        --out-workflow <path.json> [--reference <file>] [--concept <name>] [--seed <n>]

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, basename } from 'node:path';

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => {
  const i = argv.indexOf(`--${name}`);
  return i === -1 ? fallback : argv[i + 1];
};

const recipePath = arg('recipe');
const outWorkflow = arg('out-workflow');
const outGraph = arg('out-graph');
if (!recipePath || !outWorkflow) {
  console.error('usage: --recipe <file> --out-workflow <file> [--out-graph <file>] [--reference <file>] [--concept <name>] [--seed <n>]');
  process.exit(2);
}

const recipe = JSON.parse(readFileSync(recipePath, 'utf8'));
const conceptName = arg('concept');
const concept =
  (conceptName && recipe.concepts.find((c) => c.name === conceptName)) || recipe.concepts[0];
const reference = arg('reference') || recipe.reference;
const seed = arg('seed') ? Number(arg('seed')) : concept.seed;

const W = recipe.width ?? 960;
const H = recipe.height ?? 1280;
const MEGAPIXELS = recipe.megapixels ?? (W * H) / (1024 * 1024);
const UNET = recipe.unet ?? 'moss_image_sft_bf16.safetensors';
const LORA = recipe.lora ?? 'MOSS-Image-Edit\\moss_image_edit_lora_rank_64_bf16.safetensors';
const CLIP = recipe.clip ?? 'qwen3.5_9b_bf16.safetensors';
const VAE = recipe.vae ?? 'flux2-vae.safetensors';
const STEPS = recipe.steps ?? 30;
const CFG = recipe.cfg ?? 4.0;
const SAMPLER = recipe.sampler ?? 'euler';
const SCHEDULER = recipe.scheduler ?? 'normal';
const EDIT_FORMAT = recipe.edit_format ?? 'Moss-Image-Edit';
const IMAGE_STRENGTH = recipe.image_strength ?? 1.0;
const PREFIX = arg('prefix') ?? `${recipe.prefix ?? 'moss_mech'}_${concept.name}`;

// ---------------------------------------------------------------------------
// Canvas helpers
// ---------------------------------------------------------------------------

const nodes = [];
const links = [];
let linkId = 1;

const addNode = (id, spec) => {
  nodes.push({
    id,
    type: spec.type,
    pos: spec.pos,
    size: spec.size ?? [340, 120],
    flags: {},
    order: spec.order,
    mode: 0,
    inputs: spec.inputs ?? [],
    outputs: spec.outputs ?? [],
    ...(spec.title ? { title: spec.title } : {}),
    properties: { 'Node name for S&R': spec.type },
    widgets_values: spec.widgets ?? [],
    widgets_values_named: spec.widgetsNamed ?? {},
  });
};

const link = (srcId, srcSlot, dstId, dstSlot, type) => {
  const id = linkId++;
  links.push([id, srcId, srcSlot, dstId, dstSlot, type]);
  return id;
};

const inS = (name, type, linkIdValue) => ({ name, type, link: linkIdValue });
const outS = (name, type, links) => ({ name, type, links });

// ---------------------------------------------------------------------------
// The graph
// ---------------------------------------------------------------------------

// --- loaders ---------------------------------------------------------------
const unetToLora = link(1, 0, 2, 0, 'MODEL');
const loraToSkip = link(2, 0, 3, 0, 'MODEL');
const skipToSampler = link(3, 0, 12, 0, 'MODEL');

addNode(1, {
  type: 'UNETLoader',
  order: 0,
  pos: [-1180, 0],
  size: [340, 82],
  outputs: [outS('MODEL', 'MODEL', [unetToLora])],
  widgets: [UNET, 'default'],
  widgetsNamed: { unet_name: UNET, weight_dtype: 'default' },
});

addNode(2, {
  type: 'LoraLoaderModelOnly',
  order: 1,
  pos: [-1180, 130],
  size: [340, 130],
  inputs: [inS('model', 'MODEL', unetToLora)],
  outputs: [outS('MODEL', 'MODEL', [loraToSkip])],
  widgets: [LORA, 1.0],
  widgetsNamed: { lora_name: LORA, strength_model: 1.0 },
});

addNode(3, {
  type: 'SkipLayerGuidanceDiTSimple',
  order: 2,
  pos: [-1180, 310],
  size: [340, 130],
  inputs: [inS('model', 'MODEL', loraToSkip)],
  outputs: [outS('MODEL', 'MODEL', [skipToSampler])],
  widgets: ['', '22', 0, 1],
  widgetsNamed: { double_layers: '', single_layers: '22', start_percent: 0, end_percent: 1 },
});

addNode(4, {
  type: 'CLIPLoader',
  order: 3,
  pos: [-1180, 490],
  size: [340, 110],
  outputs: [outS('CLIP', 'CLIP', [])],
  widgets: [CLIP, 'moss_image', 'default'],
  widgetsNamed: { clip_name: CLIP, type: 'moss_image', device: 'default' },
});

addNode(5, {
  type: 'VAELoader',
  order: 4,
  pos: [-1180, 640],
  size: [340, 82],
  outputs: [outS('VAE', 'VAE', [])],
  widgets: [VAE],
  widgetsNamed: { vae_name: VAE },
});

// --- the reference ---------------------------------------------------------
const refToScale = link(6, 0, 7, 0, 'IMAGE');
const scaleToSize = link(7, 0, 8, 0, 'IMAGE');
const sizeToLatentW = link(8, 0, 9, 0, 'INT');
const sizeToLatentH = link(8, 1, 9, 1, 'INT');

addNode(6, {
  type: 'LoadImage',
  order: 5,
  pos: [-780, 0],
  size: [340, 314],
  title: 'REFERENCE IMAGE',
  outputs: [outS('IMAGE', 'IMAGE', [refToScale]), outS('MASK', 'MASK', [])],
  widgets: [reference],
  widgetsNamed: { image: reference },
});

addNode(7, {
  type: 'ImageScaleToTotalPixels',
  order: 6,
  pos: [-780, 360],
  size: [340, 110],
  inputs: [inS('image', 'IMAGE', refToScale)],
  outputs: [outS('IMAGE', 'IMAGE', [scaleToSize])],
  widgets: ['lanczos', MEGAPIXELS, recipe.resolution_steps ?? 16],
  widgetsNamed: {
    upscale_method: 'lanczos',
    megapixels: MEGAPIXELS,
    resolution_steps: recipe.resolution_steps ?? 16,
  },
});

addNode(8, {
  type: 'GetImageSize',
  order: 7,
  pos: [-780, 520],
  size: [340, 82],
  inputs: [inS('image', 'IMAGE', scaleToSize)],
  outputs: [outS('WIDTH', 'INT', [sizeToLatentW]), outS('HEIGHT', 'INT', [sizeToLatentH])],
});

addNode(9, {
  type: 'EmptyFlux2LatentImage',
  order: 8,
  pos: [-780, 650],
  size: [340, 82],
  inputs: [inS('width', 'INT', sizeToLatentW), inS('height', 'INT', sizeToLatentH)],
  outputs: [outS('LATENT', 'LATENT', [])],
  widgets: [1],
  widgetsNamed: { batch_size: 1 },
});

// --- the two text encoders -------------------------------------------------
// TextEncodeMOSSImageEdit slot layout, from the node def:
//   0 clip | 1 images.image_0 | 2 images.image_1 (empty growth slot) | 3 vae
// `vae` is an OPTIONAL input - the UI hides it behind "Show advanced inputs", but
// it still owns slot 3. Both encoders carry the reference: the edit LoRA needs the
// reference in every conditioning it produces.
const clipToPos = link(4, 0, 10, 0, 'CLIP');
const refToPos = link(7, 0, 10, 1, 'IMAGE');
const vaeToPos = link(5, 0, 10, 3, 'VAE');
const clipToNeg = link(4, 0, 11, 0, 'CLIP');
const refToNeg = link(7, 0, 11, 1, 'IMAGE');
const vaeToNeg = link(5, 0, 11, 3, 'VAE');

addNode(10, {
  type: 'TextEncodeMOSSImageEdit',
  order: 9,
  pos: [-360, 0],
  size: [520, 460],
  title: 'PROMPT  (type your instruction here)',
  inputs: [
    inS('clip', 'CLIP', clipToPos),
    inS('images.image_0', 'IMAGE', refToPos),
    inS('images.image_1', 'IMAGE', null),
    inS('vae', 'VAE', vaeToPos),
  ],
  outputs: [outS('CONDITIONING', 'CONDITIONING', [])],
  widgets: [concept.instruction, EDIT_FORMAT, IMAGE_STRENGTH],
  widgetsNamed: { prompt: concept.instruction, edit_format: EDIT_FORMAT, image_strength: IMAGE_STRENGTH },
});

addNode(11, {
  type: 'TextEncodeMOSSImageEdit',
  order: 10,
  pos: [-360, 520],
  size: [520, 420],
  title: 'NEGATIVE',
  inputs: [
    inS('clip', 'CLIP', clipToNeg),
    inS('images.image_0', 'IMAGE', refToNeg),
    inS('images.image_1', 'IMAGE', null),
    inS('vae', 'VAE', vaeToNeg),
  ],
  outputs: [outS('CONDITIONING', 'CONDITIONING', [])],
  widgets: [recipe.negative ?? '', EDIT_FORMAT, IMAGE_STRENGTH],
  widgetsNamed: { prompt: recipe.negative ?? '', edit_format: EDIT_FORMAT, image_strength: IMAGE_STRENGTH },
});

// --- sampler -> decode -> save --------------------------------------------
const posToSampler = link(10, 0, 12, 1, 'CONDITIONING');
const negToSampler = link(11, 0, 12, 2, 'CONDITIONING');
const latentToSampler = link(9, 0, 12, 3, 'LATENT');
const sampleToDecode = link(12, 0, 13, 0, 'LATENT');
const vaeToDecode = link(5, 0, 13, 1, 'VAE');
const imageToSave = link(13, 0, 14, 0, 'IMAGE');

addNode(12, {
  type: 'KSampler',
  order: 11,
  pos: [220, 0],
  size: [340, 300],
  inputs: [
    inS('model', 'MODEL', skipToSampler),
    inS('positive', 'CONDITIONING', posToSampler),
    inS('negative', 'CONDITIONING', negToSampler),
    inS('latent_image', 'LATENT', latentToSampler),
  ],
  outputs: [outS('LATENT', 'LATENT', [sampleToDecode])],
  // widgets_values is POSITIONAL. A KSampler's seed carries a
  // `control_after_generate` widget right after it ("fixed" keeps the seed).
  widgets: [seed, 'fixed', STEPS, CFG, SAMPLER, SCHEDULER, 1],
  widgetsNamed: {
    seed,
    control_after_generate: 'fixed',
    steps: STEPS,
    cfg: CFG,
    sampler_name: SAMPLER,
    scheduler: SCHEDULER,
    denoise: 1,
  },
});

addNode(13, {
  type: 'VAEDecode',
  order: 12,
  pos: [220, 350],
  size: [340, 82],
  inputs: [inS('samples', 'LATENT', sampleToDecode), inS('vae', 'VAE', vaeToDecode)],
  outputs: [outS('IMAGE', 'IMAGE', [imageToSave])],
});

addNode(14, {
  type: 'SaveImage',
  order: 13,
  pos: [220, 480],
  size: [340, 100],
  inputs: [inS('images', 'IMAGE', imageToSave)],
  outputs: [],
  widgets: [PREFIX],
  widgetsNamed: { filename_prefix: PREFIX },
});

// ---------------------------------------------------------------------------
// Write
// ---------------------------------------------------------------------------

const workflow = {
  id: basename(outWorkflow, '.json'),
  revision: 0,
  last_node_id: Math.max(...nodes.map((n) => n.id)),
  last_link_id: links.length,
  nodes,
  links,
  groups: [],
  config: {},
  extra: {},
  version: 0.4,
};

mkdirSync(dirname(outWorkflow), { recursive: true });
writeFileSync(outWorkflow, JSON.stringify(workflow, null, 2));

// The same graph as an API prompt, for comfyctl submit.
const graph = {
  '1': { class_type: 'UNETLoader', inputs: { unet_name: UNET, weight_dtype: 'default' } },
  '2': { class_type: 'LoraLoaderModelOnly', inputs: { model: ['1', 0], lora_name: LORA, strength_model: 1.0 } },
  '3': {
    class_type: 'SkipLayerGuidanceDiTSimple',
    inputs: { model: ['2', 0], double_layers: '', single_layers: '22', start_percent: 0, end_percent: 1 },
  },
  '4': { class_type: 'CLIPLoader', inputs: { clip_name: CLIP, type: 'moss_image', device: 'default' } },
  '5': { class_type: 'VAELoader', inputs: { vae_name: VAE } },
  '6': { class_type: 'LoadImage', inputs: { image: reference } },
  '7': {
    class_type: 'ImageScaleToTotalPixels',
    inputs: { image: ['6', 0], upscale_method: 'lanczos', megapixels: MEGAPIXELS, resolution_steps: recipe.resolution_steps ?? 16 },
  },
  '8': { class_type: 'GetImageSize', inputs: { image: ['7', 0] } },
  '9': { class_type: 'EmptyFlux2LatentImage', inputs: { width: ['8', 0], height: ['8', 1], batch_size: 1 } },
  '10': {
    class_type: 'TextEncodeMOSSImageEdit',
    inputs: {
      clip: ['4', 0],
      prompt: concept.instruction,
      vae: ['5', 0],
      edit_format: EDIT_FORMAT,
      'images.image_0': ['7', 0],
      image_strength: IMAGE_STRENGTH,
    },
  },
  '11': {
    class_type: 'TextEncodeMOSSImageEdit',
    inputs: {
      clip: ['4', 0],
      prompt: recipe.negative ?? '',
      vae: ['5', 0],
      edit_format: EDIT_FORMAT,
      'images.image_0': ['7', 0],
      image_strength: IMAGE_STRENGTH,
    },
  },
  '12': {
    class_type: 'KSampler',
    inputs: {
      seed,
      steps: STEPS,
      cfg: CFG,
      sampler_name: SAMPLER,
      scheduler: SCHEDULER,
      denoise: 1,
      model: ['3', 0],
      positive: ['10', 0],
      negative: ['11', 0],
      latent_image: ['9', 0],
    },
  },
  '13': { class_type: 'VAEDecode', inputs: { samples: ['12', 0], vae: ['5', 0] } },
  '14': { class_type: 'SaveImage', inputs: { filename_prefix: PREFIX, images: ['13', 0] } },
};

if (outGraph) {
  mkdirSync(dirname(outGraph), { recursive: true });
  writeFileSync(outGraph, JSON.stringify(graph, null, 2));
}

console.log(`wrote ${outWorkflow}`);
console.log(`  ${nodes.length} nodes | ${links.length} links | 1 chain`);
console.log(`  reference : ${reference}`);
console.log(`  concept   : ${concept.name}`);
console.log(`  seed      : ${seed}   steps ${STEPS}  cfg ${CFG}  ${SAMPLER}/${SCHEDULER}`);
console.log(`  output    : ${PREFIX}`);
