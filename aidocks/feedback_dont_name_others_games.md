---
name: feedback_dont_name_others_games
description: In committed files (memory, docs, code comments), don't name games the dev didn't create — refer to them generically ("an external reference game"). Games the dev made (e.g. CaveDefender) are fine to name.
metadata:
  type: feedback
---

When writing anything that lands in the repo (aidocks memory, docs, changelog, code comments), **do not name a game the dev did not create.** Refer to it generically — "an external reference game", "the reference game", etc. Games the **dev made** (e.g. [[project_feature_ideas]]'s references to CaveDefender, the sibling NVGT project) are fine to name and worth keeping for cross-project context.

**Why:** the dev is fine attributing to their own work, but doesn't want another creator's game named in their committed files. It came up porting a builder feature from a game called Golden Crayon — the design is worth keeping, the source game's name is not.

**How to apply:** when a design or idea is drawn from someone else's game, capture the design fully but scrub the game's name (and any path into that game's install) to a generic descriptor. When it's the dev's own game, name it normally.
