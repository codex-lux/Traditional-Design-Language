# The fault corpus

209 named errors. This is the layer that turns a reference into a teaching tool, and the one that catches cheap execution before it gets built.

## Element-first, style as a facet

Faults hang off **slots**, not styles. The half-width shutter is wrong on every house that has shutters, and authoring it 164 times would hide the pattern rather than reveal it. 93 of 95 slots carry at least one fault — `wall_thickness_masonry` and `wall_thickness_frame` (added in WP-1.3, 23 Aug 2026) are the two not yet covered.

Style enters twice, and the second way matters more:

- **`applies_to`** — usually the single token `universal`.
- **`exceptions`** — where a style legitimately does the thing that is a fault everywhere else. There are **846 of these, 496 carrying a numeric bound**, and they are the difference between a corpus that improves a design system and one that makes it timid.

A Georgian entry portico is five feet deep. That is a fatal fault by Craftsman rules — a porch under seven feet cannot be inhabited — and entirely correct by its own, because a portico is a piece of the order rather than an outdoor room. Shingle Style runs shingles over a corner with no corner board, which is an omission fault anywhere else; the licence turns out to be narrower than it looks, because it permits *omitting* a member and not *substituting* one, so a mitred-and-caulked corner still fails. `inverted_by` handles the cases with a polarity: a crisp arris is correct almost everywhere and wrong on Cape Dutch, Pueblo and Andalusian, where the fault is the absence of softening — and the bounds show why a 3/8-inch machine bullnose is the worst answer of all, too hard to read as adobe and too soft to read as masonry.

## The cause is almost never ignorance

Of 209 faults, exactly **one** has `driver: ignorance`. The rest are stock sizes, trade sequences, catalog defaults, code minima, material substitutions and line items. The flush window in a masonry wall is a *schedule* problem — the window is set before the mason arrives, and the reveal is the leftover.

Naming the driver is what makes a fault fixable rather than merely deplorable, and it is why every entry carries `cost_saved`. **32 faults are `cost_negative`**: they cost money to get wrong. Nobody is defending a budget on those, which changes the conversation entirely.

Every fault carries three fixes: `right`, `cheap` — the best answer at no added cost, which is the tier that actually gets built — and `dishonest`, the tempting shortcut that looks like a fix and is not. Naming the third is protective.

## The corpus is executable

Every fault carries a `test`: an expression, a threshold, a direction, and whether it can be evaluated from a photograph. 209 primary tests plus 273 secondary; **175 are photograph-evaluable**.

```
tdl_measurement_vocabulary(slot="shutter")     → the variable names, exactly
tdl_check_measurements({"shutter_leaf_width_in": 12,
                        "window_opening_width_in": 32}, style="colonial-revival")

→ PRESENT [fatal] The Half-Width Shutter
  value 0.375, required at-least 0.48
  cheap fix: delete the shutters — on a facade where correct shutters cannot be
  afforded, none is not a compromise but a legitimate historical condition
```

Anything the corpus could not judge is returned as **unjudged, never as passed**. That distinction is the whole difference between a tool that helps and one that reassures.

### Four states, and the fourth was added because a fault could vanish

A test may be scoped to the styles it was written for (`applies_to_styles`, OQ 63) and, since WP-5.13, preconditioned on a **measurement** (`applies_when`). A test that declines is **not run** — not passed, not failed, absent from the fault's judgement, exactly as a test written for another style is. So a fault comes back in one of four states:

| state | meaning |
|---|---|
| present | a test that was for this house ran and failed |
| clear | tests ran and none failed |
| unjudged | a number the tests need was not supplied |
| **not applicable** | every test declined its own precondition — the question does not arise |

The fourth exists because such a fault previously appeared in **no list at all**: not present, not clear, not unjudged, absent from the counts — which reads to a caller exactly like clear, and that is the one collapse this corpus forbids.

`applies_when` has since done more than the case it was built for. It gates the two RIVAL secondaries of `cornice-that-is-a-fascia` (the domestic boxed eave at 0.35–0.55 of its own height against the full entablature case at 0.85–1.2, where whichever is right the other convicts the house) on whether an order actually reaches the eave — the choice the fault's own note had always described in prose. It retired two WP-3.2 workarounds in one commit: `cornice_projection_in` and `solar_array_area_sqft` had both been WITHHELD from the measurements to keep a conditional test from firing, which silenced one fault on a name mismatch and left the other unable to hear an honest zero. Both are supplied now.

## An exception is a licence, and its own condition is read (WP-8.4)

An `exceptions[]` entry says the general rule does not convict this style, and where it carries
a `bounds_test` it **replaces** the fault's primary test. **331 of the corpus's 846 exceptions
carry a precondition** on the wall, the roof or the date, in a field called `granted_when`
(named `applies_when` until 28 August 2026, when it was renamed because
`schema/fault.schema.json` carried two fields of that name meaning different things and nobody
could tell which one ran). Until WP-8.4 nothing read it: `architrave-that-is-not-there`'s
Pueblo Revival licence, written for `construction: [adobe, rammed-earth]`, was excusing a house
whose style resolves canonically to stucco-over-wood-frame.

`core.grant_exception()` returns three verdicts, never a bool:

| | |
|---|---|
| `granted` | the condition holds; the licence applies as before |
| `refused` | the style is built in none of the ways the licence names; the general rule stands |
| `unjudged` | the style permits this construction and others too, and nothing in front of us says which one this house is |

**Where the precondition is unjudged AND the exception carries a `bounds_test`, both rules are
run and compared.** Where they agree the question is immaterial and the fault is answered;
where they disagree it is could-not-evaluate, naming the condition. Over 164 styles that is the
difference between 26 verdicts moving and 11 — a fake unjudged is as dishonest in its own
direction as a fake pass.

`granted_when.construction` resolves through `build/construction_vocabulary.py`, a **closed**
table mapping 61 tokens onto variant ids that already exist in `kits/` and recording 17 more as
unmappable with a reason. An agent needing a token that is missing reports the gap; it does not
add one. `date_range` is evaluated only where a caller supplies a date (`plan_check` passes
`context.date_of_representation`), and `regions` is not evaluated at all — 78 of its 79 uses
name a region that CONTAINS the style's own, so the key restates the style match at a coarser
grain. Both counts are ratcheted rather than assumed harmless.

**A caller that knows settles it.** `check_measurements(..., context={"declared": {...},
"date": 1765})` turns most `unjudged` verdicts into real answers, and a plan record already
declares its `construction_type` and its date.

**And a licence matches the style id EXACTLY, never its descendants (WP-9.1).** All three
selection sites in `core.py` test `e["style"] == style`, so an exception written on
`georgian-colonial-american` is never consulted for `tidewater-georgian` — while
`applies_to_styles` walks the inheritance chain. `porch-too-shallow-to-inhabit` on the shipped
Tidewater plan is not the Georgian licence failing; it is the licence never being read. That is
`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`, unruled: whether an
exception should follow the chain as `applies_to_styles` does, and whether a child may then
decline it. Do not close it by copying exceptions down the tree.

`applies_when` was added for a specific failure. `dormer-off-the-bay` carries the secondary `dormer_count % 2 == 1` — dormers are odd on a symmetrical front. The day a plan record could first state that a house carries **no** dormers, that stated zero was a real measurement, the parity test ran on it, and both reference houses were convicted of *"Dormers Off the Rhythm: 0 against equals 1."* Zero dormers is not an even number of dormers; it is no dormers. Any test whose expression divides by a count should carry a precondition, or it will error on the house that has none.

## Two axes of severity

`severity` scores the style reading. `severity_in_use` scores whether the house is good to live in. They diverge: a waste stack with nowhere to land is invisible from the street and fatal in occupation. A corpus that scores only what shows from the sidewalk would quietly deprioritise everything that decides whether the plan works, so both are recorded.

`severity_by_style` handles the rest — a missing chimney is fatal on Tudor Revival and Prairie and unremarkable on a ranch.

## Provenance

Derived from HABS documentation, NPS Preservation Briefs, the model codes, period millwork and sash catalogues, Asher Benjamin, manufacturer literature for the modern failure modes, and first principles. The corpus deliberately does not reproduce the text, structure or illustration sequence of any in-copyright book; it stands on its own sources, cited per entry.


## Guards, rails and the period baluster — one principle, three conflicts

`balustrade`, `porch_rail` and `newel_balustrade` are three slots, and OQ 14 asked whether they
were one assembly carrying one code conflict stated three times. Reading the records settled it:
they are **three different conflicts**, and the slots stay three.

| slot | period value | code | reference |
|---|---|---|---|
| `balustrade` | 30–33 in to the top of the rail | 36 in minimum guard | IRC R312.1.2 |
| `porch_rail` | 30–33 in, balusters at 4–6 in centres | 36 in guard **and** 4 in maximum sphere | IRC R312.1.2, R312.1.3 |
| `newel_balustrade` | handrail 30–32 in above the nosing | 34 in minimum, 38 in maximum | IRC **R311.7.8.1** |

Three trades, three locations, three code sections — and the last is a *handrail* rule rather
than a guard rule, which is a different requirement with a different number for a different
reason. Collapsing the slots would have merged three conflicts into one and lost two of them.

**What IS shared is the resolution, and it is worth stating once because it applies wherever a
period rail meets a modern dimension:**

> Never absorb the difference in the baluster. A baluster is a turned profile with a fixed
> relationship between its vase, its neck and its fillets, and stretching it to reach a code
> height changes that proportion visibly from the ground — which is the single most common way a
> correctly-detailed rail is spoiled. Absorb the difference in the plinth, the newel, or the
> ramp-and-ease: raise the whole assembly on a taller pedestal, lengthen the newel and re-cut
> the ramp. Where the spacing rather than the height is the conflict, take the tight end of the
> period band — 4 in centres are period-correct anyway, and the conflict disappears without a
> substitution.

The corresponding faults are `guard-height-against-the-period-rail`, `baluster-spacing-as-fence`,
`baluster-too-thin`, `newel-too-thin` and `rail-without-a-bottom-rail`.

## Scoping a test to the styles it was written for (OQ 63, 24 Aug 2026)

A test — primary or secondary — may carry `applies_to_styles`. **Absent means every style the
fault applies to**, which is the behaviour before the field existed. Present, it is matched
against the style *and its inheritance chain*, so a test scoped to a parent still applies to its
variants.

It exists because `check_measurements` reports a fault present when **any** of its tests fails.
A secondary test written for one style was therefore failing houses of every other:
`chimney-omitted` carries a Tudor Revival chimney-breadth ratio and a Prairie visual-mass test,
and both fired on a Cape Cod colonial — which is how a parti named `cape-central-chimney` came to
be reported as having no chimney. Before the fix, **17 of 129 styles could not return a clean
plan under their own native diagram**.

A test that is not for this style is **not run**, and that is not the same as passing. It does
not appear in the evaluated results in either direction.

**Scope on what a note SAYS, not on what it mentions.** Twenty-four of 273 secondary tests name a
style in their note and only six name it as a scope. The rest name one as context, as a reference
band, or as the very case the test exists to discriminate — `frieze-as-fascia-board` separates a
genuine Greek Revival frieze-band window from a collision, and scoping it to Greek Revival would
remove the case it is for.
