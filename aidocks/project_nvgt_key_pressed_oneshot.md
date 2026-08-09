---
name: project_nvgt_key_pressed_oneshot
description: NVGT key_pressed() is one-shot — consumed on the first read each frame, so never read the same key in two separate if-checks in one loop iteration.
metadata:
  type: project
---

In the pinned nvgt2 engine, `key_pressed(KEY_X)` is **consumed on the first read** each frame. Reading the SAME key in two separate `if` checks in one loop iteration means the second check always sees false.

**Why:** a common trap when one physical key drives multiple behaviors (modifier combos, mode branches). Example from a sibling NVGT game: an auto-run feature added `if(key_pressed(KEY_R) and alt_is_down())` right before an existing `else if(key_pressed(KEY_R) and !in_game)` check — with Alt up, the first read ate the R press, so plain R silently did nothing.

**How to apply:** when one physical key drives multiple behaviors, read it **once** into the outer `if` and branch inside — `if(key_pressed(KEY_R)) { if(alt_is_down()) ...; else if(!in_game) ...; }` — not two sibling `if`s that each call `key_pressed(KEY_R)`. Different keys per check are fine. In this codebase most input routes through the global `controls` (a key_config) rather than raw `key_pressed`, but raw `key_pressed`/`key_down` still appears (e.g. the camera-mode `key_up(KEY_G)` gates in `game_handlers.nvgt`), so the rule applies wherever a raw call is duplicated. Related: [[project_angelscript_reserved_words]], [[project_stability_rules]].
