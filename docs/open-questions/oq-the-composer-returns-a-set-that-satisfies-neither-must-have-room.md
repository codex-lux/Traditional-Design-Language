# oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room — the refusal is honest and the set is useless

*Status: OPEN · Raised in: WP-13.7's verification pass (16 September 2026)*

**For `briefs/family-georgian.json`, which states `must_have: ["library", "breakfast-room"]`,
the composer now returns two candidates and NEITHER holds either room.** Each says so, in its
own voice, and that half is the corpus working exactly as designed.

Measured with `revise=False`, so no revision round runs and the loop is not involved, on a
`git archive` of `49e2389` (WP-13.2 complete) against this tree:

| tree | returned at `candidates=2` | holds `library` | holds `breakfast-room` |
|---|---|---|---|
| WP-13.2 | `centre-passage-double-pile`, `five-part-palladian` | both | both |
| now | `side-hall-townhouse`, `courtyard-and-portal` | neither | neither |

## The refusal is stated, twice, per candidate

    JUDGMENT: the brief requires a library and this diagram has no place for one.
    Not added -- the position matters more than the presence.

    JUDGMENT: the brief requires a breakfast room and this diagram has no place for one.
    Not added -- the position matters more than the presence.

That is `CLAUDE.md`'s own rule — *"it will not invent a room the parti has no place for … Refusals
belong in the decision log, stated. Do not 'fix' a refusal into a guess."* Nothing here is
silent and nothing is laundered.

## What is open

**Nothing weighs the brief's `must_have` list in the RANKING.** `compose._sort_key` puts the
fatal count first and the fidelity score second, and a diagram that can house the brief's
required rooms gets no credit for it. So the refusal, which is honest per candidate, composes
into a returned SET that answers the brief with two houses that have neither room — and a
reader who asked for a library is handed a decision log explaining twice why they have not got
one, with no alternative offered that would.

The change that exposed this is WP-13.3: it made five invented alignment and mirror
measurements read the plan's own placed openings, two FATAL faults began firing honestly, the
native Georgian diagram picked up one more fatal than a less native one, and
`_sort_key`'s fatal-count-first rule dropped it below diagrams that cannot house the programme.
**Every step of that is a package doing its job**; the product property fell out of the
composition of three correct decisions.

## What must be ruled

1. **Is satisfying `must_have` a ranking term, a filter, or neither?** A filter is the strong
   reading and would have returned nothing at all for this brief on this tree, which is a
   refusal a person can act on and is not obviously worse than two unusable houses.
2. **If a term, where does it sit against the fatal count?** WP-9.2 put the fatal count ahead
   of the score deliberately and with its reasons written beside it; this would be the second
   thing to outrank a score, and the first to outrank a fatal.
3. **Does a stated refusal discharge the obligation?** The composer's position — *the position
   matters more than the presence* — is a real architectural argument and may be the right
   answer, in which case the finding is that the SET should not consist entirely of diagrams
   making it.

## What must not happen

- **Do not make the test green by asserting the rooms are present.** They are not, the composer
  says why, and demanding them is demanding the invention `CLAUDE.md` forbids.
- **Do not weight `must_have` into `_sort_key` on one session's reading.** WP-4.5 measured
  `NATIVITY_W` 6 → 20 before moving it, and this is the same class of change to the same
  function.
- **Do not read this as WP-13.3 being wrong.** Its measurements are the honest ones; reverting
  them would restore the set by putting two fatal faults back on invented constants.

---

## Amendment, 17 September 2026 — the mechanism, measured commit by commit

The entry above records WHAT the returned set became and not WHY. The why is `_sort_key`'s
PRIMARY key, which is the fatal COUNT, against a fatal count that Phase 13 raised on exactly the
diagrams the brief is about. Measured on `briefs/family-georgian.json` with `revise=False`, four
`git archive` checkouts and this tree, `engine` left at its default:

| tree | `centre-passage-double-pile` | returned leader | in the set? |
|---|---|---|---|
| `840c7f1` before Phase 13 | fit 7.0, **fatal 0**, score 71.9 | `centre-passage-double-pile` | yes, 1st |
| `49e2389` WP-13.2 complete | fit 7.0, **fatal 0**, score 71.9 | `centre-passage-double-pile` | yes, 1st |
| `ad7f631` WP-13.3 complete | fit 7.0, **fatal 2**, score 70.4 | `side-hall-townhouse` | yes, 2nd |
| `c39f3f8` before the container | fit 7.0, **fatal 2**, score 70.4 | `side-hall-townhouse` | yes, 2nd |
| `1392439` the container | fit 7.0, **fatal 4**, score 69.7 | `side-hall-townhouse` | **no** |
| this tree | fit 7.0, **fatal 4**, score 69.7 | `side-hall-townhouse` | **no** |

**The composer still computes the right answer and no longer returns it.** On this tree
`centre-passage-double-pile` scores **69.7** against the returned leader's **56.5**, and all three
of the fit-7.0 diagrams are absent while every returned one carries fatal ≤ 2. The returned four
are exactly the four lowest fatal counts (1, 2, 2, 2). `_sort_key` is doing precisely what its own
comment says — *"a plan carrying a fatal never displaces a clean one from the returned set, however
native its diagram"* — and the comment was written when a fatal was rare.

**So the product for a Tidewater Georgian brief is a TOWN HOUSE, which is the answer WP-4.5 raised
`NATIVITY_W` from 6 to 20 to stop the composer giving.** `tests/test_composer.py`'s own docstring
names that outcome as the retired one, in as many words.

## And two of the four fatals are instruments this corpus has already convicted

Named rather than counted, on `1392439`:

    FATAL [fault] The Front With No Centre: 1 against between 3 and 7.
    FATAL [fault] The Bay That Broke the Symmetry: 4 against at-most 0.
    FATAL [fault] Windows That Do Not Stand On Each Other: 26.604 against at-most 2.0.
    FATAL [fault] The Truss Default: 0.4066 against at-least 0.45.

- **The Bay That Broke the Symmetry (2 → 4 across the container)** is
  `oq/the-facade-layer-counts-a-dependencys-windows-as-bays-of-the-front` — a wing's south windows
  measured against the main block's rhythm and convicted of standing between its bays. **That
  question was raised BY WP-13.5**, the package whose edit moved this count, and it was raised as a
  reporting defect on the shipped plan; nobody measured that the same blindness was also adding two
  FATALS to the composed candidate and pushing it out of the returned set.
- **The Truss Default at 0.4066 against 0.45** is the figure `CLAUDE.md` already records under
  `oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced` — *"a main block of 45 x 28.89 ft
  convicted at 0.4066"*. Narrowing the block is what the container does.
- **The Front With No Centre** is `even-bay-front`'s 3-to-7 band reading ONE placed upper opening.
  `oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts` records that band
  convicting a side-hall front; this instance is a CENTRED front, so that question's framing does
  not cover it and the band is reading a measurement, not a type.

**This is the OQ 52 family deciding the composer's product.** A defect reported where none exists
has always been a reporting problem in this corpus; here it is choosing which house a person is
offered. That does not make the sort wrong — it makes its input wrong — and it means question 2
above ("where does `must_have` sit against the fatal count?") is now the second of two questions,
the first being **whether a fatal from an instrument with an open question against it may
disqualify at all**.

## What the controls could not see, which is the reusable half

WP-13.5 controlled its edit on the sixteen shipped plans (15 of 16 byte-identical) and on
`check_partis.py` (byte-identical output). **Neither reads the composed candidate's fatal count**,
and the three `tests/test_composer.py` rows that would have said so were ALREADY RED from WP-13.3 —
so their redness absorbed a second, different regression in silence. `CLAUDE.md`'s own *a red build
nobody can act on is worse than no build* met one layer in: **a test already red for cause A cannot
report cause B**, and a package that attributes its reds to the previous package by name is exactly
the reader who will not notice.
