---
name: feedback-readme-todo-quirks
description: "Quirks and caveats for sf/docks/main/readme.txt and sf/docks/main/todo list.txt — readme is out of date on map modes, todo unfinished items are not commitments."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1df2413-bf71-468a-881b-4377e9893f1d
---

## readme.txt

- Player-facing high-level overview: a short pitch, a folder-layout summary, and a long enumerated list of in-game keyboard commands grouped by purpose (movement, menus, sonar, building, etc.).
- This is the *general* documentation; deeper per-feature reference lives in `sf/docks/builder/*.tp`. When a player or dev asks how a specific subsystem works, prefer the .tp file over readme.txt.
- **The readme is out of date with respect to map modes.** Older sections still reflect the 2d-only era; topdown and 3d map building have shipped. Don't mirror its older claims as authoritative — cross-check against the actual code in `src/includes/` and the per-feature .tp files when answering questions.

## todo list.txt

- Combined "done" log + idea backlog.
- Lines beginning with `Finished.` describe things that have already shipped in past versions.
- Lines beginning with `Unfinished.` are things that *might* be added later.
- **Items in the Unfinished list are not commitments.** They are notes the dev wrote to themselves. Presence in the list does not mean a feature is planned, scoped, or guaranteed to land. Do not promise a player that an unfinished item will be implemented, and do not treat it as a prioritized backlog.
- When a feature listed as Unfinished actually ships, flip the prefix to `Finished.` and leave it in the file as part of the history.

**Why:** These quirks trip up accurate answers — the readme's stale map-mode prose reads as authoritative, and the todo's Unfinished items read as promises. Neither is true.

**How to apply:** When answering questions about map modes or features, don't cite readme.txt as authoritative. When asked about todo items, never frame Unfinished entries as planned or guaranteed.
