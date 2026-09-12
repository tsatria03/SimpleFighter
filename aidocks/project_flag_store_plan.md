---
name: project_flag_store_plan
description: As-built record of numeric map flags (SHIPPED 14.9) — named session-scoped numeric values set by trusted commands (setflag/addflag/subflag/clearflag), read via a universal %flag:name% token, listed by /flags. All 4 sections built.
metadata:
  type: project
---

**STATUS: BUILT — shipped in 14.9. All 4 sections done.** Chosen (post-14.8, during 14.9) as the standalone "memory layer" built FIRST, before the [[project_logic_condition_plan]] element — logic conditions will read flags for free via `%flag:name%`. Built one section at a time, confirm+commit between. **Deviation from plan:** `expand_flag_tokens` lives in the new `flags.nvgt` (not `mapfuncts.nvgt`) to keep the whole subsystem in one file — it's global via glob-include either way, and comparse calls it right after `expand_state_tokens`. Everything else built as designed below.

## What map flags are

Named **numeric** values (default 0), **map-session scoped** — the store clears on every map load/reload, exactly like the map inventory that the planned `%item:name%` token reads. They are the mutable, runtime counterpart to [[project_map_variables_plan]] (which are load-time, immutable constants). Flags cover booleans (0/1), counters, and progress values.

## Settled decisions

- **Value:** a number (double). Whole numbers display without a trailing `.0`.
- **Scope/persistence:** map-session only; `clear_all_flags()` runs on map load (alongside the existing `inv.clear()` reset points — command_parser.nvgt:1141 and the load_map path). No save-file work.
- **Names:** mirror map variables — letters/digits/underscore, must start with a letter, no spaces, case-sensitive. **Reuse `mv_is_letter` / `mv_is_name_char`** (free helpers in `builder/misc/map_variable.nvgt`).
- **Reading — the `%flag:name%` token:** universal, resolved in `comparse` alongside the 13 state tokens ([[project_universal_state_tokens]]). Parameterized, so it's a scan-and-replace (`expand_flag_tokens`) like `random()`, NOT a fixed `string_replace` like the state tokens. An unset/cleared flag reads **0** (never errors, matching state-token behavior). Works in any command or text (`speak you have %flag:coins% coins`) and in logic conditions later, for free.
- **Write commands** — four, all **silent on success** (like the position/map-var commands so switches don't chatter), `"Invalid command syntax. Usage: ..."` on bad name or arg count. Value/amount accepts a plain number, `random(lo,hi)`, OR any token (`%flag:x%`, `%health%`, `%item:name%`) — free because those expand upstream in comparse before the command runs, then the field goes through the normal `stn` path.
  - `setflag <name> <value>` / **stfg** — set outright.
  - `addflag <name> <amount>` / **afg** — add; negative subtracts; **auto-creates from 0** on an unset flag.
  - `subflag <name> <amount>` / **sfg** — subtract; auto-creates from 0.
  - `clearflag <name>` / **cfg** — removes the entry entirely (distinct from `setflag x 0`, which keeps it present at 0); silent no-op if the flag isn't set.
  - **Alias scheme** mirrors the health/life trios (add→`a`, sub→`s`, set→`st`, clear→`c`, + flag cluster `fg`, the way `ht`=health / `lf`=life): afg/sfg/stfg/cfg. All four confirmed unused.
- **Compiled-map gating:** the four write commands are **element-only-trusted** — gate is `((base_command == "setflag" || base_command == "stfg") && (!map_is_compiled || trusted))`, mirroring `spawn`/`despawn` (command_parser.nvgt:689/706). Console-typeable on decompiled maps for testing; on a compiled map only a switch/sensor/input/timer/logic-condition (trusted source) may fire them, so players can't hand-set flags to cheat past flag-gated logic. Reuses the existing `trusted` flag ([[project_trusted_commands_compiled]]).
- **Listing — `/flags` / `fgs`:** a **normal** (works-anywhere, read-only) query. Opens a combat-log-style menu (`flagsmenu()`, modeled on `komlogmenu` in menu.nvgt): intro "Flags", header item `total flags N`, one `name, value` item per set flag, **alphabetical by name**, whole numbers without `.0`. **Empty case self-guarded INSIDE `flagsmenu()`** (speaks "There are no flags on this map." and returns without opening) so it behaves identically from the console AND from a menu zone. Escape speaks "canceled" ([[feedback_menus_say_canceled]]); read-only, selecting an item just closes. Calls `resume_pools()` at the end like `komlogmenu`.
- **Menu zone integration** (`builder/zones/menu_zone.nvgt`): add `"flags"` to `menu_zone_ids` and `"flags - map flags"` to `menu_zone_labels`, placed **after `komlog`** (grouped with the other read-only readouts; the list is grouped, not alphabetical). Add one dispatch line to `run_menu()`: `if(menu_name == "flags") { flagsmenu(); return; }`. `menu_zone_semantic_error` validates against `menu_zone_ids`, so it accepts `"flags"` for FREE — no validator edit.

## No new map-line entity / no Tier 2 entry

Flags are a command+token feature, not a builder element — no on-disk map line, no `build_*`, no `read_/write_`, no `*_semantic_error`. Name validation lives in the write-command handlers ("Invalid command syntax"). Nothing to add to the map-error checker except the free menu_zone acceptance above.

## Build plan — 4 sections

1. **Store + token (foundation).** NEW `src/includes/main/globals/flags.nvgt`: `dictionary map_flags` + `flag_get`(0 if absent)/`flag_set`/`flag_add`/`flag_sub`/`flag_clear`, `flag_names_sorted()`, `clear_all_flags()`, and a name-valid helper (reuse mv_ helpers). Add `expand_flag_tokens(cmd)` to `mapfuncts.nvgt`, wire into `comparse` next to `expand_state_tokens`, reset store on map load. Testable: `speak %flag:x%` → `0`.
2. **Write commands.** The four commands in `command_parser.nvgt` (element-only-trusted gate, name + arg validation) + entries in `command_blocker.nvgt` `allcommands` (alphabetical, full names + aliases). Testable: set/add/sub/clear from console (decompiled) and from a switch.
3. **/flags menu.** `flagsmenu()` in `menu.nvgt` (self-guarding empty), `/flags` normal command + blocker entry, `menu_zone.nvgt` integration. Testable: listing from command and from a `flags` menu zone.
4. **Docs + changelog.** `commands.txt` (5 command entries in alphabetical slots + `%flag:name%` in the token section + compiled-map category note), `maps.txt` universal-token note, NEW `docks/builder/flags.txt` help topic (distinguish runtime flags from load-time [[project_map_variables_plan]]), changelog entry under `New in 14.9.` No version bump. Then update this file to BUILT and add the `%flag:name%` token to [[project_universal_state_tokens]] + note flags exist in [[project_logic_condition_plan]].

## Files touched (summary)

NEW: `src/includes/main/globals/flags.nvgt`, `sf/docks/builder/map_flags.txt`, this plan.
EDIT: `mapfuncts.nvgt` (expand_flag_tokens), `command_parser.nvgt` (comparse wire + 5 commands), `menu.nvgt` (flagsmenu), `menu_zone.nvgt` (list + dispatch), `command_blocker.nvgt` (5 entries), map-load reset site, `commands.txt`, `maps.txt`, `changelog.txt`.
