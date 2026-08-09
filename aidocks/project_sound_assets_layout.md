---
name: project_sound_assets_layout
description: sf/sounds/ folder structure — decompiled/ (loose, author-editable) vs compiled/ packs (main.spack/builder.spack), the main/ vs builder/ split, and glob-based clip discovery.
metadata:
  type: project
---

`sf/sounds/` is gitignored and downloaded on first run by `downloadsounds()` in src/sf.nvgt if missing — don't commit clips (see [[project_repo_hygiene]]). It is split into two top-level siblings:

- **decompiled/** — the loose-folder form authors edit.
- **compiled/** — the encrypted pack form the shipped game reads (`sounds/compiled/main.spack` and `sounds/compiled/builder.spack`).

Decompiled folders win on lookup; the packs are the fallback. There is no per-pack indirection layer above this — the old `sounds/<pack>/` selector and `soundpack` global were removed. Players customize audio by dropping clips into the relevant per-entity subfolder. Clips are discovered by **glob**, so there's no sound-name list — adding a clip is the wiring, and numbered variants (taunt1/taunt2/taunt3) all resolve under the same base name (taunt) and play at random.

## decompiled/main/ — shared engine assets

- **characters/<character>/** — per-character bundle. `data/main.sif` stat block (see [[project_game_data_layout]]); `general/`, `map/`, and the bare folder hold clips resolved against `main/characters/<char>/...`.
- **equipments/shields/<name>/** — stat info.sif in `data/`, clips in sibling `general/` (draw, wear, remove, hit, break1/break2).
- **equipments/weapons/<category>/<name>/** — stat info.sif in `data/`, clips in sibling `general/`, varying by weapon (draw, fire, hit, loop1..6, reload1..3, rico, empty, ping, block1..3, ref, on/off).
- **keyboards/<theme>/, menus/<theme>/, misc/** — theme- and UI-keyed audio resolved by `get_pack_sound("main/...")` glob lookups.

## decompiled/builder/ — per-entity map-object assets

- **kombat/npc/<group>/<name>/** — stat info.sif in `data/`, clips in `general/` (at minimum spawn, hurt, death, taunt, life, tel, launch, heal_1..3; many add step1..N, hit1..N).
- **kombat/projectiles/<name>/** — projectile sound bundles for `launch_*` AI behavior.
- **construction/, transitions/, transportation/, traps/, zones/, audio/, interaction/, misc/** — per-entity map-object audio resolved by `get_pack_sound("builder/...")` and `get_map_sound("builder/...")` glob lookups.

The full per-entity clip-name catalogue (which clips each entity type looks for) lives in the player-facing `sf/docks/main/readme.txt` under "Customizing audio" — that's the authoritative list, kept in sync for players. The runtime audio model (pools, HRTF, looping-slot invariant) is in [[project_audio_model]].
