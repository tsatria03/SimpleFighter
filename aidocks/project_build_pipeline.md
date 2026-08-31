---
name: project_build_pipeline
description: Version source-of-truth (build/version.txt, mirrored into version.nvgt on launch and compile) and the build/tools.py compile → package → release → website pipeline, with per-game and host-wide config locations.
metadata:
  type: project
---

`build/version.txt` is the **single source of truth** for the version. It's mirrored into `src/includes/version.nvgt` (`string version = "X.Y"`, included from includes.nvgt before the glob-includes) automatically: `sf/sf.py`'s `sync_version()` rewrites version.nvgt from version.txt before each launch, and `build/tools.py`'s `sync_version_file()` does the same before `nvgt -c` so a compiled release carries the right version (a compiled build has no `build/version.txt` beside it to read at runtime). `tools.py`'s `get_version()` reads version.txt for release naming/tagging/website. **Don't hand-edit version.nvgt — it's a generated mirror** (see [[feedback_update_build_version_txt]]). Main-menu "change game version" overrides are transient (reset on next launch).

`build/tools.bat` launches `build/tools.py` (Python 3.12), a menu-driven tool covering commit ops (commit, undo, push, history) and release ops. Pipeline:

- **compile** — `nvgt -c -Q sf.nvgt` from `src/`, then copy `data,docks,lib` from `sf/` into the bundle; `sounds/` is downloaded on first run, never bundled.
  - **Which engine DLLs get bundled is governed by `build.shared_library_excludes` in `C:\nvgt\config.properties`** (the NVGT install's global config, OUTSIDE the repo — so it doesn't travel to another machine/CI). `nvgt -c` copies every DLL from `C:\nvgt\lib` into the bundle EXCEPT partial-name matches on that list. The dev's list (2026-08): `plist TrueAudioNext GPUUtilities systemd_notify sqlite git2 curl opus bassflac bassmidi unicode Tolk` (`unicode` + `Tolk` added 2026-08-31; use the DLL's EXACT filename casing — the matching looks case-sensitive, matching `TrueAudioNext`/`GPUUtilities` to their DLLs, so `Tolk` not `tolk`). `unicode.dll`: unused, not in `sf/lib`. `Tolk.dll`: the legacy fork replaced Tolk with STATICALLY-LINKED UniversalSpeech for screen-reader speech (`SConstruct` links `UniversalSpeechStatic`, `src/srspeech.cpp` includes `UniversalSpeech.h`, Changelog: "no more Tolk.dll required"; the TTS doc + `nvgt.evb` that still name Tolk are STALE), so Tolk.dll is dead weight — screen-reader output goes through UniversalSpeech → the per-reader clients (`nvdaControllerClient64`, `SAAPI64`, `zdsrapi`). **NOTE the two-source subtlety:** the exclude only stops `nvgt -c` copying from `C:\nvgt\lib`, but `tools.py` ALSO copies the whole curated `sf/lib` on top — so a DLL present in `sf/lib` (like Tolk.dll was) ships regardless of the exclude until it's removed from `sf/lib` too (dev removing `sf/lib/Tolk.dll` by hand). `unicode.dll` needed only the exclude because it was never in `sf/lib`. So if a release is ever missing/carrying an unexpected DLL, check that line. A repo-portable alternative (not chosen) is a project-level `src/sf.properties` with the full excludes string (project config overrides the global one entirely — it's a single string, not a merge).
- **package** — 7-Zip portable, password-protected, into `releases/`.
- **release** — force-tag `V<version>0` with trailing zero, `gh release create`.
- **website** — regex-update site HTML, commit + push.

Per-game settings in `build/tools.ini`; host-wide tool paths (nvgt, 7-Zip, gh) in `~/.game_tools/tools.ini`. No installer ships — only the 7z portable archive.

Related: [[project_path_conventions]] (the cwd=sf/ trick behind the version.txt sync), [[project_engine_pinned_nvgt2]].
