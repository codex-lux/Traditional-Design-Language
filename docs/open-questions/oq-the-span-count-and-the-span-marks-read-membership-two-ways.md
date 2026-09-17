# oq/the-span-count-and-the-span-marks-read-membership-two-ways — one record, two answers to "which element is this room in"

*Status: OPEN · Raised in: WP-11.16's span precondition, the prover that charged the wrong rectangle (14 September 2026)*

`geometry_report.span_capacity` carries a COUNT and a CHARGE written by whichever engine placed
the house, and a list of MARKS written by `geometry._disclose_spans` afterwards. WP-11.16's
precondition made both per element, so on `geometry_cp._multi_element_fixture()` they agree —
`over_capacity` 1 against 1 mark. **They agree by two different definitions of membership, and
the agreement is therefore a property of the placements this corpus produces rather than a
property of the code.**

- `geometry.spans_over_capacity` selects each element's rooms **GEOMETRICALLY**, by containment
  within `geometry.EL_TOL = 0.5` ft of the element's rectangle. It has to: the search calls it
  with synthesised `{"id", "geometry"}` rooms that carry no `block` tag at all, so the tag join
  is not available on that path. The function says so in its own body.
- `geometry._disclose_spans` selects them **BY TAG**, through `elements.element_of`, because it
  runs over a finished record where the tag is present and authoritative.

## The measurement

Driven on the CP-placed fixture, moving one dependency room 0.6 ft west of its element's face —
0.1 ft past `EL_TOL`:

| | before | after the nudge |
|---|---|---|
| `element_of(link)` | `w-dep` | **`None`** |
| `over_capacity` (geometric reader) | 1 | **1** — not recomputed; it is the placer's own number |
| `len(marks)` (tag reader) | 1 | **2** |
| `element_membership_unresolved` | absent | **set** |

So the two readers part company at 0.5 ft, and they part in OPPOSITE directions: the tag reader
declares the membership unresolved and charges **every** element (WP-11.15's deliberate
over-report, a false positive being visible where a false negative is not), while the geometric
reader silently drops the stray room from every element's scan and reports a smaller number.
`tests/test_span_findings.py::test_the_record_names_every_over_capacity_span_and_the_count_still_agrees`
then fails — loudly, which is the safe direction — but it fails naming a disagreement about
spans when the defect is a disagreement about membership.

**This is not a hypothetical branch.** `element_membership_unresolved` exists because WP-11.15
measured the condition as reachable at **0.51 ft** of overshoot: `elements.TOL` is 0.5 and
`_absorb` is documented to grow a room past its element. Both engines now hand `_absorb` a
`bounds=` map, so no placement in the tree produces it today — but "no placement produces it
today" is exactly what was true of the phantom storey, of the cross-gap span, and of the
footprint-wide charge this precondition removed.

## What has to be ruled

1. **Is a room's massing element a fact of the RECORD or of the DRAWING?** The tag says where
   the author put it; the geometry says where the placer drew it. Where they differ the corpus
   has no rule, and each reader has quietly picked one.
2. **If it is the record**, `spans_over_capacity` cannot read it on the search path, where no tag
   exists — so either the search synthesises rooms carrying their tag, or the arithmetic is
   handed a membership map instead of deriving one.
3. **If it is the drawing**, `EL_TOL` becomes load-bearing rather than a tolerance, and the
   corpus owes a rule for a room that is in no element at all. *Unjudged is not passed*: it must
   not silently join the main block, which is the defect the whole of WP-11.9 exists to remove.

## What must NOT be done

**Do not widen `EL_TOL` until the two agree.** The tolerance is not the disagreement; it is only
where the disagreement becomes visible. And do not reconcile them by making `_disclose_spans`
read geometry: its tag reading is what produces the `element_membership_unresolved` disclosure,
and deleting a disclosure to make two numbers match is how a false clear gets published.
