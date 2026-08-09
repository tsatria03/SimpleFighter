---
name: project_angelscript_reserved_words
description: Never name a variable/parameter/member `out` (or other AngelScript reserved words like in, inout, shared, final, from) in .nvgt code — it's a compile error.
metadata:
  type: project
---

`out` is a reserved keyword in AngelScript (parameter direction, alongside `in`/`inout`), so it cannot be used as a variable, parameter, or member name in any `.nvgt` code. Using it is a compile error, and since the game runs uncompiled from source a compile error means it won't launch at all.

**Why:** easy to hit when naming a local `string out` for serialized output.

**How to apply:** pick a different name (`result`, `serialized`, `output`, `buf`) for any variable that would otherwise be `out`. Watch for other AngelScript reserved words too — `in`, `inout`, `shared`, `final`, `from`, `mixin`, `abstract`, etc. Related engine gotchas: [[project_nvgt_key_pressed_oneshot]], [[project_angelscript_braceless_if]].
