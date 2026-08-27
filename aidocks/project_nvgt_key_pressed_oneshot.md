---
name: project_nvgt_key_pressed_oneshot
description: NVGT key_pressed() is one-shot — consumed on the first read each frame, so never read the same key in two separate if-checks in one loop iteration.
metadata:
  type: project
---

In the pinned nvgt engine, `key_pressed(KEY_X)` is **consumed on the first read** each frame. Reading the SAME key in two separate `if` checks in one loop iteration means the second check always sees false.

**Why:** a common trap when one physical key drives multiple behaviors (modifier combos, mode branches). Example from a sibling NVGT game: an auto-run feature added `if(key_pressed(KEY_R) and alt_is_down())` right before an existing `else if(key_pressed(KEY_R) and !in_game)` check — with Alt up, the first read ate the R press, so plain R silently did nothing.

**How to apply:** when one physical key drives multiple behaviors, read it **once** into the outer `if` and branch inside — `if(key_pressed(KEY_R)) { if(alt_is_down()) ...; else if(!in_game) ...; }` — not two sibling `if`s that each call `key_pressed(KEY_R)`. Different keys per check are fine. In this codebase most input routes through the global `controls` (a key_config) rather than raw `key_pressed`, but raw `key_pressed`/`key_down` still appears (e.g. the camera-mode `key_up(KEY_G)` gates in `game_handlers.nvgt`), so the rule applies wherever a raw call is duplicated. Related: [[project_angelscript_reserved_words]], [[project_stability_rules]].

**Corollary — a form's confirm keypress bleeds into the game unless you wait for release.** The audio form (`form.nvgt`) activates buttons with `key_repeating(KEY_SPACE)`/`key_repeating(KEY_RETURN)`. Pressing Space on okay/cancel closed the form, and when the game loop resumed, `handle_jump_keys` (`game_handlers.nvgt:702`) saw the still-held/just-pressed Space and jumped. **A `key_pressed(KEY_SPACE)` drain at the form's button site did NOT fix it** (dev tested 2026-08): the game reads jump through `controls` (`key_config.nvgt`), whose `_capture_key_state` calls `key_pressed(k)` **fresh once per resume frame** — a drain on an earlier form frame doesn't touch that; and with **autojump on** the game reads `action_down` = `key_down`, which a `key_pressed` drain can't affect at all. What DID work: at the button-activation sites in `form.nvgt`, spin until the key physically lifts — `while (key_down(KEY_SPACE)) wait(5);` (space handler), `while (key_down(KEY_RETURN) || key_down(KEY_NUMPAD_ENTER)) wait(5);` (enter handler) — so control only returns to the game with the key already up. General rule: to stop a UI confirm key from bleeding into a game action, **wait for release** before handing control back; draining `key_pressed` is not enough when the consumer re-reads the key state on its own frame or uses `key_down`.
