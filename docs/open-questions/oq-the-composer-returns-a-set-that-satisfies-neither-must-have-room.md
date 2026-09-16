# oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room — the refusal is honest and the set is useless

*Status: OPEN · Raised in: WP-13.7's verification pass (16 September 2026)*

**For `briefs/family-georgian.json`, which states `must_have: ["library", "breakfast-room"]`,
the composer now returns two candidates and NEITHER holds either room.** Each says so, in its
own voice, and that half is the corpus working exactly as designed.

Measured with `revise=False`, so no revision round runs and the loop is not involved, on a
`git archive` of `49e2389` (WP-13.2 complete) against this tree:

| tree | returned at `candidates=2` | holds `library` | holds `breakfast-room` |
|---|---|---|---|
| WP-13.2 | `centre-passage-double-pile`, `five-part-palladian` | both | both |
| now | `side-hall-townhouse`, `courtyard-and-portal` | neither | neither |

## The refusal is stated, twice, per candidate

    JUDGMENT: the brief requires a library and this diagram has no place for one.
    Not added -- the position matters more than the presence.

    JUDGMENT: the brief requires a breakfast room and this diagram has no place for one.
    Not added -- the position matters more than the presence.

That is `CLAUDE.md`'s own rule — *"it will not invent a room the parti has no place for … Refusals
belong in the decision log, stated. Do not 'fix' a refusal into a guess."* Nothing here is
silent and nothing is laundered.

## What is open

**Nothing weighs the brief's `must_have` list in the RANKING.** `compose._sort_key` puts the
fatal count first and the fidelity score second, and a diagram that can house the brief's
required rooms gets no credit for it. So the refusal, which is honest per candidate, composes
into a returned SET that answers the brief with two houses that have neither room — and a
reader who asked for a library is handed a decision log explaining twice why they have not got
one, with no alternative offered that would.

The change that exposed this is WP-13.3: it made five invented alignment and mirror
measurements read the plan's own placed openings, two FATAL faults began firing honestly, the
native Georgian diagram picked up one more fatal than a less native one, and
`_sort_key`'s fatal-count-first rule dropped it below diagrams that cannot house the programme.
**Every step of that is a package doing its job**; the product property fell out of the
composition of three correct decisions.

## What must be ruled

1. **Is satisfying `must_have` a ranking term, a filter, or neither?** A filter is the strong
   reading and would have returned nothing at all for this brief on this tree, which is a
   refusal a person can act on and is not obviously worse than two unusable houses.
2. **If a term, where does it sit against the fatal count?** WP-9.2 put the fatal count ahead
   of the score deliberately and with its reasons written beside it; this would be the second
   thing to outrank a score, and the first to outrank a fatal.
3. **Does a stated refusal discharge the obligation?** The composer's position — *the position
   matters more than the presence* — is a real architectural argument and may be the right
   answer, in which case the finding is that the SET should not consist entirely of diagrams
   making it.

## What must not happen

- **Do not make the test green by asserting the rooms are present.** They are not, the composer
  says why, and demanding them is demanding the invention `CLAUDE.md` forbids.
- **Do not weight `must_have` into `_sort_key` on one session's reading.** WP-4.5 measured
  `NATIVITY_W` 6 → 20 before moving it, and this is the same class of change to the same
  function.
- **Do not read this as WP-13.3 being wrong.** Its measurements are the honest ones; reverting
  them would restore the set by putting two fatal faults back on invented constants.
