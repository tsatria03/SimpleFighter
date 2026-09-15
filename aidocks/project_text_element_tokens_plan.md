---
name: project_text_element_tokens_plan
description: Plan (ships 15.0) to make the full universal token set work inside the DISPLAY text of map elements — one expand_text_tokens helper (state + flag + item + seq + random) called live at each element's speak/show site, across 7 elements. Design settled; build in 2 sections, confirm+commit between.
metadata:
  type: project
---

**STATUS: BUILT — shipped in 15.0. Both sections done.** `expand_text_tokens` in mapfuncts.nvgt wired into all 7 display sites; docs updated across the 6 topics + commands.txt token section; one 15.0 changelog entry. Original plan below (kept for the record).

---

**STATUS: design COMPLETE, all decisions settled (2026-09). Ships in 15.0. Not yet built.** Fulfills the reworded todo entry ("Make the universal state tokens, along with the flag, item, sequence, and random tokens, work inside the text that map elements display..."). Build one section at a time, confirm+commit between ([[feedback_confirm_before_implementing]]).

## What it is

The universal tokens (the 23 `%health%`/`%x%`/etc state tokens, plus `%flag:name%`, `%item:name%`, `%seq:name%`, and `random()`) already work in commands (resolved in comparse — [[project_universal_state_tokens]]). This makes the SAME set work inside the author-written DISPLAY text of map elements, so a sign can say "You have %flag:coins% coins and %item:health kit% kits", a dialog can read %health%, etc. Expansion happens LIVE at the moment each element shows its text (not frozen at load), so values reflect the read time and `random()` rerolls per read.

## The mechanism

One helper, **`expand_text_tokens(string s)`**, added to `mapfuncts.nvgt` next to `expand_state_tokens`. It runs the exact chain comparse uses, then random:

```
expand_state_tokens -> expand_flag_tokens -> expand_item_tokens -> expand_seq_tokens -> expand_random_tokens
```

All those are globally visible via the glob-include, so one helper calls them all. It early-returns `s` unchanged when the text contains neither `%` nor `random(`, so token-free text pays no cost.

## The 7 call sites (verified by grep — the complete set of author-text display surfaces)

| Element | File:line | What gets wrapped |
|---|---|---|
| sign | `sign.nvgt:50` | `signs[i].text` |
| text square | `text_square.nvgt:28` | `text_squares[i].text` |
| story zone (dialogs) | `story_zone.nvgt:41, 48` | `story_zones[i].text` (dlgmessage arg) |
| timed text | `timedtext.nvgt:30` | `timedtexts[i].text` |
| blockage | `blockage.nvgt:37` | the `text` local |
| text input | `text_input.nvgt:99` | `title` AND `prompt` args to `vd.input_box` |
| menu input | `menu_input.nvgt:124, 125` | each SHOWN label (first arg of `m.add_item`) AND `m.intro_text` (prompt) |

**Menu-input detail:** expand only the displayed label — `m.add_item(expand_text_tokens(labels[j]), labels[j])` — and keep the `labels[]` array raw, so `picked_label`/`%choice%` handed to the fired command stays the author's original label (no token baked into %choice%).

**Inputs — why they belong:** `title`/`prompt`/labels are text the player READS at open time (same role as a sign). The `%answer%`/`%choice%`/`%index%` tokens are a SEPARATE layer for the command that runs AFTER input, and those keep resolving in comparse as now — do NOT expand the input's submit/cancel/incorrect commands here; leave them to comparse so they stay live at click time. Story-zone `--` page breaks are untouched by the helper, so paged dialogs still page.

## Settled behavior

- **Live, per-read.** Tokens re-expand every time the text is shown; `random()` rerolls each read.
- **Literal `%`** is safe unless it EXACTLY spells a token (e.g. `%health%`) — note this in the help topics.
- **Scope confirmed = full universal set** (state + flag + item + seq + random), for parity with commands (dev's call over state-only).

## Build plan — 2 sections

1. **Helper + wiring.** Add `expand_text_tokens` to mapfuncts.nvgt; wrap all 7 call sites. Fully testable (hand-author a sign with `%health%`).
2. **Docs + changelog.** Update the 7 elements' help topics (signs, story zones, text squares, timed text, blockages, inputs) to mention live tokens + the literal-`%` caveat; add a note to the commands.txt token section that tokens now work in element display text; one `New in 15.0.` changelog entry. Then mark this file BUILT.

## Files

NEW: this plan.
EDIT (§1): `mapfuncts.nvgt`, `sign.nvgt`, `text_square.nvgt`, `story_zone.nvgt`, `timedtext.nvgt`, `blockage.nvgt`, `text_input.nvgt`, `menu_input.nvgt`.
EDIT (§2): the matching `sf/docks/builder/*.txt` topics + `commands.txt` + `changelog.txt`.
