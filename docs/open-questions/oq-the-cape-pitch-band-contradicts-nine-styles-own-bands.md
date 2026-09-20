# oq/the-cape-pitch-band-contradicts-nine-styles-own-bands — including one the fault names itself

*Status: OPEN · Raised in: WP-14.5, the fault is universal and its number is not (20 Sep 2026)*

**OPEN — `faults/raised-cape-eave.json` carries a hardcoded pitch band of 36.9–45.0 deg (9:12 to
12:12) and reaches 14 styles, nine of which state a band of their own that it contradicts.** One
of the nine, `minimal-traditional`, is named in the fault's OWN `applies_to`; another,
`cape-cod-revival`, is one of the two styles its `severity_by_style` calls FATAL.

    style                         the fault says      the style's own node says
    cape-cod-colonial             36.9 - 45.0         36.9 - 45.0     (agrees)
    cape-cod-revival              36.9 - 45.0         33.7 - 39.8     FATAL style, disagrees
    minimal-traditional           36.9 - 45.0         18.4 - 26.6     named in applies_to
    new-england-colonial          36.9 - 45.0         39.8 - 49.4     named in applies_to
    new-england-georgian          36.9 - 45.0         36.9 - 42.5
    garrison-revival              36.9 - 45.0         30.3 - 36.9
    modern-farmhouse-traditional  36.9 - 45.0         at-least 26.6
    new-england-federal           36.9 - 45.0         26.6 - 33.7
    greek-revival-northern        36.9 - 45.0         18.4 - 26.6
    monterey-colonial             36.9 - 45.0         18.4 - 22.6
    ranch-style                   36.9 - 45.0         14.0 - 22.6
    garrison-colonial / neo-eclectic / saltbox-colonial              state none

**It reaches 14 because `_applies` matches `applies_to` against the kit cascade**, the same
mechanism measured at `oq/a-test-scope-is-matched-against-the-kit-cascade` — the fault names four
styles and lands on ten more. That half of the problem is that entry's. **This entry is about the
half a scope cannot fix**: even narrowed to exactly the four styles the author named, the band
contradicts two of them.

**`tests/test_fault_scoping.py` already decided not to scope this fault, with a good argument**
that has been overtaken by a measurement: *"Scoping a test inside a fault that is already scoped
buys nothing and risks narrowing it below what its own fault says."* True of a SCOPE. WP-14.5's
`band_from_style` is not a scope, and the question it raises here is genuinely open in a way the
pitch band's was not.

**Why the substitution is NOT obviously right here, which is why this is a question.**
`truss-flattened-pitch` is a fault about a house having the wrong roof for its tradition, so its
band is the tradition's and substituting is simply performing the note's own instruction.
`raised-cape-eave` is a fault about a house claiming to be a Cape and not being one — the
eave-height test is the subject and the pitch is a corroborating tell — so the 36.9–45.0 is a
statement about **what a Cape IS**, and reading it from the style node would make it vacuous on
the very styles it is fatal for: `cape-cod-colonial` would be judged by 36.9–45.0 (the same
number, no change) and `cape-cod-revival` by 33.7–39.8 (its own band, which it always meets). A
type-defining band that every member passes by construction has stopped defining anything.

**Three answers worth naming:**

1. **Substitute, like the pitch band.** The fault then asks *does this house have the pitch its
   own style asks for*, which is a real question and is not the question this fault was written
   to ask. Cheapest, and it quietly retires a type test.
2. **Reconcile the records.** Either `cape-cod-revival`'s node is wrong about its own pitch or
   the fault is wrong about the Revival, and somebody has to read the evidence.
   `oq/a-grouping-rule-and-a-room-record-can-disagree`'s standing rule applies: **do not edit
   either number to agree with the other**, because a source exists on one side only and it is
   not consistently the same side.
3. **Leave the band and narrow the reach**, which needs `oq/a-test-scope-is-matched-against-the-kit-cascade`
   ruled first and still leaves `minimal-traditional` and `cape-cod-revival` contradicted.

**Nothing was changed in WP-14.5.** The three rows the census convicts
(`greek-revival-northern`, `minimal-traditional`, `new-england-federal`) are reported and not
acted on, because ruling 2 of that package admits a second number as EVIDENCE and this one needs
a judgement about what the fault means before the evidence can be used.
