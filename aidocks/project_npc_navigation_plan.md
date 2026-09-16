---
name: project_npc_navigation_plan
description: Feature plan (candidate 15.0, DESIGN OPEN, NOT built) — give NPCs basic local obstacle navigation so a blocked chaser sidesteps/holds instead of reversing into open air. Fixes the "reverse into the void" fall-off (a chase-terrains NPC drops off a staircase when a wall blocks its path toward you) and the general stuck-at-walls oscillation. NOT full pathfinding.
metadata:
  type: project
---

**STATUS: DESIGN OPEN, NOT built (2026-09).** Scoped out of the NPC fall work ([[project_npc_fall_mechanic_plan]]). Settle the approach/scope with the dev before building ([[feedback_confirm_before_implementing]]).

## The problem

NPC movement is GREEDY with NO pathfinding ([[project_npc_fall_mechanic_plan]] "intelligence check"). Per axis, intent = sign(target - self); each axis moves independently in `npcloop` (the `move_x`/`move_y`/`move_z` blocks, npc.nvgt ~1510-1536). When the direct step is blocked (wall / safe zone / terrain-disallowed), the code **REVERSES that axis**: `if(blocked) next_x = npcs[i].x - dx_intent;` then moves there if allowed. Consequences:
- **Reverse into the void (the trigger case):** a `chase terrains=true` chaser climbing a staircase toward a player who is PAST a wall keeps trying to step toward them, hits the wall, and reverses into the empty air beside the stairs — which `chase terrains` (terrain_off) PERMITS — so it steps off and FALLS instead of climbing. (Confirmed: player at the stair's own column (4,20) → NPC climbs fine; player one tile past a full-height wall (5,20) → NPC falls off.) Without `chase terrains` the reverse-into-air is blocked, so it stays and climbs — hence the current climb-vs-gap-chase tension.
- **Stuck-at-walls oscillation:** a wall or gap between NPC and target leaves it pacing back and forth, unable to route around.

## Goal

Basic LOCAL obstacle avoidance so a blocked chaser makes progress or holds position instead of reversing into a drop. Explicitly NOT full pathfinding (no A*, no map graph) — keep it cheap and per-tick.

## Design space (settle with dev)

- **Tier 1 — "don't reverse into the void" (minimal, low risk).** Only allow a REVERSED step onto a SUPPORTED cell; if the reversal would land on air, don't reverse (hold that axis at 0). Solves the trigger case directly: on the staircase, blocked-right no longer reverses into air, so the NPC stays on the stairs and climbs (its other-axis/up move still runs). Does NOT add routing-around-walls. Smallest change, least regression risk to existing NPC movement.
- **Tier 2 — "sidestep before reverse" (the real fix).** When the primary move toward the target is blocked, try a PERPENDICULAR step toward the target (preferring a supported cell) before falling back to reverse/hold. Lets a `chase terrains=true` NPC climb stairs AND still cross gaps — resolves the climb-vs-chase tension in one enemy. More logic, more tuning, higher regression risk (could introduce new oscillation/stuck patterns), needs careful testing across 2d + 3d.
- **Tier 3 — real pathfinding.** FEASIBLE — NVGT has a BUILT-IN `pathfinder` class (A* via MicroPather; legacy source at `misc/Legacy-NVGT/src/pathfinder.cpp`+`dep/micropather.cpp`). API: `array<vector>@ find(x1,y1,z1, x2,y2,z2, any@ data=null)` returns waypoints (3d-aware); `set_callback_function(pathfinder_callback@)` where `int pathfinder_callback(int x,int y,int z, any@=null)` returns a cell's move cost (impassable = a blocked cost); `int search_range` bounds the search; `const float total_cost`; `reset()`/`cancel()`/`automatic_reset`; diagonals configurable. So the search itself is free — you only write the callback that reports map passability. Catches: (1) the HARD part is a callback that encodes GRAVITY/support (a cell is walkable only if the NPC can stand there, not merely "not a wall") in the side-view+height model; (2) A* per NPC is costly — throttle (recompute every N ms, cache, cap search_range); (3) CONFIRM the pinned `C:\nvgt` build SF compiles against actually registers `pathfinder` (this is the legacy source; the SF engine is the same fork so it likely does, but verify). Biggest scope of the three, but not from-scratch.

## CHOSEN: Tier 2, built in 3 sections (dev's call — start here, may stop after §1)

- **§1 — Stop reversing into the void (foundation). [BUILT — awaiting playtest.]** `npc_cell_supported(cx,cy,cz)` helper + reverse-gating on move_x (both modes) and move_y (3d only); `next != current` guard added. Forward-into-air untouched. In `npcloop`'s move_x / move_y (3d horizontal) blocks, the `if(blocked) next = self - intent` reverse must NOT land a fallable (non-flying, non-topdown) NPC on an UNSUPPORTED cell — hold that axis instead. FORWARD steps onto air are left alone (so chase-terrains ledge-chasing still works); only the backward reverse-off-a-ledge is stopped. Fixes the reported staircase case (blocked-right stops reversing off the stairs, so it stays and climbs). New helper `npc_cell_supported(cx,cy,cz)` (3d: platform_supports; 2d: gmt solid non-air). Also add a `next != current` guard so a hold doesn't false-trigger the step sound. 2d move_y needs no gate (pass-1 vertical gating already zeros bad dy); move_z has no reverse. Lowest risk.
- **§2 — Perpendicular sidestep probe. [BUILT — awaiting playtest.]** `npc_sidestep(i,tx,ty,terrain_off)` (3d-only, non-flyer) + new per-NPC `sidestep_dir` (committed wall-follow direction). Called in npcloop when the NPC is stuck (moved==false) and not at the target: steps perpendicular (on the axis it needs less) onto solid, unblocked, SUPPORTED ground; commits the direction so it follows the wall to its end; a normal move clears the commit. Also made `npc_cell_supported` floor-aware (minz/miny boundary counts as support) so §1/§2 work on boundary-floor maps. Local wall-following, not pathfinding.
- **§3 — Docs + changelog.** npcs.txt behavior note (routes around simple obstacles instead of pacing) + one 15.0 changelog entry.

## Open questions

1. **Scope: Tier 1 or Tier 2?** (Recommend deciding based on appetite — Tier 1 is a safe quick win that fixes the reported bug; Tier 2 is the "climbers that also chase off cliffs" dream but riskier.)
2. **Prefer supported cells:** any AI step (sidestep or reverse) should avoid stepping into air unless deliberately crossing a gap toward the target — how strictly? (Gravity + chase-terrains make casual air-steps into falls.)
3. **When does it apply — pursuit only, or all NPC movement?** (Wander/patrol also reverse on block; changing all movement is broader.)
4. **Regression risk:** the `move_x/move_y/move_z` blocks are core to ALL NPC movement — any change must be tested against normal chasing, wandering, patrol, terrain restrictions, safe zones, 2d and 3d. No new permanent-stuck or jitter.

## Files (anticipated)

EDIT: `npc.nvgt` — the `move_x`/`move_y`/`move_z` intent/blocked logic in `npcloop` (~1510-1536). Reuses `gmt`/`platform_supports`/`npc_terrain_allows`. No data/manager/format changes. Docs (npcs.txt behavior notes) + changelog when built.

## Workaround until built

Per-enemy: `chase terrains=false` (stays on solid ground, climbs stairs, but won't chase across gaps) vs `chase terrains=true` (chases off ledges/gaps, but can reverse into a drop next to a wall). Or design the layout so a chaser isn't forced to reverse into a drop (no full-height wall beside the climb path).
