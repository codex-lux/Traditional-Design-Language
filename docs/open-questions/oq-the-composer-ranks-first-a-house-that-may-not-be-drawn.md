# oq/the-composer-ranks-first-a-house-that-may-not-be-drawn — `_sort_key` never reads the refusal written onto the dict it sorts

*Status: OPEN · Raised in: the adversarial audit of WP-13.9 (19 September 2026)*

**`build/compose.py` writes `refused` onto each returned candidate and then sorts those
candidates without reading it. Measured on `briefs/family-georgian.json` with the revision loop
running at one round on the search engine, the candidate the composer ranks FIRST is refused:**

    rank  parti                       fatal  score  refused
    0     side-hall-townhouse           1    56.5   type-fact-downgraded  bearing, stacks
    1     courtyard-and-portal          2    52.8   —
    2     ranch-tripartite              2    51.3   —
    3     centre-passage-double-pile    3    67.4   type-fact-downgraded  bearing, stacks, tiling

A reader who takes the composer's own first recommendation to the bench is handed a conflict set
where the plate would be. The second-ranked candidate is drawable and was available.

## The mechanism

`_sort_key` is `(fatal, -score, demerits, parti)`. It is applied twice: once at `compose.py:1676`
before the placed revision loop runs, and again at `:1767` on the returned slice **after** the loop
has written `"refused": ((plan2.get("geometry_report") or {}).get("refused"))` onto every candidate
at `:1763`. The second sort has the field in hand, on the same dict, four lines above — and the key
does not mention it.

Nothing else compensates. `refused` is not a finding, so it enters no severity count; `score` is
re-derived from the DECLARED record by design (`compose.py`'s own comment: so that `score` and
`score_before` are one instrument), and a refusal is a fact about the PLACEMENT, so it cannot reach
the score by that route either.

## Why this is the same defect one layer up

WP-13.4 ruled that a placement breaking a hard fact of the type is REFUSED and not drawn, and
WP-13.9 then made the revision loop read that verdict: `_improves` refuses a round whose
re-placement is newly refused, "because a house nobody may draw is not a better one." The loop
now declines to hand back a refused record it could have avoided — and the composer, one layer
up, ranks refused records first if their fatal count is lowest. The same sentence applies
verbatim and the same field is in scope.

## Why it is not fixed here

Three readings, and the corpus does not decide between them:

1. **Refused ranks last within its fatal group.** Cheapest, and it keeps every candidate in the
   set — a reader still sees the refused diagram and can read why.
2. **Refused is excluded from the returned set.** Strongest, and it can return FEWER than the
   requested candidates, or none: on this brief two of four are refused, and on a brief where all
   are, the composer would answer with nothing. `compose` currently always answers.
3. **Refused is reported and ranked as now.** The status quo made explicit, on the argument that
   the composer's job is the DIAGRAM and the refusal is the placer's — a different engine or a
   longer budget may draw the same diagram. `refused` is engine- and budget-dependent in a way
   `fatal` is not, and this measurement was taken at one round on the search.

Reading 3 is not obviously wrong, which is why this is a question. The measurement above is at
`revise_engine="heuristic"`, one round, 60 s: **re-derive it on the engine and budget any ruling
would apply to, rather than quoting this table.** The figure a ruling needs is how often a refused
candidate leads on the engine the product actually runs.

Whatever is ruled, the surface should say it: the candidate card publishes `revisedLine` and the
score axes and says nothing about whether the house may be drawn.

## Related

- `oq/a-round-is-accepted-on-the-key-and-not-on-the-rule-each-move-executed` — the same
  key-versus-rule question inside the loop rather than above it.
- `oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room` — the other way the
  returned set can be unusable while every candidate in it is correctly ranked.
- `oq/the-composers-footprint-is-not-the-placed-one` — the third quantity the card publishes that
  the placement does not use.

## Amendment, 15 October 2026 — the reading nobody had measured: every candidate refused

The question's own instruction was to re-derive on the engine and budget a ruling would apply to.
Done once, on `briefs/family-georgian.json` with the revision loop on and `auto` (the app's own
call), and then each returned candidate's plan evaluated as the bench evaluates it on opening:
**all four candidates were refused at compose, and all four again on the bench** — two of them
(`side-hall-townhouse`, `foursquare-quadrant`) with no fatal finding on either surface. The table,
and the refusal lines behind it, are in
`docs/reports/the-candidate-click-and-the-stale-bench-2026-10-15.md` §II.

What it changes about the three readings:

- **Reading 2 (exclude the refused) returns nothing on this run.** The question named that risk in
  the abstract (*"or none"*); here it is the whole set.
- **Reading 1 (refused ranks last) cannot make a drawable house first where none exists**, so on
  this brief it reorders four houses that may not be drawn. It is still the cheaper change, and
  it is right wherever the set is mixed, which the original table was.
- **Reading 3's "a longer budget may draw the same diagram" is not what the proof does here.** The
  same two candidates re-solved on the prover alone at 25 s and at 90 s are still refused at both;
  a longer proof held one more fact on one of them and refused it anyway.
- **The set is not reproducible**: two composes of one brief on one tree differed in their fourth
  candidate. A ruling taken from one table is taken from one draw.

**The surface now says it, whatever is ruled** (the question's own last paragraph asked for that):
the Candidate Set carries a tally beside the set's size (`· 4 refused`), names the facts a refused
column failed on the column, and says in the strip, for the column picked, that it cannot be drawn
and why. The ranking is untouched and this question stays open. Lucas's own report of this
(15 October: *picked the preferred candidate, expected the drawings, found the plan refused with no
fatal flaw*) is the first reader's account of the cost; it is not a ruling, and no reading is
taken from it.
