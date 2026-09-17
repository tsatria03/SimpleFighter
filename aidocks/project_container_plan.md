---
name: project_container_plan
description: Feature plan (candidate 15.0, DESIGN MOSTLY SETTLED, NOT built) — a new "container" builder trap: a roaming trap that homes at the player like a fire, and when it reaches them, catches them, carries them up to a configurable drop height, hovers, then drops them so the normal fall system hurts/kills them. Player must destroy it (weapons) before or during the catch. Models: fire (seek), teleporter (coordinate move), security_camera (health+level+xp reward).
metadata:
  type: project
---

**STATUS: DESIGN MOSTLY SETTLED, NOT built (2026-09).** Settle remaining opens with the dev before building ([[feedback_confirm_before_implementing]]). New builder entity in the **traps** category.

## Concept

A container is a roaming trap. It rolls around homing at the player (fire-style). When it reaches the player's tile it CATCHES them: the player is locked in place (can't walk) but can still aim + fire. It carries the player UP to a configurable **drop height**, HOVERS there for a configurable time, then DROPS them — releasing them so the normal player fall system does the damage (the container itself deals no direct damage; the fall does). The player's goal is to destroy it with weapons while it's rolling (so they're never caught); destroying it mid-carry still releases them to fall from the current height. One-shot: after it drops the player, it removes itself.

## Settled decisions

- **Map modes: 2d + 3d only.** Topdown has no height/fall, so containers aren't offered there. On 3d the lift is along z; on 2d "up" is the y axis (player fall on 2d is along y). Drop height default = maxz (3d) / maxy (2d).
- **After drop: ONE-SHOT** — it plays `remove` and despawns. Each container catches once.
- **While caught: no movement, but aim + fire work and every shot auto-hits the container.** Reuse the capability-flag hold pattern ([[project_capability_flags_per_frame_reset.md]]): hold `moveable`=false each frame while caught (movement is rewritten every frame by update_character_settings), keep `fireable`=true; while caught, any fire the player makes damages the container directly (no aim/collision needed, since it's co-located on the player's tile — normal bullet muzzle-exemption would otherwise make a same-tile hit impossible).
- **Roaming: LIVE LEASH (NPC-style), matching the now-fixed fire/teleporter/wind.** `spotted` recomputed every tick from the seeing-range box; chases only while the player is in range, stops (stays put) when they leave, re-engages when they return. NOT the old latch.
- **Passes through walls** (like fire/teleporter/wind) — homes straight at the player, ignores terrain. Escape by outrunning past the seeing range, not by hiding behind a wall.
- **Health: fixed author-set field** (like camera/spikes/walls). Destroyable by weapons while rolling (add to the bullet + weapon melee hit loops the same way `sucams` are — see bullet.nvgt sucams loop ~593 and weapon.nvgt).
- **Reward on destruction: level + xp fields, camera-style.** On death: if `xpmod >= 1`, `xp += containerxp * containerlevel * xpmod`, log "N experience gained. Defeated <type> level N." No kills-counter bump (not a creature). An author who wants a pure hazard sets xp to 0.
- **Hover time: configurable field** (ms).
- **Drop height: configurable, min 10** (reject "Drop height cannot be lower than 10."), default = maxz (3d) / maxy (2d).

## Sounds (builder/traps/containers/<type>/)

spawn (spawn, shared with other objects) · loop (rolling on ground) · catch (grabbed you, lift begins) · flight (loop while carrying up) · hover (holding at top, up to several sec) · drop (release — plays STATIONARY) · remove (despawn / after-drop — plays 3d/positional) · hurt (you hit it) · death (destroyed).

SOUND SET CONFIRMED SHIPPED (2026-09): 2 variants (container, container2); all 9 clip types present in both; `hurt` is MULTI-VARIANT (hurt1-5 in container, hurt1-2 in container2) so `*hurt*` glob picks one at random per hit (like npc/character hurt). No untapped clips — key map covers everything, nothing deferred.

## Gallery ([[project_builder_gallery_plan]])

The container must be added to the builder gallery too — one entry in `gallery_types_for()` (`src/includes/builder/misc/gallery.nvgt`), traps category, a single-level type `containers` (path `traps/containers/<variant>/`), alphabetized among the 10 existing traps types. The SAME audition key map must be wired into THREE places: (1) the build form's `form.monitor()` preview block, (2) this gallery clip table, (3) containers.txt "Auditioning sounds" section. Dev picks the keys (not auto-assigned). PROPOSED map (Space=main/ambient per convention; Ctrl+letters reuse cross-element mnemonics — H=death, N=spawn, U=hurt, R=remove, D=drop like camera/npc/spikes/floor-breaker): Space `*hurt*` · Ctrl+L `*loop*` (rolling) · Ctrl+N `*spawn*` · Ctrl+C `*catch*` · Ctrl+I `*flight*` · Ctrl+O `*hover*` · Ctrl+D `*drop*` · Ctrl+R `*remove*` · Ctrl+H `*death*`. (Space=hurt + Ctrl+L=loop mirrors the camera/fire/spike/wind trap convention; Ctrl+F/G/A avoided — form-reserved on a focused list; Ctrl+I matches aircraft's flight clip.) APPROVED by dev 2026-09.

## Fields / form (control order per [[feedback_builder_form_control_order]]: inputs → lists → checkboxes → buttons)

Inputs: x, y, (z), x seeing range (default maxx), y seeing range (default maxy), (z seeing range default maxz), speed, health, level, xp, drop height (default maxz/maxy, min 10), hover time.
Lists: container sound (none + folders).
Checkboxes: move on x, move on y, (move on z) — like fire.
Buttons: okay, cancel.

## On-disk format (modeled on camera + fire)

`container x y (z) xrange yrange (zrange) speed health level xp dropheight hovertime containertype movex movey (movez)`
Length: 2d/topdown = 14 tokens, 3d = 17 (z after y, zrange after yrange, movez after movey). Semantic error keyed on length (like camera 11/13, fire 9/12). Tier 1 lenok + Tier 2 `container_semantic_error` (coords, number ranges, numbers for speed/health/level/xp/dropheight/hovertime, sound-exists-or-none, bool move flags). Alphabetize `container` in the builder traps menu ([[feedback_alphabetize_builder_entities]]) and standard scaffolding (class, containerloop, spawn_/despawn_/destroy_all_/build_/read_/write_/*_semantic_error).

## Build sections (present up front, implement on go-ahead per [[feedback_describe_dont_show_code]])

Fine-grained split (dev's call, 2026-09), one component per section:

- **§1 — Class + globals + lifecycle helpers. [DONE 2026-09]** The `container` class (all fields), globals (`containerpool`, `containers[]`, phase constants), and `spawn_/despawn_/destroy_all_container`. Auto-included via `#include"builder/traps/*"`. No collisions. Nothing calls it yet.
- **§2 — Reader + writer. [DONE 2026-09]** `read_container` + `write_container` in container.nvgt; parser keyword dispatch added to map_parser.nvgt (`sd[0]=="container" && (sd.length()==14 || sd.length()==17)`, next to the wind branch). read walks the o-offset past optional 3d fields (z/zrange/movez), passes health as both current+max to spawn; write appends the line with the zsrc/zrng/zmov 3d conditionals. Field counts 14 flat / 17 3d.
- **§3 — Build form** (+ alphabetized traps entry in the build menu, map_menu.nvgt). Fields below; control order per [[feedback_builder_form_control_order]]; drop-height min-10 validation + max-height default.
- **§4 — `containerloop()` runtime + game-loop wiring.** The roam/catch/lift/hover/drop state machine (below); register `containerloop()` in the game loop; wire `destroy_all_containers()` into the map-clear path (where `destroy_all_fires` is called); capability-flag hold + fallcheck suppression while caught ([[project_capability_flags_per_frame_reset]]). Sounds spawn/loop/catch/flight/hover/drop/remove. NO weapon-destroy/reward yet. Testable: it hunts/catches/lifts/hovers/drops you, you take the fall, it removes itself.
- **§5 — Destroy + reward.** Add container to the bullet + weapon-melee (+scadder splash) hit loops (camera `sucams` pattern): hurt on hit, health down, death at zero, camera-style xp reward + "Defeated" log; auto-hit while caught; release-if-caught (fall from current height). Testable: shoot while rolling → dies+xp; shoot mid-lift → released+falls+xp.
- **§6 — spawn/despawn + build/unbuild command wiring ([[project_unbuild_despawn_plan]]).** Add `container` to the `/spawn` and `/build` branches in `command_parser.nvgt` (parse fields → `spawn_container` / `write_container`+reload), the `despawn_entity` dispatch (→ `despawn_container`, already §1), and `normalize_buildtype` (container→container, trivial); verify `/unbuild` (generic line-delete-by-keyword) recognizes it. Depends only on §1+§2. NOTE: `containers[]` is nullable (despawn + death null slots) so EVERY loop over `containers.length()` across the codebase must guard `if(@containers[i]==null)` — I write all container loops so I guard them; only add container to spier/effect_space if a later section deliberately does (guard there too). Feedback: /build "Map updated." (decompiled-only); /despawn silent success (plays `remove` at position), "There's no container to remove." on miss.
- **§7 — Map error Tier 1.** Register the `container` keyword + expected field counts (14 flat / 17 3d) in the error checker's recognized-entity/length table.
- **§8 — Map error Tier 2.** `container_semantic_error` (coords, number ranges, numbers for speed/health/level/xp/dropheight/hovertime, sound-exists-or-none, bool move flags), wired into `entity_semantic_error` dispatch. Testable: a malformed container line reports the right error in the Map errors box.
- **§9 — Gallery.** The `containers` type in `gallery_types_for()` (traps category, alphabetized), key map above.
- **§10 — Dock updates.** Build-form previews already in §3; `containers.txt` help topic (incl. "Auditioning sounds" with the SAME keys), add `container` (alphabetized) to the element list in maps.txt, one 15.0 changelog entry.

(Ordering flexible after §2; runtime §4/§5 need §2+§3 to be testable. spawn/despawn/destroy_all trio lives in §1 per dev.)

## State machine (containerloop)

- **ROLLING:** live-leash seek (spotted = in-range each tick); home per move flags at 1 tile/speed; play `loop`. Guard the catch like fire (`paused==0 && !glider_engine_on`, and skip while invehicle/onbike/inplain). On reaching the player's tile → play `catch`, freeze player movement, phase=FLIGHT.
- **FLIGHT:** player frozen (movement held false each frame), fire allowed + auto-hits container. Rise me.z (3d) / me.y (2d) toward drop height at 1 tile/speed, container tracks the player's tile; SUPPRESS the player fallcheck while carried (glider_engine_on is the precedent for a z-hold that suppresses falling). Play `flight` loop. At drop height → phase=HOVER, restart hover timer, play `hover`.
- **HOVER:** hold for hovertime, player still frozen + can fire. When elapsed → phase=DROP.
- **DROP:** play `drop` (stationary), release player (restore capability flags, stop suppressing fallcheck) → normal fall system takes over; play `remove` (3d); null the container (one-shot).
- **DESTROYED (health<=0, any phase):** play `death`, award xp (xpmod>=1), "Defeated" log; if the player was caught, release them (they fall from current height); null it.

## Open items — ALL RESOLVED (2026-09)

1. **Rise cadence:** RESOLVED — reuse the `speed` field (1 tile of lift per speed interval); no separate flight-speed field.
2. **Catch guards:** RESOLVED — only catches the player on foot; NO catch while gliding / in a vehicle / on a bike / inplain (mirrors fire's contact guard, and just keeps rolling under them).
3. **Destroyable-while-rolling wiring:** RESOLVED — destroyed by weapons exactly like a security camera: add the container to the bullet + weapon-melee (+ scadder splash) hit loops the same way `sucams` are wired.

Design is fully settled; next step is the build-section breakdown (present all sections up front per [[feedback_describe_dont_show_code]], then implement on the dev's go-ahead).

## Reference files

`src/includes/builder/traps/fire.nvgt` (seek + kill-on-contact structure, live-leash now), `src/includes/builder/transitions/teleporter.nvgt` (coordinate move), `src/includes/builder/traps/security_camera.nvgt` (health+level+xp reward, form field layout, 11/13 length semantic). Player fall system: `fallcheck()` in map.nvgt (~1023). Capability-flag hold: [[project_capability_flags_per_frame_reset]]. Docs topic: containers.txt; one 15.0 changelog entry when built.
