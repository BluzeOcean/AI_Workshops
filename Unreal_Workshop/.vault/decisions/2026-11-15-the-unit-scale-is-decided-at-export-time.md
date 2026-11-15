# The unit scale is decided at export time, not left to the importer

**Date:** 2026-11-15
**Status:** active
**Decision:** When work crosses between a DCC/other engine and Unreal, the **scale
conversion is part of the export step**, decided and applied there. It is never left to
Unreal's importer, and never discovered afterwards.

Unreal's default unit is **1 uu = 1 cm**. Blender and Unity are **metres**. So the
Blender → Unreal handoff is a **×100** scale, and Blender ↔ Unity is ×1.

**Reason:** The importers do not compensate. Importing a metre-scale mesh into Unreal
without scaling produces a character one hundredth of its intended size — and it still
looks like a valid mesh, with no error, in a scene where a 180 cm human is 1.8 uu tall.
Catching it costs a rebuild; catching it at export costs one number.

The scale is a property of the **source asset**, not of the destination — so it is decided
when the source is produced, and recorded in the recipe that produced it.
**Supersedes:** —
