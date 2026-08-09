---
name: project_path_conventions
description: "SimpleFighter's src/ (code) + sf/ (assets+launcher) + build/ + releases/ split, the cwd trick, the sf.py launcher, and where everything lives after the restructure"
metadata: 
  node_type: memory
  type: project
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

**Restructure: SimpleFighter now SEPARATES code from runtime assets into top-level folders at the repo root** (the same split CaveDefender got — see that repo's path-conventions; here it's single-side, not client/server).

- **`src/`** = code only. Entry `src/sf.nvgt`, plus `src/includes/` (`includes.nvgt`, `version.nvgt`, `builder/`, `main/`). No assets here.
- **`sf/`** = runtime assets + launcher. `sf/sf.py` (launcher), `sf/data/`, `sf/docks/`, `sf/sounds/`, `sf/lib/` (the engine DLLs/exes — was the old repo-root `lib/`).
- **`build/`** = the build/release pipeline (`tools.py` via `tools.bat`). `build/tools.ini` (per-game), `~/.game_tools/tools.ini` (host-wide tool paths), `build/version.txt` (derived).
- **`releases/`** = compiled build outputs (gitignored).

**The cwd trick (how code and assets connect):** `sf/sf.py` runs `../src/sf.nvgt` through NVGT but sets **cwd = `sf/`**, so every cwd-relative path in the code (`lib/...`, `sounds/...`, `data/...`, `docks/...`, `build/version.txt`) resolves under `sf/`. The include line `#include"includes/includes.nvgt"` in `sf.nvgt` resolves relative to the script → `src/includes/`. **No in-code path changed in the move** — only the launcher cwd (runtime) and `build/tools.py` (build) know about the split. So: a path naming a *file on disk* lives under `src/` or `sf/`; a bare `data/...`/`sounds/...`/`docks/...` string *in the code* is cwd-relative against `sf/`.

**Launcher:** `sf/sf.py` — `subprocess.Popen` + `CREATE_NO_WINDOW`, exits immediately (console only flashes, no persistent cmd window); the game opens its own NVGT window. Hard-codes the engine as `C:\nvgt2\nvgtw.exe` (the windowed/no-console variant; CaveDefender's launchers use `nvgt.exe`). See [[project_engine_pinned_nvgt2]].

**Build pipeline (`build/tools.py`, already updated for the split):** `SRC_DIR = repo/src`, `ASSETS_DIR = repo/sf`. Compile runs `nvgt -c -Q sf.nvgt` from `src/` (bundle lands in `src/sf/`), then copies `data, docks, lib` from `sf/` beside the exe (cwd-relative). **`sounds/` is NOT bundled** — the ~2.3 GB folder is downloaded on first run by `downloadsounds()`. Reads the version from `build/version.txt`.

**Path remap from the pre-restructure layout:** `sf.nvgt`→`src/sf.nvgt`; `includes/…`→`src/includes/…`; `includes/version.nvgt`→`src/includes/version.nvgt`; `data/…`→`sf/data/…`; `docks/…`→`sf/docks/…`; `sounds/…`→`sf/sounds/…`; `lib/`→`sf/lib/`.

**Version sync:** `src/sf.nvgt`'s uncompiled version-sync opens `../build/version.txt` (cwd is `sf/`, so it resolves to the repo-root `build/version.txt` that `tools.py` reads). This was briefly broken right after the restructure — it opened `build/version.txt` cwd-relative, targeting the nonexistent `sf/build/version.txt` — and was fixed by adding the `../`.
