---
name: feedback_multiline_comment_style
description: Multi-line code comments use a single /* */ block, not a stack of consecutive // lines. Single-line comments still use //.
metadata:
  type: feedback
---

When a code comment spans more than one line, write it as a single `/* ... */` block comment, not a stack of consecutive `//` lines. Single-line comments still use `//` (inline or on their own line).

**Why:** the dev's preferred house style; stacked `//` blocks read as clutter and are harder to reflow.

**How to apply:** any new multi-line comment you author uses `/* */`; when you edit an existing stacked-`//` block, convert it while you're there.
