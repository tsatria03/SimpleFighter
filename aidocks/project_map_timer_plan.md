---
name: project_map_timer_plan
description: Settled design + 6-section build plan for the map_timer element (14.7) — a coordless, map-wide countdown whose only output is author commands with time tokens.
metadata:
  type: project
---

**map_timer** — the first coordless element in the game. A single map-wide countdown; reaching any travelpoint (which unloads the map) beats it for free, so "completion = travelpoints" needs no special wiring — the timer only matters on failure to leave in time.

**On-disk (Decision A, positional quoted):** `map_timer "<time cmd>" "<period cmd>" "<count cmd>" <time> <period> <count>` — 3 quoted commands (via extract_quoted + escape_quotes, so they can carry escaped-quote spawns), then 3 bare whole-second numbers. Dispatched by keyword with NO length gate (like switch/text_input); Tier 1 lenok=true.

**Fields:** time = total budget seconds (timer inactive if 0). period = announcement interval seconds (0 disables). count = final-countdown threshold seconds (0 disables). time cmd = fires once at 0 (empty = nothing happens, element is silent by itself). period cmd = fires each period interval (author writes speak with tokens). count cmd = fires each second during countdown (author writes a beep/speak).

**Firing rules:** period fires at each multiple of the interval counting DOWN aligned to remaining (budget 90, period 30 → at 60 and 30 left), not at start or zero. count fires once per second from count→1 (zero belongs to time cmd). Inside the count zone (remaining <= count, inclusive) period PAUSES — count owns it, one clean handoff. Clock FREEZES while the game is paused (existing pause flags).

**Tokens (all 3 commands):** %seconds%/%second%, %minutes%/%minute%, %hours%/%hour% — plural = total in that unit, singular = remainder (clock piece). %hour% == %hours% (hours is the top unit, no bigger unit to leave a remainder). No days. Order-independent replace (closing % delimiter, same as %attempt%/%attempts%).

**Lifecycle:** placement anywhere in main.sif; LAST parsed line wins; one active timer per map. Builder APPENDS a new line (dev's choice) — author removes the stale line themselves. Reset in clearmap().

**Query command:** /maptime (/mt) — both free. Speaks remaining time, or "no timer on this map". Goes in commands.txt + command-blocker allcommands list, alphabetized.

**Builder home:** builder menu, MISC category (alphabetical slot: character blocker, command blocker, MAP TIMER, timed text — in both entry_names[5] and entry_ids[5] at map_menu.nvgt ~521/533). Add "map_timer" to converted_3d (coordless → works all modes). Needs its own buildtype dispatch that SKIPS the selection-marker/coordinate step every other element uses (coordless form).

**6-section build plan (confirm-and-commit each):**
1. Data/lifecycle + read/write + parser dispatch. New file src/includes/builder/misc/map_timer.nvgt (glob-included via `#include"builder/misc/*"`). Singleton globals (not an array), arm_map_timer(), destroy_map_timer() wired into clearmap() (map.nvgt ~122), read_map_timer(sd), write_map_timer(). map_parser dispatch + Tier1 lenok.
2. Runtime tick in game.nvgt (map_timer_loop) + expand_time_tokens(cmd, remaining) in mapfuncts.nvgt.
3. Coordless build_map_timer() form + misc menu wiring + buildtype dispatch.
4. /maptime (/mt) in command_parser.nvgt + docs list entries.
5. Map-error Tier 1 + Tier 2 (map_timer_semantic_error: 3 non-negative whole numbers).
6. Docs: new map_timer.txt help topic, maps.txt entity entry, commands.txt /maptime line, changelog entry. Version stays 14.7.

STATUS: BUILT & shipping in 14.7 — all 6 sections done. Files: src/includes/builder/misc/map_timer.nvgt (state, arm/destroy, read/write, map_timer_loop, build_map_timer, map_timer_remaining, map_timer_time_phrase, map_timer_semantic_error), expand_time_tokens in mapfuncts.nvgt, loop call in game.nvgt, clearmap reset in map.nvgt, parser dispatch+Tier1+Tier2 in map_parser.nvgt, menu wiring in map_menu.nvgt, /maptime in command_parser.nvgt + command_blocker.nvgt, docs (map_timer.txt, maps.txt, commands.txt, changelog.txt). Drop this entry from the backlog once 14.7 releases.

Clock-notation update (14.7): the three duration fields (time/period/count) accept plain seconds OR colon clock form — 1:30 = 90s, 2:5:30 = 7530s, lenient (1:90 = 150s). Applies everywhere (form + hand-authored on-disk). `parse_duration()` (colon→seconds, falls back to stn for plain/random) and `duration_token_error()` (validator) added to map_timer.nvgt; read_map_timer + build form + Tier2 all route through them; write_map_timer now stores the raw duration STRINGS so notation round-trips; build-form number filters switched to whitelist "0123456789:". Related: [[project_command_field_no_nested_quotes]] (escape_quotes in the writer), [[project_map_format]], [[feedback_alphabetize_commands]], [[feedback_alphabetize_builder_entities]].
