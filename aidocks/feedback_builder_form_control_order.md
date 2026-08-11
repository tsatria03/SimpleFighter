---
name: feedback_builder_form_control_order
description: Builder-entity audio forms lay controls out in a fixed order top-to-bottom — input boxes first, then lists and sliders, then checkboxes, then buttons (okay then cancel last). Give numeric fields sensible defaults.
metadata:
  type: feedback
---

Every builder-entity form (`build_<entity>()`) lays its controls out in this fixed order, top to bottom:

1. **Input boxes** (`form.create_input_box`) — coordinates (min/max x, y, z) and any other numeric/text fields.
2. **Lists and sliders** (`form.create_list`, `form.create_slider`) — e.g. a tile-sound or direction list, volume/pitch sliders.
3. **Checkboxes** (`form.create_checkbox`) — e.g. destroyable, overlap.
4. **Buttons** (`form.create_button`) — **okay first, then cancel**, always last.

**Why:** the dev's standard layout across all builder entities; a consistent control order makes the forms predictable to navigate by screen reader.

**How to apply:** any new `build_<entity>()` follows this order — don't interleave a list between input boxes, or put a button before a checkbox. Templates that follow it exactly: `build_platform` and `build_staircase` (x/y/z/health inputs → tile-sound list → volume/pitch sliders → destroyable/overlap checkboxes → okay/cancel buttons). Also give numeric fields a **sensible default** in their input box (e.g. the slant's step height defaults to `1`). See [[project_stability_rules]] (builder UI uses the audio form) and the settled forms in [[project_feature_ideas]].
