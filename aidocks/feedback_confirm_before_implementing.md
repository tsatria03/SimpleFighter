---
name: feedback-confirm-before-implementing
description: "User has repeatedly experienced Claude over-implementing despite explicit CLAUDE.md guardrails — treat every design discussion as a question, never a commission. Plan mode was tried and rejected, so this rule now rests entirely on instruction-following; vigilance matters more, not less."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e44c81c-ec7b-4076-937b-d38f13a100d4
---

Treat every design discussion as a question requiring explicit go-ahead — never a commission. "I really wish X" / "what if we did Y" / "could we extend Z" / "I have an idea" are explorations, not instructions. Lay out the design, call out tradeoffs, ask for go-ahead. Stop and wait.

**Why:** The user has repeatedly observed Claude over-implementing despite the explicit "Confirm before implementing — design discussion is not a green light" section in CLAUDE.md. They briefly tried `permissions.defaultMode: "plan"` globally as system-level enforcement, but turned it off because the approval friction was too high for routine work. This means the rule now rests **entirely on instruction-following** — there is no permission-layer backstop. The frustration is real and recurring — they've had to keep reinforcing this rule in CLAUDE.md, and the absence of a system-level catch makes vigilance more important, not less.

**How to apply:**
- Default to asking "want me to proceed?" before any Edit/Write/destructive Bash, even when the design feels obvious or small.
- Never bundle implementation into the same turn as a proposal — split the proposal turn from the implementation turn so the user can redirect.
- Never fan out into adjacent files unprompted (help topics, changelog entries, memory files alongside the main change) — each side-effect deserves its own go-ahead.
- **Hard rule: a message ending in `?` is a question, full stop.** No exceptions. Even when it reads like a polite imperative ("Could you fix the bug in X?", "Would you mind adding Y?"), respond with the relevant info or a plan and *wait* for the user to say "yes" / "go ahead" / "do it." A `?` is the user's signal that they want a response, not an action.
- **Treat information-seeking imperatives as questions too**, even without a `?`: "explain X", "tell me about X", "describe X", "walk me through X", "summarize X", "what is X", "what does X do", "what's the difference between X and Y". The user wants prose back, not code edits.
- **Common question shapes to recognize and treat as non-imperative:**
  - WH-questions: *What / why / how / when / where / who / which X?*
  - Polarity questions: *Is/are/was/were X? Do/does/did X? Have/has X? Will X?*
  - Modal possibility/permission: *Can / could / would / should / might X?*
  - Idea framings: *I have an idea about X. What if X? Wouldn't it be cool if X? I was thinking about X.*
  - Preference solicitations: *I wish X. What do you think? Any thoughts? What would you suggest?*
  - Comparisons: *Is X better than Y? Pros and cons of X? Which is faster?*
  - Status checks: *Where is X? How is X going? What's the status of X?*
- **Exceptions** (these are imperatives and can proceed without re-asking): direct unambiguous commands without `?` ("rename X to Y", "install it", "go ahead", "do it", "yes please", "delete this", "add a changelog entry for…"), follow-ups within an already-approved task, or bug fixes the user explicitly asked for in the same message.
