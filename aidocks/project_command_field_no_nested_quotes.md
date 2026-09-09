---
name: project_command_field_no_nested_quotes
description: A slash command in an entity's quoted text field may contain double quotes only if each is escaped as \" (extract_quoted is escape-aware); this lets a command spawn/build a quoted-text entity. Plain unescaped quotes still truncate.
metadata:
  type: project
---

Every entity that carries a slash command (switch, sensor, menu_input, text_input, …) stores that command in a double-quoted text field on its map line. Those fields are parsed by `extract_quoted` (`src/includes/main/functions/mapfuncts.nvgt`).

**As of 14.7, `extract_quoted` is escape-aware.** It finds field delimiters via `find_unescaped_quote` (skips any `"` preceded by a `\`) and un-escapes `\"` → `"` in each returned field. So a command stored in a quoted field CAN now contain quotes — but each inner quote must be written `\"` by hand. A plain unescaped `"` still closes the field early and truncates the command (that ambiguity is unresolvable — a quote can't be both delimiter and content without a marker).

Worked example that WORKS — inner quotes escaped, so the sign gets all its values:
`text_input 5 0 "welcome" "prompt" "" "" "spawn sign 5 0 \"hi\" sign false false" "" "" "" 0 0 false false false cancel lock false`

Worked example that FAILS — plain `"hi"` cuts the submit command at the first inner quote, so `/spawn sign 5 0` errors "wrong number of values":
`text_input 5 0 "welcome" "prompt" "" "" "spawn sign 5 0 "hi" sign false false" "" "" "" 0 0 false false false cancel lock false`

**Rule of thumb:** a command in a quoted field is safe if it has no `"`, OR if every `"` in it is escaped as `\"`. Escaping is per nesting level — a command that spawns an entity whose own command spawns a third needs `\\\"` at the outer layer, etc. One or two levels is practical; deeper gets ugly.

**Why builder-authored maps were unaffected by the escape change:** every writer STRIPS quotes before writing (`string_replace(field, "\"", "", true)`), so no builder-generated line ever contained a `\"` sequence — un-escaping is a no-op on all existing data. The only way `\"` reaches disk is hand-authoring. Edge case: a hand-authored field whose text literally ends in `\` right before its closing quote now reads as escaped and won't close (rare).

**Not yet done (Phase 2):** the builder forms still STRIP quotes on write, so a command with quotes typed into a builder form's command box loses them. To let the form auto-escape (type plain quotes, builder writes `\"` for you), swap strip→escape in the 4 command-carrying writers (switch/sensor/menu_input/text_input). Dev is fine hand-authoring `\"` for now, so Phase 2 is deferred, not planned.

Related: [[project_map_format]], [[project_stability_rules]].
