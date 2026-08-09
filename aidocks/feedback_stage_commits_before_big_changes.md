---
name: feedback_stage_commits_before_big_changes
description: Proactively flag a commit break point before a large or risky change — tell the dev to commit the safe pieces first so risky work lands in its own isolated commit. The dev commits by hand.
metadata:
  type: feedback
---

When a multi-stage feature has small/safe pieces followed by a large or risky one, **proactively tell the dev to commit the safe pieces before starting the big change** — don't wait to be asked. Call out the break point explicitly: which finished stages to commit now, and which upcoming stage is the "much bigger change" that deserves its own isolated commit.

**Why:** the dev commits by hand and wants each risky change isolated in its own commit, so if something breaks it's easy to bisect/revert without untangling it from unrelated small edits. A big change lumped in with little ones is also hard to review by screen reader and hard to roll back cleanly.

**How to apply:** at the end of a stage that completes the safe/additive work, before diving into the risky next stage, say plainly "commit now — the next part (X) is the big change and should be its own commit." Pair this with the standing [[feedback_list_modified_files]] close-out and [[feedback_confirm_before_implementing]] for the risky stage's plan. Relates to [[feedback_check_git_log_for_commits]].
