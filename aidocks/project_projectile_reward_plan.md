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

- **§1 — Class + spawn_projectile signature + all 6 call sites. [DONE 2026-09]** Class fields `projlevel`/`projxp` (named proj* to avoid shadowing global player level/xp), added to constructor + spawn_projectile after `hp` (params `plv`/`pxp`). Call sites: zone `1, level`; cloner `projectiles[i23].projlevel/projxp`; weapon+shield `0, 0`; form + read pass PLACEHOLDER `1, 0` (finalized in §3/§2). `level` global confirmed (command_parser `level +=`, arena `int(level)`). Braces 130/130. No reward until §5.
- **§2 — Read/write + parser dispatch (18/21) + Tier-1 lenok (18/21). [DONE 2026-09]** read_projectile parses `lv`/`xpv` at sd[o+2]/[o+3] (post-hp reads shifted +2), passes them to spawn (real values now). write_projectile: +level/xp params, writes `…dir hp level xp dm sp…`. Parser dispatch + Tier-1 → 18/21 (map_parser.nvgt). Form's write_projectile call still placeholder `1, 0` (finalized §3). Offsets verified (su at sd[17] 2d / sd[20] 3d). Braces 130/130, 197/197.
- **§3 — Build form. [DONE 2026-09]** `level` (default "1") + `xp` (default "0" = opt-in reward) inputs after health, char filters, `blev`/`bxp` reads; both write_projectile + spawn_projectile calls now pass the real values (placeholders gone). Braces 130/130. Author-set level/xp now flows form→line→reload. Reward still not wired (§5). ALSO (dev request 2026-09): projectile's object-info-menu entry (menu.nvgt infomenu ~568) now appends " level "+projlevel, like the security camera (level shown, xp not).
- **§4 — Tier-2 semantic. [DONE 2026-09]** `projectile_semantic_error`: added level (sd[o+2]) + xp (sd[o+3]) number checks after health; shifted damage→o+4, speed→o+5, sound→o+6, bounce→o+7, dest→o+8, pf→o+9, su→o+10 (all match read_projectile). Doc comment updated. Braces 132/132.
- **§5 — Reward-on-destroy helper wired into the 5 death sites. [DONE 2026-09]** `award_projectile_kill(uint i)` in projectile.nvgt: `gained = projxp*projlevel*xpmod; if(xpmod>=1 && gained>0){ xp+=gained; kombatlog "Defeated <type> level N" }` — xp-only (NO kills++/kill sound), SILENT when gained==0 (default xp=0 hazards don't spam). Called before destroy_projectile at all 5 sites: bullet.nvgt (766 bullet-hit, 1124 splash), glider.nvgt (291 ram), weapon.nvgt (1087 melee, 1474 swing). Braces all balanced. REWARD NOW LIVE.
- **§6 — Docs (projectiles.txt) + 15.0 changelog entry.**

## Notes

Projectile_zone format is UNCHANGED (auto-scaling, no fields). Only the `projectile` line format changes. Watch the block-comment `*/` trap ([[project_angelscript_block_comment_star_slash]]) in any glob-referencing comments. [[project_stability_rules]]: this is a deliberate no-back-compat read_/write_ signature + field-count change.
