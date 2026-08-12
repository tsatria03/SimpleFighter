---
name: project_wind_trap_plan
description: Settled but unbuilt design + section plan for the Wind trap — a fire-style seeking trap that pushes the player instead of killing, with wall-aware knockback, an optional health chip, a faced direction, and a tile push distance. Build section by section.
metadata:
  type: project
---

Settled design and section plan for the **Wind trap**, agreed with the dev on 2026-08-11 but NOT YET BUILT. Wind is modeled on [[the fire trap]] (`src/includes/builder/traps/fire.nvgt`): a placed emitter with a per-axis seeing range that wakes up and homes toward the player, playing a looping sound. It differs from fire in the payoff — instead of killing on contact, it **shoves** the player and optionally chips health. Sounds live in `sf/sounds/decompiled/builder/traps/winds/` (six types: wind…wind6, each with `loop.ogg` + `hit.ogg`, same layout as fires).

Build one section at a time, pausing for review/commit between sections, per [[feedback_confirm_before_implementing]]. Follow all stability rules ([[project_stability_rules]]): double coords, CRLF, builder audio form, mode-locked parsing, alphabetical menu slot ([[feedback_alphabetize_builder_entities]]), form control order ([[feedback_builder_form_control_order]]).

## What wind reuses from fire (same properties)

- **Position** — x, y (and z on 3d).
- **Per-axis seeing range** — x range, y range (and z range on 3d): how close the player must get before it wakes and homes.
- **Speed** — the tick interval; how often it steps toward the player (lower = faster).
- **Sound type** — a list of the wind folders (with "none" at top), each supplying `*loop*` (ongoing gust) and `*hit*` (the strike). Loop positioned/updated via the trap's sound_pool like `firepool`.
- **Move-on-axis toggles** — checkboxes for which axes it may chase along (x, y, and z on 3d).
- The `spotted` latch + per-tick homing loop from `fireloop`.

## What is NEW / different from fire

- **No kill-on-contact / no death sequence.** Fire's contact runs `clearmap` + the "you have died" retry menu. Wind does none of that. Any death happens only indirectly, if the chip damage wears the player to 0 health through the game loop's existing clamps (same approach as spike/flux-zone damage — subtract and let the loop handle death).
- **Three new fields:**
  - **direction** the wind faces — stored as an int 1-6 using the EXACT conveyor-belt scheme (`conveyor_belt.nvgt`), for cross-element consistency and to dodge the "up" ambiguity (up = y axis in 2d, z axis in 3d). Mapping: 1 left = x-, 2 right = x+, 3 = y-, 4 = y+, 5 = z- (3d only), 6 = z+ (3d only). Mode-aware form LABELS (belt's): always left/right; then 2d = down(3)/up(4), topdown+3d = backward(3)/forward(4); 3d additionally down(5)/up(6). So 2d offers left/right/down/up, topdown offers left/right/backward/forward, 3d offers all six. (Belt uses "backward"/"forward"; wind matches that rather than "back"/"front" for menu consistency.)
  - **push distance** — how many tiles it shoves you per strike.
  - **health** — chip damage per strike. Optional; blank/0 = no damage.
- **THE HIT SOUND (and the damage) FIRE ONLY WHEN health >= 1.** A wind with health 0 is a pure silent gust that only pushes — no `*hit*`, no damage. (Dev's explicit rule.)
- **Push is wall-aware ("into a wall but not past it").** BUILT in §2 as `wind_push_player`: step the player one tile at a time toward the faced direction; before each tile, stop if it would cross the map bounds (minx/maxx/miny/maxy, and minz/maxz on 3d) or if `wall_blocks(nx,ny,nz)` (`wall.nvgt:130`) is true. Uses `wall_blocks()` — the SAME canonical test the player's own walking (`body_step`) uses — rather than the NPC `gmt()` string-match, because it correctly resolves passages and platform-over-wall. Player ends against the wall on the last open tile, never through it. Deliberately does NOT stop for safe zones or npc terrain (those are NPC-specific; a gust shouldn't be). The push does NOT call `playstep()` — a shove is not a step, so it triggers no footstep audio or per-step zone effects (flux/tile). Being blown off a ledge lets the normal fall check take over next frame (emergent, intended).
- **Contact is repeated, not terminal.** After a push the player is off the wind's tile, so it re-approaches → a chase-and-knockback rhythm (unlike fire's one-and-done kill).

## Context established while designing (so we don't re-derive)

- No existing trap pushes a *living* player at all — fire/bomb/timebomb/mine/hazard all use exact-tile contact and then damage or kill; the only player-position write is the death-reset to origin (0,0,0). Wind is the first trap that relocates a living player, so there was no push precedent — we chose the NPC wall-check as the model because normal walking is already wall-blocked.
- Trap contact test pattern (from fire): `me.x==firex and me.y==firey` (+ `me.z==firez` on 3d), gated `and paused==0 and !glider_engine_on`.
- Traps live in the **traps** builder category; wind goes there in its alphabetical slot (between vanishing_hazard? no — al:  after timebomb/… place by true alpha among trap entries). Menu wiring in `map_menu.nvgt`; parser dispatch in `map_parser.nvgt`; `destroy_all_winds()` in `clearmap`.

## On-disk map line (proposed)

Fire's tokens plus the three new fields at the END (keeps parsing additive). `direction` is the int 1-6 (belt scheme), not a word. Distinguish 2d/3d by `mapmode == "3d"` inside `read_wind` (like `read_mhazard`), NOT by a raw length that could collide with another element:

- 2d / topdown: `wind x y  xrange yrange  speed windtype  direction push health  moveable moveable2`
- 3d: `wind x y z  xrange yrange zrange  speed windtype  direction push health  moveable moveable2 moveable3`

(direction/push/health sit right after windtype so the moveable bools trail at the very end, matching fire's line shape — dev's request.)

## Section plan

- **§1 — Data + lifecycle. DONE.** The `wind` class + `winds` array, `windpool`, `spawn_wind`, `destroy_all_winds` (destroy each loop sound like fire), and geometry helpers: "inside the seeing box" + "on my exact tile" contact. NOTE: `windpool` MUST be registered in the `all_pools` literal in `initialize_sound_pools()` (`decpool.nvgt`) or it never gets a `mixer()` and `apply_effect_pools()` crashes with a null-pointer the instant a wind exists ([[project_audio_model]] documents this). Missed it initially → crash at `effect_space.nvgt:45`; fixed by adding `windpool` to `all_pools`.
- **§2 — Runtime (`windloop`). DONE.** Homing loop modeled on `fireloop` but the whole tick (homing AND strike) is throttled to `windtime` — a deliberate change from fire's per-frame kill check, so a wind that has pinned the player against a wall buffets at its cadence instead of draining every frame. Latch `spotted` on entering the seeing box; per tick, home one tile toward the player on enabled axes (guarded by `paused==0`), reposition the loop sound, then if on the player's tile (and `paused==0 and !glider_engine_on`) strike: if health >= 1 play `*hit*` + `health -= windhealth`, then `wind_push_player`. Direction is a fixed WORLD axis (left/right = x∓, front/back = y±, up/down = z±), verified against the step functions — NOT rotation-relative. Hooked as `windloop();` in `game.nvgt` after `vehloop()`. NOTE: `push` should be ≥ 1 (enforced in the §4 form) — a push of 0 leaves the player on the tile and they'd take a damage pulse every tick until they walk off.
- **§3 — Map I/O + wiring. DONE.** `read_wind` / `write_wind` in `wind.nvgt` (line format above; reader branches on `mapmode`, matching the parser length gate). `map_parser` dispatch: `else if(sd[0]=="wind" && (sd.length()==12 || sd.length()==15)) read_wind(sd);` — placed after the fire dispatch; `sd[0]` disambiguates from fire's length-12 3d line, so no collision. `destroy_all_winds()` added to `clearmap` (`map.nvgt`, after `destroy_all_walls`). Effect-space registration added to `apply_effect_pools()` (`effect_space.nvgt`, after the vehicles loop): a loop over `winds` calling `apply_all_effects(windx, windy, windpool, windz)` — no null guard (compacted array).
- **§4 — Build form + menu. DONE.** `build_wind` mirrors `build_fire` (incl. space=`*hit*` / ctrl+L=`*loop*` audition) plus: a **push distance** box (default "1", required, rejected if < 1) and a **health** box (default "0", optional — blank→0) after speed; a **direction** list after the wind-sound list using the conveyor-belt mode-aware labels + int ids (2d: left/right/down/up = 1/2/3/4; topdown: left/right/backward/forward = 1/2/3/4; 3d: adds down/up = 5/6), picked via `string_to_number(get_list_item_id(...))`. Control order = inputs → lists → checkboxes → buttons. Menu: added "wind"/"wind" to the traps row of `entry_names`/`entry_ids` (after vanishing hazard), added "wind" to `converted_3d` (works on 3d), left OUT of `excluded_topdown` (works on topdown), and added the `if(buildtype=="wind") build_wind();` dispatch. NOTE: negative health can't heal — `windloop`'s `>=1` gate makes any health < 1 a silent gust, so no form guard is needed on health.
- **§5 — Docs. DONE.** Changelog entry added at the top of 14.3 (record-not-manual, [[feedback_changelog_rules]]) — brings 14.3 to 6 of 10. Help topic `sf/docks/builder/winds.txt` written, modeled on `fires.txt` (intro → How a wind works → fields → auditioning → authoring by hand), observable behavior only per [[feedback_tp_prose]], with the fire contrast woven in and the direction number codes explained in the authoring section. Auto-appears in the help menu via the `docks/builder/*.txt` scan (no menu wiring).

Post-§5 integration (dev-requested, easy to miss for a new point entity): added a wind block to `spy_check_entities` in `spier.nvgt` (mirrors the fire block — compacted array so no null guard, no `found_object`) so the spy scanner announces "wind"; and added "wind" to the `spier_entities` list in `obscurity_zone.nvgt` so it's a selectable type an obscurity zone can hide from the spier. (Wind isn't in `menu_entities` — it has no info menu entry, same as fire.)

Status: **WHOLE WIND TRAP FEATURE COMPLETE** across all five sections. Files: `wind.nvgt` (data/lifecycle/runtime/push/read/write/build), `game.nvgt` (windloop hook), `map.nvgt` (clearmap), `map_parser.nvgt` (dispatch), `effect_space.nvgt` (effect pool), `decpool.nvgt` (all_pools registration — the crash fix), `map_menu.nvgt` (traps entry + dispatch + converted_3d), `changelog.txt`, `winds.txt`.
