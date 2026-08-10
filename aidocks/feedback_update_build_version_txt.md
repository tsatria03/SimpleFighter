---
name: feedback_update_build_version_txt
description: build/version.txt is the single source of truth for the version — to bump, edit ONLY version.txt (alongside the changelog block). It's mirrored into src/includes/version.nvgt automatically on launch (sf.py) and on compile (tools.py); never hand-edit version.nvgt.
metadata:
  type: feedback
---

**`build/version.txt` is the single source of truth for the game version.** To bump the version you edit **only** `build/version.txt` to the new `X.Y` (in the same change that opens the `New in X.Y.` changelog block). It gets mirrored **into** `src/includes/version.nvgt` (`string version = "X.Y";`) automatically:

- **On launch** — `sf/sf.py`'s `sync_version()` reads `build/version.txt` and rewrites `version.nvgt` (CRLF) before starting the game, so the next launch runs as whatever `version.txt` says.
- **On compile** — `build/tools.py`'s `sync_version_file(version)` does the same before `nvgt -c`, so a compiled release carries the right version (a compiled build has no `build/version.txt` beside it to read at runtime).

**Why:** this replaced the old reversed flow (where `version.nvgt` was the source and launch wrote it out to `version.txt`). Direction now: `version.txt → version.nvgt`, matching the sibling CaveDefender project. Editing `version.nvgt` by hand is pointless — the next launch or compile overwrites it from `version.txt`.

**How to apply:**
- Bumping a version is a **two-file** edit that lands together: `build/version.txt` (the value) and the `New in X.Y.` block in `sf/docks/main/changelog.txt`. **Do not touch `version.nvgt`** — it's a generated mirror.
- `version.nvgt` will show as git-modified after you bump `version.txt` and then launch or compile; that's expected — commit the two (or three, with the changelog) together.
- Claude never launches or builds the game ([[feedback_dont_run_or_build_the_game]]), so if a bump needs `version.nvgt` regenerated without a launch/compile, just edit `version.txt` and let the dev's next launch/build propagate it — or note that `version.nvgt` is momentarily stale.

Related: [[feedback_changelog_rules]] (version-bump + changelog rules), [[project_build_pipeline]] (version source-of-truth), [[project_path_conventions]].
