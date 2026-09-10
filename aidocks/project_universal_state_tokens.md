---
name: project_universal_state_tokens
description: The universal character/position placeholder tokens (%health%, %x%, etc.) and where they resolve in the command pipeline
metadata:
  type: project
---

SimpleFighter has THREE token layers in the command pipeline, resolved at different points (14.8):

1. **`random(low,high)`** — universal, resolved by the string-to-number routine (`stn`) for any numeric field anywhere, plus `expand_random_tokens` for text contexts like `/speak`. See the random() paragraph in commands.txt / maps.txt.
2. **Universal state/position tokens** — `expand_state_tokens(cmd)` in `src/includes/main/functions/mapfuncts.nvgt` (right after `expand_random_tokens`). Called once in `comparse()` (`command_parser.nvgt`) right after `string command = sd[1];`, before the args split. 13 tokens: `%health% %maxhealth% %healthpc% %stam% %maxstam% %stampc% %level% %xp% %points% %lives% %kills% %x% %y% %z%`. Percentages use `round(.../...*100, 2)` (2 decimals, matching the stats screen). `%lives%` maps to the `lifecard` global; `%stam%`/`%maxstam%` map to `stamina`/`maxstamina`. Fast-path returns early if the command has no `%`. Replacements are ordered longest-first so none clobbers another.
3. **Element-specific tokens** — resolved by the element BEFORE `comstack`: map_timer time tokens (`%seconds%` etc.) via `expand_time_tokens`; input tokens (`%answer%`/`%choice%`/`%index%`/`%attempt%`/`%attempts%`) via `expand_input_tokens`. These only fill in inside their own element's command.

**Why comparse is the right choke point:** every command funnels through `comparse` (console directly; macros/switches/sensors/inputs/timer via `comstack` → `process_pending_commands` → `comparse` per step). Because a stack like `setx 50; speak %x%` is split and re-dispatched one step at a time, `%x%` in a later step reads the value AFTER an earlier step changed it — async-safe by construction, no special-casing. State tokens even work inside timer/input commands for free, since those are already expanded (their own tokens) before reaching comparse.

**To add a new universal state token:** add one `string_replace` line in `expand_state_tokens` (mind the longest-first ordering), then document it in the commands.txt token section and the maps.txt universal-token note. See [[project_feature_ideas]] for the element-specific input-token design and [[project_map_timer_plan]] for the time tokens.
