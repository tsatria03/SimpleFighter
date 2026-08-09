---
name: feedback_one_sentence_game_messages
description: In-game feedback messages spoken to the player must be exactly one sentence — no trailing second sentence with extra advice or instructions.
metadata:
  type: feedback
---

In-game feedback messages (the short notices spoken to a player — command results, action errors, status readouts) must be **exactly one sentence** — at least one, but never more. Don't tack on a second sentence with advice or instructions.

**Why:** the dev wants concise, single-statement feedback; trailing "do X instead" / "wait for Y" sentences are clutter when spoken by a screen reader.

**How to apply:** state the fact and stop. E.g. "This weapon does not take any ammo." NOT "...ammo. Draw a ranged weapon to reload." This is distinct from [[feedback_changelog_rules]] (which govern changelog prose, not in-game messages).
