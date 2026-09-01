---
name: project_sound_gallery_plan
description: Design/plan for the builder-menu "sound gallery" — a browse-only preview of every builder element's sounds (folder tree + per-type clip keys), built category by category. NOT STARTED.
metadata:
  type: project
---

**Status: BUILDING — engine + AUDIO implemented (2026-08-31), remaining 7 categories wired one at a time.** All 8 clip tables below are designed; the engine lives in `src/includes/builder/misc/gallery.nvgt` and is wired into the build menu (`map_menu.nvgt`: "sound gallery" item on every tab before "template"; `buildobj` dispatch). To add a category, extend `gallery_types_for()` in gallery.nvgt with its types/clips from the table below — nothing else. AUDIO, CONSTRUCTION, INTERACTION, KOMBAT, TRANSITIONS and TRANSPORTATION are live; traps/zones are DESIGNED-not-yet-wired. The engine now expands authored types into `gallery_tab`s: single-level types → one tab; two-step types (items done, npc next) → one tab per sub-category; `subpath` (npc `general/`, bike `misc/`) is applied after the variant. So the remaining special cases are already handled by the engine — new categories are still just data in `gallery_types_for()`. Related: [[project_audio_model]], [[project_sound_assets_layout]], [[feedback_menus_say_canceled]].

## Purpose

Let a map author **preview builder element sounds without opening each element's build form**. Browse-only — no placing, no selecting. Opened from the builder menu (so it runs in-map, meaning `mapname` is set and map-local asset overrides apply). Replaces the pain of opening ~53 separate forms just to hear what a tile/theme sounds like.

## Why it's cheap and self-maintaining

Every folder list is read straight from disk with the same `get_map_sound_folders("builder/...")` the forms use, so new categories / types / variants (and a map's own custom sounds) appear automatically. The **only** authored data is a small per-type clip table (main clip + any Ctrl-key extras), filled in category by category. A type with no table entry still browses — Space just plays whatever clip is in the folder.

## Navigation — three levels

1. **Category menu** — the 8 folders under `sounds/decompiled/builder/`: audio, construction, interaction, kombat, transitions, transportation, traps, zones. From `get_map_sound_folders("builder/*")`. Escape closes the gallery; include a "back" item that says "canceled".
2. **Type menu** — the chosen category's subfolders. From `get_map_sound_folders("builder/<cat>/*")`, BUT filtered to only the types whose clip table has been spec'd (see below) — an undeclared type is **hidden** until its keys are defined (dev decision 2026-08-31). Escape/back → level 1.
3. **Preview browser** — the variant folders of the chosen type. From `get_map_sound_folders("builder/<cat>/<type>/*")`. This is where audio plays:
   - **Up/Down arrow** = move; **speak the folder name**; stop any playing preview first.
   - **Space** = play the type's MAIN clip for the highlighted folder.
   - **Ctrl+<letter>** = play each extra clip, announced by its label.
   - Escape/back → level 2.

Level 3 needs live key handling during navigation, so it is a single-list form driven by a `form.monitor()` loop (like the build forms' preview section), not a plain blocking menu.

## Preview mechanic

- A dedicated preview `sound_pool` (mirrors the forms' `t`); `play_stationary` (non-positional); **destroy the previous slot before each play** so clips never stack.
- Clip resolved via `get_map_sound("builder/<cat>/<type>/<folder>/*<clip>*")` — map-context, so the current map's `assets/` overrides layer over the global library.
- Missing clip for a folder → **announce "no <label> sound"** rather than silence (mirrors the GC platform browser courtesy).
- **No volume / pitch controls.** The build forms have volume/pitch sliders that shape the preview; the gallery deliberately omits them (dev decision 2026-08-31) — it plays each clip at its natural level. So the level-3 view is JUST the list plus the play keys, no sliders.

## Key convention (uniform — matches every existing form)

- **Space** (no modifier) = the main clip.
- **Ctrl+<letter>** = each extra clip, gated on the list being focused. Letters reuse the element's existing form keys so muscle memory carries over. Confirmed 2026-08-31: every form already uses Ctrl+letter (the `control_is_down()` sits once at the top of the key block, wrapping all letters — door/elevator/passage included), so there is NOTHING to normalize.
- **Loop-promotion rule**: a few forms (doors, elevators) have NO bare-Space clip — they put the ambient `loop` on Ctrl+L along with everything else. The gallery promotes that `loop` to **Space** (its main clip) and drops the redundant Ctrl+L, so Space always plays something and `loop` stays the main/ambient clip as it is for every other type.

## Per-type clip declarations (built category by category)

**1. AUDIO — DONE.** Both types are a single `loop.ogg`.
- `musics`: main `*loop*`. No extras.
- `sources`: main `*loop*`. No extras.

**2. CONSTRUCTION — DONE (all 6 types).**
- `platforms`: main `*step*` (footstep); Ctrl+L `*land*` ("land"); Ctrl+H `*fall*` ("hard land").
- `walls`: main `*bump*` (the wall's own sound); Ctrl+L `*hurt*` ("hit"); Ctrl+H `*death*` ("death").
- `belts`: main `*loop*`. No extras. (The conveyor form also has a floor-tile list, but that's the `platforms` type — the gallery's `belts` type is just the belt's own loop.)
- `checkpoints`: main `*get*` (the reach/pickup sound); Ctrl+L `*loop*` ("loop"). Leaf holds `get.ogg` + `loop.ogg`.
- `moving platforms`: main `*loop*`. No extras. (Form's tile list is the `platforms` type; this type is the mover's own loop.)
- `vanishing platforms`: main `*loop*`. No extras. (Same split — tile list is `platforms`; this type is the vanisher's own loop.)

**3. INTERACTION — DONE (all 6 types).**
- `calendars`: main `*press*`; Ctrl+L `*loop*` ("loop").
- `clocks`: main `*press*`; Ctrl+L `*loop*` ("loop").
- `signs`: main `*press*`; Ctrl+L `*loop*` ("loop"); Ctrl+H `*break*` ("break"). (Leaf also has `step.ogg`, not previewed by the form.)
- `switches`: main `*press*`; Ctrl+L `*loop*` ("loop").
- `items`: DONE (structure approved) — the special **two-step** type. Unlike every other type, items nest a level deeper on disk: `items/<category>/<variant>/` where category is health / other / stamina. So the gallery's `items` type gets an EXTRA menu level (pick health/other/stamina, then the variant list). Clips for now (mirroring the form): main `*get*`; Ctrl+L `*loop*` ("loop"). SEE DEFERRED below — its extra clips are to be exposed.
- `sensors`: main `*loop*`; Ctrl+N `*on*` ("on"); Ctrl+O `*off*` ("off"). The sensor entity DOES support a loop — `read_sensor` spawns via the switch class (`spawn_switcher`, contact_trigger=true), which plays `builder/interaction/sensors/<type>/*loop*` when looping is on — so `loop` is the correct main clip (dev decision 2026-08-31, Option A). The stock `sensor` folder ships only `on.ogg`+`off.ogg`, so Space announces "no loop sound" there; a custom sensor with a `loop.ogg` plays it. No special-casing.
**4. KOMBAT — DONE (both types).**
- `npc`: two-step **and** one extra folder level. Path is `npc/<category>/<subtype>/general/*<clip>*` — pick a category, then a subtype, then preview. 7 categories: animals, bosses, helpers, humans, robots, specials, zombies. Each subtype folder also has a `data/` folder (info.sif) — skip it, clips are under `general/`. Baseline (mirroring the form): main `*hurt*`; Ctrl+L `*taunt*` ("taunt"); Ctrl+H `*death*` ("death"). The `general/` folder holds far more (`step`, `hit`, `spawn`, `launch`, `life`, `heal`, `tel`) — SEE DEFERRED.
- `projectiles`: single-level (`kombat/projectiles/<variant>/`). main `*hit*`; Ctrl+L `*loop*` ("loop"); Ctrl+H `*death*` ("death"). Leaf also has `hurt` + `life` — SEE DEFERRED.
**5. TRANSITIONS — DONE (all 5).** First category to use the arbitrary Ctrl-key list.
- `doors`: main `*loop*`; Ctrl+M `*move*` ("move"); Ctrl+C `*close*` ("close"); Ctrl+O `*open*` ("open"); Ctrl+D `*death*` ("death"); Ctrl+H `*hurt*` ("hurt"); Ctrl+N `*deny*` ("deny"); Ctrl+R `*grant*` ("grant"). NOTE: the door FORM has no bare-Space clip — it puts loop on Ctrl+L — but the gallery promotes the ambient `loop` to Space per the Space=main rule (loop is the Space/main clip everywhere else). All 8 clips are genuinely used: `hurt` is played from `bullet.nvgt:420` when a weapon damages a destroyable door (the door class itself never plays it, which is why it isn't in door.nvgt). The leaf's `jam` and `step` files are referenced NOWHERE in the code (door/passage/bullet all checked 2026-08-31) — both excluded as truly unused, NOT deferred.
- `elevators`: main `*loop*` (same Space=loop promotion); Ctrl+M `*move*` ("move"); Ctrl+C `*close*` ("close"); Ctrl+O `*open*` ("open"); Ctrl+B `*beep*` ("beep"). No extras.
- `lifts`: main `*loop*`. No extras. (The lift form's tile list is the `platforms` type; the gallery's `lifts` type is the lift's own loop — the `lifts/<x>/` leaf holds only `loop`.)
- `teleporters`: main `*move*`; Ctrl+L `*loop*` ("loop").
- `trampolines`: main `*land*`; Ctrl+L `*rise*` ("rise"); Ctrl+H `*spawn*` ("spawn").
**6. TRANSPORTATION — DONE (all 3).**
- `aircrafts`: single-level (`aircrafts/<variant>/`). main `*flight*`; Ctrl+L `*loop*` ("loop"); Ctrl+H `*death*` ("death"). Large extra set (alarm, appear, beacon, change, crash, engin, enter, gear, hurt, land, pass, start, turn) — SEE DEFERRED.
- `bikes`: clips nest under a `misc/` subfolder — path `bikes/<variant>/misc/*<clip>*`. main `*hurt*`; Ctrl+L `*beacon*` ("beacon"); Ctrl+H `*death*` ("death"). Big extra set in `misc/` (bell, change, crash, plummet, radar, speed, start, stop, stuck, turn) — SEE DEFERRED. NOTE: each bike ALSO has a `platforms/` subtree of bike-specific ride surfaces (ash, dirt, grass… each with fall/land/move) — deliberately NOT in the gallery (the bike form never previewed them). A bike-surfaces gallery type was built and then removed 2026-08-31; the misc set is a single leaf per variant (best as the consolidated bikes tab), while surfaces are per-variant lists, so grouping them didn't fit cleanly.
- `vehicles`: single-level (`vehicles/<variant>/`). main `*motor*`; Ctrl+L `*beacon*` ("beacon"); Ctrl+H `*death*` ("death"). Extras (hit, horn, hurt, turn) — SEE DEFERRED; note `hurt` IS used (played from `bullet.nvgt:525` on vehicle damage) even though the form doesn't preview it.
**7. TRAPS — DONE (all 10).** All single-level (`traps/<type>/<variant>/`).
- `bombs`: main `*land*`; Ctrl+L `*fall*` ("fall").
- `fires`: main `*hit*`; Ctrl+L `*loop*` ("loop").
- `floor breakers`: main `*spawn*`. Extra `remove` — deferred.
- `force fields`: main `*hit*`; Ctrl+N `*on*` ("on"); Ctrl+O `*off*` ("off").
- `hazards`: main `*fall*`; Ctrl+L `*loop*` ("loop").
- `mines`: main `*spawn*`; Ctrl+L `*loop*` ("loop"); Ctrl+H `*explode*` ("explode"). Extras `hit`, `light` — deferred.
- `security cameras`: main `*hurt*`; Ctrl+L `*turn*` ("turn"); Ctrl+H `*alert*` ("alert"). Extras `alarm`, `death` — deferred. (`hurt` confirmed used at runtime — bullet.nvgt:602/1062 — and it's the form's Space clip.)
- `spikes`: main `*hit*`; Ctrl+L `*loop*` ("loop"); Ctrl+H `*death*` ("death"). Extra `hurt` — deferred; `hurt` IS used at runtime (bullet.nvgt:497/1044) even though the form previews hit/loop/death, not hurt.
- `time bombs`: main `*land*`; Ctrl+L `*tick*` ("tick").
- `winds`: main `*hit*`; Ctrl+L `*loop*` ("loop").
**8. ZONES — DONE (all 3).** All single-level (`zones/<type>/<variant>/`); folder names contain spaces ("heal zones" etc.) — fine, the glob path is literal.
- `heal zones`: main `*heal*`; Ctrl+L `*take*` ("take"). Both leaf clips covered.
- `safe zones`: main `*out*`; Ctrl+L `*in*` ("in"). Both leaf clips covered. (Form order is out on Space, in on Ctrl+L.)
- `story zones`: main `*scroll*`; Ctrl+L `*open*` ("open"); Ctrl+H `*close*` ("close"). Leaf also has `copy` (clipboard-copy feedback), not previewed by the form — deferred.

## Confirmed decisions (2026-08-31)

- **Host menu**: the tabbed **build menu** (`buildmenu` in `map_menu.nvgt`). The "sound gallery" entry is added to **every tab**, positioned **immediately before the "template" item** (`m.add_item_to_tab(t_idx, "template", "template")` at map_menu.nvgt:589), so it's reachable no matter which category tab you're on — same pattern as `template`.
- **Undeclared types are hidden** — the type menu lists only types with a spec'd clip table.
- **No volume/pitch controls** in the preview.

## Deferred enhancements (agreed, do later)

- **Expose items' extra clips in BOTH the item build form AND the gallery** (dev decision 2026-08-31). The item leaf carries `drop`, `fire`, `hit`, and `break1..6` in addition to `get*` + `loop`, but the item build form only previews get + loop. Later: add preview keys for drop/fire/hit/break to `item.nvgt`'s form, and mirror the same expanded set in the gallery's `items` type. (Not blocking the initial gallery.)
- **Expose npc's extra clips in BOTH the npc build form AND the gallery** (dev decision 2026-08-31, same treatment as items). The `general/` folder carries `step`, `hit`, `spawn`, `launch`, `life`, `heal`, and `tel` beyond the form's `hurt`/`taunt`/`death`. Later: add preview keys for those to `npc.nvgt`'s form, and mirror the expanded set in the gallery's `npc` type. (Not blocking the initial gallery.)
- **Expose projectiles' extra clips** (`hurt`, `life`) in both the projectile form and the gallery, same policy as items/npc. The form previews only `hit`/`loop`/`death`.
- **Expose transportation extra clips** in both forms and gallery, same policy. `aircrafts` and `bikes` carry large extra sets (bikes under `misc/`); `vehicles` extras include `hit`, `horn`, `hurt`, `turn` — and `hurt` is already used at runtime (`bullet.nvgt:525`) though the form doesn't preview it. (The per-bike `platforms/` ride-surface subtree is deliberately NOT in the gallery — the bike build form never previewed it, so the gallery, which mirrors the forms, omits it too. Dev decision 2026-08-31.)
- **Expose traps' extra clips** in both forms and gallery, same policy: floor breakers `remove`; mines `hit`, `light`; security cameras `alarm`, `death`; spikes `hurt`. Spike `hurt` is already used at runtime (`bullet.nvgt:497/1044`), just not form-previewed. (story zones `copy` — clipboard feedback — also sits here, minor.)

## Implementation notes (mechanics confirmed 2026-08-31)

- **Preview pool**: reuse the global `sound_pool t` (declared `dec.nvgt:30` — `sound_pool t, temp, spool;`). Every builder form previews through it: `t.play_stationary[_extended](...)`, tracking an `int prevslot`, calling `t.destroy_sound(prevslot)` before each new play to stop the prior clip. Gallery is modal so there's no contention; reuse `t` and the same stop-previous pattern.
- **Menu + preview keys**: build the gallery on `form_menu` (`main/deps/form_menu.nvgt`). Its **`background_callback`** (funcdef `menu_callback(form_menu@, string)`, set via `m.background_callback = @func`) runs every `monitor()` tick — that's where the preview logic goes: read `m.focused_item` (+ `m.active_tab` in tabbed mode) for the highlighted variant/type, stop the previous clip on selection change, and play the mapped clip through `t` on Space / Ctrl+L / Ctrl+H. The menu already auto-speaks the focused item (`speak_position_information`), so "arrows speak the folder name" is free.
- **Tabbed mode** (`add_tab` / `add_item_to_tab`) gives the per-type tabs (audio → musics/sources, etc.).
- **Template to copy**: `learn_game_sounds_menu` (form_menu.nvgt:520) is a near-exact working prototype — cursor-move stops the previous audio, a key previews. Follows the `old_pos = m.focused_item; m.monitor(); if changed → stop` pattern; `background_callback` is the cleaner equivalent.
- **Funcdef caveat**: the callback is a free function, NOT a closure — it can't capture locals. Keep "current category + active type→clip map" in module-level state the callback reads.

## Reference

Pull the exact clip globs per category from each element's build-form preview block (the `t.play_stationary(get_map_sound(...))` lines, gated by `control_is_down()` + list focus).

## Full category → type inventory (level 1 → level 2, from disk)

- **audio**: musics, sources
- **construction**: belts, checkpoints, moving platforms, platforms, vanishing platforms, walls
- **interaction**: calendars, clocks, items, sensors, signs, switches
- **kombat**: npc, projectiles
- **transitions**: doors, elevators, lifts, teleporters, trampolines
- **transportation**: aircrafts, bikes, vehicles
- **traps**: bombs, fires, floor breakers, force fields, hazards, mines, security cameras, spikes, time bombs, winds
- **zones**: heal zones, safe zones, story zones
