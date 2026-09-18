---
name: project_security_jet_plan
description: Feature plan (candidate 15.0, DESIGN SETTLED, NOT yet built) — a new "security jet" builder trap: an enemy plane with a state machine that homes at the player on the ground like a tts enemie, and when hit takes off to a flight height and patrols the map back and forth like a projectile, landing again after a timer. Camera-style reward. 2d + 3d only. Models: tts_enemie (ground homing + melee), projectile (edge-bouncing air patrol + reward helper), container (state machine + form conventions + every integration point).
metadata:
  type: project
---

**STATUS: DESIGN SETTLED via Q&A (2026-09), building section-by-section on the dev's go-ahead.** Confirm each section before coding ([[feedback_confirm_before_implementing]], [[feedback_describe_dont_show_code]]); the dev commits between. Reference this plan the way [[project_container_plan]] was referenced during the container build — the container is the closest structural sibling (state machine, form, all runtime integrations, map errors, gallery, docs).

## Concept

A security jet is an enemy plane with a two-state machine, in the **traps** category, **2d + 3d only** (topdown has no height). It occupies a tile, has health, and the player kills it with weapons over several passes. On the ground it homes at the player like a tts enemie and melee-strikes on contact; the instant the player lands a weapon hit while it's grounded, it takes off to a flight height and cruises back and forth across the map like a projectile (harder to hit); after a flight-time timer it lands and resumes homing. Rinse and repeat until its health hits 0. The player CAN also hit it in the air (just harder). Passes through walls in both states.

## Sounds (theme folder: `builder/traps/security jets/<type>/`, one theme ships: `jet`)

- **death** — dying sound (on health <= 0).
- **engine** — the AIR loop (heard while it's flying above you).
- **flight** — one-shot on takeoff (state change to fly).
- **hit** — melee strike on the player (when a grounded jet reaches your tile).
- **hurt** — weapon-damage sound (suppressed on a killing blow, per the projectile rule the dev liked).
- **land** — one-shot when it begins descending (state change to land).
- **loop** — the GROUND loop (heard while it's moving to get you).

The always-looping ambient slot swaps `loop` (ground) <-> `engine` (air), like the container's loopsound swaps rolling<->flight.

## Settled decisions (dev, 2026-09, via one-question-at-a-time Q&A, NO pickers)

- **Reward = CAMERA-STYLE.** Has `level` + `xp` fields; destroying it awards `xp * level * xpmod` + "Defeated <jettype> level N." kombat-log line; SILENT when the reward computes to 0 (default xp=0); NO kills++ , NO loot, NO bodyfall. Mirrors [[project_container_plan]]/security_camera/projectile. (Dev explicitly chose camera-style over npc-style kill credit even though it's "an enemy plane.")
- **Flight height = a FIELD, default 5** (not fixed at 5). The height it climbs to.
- **ONE speed field** governs BOTH ground homing and air patrol (dev confirmed after I verified every builder element uses a single speed field; the only multi-speed element is the vehicle's base/accel/brake, a driving-physics special case, not a precedent). The air phase is harder to hit because it's a blind bounce, not because it's faster.
- **Separate `fire time` field** for the ground melee (ms between strikes while on the player's tile), mirroring the tts enemie's firetime — its ground behavior is modeled on the tts enemie.
- **NO defense field** — weapon hits land at full value (camera/container style, NOT tts-enemie style).
- **Passes through walls** in both states (ground homing is tts-style with no wall check; air patrol is above everything and only turns at the map edges). Dev confirmed.
- **NO move-on-x/y/z checkboxes.** Considered (the container has them) but the dev dropped them 2026-09 to avoid complicating the jet — "this will just complicate things if we try to add extra jet controls." So the movement is fixed (see below), no per-axis flags, and Tier-2 has no move-flag validation.
- **NO seeing range / live-leash** (unlike the container) — the jet is always active.

## Movement model (fixed, no flags)

Vertical/height axis is **y on 2d, z on 3d** (the axis `flight height` lives on). Horizontal axes are **x on 2d**, **x + y on 3d**.

- **GROUND (homing):** homes toward the player across the ground plane, staying at ground level (height 0) — tracks the player's x on 2d; x and y on 3d. The vertical axis is used ONLY for the climb to flight height, never for ground chasing. On the player's tile it strikes for `attack` every `fire time` (plays `hit`), gated like the tts enemie/container (blocked while the player is on an aircraft/vehicle/bike/glider — inplain/invehicle/onbike/glider_engine_on false, paused==0).
- **ASCEND:** the moment a weapon hit lands while grounded -> play `flight` (one-shot), swap the loop slot to `engine`, climb one tile per speed-step to `flight height`.
- **AIR (patrol):** patrol back and forth along **x** at the flight height, bouncing at the MAP edges (blind, not homing; holds whatever y it took off from on 3d), playing `engine`. Weapon hits still chip health here but do NOT re-trigger takeoff (it's already up).
- **DESCEND:** when the `flight time` timer expires -> play `land` (one-shot), descend one tile per speed-step back to ground level, then resume GROUND homing.

Health <= 0 in any phase -> `death` + camera-style reward + remove.

**Locked inferred defaults:** starts grounded; rise/descend are GRADUAL (one tile per speed-step, for audible feedback — "up to height 5 as soon as you hit it" read as immediate takeoff, not teleport); the flight timer counts down regardless of whether the player keeps hitting it in the air; `hurt` suppressed on a killing blow.

## Build-form fields (FINAL, dev-approved order 2026-09)

Input boxes, then the sound list, then okay/cancel. NO checkboxes, NO sliders. Order:

1. **x** (prefilled from selection) — ground starting tile
2. **y** (prefilled)
3. **z** (prefilled) — 3d only
4. **health** — default `1`
5. **attack** — required, no default (melee damage on contact)
6. **fire time** — required, no default (ms between melee strikes on the player's tile)
7. **speed** — required, no default (ms per one-tile step, ground + air)
8. **level** — default `1` (reward multiplier)
9. **xp** — default `0` (base reward; 0 = silent/no reward)
10. **flight height** — default `5`
11. **flight time** — default `5000` (ms cruising before it descends)
12. **security jet sound** — list: `none` + the `jet` folder(s)
- **okay** / **cancel** buttons

## On-disk format

`security_jet x y [z] health attack firetime speed level xp flightheight airtime jettype` — **12 tokens on 2d, 13 on 3d** (z after y). Field ORDER on disk should follow the FORM order above (x y [z] health attack firetime speed level xp flightheight flighttime jettype). Brand-new keyword, so NO back-compat concerns. Friendly name "security jet" -> on-disk token `security_jet`. Alphabetical slot in the **traps** category: right after `security_camera` (map_menu build menu + maps.txt list + command_blocker allcommands where relevant) — [[feedback_alphabetize_builder_entities]].

## Build sections (~10, one per go-ahead, no re-presenting — [[feedback_describe_dont_show_code]])

1. **Class + globals + spawn/despawn/destroy_all + pool.** `sound_pool jetpool(...)`, `security_jet@[] jets`, phase constants (GROUND/ASCEND/AIR/DESCEND), the class, `spawn_security_jet`, `despawn_security_jet`, `destroy_all_security_jets`. Sentinel-null removal ([[project_stability_rules]]).
2. **read/write + parser dispatch + Tier-1 lenok (12/13).** `read_security_jet`, `write_security_jet`, dispatch in map_parser.nvgt (read dispatch, despawn dispatch, Tier-1 lenok 12/13).
3. **Build form** `build_security_jet` — the 11 inputs + sound list, audition keys on the list (Space hurt, Ctrl+L loop, plus engine/flight/hit/land/death), NO checkboxes.
4. **`jetloop` state machine** — the four phases + melee, registered in game.nvgt's loop.
5. **Runtime integrations** — jetpool into all_pools (decpool.nvgt), effect_space apply_effect_pools, spier (announces the jet folder), obscurity_zone name lists, object-info menu (health + level, camera-style), tracker anchor, game_handlers object-menu gate.
6. **Destroy + reward + weapon/bullet hit wiring** — `award_jet_kill` (xp-only, silent at 0), a `hurt_jet(i, dmg)` helper (play `hurt` unless the hit is fatal, subtract health, health<=0 -> `death`+reward+remove, else if GROUNDED -> trigger ASCEND), and scan-and-hit blocks in weapon.nvgt (melee + swing) and bullet.nvgt (bullet-hit + splash). This is the trickiest section (mirror how the player damages projectiles: award_projectile_kill sites in bullet.nvgt/weapon.nvgt/glider.nvgt).
7. **Spawn/despawn/build/unbuild commands** — dispatch in the command handlers and the build/unbuild menu.
8. **Tier-2 semantic** — `security_jet_semantic_error` + dispatch (position, health/attack/firetime/speed/level/xp/flightheight/flighttime numbers, jet sound or "none"). NO move-flag checks.
9. **Gallery** — the security jet gallery type with its audition keys (misc/gallery.nvgt).
10. **Docs** — `sf/docks/builder/security_jets.txt` help topic, maps.txt Traps entry (alphabetical), a 15.0 changelog entry (~50-750 chars, [[feedback_changelog_rules]]), and mark this plan COMPLETE.

## Reference files (read before building)

- `src/includes/builder/kombat/tts_enemie.nvgt` — ground homing toward the player (ttseneloop, moves x/y/z toward me) + melee on the player's tile (firetime-gated, aircraft/vehicle/bike/glider guards, shield/reflection handling). NO wall check (moves through walls).
- `src/includes/builder/kombat/projectile.nvgt` — edge-bouncing line movement (cur_x_step/bounce_at_edge, projectile_at_edge), the hit-everything loop, and `award_projectile_kill` (the camera-style reward helper pattern + the death sites in bullet/weapon/glider that call it).
- `src/includes/builder/traps/container.nvgt` — the STRUCTURAL TEMPLATE: state machine (containerloop), pool + loopsound-swap, spawn/despawn/destroy_all, build form conventions, read/write, Tier-2, and the list of every runtime integration point. Copy its shape.
- [[project_container_plan]] — the as-built section list this plan mirrors. [[project_stability_rules]], [[feedback_builder_form_control_order]], [[project_angelscript_block_comment_star_slash]] (watch `*/` in glob comments).
