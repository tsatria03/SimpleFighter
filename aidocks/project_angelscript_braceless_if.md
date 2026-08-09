---
name: project_angelscript_braceless_if
description: A braceless if/else in AngelScript governs only the ONE next statement; adding a second statement into a braceless menu-dispatch branch orphans the else and fails to compile.
metadata:
  type: project
---

A braceless `if` / `else if` / `else` in AngelScript governs only the **single next statement**. Menu dispatch chains are often written braceless (`if(sel=="x") action(); else if(sel=="y") ...`), so dropping a SECOND statement into a branch — e.g. a `fade_music()` before the action — makes the action a separate unconditional statement that sits between the `if` body and the following `else`, orphaning the `else` ("else with no matching if"). That's a **compile error**, and since the game runs uncompiled from source, a file that fails to compile won't launch at all (it looks like the game silently refusing to start).

**How to apply:** to add any extra statement inside a braceless `if/else` chain, either brace the branch — `if(sel=="x") { fade_music(); action(); }` — or hoist the shared call **once before the dispatch**. Don't trust indentation to group statements — NVGT ignores whitespace entirely (see [[feedback_dont_flag_indentation]]); only braces group. This is the same reason the sentinel-null one-liner guards in [[project_stability_rules]] must stay single-statement.
