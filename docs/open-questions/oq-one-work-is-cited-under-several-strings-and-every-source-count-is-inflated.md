# oq/one-work-is-cited-under-several-strings-and-every-source-count-is-inflated — 23 works under 51 strings, and correcting them reddens the build by six

*Status: OPEN · Raised in: WP-11.7, Tranche 4 (7 Sep 2026)*

**`check_research.py` counts source STRINGS, and a work has as many strings as the people citing it
chose to type.** `cited_by` is `Counter(s for node in nodes for s in node["sources"])` — exact
match, byte for byte. So *A Field Guide to American Houses* is **six works** to this corpus:

```
  35  Virginia Savage McAlester, A Field Guide to American Houses (2nd ed., 2013)
  27  Virginia Savage McAlester, A Field Guide to American Houses, rev. ed. (2013)
  12  Virginia Savage McAlester, A Field Guide to American Houses (2013)
   3  McAlester, A Field Guide to American Houses
   1  Virginia Savage McAlester, A Field Guide to American Houses (2013), 'Folk Houses' and 'National Folk'
   1  Virginia Savage McAlester, A Field Guide to American Houses, rev. ed. (2013) - the Neoeclectic chapter
```

**Measured, over a hand-verified list of 23 works appearing under 51 strings**: collapsing each
group to its commonest spelling takes `distinct sources` **422 → 394** — 28 strings, 6.6% of the
layer, are phantoms — and takes `shared_only_nodes` **24 → 30**.

## That second number is the question

`RATCHET["shared_only_nodes"] = 24` is a ceiling, run `--strict` by `check_all.py`. **Six nodes'
compliance with it is an artefact of spelling and not of research**: `american-farmhouse-vernacular`,
`beaux-arts-american`, `craftsman`, `garrison-revival`, `modern-farmhouse-traditional`,
`neo-eclectic`. Each escapes `shared_only` today because one work it cites is spelled differently
from the way another node spells the same work.

`beaux-arts-american` is the sharpest and was found by the `classical-mediterranean` auditor
independently: its ONLY unique citation is `Arthur Drexler, ed., The Architecture of the Ecole des
Beaux-Arts (1977)`, and `beaux-arts-french` cites `Arthur Drexler (ed.), ...` — the same book, the
same year, differing by a comma and two parentheses. **One node's escape from a thin-research meter
rests on a comma.**

So the tidy is not free, and it is not a tidy: **normalising the corpus's spellings is a six-node
regression against a live ceiling, produced by making the data more correct.**

## What must be ruled

1. **Does the ceiling move when the spellings are normalised?** Raising 24 → 30 to admit a
   correction is not the same act as raising it to admit thin research, and nothing in the ratchet
   distinguishes them. WP-9.4's precedent is that a same-commit ceiling change is how a blinded
   instrument gets ratified — so if it moves, the commit must show the six names and the
   before/after set.
2. **Whether an annotated citation is a second work.** Five of the 51 are a base string plus a
   pointer (`..., 'Folk Houses' and 'National Folk'`; `..., for the framing tradition this variant
   inherits`). They are one work being cited AT a place. A structured layer
   (`oq/a-source-is-a-free-string-and-nothing-can-tell-a-book-from-a-fiction`) would hold the
   pointer in a field; a string layer cannot, and stripping the pointers loses real information.
3. **Which spelling is canonical.** The commonest is what the measurement above used, and it is not
   obviously right: `Oliver (ed.), Encyclopedia of Vernacular Architecture of the World` (15 nodes,
   no year, no forename) beats `Paul Oliver (ed.), ... (1997)` (2 nodes) on count and loses on
   completeness. Choosing by count entrenches the thinner citation.
4. **Whether anything should PREVENT the next one.** A pre-flight that refuses a near-duplicate is
   the obvious guard and it is the dangerous one: the matcher that found these 23 groups also
   offered two Brunskill pairs that are **different books** (*Brick Building in Britain* against
   *Timber Building in Britain*; *Houses and Cottages of Britain* against *Traditional Buildings of
   Britain*), and a guard that refuses a real distinct work is worse than the over-count.

## What was done, and the one string that was changed

**Nothing was normalised.** The 23 groups are recorded here and in
`docs/reports/wp-11.1-the-bench-without-a-literature.md` §XIV, unchanged, with the six nodes named.

**One exception, and the rule it follows is worth carrying**: Tranche 4 MINTED a phantom, and a
package may not leave its own behind. `mid-century-traditional` was given `Alan Hess, The Ranch
House (2004)` while `monterey-revival` already carried `Hess, The Ranch House`, so the family's
"unique" citation was a spelling. It was normalised to the fuller form after MEASURING that neither
node flips (`monterey-revival` 4 uniques → 3, `mid-century-traditional` keeps Clark 1986): `shared_only`
24 before and 24 after, `distinct sources` 423 → 422. **The measurement came first and the edit
second** — the same operation on any of the other 22 groups is the six-node regression above.

## The split REPRODUCES under parallel authorship, which is new evidence for ruling it

Found by the WP-11.7 audit, and it is the strongest argument yet that this needs a ruling rather
than patience. Two higher-rank nodes authored **in the same commit, by two of six parallel agents**,
cite one book two different ways:

```
  15 nodes  Oliver (ed.), Encyclopedia of Vernacular Architecture of the World
              <- northern-european-vernacular took this form
   2 nodes  Paul Oliver (ed.), Encyclopedia of Vernacular Architecture of the World (1997)
              <- mediterranean-vernacular took this one
```

Neither string is new — the package minted no spelling — so its claim to have left only one phantom
behind, and fixed it, still holds. What it did was **deepen a split it documents as an open question
in the same commit**, and it did so because each agent independently reused the spelling nearest to
hand. Five more of the 45 reused citations landed inside other documented clusters the same way
(McAlester, Whiffen, Scully, Blunt).

`northern-european-vernacular` took the form this entry names as the WORSE one — 15 nodes, no year,
no forename, winning on count and losing on completeness — which is question 3 above, arriving as a
live consequence rather than a hypothetical.

**Deliberately not normalised**, on this entry's own terms: which spelling is canonical is exactly
what is unruled, and picking one for two nodes because an audit noticed them would be answering the
question by attrition. Measured, so the cost of deferring is known and small: making the two agree
moves `distinct sources` by one and `shared_only` not at all.

## The instrument, and the false clean bill it first gave

The first sweep for this class normalised years, punctuation, editorial marks and stopwords and
reported **0 phantom uniques**. It was wrong: it does not strip an author's forename, so
`Alan Hess, The Ranch House (2004)` and `Hess, The Ranch House` are different strings under it —
the very case a research auditor had already found by reading. A word-set containment matcher
(≥3 shared words, ≥85% of the smaller set) finds all 23 groups and two false positives, both
Brunskill. **A cleaner-looking normaliser that misses the case you are hunting reads exactly like
proof that the case does not exist.**
