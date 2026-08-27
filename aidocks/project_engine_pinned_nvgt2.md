---
name: project_engine_pinned_nvgt2
description: "SimpleFighter runs on the pinned legacy NVGT fork at C:\\nvgt (BASS); the newer C:\\nvgt2 (miniaudio) is only for testing others' games — don't suggest upgrading"
metadata: 
  node_type: memory
  type: project
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

SimpleFighter (and all of tsatria03's games) target a **pinned legacy NVGT fork** installed at **`C:\nvgt`**. The launcher hard-codes it (`sf/sf.py` runs `C:\nvgt\nvgt.exe` — the console build, windowless via `CREATE_NO_WINDOW`, so NVGT's compile output can be captured to `sf/errors.txt`; switched from `nvgtw.exe` for exactly that reason); `build/tools.py` reads the engine path from `~/.game_tools/tools.ini`, pointed at the same `nvgt` build.

A **newer stock NVGT is also installed at `C:\nvgt2`** — the dev put it there to test someone else's game. It uses **miniaudio**; the fork stays on **BASS**, and the game's `sound_pool`/HRTF code is written against the BASS-backed sound object. The new install is NOT for this project.

**Do not suggest upgrading to current/upstream NVGT, and don't treat upstream NVGT docs/source as authoritative here.** The fork (the Legacy-NVGT C++ repo at `C:\Users\tonys\OneDrive\Documents\github\tsatria03\misc\Legacy-NVGT`) diverges incompatibly — different audio backend, plus tsatria03's own engine additions and the non-stock changes this game depends on (e.g. script-configurable `sound_pitch_lower_limit`/`sound_pitch_upper_limit`). Engine changes require a `scons` rebuild of the `nvgt` fork. See [[project_path_conventions]].
