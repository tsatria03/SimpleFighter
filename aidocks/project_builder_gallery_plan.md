---
name: project_builder_gallery_plan
description: Design/build record for the builder gallery — the build-menu "gallery" that browse-previews every builder element's sounds (folder tree + per-type clip keys). All 8 categories live + bike-surface secondary axis; deferred = exposing untapped extra clips.
metadata:
  type: project
---

**Status: COMPLETE — all 8 categories wired and live (2026-08-31).** The engine lives in `src/includes/builder/misc/gallery.nvgt` and is wired into the build menu (`map_menu.nvgt`: "gallery" item on every tab before "template"; `buildobj` dispatch). Every category (audio, construction, interaction, kombat, transitions, transportation, traps, zones) is populated in `gallery_types_for()`. To adjust a category, edit its block there — nothing else. Remaining work is only the DEFERRED extra-clip exposure below (not blocking). The engine now expands authored types into `gallery_tab`s: single-level types → one tab; two-step types (items done, npc next) → one tab per sub-category; `subpath` (npc `general/`, bike `misc/`) is applied after the variant. So the remaining special cases are already handled by the engine — new categories are still just data in `gallery_types_for()`. Related: [[project_audio_model]], [[project_sound_assets_layout]], [[feedback_menus_say_canceled]].

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
- `aircrafts`: single-level (`aircrafts/<variant>/`). DONE — all 16 clips exposed 2026-09-01 in aircraft form + gallery + aircrafts.txt (new audition section added). Full map: Space hurt, Ctrl+L loop, Ctrl+H death, Ctrl+B beacon, Ctrl+C change, Ctrl+R crash, Ctrl+U turn, Ctrl+M alarm, Ctrl+N land, Ctrl+E engin, Ctrl+S start, Ctrl+O appear, Ctrl+T enter, Ctrl+I flight, Ctrl+K gear, Ctrl+P pass. (Space was flight, now hurt; flight moved to Ctrl+I.) All 16 verified used: aircraft.nvgt + air_turbulence.nvgt (alarm/appear/pass) + airbeacon.nvgt (beacon) + hurt via bullet/weapon/glider.
- `bikes`: clips nest under a `misc/` subfolder — path `bikes/<variant>/misc/*<clip>*`. main `*hurt*`; Ctrl+L `*beacon*` ("beacon"); Ctrl+H `*death*` ("death"). Big extra set in `misc/` (bell, change, crash, plummet, radar, speed, start, stop, stuck, turn) — SEE DEFERRED. NOTE: each bike ALSO has a `platforms/` subtree of bike-specific ride surfaces (ash, dirt, grass… each with fall/land/move). These are now in the gallery as a **secondary "surface" axis on the same bikes tab** (added 2026-09-01) — no separate tab. On a focused bike: **Ctrl+'** next surface / **Ctrl+;** previous surface (announces the surface name), then **Ctrl+Space** move, **Ctrl+K** land, **Ctrl+J** fall for the selected surface. Engine support: `gallery_type.surface_folder` + `surface_clips` (the ONLY bike-specific logic in the callback); a plain-Space clip requires control UP so Ctrl+Space never also fires the bike's own hurt. Pressing any arrow (navigating bikes, with or without control) snaps the surface back to the first one — detected with key_down, never key_repeating, so it doesn't steal the arrows from the menu. (An earlier attempt to make surfaces their own tabs was removed first — surfaces are per-variant lists while misc is a single leaf, so tabs didn't group cleanly; the secondary-axis approach solves that.) The **bike build form** (`bike.nvgt`) mirrors the exact same keys on its bike sound list (added 2026-09-01) — local surface state in its own monitor loop, its existing Space=hurt handler now gated `!control_is_down()` so Ctrl+Space=move doesn't double-fire.
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

- **Host menu**: the tabbed **build menu** (`buildmenu` in `map_menu.nvgt`). The "gallery" entry is added to **every tab**, positioned **immediately before the "template" item** (`m.add_item_to_tab(t_idx, "template", "template")` at map_menu.nvgt:589), so it's reachable no matter which category tab you're on — same pattern as `template`.
- **Undeclared types are hidden** — the type menu lists only types with a spec'd clip table.
- **No volume/pitch controls** in the preview.
- **Quiet gallery** (dev decision 2026-09-01): the browser speaks only the category name on open — NO spoken key tutorial ("arrow keys to move, space to play…" was removed). Matches the build forms, which never announce their preview keys either. The keys are documented in the readme/help instead. (Cycle/selection feedback like speaking the focused surface name stays — that's item feedback, not instruction.)

## Deferred enhancements (agreed, do later)

The complete, per-element list of untapped clips is in the **Full shipped-sound inventory** section just below — that is the authoritative to-do source for expanding the gallery (and matching build forms). The bullets here are the original notes. **Caveat before exposing any untapped clip: verify it is actually used** (runtime playback and/or the build form) — some shipped files are dead (e.g. door `jam`/`step` are referenced nowhere), while others are used but just not form-previewed (spike `hurt`, vehicle `hurt` via `bullet.nvgt`). Confirm per clip the way we did for door `hurt`.

**Workflow for the extra-clip exposure pass (dev-stated 2026-09-01):** do it **one category at a time**, and the **dev chooses which key plays which extra clip** — do NOT auto-assign. For each category: propose the untapped clips (from the inventory) and let the dev pick the keys, then wire the SAME keys into THREE places: (1) the element's build form (its `form.monitor()` preview block), (2) the gallery's clip table (`gallery_types_for()` in `gallery.nvgt`), and (3) the element's help topic — update its "Auditioning sounds in the builder." section (like `bikes.txt` has) with the new keys. Reuse the Ctrl+letter convention; free letters and Ctrl+Space/apostrophe/semicolon are available (mind first-letter nav on plain letters and the key_repeating/key_pressed consumption rules — see [[project_nvgt_key_pressed_oneshot]]). The gallery is otherwise COMPLETE; this pass is optional polish.

- **Expose items' extra clips in BOTH the item build form AND the gallery** (dev decision 2026-08-31). The item leaf carries `drop`, `fire`, `hit`, and `break1..6` in addition to `get*` + `loop`, but the item build form only previews get + loop. Later: add preview keys for drop/fire/hit/break to `item.nvgt`'s form, and mirror the same expanded set in the gallery's `items` type. (Not blocking the initial gallery.)
- **Expose npc's extra clips in BOTH the npc build form AND the gallery** (dev decision 2026-08-31, same treatment as items). The `general/` folder carries `step`, `hit`, `spawn`, `launch`, `life`, `heal`, and `tel` beyond the form's `hurt`/`taunt`/`death`. Later: add preview keys for those to `npc.nvgt`'s form, and mirror the expanded set in the gallery's `npc` type. (Not blocking the initial gallery.)
- **Expose projectiles' extra clips** (`hurt`, `life`) in both the projectile form and the gallery, same policy as items/npc. The form previews only `hit`/`loop`/`death`.
- **Expose transportation extra clips** in both forms and gallery, same policy. `aircrafts` and `bikes` carry large extra sets (bikes under `misc/`); `vehicles` extras include `hit`, `horn`, `hurt`, `turn` — and `hurt` is already used at runtime (`bullet.nvgt:525`) though the form doesn't preview it. (The per-bike `platforms/` ride-surface subtree is deliberately NOT in the gallery — the bike build form never previewed it, so the gallery, which mirrors the forms, omits it too. Dev decision 2026-08-31.)
- **Expose traps' extra clips** in both forms and gallery, same policy: floor breakers `remove`; mines `hit`, `light`; security cameras `alarm`, `death`; spikes `hurt`. Spike `hurt` is already used at runtime (`bullet.nvgt:497/1044`), just not form-previewed. (story zones `copy` — clipboard feedback — also sits here, minor.)

## Full shipped-sound inventory per element (cataloged 2026-08-31)

Every distinct sound the shipped content includes for each element, with **numbered variants collapsed** (step1/step2 → step; a user may add their own variants). Format: `element: <all shipped sounds> [gallery plays: <current>] → untapped: <not yet in gallery>`. "untapped" = shipped but the gallery doesn't preview it yet (a deferred-exposure candidate, subject to the used-clip caveat above). Cataloged by unioning one clip of each type across all variants of each element under `sf/sounds/decompiled/builder/`.

**audio**
- musics: loop [loop] → none
- sources: loop [loop] → none

**construction**
- belts: loop [loop] → none
- checkpoints: get, loop [get, loop] → none
- moving platforms: loop [loop] → none
- platforms: death, fall, hurt, land, step [step, land, fall, death, hurt] → none (exposed 2026-09-01: Ctrl+D death, Ctrl+U hurt, in platform form + gallery + help; both played on platform damage/destroy. NOTE: only the platform form was extended, not the moving-platform form's tile list.)
- vanishing platforms: loop [loop] → none
- walls: bump, death, hurt [bump, hurt, death] → none

**interaction**
- calendars: break, loop, press [press, loop, break] → none (break exposed 2026-09-01: Ctrl+H in form + gallery + help; used at projectile/bomb/mine/timebomb/bullet destroy)
- clocks: break, loop, press [press, loop, break] → none (break exposed 2026-09-01: Ctrl+H, same as calendars)
- items: break, drop, fire, get, healstart, healstop, hit, loop, place, scanning, scanstart, scanstop [get, loop] → **break, drop, fire, healstart, healstop, hit, place, scanning, scanstart, scanstop** (several are category-specific — e.g. healstart/healstop on health items, scan* on others)
- sensors: off, on [gallery main is loop + on/off] → none untapped; NOTE stock ships NO loop (only on/off), so Space says "No loop sound specified" until a custom sensor adds loop (the entity supports it)
- signs: break, loop, press, step [press, loop, break, step] → none (step exposed 2026-09-01: Ctrl+S in form + gallery + help; used as footstep in map.nvgt:633)
- switches: loop, press [press, loop] → none

**kombat**
- npc: death, heal, hit, hurt, launch, life, remove, spawn, step, taunt, tel [hurt, taunt, death] → **heal, hit, launch, life, remove, spawn, step, tel** (`remove` ships only for the helpers category; hit/step absent from a few categories like humans/zombies)
- projectiles: death, hit, hurt, life, loop [hit, loop, death, hurt, life] → none (exposed 2026-09-01: Ctrl+U hurt, Ctrl+I life, in projectile form + gallery + help)

**transitions**
- doors: close, death, deny, grant, hurt, jam, loop, move, open, step [loop, move, close, open, death, hurt, deny, grant] → jam, step — BUT both are referenced NOWHERE in code (dead files) — do NOT expose
- elevators: beep, close, loop, move, open [loop, move, close, open, beep] → none
- lifts: loop [loop] → none
- teleporters: loop, move [move, loop] → none
- trampolines: land, rise, spawn [land, rise, spawn] → none

**transportation**
- aircrafts: alarm, appear, beacon, change, crash, death, engin, enter, flight, gear, hurt, land, loop, pass, start, turn [ALL 16] → none (fully exposed 2026-09-01; Space=hurt now, flight on Ctrl+I)
- bikes (own/misc): beacon, bell, change, crash, death, hurt, plummet, radar, speed, start, stop, stuck, turn [hurt, beacon, death, bell, change, speed, radar, turn, crash, start, stop, stuck] → plummet still untapped. 9 misc extras exposed 2026-09-01: Ctrl+B bell, Ctrl+C change, Ctrl+S speed, Ctrl+D radar, Ctrl+U turn, Ctrl+R crash, Ctrl+T start, Ctrl+P stop, Ctrl+X stuck (bike form + gallery + bikes.txt); all 9 played in bike.nvgt. **plummet: mechanic WIRED 2026-09-01, changelogged (14.5); gallery/form audition NOT yet exposed (needs a key).** It was shipped-but-unwired: the character long-fall cue (fall+plummet, drops >=8 tiles) is suppressed when onbike (map.nvgt:970/990 `&& !onbike`), and the bike's own misc/plummet was meant to play there but never did. Fix: added an `else if(predicted >= 8 && onbike)` branch in BOTH the 2d and 3d fall blocks that finds the moveable bike and plays its misc/*plummet* through pool `p` into `fallslot` (so the existing land-time `p.destroy_sound(fallslot)` at ~1019 stops it). Audition exposed 2026-09-01 on Ctrl+M in the bike form + gallery + bikes.txt. Bikes are now FULLY covered (all 13 misc clips + the ride-surface axis). Verified form key-safety against form.nvgt: while a list is focused the form only consumes Ctrl+F (find), Ctrl+G (go-to, if enabled), Ctrl+A (multiselect); Ctrl+C/X/V are input-field-only — so all 9 bike Ctrl-letters are collision-free.
- bikes (ride surfaces, `platforms/<surface>/`): fall, land, move — IN the gallery via the bikes tab's secondary surface axis (Ctrl+'/Ctrl+; to cycle, Ctrl+Space/K/J for move/land/fall); see the transportation note above
- vehicles: beacon, death, hit, horn, hurt, motor, turn [motor, beacon, death] → **hit, horn, hurt, turn**

**traps**
- bombs: fall, land [land, fall] → none
- fires: hit, loop [hit, loop] → none
- floor breakers: remove, spawn [remove, spawn] → none (swapped 2026-09-01: Space=remove, Ctrl+L=spawn, in form + gallery + help; remove played at floor_breaker.nvgt:34)
- force fields: hit, off, on [hit, on, off] → none
- hazards: fall, loop [fall, loop] → none
- mines: explode, hit, light, loop, spawn [spawn, explode, loop, hit, light] → none (remapped 2026-09-01: Space spawn, Ctrl+E explode, Ctrl+L loop, Ctrl+H hit, Ctrl+I light, in mine form + gallery + help; explode moved off Ctrl+H to Ctrl+E)
- security cameras: alarm, alert, death, hurt, turn [hurt, death, alert, alarm, turn] → none (remapped 2026-09-01: Space hurt, Ctrl+H death, Ctrl+L alert, Ctrl+M alarm, Ctrl+U turn, in camera form + gallery + help; all five shipped clips exposed. Cameras don't attack — no hit clip. turn/alert/alarm/death played in security_camera.nvgt; hurt at bullet.nvgt:602/1062)
- spikes: death, hit, hurt, loop [hit, loop, death, hurt] → none (hurt exposed 2026-09-01: Ctrl+U in form + gallery + help; used at bullet.nvgt:497/1044)
- time bombs: drop, hit, land, tick [tick, land, drop] → hit still untapped (remapped 2026-09-01: Space tick, Ctrl+L land, Ctrl+D drop, in timebomb form + gallery + bombs.txt help; dev did not map hit, and the stock timebomb variant ships no hit file anyway — hit is used at runtime though, timebomb.nvgt:60)
- winds: hit, loop [hit, loop] → none

**zones**
- heal zones: heal, take [heal, take] → none
- safe zones: in, out [out, in] → none
- story zones: close, copy, open, scroll [scroll, open, close, copy] → none (copy exposed 2026-09-01: Ctrl+C in form + gallery + help; clipboard-copy feedback at dlg.nvgt:14)

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
