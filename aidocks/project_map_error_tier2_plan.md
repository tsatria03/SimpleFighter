---
name: project_map_error_tier2_plan
description: Full sequencing plan for Tier 2 of map error checking — per-entity SEMANTIC validation (wrong-type fields, out-of-bounds coords, nonexistent tile/npc/sound names, bad ranges) layered on the shipped Tier 1 structural checker. 8 sections (~12–16 commits), one entity/cluster per commit. NOT STARTED.
metadata:
  type: project
---

Plan for **Tier 2 of map error checking** — the value-level, per-entity semantic validation that Tier 1 deliberately skips. **NOT STARTED** (Tier 1 shipped in 14.4 — see [[project_map_error_template]] for the shipped foundation this builds on). Build one section at a time, confirm each before coding ([[feedback_confirm_before_implementing]]), commit between sections ([[feedback_stage_commits_before_big_changes]]).

## What Tier 2 catches (that Tier 1 passes)

Tier 1's `entity_line_error()` (`map_parser.nvgt`) confirms only that the object is recognized and has the right *number* of fields. Tier 2 judges the *values*:

- **Wrong-type fields** — a numeric field holding text (`platform 5 ten 0 …`).
- **Out-of-bounds coordinates** — an object placed past the map's minx/maxx/miny/maxy (and minz/maxz in 3d).
- **Nonexistent referenced names** — a tile, npc category/subtype, sound folder, weapon, shield, or item name that isn't a real asset on disk (the `marble4`-when-only-`marble1..3`-exist case).
- **Inverted/invalid ranges** — a ranged object whose min > max.
- **Out-of-range values** — a direction id outside its set, a volume/pitch outside its allowed range, a mode-value mismatch, etc.
- **Malformed quoted text** — doors, passages, signs where quotes are missing/unbalanced and Tier 1 only sometimes catches it via field count.
- **The Tier 1 known gaps** — `>=N` entities can't catch "too many tokens", and a few length ranges overlap between modes; a per-entity checker that knows the exact expected layout for the current mode tightens these.

Framing: **Tier 1 catches mistakes that make a line disappear; Tier 2 catches mistakes that make a line wrong** (placed, but with a value the game can't use).

## Integration (how it bolts onto Tier 1)

- A **second validation pass**: after `entity_line_error(sd, mode)` returns "" (structurally OK), run a new `entity_semantic_error(sd, mode)` that returns "" or a reason. The collector (`collect_map_file_errors`, `report_single_map_line`) calls both — structural first, semantic second — and reports whichever fails. **Everything else is reused unchanged**: the `Map errors` box, `present_map_errors`, `map_error_block`, the `/maperrors` (`/ms`) command, all authoring/load hooks.
- **The column finally gets used.** The Tier 1 template reserved `line: N (col)` and Tier 1 never fills the column (whole-line errors). Tier 2's reasons point at the offending field, so extend `map_error_block` to accept an optional 1-based field index → `line: 8 (3)`. Reasons stay plain-english ([[feedback_tp_prose]]), e.g. "the 3rd value must be a number", "this tile does not exist", "this coordinate is outside the map".
- **Lookups resolve like the spawn does.** Bounds come from the map globals (minx… already loaded). Name-existence uses the same disk resolution the entity's `read_`/`build_` uses (`find_directories`, `get_map_sound_folders`, map-first-then-global for npc types, per-map musics/sources for audio). Decompiled maps only (same gate as Tier 1).

## Shared foundation, then per-entity field maps

The checks are generic; only the **field map** (which token is a coord / tile / number / range / name-of-kind-X) is per-entity. So §1 builds the reusable machinery and one pilot; later sections mostly *declare each entity's field shape and call the shared checks*. Shared helpers to build in §1: `is_number`, `coord_in_bounds(axis,val)` (mode-aware), `range_ok(min,max)`, and name-existence checks (`tile_exists`, `npc_type_exists`, `sound_clip_exists`, extended as needed).

**Validator gotchas (bake into §1, from the 2026-08 survey):**
- **Sentinels accepted WITHOUT a disk lookup:** `none`, `any`, `random`, empty string, and numeric `-1` (tile_zone "unchanged"). A naive name/number check false-positives on these — whitelist them per field.
- **`random(low,high)`** is a valid token in ANY numeric field (it expands at load), so the number check must accept it, not flag it.
- **Names resolve to on-disk folders** (sound / tile / item / npc / template) via `get_map_sound_folders` / `find_directories` / glob under `sf/sounds/.../builder/...` or the map's own `assets/` — the single most-repeated expensive check; resolve exactly as that entity's `read_`/`build_` does (map-first-then-global where applicable).
- **The HARD quoted-text entities** (door, passage, travelpoint, switch, sensor, the blockers) use `extract_quoted` + length-branched tail parsing for back-compat, so field positions are NOT fixed by index — a per-field validator must mirror the read function's own shape auto-detection, never assume a positional schema.

## Sections (all 72 parser keywords assigned)

Entity count from `dispatch_entity_line`'s keyword table = **72 distinct objects** (matches the ~73 builder-entity files). Grouped by shared field-shape:

- **§1 — Foundation + graduated pilot (walking skeleton).** Build the machinery on the simplest entities so each step adds exactly one new check type (order set by the effort survey below): (a) **spawnpoint** (coords only) → the `entity_semantic_error` second pass wired into the collector, `map_error_block` column support, `is_number` + `coord_in_bounds`; (b) an **easy entity** such as **fall_zone** (ranged box, no names) → adds `range_ok` (min≤max); (c) **checkpoint** (coords + one number + one sound folder) → adds the first `name_exists` disk lookup. Platform and the rest of geometry then confirm it all in §2. These three pilot entities are DONE in §1, so their cluster sections skip them (fall_zone out of §3, spawnpoint + checkpoint out of §8). (was originally "platform pilot"; reordered to the spawnpoint→fall_zone→checkpoint ramp after the 2026-08 survey — platform bundles coords+ranges+tile-name+numbers all at once, too big a first bite.)
- **§2 — Construction / tile-painted geometry.** wall, staircase, slant, mplatform (moving platform), vanishing_platform, belt (conveyor belt). (6)
- **§3 — Zones (box + knobs).** safe_zone, fall_zone, heal_zone, flux_zone, tile_zone, text_zone (and `zone` alias), story_zone, obscurity_zone, menu_zone. (9)
- **§4 — Audio.** sound_source, sound_ambience, url_source, url_ambience, timed_source, timed_ambience, excludable_source, excludable_ambience, speaker (each single + ranged; clip-name existence in the map's musics/sources). (9)
- **§5 — Traps.** fire, wind, spike, hazard, mhazard, vanishing_hazard, mine, bomb, time_bomb, bomb_zone, force_field, floor_breaker, projectile, projectile_zone, camera (security camera). (15)
- **§6 — Transitions & transport.** door, passage, elevator, el_floor, lift, teleporter, trampoline, travelpoint, blockage, bike, vehicle, aircraft, airbeacon, air_turbulence. (14; the most bespoke — quoted text in door/passage/blockage/elevator, travelpoint references another map).
- **§7 — NPC / combat references.** npc, npc_zone, ttsenemie (the category/subtype-existence checks; ttsenemie's spoken-text fields). (3)
- **§8 — Interaction & one-offs.** sign, text_square, clock, calendar, switch, sensor, checkpoint, spawnpoint, item, item_zone, chblocker, cblocker, timed_text, effect_space, tpl (template). (15; quoted text, command/setting lists, item names, effect params, template existence).

Total: 1 + 6 + 9 + 9 + 15 + 14 + 3 + 15 = **72**.

## Effort ranking (full survey 2026-08)

A read of every `read_*` function classified all 72 entities by validation cost. This sets the build ORDER (cheap tiers first) and confirms which shared helper each entity needs — a cross-cutting view over the category sections above (the sections are the commit buckets; the tiers are the difficulty order).

- **TRIVIAL (1) — coords only:** spawnpoint.
- **EASY (5) — coords + numbers only, no disk lookup, no quoted text (ranged min≤max is the only extra):** fall_zone, air_turbulence, airbeacon, url_source, url_ambience. (url_* carry a web URL, not verifiable on disk.)
- **MODERATE (30) — exactly one name-existence check (or one enum-membership), possibly ranged:** platform, staircase, vanishing_hazard, safe_zone, trampoline, time_bomb, heal_zone, tile_zone, flux_zone, hazard, mine, mhazard, checkpoint, spike, aircraft, camera, floor_breaker, fire, wind, force_field, projectile, bike, bomb, bomb_zone, projectile_zone, teleporter, vehicle, menu_zone, item, item_zone.
- **INVOLVED (14) — ranged/multi-box coords + two on-disk names (tile + sound, or category + sub-folder):** slant, vanishing_platform, wall, tpl, sound_ambience, sound_source, speaker, excludable_ambience, excludable_source, timed_ambience, timed_source, lift, mplatform, belt.
- **HARD (22) — quoted free-text, comma command/setting lists, or cross-references.** Lightest (quoted display text only — almost no semantic check; hard only because free text bypasses the numeric/name checkers): blockage, el_floor, text_square, timed_text, text_zone. Quoted text + one name: sign, clock, calendar, story_zone, elevator. Setting/command lists (validate each token against a fixed set): obscurity_zone, chblocker, cblocker. Cross-references / interpreters (heaviest): door, passage (lockmode + item-spec + password), travelpoint (destmap must exist), switch, sensor (quoted commands run by the builder command interpreter), npc, npc_zone (path+category+subtype → npc info.sif pack), ttsenemie (4 quoted TTS strings incl. a system-voice), effect_space (effect-type enum with a length-gated DSP-param contract).

Note (corrects an earlier assumption): **checkpoint is MODERATE, not "easy"** — it carries a sound-folder name, so it's the first name-existence entity, which is why it sits third in the §1 ramp (after spawnpoint and an EASY entity), not second.

## Section count & commit estimate

**8 sections.** §1 (foundation) is the only hard-dependency; §2–§8 can be tackled in any order and layer on independently. The three fat sections — §5 traps (15), §6 transitions/transport (14), §8 one-offs (15) — will each likely split across 2+ commits, so the realistic total is **~12–16 commits**. The hardest work is concentrated in: the **name-existence lookups** (tiles, npc types, sounds — §1/§4/§7), the **quoted-text entities** (§6/§8), and **§6**'s bespoke shapes.

## Conventions when built

- Confirm each section's scope before coding; commit per entity or per small like-group ([[feedback_confirm_before_implementing]], [[feedback_stage_commits_before_big_changes]]).
- Keep the semantic mirror in sync with the entity's real read/build field order ([[project_stability_rules]] — the same drift risk as the Tier 1 validator twin).
- Player-facing reason strings only, no internals ([[feedback_tp_prose]], [[feedback_one_sentence_game_messages]] spirit).
- **Docs on ship (dev-decided 2026-08):** a SINGLE consolidated changelog entry once the WHOLE of Tier 2 is in place — NOT one per section or per entity (72 near-identical entries would blow the per-version cap and each entity is the same player-facing story). Phrase it as improved/advanced map error reporting that now also catches value problems (bad numbers, out-of-bounds coordinates, names that don't exist). At the same time, update the maps.txt "Checking a map for errors" caveat that currently says the check does NOT judge the values themselves. Version bump if the entry opens a new version block ([[feedback_changelog_rules]], [[feedback_update_build_version_txt]]). No new help topic — it extends the Tier 1 one. (During development the per-section commits carry no changelog entries; the record lands only when the feature is complete.)
