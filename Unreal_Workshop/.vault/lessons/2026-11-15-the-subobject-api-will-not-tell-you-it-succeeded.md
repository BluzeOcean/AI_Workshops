# The subobject API will not tell you it succeeded

**Date:** 2026-11-15
**Status:** active

## Symptom

Building a Blueprint actor's components from Python failed for all 14 components with the
message "add Deck failed: " - an empty reason - and then, once that was fixed, the handles
resolved to no object at all.

## What was actually true

**1. The failure reason is a Text object, so it is truthy even when empty.**

    handle, fail = sds.add_new_subobject(params)
    if fail:              # ALWAYS true - Text is an object
    if str(fail):         # correct

The add succeeded every time; the check raised on success.

**2. A SubobjectDataHandle is not a SubobjectData.**

get_object() and get_associated_object() both want a SubobjectData and raise
"Cannot nativize 'SubobjectDataHandle' as 'SubobjectData'" if handed the handle. The chain
is three calls deep and only the last one works:

    data = lib.get_data(handle)
    obj  = lib.get_associated_object(data)     # this is the component template

**3. But a Blueprint's components are not on its CDO.** get_components_by_class() on the
generated class's default object returns an empty list, even though the components are
there and render. Enumerate them through k2_gather_subobject_data_for_blueprint instead -
that is also the only way to reach a component's template to change a property on it.

## And one from the same task

spawn_actor_from_class() **ignores the location it is given** in this build: the actor
lands wherever the editor last placed something. Call set_actor_location_and_rotation
afterwards, always - the same trap the skills already list, in a new place (an environment
stamp rather than an editor probe).

## The trigger

Any scripted Blueprint authoring: components, per-component properties, or placing a
Blueprint in a level. Prove each step by reading the value back; success here is silent and
so is failure.