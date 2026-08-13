---
name: feedback_dont_run_or_build_the_game
description: Never launch or compile the game yourself — don't run sf/sf.py, the build/ tooling (tools.py / tools.bat), or src/sf.nvgt. Make the edits and stop; the dev runs and verifies builds. Read-only inspection is still fine.
metadata:
  type: feedback
---

Do NOT launch or build the game yourself. Specifically, never run:

- `sf/sf.py` — the launcher (runs `src/sf.nvgt` under `C:\nvgt2\nvgt.exe`).
- anything under `build/` — `build/tools.py` / `build/tools.bat` (compile / package / release pipeline).
- `src/sf.nvgt` directly, or any other `nvgt` / `nvgtw` compile-or-run invocation.

**Why:** the dev runs and verifies the game on their own machine and controls the build/release loop. Launching or compiling from here is unwanted (and would spawn the pinned `C:\nvgt2` runtime — see [[project_engine_pinned_nvgt2]]).

**How to apply:** after editing `.nvgt` or build files, just report the change and the "Files changed" list. It's fine to read code, reason about correctness, and say "this should compile," but never actually run it to check. Read-only inspection commands (git status/log, ls, grep, wc, reading files) are still fine — this rule is only about launching or building the game. If you need the game run to confirm something, ask the dev to do it (they can use the `! <command>` prompt prefix). Relates to [[feedback_dont_flag_indentation]] (you can't rely on a compile pass to catch mistakes) and [[feedback_verify_code_while_fixing]] (so read carefully instead).
