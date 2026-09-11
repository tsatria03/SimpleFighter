---
name: project_unbuild_despawn_plan
description: Design plan for the unbuild and despawn commands (remove objects placed by build/spawn); NOT built
metadata:
  type: project
---

**STATUS: unbuild BUILT & shipping in 14.8; despawn still to build.** unbuild = `unbuild_entity()` in mapfuncts.nvgt (read_map_main_sif → delinear → find line → remove_at → push_map_undo → write_map_main_sif → load_map) + the `ub`/`unbuild` branch in command_parser.nvgt + allcommands entry + commands.txt + changelog. Feedback used: map-update sound + "Map updated." on success, "There's no <type> to remove." on miss. despawn NOT started — it's the in-memory, trusted-on-compiled counterpart (per-type teardown, sentinel-null; composites call their existing cleanup like a wall's platform_ids loop).** Two commands that remove what `/build` and `/spawn` place — the entity-cleanup gap the spawn help text already calls out ("the only cleanup verbs are /kill and /killall, npc-only; a /spawn of a non-npc entity has no command to remove it"). See [[project_trusted_commands_compiled]] (gating) and the build/spawn branches in `command_parser.nvgt`.

**Names & aliases (settled):**
- **unbuild** (`ub`) — inverse of `/build`. Permanent: removes the entity's line from `main.sif` and reloads. Decompiled-only.
- **despawn** (`dsp`) — inverse of `/spawn`. In-memory: removes the live entity from the session. Trusted-on-compiled.
(Aliases verified free earlier.)

**Gating (settled):**
- **unbuild = decompiled-only** (`&& !map_is_compiled`), like `/build` — it edits `main.sif`, which doesn't exist in a compiled `.map`. Belongs with the editing verbs, NOT the trusted-bypass set.
- **despawn = trusted-on-compiled** (`&& (!map_is_compiled || trusted)`), exactly like `/spawn` — so a switch/sensor/input/timer that spawns-on / despawns-off works on a shipped map, while typing despawn in the console on a compiled map stays blocked.

**Removal semantics (settled — the dev's simplification, no retyping fields):**
- **Bare form `<cmd> <type>`** → removes the MOST-RECENTLY-ADDED entity of that type (LIFO). `despawn sign` drops the newest sign; repeat to walk back. This is the common case and matches the build/test workflow.
- **Optional coord form `<cmd> <type> <x> <y> [z]`** → removes the specific one at those coordinates (coords ONLY, never the full field list) — the precision escape hatch when several exist and you don't want the newest. z on 3d maps.
- Arg parsing distinguishes the two by token count + mapmode (2 tokens = type-only; type + 2 or 3 coords = coord form).
- **Coord match = PLACEMENT CORNER (SETTLED):** the coordinate you give is the entity's own placement corner — a single-tile entity's `x y[ z]`, or a ranged entity's `minx miny[ minz]` — matched EXACTLY (not containment). Multiple entities at different corners each get uniquely targeted; if two share the exact same corner, the NEWEST (last in file / LIFO) is removed, repeatable. Tiny false-match risk (a ranged line whose maxx coincides), documented, acceptable.
- Type name accepts friendly and on-disk forms via `normalize_buildtype`, same as build/spawn.

**Why it's safe (settled):**
- despawn is in-memory only → NON-DESTRUCTIVE: over-despawning (removing a map entity, not just a spawn) is undone by a map reload.
- unbuild edits the file but is RECOVERABLE via `/undomap` (`/ud`), which already covers add/edit/remove of map lines.

**Implementation approach (settled direction):**
- **despawn:** find the target in the appropriate entity array by type; bare = last non-null of that type (highest index — spawns append to the end, so this reliably gets the newest spawn); coord = the non-null match at those coords. Remove via SENTINEL-NULL (`@<entity>s[i] = null;` + guarded loops/derefs) per the entity-array stability rule — NOT resize/remove_at.
- **unbuild:** read `main.sif` lines, find the last line (or coord-matching line) whose keyword matches the type, delete that line, write back, reload (`load_map`), like build's write-and-reload but removing.

**Scope (SETTLED — ALL entity types, both commands):**
- Composite entities (walls, ranged platforms, staircases) own a bundle of sub-tiles (e.g. a 3d wall's `platform_ids`, one platform per z — wall.nvgt:35-36). Removal must drop the whole bundle.
- **unbuild gets composites for FREE:** it deletes the single main.sif line and reloads; the reload rebuilds the map without that entity, so all sub-tiles vanish with no per-tile bookkeeping. Covers every type day one.
- **despawn reuses each entity's EXISTING teardown:** simple entities (sign, sound_source, hazard, item) = null the array slot (sentinel-null); composites call their already-written cleanup (a wall's destroy loops `platform_ids` and calls `remove_platform` — wall.nvgt:101-102). Per-type wiring, but no new removal algorithms.

**DESPAWN ARCHITECTURE (SETTLED):** must be SURGICAL — remove one live in-memory entity without touching anything else. A reload-based approach (track spawns as lines, reload + re-apply survivors) is REJECTED: `load_map` with default `force_spawned=false` keeps the player's position (only true teleports to spawn — map_parser.nvgt:837), BUT a reload resets ALL other runtime state (toggled switches, moved/killed NPCs, opened doors, collected items, timers), which is unacceptable for a gameplay cleanup command fired by a switch on a shipped map. So despawn is a per-type removal dispatch, `despawn_entity(type, by_coord, gx, gy, gz)`, mirroring `dispatch_entity_line` (map_parser.nvgt:1) — each of ~70 types has its own array, coord fields, and PROPER teardown (stop sounds, drop composite sub-tiles via platform_ids, etc.); nulling a slot without correct teardown leaks sounds/tiles. Match = last non-null of type (bare) or coord match (placement corner), newest wins, sentinel-null removal per the stability rule.
**DESPAWN FEEDBACK (SETTLED):** SILENT on success (gameplay cleanup, unlike unbuild's authoring "Map updated."); spoken notice only when nothing of that type exists to remove.
**DESPAWN SECTIONS (SETTLED — one category at a time):** (1) [DONE] Foundation + Interaction category [branch gated `&& (!map_is_compiled || trusted)`, arg parsing, dispatch skeleton, shared match logic, feedback, allcommands, + sign/switch/sensor/clock/calendar/instrument/text_input/menu_input/text_square]; (2) Traps; (3) Construction (composites w/ platform_ids); (4) Audio; (5) Zones; (6) Transitions; (7) Transportation; (8) Kombat+misc; (9) Docs (commands.txt + changelog + update /spawn's "no cleanup verb" note). Each category section adds its cases + proper teardown, independently testable.

**Build sequencing (SETTLED):** build in SEVERAL SECTIONS, ONE COMMAND AT A TIME (do unbuild fully, or despawn fully, before the other — dev's call which first), and DOCUMENT THEM SEPARATELY (separate commands.txt entries, separate changelog entries).

**OPEN details (small, decide at build time):**
- **Feedback behavior** — silent on success (good for switch cleanup) vs a spoken confirmation; and what to say when there's nothing of that type to remove (a notice like "There's no sign to remove." vs silent). Likely: silent success + spoken notice on nothing-to-remove, but undecided.
- **Item-mode siblings** — build maps item_door→door etc.; does unbuild/despawn need the same aliasing?

**Docs when built:** commands.txt entries (unbuild decompiled-only; despawn trusted-on-compiled — note both in the "Commands on compiled maps." section); UPDATE the `/spawn` help paragraph that says only /kill/killall exist for cleanup; changelog. Alphabetize into allcommands + commands.txt. On the todo list this is the "Add some commands to remove objects placed by the build and spawn commands." unfinished item.
