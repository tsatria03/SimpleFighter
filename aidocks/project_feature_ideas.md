---
name: project_feature_ideas
description: Living backlog of candidate FEATURE ideas and settled-but-unbuilt designs for SimpleFighter — maintain it whenever the dev settles a design, promotes an idea, or asks to brainstorm. These are candidates/plans, NOT shipped; the shipped record is changelog.txt and the todo list.
metadata:
  type: project
---

Living backlog of feature ideas and agreed-but-not-yet-built designs for SimpleFighter. These are CANDIDATES and PLANS, not commitments and not shipped — the durable shipped record is `sf/docks/main/changelog.txt`, and the committed intent list is `sf/docks/main/todo list.txt`.

**MAINTENANCE:** update this file whenever (a) the dev and I settle a feature's design (record it here as the plan), (b) the dev asks to brainstorm (add candidates), or (c) a feature ships (drop it from here — it becomes changelog/todo history). Follow [[feedback_confirm_before_implementing]] — a settled design here is still a plan to get final sign-off on before coding, not a green light.

---

## Slant — a directional ramp/incline builder entity (DESIGN SETTLED 2026-08, not yet built)

A new **construction** builder entity. Modeled on the "slant" in an external reference game (its map-syntax glossary), adapted to SimpleFighter's conventions. Design was walked through and settled with the dev; the pieces below are agreed.

**Build status (2026-08, in progress, section-by-section):** DONE — §1 data+lifecycle, §2 read/write, §3 build form, §4a floor-tile spawning (diagonal ramp + top landing), §4b `slantcheck` walk-across elevation mechanic (all in `src/includes/builder/construction/slant.nvgt`). Note (fixed 2026-08): footstep sounds for steps *along the ramp axis* are played inside `slantcheck` on the snap (via `get_all_platform_tiles`, matching `playstep`), because `playstep()` runs during the horizontal step at the **pre-snap** height and finds no tile there yet — so it stays silent (perpendicular/flat steps still sound via `playstep` normally). PENDING — §5 wiring (construction menu entry between platform & staircase, parser dispatch, **`slantcheck()` call placed immediately before `fallcheck()`** in game.nvgt, `destroy_all_slants()` in clearmap), §6 docs (`slant.txt` help topic + changelog under the open 14.3), §7 slant-aware jump landing (test first — likely unneeded; see below).

**What it is.** A region you walk across that changes your **elevation** as you move — it raises (or lowers) you by a set **step height** for every tile you move along it. Think of it as a staircase you climb by walking *sideways* instead of pressing up: you set how tall each step is, and moving across it carries you up or down automatically. It sits on SF's whole-level grid — each tile you move lands you on a whole level.

**You move yourself horizontally; the slant moves you vertically.** The horizontal direction you walk never changes on its own — your stepping does that. The slant only changes elevation: **y** on 2d maps, **z** on 3d maps.

**Modes.**
- **2d** — elevation is `y`. Walking left/right (x) changes `y`.
- **3d** — elevation is `z`. Walking left/right (x) or forward/backward (y, the flat ground) changes `z`.
- **topdown** — NOT offered. No elevation axis, so a slant has nothing to change (same reason jumping/hooking are disabled on topdown). The builder simply won't list it.

**Geometry (footprint + single base height).** A slant is a **horizontal footprint plus one base height**, with the rise **computed** from step height — there is **no** min/max on the climbing axis (unlike the staircase's min/max block). 2d footprint = `min/max x`; 3d footprint = `min/max x` **and** `min/max y` (a rectangular ground area — the ramp rises along the direction axis and stays flat across the other). The **base height** is the elevation of the ramp's low end (a single value: `base y` on 2d, `base z` on 3d); each tile toward the high end is `step_height` higher, and the top height falls out of the math.

**Direction list (mode-aware, SF's own vocabulary — never compass words).** SimpleFighter uses left/right/forward/backward/up/down, not north/east/etc. (confirmed against `conveyor_belt.nvgt`'s mode-aware direction list — the pattern to copy). Each base direction is shown with **up** or **down** appended, read **literally as an instruction**: *"walk THIS way → go THIS way,"* and the opposite walk always does the opposite.
- **2d:** left up, left down, right up, right down (4 labels).
- **3d:** left up, left down, right up, right down, forward up, forward down, backward up, backward down (8 labels).

A ramp is a **two-way slope**: whichever way climbs, the opposite descends — automatically, so there is no "one-way" ramp and down-ramps need no special option (you walk the downhill way). Because a ramp can be named from either end, some labels are the **same physical slope** (e.g. "left up" ≡ "right down", "forward up" ≡ "backward down"); the duplicate phrasings are kept on purpose so the author picks whichever matches how they picture walking it. (This mirrors that reference game's `east_up`/`west_down` style, in SF words.)

**Step height.** How many whole levels of elevation you gain or lose for **each tile** you move along the slant's direction. **Whole numbers, 1 and up** — **1 is the default** (up one level per tile — the gentlest, a 45° climb); higher = steeper (e.g. 5 = up five levels per tile: x1→5, x2→10, x3→15…). Below 1 isn't possible — a half-level has no floor on SF's whole-level grid — so there's no sub-45° slope. The **form field defaults to `1`.**

**Two surface pickers — each optional, "none" opts out** (so the author chooses per-slant whether the slant builds its own floor or they build it). Each is a full "tile group" modeled on the `build_platform` / `build_staircase` forms — a tile list + tile volume + tile pitch sliders, with the standard preview (space = step, Ctrl+L = land, Ctrl+H = fall). Reuse the shared `builder/construction/platforms/` tiles, so **no new audio is needed**.
- **Bottom surface** — the sloped floor the slant lays under you as you climb, so you don't fall through the ramp itself. "none" → the author builds the ramp floor themselves.
- **Top surface** — the flat landing laid at the high end, so reaching the top of the ramp gives you ground to stand on instead of walking off into thin air. "none" → the author builds the landing themselves.
- **Walls are always the author's job** — if a player could walk off a side/edge and you want to stop them, you build that wall. The slant never makes walls.

**Builder form order.** Follow the standard control order ([[feedback_builder_form_control_order]]): **all input boxes first** — footprint (min/max x, plus min/max y on 3d), then **bottom height** (form label; internally `base_height`; defaults to `0` — the low end's elevation, ground level), then **slope amount** (form label; internally `step_height`; defaulting to `1`) — then the **direction** list, then the **bottom surface** and **top surface** groups (each a tile list + volume + pitch sliders), then any checkboxes, then the okay/cancel buttons. Note the step-height input sits with the other inputs *before* the direction list, not after it. Region-input/mode-branch pattern as in `build_staircase`/`build_platform`.

**Runtime mechanic.** When the player moves a tile along the slant's axis while inside the region, adjust `me.y` (2d) / `me.z` (3d) by ±step_height — up in the uphill direction, down the opposite (bidirectional by nature). Key off the player's **actual position change along the ramp's axis, not the key pressed**: 3d/topdown movement is **body-relative** and forward/back go through `body_step()` (there is **no** `step_forward`/`step_backward`), so react to whether `me.x`/`me.y` actually changed. `step_left`/`step_right` (`map.nvgt`) handle the x axis. Play the bottom-surface tile's step sound on each rise/fall.

**Placement & conventions to honor when built.**
- New file `src/includes/builder/construction/slant.nvgt`, alphabetized in the construction menu — between **platform** and **staircase** (verify exact slot) — per [[feedback_alphabetize_builder_entities]].
- Mirror the staircase entity structure: class + `slant@[] slants(0)` array, `spawn_/read_/write_/build_slant`, a per-frame `slantcheck()`, and `destroy_all_slants()` **wired into `map.nvgt`'s cleanup run** ([[project_include_tree]]).
- Sentinel-null removal + guards on the entity array; use the audio form — per [[project_stability_rules]]. Unlike the staircase's fill-the-column per-z spawn, the slant's bottom surface is a **diagonal run of tiles** — one floor tile per horizontal step at that step's whole level — so it follows the incline; the top surface is a flat landing at the high end.
- Map line is **space-delimited with mode-dependent length variants** (2d vs 3d), gated in `map_parser.nvgt`; honor the read_/write_ back-compat contract — see [[project_map_format]] and [[project_stability_rules]]. Field order — **2d** (length **12**): `slant minx maxx base direction step_height bottomtile bottomvol bottompitch toptile topvol toppitch`; **3d** (length **14**) inserts the `miny maxy` footprint: `slant minx maxx miny maxy base direction step_height bottomtile bottomvol bottompitch toptile topvol toppitch`. `base` = the low-end elevation (top is computed, not stored); a surface's tile is `none` to opt out. `direction` is a no-space token (`leftup`/`rightdown`/`forwardup`/…).
- New help topic: drop a `sf/docks/builder/slant.txt` — it auto-appears in the help menu ([[feedback_tp_prose]]).
- On ship: changelog entry + version bump ([[feedback_changelog_rules]], [[feedback_update_build_version_txt]]).

**Resolved (design):** step height is whole-numbers-1-and-up (rise per tile), so the player always lands on **whole levels** — no fractional heights. The bottom surface is a **diagonal run of floor tiles** (one per step) that supports you the whole way up, so there are no unsupported "in-between" heights mid-ramp. Movement reacts to the actual axis position delta (body-relative; `body_step`).

**Still open (implementation detail):**
- Exact map-line field order and the precise `sd.length()` variants per mode.
- **Resolved:** the ramp/landing surfaces are always **plain non-destroyable, non-overlap** floor (dev decision 2026-08) — no destroyable/overlap/health fields on the class or form; spawn the floor tiles as non-destroyable, non-overlap platforms. (Overlap is offered only by platform & staircase; destroyable by platform/staircase/wall/door/sign/clock/calendar/spike/projectile — a slant needs neither.)
- **Slant-aware jump landing (§7) — likely UNNEEDED; test first (finding 2026-08).** Correction to an earlier worry: the slant's floor tiles are spawned **non-backing** (§4a), and the jump-landing code lands on any `user_platform_at(...)` hit (`game_handlers.nvgt:738, 805, 848`) — which **does** see non-backing tiles. So the existing landing already handles slant tiles; `slantcheck` re-attaches (`player_slant`) the next frame. The staircase needed its `is_staircase_top`/`in_staircase_volume` predicates ONLY because its tiles are **backing** (hidden from `user_platform_at`) — that problem doesn't apply here. Plausible-but-unverified quirk: on a **step-height-1** ramp, a jump may re-land on the next tile up almost immediately (feels like small hops). **Decision: wire it up (§5), jump-test on a real ramp, and only add §6 if testing shows a real problem** — don't write speculative jump-landing edits into load-bearing code that we can't verify yet.

---

## Tile zone — an invisible region that overrides ground behavior (DESIGN SETTLED 2026-08, not yet built)

A new **zone** builder entity. Ported from an external reference game's tile zone (documented in its own tile-zone guide), trimmed to SimpleFighter with the dev. Design settled; get final sign-off before coding.

**What it is.** An **invisible rectangular region** that changes how the **ground you stand on** behaves — no platform, no wall, nothing to see or bump. It just quietly overrides properties of the tiles underfoot inside its box. Every knob is optional: set only what you want changed, leave the rest normal.

**Knob set (all optional; final — fall damage settled as "Option A", knob names locked 2026-08):**
- **surface** — which tile the zone targets, picked from a **list** of the platform tiles (same source as the platform/staircase tile pickers, `builder/construction/platforms/*`), with **`any`** at the top as the default. `any` → the overrides apply to **every** tile in the box; pick a specific tile (e.g. `ice`) → only that tile type triggers them (other ground in the box is untouched). **Floor tiles only** — no walls in the list (walls went out with pitch).
- **speed** — walk speed on those tiles (the mud/ice/sand feel). SF's `modspeed` scale (**1–20, higher = faster, SF normal 5**) — NOT the reference game's milliseconds. Overrides the player's live speed while on the tile.
- **jump height** — jump limit/boost in the zone. Range **0–20** here: **`0` = no jumping at all** (a low-ceiling/crawlspace/"no-jump" patch — something the player's own F-keys can't do, since they clamp to 1–20), `1–20` = a forced jump height, SF normal 5. (`0` is a real value; the separate "leave unchanged" sentinel is `-1`, so they don't collide.)
- **fall distance** — how many squares you can fall onto this ground before it hurts, i.e. the **hard-landing threshold** (SF normal **8**: a drop of fewer than 8 is a free soft landing, 8+ is a damaging hard landing). Lower = short drops sting; higher = long safe falls (near-fall-zone, but tunable).
- **fall damage** — the **multiplier** for how hard each fallen square hits once a fall crosses the threshold (overrides `fallmod`, SF normal **21**; it's a multiplier × distance, not a flat amount). Higher = brutal ground; lower = gentle.

Fall damage was settled as **Option A**: SF has no flat "normal-landing damage" (short landings are free) — just one multiplier (`fallmod`) plus the hard-fall threshold — so the reference game's `land_damage`/`hardland_damage` split was replaced by these two SF-native knobs (**fall distance** = the threshold, **fall damage** = the multiplier).

**Form defaults & baselines (dev-settled 2026-08).** Every knob's form field defaults to **"leave unchanged"** (the `-1` sentinel for the numeric knobs, `any` for surface) — **NOT** to the normal value. A zone touches only the knobs the author actually sets; this is what protects the player's own live speed/jump settings (an unset knob leaves them alone) and what makes layering work (an unset knob falls through to an outer zone). The **normal baselines** — speed **5**, jump height **5**, fall distance **8**, fall damage **21** — are simply what "leave unchanged" gives you, and must be **written into the help topic** so authors know what they're deviating from. A tile zone with **every knob left unchanged does nothing** — a harmless no-op that just defines an empty region (matches the reference game). (Contrast the slant's `step height`, which is a *required* field with a real default of `1`.)

**Dropped on purpose (dev decision):** **volume and pitch**. The platform/staircase build forms already give the author per-tile volume + pitch sliders, so a zone override would duplicate an author tool that already exists. And since **pitch was that game's only wall-affecting knob**, dropping it means the tile zone **never touches walls at all** — it's purely about the ground you stand on. That's the guiding rule we used: **keep a knob only if there's no author-side, area-specific control for it already** — volume/pitch have one (the build form) → dropped; speed/jump height do NOT (only the player's global A/D/F and F1–F3 keys exist, which are the player's own preference, not an authoring tool) → kept.

**Three behaviors (all kept from the reference game):**
1. **Surface filtering** — blank surface = every tile in the box; a named tile = only that tile type triggers the overrides.
2. **Layering** — when zones overlap, the **later-defined** zone wins on any knob they both set; a knob the inner zone doesn't set still uses the outer zone's value. Lets you carve exceptions (a big slow-swamp zone with an even-slower pocket inside).
3. **Auto-reset on exit** — step off the zone's tiles and every override lifts on its own (no "reset zone" needed). For **speed specifically**, it restores the **player's own** A/D/F speed, not a fixed map default, so their personal preference returns intact; jump height likewise restores the player's own F-key value.

**SF mapping / conventions when built.**
- New file `src/includes/builder/zones/tile_zone.nvgt`, alphabetized in the zones menu (verify slot — likely just after "text zone"), per [[feedback_alphabetize_builder_entities]].
- Mirror an existing zone entity (e.g. `safe_zone`/`heal_zone`) for the class + `tile_zone@[] tile_zones(0)` array + `spawn_/read_/write_/build_tile_zone` + `destroy_all_tile_zones()` **wired into `map.nvgt` cleanup**, with sentinel-null removal and guards ([[project_include_tree]], [[project_stability_rules]]).
- Runtime hooks: the movement/step speed path, the jump handling (`jumpheight`), and the fall/land-damage path — all in `map.nvgt`/`game_handlers.nvgt`. Each frame/step, find which tile zone(s) cover the player's tile, merge their overrides with **layering (later wins)** after applying the **surface filter**, apply speed/jump, and restore on exit.
- Map line is **space-delimited with mode-dependent length variants** ([[project_map_format]], [[project_stability_rules]]). Because SF's format is positional (not that game's `key=value`), every field is always present, so use a **sentinel for "no override"**: `-1` for the numeric knobs and `none` for surface (that game itself already documents `-1` = "leave normal", so this matches). Rough shape (exact order TBD): `tile_zone minx maxx miny maxy [minz maxz] surface speed jump_height fall_distance fall_damage`.
- New help topic `sf/docks/builder/tile_zone.txt` (auto-appears — [[feedback_tp_prose]]) — must state the **normal baselines** (speed 5, jump 5, fall distance 8, fall damage 21), that a knob left unchanged leaves that property normal, and that a zone with no knobs set does nothing. Changelog entry on ship (14.3 is already open, so no new version bump needed unless it's rolled forward — [[feedback_changelog_rules]], [[feedback_update_build_version_txt]]).

**Key integration points (from a read-only code survey — the whole feature is a save-override-on-enter / restore-on-exit layer over three plain globals):**
- **Speed** → global `modspeed` (`game.nvgt:4`, 1–20, default 5), re-consumed into `walktime`/`runtime` every frame at `game.nvgt:116-125`. Save on enter, override while inside, restore on exit — applies instantly.
- **Jump height** → global `jumpheight` (`game.nvgt:4`, default 5), read only at jump start (`game_handlers.nvgt:711`). Same save/override/restore.
- **Fall distance + fall damage** → in `fallcheck()` (`map.nvgt:938`): the hard-fall threshold is `fallcounter >= 8` (below it, landings are free) and the multiplier is `fallmod` (`map.nvgt:10`, default 21). Override the threshold (fall distance) and `fallmod` (fall damage) by zone membership **symmetrically in BOTH the 3d branch (~:1008) and the 2d/topdown branch (~:1129)**, restoring after the landing so it never leaks. `fall_zone`'s `player_in_fallzone()` (`fall_zone.nvgt:16`) is the precedent for special-casing landings.
- **Tile filter** → `gmt(me.x, me.y)` / `gmt(me.x, me.y, me.z)` (`mapfuncts.nvgt:185`/`:209`) returns the platform tile name underfoot; match it against the zone's `surface`.
- **Scaffold** → mirror `heal_zone.nvgt` (class + `@[]` array + `player_in_tilezone(i)` + spawn/read/write/build/destroy_all). Zone arrays are compacted (no null-guard). Register a per-frame `tilezoneloop()` at `game.nvgt:88` (beside `healzoneloop();`), and `destroy_all_tilezones()` in `clearmap()` (`map.nvgt` ~:83-100) — which must also restore any active override (the player could be standing in a zone at unload). Files under `builder/zones/*` auto-include via `includes.nvgt:17`.
- **Menu** → `map_menu.nvgt`: add `"tile zone"` (display, `:488`) and `"tile_zone"` (id, `:500`, same index) **between `story_zone` and `text_zone`**; add a `build_tile_zone()` branch in `buildobj` (~:429-471); add `"tile_zone"` to `converted_3d` (`:502`) to allow it in 3d.
- **Parser** → `map_parser.nvgt`: `else if(sd[0]=="tile_zone" && (sd.length()==N2d || sd.length()==N3d)) read_tile_zone(sd);` — 2d has no z; 3d adds `minz maxz` (+2 tokens).

**Still open (implementation detail):**
- Exact positional field order + the `sd.length()` variants per mode, and the `-1`/`none` sentinel handling in `read_tile_zone`.
- The per-frame layering merge (iterate covering zones, later-defined wins per knob) after the surface filter.
- **Jump height `0` must be a clean "can't jump"** — suppress the jump attempt entirely (no stunted 0-height hop, no stray jump sound), not merely set `jumpheight = 0` and let the jump play out. Restore the player's own jump on exit as normal.
- **Topdown — resolved:** the zone IS offered in topdown, but its form shows only **surface + speed** (jump height and the two fall knobs are altitude-based and inert there, so they're hidden from the topdown form). Simplest on-disk approach: still write all payload fields, with the hidden knobs at their `-1` sentinel in topdown — final field/length layout TBD in Stage 1 (mirror `heal_zone`'s per-mode coords).

---

## Candidate ideas (not yet designed)

**Builder comparison against an external reference game — completed 2026-08.** Every builder element in that game was checked against SimpleFighter's full set, filtered by SF's **no-element-IDs rule** (effect space is the only ID-using entity). Conclusion: only **Slant** and **Tile zone** (both designed above) are worth adding — everything else is already in SF under another name, is online-only, or is locked behind an ID/trigger ("interactable") system SF deliberately doesn't use. Lesser, more-involved maybes noted but not designed: playable **instruments**, and a **timed-map** (countdown) map setting. No need to re-run this survey.

_(No other candidates yet — add here when the dev brainstorms.)_
