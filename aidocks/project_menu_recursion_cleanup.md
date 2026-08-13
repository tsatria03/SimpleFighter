---
name: project_menu_recursion_cleanup
description: Catalog + phased fix plan for the pervasive "menu recursion" anti-pattern — interactive menu/screen functions that call themselves (to loop or refresh) or call a parent/sibling menu to "go back", instead of looping with while/return. Leaves stale frames on the stack that resurface unexpectedly. ~49 sites across ~10 files, grouped by cluster and difficulty.
metadata:
  type: project
---

# Menu recursion cleanup — catalog & plan

## The problem
`mainmenu()` is **single-pass** (handles one selection, dispatches, returns; `main()` re-runs it in a loop). Many menu/screen functions "navigate" by **calling another menu function** (or themselves) instead of returning. Because the callee often returns after one pass, the **caller's frame — with its live `form`/`while(true)` loop — stays paused on the stack**; when navigation later unwinds, that stale frame resumes and re-shows an old menu/form. This is the class of bug the dev hit: open settings → escape → load map → quit → close map menu → **settings form reappeared**.

Confirmed 2026-08. Root cause of the reported bug (settings escape/cancel/save calling `mainmenu()`) is **already fixed** in `menu.nvgt` (986, 1144, 1150 now `return`). This file plans the rest.

## Review notes (verified 2026-08 before starting)
- **Tier 1 A1 is safe:** `main()` runs `while(true){ wait(5); mainmenu(); }` (`sf.nvgt:60-64`), so replacing `mainmenu`'s internal self-calls with `return` correctly falls back to that loop. (Same fact means `downloadsounds`'s internal `mainmenu()` calls are broken — `main()` does `downloadsounds(); return;` at startup, so they'd lead to `main()` exiting.)
- **Tier 2 (D1) and E1 are a restructure, NOT a call→return swap.** `gamemenu` is single-pass (called once from `mainmenu`). Naively turning a child's `gamemenu()` back-call into `return` unwinds PAST `gamemenu` to the main menu, so "back" would skip the game menu. To make "back" return exactly one level, the PARENT menus (`gamemenu`, and the `modemenu`→`arena_target_menu` chain) must become real `while(true)` loops that re-dispatch, with children `return`ing into them. Same for `pausemenu` (confirm it loops before fixing E1). Design each carefully; this is the highest-effort tier after Tier 4.

## Correct patterns (what to convert to)
- **Self-loop → `while(true)`.** A menu that wants to re-show itself should loop internally and `return`/`break` to exit — never call itself. Template: the `*_chooser` funcs use `do_build=true; continue;` to rebuild a form in-loop (e.g. `character_chooser`).
- **Go-back → `return`.** A submenu's "back"/escape/cancel should `return` to its caller; the caller (looped, or re-invoked by `main()`) re-shows the parent. Never call the parent by name.
- **Fatal error in a parser/loader → return a failure signal**, let the caller decide; don't jump to a menu from deep inside a parse.

## Shapes
- **A** self-recursion to loop. **B** self-recursion to refresh a form. **C** call a parent/sibling menu to go back (or a loader jumping to a menu on error).

## VERIFY each site against live code before editing (line numbers are 2026-08 leads, [[feedback_verify_code_while_fixing]]). Several sites ALSO lack a `return` after the recursive call — those are the most dangerous (execution continues after the nested nav unwinds).

---

## STATUS
- **A1 DONE (2026-08).** The five `mainmenu()` self-loops (`menu.nvgt` rdl-cancel/rdl-no/speaker-test/change-version/check-updates) replaced with `return;` — each was the branch's terminating statement, so control falls to `main()`'s `while(true)` loop and re-shows a fresh menu. Verified: no `mainmenu()` calls remain in menu.nvgt (only the def). NEEDS DEV COMPILE+TEST.
- **H1 DONE (2026-08).** `updater.nvgt` all four sites fixed. `get_download_url` originally called `mainmenu()` on cancel + fell through to return the installer URL (a cancelled update downloaded anyway AND stacked a stray main menu — the exact bug the dev hit). Superseded same session: the game is now portable-only (no Inno Setup installer), so the whole installer path was removed — `get_download_url` is now a one-liner returning the portable `.7z` URL (no picker, so no cancel/`""` path), and the post-download menu dropped the `.exe`/"Run Installer" option (always Extract). Cancel point for the update is the "download now?" question. `downloadsounds` (135/149/169) `mainmenu()` go-backs → `return;` (question-no, download-fail, extract-fail): both callers handle it — `menu.nvgt:66` redownload handler falls back to `main()`'s loop, and startup `sf.nvgt:57` (`downloadsounds(); return;`) exits cleanly since the game can't run without sounds (successful extract restarts via `restart("sf.exe")`). Verified: no `mainmenu()` calls remain in updater.nvgt. **DEV TESTED — works.** Committed as `a22f1717`.
- **B1 + C1 DONE (2026-08).** `settingsmenu` wrapped in an outer `while(true)` rebuild loop (build code untouched, just re-run per iteration — locals re-declared each pass, valid in AngelScript); every refresh-recursion `form.reset(); settingsmenu();` (and the `...; return;` variants) replaced with `break;` (exit inner monitor loop → outer rebuilds). Theme-picker handlers (slt/slk/sln) now `break` in both branches. The 6 chooser go-backs in `menu_callbacks.nvgt` (charsmenu/keyboardchoosers/menuchoosers) deleted — they now only `return` their value, which the settings handler applies before rebuilding. Verified: only `settingsmenu(` refs left are the def (865) + the legit `mainmenu` call (115); brace balance = inner-while/outer-while/function. **DEV TESTED — works.** Root-cause escape/cancel/save fix (986/1144/1150 → return) landed earlier.

- **E1 DONE (2026-08) — Tier 2 complete.** `pausemenu` (`menu.nvgt:651`) wrapped in a `while(true)` loop; resume/save paths still `return` (exit), "view statistics" now re-shows the pause menu after stats closes. `statsmenu`'s non-ingame back → `return;` (was `pausemenu()`); the `statsmenu(true)` in-game path (menu_zone:23, command_parser:510 → `resume_pools(); return;`) is untouched. Both external `pausemenu()` callers (game_handlers:1264, menu_zone:32) still get return-on-resume. **DEV TESTED — works.**
- **D1 DONE (2026-08).** `game_menu.nvgt` restructured into the loop/return model. `gamemenu`, `newgamemenu`, `modemenu` are now `while(true)` loops; `loadgamemenu` stays flat (all paths terminal). Back/escape → `return` one level; every old parent/self call removed. `arena_target_menu` changed `void`→`bool` (returns true once a run is set up — `arena_setup_form` ran) so `modemenu` returns instead of re-showing the mode picker, collapsing the whole new-game chain back to the game menu after a game (or setup-cancel). `newgamemenu`'s erase-"No" → `continue` (re-show slot list); creature-list back → `continue` (re-show target list). Verified: braces 56/56, no `mainmenu()`/parent `gamemenu()` calls remain, `arena_target_menu` has no external callers. Death-path `gamemenu()` calls (charfuncts/checkpoint) left for Tier 4. **DEV TESTED — works.** (Follow-up: the `bool` `arena_target_menu`'s `while(true)` needed a trailing unreachable `return false;` or it fails "Not all paths return a value" — see [[project_angelscript_while_true_return]].)

## Clusters (grouped by difficulty)

### Tier 1 — self-contained, low risk
**A1. `mainmenu` self-loop — `menu.nvgt` 61, 70, 77, 98, 104 (5).** Each `mainmenu();` at a branch tail should be `return;` (main()'s loop re-shows it). Mechanical.

**B1. `settingsmenu` refresh-recursion — `menu.nvgt` 1000, 1006, 1016, 1036, 1055, 1081, 1089, 1102, 1116, 1131, 1138 (11).** Convert `settingsmenu` into a `while(true)` rebuild loop (mirror the `*_chooser` `do_build`/`continue` pattern). Refreshes become `continue`; the 3 exits (986/1144/1150) already `return`. NOTE the 8 "no return" ones (1000, 1016, 1036, 1055, 1081, 1089, 1102, 1116) are the highest-risk — after the nested `settingsmenu()` unwinds, the stale outer `form.monitor()` loop resumes.

**C1. Theme choosers → `settingsmenu` — `menu_callbacks.nvgt` 33, 44, 96, 103, 147, 154 (6).** `charsmenu`/`keyboardchoosers`/`menuchoosers` call `settingsmenu()` to go back. Once B1 makes settingsmenu a loop, DELETE these calls — the choosers already `return` their chosen value into settingsmenu's loop, which rebuilds. Do with B1.

### Tier 2 — self-contained subsystem, moderate
**D1. Game-menu subsystem — `game_menu.nvgt` 35, 115, 128, 140, 165, 180(A), 208, 223, 228(A), 231 (10).** The whole chain (`gamemenu`→`loadgamemenu`/`newgamemenu`→`modemenu`→`arena_target_menu`→`arena_setup_form`) navigates by calling parent/self; every completion tail-calls `gamemenu()`. Restructure so back = `return`, completion = `return`, and `gamemenu` loops (or is re-invoked cleanly). Contained to this one file. Watch the forward dispatches (36/37 gamemenu→sub, 209 modemenu→target, 227/230 target→creature/setup) — those are legit parent→child opens, keep them.

**E1. `statsmenu` ↔ `pausemenu` — `menu.nvgt` 718 (statsmenu→pausemenu, C).** `statsmenu`'s non-ingame tail calls `pausemenu()`; `pausemenu` opens `statsmenu()` at 682 (forward, fine). Make statsmenu `return`; let pausemenu loop.

### Tier 3 — parser/loader error paths (missed by the agent; several also missing `return`)
**G1. DONE (2026-08).** `load_map` (`map_parser.nvgt`) changed `void`→`bool` (true = loaded & good to play, false = failed/cancelled). All four internal `mapmenu()` jumps removed: 216 & 234 now `return false` (fixing the fall-through that read failed/empty data), 269 (escape) & 342 (missing mode) now `return false`, and a `return true` added at the success tail. Only two callers ran `game()` right after load — `map_menu.nvgt` play paths (compiled 689, decompiled 721) — now guarded `if(load_map(...)) game();`, so a cancelled/failed load drops back to the map menu instead of running game() on an empty map. The other ~98 callers (in-game reloads: travelpoints/checkpoints/doors/deaths) keep calling it as a statement (AngelScript ignores the unused bool — no mismatch). Behavior change: a failed in-game reload now leaves a cleared map instead of stacking a map menu mid-game (an improvement; those death/transition paths are Tier 4). Verified: no mapmenu() left in load_map, 5 typed returns, both guards applied. **DEV TESTED — works.**
**G2 + G3 DONE (2026-08) — Tier 3 complete.** `shield_parser.nvgt` (38) and `character_parser.nvgt` (28): the malformed-line handler (`data.length()<2`) was `alert(...); mainmenu();` with **no return**, so it (a) jumped to a menu from inside a parser that runs at startup AND mid-game (`arena_restore_run`), and (b) fell through to `if(data[0]==...){ x=parse_*(data[1]); }` — an out-of-bounds read on `data[1]` whenever a short line matched a key. Both now `continue;` (warn + skip the bad line, keep parsing the rest). Verified: no `mainmenu()` left in either parser. NEEDS DEV COMPILE+TEST.

**H1. `updater.nvgt` (4; agent found only 123/135).**
- **123 `get_download_url`** — calls `mainmenu()` on cancel but **does NOT return**, then still returns a download URL → a cancelled update can still download. **Genuine correctness bug.** Fix: return `""` on cancel; caller (`check_for_updates`, ~27) must check.
- **135, 149, 169 `downloadsounds`** — `mainmenu()` go-backs on question-no / download-fail / extract-fail (135/149 already `return`; 169 does not). Startup flow; convert to signal-and-return.

### Tier 4 — death path, HARDEST (needs game-loop analysis first)
Death handlers call `gamemenu()`/`mapmenu()` from **inside the game loop**, so the running `game()` frame stays live under the menu. Fixing means the loop must **detect death, break, and let the caller show the menu** — not a one-liner. Requires reading how `game()` exits after death before touching.
- **`charfuncts.nvgt` `show_death_prompt` 180, 181** (the shared death prompt; "no/try-again" → `gamemenu`/`mapmenu`). Entry points that feed it: `charfuncts.nvgt:124` (playerdeath), `command_parser.nvgt:1039`, `aircraft.nvgt:434`, `air_turbulence.nvgt:142` — those callers are fine; the bug is inside `show_death_prompt`.
- **`checkpoint.nvgt` 118, 119** (a death/checkpoint handler with the same `gamemenu`/`mapmenu` jump).
- **`fire.nvgt` 127** (`fireloop` inline death → `mapmenu()`).
- **`hazard.nvgt` 117** (`hazardcheck` death → `mapmenu()`; `game.nvgt:70` calls hazardcheck each frame).

## Recommended order
1. **A1** (mainmenu returns) — trivial, isolated.
2. **B1 + C1** (settingsmenu → loop; delete chooser go-backs) — kills the biggest cluster and the exact class the dev hit.
3. **H1 get_download_url** — genuine correctness bug, tiny fix.
4. **D1** (game_menu) and **E1** (stats/pause) — one reviewed change each.
5. **G1/G2/G3 + H1 downloadsounds** — loader/parser error paths; verify each.
6. **Tier 4 death path** — its own investigation of `game()`'s loop exit, then fix; highest risk, do last.

Each tier is an independent, reviewable change; commit between tiers. Get dev sign-off per tier (esp. Tier 4). No changelog unless the dev asks — these are internal control-flow fixes with no new player-facing behavior beyond "menus stop resurfacing."
