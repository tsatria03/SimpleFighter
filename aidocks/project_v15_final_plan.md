---
name: project_v15_final_plan
description: Planning record for version 15.0 — the FINAL update SimpleFighter will ever receive, marking its 2-year anniversary (repo numbering v5.0 -> v15.0). Scope TBD; carries the one firm commitment to write a whole-package closing capstone in project_change_log_summaries.txt once 15.0 ships.
metadata:
  type: project
---

**STATUS: planning (opened 2026-09-15).** 15.0 is the **last version the game will ever get** — a send-off, closing two years of development (this repo's own numbering runs v5.0 -> v15.0). Scope not yet settled; treat as a design conversation ([[feedback_confirm_before_implementing]]).

## Shipped in 15.0 so far (changelog entries used)

1. **Broken-bones firing + general stun fix.** Removed the fire-gate so you can fire with broken bones; the bone-stun now actually freezes you. Root cause was that `update_character_settings()` rewrites the capability flags to allowed every frame (before `stuncheck()`), so no stun ever stuck — `stuncheck()` now HOLDS the stun each frame, and the player got a dedicated stun state (`me_stunned`/`me_stuntimer`/`me_stundir`) decoupled from the NPC/projectile-shared global so stunning an enemy doesn't freeze the player. This fixed ALL player stuns (falls, weapon hits, projectiles), not just bones — partly reverses the 14.4 "can't fire while bones broken" entry. Files: stunner.nvgt, game_handlers.nvgt, charfuncts.nvgt, character_parser.nvgt, checkpoint.nvgt.

## Firm commitments so far

- **Final capstone in the change-log summaries.** WHEN 15.0 is done, write one last summary in [[project_change_log_summaries]] (`aidocks/project_change_log_summaries.txt`) that ties the *entire package* together — the bow on the whole two-year arc, not just a V15 era section. This is the closing note for the whole file (which currently runs V1 -> V14.9 with three capstones). Do this LAST, after 15.0's features/docs are settled, so it can reflect what actually shipped.

## Open (to settle with the dev)

- Scope: capstone-only (polish, docs, send-off framing) vs. new headline feature(s).
- Whether there's a player-facing farewell (readme/credits/changelog framing) and how understated.
- Any loose ends to close before the door shuts ([[project_deferred_concerns]], todo list, half-documented features).
- Version bump: dev flips `build/version.txt` to 15.0 with the changelog block ([[feedback_update_build_version_txt]]) — not done yet, dev's call.
