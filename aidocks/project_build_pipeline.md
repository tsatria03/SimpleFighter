---
name: project_build_pipeline
description: Version source-of-truth (src/includes/version.nvgt) and the build/tools.py compile → package → release → website pipeline, with per-game and host-wide config locations.
metadata:
  type: project
---

The version lives in `src/includes/version.nvgt` as `string version = "X.Y"` — the single source of truth, included from includes.nvgt before the glob-includes. `build/version.txt` is a derived mirror that `build/tools.py` reads. On uncompiled launch `src/sf.nvgt` syncs the constant out to it, opening `../build/version.txt` (cwd is `sf/`, so this resolves to the repo-root file). Main-menu "change game version" overrides are transient (reset on next launch).

`build/tools.bat` launches `build/tools.py` (Python 3.12), a menu-driven tool covering commit ops (commit, undo, push, history) and release ops. Pipeline:

- **compile** — `nvgt -c -Q sf.nvgt` from `src/`, then copy `data,docks,lib` from `sf/` into the bundle; `sounds/` is downloaded on first run, never bundled.
- **package** — 7-Zip portable, password-protected, into `releases/`.
- **release** — force-tag `V<version>0` with trailing zero, `gh release create`.
- **website** — regex-update site HTML, commit + push.

Per-game settings in `build/tools.ini`; host-wide tool paths (nvgt, 7-Zip, gh) in `~/.game_tools/tools.ini`. No installer ships — only the 7z portable archive.

Related: [[project_path_conventions]] (the cwd=sf/ trick behind the version.txt sync), [[project_engine_pinned_nvgt2]].
