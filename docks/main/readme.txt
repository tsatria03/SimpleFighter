Welcome to simple fighter.

Simple fighter is an audio only, blind accessible game built around a map builder. You design audio maps, populate them with characters, weapons, shields, NPCs, doors, hazards, vehicles, zones, and various other entities, and then walk around your maps and use what you've placed. All output is screen reader speech plus HRTF spatial audio, so the game can be played with the screen turned off.

Game features.

The ability to build maps in three different modes (2d, topdown, and 3d), each with its own spatial rules.
The ability to level up, gain experience, and upgrade stats with level up points.
The ability to author your own characters, shields, weapons, NPCs, doors, items, zones, and more by editing plain text info files.
The ability to add environmental effects like HRTF, reverb, echo, lowpass, highpass, phaser, flanger, chorus, and distortion to your maps through effect space zones.
The ability to drop in your own sounds for any entity. Anything that's not in the data folder lives in the sounds folder, and the engine resolves clips by glob, so adding a sound is the wiring.
The ability to bind up to 42 in game slash commands to keyboard slots through the macro system.
The ability to compile maps into encrypted packs that the game falls back to when the decompiled folder is missing.
The ability to rebind any control from inside the game, or edit the key config file by hand.
The ability to record the game's audio and save it as an mp3 file.
The ability to use special equipment such as gliders that let you fly and cloners that duplicate the entities you strike.

Map modes.

Every map is created in one of three modes, set when the map is first built. The mode determines what the axes mean and which keys are available.

2d. The x axis is left and right; the y axis is altitude (up and down). There's no north and south. Body rotation does not apply.
Topdown. The x axis is left and right; the y axis is north and south. There's no altitude axis, so jumping, hooking, jump height changes, and most height related entities are disabled. Body rotation applies, so movement, sonar, spier, and camera keys all rotate with your body.
3d. The x axis is left and right; the y axis is north and south; the z axis is altitude. Body rotation applies. Hooking and jumping are vertical, so they ignore body rotation.

Map bounds and negative coordinates.

Every map sets a minimum and maximum value for each of its axes when it's first created (minx/maxx, miny/maxy, and on 3d maps minz/maxz). The minimum and maximum can be any whole number including negatives, so a 3d map could span from minz minus 5 up to maxz 10 to give you five basement floors below ground level zero plus ten floors above. Type a leading minus sign followed by the number in any of the bound input boxes when creating a new map, and any platform, wall, zone, or other entity you build afterward can also be placed at the negative coordinates - the builder accepts the same minus syntax in its own bound inputs.
Useful patterns. Set minz to a negative value to model basements, sewers, mines, or anything else underground that an elevator could descend to. Set minx or miny to a negative value if you want the spawn point in the middle of a region that extends in both directions instead of starting from a corner. The default fallback spawn point clamps zero into the map's bounds on each axis when the map has no spawnpoint, so a map whose bounds don't include zero will land you at the nearest in-bounds corner instead of dropping you outside the map.

The folder structure.

Data folder.
Split into two siblings: data/main/ holds macro packs and other shared engine config, and data/builder/ holds authored maps (each map's decompiled folder lives at data/builder/maps/decompiled/<name>/ with its main.sif and meta.sif inside data/, plus an assets/ folder for per-map audio overrides).

Docks folder.
Split into two siblings that mirror the data layout: docks/main/ holds the documents the in-game docs menu opens (this readme, the changelog, the todo list, and the credits) and docks/builder/ holds the per-feature reference topics the map builder's help menu serves (one .tp file per topic — around sixty of them, like characters.tp, npcs.tp, and weapons.tp).

Sounds folder.
Holds the game's audio in two forms: a decompiled/ folder you can browse and edit, and a compiled/ folder holding the packed form the game falls back to. Inside decompiled/ are two siblings: main/ (characters, equipments for shields and weapons, keyboards, menus, and a small shared misc folder) and builder/ (per-entity sounds for everything you can drop on a map — kombat NPCs and projectiles, transitions like doors and elevators, transportation like bikes and vehicles, traps, construction tiles, zones, audio entities, and interaction items). The packed form lives in compiled/ as main.spack and builder.spack; a loose decompiled folder always wins over the pack when both are present, so your edits take effect without repacking. Authored info.sif files for each weapon, shield, and npc live in that entity's data/ subfolder, and the corresponding audio clips live in that entity's general/ subfolder. See the packs topic for the full lookup order and how to share packed audio.

Keyboard commands.

These are the default keys the game ships with, not fixed assignments. Every action listed below can be rebound to a different key or key combination from the settings menu, so if your layout doesn't match what's printed here, that's why. The descriptions explain what each action does; the keys are just the out of the box bindings.
Some keys behave differently depending on the map mode. Where a key has a mode dependent meaning, the mode is called out. On topdown and 3d maps, movement, sonar, spier, and camera arrow keys are body relative, meaning the same key always moves in the same direction relative to your character regardless of which way you've rotated.

Movement.

Left arrow. Step left, when pressed or held.
Right arrow. Step right, when pressed or held.
Up arrow. Step forward on the y axis, when pressed or held. On 2d maps this steps up on altitude.
Down arrow. Step backward on the y axis, when pressed or held. On 2d maps this steps down on altitude.
Letter, W. Step up on the z axis (3d maps only), when pressed or held. On 2d and topdown this key does nothing.
Letter, S. Step down on the z axis (3d maps only), when pressed or held. On 2d and topdown this key does nothing.
Page up. Step up on the z axis (3d maps only). Same as W on 3d.
Page down. Step down on the z axis (3d maps only). Same as S on 3d.
Alt. Held while moving, toggles run mode for the duration. The auto run setting flips the default so you walk while alt is held instead.
Spacebar. Jump, when pressed (or held, if auto jump is enabled in the settings menu). Disabled on topdown maps.

Body rotation (topdown and 3d only).

Letter, Q. Rotate your body 45 degrees counterclockwise.
Letter, E. Rotate your body 45 degrees clockwise.

Rotating with Q or E also points your aim where your body is facing, so the next bullet you fire flies that way without you having to set the facing manually.

Manual facing override.

These keys aim your character without moving them, so you can face one direction and fire while still walking another way.

Alt plus shift plus left arrow. Face left.
Alt plus shift plus right arrow. Face right.
Alt plus shift plus up arrow. Face forward on the y axis. On 2d, faces up on altitude.
Alt plus shift plus down arrow. Face backward on the y axis. On 2d, faces down on altitude.
Alt plus shift plus W or page up. Face up on the z axis (3d maps only).
Alt plus shift plus S or page down. Face down on the z axis (3d maps only).

Speed.

Shift plus letter A. Decrease overall movement speed.
Shift plus letter D. Increase overall movement speed.
Shift plus letter F. Reset movement speed to default.

Jump height.

F1. Decrease maximum jump height. Disabled on topdown.
F2. Increase maximum jump height. Disabled on topdown.
F3. Reset jump height to default. Disabled on topdown.

Hooking.

Disabled on topdown. The hook is purely vertical and ignores body rotation.

Letter, F. Toggle hooking upward. Throws the hook if you're not already hooked, or releases it if you are.
Letter, V. Toggle hooking downward.

Transportation.

Board a vehicle, bike, or aircraft by pressing enter while standing on it. Bikes and vehicles are then driven with the normal movement keys; aircraft have their own flight controls below.

Letter, L. Lower an aircraft's landing gear to begin landing.
Shift plus spacebar. Sound a vehicle's or bike's horn.
Shift plus left or right arrow. Steer an aircraft left or right.
Shift plus up or down arrow. Steer an aircraft forward or backward (3d and topdown only).
Left or right arrow. Decrease or increase an aircraft's speed while flying.
Up or down arrow. Raise or lower an aircraft's altitude while flying.

Sonar.

Shift plus F1. Cycle the sonar following mode.
Shift plus F2. Cycle the sonar mode (off, step, loop).
Shift plus F3. Cycle the sonar looping speed.

When the sonar is not following you, you can point it manually:

Letter, J. Face the sonar to your left side. On topdown and 3d this is body relative.
Letter, L. Face the sonar to your right side.
Letter, K. Face the sonar behind you. On 2d this faces the sonar down on altitude.
Letter, I. Face the sonar in front of you. On 2d this faces the sonar up on altitude.
Shift plus letter I. Face the sonar up on the z axis (3d maps only).
Shift plus letter K. Face the sonar down on the z axis (3d maps only).

Spier.

The spier scans the map for objects in a given direction.

Shift plus left arrow. Sweep left. Body relative on topdown and 3d.
Shift plus right arrow. Sweep right.
Shift plus up arrow. Sweep forward on the y axis. On 2d this sweeps the top.
Shift plus down arrow. Sweep backward on the y axis. On 2d this sweeps the bottom.
Shift plus W or shift plus page up. Sweep up on the z axis (3d maps only).
Shift plus S or shift plus page down. Sweep down on the z axis (3d maps only).

Camera.

The camera is a free moving cursor for inspecting the map at a distance. Hold G plus a movement key, or toggle dexterity mode so the camera responds without holding G.

Letter, G plus left or right arrow. Move the camera left or right. Body relative on topdown and 3d.
Letter, G plus up or down arrow. Move the camera forward or backward on the y axis.
Letter, G plus W or page up. Move the camera up on the z axis (3d maps only).
Letter, G plus S or page down. Move the camera down on the z axis (3d maps only).
Letter, G plus letter J. Set a left side selection marker.
Letter, G plus letter L. Set a right side selection marker.
Letter, G plus letter I. Set a forward (or top, on 2d) selection marker.
Letter, G plus letter K. Set a backward (or bottom, on 2d) selection marker.
Letter, G plus shift plus letter I. Set a top selection marker on the z axis (3d maps only).
Letter, G plus shift plus letter K. Set a bottom selection marker on the z axis (3d maps only).
Letter, G plus letter M. Toggle mfwc mode (camera focus).
Letter, G plus letter Y. Toggle dexterity mode (camera responds without holding G).
Letter, G plus letter R. Announce the tile, hazard, player presence, coordinates, and direction at the camera's current position.
Letter, G plus letter T. Play the tile sound at the camera's current position.
Letter, G plus semicolon. Speak all selection markers that have been set.
Letter, G plus apostrophe. Clear all selection markers.

Combat.

Control. Fire the currently selected weapon. Held control auto fires for weapons that support it. The bullet flies along whichever axis your character is currently facing.
Letter, R. Reload the current weapon.
Letter, X. Announce ammo for the current weapon.
Letter, T. Toggle reflection mode (for weapons that support it).

Inventory.

Tab. Cycle forward through inventory items.
Shift plus tab. Cycle backward.
Shift plus enter. Use the currently focused inventory item.
Alt plus letter I. Open the inventory menu.

Healing and shields.

Backslash. Toggle health restoration on or off.
Right bracket. Toggle shield strength restoration on or off.
Letter, O. Raze or wear a drawn shield. In one shield mode, hold O to keep the shield up; releasing lowers it.

Status and information.

Letter, C. Speak your current location and the tile being walked on.
Letter, H. Speak your health and lives.
Letter, Y. Speak your stamina.
Letter, M. Speak your shield strength.
Letter, N. Speak the direction and distance to the object you're tracking. Tracking is started from the object viewer.
Shift plus letter N. Stop tracking the current object.
Left bracket. Speak your total kills.
Shift plus left bracket. Drop the inventory item currently in focus.
Letter, Z. Toggle zone announcements on or off.
Alt plus letter Q. Speak the text zone you're currently standing in.

Menus.

Alt plus letter W. Open the weapons menu.
Alt plus letter S. Open the shields menu.
Alt plus letter E. Open the object viewer.
Shift plus alt plus letter E. Open the combat log viewer.
Shift plus letter H. Open the command help menu.
Shift plus letter V. Open the points menu.
Letter, B. Open the builder menu (disabled on compiled maps).
Letter, U. Open the map editor menu (disabled on compiled maps).
Alt plus letter R. Open the recording menu, where you can capture the game's audio and save it.

System.

Slash. Open the command prompt. Type a slash command and press enter to run it. Multiple commands can be chained with semicolons.
Enter. Interact with whatever is at your feet, including doors, signs, clocks, calendars, passages, dialogs, and menu items.
Letter, P. Pause or resume the game.
Escape. Exit the current map and return to the last menu.

Macros (script keys).

The macro system gives you 42 keyboard slots that each fire a slash command, with optional cooldown and spoken confirmation.

Backtick, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, minus, equals, backspace. Bank 1 (14 slots).
Shift plus any of the above. Bank 2 (14 slots).
Shift plus alt plus any of the above. Bank 3 (14 slots).

Macros are configured per pack and selected with the slash macset and slash mc commands.

Customizing audio.

Audio lives directly under sounds/decompiled/main/ and sounds/decompiled/builder/. The sections below list the clip names the engine looks for in each category. The lookup is glob based, so numbered variants (taunt1.ogg, taunt2.ogg, taunt3.ogg) are all picked up under the same base name (taunt.ogg). Add as many variants as you like and the engine will pick one at random.

Character general (sounds/decompiled/main/characters/<name>/general/).

bleed.ogg: Played when your character bleeds.
break.ogg: Played when your character breaks a bone.
buy.ogg: Played when your character purchases an upgrade.
change.ogg: Played when your character adjusts a setting like speed or jump height.
crit.ogg: Played when your character takes critical damage.
death.ogg: Played when your character dies.
fail.ogg: Played when a broken bone starts to kill your character from pain.
fall.ogg: Played when your character starts falling.
give.ogg: Played when your character gives themselves an item.
healing.ogg: Played in a loop while your character is healing.
healstart.ogg: Played when your character starts healing.
healstop.ogg: Played when your character stops healing.
hurt.ogg: Played when your character takes damage.
inv.ogg: Played when your character cycles through their inventory.
jump.ogg: Played when your character starts jumping.
kill.ogg: Played when your character kills an entity.
lev.ogg: Played when your character levels up.
life.ogg: Played when your character loses a life.
pain.ogg: Played when a broken bone hurts your character while they move.
pause.ogg: Played when your character pauses the game.
plummet.ogg: Played in a loop while your character is falling.
resume.ogg: Played when your character resumes the game.
rotate.ogg: Played when your character rotates with Q or E.
take.ogg: Played when your character returns an item to their inventory.
turn.ogg: Played when your character turns to face a different direction.

Character map (sounds/decompiled/main/characters/<name>/map/).

camair.ogg: Played when the camera passes over an air tile.
camclear.ogg: Played when camera selection markers are cleared.
camhazard.ogg: Played when the camera detects a hazard.
camplayer.ogg: Played when the camera lands on the player.
camset.ogg: Played when a camera selection marker is set.
camtile.ogg: Played when the camera passes over a normal tile.
camwall.ogg: Played when the camera detects a wall.
delete.ogg: Played when something is deleted from the map in the builder.
finish.ogg: Played when you finish a map through a travelpoint.
hookcatch.ogg: Played when the grappling hook catches.
hookclimb.ogg: Played in a loop while climbing on the hook.
hookdrop.ogg: Played when the hook fails to catch.
hookrelease.ogg: Played when the hook is released.
hookthrow.ogg: Played when the hook is thrown.
load.ogg: Played when a map is loading.
move.ogg: Played when something is moved on the map in the builder.
sonair.ogg: Played when sonar detects air.
sondown.ogg: Played when sonar detects a staircase going down.
sonhazard.ogg: Played when sonar detects a hazard.
sontile.ogg: Played when sonar detects a tile.
sonup.ogg: Played when sonar detects a staircase going up.
sonvanish.ogg: Played when sonar detects a vanishing platform.
sonwall.ogg: Played when sonar detects a wall.
start.ogg: Played when a map starts.
stop.ogg: Played when a map stops.
update.ogg: Played when the map is edited live in the builder.

Keyboards (sounds/decompiled/main/keyboards/<theme>/).

cap.ogg: Played when a capital letter is typed.
delete.ogg: Played when a character is deleted.
return.ogg: Played when enter is pressed in a text field.
space.ogg: Played when the space bar is pressed.
type.ogg: Played when any other character is typed.

Menus (sounds/decompiled/main/menus/<theme>/).

click.ogg: Played when scrolling through menu items.
close.ogg: Played when a menu closes.
edge.ogg: Played when a menu hits a boundary.
error.ogg: Played when a menu fails to open.
enter.ogg: Played when a menu item is selected.
music.ogg: Played in a loop as menu background music.
open.ogg: Played when a menu opens.
speaker.ogg: Played by the speaker test option in the main menu.
wrap.ogg: Played when a menu wraps from end to start.

Misc (sounds/decompiled/main/misc/).

gamestart.ogg: Played when the game is unfrozen.
gamestop.ogg: Played when the game is frozen.
menu.ogg: Played as a generic menu cue.
punch.ogg: Played as a generic impact cue.
switchoff.ogg: Played when a feature toggle (zones, tracking, etc.) is switched off.
switchon.ogg: Played when a feature toggle is switched on.
toggleoff.ogg: Played when a runtime toggle (camera dexterity, mfwc, etc.) is switched off.
toggleon.ogg: Played when a runtime toggle is switched on.
trackon.ogg: Played when an object starts being tracked.
trackoff.ogg: Played when tracking stops.
tracked.ogg: Played when a tracked object is announced.
tracking.ogg: Played in a loop while an object is being tracked.

Shields (sounds/decompiled/main/equipments/shields/<name>/general/, with stats at sounds/decompiled/main/equipments/shields/<name>/data/info.sif).

break.ogg: Played when the shield breaks.
draw.ogg: Played when the shield is drawn.
hit.ogg: Played when the shield is hit.
loop.ogg: Played in a loop while the shield is worn.
remove.ogg: Played when the shield is put away.
wear.ogg: Played when the shield is worn.

Weapons (sounds/decompiled/main/equipments/weapons/<category>/<name>/general/, with stats at sounds/decompiled/main/equipments/weapons/<category>/<name>/data/info.sif).

block.ogg: Played when a weapon reflects an attack.
draw.ogg: Played when the weapon is drawn.
empty.ogg: Played when a non melee weapon runs out of ammo.
fire.ogg: Played when the weapon fires.
hit.ogg: Played when the weapon hits a target.
loop.ogg: Played in a loop while the weapon is in use.
off.ogg: Played when reflection mode is turned off.
on.ogg: Played when reflection mode is turned on.
ping.ogg: Played when a non melee weapon finishes reloading.
ref.ogg: Played in a loop while reflection mode is active.
reload.ogg: Played while a non melee weapon is reloading.
rico.ogg: Played when a bullet ricochets.
shell.ogg: Played when a non melee weapon drops ammo shells.

NPCs (sounds/decompiled/builder/kombat/npc/<group>/<name>/general/, with stats at sounds/decompiled/builder/kombat/npc/<group>/<name>/data/info.sif).

death.ogg: Played when the NPC dies.
heal.ogg: Played when the NPC heals.
hit.ogg: Played when the NPC strikes the player.
hurt.ogg: Played when the NPC takes damage.
launch.ogg: Played when the NPC launches a minion.
life.ogg: Played when the NPC loses a life.
remove.ogg: Played when the NPC is removed from the map.
spawn.ogg: Played when the NPC spawns.
step.ogg: Played when the NPC moves a step.
taunt.ogg: Played when the NPC taunts the player.
tel.ogg: Played when the NPC teleports.

Projectiles (sounds/decompiled/builder/kombat/projectiles/<name>/).

death.ogg: Played when the projectile is destroyed.
hit.ogg: Played when the projectile hits a target.
hurt.ogg: Played when the projectile takes damage from a hit.
loop.ogg: Played in a loop while the projectile is in flight.

Items (sounds/decompiled/builder/interaction/items/<group>/<name>/).

break.ogg: Played when the item breaks.
fire.ogg: Played when the item is used.
get.ogg: Played when the item is picked up.
hit.ogg: Played when the item makes contact.
loop.ogg: Played in a loop while the item is active.

Map objects (sounds/decompiled/builder/<group>/<entity>/<name>/).

The builder folder holds clips for every entity type that can be placed on a map. Each entity type lives in a group folder by purpose (construction, interaction, transitions, transportation, traps, zones, audio, misc), and inside it the per-instance clips are organized by name. Below is the typical clip set for each entity type, each shown with its folder beneath sounds/decompiled/ — an entry written as builder/... is found at sounds/decompiled/builder/.... As with the rest of the pack the lookup is glob based, so adding extra clips with the same base name is fine.

aircrafts (builder/transportation/aircrafts/): alarm, appear, beacon, change, crash, death, enter, flight, gear, hurt, land, loop, pass, start, turn.
belts (builder/construction/belts/): loop.
bikes (builder/transportation/bikes/): per-bike misc and platform clips.
bombs (builder/traps/bombs/): fall, plus per-bomb explosion clips.
calendars (builder/interaction/calendars/): break, loop, press.
cameras (builder/traps/security cameras/): alarm, alert, death, hurt, turn.
checkpoints (builder/construction/checkpoints/): get, loop.
clocks (builder/interaction/clocks/): break, loop, press.
doors (builder/transitions/doors/): per-door close, dest, lock clips named by the door variant.
elevators (builder/transitions/elevators/): per-elevator beep, close, loop clips.
fires (builder/traps/fires/): hit, loop.
floor breakers (builder/traps/floor breakers/): remove, spawn.
force fields (builder/traps/force fields/): hit, off, on.
hazards (builder/traps/hazards/): fall, loop.
heal zones (builder/zones/heal zones/): heal, take.
lifts (builder/transitions/lifts/): loop.
mines (builder/traps/mines/): explode, hit, light, loop, spawn.
moving platforms (builder/construction/moving platforms/): loop.
platforms (builder/construction/platforms/): death, fall, hurt, land, step.
safe zones (builder/zones/safe zones/): in, out.
sensors (builder/interaction/sensors/): loop, on, off.
signs (builder/interaction/signs/): break, loop, press, step.
spikes (builder/traps/spikes/): death, loop.
story zones (builder/zones/story zones/): close, copy, open, scroll.
switches (builder/interaction/switches/): loop, press.
teleporters (builder/transitions/teleporters/): loop, move.
time bombs (builder/traps/time bombs/): land, tick.
vanishing platforms (builder/construction/vanishing platforms/): loop.
vehicles (builder/transportation/vehicles/): beacon, death, hit, horn, hurt, motor, turn.
walls (builder/construction/walls/): bump, death, hurt.

Map music and ambience (data/builder/maps/decompiled/<map>/assets/builder/audio/musics/ and data/builder/maps/decompiled/<map>/assets/builder/audio/sources/).
Drop clip folders into a map's musics/ or sources/ subfolder and the audio entity builders (sound source, sound ambience, timed source, timed ambience, excludable source, excludable ambience, and speaker) make them available to place on that map. Each leaf folder is one named clip set the entity picks up by name; the lookup is glob based, so numbered variants of a clip all play under the same base name.
