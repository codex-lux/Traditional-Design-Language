# WP-8.14 — the audit of the four flip packages, and the number nobody policed

*4 September 2026. Adversarial audit of WP-8.10 (`trim-classical`), WP-8.11 (`facade-gable`),
WP-8.12 (`sash-light`) and WP-8.13 (the five live-gate packs together) — the four packages that
executed OQ 51's delivery half. Read this before trusting a figure any of them published.*

---

## I. Method, and what it is worth saying about the result

Three techniques, all of them this repository's own:

1. **Re-derive the number; do not re-read the sentence** (WP-9.5: not one of its blocking findings
   came from reading).
2. **Revert the fix and watch the suite.**
3. **Assert the mutation LANDED before believing the colour** (WP-9.6).

**The headline is unusual for this project: the arithmetic held.** All eight published per-pack
stranding figures re-derive exactly, the branch order is guarded, both of WP-8.13's own fixes bite
under mutation, and un-flipping all eight packs returns the corpus to **7,830 dimensioned slots** —
the pre-flip baseline, to the slot. Four packages that moved every meter in the layer did not move
one of them wrongly.

What the audit found instead is **one stale number, three spent instructions, a claim asserted from
half its evidence, and the reason all four were possible** — which is a single mechanism and is §III.

## II. What was verified sound

| claim | how it was checked | verdict |
|---|---|---|
| stranded 10 / 32 / 70 (WP-8.10–8.12) | re-derived under each package's own corpus condition | **exact** |
| 146 / 25 / 9 / 1 / 0 (WP-8.13's five) | same | **exact** |
| combined 202 | un-flip the five together from today's corpus | **exact** |
| pre-flip baseline 7,830 | un-flip all eight | **exact** |
| `judged` 249 → 250 by exactly one gap | endorsed-set diff across the flip | **exact, one gap** |
| `kit.forbidden` before `opt-in.withheld` | mutation: make withheld win | **4 tests bite** |
| WP-8.13's two gate-lift fixes | mutation: revert each | **both bite** |
| scoped/unscoped counters in the sweep | slots ≥ nodes across all 8 packs | **holds** |

Two notes on that table. The branch order is guarded **incidentally** — the four tests that fire
name the withheld address, not the order, so a reader seeing them go red would diagnose the wrong
thing. And `opening-proportion` reads **145** measured alone against **146** as-shipped: a one-slot
order dependence, which is the smallest possible instance of §IV.

## III. THE FINDING: `unreached` is the one OQ 51 figure nobody derived, and it is the one that rotted

`CLAUDE.md` said **"111 slots corpus-wide survive the flip whatever it does."** The corpus says
**47**. The figure was 179 before any pack flipped, 111 after the first, then 96, then 47 — and it
was corrected exactly once, at WP-8.10, then carried unchanged through three more flips.

**`tests/test_stranding.py` was re-pinned at every one of those flips.** The test knew; the prose
did not. That is WP-9.5's second-commonest shape — a number corrected in one file and not its
neighbour — occurring **inside the register entry that documents that shape**.

The mechanism is exact and worth stating, because it is a design gap rather than an oversight:
`check_counts.py` derives **six** values for OQ 51 — `role_gaps`, `inherited_packs`, `unendorsed`,
`endorsed`, `declined`, `judged` — and holds the prose to each. `unreached` was not among them. Of
the seven figures this layer publishes, exactly one was unpoliced, and it is exactly the one that
went wrong. Nothing about that is a coincidence.

**Closed, as a three-link chain rather than a re-pin.** `unreached` joins `STRANDING`, where the
sweep's drift check — generic over `STRANDING.items()` — holds it to the corpus; `check_counts.py`
reads the constant and holds the prose to it; and `tests/test_stranding.py` asserts the key is *in*
the dict, so a future flip cannot unguard the prose by dropping it. `check_counts` goes 88 → 89
claims. The middle link reads the constant rather than re-running the 6.5 s sweep on every build —
a deliberate weaker link, stated in the comment, and complete because the first link closes it.

**And `check_counts` refused the first regex I wrote for the claim** ("a pattern that no longer
matches is a failure too"), which is that checker's own guard against exactly the fix that looks
applied and is not.

## IV. Three spent instructions, and a claim asserted from half its evidence

**The staging paragraph is advice for a decision nobody can make again.** It opens *"READ
`--stranding <pack>` BEFORE FLIPPING ONE"* and gives three figures — `storey-graduation` strands 9
while 45 survive, `facade-gable` strands 32 with none surviving — in the present tense. Both packs
are flipped; `--stranding` reports **0** for each, because a flipped pack has nothing left to drop.
The paragraph is now the record of *why the order was chosen*, in the past tense, with the durable
half (the mechanism) kept and the figures marked as measured against corpora that no longer exist.

Two more instructions had been discharged and still read as live: *"check this before flipping
`sash-light`"* (flipped), and *"worth a ruling before the gated packs come up"* (ruled 4 Sep and
executed). Both rewritten. This is WP-6.4's rule — *"until X lands" is a lie the moment X lands* —
at the scale of a whole entry: four packages of guidance accumulated and none was retired when the
thing it guided finished.

**And WP-8.13 asserted a two-directional claim from a one-directional measurement.** *"The sum is a
bound in neither direction"* rested on 181 < 202, which only shows the from-below sum under-stating.
Measured from the other side — restoring each of the five one at a time from the all-withheld
corpus — the marginal restorations are 167 + 46 + 9 + 1 + 0 = **223**:

```
    181   sum of marginal costs, measured from below
    202   the flip, measured jointly
    223   sum of marginal restorations, measured from above
```

**The inequality inverts with the direction of measurement.** The claim was true; the evidence for
it was not in the report. That is WP-8.6's class — a claim that reads as checked — in the package
that found five of its own. Both the report and `CLAUDE.md` now carry both directions and the
sharper statement they support: **a per-pack figure is a property of the corpus it was measured
against, not of the pack.**

## IV½. And the fix for an unpoliced count made another one stale, in the same hour

`CLAUDE.md`'s test total read **1,569** against a tree that collects **1,570** — the guard added in
§III is a test, and adding it moved a number nothing derives. That file says of itself that
`check_counts.py` polices counts DERIVED FROM THE CORPUS and that neither a test count nor a check
count is one, so **every number in that paragraph goes stale silently**; this is the eighth recorded
instance and the first caused by closing a different instance of the same class.

Corrected to 1,570 and read back out of the file afterwards, which is that paragraph's own rule and
the only thing that has ever caught one of these. **No guard is proposed** — pinning a pytest
collection count means running pytest inside pytest inside `check_all`, and inventing a mechanism
at the end of a long session is how this session produced four guards that could not fail (WP-9.4).
The class stays where it is documented.

## V. Deliberately not done

- **No guard on the 202 delta itself.** It is a difference between two corpora and only one of them
  exists; it is computable (this audit computed it) but a test would have to run the whole
  counterfactual sweep. The figures that *are* pinned — `dimensioned_before` 7516 and
  `dimensioned_after` 4931 — bracket it, and 4931 has not moved in five packages.
- **No test naming the branch order.** Four tests fire on a re-ordering, which is enough to catch
  it; what they cost is a reader diagnosing the wrong cause. Recorded rather than fixed, because a
  test whose only job is to name a failure another test already catches is a second spelling of one
  rule, which this corpus refuses elsewhere.
- **Nothing about the unguarded-ruling class.** `CLAUDE.md`'s WP-8.13 trap says nothing in the tree
  can verify a conversation, and that stands. The audit checked the four packages' prose for other
  unsupported ruling claims and found none.

## VI. AND §IV WAS ITSELF APPLIED IN ONE FILE AND NOT ITS FIVE NEIGHBOURS

**Found after the audit was committed, by running the meter rather than reading it.** §IV above
corrected `CLAUDE.md`'s OQ 51 staging paragraph — three present-tense instructions for a programme
that had finished — and did not sweep for the same sentences anywhere else. **Six survived, across
five files**, and one more claim beside them was falsified rather than merely spent. That is
WP-9.5's second-commonest shape (*a fix applied in one file and not its neighbour*) occurring
inside the section that names it, which is the second time in this report a lesson has demonstrated
itself.

**The substantive one is not prose in a document. It is what `check_inheritance.py` PRINTS**, on
every `--strict` run — the surface a reader is most likely to actually see:

| the footer said | re-derived |
|---|---|
| *"flip … NOW, **one pack at a time**"* | superseded: ruled 4 Sep, the last five flipped together |
| *"`--stranding <pack>` … **read it before flipping**"* | spent: all eight named packs are flipped |
| *"`storey-graduation` has 23 gaps and **strands 9 slots** while **45 survive** it"* | **STRANDED = 0** |
| *"`facade-gable` has 16 and **strands 32** with none surviving"* | **STRANDED = 0** |

And forty lines above it, `judged` *"does **NOT** move here"* — **the exact claim WP-8.13 falsified
and corrected at `measure()`, 700 lines away in the same file.** One correction, one file, two
locations, one of them updated.

The same file's `--stranding` **argparse help** is the sixth: *"the before/after OQ 51's flip may
not land without … which is how the flip **is** staged"*. It has landed and the staging is over.
Two printed surfaces in one file, and neither is prose any checker opens.

### Why all four figures were free to rot, and it is §III's rule one layer over

`check_counts.py`'s `CLAIMS` list is `(file, key, regex)` over **markdown only** — `CLAUDE.md`,
`STATE-OF-THE-PROJECT.md`, `README.md`, `docs/`. It never opens `build/*.py`. So a number a checker
*prints* is outside every guard in the tree, for exactly the structural reason `unreached` was.

§III's rule was **name the figure the checker does not derive.** Its companion, and the thing this
section adds: **name the SURFACE the checker does not read.** A checker's own output is the worst
case of it, because it carries the authority of having been computed while being hand-typed.

### The fix carries no number

The footer now states the programme as finished and **the two per-pack illustrations are deleted
rather than restated in the past tense.** `CLAUDE.md` keeps them in the past tense because there
they are the record of why the flip order was chosen; a CLI's job is to say what is true now, and
an illustration with no live use is an instruction to the next reader — the argument the 3 Sep
proportion-floor ruling turned on. **Removing a rottable number beats guarding it** where the
number has no reader.

The other four are one line each: `PLAN-OF-ACTION.md`'s *"check it before flipping `sash-light`"*,
the same sentence in two test docstrings, and `tests/test_stranding.py`'s opening line stating the
per-pack staging as current when its own body two lines down explains WP-8.13 superseded it.
**Neither test changes**: `test_opt_in_packs.py` already asserts its driven pack is on `cascade`,
and mutation-checking that — flipping `trim-craftsman` for real in both the pack file and
`dist/taxonomy.json`, with the mutation read back before believing the colour — fires it by name
along with four other tests.

**And the correction to those docstrings contained the same defect a third time.** The replacement
prose for `test_loud_stranding.py` said the rule was held by *"the assert below"*. That file has no
such assert — `test_opt_in_packs.py` does. What actually bites there is
`test_withheld_for_names_exactly_the_shipped_FLIPS_that_reach_this_node`, which reports the flipped
pack as an extra set item. **Caught by running the mutation instead of trusting the sentence**,
which is §I's first technique applied to this section's own output.

### Deliberately not done

**No extension of `check_counts.py` to scan `build/*.py`.** It would have to tell a live claim from
a historical one inside a print string — the `docs/open-questions` code-span exemption in a new
place, where the blind spot is load-bearing — and inventing a mechanism at the end of a long
session is how WP-9.4 produced four guards that could not fail. The instance is closed by deleting
the number; the class is stated here and in `CLAUDE.md`.
