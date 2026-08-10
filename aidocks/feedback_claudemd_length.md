---
name: feedback-claudemd-length
description: "Keep CLAUDE.md under 40,000 characters — move content to memory files rather than expanding inline."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1df2413-bf71-468a-881b-4377e9893f1d
---

Keep CLAUDE.md under 40,000 characters. Do not add large blocks of content inline — move detailed rules and guidance to memory files instead and reference them with a pointer line.

**Why:** CLAUDE.md was deliberately shortened from a peak of ~43,000 characters down to ~33,000. The detailed changelog rules, help-topic prose constraints, and readme/todo quirks were extracted into memory files specifically to keep the file size down.

**How to apply:** Before adding new content to CLAUDE.md, check the current character count. If an addition would push it toward or past 40,000 characters, put the content in a new memory file instead and add a brief pointer in CLAUDE.md. Existing memory files for this project: [[feedback-changelog-rules]], [[feedback-tp-prose]], [[feedback-readme-todo-quirks]].
