---
name: project_include_tree
description: The src/includes/ architecture map — main/ engine subsystems and builder/ per-entity definitions, plus the glob-include aggregation and the one-file-per-entity contract.
metadata:
  type: project
---

`src/sf.nvgt` includes only `includes/includes.nvgt` (resolved relative to the script → `src/includes/`), which pulls in three NVGT stdlib files (bgt_compat, instance, token_gen — these resolve from the NVGT install, not the repo, so don't flag them as missing) followed by glob-includes over every directory under `src/includes/builder/` and `src/includes/main/`. At ~131 files every symbol is visible everywhere and parse order follows directory-walk order (see [[project_deferred_concerns]]).

## src/includes/main/ — engine

- **globals/dec.nvgt** — central engine state: map bounds (minx/maxx/miny/maxy/minz/maxz), camera-selection markers (sel_left_set … sel_top_set), character stats (health, stamina, attack, defence, level, xp), capability flags (moveable, fireable, jumpable, runnable, etc.), timers, theme strings (chartype, keyboardtheme, menutype), and the active map identity (mapname, mapmode, mapowner). Sound-pool declarations and helpers live in the sibling decpool.nvgt.
- **globals/decpool.nvgt** — owns the sound_pool array. `initialize_sound_pools()` (called once at startup), `update_sound_pools()` (called every frame from game.nvgt), `pause_pools()` / `resume_pools()` for global freeze, and `apply_map_pool()` which flips `sound_pool_default_y_elevation` based on mapmode.
- **globals/controls.nvgt** — declares the global `key_config controls;` and `load_controls()` which reads `data/main/config/keyboard.ini` at startup (sf.nvgt aborts if it fails). Also exposes `keyboard_actions_in_order()` for the settings-menu listing.
- **globals/game.nvgt** — main game loop. Iterates `wait(5)` and dispatches per-frame `*check()` and `*loop()` calls for every entity family (doors, elevators, hazards, walls, npcs, bullets, bombs, fires, …) plus `update_sound_pools()`, `checkdeath()`, `checkloc()`.
- **globals/game_input.nvgt** — thin per-frame dispatcher: calls the `handle_*_keys()` functions in game_handlers.nvgt in order, gated by freezgame and jumping/run-mode state.
- **globals/map.nvgt** — `clearmap()`, camera-marker selection, movement and physics helpers.
- **globals/game_handlers.nvgt** — the actual `handle_*_keys()` bodies (command, macro, inventory, draw, hook, speed, height, spier, facing, rotation, step, jump, camera, kombat, sonar, misc, …). All key checks go through the global `controls` (a key_config) using action names defined in `data/main/config/keyboard.ini` — no raw `key_pressed(KEY_*)` calls.
- **globals/weapon.nvgt, weapon_manager.nvgt, bullet.nvgt, bodyfall.nvgt, hook.nvgt, sonar.nvgt, spier.nvgt, stunner.nvgt, tracker.nvgt, inventory.nvgt, fadepool.nvgt, updater.nvgt, character_manager.nvgt, shield_manager.nvgt, glider.nvgt, arena.nvgt** — runtime subsystems (arena.nvgt is the arcade-arena survival mode; see [[project_arcade_arena_revival]]).
- **parsers/map_parser.nvgt** — `load_map()` reads `data/builder/maps/decompiled/<name>/data/main.sif` (plain text) or the compiled .map pack, then dispatches each line to the appropriate `read_<entity>()`. The dispatcher itself lives in `dispatch_entity_line(string[] sd)` and is also called by the /spawn command path so a typed-args spawn behaves the same as a map load.
- **parsers/command_parser.nvgt, character_parser.nvgt, shield_parser.nvgt** — /-prefixed in-game commands and config-file parsers.
- **menus/menu.nvgt** — single home for every top-level menu (main menu, settings, stats, other UI screens). `menus/menu_callbacks.nvgt` and `menus/map_menu.nvgt` remain separate; map_menu.nvgt also houses `buildobj(string buildtype)`, the build dispatcher that routes each builder-menu entry and `/build` token to its `build_<entity>()` (moved here from map.nvgt).
- **functions/extrafuncts.nvgt, mapfuncts.nvgt, charfuncts.nvgt, comfuncts.nvgt, savefuncts.nvgt, downloaderfuncts.nvgt, filefuncts.nvgt, packfuncts.nvgt, macfuncts.nvgt** — small utilities (is_admin, array_contains, modifier-key helpers, file/path helpers, pack-resolution helpers, macro-bank helpers, etc.).
- **deps/** — vendored libraries: form.nvgt (audio form, modified from BGT), form_menu.nvgt, setupmenu.nvgt, virtual_dialogs.nvgt, sound_pool.nvgt, keyhook.nvgt, key_hold.nvgt, key_config.nvgt (pure-script action binding system — a drop-in replacement for the engine's input_bind/input_conf using only public NVGT primitives, with its own SDL-scancode name table for friendly names like SPACE/LSHIFT/SLASH and legacy BGT aliases like LCONTROL/LMENU; parses its INI directly, no ini.nvgt dependency), savedata.nvgt, speech.nvgt, dlg.nvgt, dlgplayer.nvgt, downloader.nvgt, datetime.nvgt, time_elapsed.nvgt, rotation.nvgt.
- **version.nvgt** sits at the `src/includes/` root (not under a subfolder) — the single source-of-truth `string version = "X.Y"` constant. See [[project_build_pipeline]].

## src/includes/builder/ — entity definitions

One file per gameplay entity, grouped: audio/, construction/, interaction/, kombat/, misc/, transitions/, transportation/, traps/, zones/. The transportation/ group covers bike, vehicle, aircraft, airbeacon, and air_turbulence; the globals/glider.nvgt player-controlled glider is a peer subsystem in `src/includes/main/globals/` rather than a builder entity. The one exception to the one-file-per-entity rule is the NPC system in kombat/, split across **npc.nvgt** (entity state + per-frame AI + movement loop + read/write/build) and **npc_manager.nvgt** (lifecycle / spawn-pool coordination) because the NPC behavior surface outgrew a single file; the sibling **projectile.nvgt** in kombat/ handles `launch_*` projectile lifetimes.

Typical contents of an entity file:

- a class holding the entity's runtime state,
- a global `array<class>@[] <thing>s(0)` of live instances,
- `spawn_<entity>(...)` / `destroy_all_<entity>s()` helpers — `destroy_all_<entity>s()` MUST also be called from the cleanup block in `src/includes/main/globals/map.nvgt` (search for the `destroy_all_*()` run, alphabetical) so reload-after-edit and map switches free the entity's sounds / state. A missing wire-up means removed entities keep playing audio after a /remline reload,
- a `<entity>check()` / `<entity>loop()` runtime function called from game.nvgt,
- `read_<entity>(string[] sd)` — parses one info.sif line,
- `write_<entity>(...)` — writes one line back,
- `build_<entity>()` — interactive UI for adding the entity to a map.

The read_/write_/on-disk-format stability contract lives in [[project_stability_rules]]. New builder entities go in alphabetical order within their category (see [[feedback_alphabetize_builder_entities]]).
