---
name: project_game_data_layout
description: sf/data/ layout — authored maps under builder/, and main/ config (keyboard.ini bindings, macro packs). The info.sif-is-the-contract rule for characters/shields/weapons/NPCs.
metadata:
  type: project
---

All game content is authored as plain-text info.sif files that the engine scans — the engine never hardcodes content. Code reads these cwd-relative as `data/...` (see [[project_path_conventions]]). Two sibling folders under `sf/data/`: `builder/` and `main/`.

## sf/data/builder/maps/

- **decompiled/<name>/data/** — authored maps. Always contains main.sif (the entity list — see [[project_map_format]]) and meta.sif (owner, description, created date, modified date). Per-map sound assets live under the parent `decompiled/<name>/` in kombat/, objects/, soundtracks/, etc. folders resolved by `get_map_sound(...)` lookups.
- **compiled/<name>.map** — encrypted pack form built from a decompiled folder. `load_map()` falls back here when the decompiled copy is absent. Intentionally empty in source control (release artifact).

## sf/data/main/

- **config/keyboard.ini** — the key_config bindings (sections are decorative; the loader reads every `action=value` line). Read at startup by `load_controls()`.
- **macros/** — scriptkey-bank command macros loaded by `load_macros()` and triggered from game_input.nvgt via `ordered_scriptkeys` (14 keys: backtick, 1–0, -, =, backspace) across three banks (plain / Shift / Shift+Alt) — 42 slots total. Each info.sif here is a one-macro-per-line table `<cooldown_ms> <speak_bool> <command>` (e.g. `4000 true /rt` runs /rt with a 4 s cooldown and a spoken confirmation). The only subfolder shipped is **default/<theme>/info.sif** (currently just classic) — the seed bank a fresh player starts from. Players define their own packs through /macset / /mc, so adding a new entity/weapon/item no longer requires a macro file edit.

## The info.sif contract (characters / shields / weapons / NPCs)

Authored content stat blocks live under `sf/sounds/decompiled/...` (see [[project_sound_assets_layout]]), not `sf/data/`, but the parsing rule is the same everywhere: the info.sif **is** the contract. Every numeric field is read by name in the parser, missing fields fall back to engine defaults, and unknown fields are silently ignored. Folder name = the identifier used in macros (`/dr <category> <name>`) and in the character/NPC builders. There is no data-file versioning — see [[project_deferred_concerns]]. Field-name spelling follows the spaces-not-underscores rule in [[project_stability_rules]].

- **Characters** — `characters/<character>/data/main.sif` parsed by `charparse()` (fields: weapon type, weapon type2, attack, defence, points, fall modifier, health, stamina, kills, lives, level, level modifier, experience, experience modifier, experience required); `data/attacks.sif` and `data/bodyparts.sif` are flat one-token-per-line word lists for randomized flavor text.
- **Shields** — 42 shields, `equipments/shields/<name>/data/info.sif`, key=value. Fields: defence, wear mode (0/1), weight, shield strength, shield passthrough, unlock level.
- **Weapons** — 271 weapons across archery/, artillery/, explosive/, melee/. `equipments/weapons/<category>/<name>/data/info.sif`. Common fields: damage, fire mode (0=single/1=auto), x range, y range, z range, bullet speed, repeat time, spam time, weight, ammo, loaded ammo, max ammo, unlock level, stun mode. Category folder name must match `weapon type` in a character's info.sif; leaf folder name must match `weapon type2`.
- **NPCs** — 187 types across animals/, bosses/, helpers/, humans/, robots/, specials/, zombies/. `kombat/npc/<group>/<name>/data/info.sif`. Fields group into: **Ranges** (x/y/z attack range, x/y/z sight range, patrol x/y/z range — accept literal keywords minx/maxx/miny/maxy/minz/maxz, comma-pairs, or the literal `terrain` token that auto-fits patrol bounds to contiguous walkable terrain), **Combat/progression** (health, lives, attack, defense, level, xp, fire speed, rest heal time, move speed, taunt delay), and **AI behavior** (chase mode, chase time, teleport time, targets, attacking, move x/y, drop item, tel x/y, ambient heal, ambient heal time, hit and run, flee time, flee speed, terrain, provoke speed, chase terrains, use steps/use falls, launch path, launching, launch category, launch subtype, launch time).
