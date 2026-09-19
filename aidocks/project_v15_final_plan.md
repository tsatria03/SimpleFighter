---
name: project_v15_final_plan
description: Planning record for version 15.0 — the FINAL update SimpleFighter will ever receive, marking its 2-year anniversary (repo numbering v5.0 -> v15.0). Scope TBD; carries the one firm commitment to write a whole-package closing capstone in project_change_log_summaries.txt once 15.0 ships.
metadata:
  type: project
---

**STATUS: COMPLETE (2026-09-18).** 15.0 shipped its full feature set (20 changelog entries) and the closing capstone is written (see the firm-commitment section below). 15.0 is the **last version the game will ever get** — a send-off, closing two years of development (this repo's own numbering runs v5.0 -> v15.0). Scope not yet settled; treat as a design conversation ([[feedback_confirm_before_implementing]]).

## Shipped in 15.0 so far (changelog entries used)

1. **Broken-bones firing + general stun fix.** Removed the fire-gate so you can fire with broken bones; the bone-stun now actually freezes you. Root cause was that `update_character_settings()` rewrites the capability flags to allowed every frame (before `stuncheck()`), so no stun ever stuck — `stuncheck()` now HOLDS the stun each frame, and the player got a dedicated stun state (`me_stunned`/`me_stuntimer`/`me_stundir`) decoupled from the NPC/projectile-shared global so stunning an enemy doesn't freeze the player. This fixed ALL player stuns (falls, weapon hits, projectiles), not just bones — partly reverses the 14.4 "can't fire while bones broken" entry. Files: stunner.nvgt, game_handlers.nvgt, charfuncts.nvgt, character_parser.nvgt, checkpoint.nvgt.

2. **Universal tokens in map-element text.** The full token set (state + %flag:name% + %item:name% + %seq:name% + random()) now works inside author DISPLAY text of 7 elements (sign, text square, story-zone dialog, timed text, blockage, text-input title/prompt, menu-input prompt/labels) via one `expand_text_tokens` helper called live at each show site. See [[project_text_element_tokens_plan]] (BUILT).

3. **NPC gravity / fall mechanic (pass 1 + pass 2).** NPCs now fall off ledges (while chasing with `chase terrains` on), when knocked airborne, or when spawned unsupported, instead of floating; fall/land sounds by drop distance; and a hard landing (>=8 cells, unless in a fall zone) deals health-only fall damage + a stun. New `flying` field (true=floats) + `use lands` field, both surfaced in the NPC manager; `chase terrains` extended to apply during sight-pursuit (`|| pursuing`). Also decoupled climbing from move_z/move_y for non-flyers (climb automatically onto support). See [[project_npc_fall_mechanic_plan]] (BUILT, both passes). Two changelog entries (gravity + fall damage).

4. **NPC obstacle navigation (Tier 2).** A blocked chaser HOLDS instead of reversing into the void, and on 3d wall-follows around a blocking wall to reach the player (committed sidestep). Local avoidance, not pathfinding. See [[project_npc_navigation_plan]] (BUILT). One changelog entry. (Data groundwork this arc: all 187 NPC info.sif got `flying=false`, `use lands=auto`, `move z=true`, `chase terrains=true`, `z sight range=maxz`.)

## Firm commitments so far

- **Final capstone in the change-log summaries. [DONE 2026-09-18.]** All 20 15.0 changelog entries shipped, then the capstone was written in [[project_change_log_summaries]]: a new **V15 individual section** (after V14, before the overviews), and BOTH closing overviews extended to V15 — "the modern era (V10 -> V15)" (opening + a V15 paragraph + closing) and "the whole story (V1 -> V15)" (header + arc paragraph + a final bow: "A little over two years from that first hard-coded arena, SimpleFighter is complete."). The two-year arc is now closed in that file.

## Open (to settle with the dev)

- Scope: capstone-only (polish, docs, send-off framing) vs. new headline feature(s).
- Whether there's a player-facing farewell (readme/credits/changelog framing) and how understated.
- Any loose ends to close before the door shuts ([[project_deferred_concerns]], todo list, half-documented features).
- Version bump: dev flips `build/version.txt` to 15.0 with the changelog block ([[feedback_update_build_version_txt]]) — not done yet, dev's call.
