---
name: feedback_menus_say_canceled
description: Every menu/input-box back, escape, or cancel path should speak "canceled" so a screen-reader player always gets audible feedback when backing out.
metadata:
  type: feedback
---

When building any menu or input box, every way of backing out without choosing an action must `speak("canceled")`: pressing Escape (a menu's `m.run()` returns < 0; an input box / `vd.input_box` / `vd.password_box` returns ""), choosing a **Back** item (even in a "single"/leaf menu — Back closes the menu, it doesn't open a sub-menu), and choosing **No** on a yes/no confirmation.

**Why:** the dev wants consistent audible feedback when canceling out; silent menus leave a screen-reader player unsure whether anything happened.

**How to apply:** in every new menu/input flow, wire `speak("canceled")` on the escape path, the Back item, and the No/decline path. Match the existing menus in the codebase that already do this. Related: [[feedback_yes_no_menu_labels]].
