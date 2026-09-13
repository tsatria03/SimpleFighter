---
name: project_sequence_plan
description: As-built record of the sequence element (SHIPPED 14.9) — a coordless combination-puzzle element fed by /seqstep, matching ordered tokens and firing a command on completion. All 5 sections built.
metadata:
  type: project
---

**STATUS: BUILT — shipped in 14.9. All 5 sections done.** Element in `src/includes/builder/misc/sequence.nvgt` (class + `feed_sequence`/`reset_sequence`/`find_sequence` engine + read/write + `build_sequence` form + `sequence_semantic_error` Tier 2 + `expand_seq_tokens` for `%seq:name%`). Commands `/seqstep` (sqs) / `/seqreset` (sqr) in command_parser (trusted). Event-driven — NO game.nvgt loop. Deviations from plan: Tier 1 mirror + dispatch landed in §1 (stability rule), and `expand_seq_tokens` lives in sequence.nvgt (not mapfuncts) to keep the subsystem together. Everything else as designed below.

**Original STATUS (kept for the record): design COMPLETE, all decisions settled (2026-09).** A combination-puzzle feature adapted to SF from an external reference game's coordless "sequence trigger" (which watches other triggers by ID). SF is ID-less, so the adaptation is **name-based**: the sequence is a coordless element, and ordinary switches FEED it steps by name with a command instead of being watched by ID. Reuses the patterns from [[project_flag_store_plan]] (name-based, session-scoped, parameterized token) and [[project_universal_state_tokens]]. Ships in **14.9** (dev confirmed room for it). Build one section at a time, confirm+commit between ([[feedback_confirm_before_implementing]], [[feedback_stage_commits_before_big_changes]]).

## What it is

A **sequence** is the "enter the combination in order" primitive: a keypad, a Simon-says, step-the-plates-in-order. It's a coordless element (no position, like map_timer / map_variable) holding an ordered list of step tokens; switches feed it one token at a time, and it fires a command when the full order is entered correctly. The external reference game keyed its sequence to other triggers' IDs; SF flips it to name-based feeding since SF has no entity IDs (same reason flags/logic conditions are name-based).

## Settled decisions

- **Name:** `sequence` (friendly == on-disk, one word).
- **Category:** misc, coordless (alongside map_timer, map_variable), alphabetical.
- **Fields:** `name` (letter-led, letters/digits/underscore, flag-style, reuse `mv_is_letter`/`mv_is_name_char`); `steps` (comma-separated tokens, e.g. `7,4,9` or `red,blue,green`); `on complete command`; `on fail command` (optional, "leave blank to skip"); `reset on fail` (checkbox, default ON); `single use` (checkbox, default OFF).
- **Step tokens:** simple space-free words (a space breaks `/seqstep` arg parsing; comma is the list separator). Matched as exact text.
- **Feeding:** a switch fires `/seqstep <name> <token>`. Token == next expected step → advance; was the last step → run **on-complete** command. **Any wrong token** (settled — not the GC "ignore unknown" option) → run **on-fail** command, and if reset-on-fail, restart from step 0.
- **Re-arm:** completing resets to step 0 (repeatable) UNLESS single-use, which then goes dormant.
- **`/seqreset <name>`** clears progress to 0 on demand (for a lever/timer/sensor to scramble the puzzle beyond the automatic resets).
- **`%seq:name%` token** (settled — include it): the count of correct steps entered so far, 0 when reset/unset. Universal, parameterized scan-and-replace like `%flag:name%`/`%item:name%` (resolved in comparse); reads to the value it needs. Add to [[project_universal_state_tokens]] (would be the 24th... actually parameterized, listed separately like flag/item).
- **Session-scoped:** progress starts at 0 each map load (the definition reloads from the map line; the runtime progress is fresh).
- **Trusted:** `/seqstep`, `/seqreset`, and the complete/fail commands run trusted (element-firable on compiled maps, console-blocked there), like the flag commands ([[project_trusted_commands_compiled]]). Gate: `((base_command=="sqs"||base_command=="seqstep") && (!map_is_compiled || trusted))`.
- **Aliases:** `/seqstep` → **sqs**, `/seqreset` → **sqr** (both confirmed free; "sst" was taken by substam).
- **On-disk:** `sequence <name> "<steps>" "<complete cmd>" "<fail cmd>" <reset_on_fail> <single_use>` — coordless; name is a bare token, steps + the two commands are quoted (escape_quotes), then two bare bools.

## Model note (element vs store)

The sequence is an ELEMENT (spawned instance from the map line, like map_timer), found by name — NOT a bare dictionary store like flags. Each `sequence` line spawns an instance holding its definition + a `current_step` counter. `/seqstep name token` looks up the instance by name and advances it. Multiple sequences = multiple named instances. Reset-on-load happens naturally (instances re-spawn from lines with current_step 0).

## Build plan — 5 sections

1. **Element + engine + `%seq:name%` token.** The `sequence` class (name, steps array, complete/fail cmds, reset_on_fail, single_use, current_step) + live array; `read_sequence`/`write_sequence` (coordless, quoted steps/cmds + trailing bools); a `feed_sequence(name, token)` engine (advance / on last → complete via comstack(trusted) / wrong → fail + reset) and `reset_sequence(name)`; `find_sequence(name)`; `destroy_all_sequences()` + map.nvgt cleanup; and `expand_seq_tokens` for `%seq:name%` wired into comparse after the flag/item tokens. (No build form / commands yet.)
2. **Commands.** `/seqstep` (sqs) + `/seqreset` (sqr) in command_parser (trusted gate), + command_blocker `allcommands` entries (alphabetical). Testable end-to-end via hand-authored `sequence` line + switches.
3. **Build form + menu registration.** `build_sequence` (coordless form: name, steps, complete cmd, fail cmd, reset-on-fail checkbox, single-use checkbox) + `buildobj` dispatch + misc category entry_names/entry_ids/converted_3d in map_menu.nvgt (alphabetical). Friendly==on-disk `sequence`, so no normalize_buildtype entry.
4. **Map errors.** Tier 1 mirror in `entity_line_error` (`lenok=true`); Tier 2 `sequence_semantic_error` (name valid identifier, steps field non-empty, the two trailing bools valid; commands are free text).
5. **Docs + changelog.** New `sequences.txt` topic (example-heavy: keypad, plate-order puzzle, combined with flags/logic to open a door; explain feeding, wrong-resets, re-arm, single-use, %seq:name%, /seqreset); commands.txt entries for seqstep/seqreset + `%seq:name%` in the token doc; maps.txt element-list entry; changelog under `New in 14.9.` (fits — dev confirmed ~2 slots left). Then mark this file BUILT, add `%seq:name%` to [[project_universal_state_tokens]].

## Files (summary)

NEW: `src/includes/builder/misc/sequence.nvgt`, `sf/docks/builder/sequences.txt`, this plan.
EDIT: `command_parser.nvgt` (comparse token wire + 2 commands), `mapfuncts.nvgt` OR sequence.nvgt (expand_seq_tokens — put in sequence.nvgt to keep the subsystem together, like flags), `command_blocker.nvgt`, `map_menu.nvgt`, `map_parser.nvgt` (dispatch + Tier1 mirror + Tier2 dispatch), `map.nvgt` (destroy_all wire), `game.nvgt` (no per-frame loop needed — sequences are event-driven via /seqstep, so NO game.nvgt loop, unlike logic conditions), `commands.txt`, `maps.txt`, `changelog.txt`.

---

## ADDENDUM: sequence MODES (custom / ascending / descending) — 14.9, NOT built yet

A follow-up enhancement to the shipped sequence element, so authors don't have to type a long explicit combination for a number puzzle: a sequence gains a **mode**, and the ascending/descending modes let the player SORT numbers instead of matching an authored list. Inspired by the number-sorting game Ascending Match (co-created by the dev + KamiKitsune — keep the name out of committed files per [[feedback_dont_name_others_games]]); this is NOT a port of that whole game (no subsystem, no swap UI), just a matching mode on the existing element.

**Settled decisions:**
- New build-form list, caption **"mode"** (bare options, descriptions in the topic): **custom**, **ascending**, **descending**.
- **custom** = the current behavior: match the exact `steps` tokens in the exact order typed (the keypad/code case). Renamed from the implicit-only mode; it's the default. **The build form always writes a mode (required, defaults to custom)** — the on-disk back-compat below is ONLY for old hand-authored lines that predate the mode token.
- **ascending / descending** = no step list; instead a **count** (how many numbers). Each fed number must be numerically **greater (ascending)** or **less (descending)** than the last one fed; complete when `count` numbers have been accepted in order. A non-numeric or wrong-direction token is a wrong entry.
- **Form field swap by mode** (sensor-style rebuild): custom shows the **steps** box; ascending/descending show a **count** box.
- **`reset on fail`** (existing field) already governs a wrong entry: on = restart the whole sort, off = reject that entry and keep going. No new field.
- **Randomness is external, unchanged:** for a different puzzle each play, switches feed **frozen-random map variables** (`mapvar n1 random(1,44)` → `$n1`); a bare `random()` on a switch would reroll each press, so map variables are required for the random flavor (no new code — [[project_map_variables_plan]] already does the freezing). A fixed sort (same each play) needs no map variables.
- **`%seq:name%`** still reports correct-count-so-far in all modes.
- **On-disk (mode REQUIRED, no back-compat — dev's call):** a bare **mode** token after the name — `sequence <name> <mode> "<steps-or-count>" "<complete>" "<fail>" <rof> <su>`. The first quoted field is the comma-list in custom mode or the count number in ascending/descending. `read_sequence` requires `sd[2]` to be custom/ascending/descending; a line without a valid mode does NOT load. (The sequence element only shipped in 14.9, so requiring the mode was accepted over back-compat for old mode-less lines.)
- **Class additions:** `mode` (string), `count` (uint, for asc/desc), `last_value` (double, the last number fed for the comparison). custom keeps using `steps[]` + `current_step`; asc/desc use `count` + `current_step` + `last_value`.
- **Version:** ships in **14.9** as a SEPARATE changelog entry (NOT merged into the existing sequence entry) — dev's call.

**Build plan — 3 sections:**
1. **Engine + Tier 2 (DONE).** Added `mode`/`count`/`last_value` to the class; branched `feed_sequence` for ascending/descending (numeric compare via stn, `logic_is_number` reject for non-numbers, direction check, complete at count); made `read_sequence` REQUIRE the mode token (no back-compat); updated `write_sequence` (mode + steps_or_count). **Tier 2 was pulled into §1** (extended `sequence_semantic_error`: mode required + in {custom,ascending,descending}; custom → steps non-empty; asc/desc → count a positive number) so the reader and validator stay in sync — otherwise a new sort line false-flags in the map-error box.
2. **Build form.** The mode list (custom/ascending/descending) + steps/count field swap (rebuild-on-mode-change like the sensor form); write the chosen mode + the steps-or-count field.
3. **Docs.** Update the sequences.txt topic (explain the three modes + a random-sort example with map variables) and the maps.txt/commands.txt notes; add the SEPARATE 14.9 changelog entry.
