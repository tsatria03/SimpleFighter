---
name: feedback_error_dlg_sound
description: Error dlg() dialogs (message starts with "Error") pass dlgsound:true so the themed error.ogg plays; do the same for new ones.
metadata:
  type: feedback
---

Error `dlg()` dialogs — any whose message strictly starts with "Error" (`dlg("Error. …")`, also "Error:", "Error!", "Error,") — pass **`dlgsound:true`** so the current menu theme's `error.ogg` plays alongside the spoken text. Swept across all 78 existing ones 2026-08-30 at the dev's request (76 gained the arg, 1 flipped from an explicit `dlgsound:false` at `game_menu.nvgt:141`, 1 already had it at `extrafuncts.nvgt:242`).

**Why:** every menu theme ships an `error.ogg` (also used as the menu disabled-item sound via `m.disabled_sound` in `menu_callbacks.nvgt`), but no error dialog was actually playing it — `dlg()`'s `dlgsound` parameter (3rd arg, `dlg.nvgt`) defaults to `false` and no call passed `true`, so error dialogs were silent of any audible cue.

**How to apply:** when adding a new error dialog with `dlg()`, pass `dlgsound:true` as a NAMED arg (keeps `dlgcoppy` at its default `true` so copy-with-C still works). Leave non-error `dlg()` dialogs silent (the default). This is NOT the dlg→alert blanket-convert that [[project_dialog_conventions]] warns against — the dialogs stay `dlg()`, they just become audible. Only `dlg()` is in scope; `alert()` error boxes are native OS dialogs and don't play a themed sound.
