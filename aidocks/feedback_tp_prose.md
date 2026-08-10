---
name: feedback-tp-prose
description: "Rules for writing sf/docks/builder/*.txt help topic files — never reference engine internals, describe observable behavior only, keep filenames flat."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1df2413-bf71-468a-881b-4377e9893f1d
---

Rules for writing or editing `.txt` help topic files in `sf/docks/builder/`:

- **Never reference engine code.** Topic files are player- and author-facing documentation, not internal dev notes.
  - Don't name function names (e.g. `fallcheck`, `charparse`, `spawn_npc`, `melee_strike`, `update_char_*`).
  - Don't name source files (e.g. `map.nvgt`, `weapon.nvgt`, `character_parser.nvgt`).
  - Don't name internal variables (e.g. `fallcounter`, `wepchar`, `me_rotation`).
- **Describe the behavior the player or author observes**, not the implementation. "Each tile beyond the threshold counts for fall modifier raw damage" instead of "fallcounter times fall modifier in fallcheck()". If a behavior is too tangled to explain without naming code, that's usually a sign the explanation should be shorter or the design is leaking.
- **Filenames must stay flat** — no nested folders — because helpread() strips the `docks/builder/` prefix and `.txt` for the window title.
- **New topics appear automatically.** `/help` (the `hp`/`help` command in `command_parser.nvgt`) scans `docks/builder/*.txt` (under `sf/`, cwd-relative) via `find_files` and lists every topic — no `menu.nvgt` wiring is needed to make a new topic show up. (Verified 2026-06; an older note claimed manual wiring was required.)
- Not every entity needs a help topic. Only add one when there is enough player/author-facing behavior to document.

**Field-description formatting conventions** (the dev cares about these — apply to every new topic):
- **One field per line.** When listing a builder form's fields, give each distinct named field its own line as `Field name. Description.` — never pack multiple named fields onto one line (no `Tile, tile volume, tile pitch. ...` or `Move on x / y / z axis. ...`). A grouped positional concept may stay one entry: `Coordinates.`, `Bounding box.`, and a size entry (`Hazard size.`/`Platform size.`) each cover their axis inputs on a single line, matching how `Coordinates` is treated everywhere.
- **Lead-in ends with "the following:".** The sentence that introduces a field list should end with `the following:` — e.g. `The lift form takes the following:`, `The passage form exposes the following:`, `Its form takes the following:`. The dev appended this wording across the 8 transition/trap/construction topics and wants it as the standard going forward.
- Checkbox fields read `Name (checkbox). ...`; slider/percentage fields note the 0-to-minus-100 volume range and percentage-around-100 pitch where relevant.

**Why:** .txt files are read by players and map authors directly from the in-game help menu. Leaking internal names into them is confusing to non-devs and creates maintenance debt when internals are renamed.

**How to apply:** Any time a .txt file is being written or edited, verify no function names, file names, or variable names appear in the prose. If something can't be described without naming code, shorten the explanation instead.
