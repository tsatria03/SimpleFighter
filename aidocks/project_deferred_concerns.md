---
name: project_deferred_concerns
description: Known shape-of-the-code issues that aren't bugs — no data-file versioning, glob-include aggregation noise, silent parser fallthrough, multi-length encoding fragility, silent sound-lookup failures, no tests/linter. Don't proactively "fix" them.
metadata:
  type: project
---

Known shape-of-the-code issues. None are urgent. Don't proactively "fix" them; just be aware when the related area comes up.

- **No data-file versioning in info.sif files.** Every authored file is a flat key=value list with no version stamp; missing keys fall back to engine defaults. The day you change what an *existing* default means, every old file silently shifts behavior with no marker.
- **Glob-include aggregation at ~131 files is getting noisier.** Every symbol is visible everywhere; parse order depends on directory-walk order. No order-sensitive code today, but the risk grows. (Include-tree map: [[project_include_tree]].)
- **Silent parser fallthrough in `map_parser.nvgt`.** Lines that don't match any expected `sd.length()` are dropped with no warning — malformed maps load "successfully" with entities silently absent.
- **Multi-length / open-ended encoding is bug-prone.** A spanning entity may need three discrete length variants (2d, legacy single-y topdown/3d, current min/max-y topdown/3d); a forgotten variant silently breaks one of them, and an over-permissive `>=N` lets garbage tokens through. (See [[project_map_format]], [[project_stability_rules]].)
- **Sound lookups fail silently.** `get_pack_sound` / `get_map_sound` returning no match plays nothing — deliberate, but a clip-path typo is indistinguishable from "feature has no sound." (See [[project_audio_model]].)
- **No tests or linter — the data layer is unverified.** The NVGT compiler catches syntax errors only. No check that read_/write_ agree, that authored keys are recognized, or that a parsed map's entity count matches the file.
