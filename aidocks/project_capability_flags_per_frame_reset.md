---
name: project_capability_flags_per_frame_reset
description: Load-bearing gotcha — update_character_settings() rewrites the whole player capability-flag set (fireable/moveable/jumpable/turnable/cammable/speedable/spiable/etc) to allowed EVERY frame from the character-blocker zones, and runs before stuncheck() in the game loop, so any transient flag change (a stun, a temporary freeze) only lasts one frame unless it is re-asserted AFTER update_character_settings each frame.
metadata:
  type: project
---

**The trap (root-caused & fixed in 15.0).** For a long time the player bone-stun "looked" like it worked — the pain sound + "Ouch! Your X hurts!" message fired — but never actually froze the player. Cause: `update_character_settings()` (character_blocker.nvgt) rewrites the ENTIRE player capability-flag set every frame from the character-blocker zones:

```
fireable = !is_chsetting_blocked("firing");   // no blocker => true again
moveable = ...  jumpable = ...  turnable = ...  cammable = ... etc.
```

It runs at `game.nvgt:54`, BEFORE `stuncheck()` (game.nvgt:78) and before `game_input()`. So `stun_target()` setting `fireable=false` was wiped back to true one frame later. `stuncheck()` historically only RELEASED a stun on timer expiry; it never HELD the flags down during the stun, so every stun (bones, falls, weapon hits, projectiles) lasted ~1 frame for capability purposes and never froze the player on foot. The old "can't fire while bones broken" gate (14.4) existed precisely because the stun-based freeze didn't stick.

**The rule this implies.** Any transient capability-flag change (a freeze, a stun, a lockout) that must persist for more than one frame has to be **re-asserted every frame AFTER `update_character_settings()`** — setting it false once is not enough, the per-frame reset clobbers it. The natural place is a per-frame check (like `stuncheck()`), not the one-shot event that starts the effect.

**How 15.0 fixed it.** `stuncheck()` now HOLDS the stun each frame (re-asserts the 8 flags false until the timer expires), which wins because it runs after `update_character_settings()`. The player also got a dedicated stun state (`me_stunned`/`me_stuntimer`/`me_stundir`) separate from the `stunned`/`stuntimer`/`stundir` globals — those globals are overloaded as the release timer for NPC/projectile stuns (set inline in weapon.nvgt / bullet.nvgt / projectile.nvgt), so without the split the hold-branch would have frozen the player whenever they stunned an enemy. `me_stunned` is cleared on respawn/life-loss (`charparse`, `player_lose_life`, `bonecheck`'s bone-death branch) so a lingering stun can't freeze a fresh life. See [[project_stability_rules]] (capability flags gate input as a set).

**Note:** `stun_target()` is only ever called with `"me"` — its animal/boss/etc and projectile branches are effectively dead (NPC/projectile stuns are done inline at the hit sites). The global `stunned` is never read as gameplay state outside stunner.nvgt; the freeze works purely through the capability flags.
