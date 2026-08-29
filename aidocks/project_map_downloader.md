---
name: project_map_downloader
description: Phase-1 map downloader — in-game download of compiled .map packs from the dev's VPS (reality-breaker-studios.net) served by Caddy. Server side BUILT & proven 2026-08-29; the game-side download_map() flow is PLANNED (not yet coded). Upload is a deliberately-separate later phase.
metadata:
  type: project
---

Plan + running record for the **map downloader** — letting players fetch compiled maps from the dev's VPS from inside the game. **Phase 1 is download only.** Upload is a separate future phase because a static file server can *serve* but can't *receive* — uploads need a listening receive endpoint (+ auth/abuse handling) that download doesn't. Build the game side one section at a time, confirm each before coding ([[feedback_confirm_before_implementing]]), commit between.

## Why the VPS (not GitHub)
A compiled map is a single self-contained `.map` pack — custom sounds, map-scoped builder templates, baked geometry all travel inside the one file (see [[project_build_pipeline]]). Downloading is just "fetch one file, drop it in the compiled folder, it plays." The dev prefers the VPS over GitHub because asset-heavy packs can exceed GitHub's per-file/repo/bandwidth limits; a VPS folder has none.

## Server side — BUILT & PROVEN 2026-08-29
- **Host:** the dev's Windows VPS. Domain **reality-breaker-studios.net** (GoDaddy), apex `@` A record → **152.44.46.28** (the VPS public IP) — DNS already resolved, nothing to add. No prior website on it.
- **Web server:** **Caddy** (single binary `caddy_windows_amd64.exe`, no install, CLI-only) run in the FOREGROUND (dev is fine hiding the window; promote to a Windows service later if desired):
  `caddy_windows_amd64.exe file-server --root C:\Users\Administrator\Desktop\SimpleFighter --listen :80`
  Served root is the **game-root folder**, so the index sits at the URL root and maps under `/maps/`. Caveat the dev was warned of: a static server has no auth — every file under `--root` is publicly fetchable by URL (no directory browse since `--browse` is off, but known/guessed names are served), so keep that folder to maps + index only, nothing private.
- **Firewall:** inbound TCP 80 opened in BOTH Windows Defender Firewall (`netsh advfirewall firewall add rule ... localport=80`) AND the VPS provider's network firewall (the usual blocker).
- **On-disk layout (VPS):** `C:\Users\Administrator\Desktop\SimpleFighter\` (the served root) holds `index.txt` + `index_gen.bat` + a `maps\` subfolder of the compiled `.map` packs. (The dev moved the two index files UP to the root so they aren't mixed in with the maps folder — hence serving the root, not `maps\`.)
- **Proven URLs (tested in a browser, all work):** `http://reality-breaker-studios.net/index.txt` (lists the maps) and `http://reality-breaker-studios.net/maps/<name>.map` (downloads the pack).

## Index format — Shape A: plain auto-index (dev-decided 2026-08-29)
One `.map` filename per line, **extension included** (dev wants it shown in the menu). No metadata (author/description) — a richer delimited format was offered and DEFERRED (it can't be auto-generated; would need hand-maintenance). Chosen because it's zero-maintenance:
- **`index_gen.bat`** regenerates it: `cd /d "%~dp0"` then `dir /b maps\*.map > index.txt`. Lives in the repo at **`sf/index_gen.bat`** (committed as a utility) and is copied to the VPS root next to the `maps\` folder; the dev double-clicks it after adding/removing maps (or schedules it via Task Scheduler — then delete the `pause` line so it doesn't hang). `dir /b` emits bare filenames even with the `maps\` path arg, so `index.txt` stays clean bare names; the game prepends `/maps/` for the actual download. No path text ever goes IN the file.
- Current maps (all underscores, no spaces): 2d_test, 3d_test, elevator_example, old_house, old_main, topdown_test.

## Game side — PLANNED, not yet coded
Almost pure reuse. Only TWO files change.

**Menu:** in `mapmenu()` (`map_menu.nvgt`, the OUTER maps menu — items: load map / new map / back), add **"download map"** right AFTER "new map" (dev-chosen slot): `m.add_item("download map", "dlmap");` + handler `if(buildem=="dlmap") { download_map(); continue; }`.

**Function `download_map()`** — lives in **`updater.nvgt`** (home of `downloadsounds()`, the analogous download FLOW; NOT downloaderfuncts.nvgt, which is helpers like `beep_percentage`; `dl_file` itself is in `downloader.nvgt`). A one-line base-URL global sits at the top of `updater.nvgt` so the domain lives in ONE place: `string map_server_url = "http://reality-breaker-studios.net";`. Flow:
1. `url_get(map_server_url + "/index.txt")` → on "" or an HTML error page (`string_contains(.,"<!DOCTYPE",1) > -1`, the updater's own guard) alert + bail.
2. Parse with `clean_lines_from_text()` (extrafuncts — trims, drops blanks) → a menu of the `.map` filenames (shown with extension).
3. On pick: if `file_exists("data/builder/maps/compiled/"+name)`, confirm overwrite via `question(...)` (returns 1 = yes) BEFORE replacing — never silent (dev-agreed). Then `dl_file(map_server_url + "/maps/" + name, "data/builder/maps/compiled/" + name)` (the existing progress-beep downloader; returns "finished"/"canceled").
4. Success → alert that it's downloadable from **load map → compiled maps**.

**Playback needs NO wiring:** compiled maps are listed by `find_files("data/builder/maps/compiled/*.map")` (`map_menu.nvgt` ~:670), so a downloaded pack auto-appears in load map → compiled maps and plays via `load_map(name, owner, force_compiled:true, force_spawned:true)`. Local compiled path is `data/builder/maps/compiled/<name>.map` (cwd `sf/`, see `packfuncts.nvgt:18`).

**Decisions locked:** overwrite asks Yes/No first (dev-agreed); every escape/back speaks "canceled" ([[feedback_menus_say_canceled]], [[feedback_yes_no_menu_labels]]); map filenames must avoid spaces (all current ones do — else `dl_file`'s raw URL breaks; URL-encoding deferred). Plain `http` for now (works with `url_get`/`dl_file`); HTTPS is a later one-flag Caddy change, mostly relevant once uploads carry a token.

## Sections to build (game side)
- **§1 — `download_map()` + `map_server_url`** in `updater.nvgt`. **BUILT 2026-08-29** (uncommitted at time of writing). Needs dev compile-check.
- **§2 — menu item + handler** in `mapmenu()` (`map_menu.nvgt`), "download map" after "new map". NOT yet built.
- **§3 — docs (last, per standing rule):** changelog entry + a short mention in the maps help topic ([[feedback_changelog_rules]], [[feedback_update_build_version_txt]]).

## Future phase — upload (NOT designed)
Would need a receive endpoint (a small server-side handler or FTP/SFTP — Caddy static can't accept), a client-side send (bundle `curl.exe`, `run()` it like `7zr.exe`), and an auth/abuse decision (token baked in client = slows casual abuse only; size cap + `.map`-only check server-side). A **moderated** variant (players submit, dev curates into the public folder) sidesteps the open-write abuse surface and keeps download trivial.
