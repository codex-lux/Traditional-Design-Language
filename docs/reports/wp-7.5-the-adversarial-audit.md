# WP-7.5 — the adversarial audit of WP-7.4, and the two bugs it found in my own fix

*27 August 2026. Commit `c4751b1`. No new feature: this package is the check on the one
before it.*

---

## What this package is

Lucas asked for a genuine adversarial pass over WP-7.4 — not a re-read confirming the work,
but an attempt to find what was wrong with it — and set the standard explicitly: *"Do not
treat 'the tests I already wrote pass' as sufficient evidence of correctness — that's
necessary, not sufficient."*

Four independent read-only auditors ran over `b8b8f36..HEAD` on four separate angles: edge
cases and regressions per changed file **and every caller of it**; whether each new test is
meaningful, by mentally reverting the fix and confirming the test fails; second-order risk
(security, injection, data loss, performance, cost); and whether the same bug pattern occurs a
second time elsewhere. Nothing an auditor reported was acted on until it had been reproduced
directly — three of the reports did not survive that, and the ones below did.

**The result is two findings that blocked deployment, seven worth fixing, six tests that
passed either way, and two deferrals.** Both blocking findings were introduced by WP-7.4, and
one of them was a false claim in my own commit message. That is the point of the exercise and
it is why it gets a report of its own.

---

## Blocking 1 — the fixture packer drew collisions, and its own comment said it could not

WP-7.4b reserved a room's corner by starting a newly-opened wall past the deepest fixture
placed **anywhere** in the room, and the commit called that conservative in as many words:
*"the failure it prevents is a drawn collision and the failure it causes is a NAMED refusal."*

That reasoning is wrong, and it is wrong in the direction that matters. Every wall packs from
its **low** end, and the four low ends are four different corners. The rule guarded SW, did
nothing at all for NE, and actively pushed W into N at NW. Worse, the largest failure class it
could never have caught is **opposite** walls, where no corner rule has anything to say.

Measured over 81 plausible primary-bathroom sizes: **60 came out with a fixture overlapping
another or sitting outside the room.** The corpus's own 16 plans show none of it — which is
exactly why this needed measuring rather than reasoning about, and why the sweep is now a test
rather than a paragraph.

The approximation is gone. A candidate seat is turned into its **actual rectangle** and
rejected if it leaves the room or touches anything already placed:

```python
def _seat_rect(cw, seat, fw, fd):
    along = walls[cw]["along"]
    if along and fd > d + 1e-6: return None
    if not along and fd > w + 1e-6: return None
    off = (y if cw == "S" else y + d - fd) if along else (x if cw == "W" else x + w - fd)
    return ((seat, off, fw, fd) if along else (off, seat, fd, fw))
```

Re-measured over 144 room sizes and 448 placed fixtures: **0 overlaps, 0 outside**, at a 1e-9
tolerance.

Two things fell out of the fix. Position and extent were rounded to *different* precisions —
3dp and 2dp — so a fixture against the far wall came out at `2.333 + 2.67 = 5.003` in a 5.00 ft
room, and any check downstream had to tolerate a number that should have been exact. Both are
3dp now. And the inner helper had been named `_rect`, shadowing the module-level `_rect(r)`
that the same function calls thirty lines earlier.

The refusal message also changed meaning: it reports each wall's **clear** run now, not its
gross length, because a refusal that quotes a length the packer cannot actually use is telling
the reader the room is bigger than the packer thinks it is.

---

## Blocking 2 — a nondeterministic test WP-7.4b said it had replaced was still in the suite

WP-7.4b's message says *"the three tests replacing it assert on the deterministic engine."*

Three tests were **added**. `test_a_fixture_is_tried_on_every_wall_before_it_is_refused` was
never removed, and it still asserted a fixture count against the default `auto` engine — which
is wall-clock-bounded CP, and therefore a test whose result depends on how busy the machine is.

This is the exact claim-versus-code failure the whole programme exists to remove, committed by
me, in a commit message, in a package whose first finding was a docstring that described
something the code did not do. WP-6.4's rule — *"until X lands" is a lie the moment X lands and
is refused* — has a sibling: **"replaced" is a lie the moment the thing is still there.**
Replaced properly, on the heuristic.

---

## Worth fixing — seven, each verified before it was believed

**The same span bug, a second time, in the renderer.** `render_section.render_bearing_diagram`
drew an over-capacity span marker by feeding an x-axis span's midpoint — an **X** coordinate —
into `Yc`, then spanning the whole plate. On the Tidewater plan that put the 20 → 60 ft finding
at `Yc(40.0)`: a bar lying on the north exterior wall of a 40.08 ft panel, with its label above
the panel top. **Pre-existing** (WP-3.1) and never reached, because both reference plans
reported zero over-capacity spans until WP-7.4a. The first thing that fix did was make a wrong
drawing visible. Markers now sit over the failing bay:

```python
a, b = sp["from_ft"], sp["to_ft"]
if sp["axis"] == "x":
    x1, x2 = X(a), X(b); y = Yc(H / 2.0)
else:
    y1, y2 = Yc(a), Yc(b); x = X(W / 2.0)
```

**The score decomposition printed to the user did not add up.** 714.6 against parts summing to
644.7, the missing 69.9 being the span charge. A breakdown a reader cannot reconcile with its
own total is worse than no breakdown, because it invites them to trust the arithmetic they can
see.

**`_span_charge`'s could-not-evaluate signal was computed and discarded by both callers**, and
`_score`'s new `span_charge` key reached no report at all. This is the OQ 52 family again, in
the package that was fixing an instance of it. Both engines now publish
`geometry_report.span_capacity` with an explicit `None` → **COULD NOT EVALUATE** third state.

**Two catalogue loads were uncached inside a 250-candidate loop.** WP-7.4 put `span_check`
inside the candidate loop without noticing that `load_construction` and
`_timber_bay_applies_to` read from disk on every call: measured **96 reads of
`timber-bay.json` per heuristic solve and 209 per CP solve.** Memoised; the solve went
0.45 s → 0.37 s, so the term now costs less than nothing against the baseline it was added to.

**The catalogue LOAD was guarded and the CALL was not**, so a malformed catalogue took down the
whole placement while a *missing* one degraded gracefully — the worse input getting the better
handling. One behaviour now, and it is the honest one: unjudged.

**`int(GEO.SPAN_W) * SCALE` truncated.** A weight below 1.0 silently became a **zero** penalty,
so a future sweep landing on 0.8 would have produced an inert term that looked configured. A
`_w()` helper rounds the scaled value. The shipped weights are unchanged; this is a trap
removed, not a behaviour changed.

**`bearing_lines` overwrote the court explanation** that `wall_lines` writes for an unroofed
void — including in the IFC property set, so an exported model lost the reason a wall was
there. It preserves an existing `why` now. And `kits/neo-eclectic.kit.json` plus one asset
`alt_text` still named `double-hung-sash`, an id WP-7.4c had removed.

---

## Tests that passed either way, now made to bite

This is the half of the audit the user's standard was aimed at, and it found more than the code
review did.

- **`test_an_on_grid_interior_wall_does_break_a_span` was byte-identical with the fix
  reverted.** It carries an off-grid wall in the same call now, and both tests in that class
  fail on revert.
- **The under-band test's only revert-sensitive assertion sat inside `if engine == "cp-sat"`**,
  so with no ortools, on a slower box, or on a CP timeout it degraded to a shape check that
  could not detect the WP-7.4 revert at all — and the sibling test's own docstring records that
  CP on that plan is wall-clock nondeterministic. It runs on the deterministic result now, and
  **the CP half `pytest.skip`s rather than passing** when the engine did not run.
- **The refusal test's assertion was a disjunction**, so a catalogue rename would have made
  every refusal take the other branch and the four-wall check would never have executed. It
  also counted four *matches* rather than four *distinct* walls.
- **The wall-run citation regex had no word boundary** — "12 in a row" read as 1.0 ft — and
  floored at five, where five is the settled answer, so the floor could not fail.
- **`elements/slots.json`'s vocabulary ratchet had no pawl.** Nothing asserted the enum still
  matches the kits in either direction, and *deleting* the block removed the check rather than
  breaking it. Confirmed to fail now when one id is dropped.
- **Nothing pinned that `_span_charge` is non-negative** — the property the exact early-out
  rests on — nor its unjudged contract. Both pinned.

---

## Deferred, with reasons

**OQ 85, both halves.** `span_check` still credits a bearing wall **across the whole floor
plate however short it is**: a 1.5 ft closet stub on the bay line turns a 40 ft failure into
two clean passes. Correcting it takes the two shipped plans from 4 over-capacity spans to 8.

It is the same class as WP-7.4a's bug, one field away, and it is **not** fixed here on purpose.
The honest model is a span per **run** rather than per axis line — joists bearing on a 4 ft wall
are supported, the joists beside it are not — which is a different computation rather than a
filter. It changes the structural verdict on both reference plans again, and it would re-open
the sweep that set `SPAN_W`. **It wants a ruling before it wants code.**

The second half is that **`plan_check` has no span finding of any kind**, so the validator
verdict the workbench shows and the fidelity score the composer ranks on still say nothing
about capacity: a plan with a 60 ft unsupported run gets a clean verdict. That is OQ 84's
**critic** half, and OQ 84 was closed without saying so. `build/structure.py` also contains no
`sys.exit`, so `check_all.py`'s two invocations of it print and return 0 whatever they find —
though the no-exit convention is shared with `plan_check.py`, `roof.py` and `elevation.py`, so
that part is a convention question rather than a bug in one file.

---

## Also corrected

`docs/structure.md` said the Tidewater plan's zero over-capacity spans were *"a genuine,
checked pass"* and cited a test that no longer exists. `CHANGELOG.md` carried the same claim.
Both were true when written and were falsified by WP-7.4a — the WP-6.4 disease, caught this
time in the same session that caused it rather than a package later.

---

## Verification

All 37 test files pass. Every checker green. `check_addresses` ratchets unmoved — own 442
pairs / 0 collisions, cascade 1,264 / 9. CP keeps **OPTIMAL** on
`tidewater-georgian-careful`, which is the specific thing WP-7.1 broke and had to bisect, and
is therefore checked after every change that touches either engine.

---

## What this package did not do

It did not re-audit WP-6.1 through 6.4; WP-6.4 was that audit and its findings stand. It did
not act on three auditor reports that could not be reproduced — an auditor's finding is a
hypothesis, and the corpus's rule about unsupported calls applies to them as much as to a
measurement. And it did not fix OQ 85, for the reason stated above: the correct model there
changes a published verdict, and changing a verdict is Lucas's call rather than an audit's.
