---
name: project_instrument_simulator_port_plan
description: Record of porting the standalone Instrument Simulator (a keyboard piano/drum toy the dev pulled from the builder years ago and spun off into its own app) back into SimpleFighter as the "instrument" builder object. SHIPPED in 14.6. The port allows recording and playback only, NOT saving or loading recordings, on purpose. Captures the as-built design and where it diverged from the original plan.
metadata:
  type: project
---

The **Instrument Simulator** is back in SimpleFighter as the **instrument** builder object, shipped in **14.6**. It was once an in-builder feature (play drums and piano on the keyboard for fun); the dev removed it years ago and rebuilt it as a separate app, then ported that modernized app back in section by section (2026-09-04). The standalone app that seeded this (`C:/Users/tonys/OneDrive/Desktop/InstrumentSimulator-src/...`) has since been **deleted** by the dev — SF's copy is now the only one. This doc is the as-built record; the code is the source of truth.

## The deliberate scope decision (still load-bearing)

**The SF instrument lets you RECORD and PLAY BACK a performance, but NOT save or load recordings. This is on purpose.** The standalone's recorder could `save()` a performance to an encrypted `.rec` file and `load()` it back through a file menu; those paths (and their Alt+S / Alt+L hotkeys, `input_box`, the recordings directory, and the encryption key) were **dropped**. What shipped: **Alt+R** to record (after a 3-2-1 countdown + beep), **Alt+Return** to stop, **Alt+P** to play back, **Return/R** to stop playback. A recording lives only until you leave the map or record over it — no files land in SF's data.

**Why:** the dev wants the instrument to stay a lightweight fun feature, not a mini-DAW that writes files. Recording is for immediate playback in the moment, not for building a library.

## As-built layout

- **`src/includes/builder/interaction/instrument.nvgt`** — `class instrument` (spatial entity + all playing logic), the `instrument@[] instruments` / `spawn_instrument` / `destroy_all_instruments` trio, `instrumentcheck()` (per-frame activation), `cycle_instrument_folder()`, the `read_*`/`write_*`/`build_instrument()` map+form functions, and `instrument_semantic_error()`. Declares the global `sound_pool instpool;`.
- **`src/includes/builder/interaction/instrument_recorder.nvgt`** — `class inst_recorder` (record/playback only). The global instance is `inst_recorder instrec;` in `dec.nvgt`.
- **`dec.nvgt`** — added `inst_recorder instrec;`. **`decpool.nvgt`** — `instpool` added to `all_pools` (gets mixer, listener updates, pause/resume for free). **`map.nvgt`** — `destroy_all_instruments()` in the teardown block. **`game.nvgt`** — `instrumentcheck()` in the per-frame dispatch (after `hazardcheck`).
- **Sounds:** `sf/sounds/decompiled/builder/interaction/instruments/{pianos,drums,others}/<name>/` — pianos and others hold `p1..p36.ogg`, drums hold `d1..d36.wav` (not every folder fills all 36; a missing note is silent). Loaded via `get_map_sound(...)` / `get_map_sound_folders(...)`, so map-asset instrument folders and compiled packs both work — authors add an instrument by dropping in a folder.
- **Docs:** help topic `sf/docks/builder/instruments.txt`; `maps.txt` interaction list entry; readme "Customizing audio" catalogue entry.

## How it works (as built)

- **Category: interaction.** The build-menu "instrument" sits in the interaction tab between clock and item (`map_menu.nvgt`: `entry_names`/`entry_ids` row 3, plus `converted_3d` so it's kept on 3d maps; NOT in `excluded_topdown` since it works on topdown). Category is about how the player relates to the entity (operated, like sign/clock/item), not that it outputs sound.
- **Activation:** stand on the tile/area and press interact (`instrumentcheck()` uses `controls.action_pressed("interact")` — one-shot, not the `action_repeating` the non-modal interaction entities use, so holding interact can't re-open right after Escape). `play_mode()` calls `pause_game()`, says "Instrument opened. Currently on <category>, <instrument>.", runs a self-contained `wait(5)` loop of `instrec.recordcheck()` + `update()` until Escape, then `instpool.destroy_all()` + `resume_game()` + "Instrument closed." Per-instance state (category, instrument, pedals) persists between openings until the map closes.
- **Playing:** 36 notes across the number/letter rows (`note_keys` table). **Tab** cycles THREE categories — pianos, drums, **others** (others is melodic, uses `p<N>.ogg` like pianos). Left/Right change instrument within a category (each category remembers its own). Held Up/Down bend pitch, release snaps back. **Enter** = overlap pedal (notes ring together into chords vs cut). **Backslash** = staccato pedal (cut on key release vs ring out). UI-feedback clips come from `get_pack_sound("main/misc/...")`.
- **Recorder event model:** `delay:P:cad:pitch:path` (note-on), `delay:S:cad` (note-off), `delay:B:pitch` (bend), where cad is 1/2/3 for pianos/drums/others. Playback tracks a per-category ringing slot so articulation and bends reproduce. Legacy record-format fallbacks were dropped (fresh, session-only).
- **Effect spaces:** ONE registration line in `apply_effect_pools()` (`effect_space.nvgt`): `apply_all_effects(me.x, me.y, instpool, me.z)`, in the player-centric cluster with `p`/`hookpool`/`sonarpool` — notes play stationary at the player who operates and hears it. Live playing and recorder playback both route through `instpool`, so one line covers both.
- **Spier + obscurity:** `spy_check_entities()` (`spier.nvgt`) announces "instrument" / "N x M tile instrument", gated by `is_obscured("instrument","spier")`; "instrument" added to `spier_entities` in `obscurity_zone.nvgt`.
- **Map line (pure coordinates):** single `instrument x y [z]`, ranged `instrument minx maxx miny maxy [minz maxz]` (z only in 3d; topdown treated like 2d). Parsed by `read_instrument`/`read_ranged_instrument`, written by `write_instrument`/`write_ranged_instrument`, built by `build_instrument()` (single/ranged build-mode list, coords only).
- **Map errors:** Tier 1 `entity_line_error()` in `map_parser.nvgt` recognizes `instrument` with counts `3||5` (2d/topdown) / `4||7` (3d); Tier 2 `instrument_semantic_error()` (in `instrument.nvgt`, dispatched from `entity_semantic_error()`) validates each coordinate token and, for ranged, max ≥ min per axis.

## Where it diverged from the original plan

- **Not breakable** — no `destroyable` field (dev's call). The map line is coordinates only; no trailing flag. So the entity-menu destroy path never applies.
- **Third category "others"** was added (the plan assumed just pianos/drums); it carries through `instcad==3`, `otherslot`, the recorder's cad 3, and playback's `play_otherslot`.
- **Pool name is `instpool`** (not "instrumentpool"), declared in `instrument.nvgt`; there is NO separate recorder pool — recorder playback shares `instpool`.
- **Entity menu does NOT apply.** The plan said to add it to the on-map entity list menu and gate with `is_obscured("instrument","menu")`, but that menu (`menu.nvgt`) only lists PHYSICAL objects (aircraft, door, npc, platform, wall…); no interaction entity (clock, calendar, sign, item) is in it. So the instrument is spier-only, mirroring clock — nothing was added to `menu_entities`/the entity menu.
- **`instrument_semantic_error` is modeled on `fall_zone`** (coord-only, `coord_token_error`/`range_token_error`), not door/passage — the line has no named-folder field to validate (instruments are chosen live), so the Tier 2 check is lighter than the plan anticipated.
- **Tier 1 lives in a parallel table.** `entity_line_error()` (the map-error recognized-object/count table) is separate from `dispatch_entity_line` and had to be updated too — missing it caused a real "not a recognized object" report on a valid line mid-port.
