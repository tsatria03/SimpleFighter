---
name: list-modified-files
description: Always end a turn that edited files with an explicit list of every file modified
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

After any turn that modifies files, explicitly tell the dev WHICH files were touched, using bare filenames only, so they can review the changes themselves.

**Why:** The dev (a screen reader user) reviews changes by opening the files; a summary that describes edits without naming every touched file makes those changes hard to find. They know the repo layout, so directory paths are noise — bare filenames are easier to read. Requested 2026-06-06 after a multi-file save-system edit; reaffirmed 2026-06-09 (bare names only, no paths).

**How to apply:** End each response that performed edits with a short "Files changed:" list covering every file written, edited, or deleted that turn — including doc files (changelog, help topics, readme) and config (keyboard.ini), not just code. One line per file. Bare filenames only (e.g. savefuncts.nvgt, game_menu.nvgt) — never directory paths, even partial ones; the dev knows where everything lives. Related: [[feedback_confirm_before_implementing]].
