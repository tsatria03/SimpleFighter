---
name: feedback_dock_line_length_1024
description: "Keep every line in the player-facing docks (sf/docks/main + sf/docks/builder) at or under 1024 characters, because the dev's screen reader splits any longer line."
metadata:
  type: feedback
---

Each line in a player-facing doc must stay **at or under 1024 characters**. The dev reads these by screen reader, which splits any line longer than that into multiple lines, reading awkwardly.

This applies to **all player-facing docks**:
- Main docks: `sf/docks/main/{changelog,readme,todo list,credits}.txt`
- Builder help topics: `sf/docks/builder/*.txt`

**Why:** these docs are written one logical entry per physical line — a changelog entry, a readme paragraph, a help topic's section — with no wrapping inside the file. So a single long paragraph is one long line, and once it passes 1024 chars the reader chops it mid-thought.

**How to apply:** after editing or adding any dock text, check the length of the edited line(s) (e.g. `awk 'NR==n {print length($0)}' file`). If a line is over 1024, tighten the wording first (preferred — trim examples/redundancy, keep the substance), or split it into two entries / sentences-on-their-own-lines if the content genuinely needs the room. When writing new dock prose, keep entries lean so they don't creep over on the next edit. Relates to [[feedback_changelog_rules]] (entry caps / prose style) and [[feedback_tp_prose]] (help-topic prose); the [[feedback_one_sentence_game_messages]] rule is separate — that's for in-game feedback, not docs.
