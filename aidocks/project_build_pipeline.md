---
name: project_build_pipeline
description: Version source-of-truth (build/version.txt, mirrored into version.nvgt on launch and compile) and the build/tools.py compile → package → release → website pipeline, with per-game and host-wide config locations.
metadata:
  type: project
---

`build/version.txt` is the **single source of truth** for the version. It's mirrored into `src/includes/version.nvgt` (`string version = "X.Y"`, included from includes.nvgt before the glob-includes) automatically: `sf/sf.py`'s `sync_version()` rewrites version.nvgt from version.txt before each launch, and `build/tools.py`'s `sync_version_file()` does the same before `nvgt -c` so a compiled release carries the right version (a compiled build has no `build/version.txt` beside it to read at runtime). `tools.py`'s `get_version()` reads version.txt for release naming/tagging/website. **Don't hand-edit version.nvgt — it's a generated mirror** (see [[feedback_update_build_version_txt]]). Main-menu "change game version" overrides are transient (reset on next launch).

`build/tools.bat` launches `build/tools.py` (Python 3.12), a menu-driven tool covering commit ops (commit, undo, push, history) and release ops. Pipeline:

- **compile** — `nvgt -c -Q sf.nvgt` from `src/`, then copy `data,docks,lib` from `sf/` into the bundle; `sounds/` is downloaded on first run, never bundled.
- **package** — 7-Zip portable, password-protected, into `releases/`.
- **release** — force-tag `V<version>0` with trailing zero, `gh release create`.
- **website** — regex-update site HTML, commit + push.

Per-game settings in `build/tools.ini`; host-wide tool paths (nvgt, 7-Zip, gh) in `~/.game_tools/tools.ini`. No installer ships — only the 7z portable archive.

Related: [[project_path_conventions]] (the cwd=sf/ trick behind the version.txt sync), [[project_engine_pinned_nvgt2]].
