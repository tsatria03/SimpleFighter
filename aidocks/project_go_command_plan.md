---
name: project_go_command_plan
description: Feature plan (candidate 15.0, DESIGN being settled via Q&A, NOT yet built) — extend /go so it can MOVE any single-point map entity to a coordinate by type keyword (newest-of-type), replacing the old NPC-only category+subtype move form. Modeled on the /build /unbuild /spawn /despawn /kill /killall name-dispatch pattern.
metadata:
  type: project
---

**STATUS: DESIGN being settled via Q&A (2026-09), one question at a time (screen-reader dev). NOT yet built.** From the dev's todo: "Make it so the /go command can take any entity to use for moving." Reference the six name-dispatch commands (/build, /unbuild, /spawn, /despawn, /kill, /killall) AND the current /go.

## How /go works TODAY (command_parser.nvgt ~51, gop() in map.nvgt:145)
- `/go x y` (2d/topdown) or `/go x y z` (3d) -> moves the PLAYER (`gop("me","",x,y,z)`): sets me.x/y/z, resets fall/jump state, plays char *move* cue, speaks "Player moved to ...".
- `/go <category> <subtype> x y [z]` -> moves an NPC found by category+subtype (e.g. `go zombie walker 5 5`) to x,y,z: sets npcs[i].x/y/z, repositions tauntsound, restarts movetimer, plays *move*. NPC-ONLY, uses the old clunky category+subtype addressing.
- `gop()` clamps the destination to map bounds (minx..maxx etc.) -> "You can't move yourself or an entity out of map boundries." Gated `(!map_is_compiled || trusted)` (in-memory, live -- a switch/sensor can relocate during play on compiled maps).

## Settled decisions (dev-confirmed 2026-09)
- **Unified type keyword, no subtype** (like /kill): `/go <type> ...` addresses by the despawn/kill keyword (`npc`, `camera`, `jet`, ...); the old NPC category+subtype form is DROPPED. `go npc 10 5` moves the newest npc.
- **Option A — NEWEST only.** `/go <type> <destx> <desty> [destz]` moves the NEWEST entity of that type to the destination. NO source-coordinate form (rejected Option B). The destination is always the trailing coordinate.
- **Player form unchanged:** `/go <destx> <desty> [destz]` still moves the player.
- **SCOPE = SINGLE-POINT entities only.** The dev EXCLUDES anything with min/max x/y/z (ranged boxes + built tile structures: signs, clocks, calendars, doors, spikes, all zones, walls, platforms, staircases, slants, etc.). Only entities stored as one point (a settable x/y/z) are movable -- move = set position + reposition its sound(s) + reset move timer, exactly like today's NPC move. The exact movable list is pending an entity-map (Explore agent running 2026-09); `projectile` is the one suspected BOTH (point prox/proy/proz + mnx/mxx bounce bounds) -- decide whether its bounce range disqualifies it.

## SCOPE FINALIZED (dev-confirmed 2026-09) — 16 movable single-point types
Entity map done (Explore agent 2026-09). Movable set + per-type detail (all coords INT unless noted; each move_<type> = find newest live instance, set position, reposition its looping slots, reset its move timer, return bool):
1. `npc` — npcs[i].x/y/z; reposition `tauntsound` + (humans) `refsound2` via `npc_pool(category).update_sound_3d(...)`; restart `movetimer`. (Model: gop's existing NPC branch.)
2. `camera` — sucams[i].sucamx/y/z; reposition `camsound`/`alarmsound`/`wornsound` via `sucampool.update_sound_3d`.
3. `jet` — jets[i].jetx/y/z; reposition `loopsound` via `jetpool.update_sound_3d`; restart `movetimer`.
4. `container` — containers[i].containerx/y/z; `loopsound` via `containerpool.update_sound_3d`; restart `movetimer`.
5. `ttsenemie` — ttsenemies[i].ttsemx/y/z; `ttsemsound` via `ttsempool.update_sound_3d`; restart `ttsenemietimer`.
6. `bike` — bikes[i].bikex/y/z; `bikesound` via `bikepool.update_sound_3d`.
7. `aircraft` — aircrafts[i].plainx/y/z; `loopsound` (played via play_3d) — set coords + re-emit; `plaintimer`.
8. `vehicle` — vehicles[i].vehx/y/z; `vehsound` via `vehpool.update_sound_3d`.
9. `fire` — fires[i].firex/y/z; `firesound` via `firepool.update_sound_3d`; `firetimer`. (firerange* are seeing-ranges, NOT a footprint.)
10. `teleporter` — teleporters[i].telx/y/z; `telsound` via `telpool.update_sound_3d`; `teltimer`. (dtelx/y/z = the destination it sends the PLAYER, independent — do NOT touch.)
11. `bomb` — bombs[i].bombx/y/z; `fallsound`/`landsound` via `bombpool.update_sound_3d`; `bombtimer`.
12. `time_bomb` — timebombs[i].timbombx/y/z; `loopsound` via `bombpool.update_sound_3d`.
13. `mine` — mines[i].minex/y/z; `minesound`/`lightsound` via `minepool.update_sound_3d`.
14. `wind` — winds[i].windx/y/z (**DOUBLE coords**); `windsound` via `windpool.update_sound_3d`; `windtimer`. (windrange* = seeing-ranges.)
15. `spawnpoint` — spawnpoints[i].spawnx/y/z; NO sound, NO timer — pure coord set.
16. `checkpoint` — checkpoints[i].checkx/y/z; `checksound` (looping only if `looping`) via `checkpool.update_sound_3d`; no roam timer.

EXCLUDED: `floor_breaker` + `speaker` (dev's call 2026-09 — floor_breaker drags a platform tile, speaker is a two-point stereo pair); `projectile` + `air_turbulence` (BOTH point+min/max, out by the no-min/max rule); all RANGE entities (signs, doors, spikes, zones, walls, platforms, staircases, slants, sound sources, etc.).

## Still OPEN
- Ridden-transport: RESOLVED (dev 2026-09) — move the rider along. In move_aircraft/vehicle/bike, if the machine is being ridden (its `moveable` flag, the same one despawn checks as was_flying/was_driving/was_riding), also set me.x/y/z to the destination so the player stays aboard.
- DEFERRED FOLLOW-UP (dev 2026-09, "one thing at a time — go command first"): a BROADER "any player force-move carries the ridden transport" fix, covering the axis commands (setx/addx/suby/setz...) and combat knockback (weapon.nvgt ~566/588 + bullet.nvgt ~174/227 push the player; firing is NOT suspended while riding). Options were "everything that moves you" vs "only commands you issue" — NOT yet chosen. Do this AFTER the /go feature ships. The clean impl is a shared `carry_transport()` (snap the moveable machine's coords to me.x/y/z) or an auto re-sync at the top of the ride loops. The /go feature itself only handles its OWN two directions (below).
- Player-move-while-riding: RESOLVED (dev 2026-09) — the SYMMETRIC case (part of the /go feature). Today `/go x y z` on yourself while riding moves ONLY the player, desyncing you from the machine (its sound stays at the old spot; dismount needs me.x==vehx so you can get stuck). FIX in Section 4: in gop's "me" branch, AFTER setting me.x/y/z, if riding (invehicle/onbike/inplain), find the ridden machine (the one with moveable==true in vehicles/bikes/aircrafts) and set its coords to match, so the transport comes with you. (While riding, the loops keep me and the machine in lockstep — each drive step bumps both by the same delta, vehicle.nvgt ~100-102 — so they must stay equal.)
- Command shape: distinguish player vs type form by ARG COUNT (2d: 3 tokens=player `go x y`, 4=type `go type x y`; 3d: 4=player, 5=type). Bounds-check the destination the way gop does (extract a shared check or reuse). Feedback mirrors kill: "Moved the X to A, B[, C].", "There's no X to move.", "You can't move a Y." (ranged/unknown). Gating keep `(!map_is_compiled||trusted)`.
- Docs (commands.txt /go rewrite) + one 15.0 changelog entry.

## Section progress
1. **Kombat move helpers (5). [DONE 2026-09]** After each `kill_*`: `move_npc` (x/y/z, reposition tauntsound via npc_pool.update_sound_3d, restart movetimer — gop's NPC branch generalized to newest), `move_camera` (sucamx/y/z, nudge camsound; stationary, no timer; alarm/worn non-positional), `move_security_jet` (jetx/y/z, loopsound, movetimer), `move_container` (containerx/y/z, loopsound, movetimer), `move_ttsenemie` (ttsemx/y/z, ttsemsound, ttsenemietimer). Each finds NEWEST live, returns bool; caller bounds-checks + speaks. move_x/y/z in npc.nvgt are FIELDS not functions (no collision). Braces verified.

2. **Transport move helpers (3). [DONE 2026-09]** After each `kill_*`: `move_vehicle` (vehx/y/z, reposition vehsound via vehpool.update_sound_3d), `move_bike` (bikex/y/z, bikesound), `move_aircraft` (plainx/y/z). EACH: if `moveable` (being ridden -- same flag despawn checks) set me.x/y/z = the machine's (int) coords so the rider stays aboard + lockstep holds. Aircraft SPECIAL: while flown its loopsound is destroyed + engine non-positional, so only carry the pilot; while parked reposition loopsound. Braces verified.

3. **Trap + misc move helpers (8). [DONE 2026-09]** After each `despawn_*`: `move_fire`/`move_teleporter`/`move_wind` (set coords, reposition loop via <pool>.update_sound_3d, restart firetimer/teltimer/windtimer; teleporter leaves dtel* untouched; wind coords DOUBLE no int cast), `move_bomb`/`move_timebomb`/`move_mine` (relocate + reposition active cues guarded !=-1, NO timer reset = fuse keeps counting; bomb sound z=0), `move_spawnpoint` (pure coord, no sound/timer), `move_checkpoint` (reposition checksound if !=-1, no timer). All 16 move_* now exist. Braces + timer/sound fields verified.

## Build shape (mirror the kill feature) — ~6 sections
Per-type `move_<type>(destx,desty,destz)` in each entity file + `move_entity(type,...)` dispatcher + `is_movable_type(type)` in map_parser (next to kill_entity). Rewrite /go: player form (arg count) -> gop; type form -> `normalize_buildtype` -> is_movable_type guard -> bounds check -> move_entity. DROP gop's dead NPC branch (map.nvgt ~170-195). See [[project_kill_command_plan]] (closest sibling), [[project_stability_rules]] (double coords for wind, sound repositioning), [[feedback_alphabetize_commands]].
