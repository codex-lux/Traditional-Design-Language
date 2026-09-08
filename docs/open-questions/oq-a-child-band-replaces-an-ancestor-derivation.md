# oq/a-child-band-replaces-an-ancestor-derivation — 224 figures where a band stands over an expression

*Status: OPEN · Raised in: WP-11.4, the threshold and the stacks (4 September 2026)*

**OPEN — a descendant kit states a BAND for a parameter an ancestor DERIVES, the merge keeps the
band, and the resolved record no longer carries the derivation at all.** Met in ordinary work, on
the one figure WP-11.4 needed and could not read.

`kits/georgian-colonial-american.kit.json` derives the entrance flight's riser count:

```
"riser_count_from_grade": { "expr": "ceil(part * 2.4 / 6.75)", "source": "storey-graduation",
                            "computed_at": { ..., "value": 4 }, "kind": "derived" }
```

`kits/tidewater-georgian.kit.json` `extends` that slot and states, for the same parameter:

```
"riser_count_from_grade": { "range": [3, 6], "unit": "count", "kind": "measured" }
```

The child's object replaces the parent's whole object, which is what `extends` means and is
correct. **What is lost is that the corpus knows the answer.** `python3 build/resolve_kit.py
federal-style --verbose` prints `riser_count_from_grade 4  ceil(part * 2.4 / 6.75)
[storey-graduation]`; the same command on `tidewater-georgian` prints nothing for that parameter,
because the resolved record now holds a band and a band is not a figure. A drawing needs a number.

**MEASURED, 4 September 2026: 224 (node, slot, parameter) triples over 58 nodes and SEVEN distinct
slot+parameter pairs** where the nearest statement in a node's chain is a `range` and some ancestor
states an `expr` for the same parameter:

| slot | parameter |
|---|---|
| `casing` | `width_in` |
| `height_proportion` | `second_over_first` |
| `pediment` | `rise_over_span` |
| `pilaster` | `projection_in` |
| `pilaster` | `width_in` |
| `steps_and_stoop` | `riser_count_from_grade` |
| `window_sill` | `projection_in` |

Seven parameters is a small vocabulary and 224 arrivals is not a small number: every one of them is
a place where a reader of the resolved kit sees a range and the corpus, one step up, has an
expression with a source pack behind it.

**What WP-11.4 did, which is not an answer.** It draws the band's LOW end and says so on the record
and on the plate, graded `editorial-from-prose`, with the three facts recorded beside it — the band,
the slot's own basis prose (which says *"three to five risers"*, contradicting the band's own top
end), and the parent's derived 4. On `tidewater-georgian` the drawn figure is 3 and the parent's
derivation is 4, and both are inside the band.

**What a ruling has to settle.**

1. **Whether a band and an expression are the same KIND of statement.** They are not: an expression
   with a `source` pack is derivable at any binding and a band is a report of a measured
   population. A merge that lets one replace the other is treating them as interchangeable.
2. **Whether a child band should NARROW an ancestor derivation rather than replace it.** "The
   parent derives 4 and this node's own survey found 3 to 6" is a coherent record and the schema
   cannot express it; "the parent derives 4 and this node says 7 to 9" is a contradiction and
   nothing would report it.
3. **What a reader of a band is entitled to.** Today, nothing points from the band back to the
   derivation it displaced. Whatever else is ruled, `resolve_slots` could carry the displaced
   statement under a second key at no cost to anything that reads the first.

**Do not resolve an instance by deleting the child's band.** Three of the seven parameters have a
source on one side only, and it is not consistently the same side — the same caution
`oq/a-grouping-rule-and-a-room-record-can-disagree` carries, one layer down.
