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

   **DONE (data side):** `flying=false` AND `use lands=auto` appended (CRLF) to all 187 shipped NPC info.sif files under `sf/sounds/decompiled/builder/kombat/npc/` (all categories incl. helpers). Idempotent scripts used; parser silently ignores both keys until engine support lands, so this is currently a safe no-op. (`use falls=auto` was already present pre-existing.) NOTE: `flying=false` is committed; `use lands=auto` was added later and may be uncommitted.
3. **Landing consequences scope. [SETTLED — fall+land FIRST, damage as a later pass once fall+land is confirmed working.]** First pass: NPCs fall and land with their normal land/step sound, NO damage. Damage is a separate follow-up.

   **NPCs have NO bones.** The bone system (`broken_bones`, `break_charbones`, `bonecheck`) is player-only. `npc_apply_break_charbones` / `npc_play_pain` in npc.nvgt are MISNAMED — they act on the PLAYER (when an animal/zombie NPC hits you). So a future NPC fall-damage pass is HEALTH-only (subtract from npc health/lives), no bone breaks.

## Vertical-axis / gravity rule [SETTLED — support-aware (option B)]

For a **non-flying** NPC, gravity OWNS the vertical axis. The AI's UPWARD move is allowed **only when the destination cell is supported** (something to stand on) — this stops the jitter (never rise into empty air) while STILL letting a ground enemy climb onto reachable platforms. The AI never moves itself DOWN (gravity does that).

- **3d:** vertical = **z**, horizontal = **x, y** (x = left/right, y = forward/backward). Non-flyer moves FREELY in x AND y (full ground navigation, unchanged); it may move UP in z only if `platform_supports(x, y, z+1)` is true; it falls in z when unsupported.
- **2d:** vertical = **y**, horizontal = **x**. Non-flyer moves freely in x; it may move UP in y only if the destination cell `(x, y+1)` holds a solid walkable tile (not air, not a wall — the movement code already blocks walls); it falls in y when unsupported. (In 2d the character stands ON the tile's own cell, so climbing = moving onto a higher solid tile.)
- Flying NPCs keep using move_y/move_z with no support gate, exactly as today.
- **Limitation (both modes):** it's a STEP onto a reachable supported cell, not a float THROUGH empty levels. An enemy can climb onto an adjacent higher platform but cannot ascend through open air to a platform with a gap beneath it — mark such an enemy `flying=true` (a fuller NPC jump/step-up navigation is a separate feature, out of scope).
- **Implementation note:** in `npcloop`, the upward vertical-intent branch (2d move_y block ~1424 when going up; 3d move_z block ~1436 when going up) gains a support check on the destination for non-flyers, and downward vertical intent is dropped for non-flyers (gravity owns it). Flyers bypass the gate.

## Technical findings for the engine build

- **Do NOT reuse the player's `falltime`/`falltimer`.** `falltime` (map.nvgt:24, default 250) is recomputed every frame from PLAYER speed/weight (game.nvgt:138: `falltime = 250/modspeed - shieldweight - wepchar.weight` — ~50ms/cell at normal speed 5, faster when quicker), and `falltimer`/`fallcounter`/`falling` are player globals. NPCs need their OWN per-instance fields + a FIXED fall interval. **Set: `npc_falltime = 50` ms/cell** (dev's call — matches the player's ~50ms normal-speed fall).
- **Constructor order (npc.nvgt ~150-234):** sets field defaults, then `npc_parse(this)` at line 187 reads the info.sif (so `flying` from the file lands here), then a `scale_level` block (212+) overrides combat stats for arena/scaled spawns. So set `flying=false` (+ falling=false, fallcounter=0) in the defaults BEFORE line 187 so the file can override flying.
- **Field name is `flying`** (settled), true=float, false=fallable; parsed in `npc_parse_file` near the move-flag block (`else if(k == "flying") self.flying = string_to_bool(v);`). It is a CHARACTER stat in the NPC info.sif, NOT a map-line field.
- Support helpers reusable as-is on NPC int coords: `gmt(x,y)` (2d), `platform_supports(x,y,z)` (3d), `wall_blocks` (wall-climb-out on landing).

## Pass 1 build — fall + land ONLY (no damage). §1 + §2 BUILT (engine + sounds); §3 (manager UI) + §4 (docs/changelog) remain.

1. **npc class fields:** `bool flying; bool falling; int fallcounter; timer falltimer;` + a fixed NPC fall interval constant. Default `flying/falling=false`, `fallcounter=0` in the constructor defaults (before npc_parse at line 187).
2. **Parse:** `flying` in `npc_parse_file` (near move x/y/z at ~495-497). [DATA DONE: all 187 shipped info.sif already carry `flying=false`.]
3. **Movement gating in `npcloop` (support-aware):** for a NON-flyer, in the vertical axis (2d move_y block ~1424 / 3d move_z block ~1436): drop DOWNWARD intent entirely (gravity owns it), and permit UPWARD intent only when the destination cell is supported (3d: `platform_supports(x,y,z+1)`; 2d: `(x,y+1)` is a solid non-air, non-wall tile). Horizontal axes (x always; y on 3d) are untouched. Flyers bypass the gate (move as today).
4. **Gravity step:** an `npc_fallcheck(i)` called once per NPC EVERY frame in `npcloop` (OUTSIDE the movement-timer gate). Mirrors the player's `fallcheck`: 2d support = `gmt(x,y)` not ""/"air"; 3d support = `platform_supports(x,y,z)`; start falling when unsupported and above min; descend one cell per the NPC's own falltimer; land on solid / floor (mirror the wall-climb-out). Skips: topdown, `flying`, paused.
5. **Landing sound [SETTLED — reuse the existing fall-sound system].** The infra already exists and matches the dev's intent: field **`use_falls`** (auto/own/player/never) — PRE-EXISTING on all NPCs (NOT added by the flying script), already PARSED (npc.nvgt:446), already IN THE NPC MANAGER as the "use falls" list (`npc_manager.nvgt:373`, saved at 442). **`resolve_npc_fall_sound()`** (npc.nvgt:313) already resolves the `*fall*` clip: own (`builder/kombat/npc/<cat>/<sub>/general/*fall*`) → platform tile (`builder/construction/platforms/<tile>/*fall*`) → "skip" sentinel; `own`/`player`/`auto`/`never` modes. Currently consumed only by the death `spawn_bodyfall`.
   - **Design [UPDATED — dev's call]:** the LAND sound gets its OWN new field **`use lands`**, NOT a reuse of `use falls`. `use_falls` keeps governing the `*fall*` (descent/whoosh) clip; a NEW `use_lands` field governs the `*land*` (touchdown) clip. Both are per-NPC, four modes (auto/own/player/never), so an NPC can have a fall whoosh but no land thud, or either sourced own-vs-platform independently. Player's `playland` (map.nvgt:785) plays a `*land*` clip (char `*land*` + tile `*land*`) distinct from `*fall*`, which is why they warrant separate control.
   - **New `use_lands` field — full parallel to `use_falls`, all of these needed:**
     - npc class field `string use_lands;` default `"auto"` (mirror `use_falls` at npc.nvgt:87/142).
     - Parse: `else if(k == "use lands") self.use_lands = v;` (npc_parse_file, beside `use falls` at ~446).
     - New resolver **`resolve_npc_land_sound(self)`** mirroring `resolve_npc_fall_sound` but with `*land*` paths (own `.../npc/<cat>/<sub>/general/*land*` → platform tile `builder/construction/platforms/<tile>/*land*` → "skip"); `own`/`player`/`auto`/`never`.
     - NPC manager: add a **new "use lands" list** in `edit_npc_form` right beside the existing "use falls" list (npc_manager.nvgt:373 area) + preset-load + save-write (mirror lines 373/380/442).
     - **DATA [DONE]:** `use lands=auto` appended (CRLF) to all 187 shipped NPC info.sif (same idempotent script as `flying`). Parser ignores it until the resolver/consumer lands, so it's currently a safe no-op.
   - **Runtime [BUILT — player-matching, dev's call]:** ONE sound on landing, chosen by drop distance via `npc_fall_threshold = 8` (mirrors the player's fall_threshold): `fallcounter >= 8` → hard landing plays `resolve_npc_fall_sound` (use_falls); `< 8` → soft landing plays `resolve_npc_land_sound` (use_lands). NO start-of-fall whoosh (dev's call). Played at NPC coords via its category `pool.play_extended_3d`; "skip"/empty = silent. (At landing the NPC is on the solid tile, so both resolvers' platform-tile fallback finds the tile's `*fall*`/`*land*` clip.)
   - **NO manager change for `use_falls`** — already fully wired. Manager additions this feature: the `flying` checkbox AND the new `use lands` list.
   - **Origin of `use_falls` (verified via git):** it pre-dates this work on BOTH sides — the code (`resolve_npc_fall_sound` + parse + manager list) landed in commit `06fabb1d` "Major game enhancements", and `use falls=auto` was already in the shipped info.sif before the `flying=false` commit (`f6105c02`, which added ONLY `flying=false`). It was built for the **death bodyfall**: when an NPC dies, `spawn_bodyfall` (command_parser.nvgt:239/286, npc.nvgt:1679) drops the corpse and uses `resolve_npc_fall_sound(npc)` for the sound of the body hitting the ground. No LIVING NPC uses it yet (they can't fall). So the new gravity system is simply a SECOND consumer of the same `use_falls` setting — one field then governs both a corpse's fall sound and a live NPC's fall/land sound.
6. **Expose `flying` as a toggle in the NPC manager [SETTLED — yes]. Located: `edit_npc_form()` in `npc_manager.nvgt:342`.** The edit form is generated from `keys[]` (input boxes) and **`cb_keys[]`** (checkboxes, line 345 — currently `{"attacking","move x","move y","move z","drop item","tel x","tel y","tel z","ambient heal","launching","hit and run","chase terrains"}`). Both the checkbox render (lines 404-409, preset from the file's existing value) and the save-write (lines 439-440) loop over `cb_keys[]`, so the change is a ONE-ITEM addition: insert `"flying"` after `"move z"` in `cb_keys[]`. That yields both the toggle AND the write-back.
   - **CRITICAL:** `edit_npc_form` REWRITES the whole info.sif from scratch on save using only the known keys/cb_keys/list fields — it does NOT preserve unknown fields. So the appended `flying=false` would be SILENTLY DROPPED the first time an NPC is edited+saved UNLESS `flying` is in `cb_keys[]`. Adding it there is therefore REQUIRED (not just for the UI) to keep the field alive through the editor. (Note: this same rewrite behavior means any info.sif field not in the editor's lists is already lost on edit — pre-existing, out of scope.)
   - `build_npc()` (placing an NPC on the map) needs NO change — it doesn't touch stats.

## Pass 2 (later, after fall+land confirmed): fall DAMAGE — HEALTH ONLY (NPCs have no bones). Scale by fallcounter; tune an NPC threshold/mod.

## Files (anticipated)

Pass 1 EDIT: `npc.nvgt` only (class fields + constructor defaults, `flying` parse, npcloop movement gating + gravity step). Reuses `gmt` (mapfuncts), `platform_supports` (platform.nvgt), `wall_blocks` (wall.nvgt) unchanged. Docs (npcs.txt / info.sif field doc) + changelog when shipping.
