# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

SimpleFighter is an audio-only action / map-builder game written in **NVGT** (Non-Visual Game Toolkit, an AngelScript-based engine). All gameplay code is .nvgt. There is no visual rendering — output is screen-reader speech plus HRTF spatial audio through NVGT's sound_pool.

## Running

There is no test suite or linter. Run or compile sf.nvgt with the NVGT runtime for development.

sf.nvgt is the entry. main() installs the keyhook, gates on SCREEN_READER_AVAILABLE / SOUND_AVAILABLE, blocks a second instance via gamstence.is_already_running, initializes sound pools, parses character / shield / weapon data, optionally checks for updates against the compiled-in `version` constant, downloads the sounds/ folder if missing, then loops mainmenu().

## Stability rules — read first, break never

These are the load-bearing invariants of the codebase. Violate one and either old maps stop loading, parsers silently fail, or the runtime drifts. Read these before any edit.

- **read_* / write_* signatures need care.** Every entity in includes/builder/**/*.nvgt exposes a read_<entity>(string[] sd) parsing one info.sif line and a write_<entity>(...) producing one; map_parser.nvgt's sd.length() checks gate which read_* runs. Backward compatibility for older maps is **case-by-case** — some entities accept multiple historical sd.length() shapes, others only the current one and an older line is silently dropped. Before changing a signature, check that entity's existing length handling; adding or preserving back-compat is a per-entity judgment call. Refactoring inside build_* (the UI) is generally safe.
- **mapmode is creation-locked.** A map's mode 2d|topdown|3d line is set when the map is created and read by load_map(). Do not mutate mapmode mid-map. Map-editing commands (editline, addline, remline in the command parser) explicitly reject mode changes. The parser's sd.length() checks are **multi-valued** (e.g. ==10 || ==11 || ==12 for platforms; ==18 || ==20 for doors; or `>=N` for entities with optional trailing tokens like blockage, elevator, passage, several zones). Extra lengths encode 3d (z fields **inserted inside the coordinate block**, not appended) and the topdown/3d min/max-y variant. Preserve every length case when adding or modifying entities.
- **CRLF line endings are enforced.** *.sif, *.nvgt, *.py, *.txt, *.bat, *.ps1, *.md, and *.ini are pinned to text eol=crlf in .gitattributes. The NVGT compiler, in-game .sif readers, and build scripts all expect Windows line endings. Tools that auto-strip CRLF will break the working tree silently. Generate new files with CRLF, or call the split_lines() helper in extrafuncts.nvgt on the read side.
- **Coordinates are double.** Some legacy fields are still int; convert when you touch them. Don't introduce new int coords.
- **Capability flags gate input handlers as a set.** moveable, fireable, cammable, healable, jumpable, quittable, speedable, spiable, turnable (and others in dec.nvgt) gate which keys do what. pause_game() and resume_game() flip them as a coordinated set — don't toggle them individually unless you know exactly which subsystem you're freezing.
- **3d wall/platform tiles spawn per-z.** Volumetric entities in 3d mode loop for(double z = minz; z <= maxz; z++) and push each per-z spawn_platform id into a platform_ids array on the parent entity. See wall.nvgt for the canonical pattern. Don't try to represent height with a single platform record.
- **Builder UI uses the audio form for multi-input flows.** form.create_window, form.create_input_box, form.create_button, form.monitor, form.is_pressed. See sf.nvgt's dockread / helpread for the canonical shape. Single one-shot prompts may use vd.input_box. Don't roll your own input loop.
- **Entity arrays use sentinel-null removal, not `remove_at`.** Every `<entity>@[] <entity>s(0);` array in the game (platforms, walls, staircases, hazards, npcs, bullets, bombs, mines, timebombs, doors, fires, checkpoints, switchers, teleporters, spikes, sucams, ttsenemies, bodyfalls, vehicles, bikes, aircrafts, objs, calendars, clocks, signs — and any new entity) treats mid-game removal as `@<entity>s[i] = null;`, NOT `<entity>s.remove_at(i);`. This keeps stored cross-entity indices stable (e.g. `walls[i].platform_ids[k]` doesn't drift when a peer entity is destroyed) and fixes the skip-after-remove class of bug inside `for(i; i < length; i++)` loops. Every iteration site must guard with `if(@<entity>s[i] == null) continue;` at the top of the loop body (or inline `if(@<entity>s[i] != null) ...` for braceless one-liners like `effect_space.nvgt`'s `apply_effect_pools()`). Every stored-id deref needs `&& @<entity>s[id] != null` in the bounds check. `destroy_all_<entity>s()` keeps `<entity>s.resize(0)` — that's the only place compaction is allowed, and it happens between maps. Compacting loops (`for(uint i=0; i<<entity>s.length();)` with conditional `i++`) break under sentinel-null and must be rewritten as standard `for(...; i++)` loops. When adding a new entity, follow this from the start.
- **Camera-mode key collisions need `key_up(KEY_G) and !camdext` gates.** The camera handler in `game_handlers.nvgt`'s `handle_camera_keys()` is gated by `key_down(KEY_G) || camdext` — so when G is held (or camdext is on), every key the user presses fires its `camera_*` action. The trap: many camera keys (R, T, Y, M, J, K, L, I) are *also* bound to non-camera actions (reload, weapon_reflection_toggle, info_stamina, info_mfc, sonar_*, aircraft_land, etc.), and a non-gated non-camera handler will fire on the same press, producing double-actions like "camera readout" plus "this weapon does not take any ammo". Any handler whose action shares a physical key with a `camera_*` action in `data/main/config/keyboard.ini` must back off when camera mode is active by adding `and key_up(KEY_G) and !camdext` to its condition (see the `reload` handler at `game_handlers.nvgt:1373` for the canonical pattern). When binding a new action to an existing key, cross-check `keyboard.ini`'s `[camera]` block first.
- **info.sif key=value pairs use spaces, not underscores, in field names.** The on-disk convention is `key with spaces=value` (e.g. `weapon type=melee`, `fire speed=300`, `hit and run=true`, `flee time=2000`), reserving underscores only for *identifier values* that legitimately need them (folder names like `long_rope`, tile names like `wallstone_dark`, item names like `health_kit`). Parser keys, builder form key arrays, doc references, and authored .sif files all need to stay aligned on this — if you add a new key, write it spaced; if you find an old underscored key like `hit_and_run` or `flee_time` anywhere, it's a leftover that should be migrated (sweep the parser, the builder's keys / cb_keys arrays, every info.sif file that uses it, and the matching .tp doc together). Note that internal AngelScript variable names keep their underscores (e.g. `self.hit_and_run`, `self.flee_time`) — only the *user-facing key strings* and authored file content follow the spaces rule.

## Script side vs engine side — investigate script first, modify engine last

The codebase spans two repos: SimpleFighter (this one, .nvgt scripts) and Legacy-NVGT (the engine, C++). Engine changes are slower to iterate, harder to revert, and require a `scons` rebuild before they're testable, so the default rule when chasing a bug or a perf issue is **diagnose in the script layer first**, and only reach for engine changes once you've ruled out the script layer with concrete evidence.

- **Symptom → script side first.** When a behavior is wrong or slow, start by tracing it through the `.nvgt` call sites that produce it. Most of what feels like an "engine issue" turns out to be a wrapper, a resolver, or a hot loop in script — and even when the engine *is* involved, the script side usually has a way to mitigate or sidestep it without touching C++.
- **Isolate with a minimal repro before touching either side.** When a bug only shows up in complex maps or large packs, build the smallest version that still triggers it and bisect. The "50 signs with `signtype=none` still lags" experiment that uncovered the O(N) pack scan was worth hours of engine speculation.
- **Stub or comment out instead of optimizing.** When a script function might be the bottleneck, comment out its call site and rerun. If the symptom disappears, you've found your layer without changing logic. Then optimize for real. Engine changes don't have this luxury — every C++ change is at least a rebuild round-trip.
- **Engine changes for what only the engine can do.** New API surface (e.g. `directory_rename`, `add_sound_default_pack`), fundamental capability gaps (multi-pack chain, in-memory `BASS_StreamCreateFile` for packed sounds), or fixes below the script binding boundary (per-byte decrypt loops, BASS callback overhead) are real engine work. Script-layer wrappers, lookup costs, per-frame entity loops, and audio-resolution helpers are not.
- **Don't conflate "the engine could be faster" with "the engine is the bottleneck."** Engine optimizations off the actual hot path produce no observable change for the player. `pack_buffer_decrypt` vectorization, single-hashmap-lookup in `read_file`, and `memload`-as-default were real wins that did **not** fix entity-heavy map sluggishness — because the hot path was a script-side O(N) string scan, not pack I/O.

When you do change the engine, note it in this file so the next person knows the engine isn't stock NVGT.

**Non-stock engine changes (Legacy-NVGT) in use by this game:**
- **Script-configurable pitch limits.** `sound.cpp`'s pitch clamp (formerly hardcoded `0.05`–`5.0`, i.e. 5%–500%) now reads two script-exposed globals `sound_pitch_lower_limit` / `sound_pitch_upper_limit` (multiplier units; defaults unchanged at `0.05`/`5.0`). All four clamps (`sound::set_pitch`/`slide_pitch`, `mixer::set_pitch`/`slide_pitch`) consult them. Set the global once at startup to widen the range without recompiling; the builder pitch sliders (`5`–`500`) must be raised to match if you want to author beyond the default. Requires a `scons` rebuild before the game's `sound_pitch_*` references will compile.

## Confirm before implementing — design discussion is not a green light

The dev's default mode of working in this repo is to describe an idea or ask a question first, then explicitly say "go ahead" or "yes please" before any code, doc, or changelog edit happens. Treat a design proposal — even a detailed and apparently-settled one — as a question to be answered with a plan, not a task to start executing. Stop at the "want me to proceed?" point and wait for confirmation.

- **A description of a feature is a question, not an instruction.** When the dev writes "I really wish X" or "what if we did Y" or "could we extend Z" — they are exploring, not commissioning. Lay out the design, call out tradeoffs, ask for go-ahead. Don't start editing.
- **Don't bundle implementation into the same turn as the proposal.** Even when a design feels obvious or small, splitting the proposal turn from the implementation turn gives the dev a chance to redirect, refine scope, or say "not now." Bundling them in one turn skips that decision.
- **Don't fan out into adjacent files unprompted.** Implementing a feature plus updating two help topics plus a changelog entry plus a memory file — all in one unconfirmed batch — is the over-reach pattern to avoid. Each is a separate side-effect that deserves its own go-ahead.
- **Exceptions where continuing without re-asking is fine:**
  - The dev has already approved the broader task and a follow-up is clearly within scope (e.g. "section 2 of the bike refactor" right after they approved section 1).
  - The dev explicitly reported a bug and asked for the fix in the same message — that's an implicit go-ahead to implement the fix (still confirm scope if uncertain).
  - The dev directly asked for a specific edit ("rename X to Y", "delete this block", "add a changelog entry for…") — those are imperative and can proceed.
- **When in doubt, ask.** "Want me to proceed?" is cheap; rollbacks aren't.

## Map mode (2d / topdown / 3d)

Every map carries a mode 2d|topdown|3d line at the top of info.sif. load_map() resets mapmode = "" and reads it from the file. The parser branches on mapmode == "3d" to accept extra z-coordinate fields, and the builder/runtime branches on the same flag for spatial behavior.

**Spanning entities require min/max y in topdown and 3d.** Any entity that already takes minimum/maximum x (i.e. it spans tiles along the x axis — platforms, vanishing platforms, walls, blockages, conveyor belts, hazards, force fields, spikes, doors, lifts, every zone, etc.) MUST also take minimum/maximum y when the map's mode is topdown or 3d, where y is a spatial axis (depth) rather than a single floor level. The builder UI must prompt for both, the spawn function must accept distinct y1/y2 values, write_<entity> must emit both, and read_<entity> must accept them. For 2d maps y stays a single value (it's the floor height, not a spatial range). For backward compatibility, read_<entity> must still accept the older single-y line shape from pre-existing topdown/3d maps (treat the missing maxy as equal to miny — same as today's behavior of a one-tile-deep strip), so map_parser.nvgt's sd.length() check for those entities becomes three-valued: the original 2d length, the original single-y topdown/3d length (still loads), and the new min/max-y topdown/3d length. New maps authored after this change write the two-y form.

## Map format

data/builder/maps/decompiled/<name>/data/main.sif, plain text, one entity per line, space-delimited. Header lines are mode and minx/maxx/miny/maxy/minz/maxz; the sibling data/meta.sif holds owner, description, created date, modified date (key=value form). Example main.sif:

mode 3d
minx 0
maxx 100
miny 0
maxy 100
minz 0
maxz 100
bike 50 50 0 1 1500 bike

Maps may also be compiled into encrypted .map packs at data/builder/maps/compiled/<name>.map; load_map() falls back to the pack when the decompiled folder is absent. The pack handle (map_pack) is opened by load_map_pack and assigned to sound_default_pack so audio reads transparently from inside the .map, while .sif reads go through map_pack.read_file("data/main.sif", ...) and map_pack.read_file("data/meta.sif", ...) directly.

**Quoted text fields.** A set of text-bearing entities wrap their free-text / identifier fields in double quotes on disk. The convention was established by switch / sensor (their on/off commands) and ttsenemie (its taunt / hurt / death / voice fields), which already used quoted fields and are the template the rest follow. It now also covers: blockage, text_zone (and its `zone` alias), text_square, el_floor, clock, calendar, sign, story_zone, timed_text, elevator (spoken/label text), and door / passage (two quoted fields each — item id **and** password, so both may contain spaces). The contract is the read_switch shape: write_<entity> strips any literal `"` from the field then wraps it; read_<entity> parses the fixed front (coords + structural fields) positionally, pulls the quoted block via extract_quoted(), then splits the trailing structural fields out of the remainder. These entities are **not back-compatible** — there is no dual-path read, so a pre-quote (unquoted) line silently drops and old maps must be re-saved/migrated. Because door/passage text can now hold spaces, their map_parser dispatch gates were changed from exact token counts to mode-aware >= floors (door >=18 / >=20 in 3d, passage >=16 / >=18). Door's single and ranged forms now share the one `door` keyword (there is no `ranged_door`), distinguished inside read_door by how many coordinates precede the first quoted field — see the single/ranged keyword unification note below.

**Single/ranged share one keyword (no `ranged_` anymore).** Every entity that offers both a single-tile and a ranged-area form — clocks, calendars, signs, text squares, switches, sensors, travelpoints, hazards, spikes, vanishing hazards, force fields, timed text, doors/item doors, and the sound/url/timed sources and ambiences — now reads and writes under one base keyword. There is no `ranged_<entity>` keyword in the builder menu, on disk, or in /spawn. `write_<entity>` emits the base name for single and `write_ranged_<entity>` emits the **same** base name for ranged; the parser tells them apart by line shape. Unquoted entities branch on `sd.length()` in `dispatch_entity_line` (short length → `read_<entity>`, longer → `read_ranged_<entity>`). Quoted entities can't use a raw length (quoted text varies), so `read_<entity>` counts the coordinate tokens before the first `"`-prefixed token and delegates to `read_ranged_<entity>` when there are too many (2 vs 4 in 2d, 3 vs 6 in 3d; door is higher and mode-aware — 12 vs 14 tokens in 2d, 14 vs 17 in 3d — because of its many pre-quote fields). The builder shows one menu entry per entity with a `build mode` single/ranged list (single default), built with the form-rebuild loop (see `build_door` / the new-map form). When adding a new spanning entity, follow this — never introduce a `ranged_` keyword or a second "ranged X" menu entry. (Reading old `ranged_<entity>` lines is **not** supported; the one stock occurrence, old_main's `ranged_travelpoint`, was migrated to `travelpoint`.)

## Include tree

sf.nvgt includes only includes/includes.nvgt, which pulls in three NVGT stdlib files (bgt_compat, instance, token_gen — these resolve from the NVGT install, not the repo, so don't flag them as missing) followed by glob-includes over every directory under includes/builder/ and includes/main/.

### includes/main/ — engine

- globals/dec.nvgt — central engine state: map bounds (minx/maxx/miny/maxy/minz/maxz), camera-selection markers (sel_left_set … sel_top_set), character stats (health, stamina, attack, defence, level, xp), capability flags (moveable, fireable, jumpable, runnable, etc.), timers, theme strings (chartype, keyboardtheme, menutype), and the active map identity (mapname, mapmode, mapowner). Sound-pool declarations and helpers live in the sibling decpool.nvgt.
- globals/decpool.nvgt — owns the sound_pool array. initialize_sound_pools() (called once at startup), update_sound_pools() (called every frame from game.nvgt), pause_pools() / resume_pools() for global freeze, and apply_map_pool() which flips sound_pool_default_y_elevation based on mapmode.
- globals/controls.nvgt — declares the global `key_config controls;` and load_controls() which reads data/main/config/keyboard.ini at startup (sf.nvgt aborts if it fails). Also exposes keyboard_actions_in_order() for the settings-menu listing.
- globals/game.nvgt — main game loop. Iterates wait(5) and dispatches per-frame *check() and *loop() calls for every entity family (doors, elevators, hazards, walls, npcs, bullets, bombs, fires, …) plus update_sound_pools(), checkdeath(), checkloc().
- globals/game_input.nvgt — thin per-frame dispatcher: calls the handle_*_keys() functions in game_handlers.nvgt in order, gated by freezgame and jumping/run-mode state.
- globals/map.nvgt — clearmap(), camera-marker selection, movement and physics helpers.
- globals/game_handlers.nvgt — the actual handle_*_keys() bodies (command, macro, inventory, draw, hook, speed, height, spier, facing, rotation, step, jump, camera, kombat, sonar, misc, …). All key checks go through the global `controls` (a key_config) using action names defined in data/main/config/keyboard.ini — no raw key_pressed(KEY_*) calls.
- globals/weapon.nvgt, weapon_manager.nvgt, bullet.nvgt, bodyfall.nvgt, hook.nvgt, sonar.nvgt, spier.nvgt, stunner.nvgt, tracker.nvgt, inventory.nvgt, fadepool.nvgt, updater.nvgt, character_manager.nvgt, shield_manager.nvgt, glider.nvgt — runtime subsystems.
- parsers/map_parser.nvgt — load_map() reads data/builder/maps/decompiled/<name>/data/main.sif (plain text) or the compiled .map pack, then dispatches each line to the appropriate read_<entity>(). The dispatcher itself lives in dispatch_entity_line(string[] sd) and is also called by the /spawn command path so a typed-args spawn behaves the same as a map load.
- parsers/command_parser.nvgt, character_parser.nvgt, shield_parser.nvgt — /-prefixed in-game commands and config-file parsers.
- menus/menu.nvgt — single home for every top-level menu (main menu, settings, stats, other UI screens). menus/menu_callbacks.nvgt and menus/map_menu.nvgt remain separate; map_menu.nvgt also houses `buildobj(string buildtype)`, the build dispatcher that routes each builder-menu entry and `/build` token to its `build_<entity>()` (moved here from map.nvgt).
- functions/extrafuncts.nvgt, mapfuncts.nvgt, charfuncts.nvgt, comfuncts.nvgt, savefuncts.nvgt, downloaderfuncts.nvgt, filefuncts.nvgt, packfuncts.nvgt, macfuncts.nvgt — small utilities (is_admin, array_contains, modifier-key helpers, file/path helpers, pack-resolution helpers, macro-bank helpers, etc.).
- deps/ — vendored libraries: form.nvgt (audio form, modified from BGT), form_menu.nvgt, setupmenu.nvgt, virtual_dialogs.nvgt, sound_pool.nvgt, keyhook.nvgt, key_hold.nvgt, key_config.nvgt (pure-script action binding system — a drop-in replacement for the engine's input_bind/input_conf using only public NVGT primitives, with its own SDL-scancode name table for friendly names like SPACE/LSHIFT/SLASH and legacy BGT aliases like LCONTROL/LMENU; parses its INI directly, no ini.nvgt dependency), savedata.nvgt, speech.nvgt, dlg.nvgt, dlgplayer.nvgt, downloader.nvgt, datetime.nvgt, time_elapsed.nvgt, rotation.nvgt.
- version.nvgt sits at the includes/ root (not under a subfolder) — the single source-of-truth `string version = "X.Y"` constant.

### includes/builder/ — entity definitions

One file per gameplay entity, grouped: audio/, construction/, interaction/, kombat/, misc/, transitions/, transportation/, traps/, zones/. The transportation/ group covers bike, vehicle, aircraft, airbeacon, and air_turbulence; the globals/glider.nvgt player-controlled glider is a peer subsystem in includes/main/globals/ rather than a builder entity. The one exception to the one-file-per-entity rule is the NPC system in kombat/, which is split across npc.nvgt (entity state + per-frame AI + movement loop + read/write/build) and npc_manager.nvgt (lifecycle / spawn-pool coordination) because the NPC behavior surface outgrew a single file; the sibling projectile.nvgt in kombat/ handles launch_* projectile lifetimes. Typical contents of an entity file:

- a class holding the entity's runtime state,
- a global array<class>@[] <thing>s(0) of live instances,
- spawn_<entity>(...) / destroy_all_<entity>s() helpers — `destroy_all_<entity>s()` MUST also be called from the cleanup block in `includes/main/globals/map.nvgt` (search for the `destroy_all_*()` run, alphabetical) so reload-after-edit and map switches free the entity's sounds / state. A missing wire-up means removed entities keep playing audio after a /remline reload,
- a <entity>check() / <entity>loop() runtime function called from game.nvgt,
- read_<entity>(string[] sd) — parses one info.sif line,
- write_<entity>(...) — writes one line back,
- build_<entity>() — interactive UI for adding the entity to a map.

The read_* / write_* / on-disk-format stability contract is covered in **Stability rules** above — anything you change here must respect it.

## Game data (data/)

Three sibling folders. All authored as plain text info.sif files alongside (optional) sound assets — the engine never hardcodes content, it scans these folders.

### data/builder/maps/

- **decompiled/<name>/data/** — authored maps. Always contains main.sif (the entity list described above) and meta.sif (owner, description, created date, modified date). Per-map sound assets live under the parent decompiled/<name>/ in kombat/, objects/, soundtracks/, etc. folders resolved by get_map_sound(...) lookups.
- **compiled/<name>.map** — encrypted pack form built from a decompiled folder. load_map() falls back here when the decompiled copy is absent. Currently empty in this checkout.
- **Stock maps in source control**: 2d_test, 3d_test, topdown_test, elevator_example, house_example, main. main is the title-screen / hub map; the rest are demos / smoke tests. When adding a new entity type, smoke-test it by adding a line to the matching mode's test map's data/main.sif and reloading.

### data/macros/

Scriptkey-bank command macros loaded by load_macros() and triggered from game_input.nvgt via ordered_scriptkeys (14 keys: backtick, 1–0, -, =, backspace) across three banks (plain / Shift / Shift+Alt) — 42 slots total. Each info.sif here is a one-macro-per-line table:

<cooldown_ms> <speak_bool> <command>

so e.g. 4000 true /rt runs /rt through the command parser when the slot is fired, with a 4 s cooldown and a spoken confirmation. The only subfolder still shipped is **default/<theme>/info.sif** (currently just classic) — the seed bank a fresh player starts from. Previous bundled banks (weapon quick-draw, item quick-give, in-builder scriptkeys) were removed because players define their own packs through /macset / /mc; adding a new entity, weapon, or item no longer requires a corresponding macro file edit.

## Sound assets (sounds/)

sounds/ is split into two top-level siblings — **decompiled/** for the loose-folder form authors edit (`sounds/decompiled/main/` for shared engine assets: characters, equipments/shields, equipments/weapons, keyboards, menus, misc; and `sounds/decompiled/builder/` for per-entity map-object assets: kombat/npc, kombat/projectiles, construction, transitions, transportation, traps, zones, audio, interaction, misc) — and **compiled/** for the encrypted pack form the shipped game reads (`sounds/compiled/main.spack` and `sounds/compiled/builder.spack`). Decompiled folders win on lookup; the packs are the fallback. There is no per-pack indirection layer above this — the old `sounds/<pack>/` selector and `soundpack` global were removed. Players customize audio by dropping clips into the relevant per-entity subfolder under `sounds/decompiled/main/` or `sounds/decompiled/builder/`.

Inside sounds/decompiled/main/:

- characters/<character>/ — per-character bundle. data/main.sif is the stat block parsed by charparse() (fields: weapon type, weapon type2, attack, defence, points, fall modifier, health, stamina, kills, lives, level, level modifier, experience, experience modifier, experience required); data/attacks.sif and data/bodyparts.sif are flat one-token-per-line word lists used to randomize attack/bone-damage flavor text. general/, map/, and the bare folder hold the sound clips that get_pack_sound("main/characters/<char>/...") resolves against. There is no sound-name list — clips are discovered by glob, so adding a clip is the wiring.
- equipments/shields/<name>/data/info.sif — 42 shields. key=value per line. Fields: defence, wear mode (0/1), weight, shield strength, shield passthrough, unlock level. Clips live in the sibling general/ subfolder: draw.ogg, wear.ogg, remove.ogg, hit.ogg, break1.ogg, break2.ogg.
- equipments/weapons/<category>/<name>/data/info.sif — 271 weapons across archery/, artillery/, explosive/, melee/. Common fields: damage, fire mode (0=single / 1=auto), x range, y range, z range, bullet speed, repeat time, spam time, weight, ammo, loaded ammo, max ammo, unlock level, stun mode. The category folder name must match weapon type in a character's info.sif; the leaf folder name must match weapon type2. Clips live in the sibling general/ subfolder and vary by weapon (draw, fire, hit, loop1..6, reload1..3, rico, empty, ping, block1..3, ref, on/off).
- keyboards/<theme>/, menus/<theme>/, misc/ — theme- and UI-keyed audio resolved by get_pack_sound("main/...") glob lookups.

Inside sounds/decompiled/builder/:

- kombat/npc/<group>/<name>/data/info.sif — 187 NPC types across animals/, bosses/, helpers/, humans/, robots/, specials/, zombies/. Stat block fields:
  - **Ranges** — x attack range, y attack range, z attack range, x sight range, y sight range, z sight range, patrol x range, patrol y range, patrol z range. Range fields accept the literal keywords minx/maxx/miny/maxy/minz/maxz or comma-pairs (minx,maxx) — these are resolved at spawn time against the active map's bounds, so an NPC with x sight range=maxx sees across the whole map regardless of map size. The patrol fields also accept the literal terrain token, which auto-fits the patrol bounds to the contiguous walkable terrain around the NPC's spawn tile (see patrol_x_terrain / patrol_y_terrain / patrol_z_terrain in npc.nvgt).
  - **Combat / progression** — health, lives, attack, defense, level, xp, fire speed, rest heal time, move speed.
  - **AI behavior** — chase mode (colon-pair, e.g. sight:none), chase time (triple a:b:c for the chase phases), teleport time (triple), targets (player, etc.), attacking, move x, move y, drop item, tel x, tel y, ambient heal, ambient heal time, hit and run, flee time, flee speed, terrain (any or specific tile types), provoke speed, chase terrains, use steps / use falls (auto or explicit), launch path, launching, launch category, launch subtype, launch time.
  - Sibling clips are matched by glob — at minimum spawn, hurt, death, taunt, life, tel, launch, heal_1..3; many add step1..N, hit1..N.
- kombat/projectiles/<name>/ — projectile sound bundles for launch_* AI behavior.
- construction/, transitions/, transportation/, traps/, zones/, audio/, interaction/, misc/ — per-entity map-object audio resolved by get_pack_sound("builder/...") and get_map_sound("builder/...") glob lookups from the engine.

When adding a new shield/weapon/NPC, the info.sif is the contract — every numeric field is read by name in the parser, missing fields fall back to engine defaults, and unknown fields are silently ignored. Folder name = the identifier used in macros (/dr <category> <name>) and in character/NPC builders.

## Audio model

NVGT sound_pool with HRTF. Player position is the vector me; listener orientation is me_rotation (degrees). Pools are advanced each frame via update_sound_pools(), and 3D plays use play_3d / play_extended_3d with calculate_theta(me_rotation) for listener heading. 2D-only sounds use play_stationary / play_stationary_extended. Per-tile/wall volumes and pitches travel with the entity (volume, pitch fields on each class) and are passed into the play call.

Sound assets are looked up via get_pack_sound("...") / get_map_sound("...") with glob patterns like main/characters/<chartype>/map/*camclear* or builder/construction/walls/<wallname>/*death*. The chartype, menutype, keyboardtheme strings drive theme selection within sounds/decompiled/main/.

**Adding a new sound_pool**: declare `sound_pool foopool;` in whichever file owns it (per-entity pools live at line 1 of the entity's `.nvgt`; subsystem pools in the subsystem's globals file; shared/generic pools in `dec.nvgt`/`game.nvgt`/`map.nvgt`), then append the name to the single `all_pools = {...}` array literal in `includes/main/globals/decpool.nvgt`. That one append wires it into initialize/update/pause/resume. If the pool plays positioned sounds that should pick up effect_space FX, also add a per-entity loop to `apply_effect_pools()` in `includes/builder/audio/effect_space.nvgt` (separate from `all_pools` because each loop needs the owning entity's coords) — the `airbeacons` entry there is the template.

## Player-facing docs (docks/)

- **docks/main/** — `changelog.txt`, `readme.txt`, `todo_list.txt`, `credits.txt`. Opened by `docksmenu()` / `dockread()` in sf.nvgt. `changelog.txt` is the source of truth for what shipped — trust it over readme/todo. Format: each version starts with a New in X.Y. header, followed by one paragraph per change in reverse-chronological order (newest at the top of the file). Entries describe the symptom, the root cause when it was a bug, and the resulting behavior, so the file doubles as a postmortem log.
- **docks/builder/** — per-feature `.tp` reference topics served by `helpread()` from the map builder's help menu. Filenames stay flat (no nested folders); helpread strips `docks/builder/` and `.tp` for the window title. New topics are picked up automatically — the `hp`/`help` command in `command_parser.nvgt` scans `docks/builder/*.tp` at runtime via `find_files`, so no `menu.nvgt` wiring is needed.

Rules for writing/editing these files live in memory, not here: changelog entry format and per-version caps, .tp prose constraints, readme/todo quirks.

The game version lives in `includes/version.nvgt` as `string version = "X.Y"` — single source of truth. Uncompiled launches sync `build/version.txt` from it; compiled binaries skip the sync. Main-menu "change game version" overrides are transient (reset on next launch).

## Build / release pipeline (build/)

`build/tools.bat` launches `build/tools.py` (Python 3.12), a menu-driven tool covering commit ops (commit, undo, push, history) and release ops (compile / package / release / website, individually or as a full run). Per-game settings live in `build/tools.ini`; host-wide tool paths live in `~/.game_tools/tools.ini`.

Pipeline: **compile** (nvgt -c -Q) → **package** (7-Zip portable, password-protected) → **release** (force-tag `V<version>0` with trailing zero, `gh release create`) → **website** (regex-update site HTML, commit + push).

`build/version.txt` is a derived artifact synced from `includes/version.nvgt` at uncompiled launch — don't edit directly; tools.py reads it.

This game does not ship an installer — only the 7z portable archive. The Inno Setup `installer.iss` and the `[installer]` block of `tools.ini` have been removed because players prefer portable. If you ever re-add an installer, both files need to come back together.

## Repo hygiene (.gitattributes, .gitignore)

CRLF enforcement is covered in **Stability rules** above; the rest:

- **.gitignore** keeps:
  - the `.claude` directory out of the tree, plus both `claude.md` and `CLAUDE.md` so this guidance file is excluded from the repo on every filesystem (lowercase covers case-insensitive Windows/macOS, uppercase covers case-sensitive Linux). The file stays on disk locally so Claude Code keeps reading it; it's just not shipped to GitHub.
  - all audio (*.mp3, *.ogg, *.wav) — the sounds/ folder ships separately and is downloaded on first run by downloadsounds() in sf.nvgt if missing. Don't commit clips.
  - *.map — compiled map packs are release artifacts, not source. Authored maps live as data/builder/maps/decompiled/<name>/data/main.sif and are committed; the data/builder/maps/compiled/ folder is intentionally empty in source.
  - New File*.txt — the dev's personal scratch / notes file. Cleared and rewritten frequently. Don't read or rely on its contents as authoritative; it isn't project documentation, just a private notepad. **Don't write new content to it.**
  - lib/ and releases/ — build outputs (NVGT runtime libs and the packaged release artifacts produced by build/tools.py).

## Deferred concerns (not bugs, but worth tackling eventually)

Known shape-of-the-code issues. None are urgent or breaking anything today. Don't proactively "fix" them; just be aware when the related area comes up.

- **No data-file versioning in info.sif files.** Every authored file is a flat key=value list with no version stamp; missing keys fall back to engine defaults. The day you change what an *existing* default means, every old file silently shifts behavior with no marker.
- **Glob-include aggregation at ~114 files is getting noisier.** Every symbol is visible everywhere; parse order depends on directory-walk order. No order-sensitive code today, but the risk grows.
- **Silent parser fallthrough in `map_parser.nvgt`.** Lines that don't match any expected `sd.length()` are dropped with no warning — malformed maps load "successfully" with entities silently absent.
- **Multi-length / open-ended encoding is bug-prone.** A spanning entity may need three discrete length variants (2d, legacy single-y topdown/3d, current min/max-y topdown/3d); a forgotten variant silently breaks one of them, and an over-permissive `>=N` lets garbage tokens through.
- **Sound lookups fail silently.** `get_pack_sound` / `get_map_sound` returning no match plays nothing — deliberate, but a clip-path typo is indistinguishable from "feature has no sound."
- **No tests or linter — the data layer is unverified.** The NVGT compiler catches syntax errors only. No check that read_/write_ agree, that authored keys are recognized, or that a parsed map's entity count matches the file. The concerns above all share this root.
