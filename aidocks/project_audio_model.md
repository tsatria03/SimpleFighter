---
name: project_audio_model
description: The runtime audio model — sound_pool + HRTF, me/me_rotation, 3d vs stationary plays, get_pack_sound/get_map_sound resolution, adding a new pool, and the load-bearing looping/locked-slot invariant.
metadata:
  type: project
---

## Model

NVGT `sound_pool` with HRTF. Player position is the vector `me`; listener orientation is `me_rotation` (degrees). Pools are advanced each frame via `update_sound_pools()`. 3D plays use `play_3d` / `play_extended_3d` with `calculate_theta(me_rotation)` for listener heading. 2D-only sounds use `play_stationary` / `play_stationary_extended`. Per-tile/wall volumes and pitches travel with the entity (`volume`, `pitch` fields on each class) and are passed into the play call.

Sound assets are looked up via `get_pack_sound("...")` / `get_map_sound("...")` with glob patterns like `main/characters/<chartype>/map/*camclear*` or `builder/construction/walls/<wallname>/*death*`. The `chartype`, `menutype`, `keyboardtheme` strings drive theme selection within `sf/sounds/decompiled/main/`. A no-match plays nothing — deliberate, but a clip-path typo is indistinguishable from "feature has no sound" (see [[project_deferred_concerns]]). Folder structure is in [[project_sound_assets_layout]].

## Adding a new sound_pool

Declare `sound_pool foopool;` in whichever file owns it (per-entity pools live at line 1 of the entity's `.nvgt`; subsystem pools in the subsystem's globals file; shared/generic pools in `dec.nvgt`/`game.nvgt`/`map.nvgt`), then append the name to the single `all_pools = {...}` array literal in `src/includes/main/globals/decpool.nvgt`. That one append wires it into initialize/update/pause/resume. If the pool plays positioned sounds that should pick up effect_space FX, also add a per-entity loop to `apply_effect_pools()` in `src/includes/builder/audio/effect_space.nvgt` (separate from `all_pools` because each loop needs the owning entity's coords) — the `airbeacons` entry is the template.

## Looping / "locked slot" invariant (load-bearing)

Sounds you later pause / resume / reposition / stop must be **looping or persistent ("locked") slots; one-shots are fire-and-forget.** A `sound_pool` recycles a slot index the instant a non-looping sound finishes *or is paused* (`reserve_slot` skips only `looping`/`persistent` slots), so a stored handle to a finished/paused one-shot will, once the slot is reused, operate on a *different* entity's sound — audio plays from, or cuts out on, the wrong instance. This was the NPC / tts-enemie "sounds play for the wrong instance" bug, worst in same-type swarms (the arena). Rules:

1. Any per-entity "voice" you keep repositioning / pausing / destroying is played `looping` so its slot stays locked to that entity — see the npc taunt, tts `ttsemsound`, passage `passagesound`; re-roll a looping voice for variety by destroy-then-replay, not by replaying a one-shot.
2. Never `destroy_sound` a stored one-shot handle to "refresh" it — let one-shots finish on their own.
3. Init every stored sound-handle field to `-1`, guard every pause / resume / `update_sound_3d` / `destroy_sound` with `!= -1`, and reset to `-1` after destroy (an uninitialized handle defaults to `0`, a *valid* slot — destroying it clobbers whoever owns slot 0).
4. The "fall silent while in pain" duck lives in a shared `react_to_hit(pool, mask_slot)` method on both `npc` and `ttsenemie` — route any new hit source through it rather than re-rolling the pause/window inline.

NPC category pools and `ttsempool` are constructed large (`(500)`, like `bulletpool` / `bombpool` / `itempool` / `projpool`) rather than the default 100, because each live enemy holds one looping-voice slot plus transient one-shots and a swarm (the arena, up to 50 same-category enemies) funnels them all into a single pool.

Related: [[project_stability_rules]], [[project_arcade_arena_revival]].
