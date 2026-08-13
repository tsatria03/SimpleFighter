---
name: project_angelscript_while_true_return
description: A value-returning AngelScript function whose only return statements live inside a while(true) loop fails to compile with "Not all paths return a value" — the compiler does no infinite-loop analysis. Add an unreachable return after the loop.
metadata:
  type: project
---

# AngelScript: while(true) doesn't satisfy the return-path check

If a non-void function's every `return` is *inside* a `while(true)` loop (the loop only exits via those returns, never `break`s or falls through), AngelScript still reports **`ERROR: Not all paths return a value`** and the game won't compile — so it won't launch, since it runs from source. The compiler does not prove the loop is infinite; it just sees a path where the loop "ends" and no return follows.

Fix: add an unreachable fallback `return <default>;` after the loop's closing brace.

```
bool arena_target_menu(string mode)
{
while(true)
{
...
if(back) return false;
...
return true;
}
return false;   // unreachable, but the compiler requires it
}
```

Hit 2026-08 converting the game-menu subsystem to the loop/return model ([[project_menu_recursion_cleanup]]): `arena_target_menu` (game_menu.nvgt) became `bool` with a `while(true)` body. `void` loop-menus (gamemenu/newgamemenu/modemenu/pausemenu) are unaffected — only value-returning ones need the trailing return. Related compile gotchas: [[project_angelscript_braceless_if]], [[project_angelscript_reserved_words]].
