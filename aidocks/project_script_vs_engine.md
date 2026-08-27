---
name: project_script_vs_engine
description: Investigate-script-first philosophy — diagnose bugs/perf in the .nvgt layer before touching the C++ engine — plus the list of non-stock Legacy-NVGT (nvgt) engine changes this game depends on.
metadata:
  type: project
---

The codebase spans two repos: SimpleFighter (this one, .nvgt scripts) and Legacy-NVGT (the engine, C++ — the pinned `nvgt` fork, see [[project_engine_pinned_nvgt2]]). Engine changes are slower to iterate, harder to revert, and require a `scons` rebuild before they're testable, so the default when chasing a bug or perf issue is **diagnose in the script layer first**, and only reach for engine changes once you've ruled out the script layer with concrete evidence.

- **Symptom → script side first.** When a behavior is wrong or slow, start by tracing it through the `.nvgt` call sites that produce it. Most of what feels like an "engine issue" turns out to be a wrapper, a resolver, or a hot loop in script — and even when the engine *is* involved, the script side usually has a way to mitigate or sidestep it without touching C++.
- **Isolate with a minimal repro before touching either side.** When a bug only shows up in complex maps or large packs, build the smallest version that still triggers it and bisect. The "50 signs with `signtype=none` still lags" experiment that uncovered the O(N) pack scan was worth hours of engine speculation.
- **Stub or comment out instead of optimizing.** When a script function might be the bottleneck, comment out its call site and rerun. If the symptom disappears, you've found your layer without changing logic. Then optimize for real. Engine changes don't have this luxury — every C++ change is at least a rebuild round-trip.
- **Engine changes for what only the engine can do.** New API surface (e.g. `directory_rename`, `add_sound_default_pack`), fundamental capability gaps (multi-pack chain, in-memory `BASS_StreamCreateFile` for packed sounds), or fixes below the script binding boundary (per-byte decrypt loops, BASS callback overhead) are real engine work. Script-layer wrappers, lookup costs, per-frame entity loops, and audio-resolution helpers are not.
- **Don't conflate "the engine could be faster" with "the engine is the bottleneck."** Engine optimizations off the actual hot path produce no observable change for the player. `pack_buffer_decrypt` vectorization, single-hashmap-lookup in `read_file`, and `memload`-as-default were real wins that did **not** fix entity-heavy map sluggishness — because the hot path was a script-side O(N) string scan, not pack I/O.

When you do change the engine, note it here so the next person knows the engine isn't stock NVGT.

## Non-stock engine changes (Legacy-NVGT) in use by this game

- **Script-configurable pitch limits.** `sound.cpp`'s pitch clamp (formerly hardcoded `0.05`–`5.0`, i.e. 5%–500%) now reads two script-exposed globals `sound_pitch_lower_limit` / `sound_pitch_upper_limit` (multiplier units). All four clamps (`sound::set_pitch`/`slide_pitch`, `mixer::set_pitch`/`slide_pitch`) consult them. `src/sf.nvgt` sets them at startup to `0.05` / `10.0` (i.e. up to 1000%); raise the builder pitch sliders (`5`–`500`) to match if you want to author beyond `500`. Requires a `scons` rebuild before the game's `sound_pitch_*` references will compile.
