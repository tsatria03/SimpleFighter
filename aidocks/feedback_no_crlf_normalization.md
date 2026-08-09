---
name: no-crlf-normalization
description: Do NOT run python CRLF-normalization passes after edits; git autocrlf handles line endings on commit
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

Stop running the post-edit python CRLF normalizer (`d.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')`) after every file edit. The dev's git setup (.gitattributes eol=crlf + commit-time normalization) converts line endings automatically when they commit.

**Why:** The normalization step added noise to every turn and is redundant — requested 2026-06-06. CLAUDE.md's "generate new files with CRLF" guidance still applies to file CONTENT being authored (don't deliberately write LF-only files), but no post-edit fixup pass is wanted.

**How to apply:** After Edit/Write calls, just stop — no Bash normalization step. Related: [[list-modified-files]].
