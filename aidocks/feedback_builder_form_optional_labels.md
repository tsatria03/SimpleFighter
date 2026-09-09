---
name: feedback_builder_form_optional_labels
description: Optional builder-form fields must signal so in their own caption using the "leave blank to skip" phrasing (the switch/sensor convention); required fields need no marker.
metadata:
  type: feedback
---

In a builder form, every **optional** input/control must say so **in its own label**, so a screen-reader user knows it can be left blank without tabbing away to find out. A caption that gives no hint — e.g. `prompt: spoken when the menu opens` — reads as if the field is required. Signal it with the standard **"leave blank to skip"** phrasing that the switch and sensor command fields already use (e.g. `prompt: spoken when the menu opens, leave blank to skip`). Use that exact phrasing for consistency across forms — the dev chose it (2026-09) over the bare word "optional."

**Required** fields need no marker — required is the default expectation.

**Why:** the dev flagged (2026-09) that the menu input's `prompt` field didn't signal it was optional, unlike its command fields which said "leave blank to skip," and asked that optional fields match that switch/sensor wording. The rule is general — it applies to every element with optional fields, not just menu inputs.

**How to apply:** when adding a `create_input_box` (or any control) for an optional field, bake the optionality into the caption string. Applies to new elements and is worth fixing retroactively on existing forms when you're already in them. Composes with [[feedback_builder_form_control_order]].
