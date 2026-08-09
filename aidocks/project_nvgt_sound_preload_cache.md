---
name: project_nvgt_sound_preload_cache
description: NVGT sound.load caches decoded audio by FILENAME; regenerating audio into a reused path replays the old clip. Use a unique filename each time or pass allow_preloads=false.
metadata:
  type: project
---

NVGT's `sound::load(filename, pack@, bool allow_preloads = !system_is_mobile)` consults a global **filename-keyed preload cache** (`get_sound_preload(filename)` in the engine's sound.cpp). On a hit it builds the stream from the CACHED bytes and ignores the file's current contents on disk. So if you write new bytes to the SAME filename and load it again, you get the PREVIOUS clip back. `sound.close()` does NOT clear the cache (it's a separate global map).

**Why:** this bites any time audio is regenerated into a reused path — TTS-rendered-to-file, downloaded clips, recorded audio. The first clip caches; every reload of that filename replays the cached audio.

**How to apply:** any time you regenerate audio into a reused path, either:
- **Direct sound object** — load with preloads off: `snd.load(outfile, sound_default_pack, false)` (the third arg is `allow_preloads`; `sound_default_pack` is the registered global).
- **Through a sound_pool** — the bundled sound_pool always loads with default preloads and exposes no flag, so give each clip a **unique filename** instead (append an incrementing counter), and delete the previous temp file (`file_delete`, after `destroy_sound` frees it) to avoid temp churn.

Related: [[project_audio_model]], [[project_path_conventions]].
