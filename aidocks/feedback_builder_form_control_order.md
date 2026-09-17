---
name: feedback_builder_form_control_order
description: Builder-entity audio forms lay controls out in a fixed top-to-bottom order — input boxes first, then lists, then sliders, then checkboxes, then buttons (okay then cancel last). Give numeric fields sensible defaults.
metadata:
  type: feedback
---

Every builder-entity form (`build_<entity>()`) lays its controls out in this fixed order, top to bottom (each group "if any" — skip a group that has no controls):

1. **Input boxes** (`form.create_input_box`) — coordinates (min/max x, y, z) and any other numeric/text fields.
2. **Lists** (`form.create_list`) — e.g. a tile-sound or direction list.
3. **Sliders** (`form.create_slider`) — e.g. volume/pitch.
4. **Checkboxes** (`form.create_checkbox`) — e.g. destroyable, overlap.
5. **Buttons** (`form.create_button`) — **okay first, then cancel**, always last.

Lists always come before sliders. This fits the common sound pattern directly: the sound-theme list, then its volume/pitch sliders ("pick the sound, then set its volume and pitch").

**Why:** the dev's standard layout across all builder entities; a consistent control order makes the forms predictable to navigate by screen reader.

**How to apply:** any new `build_<entity>()` follows this order — inputs, then lists, then sliders, then checkboxes, then okay/cancel. Don't interleave a list between input boxes or put a button before a checkbox. Also give numeric fields a **sensible default** in their input box (e.g. the slant's step height defaults to `1`, fire/teleporter seeing-range fields default to `maxx`/`maxy`/`maxz`). Templates that follow it exactly: `build_platform` and `build_staircase` (x/y/z/health inputs → tile-sound list → volume/pitch sliders → destroyable/overlap checkboxes → okay/cancel buttons). See [[project_stability_rules]] (builder UI uses the audio form) and the settled forms in [[project_feature_ideas]].
