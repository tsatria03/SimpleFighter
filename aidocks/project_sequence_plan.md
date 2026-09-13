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
