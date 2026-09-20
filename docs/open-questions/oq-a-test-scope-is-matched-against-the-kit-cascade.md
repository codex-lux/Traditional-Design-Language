# oq/a-test-scope-is-matched-against-the-kit-cascade — three Georgian ids reach 77 of 164 styles

*Status: OPEN · Raised in: WP-14.5, the fault is universal and its number is not (20 Sep 2026)*

**OPEN — `applies_to_styles` is matched against `core._style_chain`, which is the resolve_kit
cascade plus six hops of `member_of`, so a scope naming three Georgian ids reaches nearly half
the corpus.** Measured: `["georgian-colonial-american", "english-georgian", "georgian-revival"]`
reaches **77 of 164 styles**, among them Greek Revival (American and Northern), New England
Federal, Jeffersonian Classicism, Italian Renaissance Revival, Minimal Traditional and
Neoclassical Revival — every one of which states a roof pitch band of its own, none of which any
reader would describe as Georgian.

**That reading is deliberate and is right for its own case.** OQ 63 chose it in writing —
*"a test scoped to a parent still applies to its descendants"* — and
`tests/test_fault_scoping.py` pins it with `tidewater-georgian`, a variant of
`georgian-colonial-american` that inherits its pitch band with everything else. The cascade is
how this corpus says *a Tidewater Georgian is a Georgian*.

**The defect is that it is also how the corpus says a Greek Revival house is a Georgian,** and
nothing distinguishes the two uses. A kit cascade is a statement about where a style's KIT
comes from; a test scope is a statement about which tradition a NUMBER was written for, and
those are not the same relation. Greek Revival inherits Georgian joinery and rejects the
Georgian roof.

**The measurement that raised it.** WP-14.5 read what OQ 63's scoping of
`truss-flattened-pitch`'s pitch secondary actually did. Over the 41 styles the elevation layer
speaks for, 15 supply a pitch, 10 of those failed the Georgian band, **the scope removed 3 and
left 7** — and all ten, scoped away or still convicted, sit INSIDE the band their own style node
states. OQ 63's own closing sentence says those styles are *"now UNJUDGED on pitch by this test
rather than wrongly failed"*; seven of them were still being wrongly failed, and that entry is
corrected.

**One of the three scopes is gone and two remain, on exactly that list.** WP-14.5 replaced the
pitch scope with `band_from_style` — the band comes from the style or the test does not run —
which needs no scope, because the band IS the scope. The other two are
`return-shallower-than-tall` sec[1] and `sunken-dormer` sec[1], both naming the same three ids
and both reaching the same 77. Neither has been measured for false convictions; nobody has
looked.

    chimney-omitted            sec[0]  ["tudor-revival"]              1 id  ->  12 styles
    chimney-omitted            sec[1]  ["prairie-school"]             1 id  ->   4 styles
    parapet-as-stage-flat      sec[3]  ["pueblo-revival"]             1 id  ->   1 style
    return-shallower-than-tall sec[1]  the three Georgian ids         3 ids ->  77 styles
    sunken-dormer              sec[1]  the three Georgian ids         3 ids ->  77 styles

**The question is Lucas's, and it has three answers worth naming:**

1. **Leave it.** A scope is a blunt instrument and `band_from_style` is the sharp one; where a
   number is per-style the substitution is available, and where it is not a scope is the best
   that can be said. The cost is that the two surviving scopes are as wide as the one that was
   measured wrong, and nobody has checked them.
2. **Give a scope a second relation to match on** — exact, or `regional_of`/`variant_of` only,
   rather than the whole kit cascade. That is a new axis on the test object and it needs a
   ruling about what a scope MEANS before it can be given a reading.
3. **Measure the two survivors first and decide afterwards.** Cheapest, and it is what this
   entry recommends: the same sweep that found the seven runs on any scoped test.

**Do not close it by narrowing `_style_chain`.** That function is `_applies`'s reader too — it
decides which styles a whole FAULT reaches — and narrowing it would silently un-apply faults
nobody is asking about. The two questions are joined only by sharing a function; a scope on a
test and an applicability on a fault are different claims and this entry is about the first.

**Related and NOT the same:**
`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants` is this question with the
sign reversed — an exception matches EXACTLY and reaches no descendant at all, while a test
scope matches the whole cascade and reaches 77. One corpus, two mechanisms, opposite errors,
and neither has been ruled.
