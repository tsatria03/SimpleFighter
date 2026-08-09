---
name: feedback_verify_code_while_fixing
description: When fixing anything, read the surrounding code, confirm the reported detail is actually true (re-locate by symbol not stored line number), and flag adjacent errors found along the way — don't blindly trust a finding's claims.
metadata:
  type: feedback
---

When fixing a bug or applying a change, don't just patch the reported spot — **read the code carefully around it, confirm the report is accurate, and surface any errors you notice while you're in there.**

**Why:** review findings and remembered line numbers drift and can be wrong. Blindly following them ships broken or incomplete fixes — and the dev runs/verifies builds themselves, so a wrong edit ships.

**How to apply:**
- Re-locate the target by symbol, not the stored line number (line numbers drift after edits).
- Read enough surrounding code to understand intent before changing it.
- Verify the finding's claim is actually true; correct it if not.
- Fix or flag adjacent problems you trip over — but keep the fix scoped, don't silently balloon it.

Related: [[feedback_confirm_before_implementing]].
