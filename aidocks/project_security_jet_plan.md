---
name: project_security_jet_plan
description: Feature plan (candidate 15.0, DESIGN SETTLED, NOT yet built) — a new "security jet" builder trap: an enemy plane with a state machine that homes at the player on the ground like a tts enemie, and when hit takes off to a flight height and patrols the map back and forth like a projectile, landing again after a timer. Camera-style reward. 2d + 3d only. Models: tts_enemie (ground homing + melee), projectile (edge-bouncing air patrol + reward helper), container (state machine + form conventions + every integration point).
metadata:
  type: project
---

**STATUS: COMPLETE — all 10 sections built & shipping in 15.0 (2026-09).** The full security jet feature is done: §1 class/globals/pool/lifecycle, §2 read/write/parser dispatch/lenok/clearmap, §3 build form, §4 jetloop state machine, §5 runtime integrations (decpool/effect_space/spier/obscurity/object-menu/tracker/object-menu-gate), §6 destroy+reward+weapon/bullet/glider hit wiring, §7 commands (no new code), §8 Tier-2 semantic, §9 gallery, §10 docs. New builder entity in the **kombat** menu category (sounds under builder/kombat/security jets/, code file in builder/kombat/ — dev moved it there with security_camera 2026-09, glob-included either way). Drop this plan from the active backlog once 15.0 releases.

**ADDENDUM (2026-09, post-build, ships 15.0):** added an **auto flight** trailing bool field. Off (default) = spawn on the ground homing as before; on = spawn already airborne at flight height in JET_AIR, engine loop + flight timer running, comes down after flight time then resumes ground homing (Option A — "already up at height", NOT a self-climb). New class field `bool autoflight`, constructor `bool af=false` param (set the vertical to flightheight + phase JET_AIR + restart flight/move timers, engine loop instead of ground loop, NO takeoff cue), threaded through spawn/read/write (+build-form checkbox after the sound list) and the bullet cloner (clones the original's autoflight). **HARD format change, NO back-compat** (dev-directed): trailing `true`/`false` after jettype, so 13 tokens on 2d / 14 on 3d; map_parser read-dispatch + lenok now `(13||14)`, Tier-2 validates it via `is_bool_token`. Harmless for players (the jet itself is new in 15.0, no released map has one). Docs: security_jets.txt (field + hand-authoring line) + a separate 15.0 changelog entry.

**BUILD HISTORY (was): DESIGN SETTLED via Q&A (2026-09), building section-by-section on the dev's go-ahead.** Confirm each section before coding ([[feedback_confirm_before_implementing]], [[feedback_describe_dont_show_code]]); the dev commits between. Reference this plan the way [[project_container_plan]] was referenced during the container build — the container is the closest structural sibling (state machine, form, all runtime integrations, map errors, gallery, docs).

## Concept

A security jet is an enemy plane with a two-state machine, in the **kombat** builder-menu category (dev moved cameras + jets from traps -> kombat 2026-09, sounds now under `builder/kombat/security jets/`; the .nvgt CODE file now lives in `src/includes/builder/kombat/` too — dev moved security_jet.nvgt + security_camera.nvgt there 2026-09, container.nvgt stayed in traps; glob-included either way), **2d + 3d only** (topdown has no height). It occupies a tile, has health, and the player kills it with weapons over several passes. On the ground it homes at the player like a tts enemie and melee-strikes on contact; the instant the player lands a weapon hit while it's grounded, it takes off to a flight height and cruises back and forth across the map like a projectile (harder to hit); after a flight-time timer it lands and resumes homing. Rinse and repeat until its health hits 0. The player CAN also hit it in the air (just harder). Passes through walls in both states.

## Sounds (theme folder: `builder/kombat/security jets/<type>/`, one theme ships: `jet`)

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
- **AIR (patrol):** patrol back and forth at the flight height, bouncing at the MAP edges (blind, not homing), playing `engine` — **x only on 2d**, and **BOTH x and y on 3d** (projectile-style diagonal roam: cur_x_step + cur_y_step, each axis flipping independently at its own edge, 0..maxx / 0..maxy). Weapon hits still chip health here but do NOT re-trigger takeoff (it's already up). (Dev clarified 2026-09: the 3d air patrol moves on x AND y like a projectile's diagonal directions, not x only.)
- **DESCEND:** when the `flight time` timer expires -> play `land` (one-shot), descend one tile per speed-step back to ground level, then resume GROUND homing.

Health <= 0 in any phase -> `death` + camera-style reward + remove.

**Locked inferred defaults:** starts grounded; rise/descend are GRADUAL (one tile per speed-step, for audible feedback — "up to height 5 as soon as you hit it" read as immediate takeoff, not teleport); the flight timer counts down regardless of whether the player keeps hitting it in the air; `hurt` suppressed on a killing blow; `land` plays ON TOUCHDOWN (dev 2026-09), not when the descent begins. **Flight height is CLAMPED to the map's vertical bound in the constructor** (`min(flightheight, maxy)` 2d / `min(flightheight, maxz)` 3d, `jet_vmax`) so the jet can never climb out of the top of the map, whatever an author or hand-edited line sets — covers ASCEND + AIR since both read the field (dev asked 2026-09). No lower floor (a flight height below ground level just skips the climb).

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
11. **flight time** — default `10000` (ms cruising before it descends)
12. **security jet sound** — list: `none` + the `jet` folder(s)
- **okay** / **cancel** buttons

## On-disk format

`jet x y [z] health attack firetime speed level xp flightheight flighttime jettype` — **12 tokens on 2d, 13 on 3d** (z after y). Field ORDER on disk follows the FORM order above. Brand-new keyword, so NO back-compat concerns. **On-disk keyword / build-menu id / spawn-despawn-build-unbuild command token = `jet`** (dev-chosen shorthand 2026-09, NOT `security_jet`), while the friendly DISPLAY name stays "security jet" and the runtime routing strings (spier is_obscured, tracker tracking_type, object-menu entry_type, obscurity_zone lists) stay `"security jet"` (space). SAME split the security camera has (token `security_camera` vs display `security camera`), just a shorter token. So: map line keyword `jet`; read/lenok/despawn/semantic dispatch key `jet`; map_menu entry_ids/buildtype/converted_3d/excluded_topdown all `jet`; but obscurity/spier/tracker/entry_type `"security jet"`. The friendly-name menu slot is alphabetical in the **kombat** category row (npc, projectile, security camera, security jet, tts enemie), so `jet`'s entry_id sits at that position by PARITY, not alphabetically among ids. jettype (sound-theme folder, last token) is also `jet` -- keyword and jettype are different positions, no conflict. [[feedback_alphabetize_builder_entities]].

## Build sections (~10, one per go-ahead, no re-presenting — [[feedback_describe_dont_show_code]])

1. **Class + globals + spawn/despawn/destroy_all + pool.** `sound_pool jetpool(...)`, `security_jet@[] jets`, phase constants (GROUND/ASCEND/AIR/DESCEND), the class, `spawn_security_jet`, `despawn_security_jet`, `destroy_all_security_jets`. Sentinel-null removal ([[project_stability_rules]]).
2. **read/write + parser dispatch + Tier-1 lenok (12/13).** `read_security_jet`, `write_security_jet`, dispatch in map_parser.nvgt (read dispatch, despawn dispatch, Tier-1 lenok 12/13).
3. **Build form** `build_security_jet` — the 11 inputs + sound list, NO checkboxes. Audition keys on the list (dev-confirmed 2026-09, AVOIDING the form-reserved Ctrl+A/C/F/G): **Space hurt, Ctrl+L loop, Ctrl+E engine, Ctrl+I flight, Ctrl+H hit, Ctrl+N land, Ctrl+D death.** The gallery (§9) and docs (§10) MUST use this exact set.
4. **`jetloop` state machine** — the four phases + melee, registered in game.nvgt's loop.
5. **Runtime integrations** — jetpool into all_pools (decpool.nvgt), effect_space apply_effect_pools, spier (announces the jet folder), obscurity_zone name lists, object-info menu (health + level, camera-style), tracker anchor, game_handlers object-menu gate.
6. **Destroy + reward + weapon/bullet/glider hit wiring [BUILT 2026-09].** `award_jet_kill` (xp-only, silent at 0) + `hurt_jet(i, dmg)` (play `hurt` UNLESS fatal, subtract health, and if GROUNDED+survived -> takeoff: `flight` cue + ground-loop->engine-loop swap + phase ASCEND; death itself is jetloop's top-check job, NOT inlined here -- container model). Scan-and-hit blocks: weapon.nvgt melee (new `best_type = 19` in the target scan + a `best_type == 19` apply block calling hurt_jet), bullet.nvgt (direct-hit block with cloner via spawn_security_jet + splash loop in try_bullet_splash, skip_kind `"jet"`), and glider.nvgt (a ram block after the camera's). **Glider ram ADDED (dev, 2026-09): jets ARE glider-hittable** (unlike the container, which traps you) -- "since jets do not trap you, it should be hittable with a glider." Grounded hit = takeoff; airborne hit = just chips health (no re-takeoff).
7. **Spawn/despawn/build/unbuild commands [DONE 2026-09, NO NEW CODE].** All five command paths already resolve `jet` from earlier sections: `/build` menu+no-args -> `buildobj("jet")` (map_menu, §3); `/build` inline + `/spawn` -> `normalize_buildtype("jet")`=`jet` -> `dispatch_entity_line`/`entity_line_error` (§2 read+lenok); `/despawn` -> `despawn_entity("jet")` (map_parser, §2); `/unbuild` -> `unbuild_entity` (GENERIC keyword match on `t[0]`, entity-agnostic). `normalize_buildtype` needs NO `jet` entry -- it only translates tokens that DIFFER from their keyword (e.g. `security_camera`->`camera`); `jet`'s token == its keyword, so it falls through `return buildtype`. This is the payoff of the `jet` token choice.
8. **Tier-2 semantic [DONE 2026-09]** — `security_jet_semantic_error` (position via coord_token_error, then health/attack/firetime/speed/level/xp/flightheight/flighttime is_number_token, then jet sound name_exists in `builder/kombat/security jets/*` or "none"; keyed is3d on length==13; mirrors read order). Dispatched in map_parser entity_semantic_error under `k=="jet"`. NO ranges/direction/flags.
9. **Gallery [DONE 2026-09]** — `security_jets` gallery_type added to the **kombat** category block (misc/gallery.nvgt), keys Space hurt / L loop / E engine / I flight / H hit / N land / D death. ALSO moved the `security_cameras` gallery_type from the traps block to the kombat block — REQUIRED by the folder move (gallery derives the sound path from the category, so a kombat-folder element must sit in the kombat block or it reads the empty old traps path). Container gallery_type STAYS in traps (it didn't move).
10. **Docs [DONE 2026-09]** — `sf/docks/builder/security_jets.txt` help topic created (CRLF, observable-behavior only, auto-listed by the help scan); maps.txt "Security jets." entry added to the **Kombat** section (after Security cameras); 15.0 changelog entry at top of block (561 chars; 15.0 now 15 entries). Noted to dev: a PRE-EXISTING maps.txt line (placeholder tokens, 1307 chars) is over the 1024 dock cap -- unrelated, left for the dev.

## Reference files (read before building)

- `src/includes/builder/kombat/tts_enemie.nvgt` — ground homing toward the player (ttseneloop, moves x/y/z toward me) + melee on the player's tile (firetime-gated, aircraft/vehicle/bike/glider guards, shield/reflection handling). NO wall check (moves through walls).
- `src/includes/builder/kombat/projectile.nvgt` — edge-bouncing line movement (cur_x_step/bounce_at_edge, projectile_at_edge), the hit-everything loop, and `award_projectile_kill` (the camera-style reward helper pattern + the death sites in bullet/weapon/glider that call it).
- `src/includes/builder/traps/container.nvgt` — the STRUCTURAL TEMPLATE: state machine (containerloop), pool + loopsound-swap, spawn/despawn/destroy_all, build form conventions, read/write, Tier-2, and the list of every runtime integration point. Copy its shape.
- [[project_container_plan]] — the as-built section list this plan mirrors. [[project_stability_rules]], [[feedback_builder_form_control_order]], [[project_angelscript_block_comment_star_slash]] (watch `*/` in glob comments).
