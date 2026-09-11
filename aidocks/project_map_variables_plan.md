---
name: project_map_variables_plan
description: Settled design + section build plan for the map variables builder element (load-time named-number substitution); NOT yet built
metadata:
  type: project
---

**STATUS: DESIGN SETTLED, not built.** A new builder element that brings named, load-time numeric constants to maps. Inspired by an external reference game's "map variables" (do NOT name it in committed files per [[feedback_dont_name_others_games]]), but re-scoped for SimpleFighter's architecture. Queued as the small, self-contained feature chosen INSTEAD of the big [[project_logic_condition_plan]] (which stays deferred as too large). Distinct from a future runtime "flags" store (that one is command-set + mutable mid-play and is really the first half of logic conditions; map variables are static/load-time and stand alone).

## Naming (SETTLED): friendly `map_variable` -> on-disk `mapvar`
Two names, wired through `normalize_buildtype`, EXACTLY like the abbreviated elements (moving_platform->mplatform, security_camera->camera, aircraft_beacon->airbeacon):
- **Friendly name** (builder menu label, what you type in `/build`): `map_variable`.
- **On-disk written keyword** (the actual map line, the parser dispatch key, the map-error dispatch key): `mapvar`.
- `normalize_buildtype` maps `map_variable` -> `mapvar`; `/build` accepts either form (friendly or on-disk) like every other element.
- (History: dev first considered `map_variable` everywhere for consistency with map_timer, then after seeing the abbreviated-keyword precedent chose the friendly-long / on-disk-short split. The `$name` REFERENCE is unaffected either way — it uses the author's chosen variable name, never the keyword.)

## What it is
A **map variable** is a named number, defined once in the map file, substituted BY REFERENCE into later lines when the map loads. Static: resolved once at load, never changes during play. On-disk line: `mapvar name value` — a COORDLESS, positionless element (same family as the map timer [[project_map_timer_plan]]; no x/y/z, not anywhere in the game world). Reference it elsewhere as `$name`.

## Why (the driving need)
SF already has `random(low,high)` in every numeric field, so "randomize a value" is covered. The ONE thing `random()` can't do is **freeze a single roll and reuse the SAME value across multiple lines** — map variables fix exactly that. Two real uses:
1. Freeze one random roll shared across lines (a sign, a travelpoint, a sound_source all at the same random coordinate).
2. Name a coordinate once, reference it across an object's several lines; move the object by editing one number (DRY coordinates).

## SCOPE (settled): NUMERIC fields only, in spirit
The reference game also substitutes variables into sound FILENAMES (`loop_music$var.ogg`) because its sound folder is FLAT (one dir, ~7000 literal filenames with the variant baked in). **That does NOT port to SF:** SF sounds are deeply nested and glob-selected (`get_map_sound("builder/.../*death*")` — folder path + pattern, never a literal filename), and SF already randomizes clips via glob. So the filename trick is MOOT for SF. Map variables target the numeric fields (coords, ranges, counts, speeds, healths) — the freeze-a-roll and DRY-coords wins.

## Settled decisions
1. **Line-wide substitution.** `$name` is replaced ANYWHERE it appears in a line (not just number fields). Caveat (documented, accepted): a literal `$word` in a quoted text/command field where `word` is a defined variable WILL substitute. Safe cases: `$5` or a bare `$` never match (names must start with a letter). Only `$definedname` in literal text is affected; the author controls both.
2. **Variable-first (define-above-use).** A variable must be defined on a line ABOVE any line that references it — inherent to the top-to-bottom load order. Variables can live ANYWHERE in the file (top/middle/anywhere), scattered as needed, as long as each sits above its uses. The BUILDER FORM APPENDS (normal build convention), so the workflow is: build the variable first, THEN build the elements that use it (they land below it). For precise placement above already-built entities, edit raw map data (`/rawmap`/`/rawdata`) — same as the reference game's own workflow. NOTE: my earlier "top-insertion" idea was REVERSED — append is correct and better matches "variables everywhere". This is about FILE line order, NOT spatial position (the element is positionless).
3. **Undefined variable → WARN.** If `$name` has no definition above it, the text stays literal AND it is flagged in the map errors box (e.g. "Line N: undefined variable 'name'"), riding SF's existing map-error system [[project_map_error_template]]. (User first chose silent, then flipped to warn.)

## Mechanics (settled)
- **Value:** a number or a `random(...)` expression, resolved ONCE via the number parser (`stn`) at the `mapvar` line and FROZEN; every `$name` below reuses that frozen number.
- **Name rules:** starts with a letter; letters/digits/underscore only; case-sensitive; no whitespace or `$`.
- **`$name` boundary rule:** read from `$` until the first char that isn't [A-Za-z0-9_] (punctuation/whitespace/EOL). So `$dest.` -> `dest`, and `$flower` vs `$flower2` stay distinct.
- **Redefinition:** a later `mapvar x ...` updates the table going downward (lines below get the new value) — last-definition-above-a-line wins.
- **Falls out for free:** because substitution runs before a `mapvar` line is parsed, a later variable can reference an earlier one (`mapvar b $a`).
- **Coexistence with the other two substitution layers** [[project_universal_state_tokens]]: `%tokens%` (runtime, comparse) untouched — different syntax (`%` vs `$`) and time (run-time vs load-time); `random()` — a map variable's value can BE a random() (that's how you freeze a roll), and other lines' random() resolve per-field as before. Order at load: `$name` substitution FIRST, then normal parse (per-field random(), quoted-field handling).

## Load hook (confirmed by reading load_map)
`load_map` (map_parser.nvgt ~825-868) walks `lines` top-to-bottom; per line it normalizes whitespace into `normalized_line` (861-867) THEN `string_split`s (868), and header-style lines (`minx`, `mode`, ...) are caught before dispatch (869+). So: (a) a per-load `dictionary` name->frozen-value, reset each load; (b) the `$name` substitution pass runs on `normalized_line` BEFORE the split; (c) a `mapvar` line is caught like the other headers — resolve value, store, `continue` (no entity, never reaches dispatch_entity_line). No `read_` function needed. Works on compiled maps too (pure load-time text resolution). SHARED HELPER: the table-build + per-line substitute logic must be reusable by BOTH the loader AND the map-error scanner (see below), or the scanner will false-positive on every `$var` in a numeric field.

## Authoring verbs
- **Builder form + `/build map_variable ...`** (friendly) or `/build mapvar ...` (on-disk): decompiled-only (edits main.sif), appends.
- **`/spawn`**: MEANINGLESS (substitution already happened at load; a runtime spawn does nothing) — effectively unsupported / no-op.
- **`/unbuild map_variable`**: works for free (generic line-delete + reload). Unbuilding a variable in use makes its refs undefined -> map-error warnings (expected).
- **`/despawn`**: N/A (no runtime object; dispatch has no `mapvar` case -> "There's no ... to remove."), same as templates.

## BUILD SECTIONS (one at a time, dev tests+commits between, docs last)
1. **[DONE — dev-confirmed: sign at `$spot` lands correctly; only the expected §3-pending false map error shows]** **Load-time substitution engine + `mapvar` consumption.** New file `src/includes/builder/misc/map_variable.nvgt` holds the shared engine: `substitute_map_variables(line, vars@)` (line-wide `$name` replace, boundary rule, unknown left literal, fast-path when no `$`), the `mv_is_letter`/`mv_is_name_char` char helpers, and `freeze_map_variable_value(raw)` (= `expand_random_tokens`, which rolls random() once to a clean integer string and leaves plain numbers as-is). load_map got: a per-load `dictionary map_vars;` before the line loop, a `substitute_map_variables(normalized_line, map_vars)` call between the whitespace-trim and the `string_split`, and a `mapvar` branch in the header chain (`else if(sd[0]=="mapvar" && sd.length()>=3) map_vars.set(sd[1], freeze_map_variable_value(sd[2]));`) that stores+freezes and never dispatches. Per-load variable dictionary in load_map; the `$name` boundary parser + line-wide substitute pass on normalized_line before split; `mapvar` line detection + value resolution (stn, freezing random()) + storage, consumed without dispatch; variable-referencing-variable falls out. Extract the substitute logic as a SHARED helper (reused by §3). Hand-author test: a raw map with `mapvar spot 30` then `sign $spot 0 "..."` loads with spot filled in; a `random(...)` value stays frozen across a reload's multiple refs.
2. **Builder form + menu wiring.** Coordless two-field form (name, value) in the MISC build category under the friendly label **map_variable**, alphabetized [[feedback_alphabetize_builder_entities]]; add the `map_variable`->`mapvar` mapping to `normalize_buildtype`; form-level validation (name format, value non-empty); `write_mapvar` appends the `mapvar` line. No `read_` function (loader consumes it). Test: build a variable via the form, then build an element referencing it.
3. **Map error checking.** Tier 1: register `mapvar` known/lenok. Tier 2: `mapvar_semantic_error` — name format + value numeric-or-random(). Undefined-variable WARNING: the error scanner must build the variable table AND substitute (via the §1 shared helper) BEFORE running each line's semantic check (else every `$var` in a coord field false-flags "not a number"); then any `$name` still unresolved is reported as "undefined variable 'name'". Test via /maperrors.
4. **Docs.** New `sf/docks/builder/map_variables.txt` help topic; add to the maps.txt element list; changelog entry — the 14.8 block has 9 entries (the "New in 14.8." line is a header, not an entry), so ONE slot remains under the 10-cap and this fits in 14.8 with no version bump [[feedback_changelog_rules]] [[feedback_update_build_version_txt]].

## Open at build time (small)
- Exact misc-menu alphabetical slot and the help-topic prose.
- Whether the undefined-variable warning also fires at load (Tier 1 auto-box) or only on /maperrors — follow whatever the Tier 1 system already does.
- Version/changelog placement: 14.8 has 9 entries, one slot free, so the entry lands in 14.8.
