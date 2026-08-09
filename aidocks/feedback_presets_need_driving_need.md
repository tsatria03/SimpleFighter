---
name: feedback-presets-need-driving-need
description: "Don't propose presets/type-abstractions for builder entities without a real driving pain or user demand; most entities have manageable field counts and don't need them."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

Adding a preset system (effect-style) or an externalized type/asset folder (NPC-style) to a builder entity must be justified by a **real driving need**, not by technical possibility or symmetry with effects/NPCs.

The two existing cases each had a concrete pressure:
- **NPCs** got externalized type files (info.sif + asset folder, line = coords + level + type + subtype) because 30+ fields plus checkboxes was genuinely unmemorable to type by hand.
- **Effect spaces** got inline presets because players genuinely wanted them — a DSP effect without presets feels incomplete.

The dev's verdict (after a full entity-by-entity sweep): **none of the other ~65 entities need presets.** Most are config-only with small, hand-manageable field sets (e.g. a wall is health + theme + volume + pitch + two flags) and nobody is asking to save presets for them. Their inline config is deliberately per-placement-tweakable, which is the opposite of NPC fields that *define* a reusable creature.

**Why:** building presets/templates for entities with no driving need is a solution chasing a problem — bespoke per-entity work (key schema + form wiring) for no payoff, plus extra maintenance surface. The general "entity templates" feature also splinters because per-placement-unique entities (text, commands, destinations, passwords, URLs — see the Group 3 set) can't be templated at all.

**How to apply:** when tempted to suggest presets/templates for an entity, first ask whether there's an actual pain point (too many fields) or expressed demand. If not, don't propose it. Relates to [[feedback-confirm-before-implementing]].
