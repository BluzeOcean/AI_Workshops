# A material graph link that does not raise, does not link

**Date:** 2026-11-15
**Status:** active

## Symptom

An arena deck rendered as **one 99 m plate** instead of a grid of 6 m ones. The material
had the right texture, the right tiling numbers on a TextureCoordinate node (u = 8.25,
v = 6.0), and every material *property* read back connected. Nothing errored. Nothing even
warned.

## What was actually true

MaterialEditingLibrary.connect_material_expressions **returns successfully when the pin
name is wrong and connects nothing** - the same failure shape as
connect_material_property, which this project had already been bitten by. The node was in
the graph, the number was right, and the link did not exist.

Read it back, do not trust the call:

    # input names per expression, and whether each slot is filled
    ins   = mel.get_material_expression_input_names(dst)      # ['UVs', 'Tex', ...]
    slots = mel.get_inputs_for_material_expression(mat, dst)  # [None, None, None]  <- nothing linked
    mel.connect_material_expressions(src, out_name, dst, 'UVs')
    slots = mel.get_inputs_for_material_expression(mat, dst)  # [TextureCoordinate, None, None]

A TextureSample's UV pin is called **UVs**, not UV.
get_material_expression_output_names and get_material_expression_input_names give the real
names; the main output of most nodes is the empty string.

## Two more traps from the same task

1. **connect_material_property wants the MaterialProperty ENUM in 5.9, not a string.**
   Passing 'BaseColor' raises NativizeProperty: Cannot nativize 'str' as 'Property'. The
   call is connect_material_property(node, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR).
2. **Deleting and recreating a material asset orphans every reference to it.** A rebuild
   loop that does delete_asset then create_asset leaves level actors holding a dead object,
   and they render with the default grey material - which looks exactly like 'the floor
   lost its texture'. Re-assign the materials in the level AFTER every material rebuild,
   or the map is one step behind its assets.

## The trigger

Building or repairing a material graph from Python, in this editor, with more than one
node and more than one link. Verify every link; a material that renders wrong with no
error in the log is this by default.
