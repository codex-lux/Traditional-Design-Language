# OQ 21 — Variant `op`s match on a free string

*Status: CLOSED 24 AUG 2026 · Raised in: From authoring the Georgian kit*

**CLOSED 24 Aug 2026 — the checker is enough.** `check_kits.py` errors on an `op` naming an undefined id, which is the failure mode that actually bit, and the corpus is now fully populated and stable at 159 kits. Constraining the match in the schema would re-resolve every kit that uses an op to prevent a class of error already caught at build time. Not worth it. *Original entry follows.*<br><br>**OPEN — Variant `op`s match on a free string.** A one-character difference turns a `replace` into an `add` and quietly duplicates a record. `check_kits.py` now errors on it, but the failure mode is inherent to the design.
