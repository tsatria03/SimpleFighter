# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

SimpleFighter is an audio-only action / map-builder game written in **NVGT** (Non-Visual Game Toolkit, an AngelScript-based engine). All gameplay code is .nvgt. There is no visual rendering — output is screen-reader speech plus HRTF spatial audio through NVGT's sound_pool.

## Running

There is no test suite or linter. Run or compile sf.nvgt with the NVGT runtime for development.

sf.nvgt is the entry. main() installs the keyhook, gates on SCREEN_READER_AVAILABLE / SOUND_AVAILABLE, blocks a second instance via gamstence.is_already_running, initializes sound pools, parses character / shield / weapon data, optionally checks for updates against the compiled-in `version` constant, downloads the sounds/ folder if missing, then loops mainmenu().

## Stability rules — read first, break never

These are the load-bearing invariants of the codebase. Violate one and either old maps stop loading, parsers silently fail, or the runtime drifts. Read these before any edit.

- **read_* / write_* signatures and the on-disk line format are a contract.** Every entity in includes/builder/**/*.nvgt exposes a read_<entity>(string[] sd) that parses one info.sif line and a write_<entity>(...) that produces one. Old maps in data/builder/maps/decompiled/<name>/data/main.sif must keep loading; the dispatched sd.length() checks in map_parser.nvgt must keep passing. Refactoring inside build_* (the interactive UI) is generally safe; changing what read_* / write_* accept or emit is not.
- **mapmode is creation-locked.** A map's mode 2d|topdown|3d line is set when the map is created and read by load_map(). Do not mutate mapmode mid-map. Map-editing commands (editline, addline, remline in the command parser) explicitly reject mode changes. The parser's sd.length() checks are **multi-valued** (e.g. ==10 || ==11 || ==12 for platforms; ==18 || ==20 for doors; or `>=N` for entities with optional trailing tokens like blockage, elevator, passage, several zones). Extra lengths encode 3d (z fields **inserted inside the coordinate block**, not appended) and the topdown/3d min/max-y variant. Preserve every length case when adding or modifying entities.
- **CRLF line endings are enforced.** *.sif, *.nvgt, *.py, *.txt, *.bat, *.ps1, *.iss, *.md, and *.ini are pinned to text eol=crlf in .gitattributes. The NVGT compiler, in-game .sif readers, and build scripts all expect Windows line endings. Tools that auto-strip CRLF will break the working tree silently. Generate new files with CRLF, or call the split_lines() helper in extrafuncts.nvgt on the read side.
- **Coordinates are double.** Some legacy fields are still int; convert when you touch them. Don't introduce new int coords.
- **Capability flags gate input handlers as a set.** moveable, fireable, cammable, healable, jumpable, quittable, speedable, spiable, turnable (and others in dec.nvgt) gate which keys do what. pause_game() and resume_game() flip them as a coordinated set — don't toggle them individually unless you know exactly which subsystem you're freezing.
- **3d wall/platform tiles spawn per-z.** Volumetric entities in 3d mode loop for(double z = minz; z <= maxz; z++) and push each per-z spawn_platform id into a platform_ids array on the parent entity. See wall.nvgt for the canonical pattern. Don't try to represent height with a single platform record.
- **Builder UI uses the audio form for multi-input flows.** form.create_window, form.create_input_box, form.create_button, form.monitor, form.is_pressed. See sf.nvgt's dockread / helpread for the canonical shape. Single one-shot prompts may use vd.input_box. Don't roll your own input loop.
- **info.sif key=value pairs use spaces, not underscores, in field names.** The on-disk convention is `key with spaces=value` (e.g. `weapon type=melee`, `fire speed=300`, `hit and run=true`, `flee time=2000`), reserving underscores only for *identifier values* that legitimately need them (folder names like `long_rope`, tile names like `wallstone_dark`, item names like `health_kit`). Parser keys, builder form key arrays, doc references, and authored .sif files all need to stay aligned on this — if you add a new key, write it spaced; if you find an old underscored key like `hit_and_run` or `flee_time` anywhere, it's a leftover that should be migrated (sweep the parser, the builder's keys / cb_keys arrays, every info.sif file that uses it, and the matching .tp doc together). Note that internal AngelScript variable names keep their underscores (e.g. `self.hit_and_run`, `self.flee_time`) — only the *user-facing key strings* and authored file content follow the spaces rule.

## Script side vs engine side — investigate script first, modify engine last

The codebase spans two repos: SimpleFighter (this one, .nvgt scripts) and Legacy-NVGT (the engine, C++). Engine changes are slower to iterate, harder to revert, and require a `scons` rebuild before they're testable, so the default rule when chasing a bug or a perf issue is **diagnose in the script layer first**, and only reach for engine changes once you've ruled out the script layer with concrete evidence.

- **Symptom → script side first.** When a behavior is wrong or slow, start by tracing it through the `.nvgt` call sites that produce it. Most of what feels like an "engine issue" turns out to be a wrapper, a resolver, or a hot loop in script — and even when the engine *is* involved, the script side usually has a way to mitigate or sidestep it without touching C++.
- **Isolate with a minimal repro before touching either side.** When a bug only shows up in complex maps or large packs, build the smallest version that still triggers it and bisect. The "50 signs with `signtype=none` still lags" experiment that uncovered the O(N) pack scan was worth hours of engine speculation.
- **Stub or comment out instead of optimizing.** When a script function might be the bottleneck, comment out its call site and rerun. If the symptom disappears, you've found your layer without changing logic. Then optimize for real. Engine changes don't have this luxury — every C++ change is at least a rebuild round-trip.
- **Engine changes for what only the engine can do.** New API surface (e.g. `directory_rename`, `add_sound_default_pack`), fundamental capability gaps (multi-pack chain, in-memory `BASS_StreamCreateFile` for packed sounds), or fixes below the script binding boundary (per-byte decrypt loops, BASS callback overhead) are real engine work. Script-layer wrappers, lookup costs, per-frame entity loops, and audio-resolution helpers are not.
- **Don't conflate "the engine could be faster" with "the engine is the bottleneck."** Engine optimizations off the actual hot path produce no observable change for the player. `pack_buffer_decrypt` vectorization, single-hashmap-lookup in `read_file`, and `memload`-as-default were real wins that did **not** fix entity-heavy map sluggishness — because the hot path was a script-side O(N) string scan, not pack I/O.

When you do change the engine, note it in this file so the next person knows the engine isn't stock NVGT.

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

The expected sd.length() for each entity in map_parser.nvgt is **multi-valued** (e.g. ==10 || ==11 || ==12 for platforms, ==18 || ==20 for doors, or `>=N` for entities with optional trailing tokens like blockage, elevator, passage) — extra lengths encode 3d (z fields **inserted inside the coordinate block**, not appended) and the topdown/3d min/max-y variant. When adding or modifying an entity, preserve every length case.

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

## Include tree

sf.nvgt includes only includes/includes.nvgt, which pulls in three NVGT stdlib files (bgt_compat, instance, token_gen — these resolve from the NVGT install, not the repo, so don't flag them as missing) followed by glob-includes over every directory under includes/builder/ and includes/main/.

### includes/main/ — engine

- globals/dec.nvgt — central engine state: map bounds (minx/maxx/miny/maxy/minz/maxz), camera-selection markers (sel_left_set … sel_top_set), character stats (health, stamina, attack, defence, level, xp), capability flags (moveable, fireable, jumpable, runnable, etc.), sound slots, timers, theme strings (chartype, keyboardtheme, menutype), and the active map identity (mapname, mapmode, mapowner).
- globals/game.nvgt — main game loop. Iterates wait(5) and dispatches per-frame *check() and *loop() calls for every entity family (doors, elevators, hazards, walls, npcs, bullets, bombs, fires, …) plus update_sound_pools(), checkdeath(), checkloc().
- globals/game_input.nvgt — keyboard dispatch (slash for command parser, scriptkey banks via Shift / Shift+Alt, run-mode via Alt, etc.).
- globals/map.nvgt — clearmap(), camera-marker selection, movement and physics helpers.
- globals/game_handlers.nvgt — input-handler callbacks split out of game_input.nvgt; the per-key behavior bodies live here.
- globals/weapon.nvgt, weapon_manager.nvgt, bullet.nvgt, bodyfall.nvgt, hook.nvgt, sonar.nvgt, spier.nvgt, stunner.nvgt, tracker.nvgt, inventory.nvgt, fadepool.nvgt, updater.nvgt, character_manager.nvgt, shield_manager.nvgt, glider.nvgt — runtime subsystems.
- parsers/map_parser.nvgt — load_map() reads data/builder/maps/decompiled/<name>/data/main.sif (plain text) or the compiled .map pack, then dispatches each line to the appropriate read_<entity>(). The dispatcher itself lives in dispatch_entity_line(string[] sd) and is also called by the /spawn command path so a typed-args spawn behaves the same as a map load.
- parsers/command_parser.nvgt, character_parser.nvgt, shield_parser.nvgt — /-prefixed in-game commands and config-file parsers.
- menus/menu.nvgt — single home for every top-level menu (main menu, settings, stats, other UI screens). menus/menu_callbacks.nvgt and menus/map_menu.nvgt remain separate.
- functions/extrafuncts.nvgt, mapfuncts.nvgt, charfuncts.nvgt, comfuncts.nvgt, savefuncts.nvgt, downloaderfuncts.nvgt, filefuncts.nvgt, packfuncts.nvgt, macfuncts.nvgt — small utilities (is_admin, array_contains, modifier-key helpers, file/path helpers, pack-resolution helpers, macro-bank helpers, etc.).
- deps/ — vendored libraries: form.nvgt (audio form, modified from BGT), form_menu.nvgt, setupmenu.nvgt, virtual_dialogs.nvgt, sound_pool.nvgt, keyhook.nvgt, key_hold.nvgt, savedata.nvgt, speech.nvgt, dlg.nvgt, dlgplayer.nvgt, downloader.nvgt, datetime.nvgt, time_elapsed.nvgt, rotation.nvgt.
- version.nvgt sits at the includes/ root (not under a subfolder) and is the single source-of-truth `string version = "X.Y"` constant described under the changelog rules below.

### includes/builder/ — entity definitions

One file per gameplay entity, grouped: audio/, construction/, interaction/, kombat/, misc/, transitions/, transportation/, traps/, zones/. The transportation/ group covers bike, vehicle, aircraft, airbeacon, and air_turbulence; the globals/glider.nvgt player-controlled glider is a peer subsystem in includes/main/globals/ rather than a builder entity. The one exception to the one-file-per-entity rule is the NPC system in kombat/, which is split across npc.nvgt (entity state + read/write/build), npc_manager.nvgt (lifecycle / spawn-pool coordination), and npc_runner.nvgt (per-frame AI + movement loop) because the NPC behavior surface outgrew a single file; the sibling projectile.nvgt in kombat/ handles launch_* projectile lifetimes. Typical contents of an entity file:

- a class holding the entity's runtime state,
- a global array<class>@[] <thing>s(0) of live instances,
- spawn_<entity>(...) / destroy_all_<entity>s() helpers,
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

### docks/builder/

In-game help topics, one .tp file per topic, served by helpread() in sf.nvgt. Each is plain prose (character.tp, npc.tp, weapon.tp, shield.tp, effect_space.tp, obscurity_zone.tp, character_blocker.tp, command_console.tp, tts_enemie.tp, aircraft.tp, glider.tp, switch.tp, cloner.tp, pack.tp). Filenames must stay flat — no nested folders — because helpread strips docks/builder/ and .tp from the path for the window title. Add new help topics by dropping a new .tp here and wiring it into the help menu in menu.nvgt.

**Help topic prose rules — never reference engine code from a .tp file.** Topic files are player-and-author facing documentation, not internal dev notes. Don't name function names (fallcheck, charparse, spawn_npc, melee_strike, update_char_*, etc.), don't name source files (map.nvgt, weapon.nvgt, character_parser.nvgt, etc.), and don't name internal variables (fallcounter, wepchar, me_rotation, etc.). Describe the *behavior* the player or author observes — "each tile beyond the threshold counts for fall modifier raw damage" instead of "fallcounter times fall modifier in fallcheck()". If a behavior is too tangled to explain without naming code, that's usually a sign the explanation should be shorter or the design is leaking.

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
  - **AI behavior** — chase mode (colon-pair, e.g. sight:none), chase time (triple a:b:c for the chase phases), teleport time (triple), targets (player, etc.), attacking, move x, move y, drop item, tel x, tel y, ambient heal, ambient heal time, hit_and_run, flee_time, flee_speed, terrain (any or specific tile types), provoke_speed, chase_terrains, use steps / use falls (auto or explicit), launch path, launching, launch category, launch subtype, launch time.
  - Sibling clips are matched by glob — at minimum spawn, hurt, death, taunt, life, tel, launch, heal_1..3; many add step1..N, hit1..N.
- kombat/projectiles/<name>/ — projectile sound bundles for launch_* AI behavior.
- construction/, transitions/, transportation/, traps/, zones/, audio/, interaction/, misc/ — per-entity map-object audio resolved by get_pack_sound("builder/...") and get_map_sound("builder/...") glob lookups from the engine.

When adding a new shield/weapon/NPC, the info.sif is the contract — every numeric field is read by name in the parser, missing fields fall back to engine defaults, and unknown fields are silently ignored. Folder name = the identifier used in macros (/dr <category> <name>) and in character/NPC builders.

## Audio model

NVGT sound_pool with HRTF. Player position is the vector me; listener orientation is me_rotation (degrees). Pools are advanced each frame via update_sound_pools(), and 3D plays use play_3d / play_extended_3d with calculate_theta(me_rotation) for listener heading. 2D-only sounds use play_stationary / play_stationary_extended. Per-tile/wall volumes and pitches travel with the entity (volume, pitch fields on each class) and are passed into the play call.

Sound assets are looked up via get_pack_sound("...") / get_map_sound("...") with glob patterns like main/characters/<chartype>/map/*camclear* or builder/construction/walls/<wallname>/*death*. The chartype, menutype, keyboardtheme strings drive theme selection within sounds/decompiled/main/.

## Player-facing docs (docks/)

The docks/ folder splits into two buckets that mirror the code layout:

- **docks/main/** — files the in-game docs menu (docksmenu() / dockread() in sf.nvgt) opens: changelog.txt, readme.txt, todo_list.txt, credits.txt.
- **docks/builder/** — per-feature reference topics (the .tp files described in the section above), served by helpread() from the map builder's help menu.

When the dev or a player asks "where does the changelog live?" it's now `docks/main/changelog.txt`, not `docks/changelog.txt`. The same migration applied to readme and todo_list. Code references in sf.nvgt have already been updated to read from the new paths; old code paths or scripts referencing `docks/<file>.txt` directly need to be updated to `docks/main/<file>.txt`.

- **docks/main/changelog.txt** — the **source of truth** for what has actually shipped, version by version, from v1.0 through v11.6. Every feature, fix, and behavior change has an entry here. **Trust this over readme.txt and todo_list.txt** — those drift; the changelog does not. If a player or the dev asks "is X implemented?", grep this file before assuming anything. Format: each version starts with a New in X.Y. header, followed by one paragraph per change in reverse-chronological order (newest at the top of the file). Entries describe the symptom, the root cause when it was a bug, and the resulting behavior, so the file doubles as a postmortem log.

  **Writing new changelog entries — rules:**
  - **Player-facing prose only.** Describe what the player sees, hears, or can now do — never the code-side cause, internal field names, parser branches, or refactors. If a change has no observable effect for the player, it does not belong in the changelog at all.
  - **One entry = one line of one or more sentences.** Minimum 1 sentence, maximum 3 sentences per entry. **Default to 1 sentence.** Use 2 only when the change has a meaningful caveat, a why, or a paired side-effect the player should know about. Use 3 only when the change is genuinely substantial — multiple linked behaviors, a player-visible workflow shift, or a fix whose mechanism is non-obvious. A small fix or a one-off feature with no caveats is 1 sentence, period. Do not pad to fill a sentence count.
  - **Skip changes that are too small to matter to the player.** If a fix or addition only benefits the dev/code, or is so minor that reading about it adds nothing for the player, leave it out.
  - **Per-version entry caps (independent — each version's cap applies to that version alone, not to a shared budget across the major):**
    - A major `.0` release (e.g. v11.0) holds **up to 20 entries / lines**.
    - Each minor release after it (e.g. v11.1, v11.2, …) holds **up to 10 entries / lines**.
    - Once the in-progress version is full, **roll to the next minor** (or the next major's `.0` if you're already past .9 / it makes sense) rather than overflowing the cap. v10.0 with 20 entries followed by v10.1 with 10 entries is the canonical example of the rule in practice.
  - **When opening a new version block** (adding the first entry under a `New in X.Y.` header that didn't exist before), also bump `includes/version.nvgt`'s `version = "X.Y"` constant to match. The changelog and the in-script version are two halves of the same shipped artifact; opening a new version block in only one of them leaves the codebase in an inconsistent state where the changelog claims X.Y exists but the running game still self-reports as X.Y-1. The bump is a one-line edit and should land in the same change that opens the version block.
  - Order within a version stays reverse-chronological (newest entry at the top of that version's block), matching the existing file.

- **docks/main/readme.txt** — the player-facing high-level overview: a short pitch, a folder-layout summary (data/, docks/, etc.), and a long enumerated list of in-game keyboard commands grouped by purpose (movement, menus, sonar, building, etc.). This is the *general* documentation; deeper per-feature reference lives in docks/builder/*.tp (character.tp, npc.tp, weapon.tp, etc.) served by helpread(). When the user asks how a specific subsystem works, prefer the .tp file over readme.txt. The readme is **out of date** with respect to map modes — the prose in older sections still reflects the 2d-only era; topdown and 3d map building have shipped, and the readme needs a sweep to catch up. Don't mirror its older claims as authoritative; cross-check against the actual code in includes/ and the per-feature .tp files when answering questions.

- **docks/main/todo_list.txt** — combined "done" log + idea backlog. Lines beginning with **Finished. describe things that have already shipped in past versions; lines beginning with ****Unfinished. are things that *might* be added later. **Items in the unfinished list are not commitments** — they are notes the dev wrote to themselves; presence here does not mean a feature is planned, scoped, or guaranteed to land. Don't promise the user that a listed unfinished item will be implemented, and don't treat it as a prioritized backlog. When a feature listed as Unfinished actually ships, flip the prefix to **Finished. and leave it in the file as part of the history.

  Note: there is no longer a docks/version.txt. The version lives as a `string version = "X.Y";` declaration in **includes/version.nvgt**, which is the single source of truth — the dev edits this file directly when bumping versions. At dev launch (when `SCRIPT_COMPILED` is false), sf.nvgt's main() reads build/version.txt, compares it to the in-script `version`, and rewrites it only if they differ, so build/version.txt stays in sync as a derived artifact for tools.py and installer.iss to consume. Compiled binaries skip this sync entirely. Runtime overrides for players are handled through the main menu's "change game version" option, which assigns to the same variable; that override is transient and resets to the compiled-in value on next launch.

## Build / release pipeline (build/)

build/tools.bat launches build/tools.py under Python 3.12. The script is a menu-driven release tool:

- **Commit ops**: make a commit (interactive summary + multi-line description, optional push), undo last commit (git reset --soft HEAD~1, refuses if nothing unpushed), push, history (last 50 commits with per-commit submenu: show description, copy SHA, create/push tag, copy tag, soft/hard reset).
- **Release ops**: full release, or any of compile-only / package-only / release-only / website-only. Internally these all call run_release(skip_compile, skip_package, skip_release, skip_website, skip_empty_release) with SKIP=0 (ask), DO=1 (force run), SILENT_SKIP=2 (skip silently). The script can also be invoked non-interactively with five integer args.

Pipeline stages inside run_release:

1. **Compile** — runs nvgt -c -Q sf.nvgt directly. tools.py reads build/version.txt (kept in sync from includes/version.nvgt — see docks section above) to compute the release tag V<version>0. The compiled cst/ output is moved into releases/windows/<Game>_windows_portable_password_is_<password>/<NVGT_OUT>/ (replacing the previous copy).
2. **Package** — builds two artifacts in releases/archives/:
   - 7-Zip portable: 7z a -t7z ... -mx=9 -m0=LZMA2 -md=64m -mfb=64 -ms=on -mmt=12 -p<password> -mhe=on (encrypted, headers encrypted).
   - Inno Setup installer via iscc /Q with /D defines for MyAppId, MyAppName, MyAppURL, MyAppExeName, MyAppPassword, MySourcePath. The .iss reads version.txt at compile time and installs to {autopf}\tsatria03\<Game>\cst with an AppMutex={#MyAppName}_Mutex for single-instance enforcement.
3. **Release** — force-tags HEAD as V<version>0, deletes any existing GitHub release for that tag, then gh release create with both archive + installer attached.
4. **Website** — runs site_updater.ps1 (regex-replaces V\d+\.\d+0 with the new tag and V\d+\.\d+ with the new version in the site HTML), then commits + pushes the change in the separate site repo (skipping if a matching commit already exists).

### Configuration

- **build/tools.ini** — per-game settings:
  - [game] name, password, nvgt_file — the password is the 7z / installer password and is also embedded in the artifact filenames.
  - [installer] iss, app_id, app_url, exe_name — Inno Setup parameters (the app_id is the GUID baked into AppId={{{#MyAppId}}).
  - [site] html, repo, path — absolute path to the site HTML, the repo root for committing, and the in-repo path for git add.
- **~/.game_tools/tools.ini** — host-wide tool paths under [tools]: nvgt, sevenzip, iscc, gh. Not in this repo.
- **build/version.txt** — single line, plain version number (e.g. 11.1). Derived from includes/version.nvgt, kept in sync by sf.nvgt's main() on every uncompiled launch — don't edit it directly, edit version.nvgt and run sf.nvgt once. tools.py reads this file to compute the release tag V<version>0 (a trailing zero is appended); the website regex distinguishes tag-with-trailing-zero from version-without. installer.iss also reads it at install-build time for the installer's version metadata.

When changing the release flow, update tools.py and installer.iss together — the installer's MySourcePath is computed from WIN_SOURCE in tools.py and depends on the password embedded in the folder name.

## Repo hygiene (.gitattributes, .gitignore)

CRLF enforcement is covered in **Stability rules** above; the rest:

- **Linguist overrides** in .gitattributes classify *.nvgt as AngelScript and *.sif as INI so GitHub's language stats and syntax highlighting don't show the project as ~100% other languages. *.dat is forced to Binary. The big block of additional linguist-language lines is forward-compatible — most of those extensions don't exist in this repo yet.
- **.gitignore** keeps:
  - the `.claude` directory out of the tree. The previous `claude.md` lowercase entry was removed because on case-insensitive Windows filesystems it would also match the tracked **CLAUDE.md**, so any casing rename would silently take the file out of git. Don't add it back.
  - all audio (*.mp3, *.ogg, *.wav) — the sounds/ folder ships separately and is downloaded on first run by downloadsounds() in sf.nvgt if missing. Don't commit clips.
  - *.map — compiled map packs are release artifacts, not source. Authored maps live as data/builder/maps/decompiled/<name>/data/main.sif and are committed; the data/builder/maps/compiled/ folder is intentionally empty in source.
  - New File*.txt — the dev's personal scratch / notes file. Cleared and rewritten frequently. Don't read or rely on its contents as authoritative; it isn't project documentation, just a private notepad. **Don't write new content to it.**
  - lib/ and releases/ — build outputs (NVGT runtime libs and the packaged release artifacts produced by build/tools.py).

## Deferred concerns (not bugs, but worth tackling eventually)

Known shape-of-the-code issues. None are urgent or breaking anything today. Don't proactively "fix" them; just be aware when the related area comes up.

- **No data-file versioning in info.sif files.** Every authored file (character, weapon, shield, npc, map) is a flat key=value list with no version stamp. Missing keys fall back to engine defaults, which is fine — but the day you change what an *existing* default means, every old file that omitted the key silently shifts behavior with no marker saying which engine version it was authored against.

- **`includes/main/globals/dec.nvgt` is global-soup.** ~183 lines declaring globals for almost every subsystem (map bounds, player stats, all 17 capability flags, sound slots, theme strings, active-map identity). Any operation that needs to coordinate across the state set (pause/resume, save-snapshots, reset-to-title) has to know which 50 globals to touch and in what order.

- **Glob-include aggregation at ~116 files is getting noisier.** sf.nvgt → includes/includes.nvgt globs over everything under includes/builder/** and includes/main/**. Every symbol is visible everywhere, and parse order depends on what the OS returns from the directory walk. No order-sensitive code today, but the risk grows with file count.

- **Silent parser fallthrough in `includes/main/parsers/map_parser.nvgt`.** Each entity dispatch checks `sd.length()` against expected values; lines that don't match any variant are dropped with no warning. A malformed map (typo, stale tool, missing field) loads "successfully" with entities silently absent.

- **Multi-length / open-ended encoding is non-obvious and bug-prone.** A new spanning entity may need three discrete sd.length() variants (2d, legacy single-y topdown/3d, current min/max-y topdown/3d) or an open-ended `>=N` check when trailing tokens are optional. A forgotten variant silently breaks one of: backward compatibility, 3d support, or topdown support; an `>=N` that's too permissive lets garbage trailing tokens through to read_<entity>.

- **Sound lookups fail silently.** `get_pack_sound("...")` / `get_map_sound("...")` returning no match plays nothing. *Deliberate* on the player side — a missing clip should never spam a screen reader during gameplay — but a typo in a clip path is indistinguishable from a feature with no sound, which makes authoring brutal.

- **`remove_platform()` uses array indices, which go stale the moment any other platform is removed.** Entities that own backing platforms (lifts, moving platforms, passages, walls, staircases, conveyor belts, vanishing platforms, floor breakers, hazard side-ledges) store the integer index returned from `spawn_platform()` at spawn time, but `remove_platform()` calls `platforms.remove_at(id)` which compacts the global array — every other entity's still-stored id past that point now points to the wrong platform. The bug stays hidden during normal gameplay; the trigger is the chained `destroy_all_lifts` / `destroy_all_moving_platforms` / `destroy_all_passages` from `clearmap()`, where each removal shifts the array out from under the next call. Internal reverse-order sorting within each function only fixes drift *within* that function, not across the chain.

- **No tests or linter — the data layer is unverified.** The NVGT compiler catches syntax errors and nothing else. There is no automated check that `read_<entity>` and `write_<entity>` agree, that every key in an authored `info.sif` is one the parser actually recognizes, or that a parsed map contains as many entities as the file had non-blank lines. The three deferred concerns immediately above (versioning, parser fallthrough, dual-length encoding) all share the same root: silent failure in a data-driven layer with no validation pass.
