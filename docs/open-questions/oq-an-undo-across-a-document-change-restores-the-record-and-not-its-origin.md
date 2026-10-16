# oq/an-undo-across-a-document-change-restores-the-record-and-not-its-origin — the history holds records and the origin is kept beside it

*Status: OPEN · Raised in: the audit of the candidate-click follow-up (16 October 2026)*

**OPEN — undo and redo move the bench between plan RECORDS, and where a record came from
(`session.planFrom`) is not part of the history, so an undo that crosses the loading of a different
house can leave a record on the bench under another house's origin.** Lucas was asked on 16 October
2026 and ruled **leave it, record it**: no code is changed for it. This file is the record.

## The reproduction

1. Compose a brief and open candidate 1 of the first job. The bench holds `centre-passage-double-pile-smith`
   with `planFrom = candidate | job A | 1`.
2. Compose the same brief again, and open the same diagram from the second job. A composed plan's id
   is `{parti}-{briefId}`, so the id is the same; the record is a different house; `planFrom` is now
   `candidate | job B | 1`.
3. Press undo. `planDoc` restores the record of step 1. `planFrom` still reads job B.

The record on the bench is job A's candidate and the journey reads it as job B's. Evaluations are keyed
to the origin they were asked from (`journey.js::originKeyOf`), so job A's record is evaluated and
believed under job B's key, and Next to the Plan step is offered on the strength of a compose the
record is not from.

## Why it was left

- It needs three things at once: two composes of one parti, the same diagram opened from each, and an
  undo across the second open. Nothing is drawn wrongly and nothing is exported wrongly; what can be
  wrong is a Next that is offered when it should be held, or the front door's line about where the
  house on hand came from.
- Every route to the other readings has a cost Lucas declined: carrying the origin in each history
  entry changes `state/planDoc.js`, which knows nothing about the session; clearing the history on a
  load of a whole new document removes the ability to undo an accidental load.
- The other half of the same family is closed. A record put on the bench with no origin to record
  clears the standing origin only where that origin names the same plan id
  (`state/session.js::clearPlanFrom`), so an undo back to a house with a different id keeps its origin.

## What would settle it

A ruling on which of the three is wanted. If the origin is to travel with the history, `planDoc`'s
snapshot would carry a copy of `planFrom` and `load`, `undo` and `redo` would write it back through
`session.set`, with the evaluation key following; the census in `src/planOrigin.test.mjs` would then
need a fourth class of load, the restore.
