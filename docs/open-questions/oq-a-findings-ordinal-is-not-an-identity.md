# oq/a-findings-ordinal-is-not-an-identity — a finding's id moves when an unrelated sibling clears

*Status: OPEN · Raised in: the adversarial audit of WP-11.9, WP-11.10 and WP-11.11 (7 September 2026)*

`plan_check.Findings.add` builds an id from the layer, the room, and the rule or fault id where
there is one, then appends an ORDINAL where two findings land on the same key. Its docstring says
that ordinal is *"stable for a given plan and a given checker, which is what a diff between two
evaluations of the same record needs."*

**That sentence is false, and here is the measurement.** Take `tidewater-georgian-careful` and
shrink `backhall` until its `daylight-depth` finding clears. The aspect finding beneath it —
unchanged in kind, room, layer and statement — moves:

```
before:  daylight:backhall (daylight-depth), daylight:backhall#1 (room-off-the-aspect-…)
after:   daylight:backhall (room-off-the-aspect-…)
```

`PlanWorkbench.jsx:317` diffs on `f.id` to report "N findings new since the last evaluation", so the
bench says a row cleared and a new one opened for a finding nothing touched. The same mechanism
churned **6 of 1,505** ids at WP-11.9's merge, for rows whose statements were byte-identical either
side. Ordinal-suffixed ids across the sixteen shipped plans: **472 of 1,620.**

## Why it was not fixed when it was found

The obvious repair is to put `kind` in the key — it is the field that says what a finding is about,
in one token, and `add()` is the only reader in the tree that does not look at it. It was built,
measured (ordinal-suffixed ids 472 → 395, 0 collisions, longest id 66 chars), and **reverted**,
because `tests/test_critique.py::test_the_finding_id_is_unchanged_by_the_evidence_it_carries`
states the opposite contract in as many words:

> OQ 32: an id is what a finding is ABOUT. Evidence rides beside it and must never enter it, or
> every citation and every open/cleared diff breaks on a number.

and that test lists `kind` among the evidence, beside `need_ft`, `have_ft`, `axis` and `item`.
Changing a pinned contract on one session's reading is exactly the move this audit criticised
WP-11.9 for making to the composer's score. **The build caught it**; the revert is the honest
answer until somebody rules.

It also had a measured cost of its own: finding ids expressible as a `finding:<id>` citation fell
**55 → 12 of 1,620** (`oq/a-finding-citation-cannot-name-a-finding`), because every new segment adds
a colon the grammar's `ID_CHARS` excludes.

## What is being asked

Is `kind` EVIDENCE, or is it IDENTITY?

- **Evidence** — the current contract. Then the ordinal stays, the docstring's stability claim must
  be corrected rather than left standing, and the bench needs some other way to tell a cleared row
  from a renumbered one (matching on `(layer, room, kind, statement)` client-side, say).
- **Identity** — then `kind` joins the key, ids churn once, `test_the_finding_id_is_unchanged_by_
  the_evidence_it_carries` is re-pinned to test the *measurements* it was really written about
  (`need_ft` and friends, which genuinely must not enter), and the citation grammar question above
  becomes load-bearing rather than latent.

The distinction is real and the test does not draw it: `need_ft=10.667` changes as the plan changes
and is plainly evidence; `kind="furniture-fit"` is a closed vocabulary naming what sort of finding
this is, and does not change while the finding is the same finding.

## What must not be done to close it

- **Do not re-pin the OQ 32 test to make a change green.** Its docstring is a stated principle, not
  a measurement, and its failure message is the contract.
- **Do not "fix" the churn by removing the ordinal.** Two findings would then share an id, which
  `add()`'s own docstring says is a collision within one plan rather than the deliberate
  cross-plan reuse it permits.
