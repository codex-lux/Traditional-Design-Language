# oq/a-brief-can-name-a-massing-no-parti-is-built-on — the composer returns no candidates and says nothing about why

*Status: OPEN · Raised in: WP-14.19 (25 September 2026)*

**The finding.** WP-14.19 gave the brief a `parti` and refused, by name and before a job exists, a
named parti whose own massing contradicts the brief's `massing`. The refusal reads the same
predicate as `compose.pick_partis`' massing filter (`compose._massing_admits`), so the filter and
the refusal cannot come to disagree about what a contradiction is. Building it found the neighbour
it does not cover. **A brief whose `massing` no parti is built on composes an EMPTY set, and the
result says nothing about why.**

**Measured on this tree.** The massing catalogue holds 40 massings, and 5 of them are in no parti's
`massing` or `alternate_massings`: `mansard-block`, `prairie-cruciform`, `pyramidal-cottage`,
`telescope-house` and `temple-front-with-wings`. 34 style nodes name one of those five in their
`massing_affinities`, 6 of them as `canonical` (`beaux-arts-french`, `greek-revival-american`,
`greek-revival-southern-plantation`, `neoclassical-revival`, `prairie-school`, `second-empire`).
`briefs/family-georgian.json` with `massing: mansard-block` passes the brief schema,
`compose.check_brief_refs` and `jobs._validate_brief`; `pick_partis` returns no rows; and
`compose()` returns `candidates: []`, with no `dropped_lot_infeasible`, no `named_parti` and no
line in `how_to_read_this` naming the massing. **An unknown massing does the same.**
`schema/brief.schema.json` types `massing` as a free string with no enum and no pattern, so
`massing: no-such-massing` is accepted and composes into the same silence.

**Why it is a ruling and not a missing check.** Three answers are available, and they are
different things to tell a client:

1. **Refuse it before a job, as a contradictory named parti is refused.** It is the same shape:
   the brief asks for something the corpus cannot build. It changes what `tdl_compose` and
   `POST /api/compose` accept, which is a frozen surface WP-14.19 was not given.
2. **Compose it and say so.** Return the empty set with a line naming the massing and the
   partis that exist, on the precedent of `dropped_lot_infeasible`. The request stays legal, and
   the answer stops being silent.
3. **Treat the massing as a preference.** Fall back to style affinity when nothing admits it.
   That is a re-pick, and the brief schema's own description says a brief's absent fields are
   decided and reported, not that its present ones are overridden.

What none of the three may do is leave it as it is. A set with nothing in it and no reason is the
fake-unjudged shape: it reads exactly like a composer that looked at every diagram and found each
one wanting.

**Not done in WP-14.19.** The package's freeze was lifted for the `parti` field alone, and the
refusal it built is scoped to a named parti. An unknown `massing` string also raises the question
of whether the schema should enumerate the catalogue's ids, as it does not for `style` either.

## Related

- `oq/a-brief-cannot-name-a-parti`, closed by WP-14.19, whose refusal half this sits beside.
- `docs/reports/wp-14.19-a-brief-may-name-a-parti.md`, which measured it.
