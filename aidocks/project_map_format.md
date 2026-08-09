---
name: project_map_format
description: On-disk map format (main.sif/meta.sif, .map packs), map modes 2d/topdown/3d, spanning-entity min/max y, quoted text fields, and the single/ranged one-keyword rule.
metadata:
  type: project
---

## Map mode (2d / topdown / 3d)

Every map carries a `mode 2d|topdown|3d` line at the top of main.sif. `load_map()` resets `mapmode = ""` and reads it from the file. The parser branches on `mapmode == "3d"` to accept extra z-coordinate fields, and the builder/runtime branches on the same flag for spatial behavior. mapmode is creation-locked — see [[project_stability_rules]].

**Spanning entities require min/max y in topdown and 3d.** Any entity that already takes minimum/maximum x (spans tiles along x — platforms, vanishing platforms, walls, blockages, conveyor belts, hazards, force fields, spikes, doors, lifts, every zone, etc.) MUST also take minimum/maximum y when the map's mode is topdown or 3d, where y is a spatial axis (depth) rather than a single floor level. The builder UI must prompt for both, the spawn function must accept distinct y1/y2 values, `write_<entity>` must emit both, and `read_<entity>` must accept them. For 2d maps y stays a single value (floor height, not a spatial range). For backward compatibility, `read_<entity>` must still accept the older single-y line shape from pre-existing topdown/3d maps (treat missing maxy as equal to miny — a one-tile-deep strip), so `map_parser.nvgt`'s `sd.length()` check for those entities becomes three-valued: original 2d length, original single-y topdown/3d length (still loads), and the new min/max-y topdown/3d length. New maps authored after this change write the two-y form.

## Map format on disk

`sf/data/builder/maps/decompiled/<name>/data/main.sif`, plain text, one entity per line, space-delimited. Header lines are `mode` and minx/maxx/miny/maxy/minz/maxz; the sibling `data/meta.sif` holds owner, description, created date, modified date (key=value form). Example main.sif:

```
mode 3d
minx 0
maxx 100
miny 0
maxy 100
minz 0
maxz 100
bike 50 50 0 1 1500 bike
```

Maps may also be compiled into encrypted `.map` packs at `sf/data/builder/maps/compiled/<name>.map`; `load_map()` falls back to the pack when the decompiled folder is absent. The pack handle (`map_pack`) is opened by `load_map_pack` and assigned to `sound_default_pack` so audio reads transparently from inside the .map, while .sif reads go through `map_pack.read_file("data/main.sif", ...)` and `map_pack.read_file("data/meta.sif", ...)` directly.

## Quoted text fields

A set of text-bearing entities wrap their free-text / identifier fields in double quotes on disk. The convention was established by switch / sensor (on/off commands) and ttsenemie (taunt / hurt / death / voice fields), the template the rest follow. It now also covers: blockage, text_zone (and its `zone` alias), text_square, el_floor, clock, calendar, sign, story_zone, timed_text, elevator (spoken/label text), and door / passage (two quoted fields each — item id **and** password, so both may contain spaces). The contract is the read_switch shape: `write_<entity>` strips any literal `"` from the field then wraps it; `read_<entity>` parses the fixed front (coords + structural fields) positionally, pulls the quoted block via `extract_quoted()`, then splits the trailing structural fields out of the remainder. These entities are **not back-compatible** — there is no dual-path read, so a pre-quote (unquoted) line silently drops and old maps must be re-saved/migrated. Because door/passage text can hold spaces, their map_parser dispatch gates were changed from exact token counts to mode-aware `>=` floors (door >=18 / >=20 in 3d, passage >=16 / >=18). Door's single and ranged forms share one `door` keyword (no `ranged_door`), distinguished inside read_door by how many coordinates precede the first quoted field.

## Single/ranged share one keyword (no `ranged_` anymore)

Every entity that offers both a single-tile and a ranged-area form — clocks, calendars, signs, text squares, switches, sensors, travelpoints, hazards, spikes, vanishing hazards, force fields, timed text, doors/item doors, and the sound/url/timed sources and ambiences — reads and writes under one base keyword. There is no `ranged_<entity>` keyword in the builder menu, on disk, or in /spawn. `write_<entity>` emits the base name for single and `write_ranged_<entity>` emits the **same** base name for ranged; the parser tells them apart by line shape. Unquoted entities branch on `sd.length()` in `dispatch_entity_line` (short → `read_<entity>`, longer → `read_ranged_<entity>`). Quoted entities can't use a raw length (quoted text varies), so `read_<entity>` counts the coordinate tokens before the first `"`-prefixed token and delegates to `read_ranged_<entity>` when there are too many (2 vs 4 in 2d, 3 vs 6 in 3d; door is higher and mode-aware — 12 vs 14 tokens in 2d, 14 vs 17 in 3d — because of its many pre-quote fields). The builder shows one menu entry per entity with a `build mode` single/ranged list (single default), built with the form-rebuild loop (see `build_door` / the new-map form). When adding a new spanning entity, follow this — never introduce a `ranged_` keyword or a second "ranged X" menu entry. (Reading old `ranged_<entity>` lines is **not** supported; the one stock occurrence, old_main's `ranged_travelpoint`, was migrated to `travelpoint`.)

## Stock maps

In source control: 2d_test, 3d_test, topdown_test, elevator_example, house_example, old_main. old_main is the title-screen / hub showcase map; the rest are demos / smoke tests. When adding a new entity type, smoke-test it by adding a line to the matching mode's test map's `data/main.sif` and reloading.

Related: [[project_stability_rules]], [[project_game_data_layout]].
