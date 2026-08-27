# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This file is a **lean dispatcher**. It carries only the orientation you need before you know what you're doing, plus a trigger for every load-bearing rule. The detail lives in the `aidocks/` memory files (indexed in `aidocks/MEMORY.md`) — open the linked `[[memory]]` before editing in its area. The memory files are not auto-loaded, so treat every trigger below as "there is a rule here; go read it before you touch this."

## What this is

SimpleFighter is an audio-only action / map-builder game (currently v14.2) written in **NVGT** (Non-Visual Game Toolkit, an AngelScript-based engine). All gameplay code is .nvgt (~131 files, ~54k lines). There is no visual rendering — output is screen-reader speech plus HRTF spatial audio through NVGT's sound_pool. It's really two games on one content engine: the **arcade arena** (launch-and-fight survival mode) and **maps + the map builder** (author/play maps in 2d, topdown, or 3d), with 270+ weapons, 40+ shields, and ~187 NPCs shipping ready-made as plain-text `info.sif` content.

## Layout — code and assets are split

- **`src/`** — code only. Entry `src/sf.nvgt`, plus `src/includes/`.
- **`sf/`** — runtime assets + launcher. `sf/sf.py` (launcher), `sf/data/`, `sf/docks/`, `sf/sounds/`, `sf/lib/`.
- **`build/`** — build/release pipeline. **`releases/`** — compiled outputs (gitignored).
- **`aidocks/`** — this project's memory folder (committed). "Memory" / "memories" always means this folder.

**The cwd trick:** `sf/sf.py` runs `../src/sf.nvgt` through NVGT but sets **cwd = `sf/`**, so every cwd-relative path in the code (`lib/...`, `sounds/...`, `data/...`, `docks/...`) resolves under `sf/`, while `#include"includes/includes.nvgt"` resolves relative to the script → `src/includes/`. So a path naming a *file on disk* is under `src/` or `sf/`; the bare `data/...` / `sounds/...` / `docks/...` strings in the code are cwd-relative against `sf/`. Full detail: **[[project_path_conventions]]**.

**Engine is pinned to the legacy fork at `C:\nvgt`** (BASS audio; `sf.py` runs `C:\nvgt\nvgt.exe` — the console build, windowless via `CREATE_NO_WINDOW`, so it can capture compile errors to `sf/errors.txt`). A newer stock NVGT at `C:\nvgt2` (miniaudio) is only for testing other people's games — do not target it or treat upstream NVGT as authoritative. See **[[project_engine_pinned_nvgt2]]**.

## Running

No test suite or linter. The game is launched with `sf/sf.py` (runs `src/sf.nvgt` under `C:\nvgt\nvgt.exe`, cwd `sf/`) and compiled/packaged via `build/tools.py` — but **the dev runs and builds it, not Claude**: never launch or compile it yourself (**[[feedback_dont_run_or_build_the_game]]**). `src/sf.nvgt` is the entry; its main() installs the keyhook, gates on SCREEN_READER_AVAILABLE / SOUND_AVAILABLE, blocks a second instance, initializes sound pools, parses character/shield/weapon data, optionally checks for updates, downloads the sounds/ folder if missing, then loops mainmenu(). The version source of truth is `build/version.txt`, mirrored into `src/includes/version.nvgt` on launch (`sf.py`) and compile (`tools.py`) — see **[[feedback_update_build_version_txt]]**.

## Memory dispatch — where the detail lives

| Topic | Open before you… |
|---|---|
| **[[project_stability_rules]]** | edit any read_/write_ parser, entity array, capability flag, camera key, or info.sif field — the load-bearing invariants (also triggered inline below) |
| NVGT / AngelScript gotchas | write any .nvgt — these cause compile failures (and the game runs from source, so a compile error = won't launch): **[[project_nvgt_key_pressed_oneshot]]** (read a key once, branch inside), **[[project_angelscript_braceless_if]]** (a braceless branch holds only one statement), **[[project_angelscript_reserved_words]]** (don't name a var `out`), **[[project_nvgt_sound_preload_cache]]** (reused filename replays the old clip) |
| **[[project_include_tree]]** | navigate or add to `src/includes/` — the main/ + builder/ architecture map and one-file-per-entity contract |
| **[[project_map_format]]** | touch the on-disk map format, map modes, quoted fields, single/ranged forms, or spanning-entity min/max y |
| **[[project_game_data_layout]]** | edit `sf/data/` — authored maps, keyboard.ini, macro packs, and the characters/shields/weapons/NPCs info.sif contract |
| **[[project_sound_assets_layout]]** | work in `sf/sounds/` — decompiled vs compiled packs, main/ vs builder/ split, glob clip discovery |
| **[[project_audio_model]]** | add a sound_pool or handle any sound you pause/resume/reposition — the HRTF model and the looping/"locked slot" invariant |
| **[[project_script_vs_engine]]** | chase a bug or perf issue, or consider a C++ change — investigate-script-first, plus the non-stock nvgt engine changes list |
| **[[project_build_pipeline]]** | change the version or run a release — version source-of-truth + build/tools.py pipeline |
| **[[project_repo_hygiene]]** | wonder what's gitignored or why CRLF is enforced |
| **[[project_deferred_concerns]]** | before "fixing" a shape-of-the-code smell — the known non-bugs to leave alone |
| **[[project_arcade_arena_revival]]** | work on the arcade arena (arena.nvgt) |

## Stability rules — read first, break never (triggers)

These are the invariants that, if violated, silently break old maps, parsers, or the runtime. Each line is a trigger; the full explanation is in **[[project_stability_rules]]** — read the matching entry there before the edit.

- **read_*/write_* signatures need care** — `map_parser.nvgt`'s `sd.length()` gates which read runs; back-compat for old maps is per-entity, changing a signature can silently drop old lines.
- **mapmode is creation-locked** — never mutate mid-map; parser `sd.length()` checks are multi-valued (encode 2d / 3d z-fields / topdown-3d min-max-y). Preserve every length case.
- **CRLF line endings are enforced** on `*.sif/.nvgt/.py/.txt/.bat/.ps1/.md/.ini` — generate new files with CRLF; don't run a normalizer ([[feedback_no_crlf_normalization]]).
- **Coordinates are double** — don't introduce new int coords.
- **Capability flags gate input as a set** — `pause_game()`/`resume_game()` flip them together; don't toggle individually.
- **3d wall/platform tiles spawn per-z** — loop `minz..maxz`, push each spawn id into the parent's `platform_ids` array (see `wall.nvgt`).
- **Builder multi-input flows use the audio form** — `form.create_*`/`monitor`/`is_pressed`; don't roll your own input loop.
- **Entity arrays use sentinel-null removal, not `remove_at`** — `@<entity>s[i] = null;` + guard every loop/deref; only `destroy_all_*()` may `resize(0)`.
- **Camera-mode key collisions** — any handler sharing a physical key with a `camera_*` action must add `and key_up(KEY_G) and !camdext` (pattern at `game_handlers.nvgt:1373`).
- **info.sif field names use spaces, not underscores** (`weapon type`, `flee time`); underscores only in identifier *values* (folder/tile/item names).

## Working style (triggers)

- **Confirm before implementing.** The dev's default is to describe an idea first, then say "go ahead." Treat a design proposal as a question to answer with a plan, not a task to start; don't fan out into adjacent files unprompted. Exceptions and full rule: **[[feedback_confirm_before_implementing]]**.
- **End file-editing turns with an explicit "Files changed:" list.** **[[feedback_list_modified_files]]**.
- **New commands / builder entities go in their true alphabetical slot**, not appended. **[[feedback_alphabetize_commands]]**, **[[feedback_alphabetize_builder_entities]]**.
- **Presets/type-abstractions need a real driving need** before you propose them. **[[feedback_presets_need_driving_need]]**.
- **Keep this file under 40,000 characters** — move detail to memory, don't expand inline. **[[feedback_claudemd_length]]**.

## Player-facing docs (sf/docks/)

- **sf/docks/main/** — `changelog.txt` (source of truth for what shipped — trust over readme/todo; reverse-chronological, `New in X.Y.` headers), `readme.txt`, `todo list.txt`, `credits.txt`. Opened by `docksmenu()`/`dockread()` in src/sf.nvgt. The readme's "Customizing audio" section is the authoritative per-entity clip-name catalogue.
- **sf/docks/builder/** — per-feature `.txt` reference topics served by `helpread()`; the `hp`/`help` command scans `docks/builder/*.txt` at runtime, so new topics auto-appear (no menu wiring).

Rules for writing/editing these: **[[feedback_changelog_rules]]**, **[[feedback_tp_prose]]**, **[[feedback_readme_todo_quirks]]**.

Note: `CLAUDE.md` is committed (not gitignored).
