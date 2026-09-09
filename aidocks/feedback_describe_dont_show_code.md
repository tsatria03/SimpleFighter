---
name: feedback_describe_dont_show_code
description: For a multi-section build, review ALL section plans up front in one message (section count + per-section classes/functions + prose), then code each section on the dev's go-ahead WITHOUT re-presenting its plan; never paste the actual code into chat.
metadata:
  type: feedback
---

When implementing a multi-section entity/feature, **front-load the whole plan**: in ONE message, state **how many sections** it will take and, for **every section**, **name the classes and/or functions** it adds with a **one-line prose explanation of what each does** — but do NOT show the actual code (class bodies, function bodies, signatures with the code) in chat. Then, when the dev signals they're ready for a section, **just code that section directly — do NOT re-present its plan** (they already have it from the up-front review).

**Why:** The dev reviews the real files directly after each section is built, and wants the entire section map once at the start rather than a fresh plan before every section (dev, 2026-09 — updated from the earlier per-section-plan approach). Printing the source in chat is redundant and clutters the screen-reader read-through — they want the map (section count + named classes/functions + what each does), not the source lines, and not a repeat of the plan each section.

**How to apply:** At the start of a build, give the full section-by-section overview in one message (all sections, their classes/functions, and what each does). Then build one section per dev go-ahead: write the files and stop, no plan recap for that section. Never include code blocks of the classes/functions you're adding. Composes with [[feedback_confirm_before_implementing]] (the dev's per-section "ready" is still the go-ahead — don't run ahead across sections) and [[feedback_list_modified_files]] (still end each build with the changed-files list). Between sections still check the latest commit ([[feedback_check_git_log_for_commits]]).
