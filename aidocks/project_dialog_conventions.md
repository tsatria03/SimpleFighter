---
name: project_dialog_conventions
description: SF's three dialog functions and when each is used — dlg() for everyday spoken player dialogs, dlgmessage() only for story-zone --paged text, alert() for visual/pre-init/tooling notices. Don't blanket-convert between them.
metadata:
  type: project
---

SimpleFighter has three distinct dialog functions with different jobs. Match new code to the existing convention rather than standardizing everything on one.

- **`dlg(message, dlgcoppy=true, dlgsound=false, timeout=-1, stztype="")`** (`deps/dlg.nvgt`) — the everyday **spoken** dialog and SF's default (~104 call sites). Speaks `message`, supports copy (C), scroll (arrows re-speak), and escape/enter to dismiss; returns `true` if escaped. Use this for normal in-game, player-facing messages and confirmations.
- **`dlgmessage(messages, stztype="")`** (`deps/dlg.nvgt`) — a **narrow, specialized** wrapper (~3 call sites, all story zones). Splits `messages` on `--` into pages and shows each via `dlg()`, playing story-zone open/scroll/close sounds. It is **not** a general alert wrapper — reserve it for multi-page `--`-delimited text (story zones). Note this is the *opposite* of the sibling CaveDefender project's convention, where dlgmessage was the preferred generic alert; do not carry that idea here.
- **`alert(title, text, can_cancel=false, flags=0)`** (`deps/virtual_dialogs.nvgt` → `vd.alert`) — the NVGT **visual** alert box (~44 call sites). Used **deliberately** where a spoken dialog won't do: pre-initialization fatals before the screen reader / soundsystem are up (`sf.nvgt` — screen-reader/soundsystem load failures, single-instance, restart failures, the dockread file-missing alert), the map/sound pack compiler & decompiler tooling (`packfuncts.nvgt`), the updater's download/extract/restart notices (`updater.nvgt`), config-load failures (`controls.nvgt`), and parser errors (`character_parser.nvgt`, `shield_parser.nvgt`).

**How to apply:** new spoken player dialog → `dlg()`. Multi-page story text → `dlgmessage()`. A notice that must appear before audio/screen-reader init, or in the pack-tooling / updater flows → `alert()`. Don't blanket-convert existing `alert()` calls to spoken dialogs (several are visual on purpose) or `dlg()` calls to `dlgmessage()`. Related: [[feedback_menus_say_canceled]], [[feedback_one_sentence_game_messages]].
