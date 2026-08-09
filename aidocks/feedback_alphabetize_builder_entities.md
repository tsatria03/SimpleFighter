---
name: feedback-alphabetize-builder-entities
description: "When adding a new builder entity, insert it in alphabetical order within its category — both in the builder menu code and in any help topic that lists entities."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 777a1634-8da0-4673-807a-7d9e5ab41e7f
---

When adding a new builder entity (or moving one between categories), place it in **alphabetical order within its category group** in every place that enumerates entities:

- The builder menu arrays in `src/includes/main/menus/map_menu.nvgt` (the per-category `entry_names` / `entry_ids` rows) — keep the entity in its category's alphabetical position, not appended at the end.
- Any help topic that lists builder entities by category — notably the object index in `sf/docks/builder/maps.tp` (grouped Audio, Construction, Interaction, Kombat, Misc, Transition, Trap, Transportation, Zone), and any other topic that cross-references a set of entities.

Sort by the entity's friendly/menu name within its category. Keep the code order and the help-topic order matching each other.

**Why:** the dev repeatedly has to re-sort builder entities alphabetically in both the code and the relevant help topics after they're added out of order, and asked that new entities be slotted in correctly from the start. Same pattern as commands — see [[feedback-alphabetize-commands]].

**How to apply:** before finishing a builder-entity addition, find its alphabetical slot within its category in both `src/includes/main/menus/map_menu.nvgt` and every help topic that lists it, and insert there rather than appending.
