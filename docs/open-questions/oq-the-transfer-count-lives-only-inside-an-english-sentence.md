# oq/the-transfer-count-lives-only-inside-an-english-sentence — and a third reader now wants it

*Status: OPEN · Raised in: WP-12.5, the overlays and the modifiers (9 September 2026)*

**`geometry_report.vertical` is a list of English sentences, and the number of transfer beams
exists nowhere else.** `build/disclosures.py::transfers` gets at it with

```python
m = re.match(r"^(\d+) upper wall line", line)
```

and says so in its own docstring — *"the count lives only inside an English sentence in
`geometry_report.vertical`"*. That was tenable while one reader wanted it.

There are three now. The disclosure line prints it; `render_plan.py` draws that line; and
WP-12.5's exploded model wants it, because §7.6 of the Phase 12 PRD says the drop-lines the
explode draws are the transfer-beam diagram and their count must agree with what the record
discloses. The PRD's own sentence says the count "matches `geometry_report.vertical`", which is
a category error — a count cannot match a list of prose — and WP-12.5 corrected it to
`disclosures.transfers(plan)` rather than following it.

## What WP-12.5 did, and why it is not a fix

`round/overlays.js::transferCount` **reads the disclosure's sentence** rather than recomputing
the walls. That is deliberate: WP-11.12 established that a second computation of a charged
quantity can convict a placement on numbers it was not chosen by, and the walls behind this
figure are exactly such a quantity. So the Round parses the same English the plate prints.

That is one reader fewer than recomputing, and one parser more than there should be. It also
means the Round's count is `null` — unjudged, not zero — whenever the sentence is worded in a
way the regex does not match, which no test can currently provoke because only one writer
produces it.

## The question

Should `geometry_report.vertical` carry the count as a field beside the sentence?

The argument for is that three readers now want a number that only prose holds, and prose is
the one thing in this corpus that no checker can hold to anything. The argument against is that
the sentence is authored by one writer and read by readers that all live in this tree, so the
duplication is contained — and that adding a field means the field and the sentence can then
disagree, which is `oq/a-grouping-rule-and-a-room-record-can-disagree`'s whole family.

If it is added, **the sentence must be generated from the field and not written beside it**, or
the corpus acquires a fourth way for one number to be two.

## Where it lives

`build/disclosures.py::transfers`, `build/geometry.py` (the writer of `geometry_report.vertical`),
and `workbench/app/src/round/overlays.js::transferCount`.
