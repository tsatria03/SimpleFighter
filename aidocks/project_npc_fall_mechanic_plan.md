---
name: project_npc_fall_mechanic_plan
description: Investigation + design notes for giving NPCs a fall/gravity system (candidate for 15.0). NPCs currently float — they move freely in y (2d) / z (3d) with no support check. The player's fallcheck() in map.nvgt is the model; the support helpers (gmt / platform_supports) are position-based and reusable. Design NOT yet settled, NOT built.
metadata:
  type: project
---

**STATUS: investigated, design OPEN, NOT built (2026-09).** Candidate 15.0 feature: make NPCs fall off ledges/when knocked airborne instead of floating. The mechanics are very doable — terrain detection already exists and is reusable — but three design decisions must be settled with the dev first ([[feedback_confirm_before_implementing]]). See [[project_v15_final_plan]].

## The player fall system (the model to mirror)

`fallcheck()` in `map.nvgt` (~1023-1360), run every frame from the game loop (`game.nvgt:69`).

- **Bail-outs:** does nothing on topdown maps, on a hook, during door/elevator/vehicle/plane movement, or while gliding.
- **Support test:**
  - 2d: supported if `gmt(me.x, me.y)` is not `""` and not `"air"`. Unsupported + `me.y > miny` (and not jumping/already falling) → start falling.
  - 3d: supported if `platform_supports(me.x, me.y, me.z)`. Unsupported + `me.z > minz` → start falling.
- **Descent:** a shared timer (`falltimer`/`falltime`) drops one cell per tick — `me.y--` (2d) / `me.z--` (3d) — incrementing `fallcounter`. Predicts drop distance up front to decide whether to play the plummet sound (drop >= 8).
- **Landing:** when a solid cell appears below (or z<=minz / y hits ground): soft landing (`fallcounter < fall_threshold`, default 8, or in a fall zone) → `playland()`, no harm. Hard landing → `playfall()` + damage `fallcounter * fallmod` (shield -> health), `break_charbones` (scales with fallcounter), a stun of `10 * fallcounter`, and damages the destroyable wall/platform/staircase/bike landed on. Tile zones can override threshold/fallmod for a landing (`tilezone_apply_fall`).
- **State:** `falling`, `fallcounter`, `falltimer`/`falltime`, `fall_threshold` (default 8), `fallmod` — all GLOBAL singletons (one player).

## The NPC side (why they float)

`npcloop()` in `npc.nvgt` (line 1022), per-frame.

- NPC coords are **`int x, y, z`** (npc.nvgt:13) — integers, NOT double like the player's `me`.
- NPCs move by AI intent in x, y (2d height), z (3d height), each gated by builder flags **`move_x`/`move_y`/`move_z`** (class lines 53-55). Movement is wall/terrain-aware but has **NO gravity/support concept** — an NPC sits at any height and nothing pulls it down.
- **Push already moves them vertically:** `apply_push` (weapon knockback, `weapon.nvgt:1571`) shoves an NPC step-by-step along x/y/z, stops at blocked tiles (`tile_blocked`), leftover -> impact damage. A vertical push launches an NPC into the air where it then floats.
- **Consequence machinery already exists on NPCs:** health, lives, pain sounds, and `npc_apply_break_charbones` (npc.nvgt:1010). And `gmt` / `platform_supports(double x,y,z)` / `wall_blocks(double x,y,z)` are position-based, so they work for NPC int coords as-is (auto-convert).

## What's missing (mechanically, only two things)

1. **Per-NPC fall state** — the `npc` class has no `falling` / `fallcounter` / `falltimer` fields (player's are globals; each NPC needs its own).
2. **A gravity step in `npcloop()`** — after AI move + push, nothing checks "is this NPC unsupported? pull it down." That's the feature: a per-NPC mirror of the player's support test + descent + landing.

## Three design decisions to settle (the real work)

1. **Gravity vs. intentional height. [SETTLED — option A.]** New NPC info.sif field **`flying`** (spaced key would be `flying`, a single word): `true` = floats/immune to gravity (today's behavior), `false` = fallable. The field is OPTIONAL on any NPC; **absent defaults to `false` (fallable)**. Dev's call: ADD `flying=false` to every shipped external NPC info.sif file so the whole roster is explicitly fallable. Cost: one field in the info.sif contract ([[project_game_data_layout]]) — note this is a per-NPC CHARACTER stat in the npc data file, NOT a map-line field, so existing map lines don't change.
2. **Backward compatibility. [SETTLED — option A, accept it.]** Gravity is the new default; floating-by-design or vertically-patrolling NPCs will drop on load unless their `flying` is set true. Some existing maps will change until authors flip the flag — accepted.

   **DONE (data side):** `flying=false` appended (CRLF) to all 187 shipped NPC info.sif files under `sf/sounds/decompiled/builder/kombat/npc/` (all categories incl. helpers). Idempotent script used; parser silently ignores the key until engine support lands, so this is currently a safe no-op.
3. **Landing consequences scope. [SETTLED — fall+land FIRST, damage as a later pass once fall+land is confirmed working.]** First pass: NPCs fall and land with their normal land/step sound, NO damage. Damage is a separate follow-up.

   **NPCs have NO bones.** The bone system (`broken_bones`, `break_charbones`, `bonecheck`) is player-only. `npc_apply_break_charbones` / `npc_play_pain` in npc.nvgt are MISNAMED — they act on the PLAYER (when an animal/zombie NPC hits you). So a future NPC fall-damage pass is HEALTH-only (subtract from npc health/lives), no bone breaks.

## Vertical-axis / gravity rule [SETTLED]

For a **non-flying** NPC, gravity OWNS the vertical axis and its vertical-move AI is suppressed (so it can't walk up into empty air and jitter against gravity):
- 2d: vertical = **y**, horizontal = **x**. Non-flying NPC does NOT self-move in y; moves in x only + falls in y.
- 3d: vertical = **z**, horizontal = **x, y** (ground plane — x = left/right, y = forward/backward). Non-flying NPC does NOT self-move in z; it still moves FREELY forward/backward and left/right (x AND y), and only falls in z. Confirmed with dev: 3d ground navigation is unchanged.
- Flying NPCs keep using move_y/move_z exactly as today.
- Caveat: on 3d a non-flying NPC won't climb UP onto raised platforms on its own — mark such an enemy `flying=true`.

## Technical findings for the engine build

- **Do NOT reuse the player's `falltime`/`falltimer`.** `falltime` (map.nvgt:24, default 250) is recomputed every frame from PLAYER speed/weight (game.nvgt:138: `falltime = 250/modspeed - shieldweight - wepchar.weight`), and `falltimer`/`fallcounter`/`falling` are player globals. NPCs need their OWN per-instance fields + a FIXED fall interval (e.g. a constant ~250ms, tunable).
- **Constructor order (npc.nvgt ~150-234):** sets field defaults, then `npc_parse(this)` at line 187 reads the info.sif (so `flying` from the file lands here), then a `scale_level` block (212+) overrides combat stats for arena/scaled spawns. So set `flying=false` (+ falling=false, fallcounter=0) in the defaults BEFORE line 187 so the file can override flying.
- **Field name is `flying`** (settled), true=float, false=fallable; parsed in `npc_parse_file` near the move-flag block (`else if(k == "flying") self.flying = string_to_bool(v);`). It is a CHARACTER stat in the NPC info.sif, NOT a map-line field.
- Support helpers reusable as-is on NPC int coords: `gmt(x,y)` (2d), `platform_supports(x,y,z)` (3d), `wall_blocks` (wall-climb-out on landing).

## Pass 1 build — fall + land ONLY (no damage). Not yet started.

1. **npc class fields:** `bool flying; bool falling; int fallcounter; timer falltimer;` + a fixed NPC fall interval constant. Default `flying/falling=false`, `fallcounter=0` in the constructor defaults (before npc_parse at line 187).
2. **Parse:** `flying` in `npc_parse_file` (near move x/y/z at ~495-497). [DATA DONE: all 187 shipped info.sif already carry `flying=false`.]
3. **Movement gating in `npcloop`:** move_y block (~1424) — add `&& (mapmode != "2d" || npcs[i].flying)`; move_z block (~1436) — add `&& npcs[i].flying`.
4. **Gravity step:** an `npc_fallcheck(i)` called once per NPC EVERY frame in `npcloop` (OUTSIDE the movement-timer gate). Mirrors the player's `fallcheck`: 2d support = `gmt(x,y)` not ""/"air"; 3d support = `platform_supports(x,y,z)`; start falling when unsupported and above min; descend one cell per the NPC's own falltimer; land on solid / floor (mirror the wall-climb-out). Skips: topdown, `flying`, paused.
5. **Landing sound: DEFERRED — discuss later** (candidate: NPC's own step sound via `resolve_npc_step_sound` + `pool.play_extended_3d` at npc coords; for now can land silently). Decide before shipping.
6. **Expose `flying` as a toggle in the NPC manager [SETTLED — yes]. Located: `edit_npc_form()` in `npc_manager.nvgt:342`.** The edit form is generated from `keys[]` (input boxes) and **`cb_keys[]`** (checkboxes, line 345 — currently `{"attacking","move x","move y","move z","drop item","tel x","tel y","tel z","ambient heal","launching","hit and run","chase terrains"}`). Both the checkbox render (lines 404-409, preset from the file's existing value) and the save-write (lines 439-440) loop over `cb_keys[]`, so the change is a ONE-ITEM addition: insert `"flying"` after `"move z"` in `cb_keys[]`. That yields both the toggle AND the write-back.
   - **CRITICAL:** `edit_npc_form` REWRITES the whole info.sif from scratch on save using only the known keys/cb_keys/list fields — it does NOT preserve unknown fields. So the appended `flying=false` would be SILENTLY DROPPED the first time an NPC is edited+saved UNLESS `flying` is in `cb_keys[]`. Adding it there is therefore REQUIRED (not just for the UI) to keep the field alive through the editor. (Note: this same rewrite behavior means any info.sif field not in the editor's lists is already lost on edit — pre-existing, out of scope.)
   - `build_npc()` (placing an NPC on the map) needs NO change — it doesn't touch stats.

## Pass 2 (later, after fall+land confirmed): fall DAMAGE — HEALTH ONLY (NPCs have no bones). Scale by fallcounter; tune an NPC threshold/mod.

## Files (anticipated)

Pass 1 EDIT: `npc.nvgt` only (class fields + constructor defaults, `flying` parse, npcloop movement gating + gravity step). Reuses `gmt` (mapfuncts), `platform_supports` (platform.nvgt), `wall_blocks` (wall.nvgt) unchanged. Docs (npcs.txt / info.sif field doc) + changelog when shipping.
