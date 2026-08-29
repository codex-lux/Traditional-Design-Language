# oq/a-material-neutral-assembly-decides-a-material-question — the authority walk lets a slot that says nothing about a material refuse a question about it

*Status: OPEN · Raised in: The WP-8.4 adversarial audit (28 Aug 2026)*

**OPEN — `construction_vocabulary.resolve()` walks slots in authority order and the first slot
that can answer decides, but "can answer" is decided by whether the token's variants appear in
that slot, not by whether that slot has anything to say about the question.** A slot whose
canonical variant is MATERIAL-NEUTRAL — `solid-masonry-two-wythe` says how many wythes and
nothing about the stone — hits the `if not live: fails` branch and returns a hard refusal, and
the walk stops there before a slot that does know the answer is consulted.

**Two instances found, both fixed by hand, both on the same node.** `brick` returned `holds` on
`scottish-baronial` (granite) until `solid-masonry-two-wythe` and `-three-wythe` were removed
from its list and `primary_cladding` was put first. `stone-rubble` then returned `fails` on the
same node — whose `primary_cladding` is canonically `squared-rubble-granite-ashlar-harled-rubble`,
which the detail line printed *while refusing* — until it too was given cladding-first order.
That refusal was not academic: `quoin-by-catalogue`'s Scottish Baronial licence, whose own `why`
reads *"Rubble walling with dressed ashlar corner dressings of irregular size is the tradition"*,
was refused on a rubble-walled house.

**The fix applied is per-token slot order, which is a convention rather than a rule.** Six tokens
span `construction_type` and `primary_cladding`; two now lead with the cladding (`brick`,
`stone-rubble`) and four with the assembly (`adobe`, `wood-frame`, `log`, `cut-stone`), each for
a stated reason in its own entry. Nothing enforces the split, nothing tests that a new token
picks the right side, and the reason lives in a comment beside each.

**The general rule that would replace it, unbuilt and not obviously right:** a slot cannot refuse
a token whose question it is neutral about — i.e. `not live` should yield `undecidable-soft` and
defer, rather than `fails`, when none of the slot's own canonical variants is *classified* for
that token's axis. It needs an axis on each variant, which the ontology does not carry, and it
would change verdicts across the whole vocabulary rather than the two tokens fixed here.

**One case is left deliberately undecided and is the reason this is a question rather than a
finding.** `cut-stone` reads assembly-first, so `beaux-arts-american` — canonically
`masonry-veneer-over-frame` — answers `fails`, refusing two licences (`keystone-on-a-steel-lintel`
and `surround-that-lies-about-the-wall`). Under a cladding-first reading it would answer `holds`
through its ashlar face and both licences would be granted on a VENEER building, which is
probably wrong: a licence about a real stone lintel should not be earned by a stone-faced frame
wall. So the material-versus-assembly split is not a clean rule waiting to be written down. It is
a per-token judgment about what each licence is really asking, and the honest first step is
probably to say so in the vocabulary's schema rather than to generalise.
