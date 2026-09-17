---
name: project_projectile_reward_plan
description: Feature plan (15.0, DESIGN SETTLED, building section-by-section) — re-add level + xp reward fields to projectiles (removed in the 9.6 "refactored projectiles" change). Destroying a placed/zone projectile awards xp camera-style. HARD format change, NO back-compat (dev's call).
metadata:
  type: project
---

**STATUS: DESIGN SETTLED, building section-by-section (2026-09).** Dev wants the pre-9.6 projectile level/xp reward back. Confirm each section on the dev's go-ahead ([[feedback_confirm_before_implementing]], [[feedback_describe_dont_show_code]]).

## Background (git)

The 9.6 refactor (commit a057190a, "Refactored projectiles from the ground up") DROPPED health, lives, level, and experience-drop fields to make projectiles "simple bouncing hazards instead of mini-creatures." A later 9.6 change re-added `health`+`destroyable` (shoot a projectile out of the air), but NOT level/xp. Old scheme (a057190a^:includes/builder/kombat/projectile.nvgt): `projlevel` + `poxp` fields; on destroy `xp += poxp*projlevel*xpmod` + "Defeated <type> level N" log + `kills+=1` + kill sound; level ALSO scaled damage (`damage*projlevel`). Old projectile_zone (line 30) spawned with projlevel=1, poxp=player level.

## Settled decisions (dev, 2026-09)

- **Restore level + xp** to projectiles. HARD format change, **NO back-compat** — projectile line 16/19 → **18/21** fields; old lines without the two fields won't load (dev accepts this).
- **Level = REWARD ONLY** (NOT the old damage-scaling): destroying a projectile grants `xp * level * xpmod`; damage stays exactly the `attack`/damage field. Like camera/container.
- **On destroy: xp + "N experience gained. Defeated <projtype> level N." log ONLY.** NO kills++ , NO kill sound (camera/container style, not the old NPC-style).
- **Placed projectiles:** author-set level + xp (build form inputs, like camera).
- **Projectile zones:** OLD AUTO-SCALING — spawned projectiles get level=1, xp=player's current level (reward ≈ player level * xpmod). NO new fields on the projectile_zone form/format.
- **Weapon/shield-launched projectiles: LEFT ALONE** — pass level=0, xp=0. They're `destroyable=false` (can't be shot down) so they'd never reward anyway; making them destroyable would be a player-self-farm exploit + redefine what launches are. ("Shoot down incoming NPC projectiles for xp" is a separate future feature if ever wanted.)
- **Cloner** (bullet.nvgt clones a struck projectile): carries the ORIGINAL projectile's level/xp.

## Field placement (on-disk)

Insert `level xp` right after `health`, mirroring camera (`hp level xp`): `projectile x y [z] leftx rightx backy fronty [botz topz] direction health level xp attack speed projtype bounce destroyable fireable singleuse`. Counts: 18 (2d/topdown) / 21 (3d).

## spawn_projectile call sites (6 — all need the new level/xp params)

1. projectile.nvgt build form (~572) — author level/xp.
2. projectile.nvgt read_projectile (~603) — parsed level/xp.
3. projectile_zone.nvgt (~38) — level=1, xp=level (player level).
4. bullet.nvgt cloner (~761) — original's level/xp.
5. weapon.nvgt launch (~503) — 0, 0.
6. shield_parser.nvgt reflect (~182) — 0, 0.

## Reward-on-destroy sites (~5 — projectile health<=0)

bullet.nvgt (bullet hit ~763, splash ~1120), glider.nvgt (~287), weapon.nvgt (melee ~1084, swing ~1470). Add a shared helper `award_projectile_kill(uint i)` (xp += poxp*level*xpmod + Defeated log) called at each, before the projectile is nulled.

## Build sections (section-by-section, dev's call)

- **§1 — Class + spawn_projectile signature + all 6 call sites** (level/xp params; values per the table above).
- **§2 — Read/write + parser dispatch (18/21) + Tier-1 lenok (18/21).**
- **§3 — Build form** (level + xp inputs, prefilled like camera; control order).
- **§4 — Tier-2 semantic** (validate level + xp are numbers, in projectile_semantic_error, adjusting offsets for the two new fields).
- **§5 — Reward-on-destroy helper wired into the ~5 death sites.**
- **§6 — Docs (projectiles.txt) + 15.0 changelog entry.**

## Notes

Projectile_zone format is UNCHANGED (auto-scaling, no fields). Only the `projectile` line format changes. Watch the block-comment `*/` trap ([[project_angelscript_block_comment_star_slash]]) in any glob-referencing comments. [[project_stability_rules]]: this is a deliberate no-back-compat read_/write_ signature + field-count change.
