---
name: project_angelscript_block_comment_star_slash
description: A '*/' sequence inside a /* */ block comment closes the comment EARLY, so the rest is parsed as code and the build fails. Easy to hit in this codebase because comments often reference glob clip-name / path patterns.
metadata:
  type: reference
---

A `/* … */` block comment ends at the FIRST `*/`, even mid-word. So writing a glob/path pattern that contains `*/` **inside a block comment silently terminates it**, and the compiler parses the remaining prose as code → "Expected identifier / Instead found '*'" (and often a stray reserved word like `is`, `for`, `in` a few tokens later). The game runs from source, so this is a hard compile failure that blocks launch.

**What bit us (2026-09, container.nvgt):** a comment read `... a guard in the key_step_*/key_strafe_* movers ...`. The `*/` in `key_step_*/` closed the comment; errors reported at that line + the next comment with the same phrase. Fixed by dropping the asterisks: `key_step/key_strafe`.

**How to apply:** in a `/* */` block comment, never write a token containing `*/`. This codebase's comments frequently name glob patterns — `*loop*`, `*hurt*`, `builder/traps/.../` , `key_step_*/...`. A lone `*hurt*` is fine (no slash after the star); the danger is specifically `*` immediately followed by `/` (e.g. `foo_*/bar`, or ending a path glob with `*/`). Rewrite it: drop the star (`key_step/key_strafe`), space it out (`foo_ / bar`), or use a single-line `//` comment (where `*/` is harmless — that's why the same phrase on `//` lines didn't error). Sibling AngelScript gotchas: [[project_angelscript_braceless_if]], [[project_angelscript_reserved_words]], [[project_angelscript_while_true_return]]. Style: [[feedback_multiline_comment_style]].
