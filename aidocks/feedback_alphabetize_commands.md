---
name: feedback-alphabetize-commands
description: "When adding a new in-game slash command, insert it in alphabetical order by full command name in both the command-blocker allcommands list and commands.txt."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

When adding a new `/`-prefixed in-game command, place it in **alphabetical order by full command name** (not by alias) in every list that enumerates commands:

- The `allcommands` array in `src/includes/builder/misc/command_blocker.nvgt` (each command is two entries: full name then alias, e.g. `"redomap", "ro"` — keep the pair together at the command's alphabetical slot).
- The command entries in `sf/docks/builder/commands.txt`.

The lists are loosely grouped by prefix family but the dev wants new commands slotted into their true alphabetical position — e.g. `redomap` goes between `rawdata` and `relchar`, while `undomap` goes at the end after `suicide`. Keep complementary pairs adjacent and alphabetized within themselves where the existing convention already does so (gamestart/gamestop, give/giveall, kill/killall).

**Why:** the dev manually re-sorted undo/redo into proper alphabetical order after they were first appended at the end, and asked that future commands follow suit.

**How to apply:** before finishing any command addition, find the command's alphabetical position in both files and insert there rather than appending. Related: [[feedback-confirm-before-implementing]].
