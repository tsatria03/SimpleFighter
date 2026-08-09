---
name: feedback_dont_flag_indentation
description: AngelScript/NVGT ignores indentation entirely; don't flag uneven whitespace as a concern or spend tool calls "fixing" it for compilation's sake.
metadata:
  type: feedback
---

AngelScript (the `.nvgt` language) is brace-delimited, so indentation is purely cosmetic and never affects compilation — unlike Python, where it's syntactically required.

**Why:** flagging or apologizing for "uneven indentation" after edits is noise — it has zero effect on the code.

**How to apply:** after an edit leaves whitespace slightly off, don't call it out or spend extra tool calls fixing it for compilation's sake. Only adjust indentation if the dev explicitly asks for tidy formatting. Braces, not indentation, are what group statements — see [[project_angelscript_braceless_if]]. Relates to [[feedback_no_crlf_normalization]].
