---
name: project_repo_hygiene
description: .gitattributes CRLF enforcement and what .gitignore keeps out (audio, .map/.spack packs, lib/, releases/, the compile bundle, personal scratch files). CLAUDE.md is committed, not ignored.
metadata:
  type: project
---

## CRLF enforcement (.gitattributes)

`*.sif, *.nvgt, *.py, *.txt, *.bat, *.ps1, *.md, *.ini` are pinned to `text eol=crlf`. Full rationale in [[project_stability_rules]]; don't run a post-edit normalizer pass ([[feedback_no_crlf_normalization]]).

## .gitignore keeps out

- the `.claude` directory.
- all audio (`*.mp3, *.ogg, *.wav`) — `sf/sounds/` ships separately and is downloaded on first run by `downloadsounds()` in src/sf.nvgt if missing. Don't commit clips.
- `*.map` and `*.spack` — compiled map/sound packs are release artifacts, not source. Authored maps live as `sf/data/builder/maps/decompiled/<name>/data/main.sif` and are committed; the compiled/ folders are intentionally empty in source.
- `New File*.txt` — the dev's personal scratch / notes file. Don't read it as authoritative and **don't write to it**.
- `lib/` and `releases/` — build outputs. (The `lib/` pattern matches `sf/lib/` too, since it has no leading slash.)
- `/src/sf/` and `/src/sf.exe` — the NVGT compile bundle (`tools.py` runs `nvgt -c` from `src/`, so it lands at `src/sf/` before being moved to `releases/`). Anchored to `src/` on purpose so it does **not** match the top-level `sf/` assets folder.
- `__pycache__/`.

Note: `CLAUDE.md` is **not** gitignored in this repo and is committed. The `aidocks/` memory folder is committed too (it's the project's memory — see MEMORY.md).
