---
name: feedback_yes_no_menu_labels
description: For a yes/no menu, label the two items exactly "Yes" and "No" (Yes first) — put the context in the prompt, not in the option labels.
metadata:
  type: feedback
---

When a menu is a yes/no choice, make the two menu items say exactly **"Yes"** and **"No"** — nothing more. Don't append explanatory clauses like "Yes, respawn them each time the wall recovers" / "No, they leave when the wall falls".

**Why:** the question line above the menu already carries the meaning; verbose option labels are redundant and slower to read by screen reader.

**How to apply:** put the full context in the menu's question/prompt text; keep the options themselves to bare "Yes" and "No" (Yes first, so `choice==0` is Yes). Related: [[feedback_menus_say_canceled]].
