# oq/a-licence-conditioned-on-the-wrong-axis — an exception's precondition names the wall when what it means is the member

*Status: OPEN · Raised in: The WP-8.4 adversarial audit (28 Aug 2026)*

**OPEN — `granted_when.construction` is the only precondition anything evaluates, so a condition
about something else gets written in it, and then refuses the licence on the style it was written
for.** `porch-ceiling-of-exposed-joists` grants its Craftsman licence when
`construction: [timber-frame, heavy-timber]`. A Craftsman is canonically `platform-frame`, so the
licence is refused on the one style it names — and an exposed-structure porch ceiling is that
style's defining feature.

**The condition is not under-specified; it is on the wrong axis.** Its own `why` and `bounds` are
about the MEMBERS, not the wall: *"real beams and rafters of full dimension, planed, with the
boarding above them visible as a finished surface"*, and *"Exposed 2x framing with joist hangers
and OSB is not this exception under any circumstances."* That is a fact about the porch roof's
workmanship. The corpus has no slot for it, and `build/construction_vocabulary.py`'s own rule is
that an agent needing a name the corpus lacks REPORTS the gap rather than inventing one.

**Widening it to `wood-frame` was considered and refused.** It would grant the licence to every
wood-framed house and throw away exactly the discrimination the licence is made of. The
`bounds_test` still gates it on measurements, but the licence would be earned by the wall rather
than by the joinery.

**Measured, so the size is known.** Of 123 exceptions carrying a construction precondition, 19 are
refused on the style in their own `style` key. Seventeen are substantive and correct — a
stucco-over-frame `pueblo-revival` genuinely is not adobe, and refusing there is the whole point
of evaluating these at all. Two named an exact variant as a stand-in for a class and were
corrected on their own prose (`water-table-that-follows-the-grade` on Cotswold,
`quoin-by-catalogue` on Scottish Baronial). This is the nineteenth, and the only one where the
condition asks about the wrong thing entirely.

**Guarded rather than left loose.**
`tests/test_construction_scope.py::TestALicenceIsNotRefusedOnTheStyleItWasWrittenFor` fails if any
NEW licence joins it, and carries this one in a named `KNOWN_WRONG_AXIS` set with the reason, so
it cannot be mistaken for a passing case. The set is asserted to still reproduce, so a silent fix
fails the build too.

**What would close it.** Either a `granted_when` key for the thing actually being conditioned —
which means deciding whether preconditions may address assemblies other than the wall, and what
the corpus records about them — or a ruling that a licence whose condition the corpus cannot state
carries no `construction` key at all and leans on its `bounds_test`. The second is cheaper and
loses the intent; the first is a schema question that should be answered once for all such cases
rather than for this one.
