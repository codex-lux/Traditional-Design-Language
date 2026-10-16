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

## Amendment, 15 October 2026 — one brief, one run: every candidate refused

*(Corrected 16 October 2026 by the audit of the change that wrote it: the heading and two sentences
generalised one run, one recommendation was stated as fact, and the bench column of the table was
evaluated by a different route from the one a candidate takes on opening. Corrections are in place,
dated, and say what they replace.)*

The question's own instruction was to re-derive on the engine and budget a ruling would apply to.
Done once, on `briefs/family-georgian.json` with the revision loop on and `auto` (the app's own
call), and then each returned candidate's plan evaluated through the bench's evaluate route with
two corrective rounds. **That is the route an example or a pasted record takes on the bench; a
candidate opened from the Candidate Set is evaluated with none** (`PlanWorkbench.jsx` sets its
`reviseNextRef` for an example and a paste only, and the route's default is 0), so the "on the
bench" column is the same record after two rounds of repair and not the first evaluation a
candidate gets. **All four candidates were refused at compose, and all four again on that
evaluation** — two of them (`side-hall-townhouse`, `foursquare-quadrant`) with no fatal finding on
either. The table, and the refusal lines behind it, are in
`docs/reports/the-candidate-click-and-the-stale-bench-2026-10-15.md` §II. A compose by an independent auditor of
this change on 16 October (`compose(briefs/family-georgian.json, 4)`, revision on, `auto`, defaults,
reported by that auditor and not re-run by the author) refused 4 of 4 again, with a different set
and order and no fatal on any: the qualitative result reproduced, the
table did not, which is the point of the last bullet below.

What it changes about the three readings, **on this brief and this run**:

- **Reading 2 (exclude the refused) returns nothing here.** The question named that risk in the
  abstract (*"or none"*); here it is the whole set.
- **Reading 1 (refused ranks last) cannot make a drawable house first where none exists**, so on
  this brief it reorders four houses that may not be drawn. It would be the cheaper change wherever
  the set is mixed, as the original table was; the report recommends it, and nothing here rules
  between the readings. (The first version of this bullet said it *is* right wherever the set is
  mixed, which asserted a recommendation as a finding.)
- **Reading 3's "a longer budget may draw the same diagram" is not what the proof did here.** The
  same two candidates re-solved on the prover alone at 25 s and at 90 s were still refused at both;
  a longer proof held one more fact on one of them and refused it anyway.
- **The set is not reproducible**: two composes of one brief on one tree differed in their fourth
  candidate, and a third differed from both. A ruling taken from one table is taken from one draw.

**What the surface now says of it, whatever is ruled** (the question's own last paragraph asked for
that). The per-column refusal line and the conflict set below the columns predate this change
(WP-13.4). New: a tally beside the set's size (`· N refused`, and `· N not judged for drawing` for a
candidate the placed loop never reached, which carries `refused: null` too and is not a pass); the
facts a refused column failed on, in its foot line and beside its counts; a strip that says, for the
column picked, whether it can be opened or why not, and, for a set in which nothing can be opened,
that the brief or the parti is what changes. The ranking is untouched and this question stays open.
Lucas's report of the original screen (15 October: they picked the candidate they preferred,
expected the drawings and found the plan refused with no fatal flaw) is paraphrased here, not quoted; it is
the first reader's account of the cost and not a ruling, and no reading is taken from it. The
compose function's local sort alias is `_sort_key`; the module-level function is `compose.rank_key`.
