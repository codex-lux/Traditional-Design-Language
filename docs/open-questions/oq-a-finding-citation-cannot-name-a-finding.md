# oq/a-finding-citation-cannot-name-a-finding — 1,608 of 1,620 finding ids are unciteable by the grammar that has a `finding` kind for them

*Status: OPEN · Raised in: the adversarial audit of WP-11.9, WP-11.10 and WP-11.11 (7 September 2026)*

The citation grammar carries a `finding` kind. `citations.py::_known_ids` names it among the kinds
with no corpus registry; `citations.js::routeCite` routes `finding:<id>` to the workbench with that
finding selected. And the grammar cannot express a finding id:

```
ID_CHARS = r"A-Za-z0-9_.-"          # citations.py, and the same constant in citations.js
REF_RE   = ^([a-z]+):([ID_CHARS]+)(?:#([FRAG_CHARS]+))?\Z
```

**`:` is not in `ID_CHARS`**, and `plan_check.Findings.add` builds every id by joining its parts
with `:` — `layer`, the room, the rule or fault, and (since this audit) the kind. So any finding
about a ROOM, or carrying a rule id, has an unciteable id.

Measured over all 16 shipped plan records:

| | citable as `finding:<id>` | of |
|---|---|---|
| before this audit | **55** | 1,620 |
| after it | **12** | 1,620 |

The twelve are the plan-wide findings whose id is a single bare segment (`plan`, `completeness`).
`adjacency:great-room` is not citable; neither is `fault:cornice-that-is-a-fascia:fault-present`.

**Pre-existing, and widened by 43 by this audit's own id fix.** Putting `kind` into the id (so a
finding's identity stops moving when a sibling clears — see
`docs/reports/audit-2026-09-07-the-things-the-session-did-not-measure.md` §IV) gave a colon to
findings that previously had none. That cost is stated here rather than absorbed: 3.4% citable
became 0.7%, both of them approximately none, and the id fix removed a defect a reader could
actually see.

## What is being asked

Widen `ID_CHARS` to admit `:`, or give findings an id shape the grammar can already express?

Neither is obviously right, and both have a cost this corpus has already paid once:

- **Widening the class touches THREE spellings** — `REF_RE` and `CITE_RE` in
  `workbench/server/`, `parseCite` in the app — held together by
  `test_grammar_agreement.py`, which exists because an audit found two of the three disagreeing
  about the dot in a constraint id. `[a-z]+:[A-Za-z0-9_.:-]+` also makes `style:craftsman:junk`
  parse where it does not today, on every kind and not only on findings.
- **Reshaping the id** to, say, a single dotted token would undo the readability that makes
  `daylight:backhall:room-off-the-aspect-its-record-wants` legible in a bench URL, and the id's
  own docstring is explicit that its parts are the durable ones.

## What must not be done to close it

- **Do not drop the `finding` kind** because nothing can cite one. It routes correctly the moment
  an id reaches it; the grammar is the half that is wrong.
- **Do not remove `kind` from the id to recover the 43.** It is there because a finding's identity
  was moving when an unrelated sibling cleared, which a reader of the bench could see; unciteability
  is a hole nobody has yet fallen into, since the twelve citable ids are not the interesting ones.
