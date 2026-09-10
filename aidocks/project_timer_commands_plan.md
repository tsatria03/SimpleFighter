---
name: project_timer_commands_plan
description: Sketch (not built) for four slash commands that control the RUNNING map timer — addtime / subtime / settime (adjust remaining, keeping its commands) plus stoptime (silent cancel, no time command). What /spawn map_timer can't do.
metadata:
  type: project
---

**Problem this solves.** The map_timer ([[project_map_timer_plan]]) starts at map load. An input/switch can already START or EXTEND a timer by /spawn map_timer, but /spawn (and /build) only work on DECOMPILED maps, so dynamic time control is impossible in a compiled, shipped map. These would be ordinary commands (not builder verbs), so they work compiled or not — letting players gain, lose, or clear time mid-run in a shipped map.

**Scope trimmed (dev decision):** dropped `starttime` (it just duplicates /spawn map_timer — both create/replace a whole timer; place a static map_timer line instead and adjust it) and `stoptime` (dev doesn't want it). The three keepers all ADJUST the running timer's remaining while keeping its existing commands — which /spawn cannot do (spawn wipes and restarts). They cover the shipped-map case: place a static map_timer, then adjust it live from a switch/sensor/input. Amounts accept clock notation (parse_duration).

**Commands (operate on the single active map timer):** on SUCCESS they are silent (consistent with the timer being silent), but when there is NO active timer to act on they SPEAK an error (dev's call) — e.g. "There's no timer on this map." — matching /maptime rather than a silent no-op.
- **addtime <time>** (`/att`) — add to the remaining clock. Time-bonus pickup. Impl: `map_timer_total += parse_duration(arg)`.
- **subtime <time>** (`/sut`) — subtract from the remaining; if it reaches 0 the time command fires. Time penalty. Impl: `map_timer_total -= dur` (or add to elapsed), clamp so remaining≥0.
- **settime <time>** (`/stt`) — set the remaining to an exact value, keeping the timer's commands. Impl: reset elapsed so remaining == dur. Checkpoint that hands out a fresh budget. NOTE: settime 0 (and subtime past zero) EXPIRE the timer WITH the time command firing — that's the failure path, not a silent cancel.
- **stoptime** (`/spt`) — cancel the active timer WITHOUT firing its time command (silent disarm — the "defuse the bomb, no explosion" verb). Sets active=false, done=true. This is the ONLY silent cancel; add/sub/set can only end a timer by expiring it. Added back after the dev saw that expiring always fires the consequence.

Aliases `/att`, `/sut`, `/stt`, `/spt` all verified FREE (no collisions). No percent flag (percent-of-what is unclear for a timer; keep time absolute).

**Design notes / open questions:**
- Silent on success (the author's own commands do the talking), but speak "There's no timer on this map." when none is active — a timer must already be running (built statically or spawned) for these to have anything to act on.
- Boundary tracking: after addtime/settime, remaining jumps; the loop's `map_timer_last_sec` guard just resumes from the new value — events for skipped seconds don't retro-fire, which is fine. Reset last_sec so the next boundary is clean.
- Each new command needs: command_parser branch, command-blocker allcommands entry (alphabetized), commands.txt line (alphabetized), and a note in map_timer.txt.
- Guard on there being an active timer; decide whether these should also work while the timer is done/expired.
- Mirror the health-command idiom the dev likes (add/sub/set), and reuse parse_duration for clock-notation amounts.

STATUS: BUILT & shipping in 14.7. addtime/subtime (map_timer_total +=/-=), settime (reset elapsed + set total + last_sec=-1 + tick.restart), stoptime (active=false, done=true) — four branches in command_parser.nvgt grouped after /maptime; 8 allcommands entries; commands.txt + map_timer.txt "Adjusting the timer" section + changelog. Silent on success, speak "There's no timer on this map." when none. subtime-to-0 / settime-0 expire via the loop (fire time cmd); stoptime is the silent cancel. Reuses parse_duration + duration_token_error (clock notation). starttime stays dropped. Drop this entry from backlog once 14.7 releases. Recorded as a future option for mid-run time control in shipped maps. Related: [[project_map_timer_plan]], [[feedback_alphabetize_commands]].
