---
name: feedback-changelog-rules
description: "Rules for writing changelog entries in sf/docks/main/changelog.txt — sentence caps, per-version entry limits, version bump requirement, reverse-chronological order."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1df2413-bf71-468a-881b-4377e9893f1d
---

Rules for writing new entries in `sf/docks/main/changelog.txt`:

- **A changelog is a RECORD OF WHAT CHANGED, not a manual.** The readme is the manual and the help topics are the reference — the changelog just says, in a sentence or two, what's new or different. If an entry starts spelling out *how to use* a feature (form fields, sub-options, step-by-step mechanics), it has drifted into readme territory; pull it back to the high-level "what changed" and let the readme/help topic carry the how. (Learned 2026-08 on the slant builder entry: I wrote a four-sentence entry walking through the whole build form — footprint, bottom height, slope amount, direction, surfaces — and the dev cut it to the two-sentence "what it is + topdown caveat." A whole feature landing in one version gets ONE concise entry, not a mechanics tour.)
- **Player-facing prose only.** Describe what the player sees, hears, or can now do — never the code-side cause, internal field names, parser branches, or refactors. If a change has no observable effect for the player, it does not belong in the changelog at all.
- **One entry = one line of one or more sentences.** Minimum 1 sentence, maximum 3 sentences per entry. **Default to 1 sentence.** Use 2 only when the change has a meaningful caveat, a why, or a paired side-effect the player should know about. Use 3 only when the change is genuinely substantial — multiple linked behaviors, a player-visible workflow shift, or a fix whose mechanism is non-obvious. A small fix or a one-off feature with no caveats is 1 sentence, period. Do not pad to fill a sentence count.
- **Skip changes that are too small to matter to the player.** If a fix or addition only benefits the dev/code, or is so minor that reading about it adds nothing for the player, leave it out.
- **Per-version entry caps (independent — each version's cap applies to that version alone, not to a shared budget across the major):**
  - A major `.0` release (e.g. v11.0) holds **up to 20 entries / lines**.
  - Each minor release after it (e.g. v11.1, v11.2, …) holds **up to 10 entries / lines**.
  - Once the in-progress version is full, **roll to the next minor** (or the next major's `.0` if you're already past .9 / it makes sense) rather than overflowing the cap.
- **When opening a new version block** (adding the first entry under a `New in X.Y.` header that didn't exist before), also bump the version to match. `build/version.txt` is the **single source of truth** — edit it to the new `X.Y`, and it's mirrored into `src/includes/version.nvgt` automatically on launch (`sf.py`) and on compile (`tools.py`). **Do not hand-edit `version.nvgt`** — it's a generated mirror. The changelog and the version are two halves of the same shipped artifact, so the `version.txt` bump should land in the same change that opens the version block (see [[feedback_update_build_version_txt]]).
- **Order within a version stays reverse-chronological** (newest entry at the top of that version's block), matching the existing file. New entries go at the top of the block, not the bottom.

**Why:** These rules were explicitly authored to keep the changelog readable and scoped — per-version caps prevent bloat, the sentence limit prevents padding, and the version bump rule keeps the in-game version string consistent with what's been shipped.

**How to apply:** Any time a changelog entry is being written or a new version block is being opened, follow these rules exactly. The caps are hard limits, not suggestions — roll to the next version rather than overflow.
