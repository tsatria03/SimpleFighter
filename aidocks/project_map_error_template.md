---
name: project_map_error_template
description: Settled (not-yet-built) template for the authoring-side map-error report — the compiler-style per-line block (line / text / ERROR) shown collected in one dismissable info box across every add/edit/build/spawn/paste path. Permit-but-warn, never block.
metadata:
  type: project
---

**BUILT 2026-08 (ships in 14.4); template + design record kept for reference.** Design for **authoring-side map error checking** — the errors reported when a builder line is *created or changed*, distinct from load-time (a bad line is silently dropped by `map_parser.nvgt`'s `dispatch_entity_line`; see [[project_deferred_concerns]]). Two tiers were agreed:

- **Tier 1 (structural) — build first.** Catch the two whole-line problems: the object keyword is **not recognized**, or it has the **wrong number of values** for the map mode. The signal already exists: `dispatch_entity_line(string[] sd)` (`map_parser.nvgt`) returns `false` when no keyword+length gate matches (a known keyword with a wrong field count falls through to the final `else return false` just like an unknown keyword). A shared validator mirrors those gates **without spawning**. Honest limitation to state up front: platform (and other) length gates in dispatch aren't strictly mode-aware, so a right-length-but-wrong-mode line can slip Tier 1 — that's tightened in Tier 2.
- **Tier 2 (semantic) — later, one builder entity at a time.** Per-object checks: numeric fields are actually numbers, coordinates fall inside the map bounds, referenced tile/npc/sound names exist. This is where a **column** becomes meaningful (pointing at the offending value). Full section-by-section plan: [[project_map_error_tier2_plan]].

**Behavior = PERMIT-BUT-WARN, never block (dev decision).** Every authoring path still writes/pastes the data so the author keeps full control; the validator only *reports* so they fix it themselves. A bad line therefore still won't appear in the world until corrected (the engine can only spawn lines it understands), but it's now *announced* instead of vanishing silently. A clean edit shows no box — just the normal "Map updated."

**Authoring paths that must feed the same collector + box:** `map_menu.nvgt` (addline, editline), `menu_zone.nvgt` (its own addline, editline), `command_parser.nvgt` (`/build …`, `/spawn` — fix its misleading "Unknown object type" message — and both `/rawdata` branches). `remline` needs nothing. `mapfuncts.nvgt`'s `validate_map_data` currently checks only the header (mode + minx/maxx/miny/maxy [+minz/maxz on 3d]) and ignores entity lines, so rawdata paste has the same blind spot and must run the per-line entity pass too.

**Presentation — one collected info box, modeled on the engine compiler's error report.** Collect ALL invalid lines into one read-only, scrollable, dismissable box via **`vd.info_box(title, caption, text)`** (`virtual_dialogs.nvgt:109` — an audio-form dialog with a read-only multiline text box + Close/Cancel, returns bool; NOT the native Windows `InfoBox`). This mirrors the engine's `MessageCallback` / `ShowAngelscriptMessages` (`Legacy-NVGT/src/nvgt_angelscript.cpp:256-294`), which accumulates every message and shows them all in ONE `info_box("Compilation error", …)`, each error itemized with a blank line between. So it's not a box per error — it's one box that **itemizes every individual error**.

The engine's default per-message template (nvgt_angelscript.cpp:284) is `file: %s` / `line: %u (%u)` / `%s: %s` (type is ERROR/WARNING/INFO) + a blank separator line.

**THE MAP-ERROR TEMPLATE (dev-settled field order: line, then text, then error):** drop the compiler's `file:` line (every error is in the one map being edited) and its column-when-absent; keep the lowercase `line:` key and uppercase `ERROR:` type; add a `text:` line showing the exact entered line. Column is shown only **if any** (Tier 1 has none → `line: 8`; a Tier 2 value-level error would show `line: 8 (3)`).

Per-entry block:

```
line: <position in the map> (<column, only if there is one>)
text: <the exact line the author entered>
ERROR: <plain-english reason>
```

Full example box (2d map, three bad platforms; a correct 2d platform is `platform 0 20 0 100 stone 0 100 false false`):

- Title bar: `Map errors`
- Caption / box label: `Map errors` (dev-settled 2026-08 — just the words "Map errors", NOT a count or "fix it from the edit a line menu" sentence; that guidance lives in the docs instead)
- Body:

```
line: 8
text: platform 0 20 0 100 stone 0 100 false
ERROR: this object has the wrong number of values.

line: 13
text: platfrom 0 20 0 100 stone 0 100 false false
ERROR: this is not a recognized object.

line: 15
text: platform 0 20 0 100 stone 0 100 false false 5 up
ERROR: this object has the wrong number of values.
```

Tier 1 reasons are exactly these two plain-English strings — *"this is not a recognized object."* and *"this object has the wrong number of values."* — no field names or internal jargon in the box (players read it; keep it like a help topic, [[feedback_tp_prose]]).

**Re-show command `/maperrors` (alias `/ms`).** Because the box can be dismissed by accident, a command re-shows the most recent report. The collected error text already lives in a variable, so the command just re-runs the same `vd.info_box`. Behavior: re-shows the last map-error report for the map being edited; if there's nothing to show (no errors yet, or the last authoring attempt came back clean) it speaks one sentence (e.g. *"There are no map errors to show."*, [[feedback_one_sentence_game_messages]]). The stored report tracks the **last** authoring attempt — a new add/edit/build/spawn/paste that finds problems replaces it, and a clean attempt clears it, so `/maperrors` never shows stale, already-fixed errors. Gated to map building like the other builder commands and blockable in a command blocker. `/ms` confirmed free 2026-08 (the only `"ms"` in the source is a millisecond slider-unit label in `effect_space.nvgt`, not a command). Slot `maperrors` into its true alphabetical position (between `macset` and `mapinfo`) in both the `allcommands` list (`command_blocker.nvgt`) and `commands.txt` ([[feedback_alphabetize_commands]]).

**Docs (dev-settled 2026-08): append a dedicated section to `maps.txt`, NOT a standalone topic.** Map errors are a cross-cutting authoring behavior, not a placeable entity, so they don't belong in the per-entity help list; the section goes inside the general maps topic where the building workflow is already documented. (Note: help topics are plain `.txt` now — the old `.tp` extension was dropped in 14.3 — so it's `maps.txt`, not `maps.tp`.) Cover, in observable-behavior terms only ([[feedback_tp_prose]], ≤1024 chars/line [[feedback_dock_line_length_1024]]): a bad add/edit/build/paste line is still written but reported in a dismissable box; how to read a block (line / text / error, with the two plain reasons); that a flagged line won't appear until fixed via edit a line; and the `/maperrors` (`/ms`) re-show command.

**On ship (dev wants these done AFTER the whole thing is built, not staged ahead — writing them earlier would make the changelog describe unshipped behavior):** Tier 1 is changelog-worthy because it's player-observable (you now *hear* a bad line instead of losing it silently). Add **two** changelog entries under the open version, reverse-chron (the `/maperrors` command was designed after the reporting, so the command entry sits ABOVE the reporting entry): one for the basic error reporting, one for the `/maperrors` (`/ms`) command. Also add the `/maperrors` line to `commands.txt` in its alphabetical slot (between the `macset` and `mapinfo` entries), per [[feedback_alphabetize_commands]] (which also covers the `allcommands` list in `command_blocker.nvgt`). See [[feedback_changelog_rules]], [[feedback_update_build_version_txt]]. Follow [[feedback_confirm_before_implementing]] (get go-ahead per stage) and [[feedback_stage_commits_before_big_changes]] (Tier 1 commits before the per-entity Tier 2 work begins). Related: [[project_stability_rules]] (the length-gate table + the drift risk of mirroring it), [[project_map_format]], [[project_dialog_conventions]] (dlg/info_box choices).
