# oq/a-placement-finding-is-classed-by-what-the-engine-is-for-five-kinds — the analyst's `placement` class reads the record's fields for four drawn kinds and the engine's name for five

*Status: OPEN · Raised in: WP-9.4 (2 Sep 2026)*

**The finding.** `build/critique.py::_is_placement` decides whether a drawn finding is *the
engine's* — the declared record would have satisfied the need and the placement did not — or
something a move may act on. The WP-9.1 report and the function's own docstring said the
decision is *"made against the DECLARED record"*. It is, for four of nine kinds:
`stair-not-drawn` reads `declared_fits`, `fixture-unplaced` the declared walls against the
fixture's footprint, `wall-run` the declared free walls, and the passage kinds `declared_ft`.
For the other five — `unreachable`, `cut-off`, `stack-broken`, `drawn-vs-declared`,
`landing-off-well`, `stack-unplaced` — the rule is `engine != "cp-sat"`, or unconditionally
True. On the search engine those findings are always the engine's; on the proving engine
never. That is why every heuristic critique of the Tidewater plan reports 26–28 placement
items and every CP-SAT critique reports 0.

**Why it is defensible, and why it is a question.** For `unreachable` the declared record
*does* contain the door the search did not seat — the finding's own `declared` count says
so — and a proof that cannot seat it has shown the declaration cannot be built as written.
So "the engine's on the search, the record's on the proof" is a reading of the two engines'
guarantees, not a guess. But it is a reading, and it decides what the loop is ALLOWED TO
TOUCH: on the search engine the topology moves the ruling granted (`add-the-grammar-door`,
`drop-optional-room`) are never reached, because every stranded room is first the engine's.
WP-9.2's sweep never fired either move for exactly this reason.

**What is asked.**

1. Should `unreachable`/`cut-off` on the search engine consult the record further — e.g. the
   declared shared wall between the room and its declared neighbour against
   `openings.required_wall_ft` — so that a room the declaration could never have reached
   is the record's even on the search?
2. Should `drawn-vs-declared` (a room drawn outside its declared band) be the engine's
   unconditionally, given WP-6.3's finding that the search places a room below its band and
   says nothing? Or the record's where the declared band itself cannot tile?
3. Is a two-engine answer — the search's finding is the engine's until the proof has been
   asked — the right shape, or should the analyst say *could not evaluate* on the search for
   these five kinds and let the lever decide?

**What is not asked.** Whether the loop may act on a `placement` item: it may not, and that
is settled by the ruling recorded in `oq/the-revision-loops-authority-over-topology`.
