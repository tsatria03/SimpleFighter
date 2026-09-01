---
name: feedback_check_git_log_for_commits
description: The dev commits their own work, often between turns without saying so; check git log/status before asking about or assuming commit state.
metadata:
  type: feedback
---

The dev commits changes themselves, not you. Before asking "want me to commit?" or assuming something is uncommitted, check `git log --oneline` (and `git status`) — they often commit between turns without saying so, and the git log is the source of truth for what's landed.

**Why:** they were mildly annoyed at being asked about a commit they'd already made.

**How to apply:** after an editing turn, run a quick `git log` / `git status` to see whether they've already committed before mentioning commits at all. Still never commit for them unless explicitly asked. Relates to [[feedback_list_modified_files]] and [[feedback_stage_commits_before_big_changes]].

**Section-workflow trigger (added 2026-08):** when building a multi-section feature and the dev says they're **ready for the next section** (or anything similar), run `git log --oneline` / `git status` to confirm the previous section is already committed and the tree is clean before starting the next one — the dev asked for this so each section stays isolated in its own commit ([[feedback_stage_commits_before_big_changes]]); if the previous work isn't committed yet, flag it before proceeding.

**Refinement (dev-stated 2026-08-31):** only run that git check when the dev has NOT already told you the commit status. If they say "section N committed" / "I committed it" / similar, skip the git check and just continue — the check is only for confirming state you don't already know, not a ritual to repeat every section.
