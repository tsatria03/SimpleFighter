---
name: project_timer_commands_plan
description: Sketch (not built) for slash commands that adjust a running map timer at runtime — addtime / stoptime / settime / starttime — the compiled-safe alternative to /spawn map_timer.
metadata:
  type: project
---

**Problem this solves.** The map_timer ([[project_map_timer_plan]]) starts at map load. An input/switch can already START or EXTEND a timer by /spawn map_timer, but /spawn (and /build) only work on DECOMPILED maps, so dynamic time control is impossible in a compiled, shipped map. These would be ordinary commands (not builder verbs), so they work compiled or not — letting players gain, lose, or clear time mid-run in a shipped map.

**Sketched commands (all operate on the single active map timer):**
- **addtime <seconds>** — add seconds to the remaining time; a negative value subtracts (clamp remaining at 0, which would then trigger the time command on the next tick). Implementation: adjust the timer's total (remaining = total − elapsed), so `map_timer_total += seconds`. Enables "gain 30 seconds" / "penalty" pickups. No-op (silent) if no active timer.
- **stoptime** — cancel the active timer immediately WITHOUT firing its time command (the "disarm the bomb" verb). Sets active=false, done=true. This is the missing clean cancel; today you can only end a timer by leaving the map or overriding it with a fresh spawn.
- **settime <seconds>** — set the remaining time to an exact value (reset elapsed so remaining == seconds). For checkpoints that hand out a fixed new budget.
- **starttime "<time cmd>" "<period cmd>" "<count cmd>" <time> <period> <count>** — the compiled-safe cousin of /spawn map_timer: arm/replace the timer from a command that also works in shipped maps. (Optional — overlaps with settime+addtime; include only if starting a brand-new timer with commands mid-map is wanted in compiled maps.)

**Design notes / open questions:**
- All are silent by default (consistent with the timer being silent — the author's own commands do the talking). Possibly a brief spoken confirmation, TBD.
- Boundary tracking: after addtime/settime, remaining jumps; the loop's `map_timer_last_sec` guard just resumes from the new value — events for skipped seconds don't retro-fire, which is fine. Reset last_sec so the next boundary is clean.
- **Aliases must be checked for collisions** — `/st` is TAKEN (stats), so stoptime needs another (e.g. /stt). Check /at (addtime), /set/settime, /start before use.
- Each new command needs: command_parser branch, command-blocker allcommands entry (alphabetized), commands.txt line (alphabetized), and a note in map_timer.txt.
- Guard on there being an active timer; decide whether these should also work while the timer is done/expired.

STATUS: sketch only, NOT built and not scheduled — recorded at the dev's request as a future option if shipped maps ever need mid-run time control. Related: [[project_map_timer_plan]], [[feedback_alphabetize_commands]].
