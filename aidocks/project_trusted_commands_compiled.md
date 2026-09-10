---
name: project_trusted_commands_compiled
description: The trusted flag that lets builder elements run restricted commands on compiled maps, and the changemap ungating
metadata:
  type: project
---

Shipped in 14.8. Lets certain decompiled-only commands run on a **compiled** map when fired by a builder **element**, while the same command typed in the console or fired by a macro stays blocked — a source-based trust model, not a per-command one.

**The mechanism (a `trusted` flag threaded through the command pipeline):**
- `comstack(string input, bool trusted=false)` and the `pending_command` struct both carry a `bool trusted` (`comfuncts.nvgt`).
- `process_pending_commands` reads `pending_command.trusted` back and passes it to `comparse(string comd="", bool trusted=false)` (`command_parser.nvgt`).
- `comparse`'s own internal `comstack(cmd, trusted)` call (for semicolon stacks) forwards its received value, so a trusted multi-step command stays trusted across the split.
- **Trusted sources pass `true`:** the 7 `comstack` calls in `switch.nvgt` (covers sensors via `spawn_switcher`), `text_input.nvgt` (5), `menu_input.nvgt` (2), `map_timer.nvgt` (3).
- **Untrusted (default `false`):** the interactive console `comparse()`, and `use_command` (macros + helper NPCs). Macros stay untrusted on purpose — a player binding `/spawn` to a macro is the cheat this guards against.

**The gate:** restricted commands changed from `&& !map_is_compiled` to `&& (!map_is_compiled || trusted)`. Applied to the runtime/gameplay set only: `go`, the nine coord commands (`addx`..`setz`), `spawn`, `gozone`, `suicide`. The editing commands (`build`, `newmap`, `delmap`, `rawmap`, `rawdata`, `undomap`, `redomap`, `maperrors`, `menu`) were NOT touched — they read/write the decompiled `main.sif`, which doesn't exist in a compiled `.map`, so they can't function on compiled regardless.

**`changemap` is different — fully ungated** (works typed or element-fired on compiled). Its gate was removed outright, AND its two existence checks were switched from `directory_exists(".../decompiled/"+name)` to `map_exists(name)` (checks both forms), with `bool dest_compiled = map_is_compiled && file_exists(".../compiled/"+name+".map")` passed as `force_compiled` — the travelpoint pattern (`travelpoint.nvgt`), so it prefers the compiled copy when on a compiled map and one exists, else falls back to decompiled. Also fixed a pre-existing bug: it no longer validates destination coords against the SOURCE map's bounds before loading (was rejecting valid targets); it loads first, then `gop` validates against the destination's bounds.

**To add a new element-runnable-on-compiled command:** gate it `&& (!map_is_compiled || trusted)`. To make one work everywhere on compiled, leave it ungated. See [[project_universal_state_tokens]] for the other recent comparse-layer feature, and the "Commands on compiled maps." section of `sf/docks/builder/commands.txt` for the player-facing three-tier explanation.
