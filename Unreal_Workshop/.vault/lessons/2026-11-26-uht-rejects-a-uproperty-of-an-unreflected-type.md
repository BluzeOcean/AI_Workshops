# UHT rejects a UPROPERTY of an unreflected type, and a UFUNCTION parameter that shadows a base member

**Status:** active

**Date:** 2026-11-26
**Symptom:** Two UHT errors, both from porting a component out of a larger actor:

```
IronPathPathComponent.h(172): Error: Unable to find 'class', 'delegate', 'enum', or
'struct' with name 'FIronPathPathCurve'

IronPathPathComponent.h(96): Error: Function parameter: 'bVisible' cannot be defined in
'SetPathVisualsVisible' as it is already defined in scope 'USceneComponent'
(shadowing is not allowed)
```

Neither is a C++ error, and neither is reported by the compiler — UHT runs first and
stops the build, so the message names neither the real problem nor the fix.

**Cause:** `UPROPERTY` needs a type the reflection system can see. A plain C++ struct
with no `USTRUCT` has no reflected form, so a `UPROPERTY()` of it is meaningless to
UHT — the property cannot be serialized, searched or exposed to Blueprints. The jam's
original code had the same member as a **plain** member for exactly this reason, and
the port made it a `UPROPERTY` because every other member in the class was one.

The second is UHT's own rule: a `UFUNCTION` parameter may not shadow a member of the
base class. `USceneComponent` already has a `bVisible`, so a parameter of that name is
ambiguous in the generated thunk.

**Fix:** Keep a non-reflected struct a plain member, and give the parameter a name the
base class does not use:

```cpp
// A plain struct is not reflectable: keep it out of UPROPERTY.
FIronPathPathCurve DrawnPath;

// USceneComponent already has bVisible.
UFUNCTION(BlueprintCallable, Category = "IronPath|Path")
void SetPathVisualsVisible(bool bShowVisuals);
```

**Applies when:** Porting a class from an engine example or another project — engine
examples mark their plain structs `UPROPERTY` far less often than people expect — and
whenever UHT reports *"Unable to find 'class', 'delegate', 'enum', or 'struct'"* or a
shadowing error, both of which are reflection errors wearing a C++ error's clothes.

**Related:** the port that produced both errors is the drawn-path module in
`D:\UE\IronPath\Source\IronPath\Public\Gameplay\`.
