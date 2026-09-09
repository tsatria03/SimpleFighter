---
name: feedback_spier_obscurity_objectmenu_gating
description: Only entities with sound themes get spier + obscurity wiring; only entities with health go in the object menu. Don't reflexively mirror switch/instrument for soundless entities.
metadata:
  type: feedback
---

Two standing gating rules the dev applies when deciding what a new builder entity wires into:

- **Spier + obscurity** — wire these ONLY if the entity **has a sound theme** (emits audio the player navigates by or would want silenced). A soundless entity gets neither: no block in `spier.nvgt`, and it is NOT added to `obscurity_zone.nvgt`'s `spier_entities` list. (Example: `menu_input` has no sound theme, so it is deliberately not spyable or obscurable — even though its sibling the switch is, because the switch has a sound theme.)
- **Object menu** (the on-field object tracker / info menu) — add an entity ONLY if it **has health** (is destroyable). Entities with no health do not belong in it.

**Why:** the dev's consistent design line — the spier and obscurity systems are for audible things, and the object menu tracks things with health.

**How to apply:** when building a new builder entity, ask two questions before wiring: (1) does it have a sound theme? → then add the spier block + the obscurity `spier_entities` entry; (2) does it have health? → then add it to the object menu. If neither, skip those systems. Do NOT reflexively copy switch/instrument spier/obscurity wiring onto a soundless entity. See [[project_include_tree]] for where these systems live.
