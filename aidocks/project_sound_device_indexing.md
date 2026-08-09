---
name: project_sound_device_indexing
description: NVGT/BASS sound-device list indexing — index 0 is "No sound", index 1 is "Default" (a real entry), 2+ are named devices. SF trims index 0 and stores sound_output_device = trimmed_index + 1. Don't add a synthetic "Default" item.
metadata:
  type: reference
---

NVGT's `get_sound_output_devices()` wraps BASS's device enumeration: the returned array is **index 0 = "No sound"** (a virtual no-audio device), **index 1 = "Default"** (the actual system default output, literally named "Default"), then **2+ = the named devices**.

SimpleFighter's sound-device chooser handles this in two places, both by dropping "No sound":

- **The chooser** (`menu.nvgt`, the `sdm` button, ~line 1067): `string[]@ devices = get_sound_output_devices(); devices.remove_at(0);` — so the trimmed list **already starts with "Default"** at trimmed index 0. On selection: `soundcard = devices[mres]; sound_output_device = mres + 1;` — i.e. `sound_output_device` is the original BASS device index.
- **Load** (`savefuncts.nvgt`, ~line 176): same trim, then it finds the saved `soundcard` name in the trimmed list and sets `sound_output_device = i + 1`.

The startup default is `string soundcard="Default";` (`dec.nvgt:13`), which is exactly trimmed-index-0 "Default".

**Do NOT add your own synthetic "Default" menu item** — it duplicates the real one and makes "Default" appear twice. The "currently set to " + soundcard readout already names the active device correctly because Default is a real list entry. When touching this menu, keep the `remove_at(0)` + `mres + 1` mapping consistent across the chooser and the load path. Related: [[project_audio_model]].
