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

## Scoping a test to the styles it was written for (OQ 41, 24 Aug 2026)

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
