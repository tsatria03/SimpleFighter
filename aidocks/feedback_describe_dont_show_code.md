---
name: feedback_describe_dont_show_code
description: When building section by section, state the section count and name the classes/functions to be added with prose explanations, but never paste the actual code into chat.
metadata:
  type: feedback
---

When implementing work section by section, tell the dev up front **how many sections** the entity/feature will take, and for the section at hand **name every class and/or function** being added with a **one-line prose explanation of what each does** — but do NOT show the actual code (class bodies, function bodies, signatures with the code) in chat.

**Why:** The dev reviews the real files directly after each section is built; printing the source in chat is redundant and clutters the screen-reader read-through. They want the map (section count + named classes/functions + what each does), not the source lines.

**How to apply:** At the start of a build, state the total section count for the current entity. Each section, list the classes/functions to add (by name) with a short description of each one's role and behavior; explaining behavior in prose is encouraged. Then write the files and stop. Never include code blocks of the classes/functions you're adding. This composes with [[feedback_confirm_before_implementing]] (still get per-section sign-off) and [[feedback_list_modified_files]] (still end with the changed-files list).
