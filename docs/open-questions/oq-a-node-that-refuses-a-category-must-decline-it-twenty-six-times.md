# oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times — the backlog refills as it is worked, and 249 is what is visible at one instant

*Status: OPEN · Raised in: WP-8.7, the first adjudication pass (2 Sep 2026)*

**OPEN — declining a pack promotes the next one into the same role, so a node whose own record
refuses an entire CATEGORY of proportioning cannot settle it pack by pack.** Measured on
`appalachian-log-house`: **26 declines across 9 rounds** to reach fixpoint. `log-vernacular-american`:
the same 26, in 10.

## The measurement

`resolve_packs` fills a role from the nearest ancestor that binds one. Decline that pack and the
role does not close — it re-attributes to the next ancestor down the chain, which is a new
unendorsed gap for the same node in the same role. WP-8.2 saw the first order of this ("ten
declines and `unendorsed` did not move once") and made `judged` a floor because of it. This is the
same mechanism read to the end.

Simulated by declining every visible gap for one node and re-measuring until nothing is left, the
queue for `appalachian-log-house` is:

> palladio-corinthian, facade-classical, sash-light, palladio-doric, facade-peristyle,
> opening-proportion, vignola-doric, facade-arcade, opening-mullioned, vignola-ionic,
> facade-picturesque, opening-pointed, vignola-corinthian, facade-medieval-english, benjamin-doric,
> stone-course, corbel-course, gibbs-doric

— five classical orders, a Gothic pointed-arch pack, a Mudejar corbel course and an Iberian arcade,
all arriving at a single-pen log cabin whose own record says *"There is no applied proportional
system and adding one falsifies the type."* Fifteen of the twenty-six are written on that one
sentence. Writing the same sentence fifteen times is not fifteen judgments.

**So the published 249 is not the size of the work. It is the size of what is visible at one
instant.** Eighteen nodes carry a comparable blanket refusal in their own records, covering 60 of
the 249. If each needs something like 26, that class alone is roughly 470 declines — nearly twice
the whole published backlog, to settle less than a quarter of it.

## Why this bears on OQ 51's own ruling

OQ 51 is ruled *adjudicate first, flip to opt-in second*, on the reasoning that flipping first
"strands 287 role gaps in one commit" while adjudicating is honest authoring. That reasoning holds
for a node that takes SOME of what the cascade sends it and not the rest — most of the corpus.

It does not obviously hold for a node that takes none of it. There, the pack-by-pack adjudication
and the opt-in flip reach the identical end state, and the only difference is whether the record
says it once or twenty-six times. A node declining `opening-pointed` — a Gothic arch pack — is not
recording a judgment anybody needed; it is paying the mechanism's bill in the corpus's own prose.

## The question for a ruling

**May a node refuse a category in one statement, rather than a pack at a time?** Three shapes, and
they are not equivalent:

1. **A per-node opt-in now, for this class only** — `inherits_packs: false` (or an empty allowlist)
   on the nodes whose records refuse the category, leaving the cascade untouched everywhere else.
   It is OQ 51's destination applied early to the subset where the destination and the backlog
   agree. It strands nothing that the twenty-six declines would not also strand, and the record
   still states the refusal once, in the node's own words.
2. **A category decline** — `declined_packs` accepting a KIND (`order`, `facade-system`) rather
   than an id. Smaller than a flip, but it invents a vocabulary of categories that the pack
   records do not currently carry, and `kind` is not today a field anyone has ruled on as a
   refusal axis.
3. **Leave it** — twenty-six declines per node, each individually true and individually citable.
   Defensible: every one of them is a real judgment about a real delivery, and the corpus prefers
   an explicit refusal to an implicit one everywhere else. The cost is that the backlog's headline
   number cannot be read as progress, and the work is roughly double what it looks like.

**What I would do:** option 1, scoped by a named list rather than a rule, and only for nodes whose
own record refuses the category in a quotable sentence — the same evidentiary bar as a decline. It
is the one option where the thing written down is the thing the record actually says.

**What this question does NOT ask.** Nothing here proposes flipping inheritance corpus-wide; that
is OQ 51's second half and its own package. And nothing here is a reason to stop adjudicating the
nodes that take some of what they are sent, which is most of them.

## What was done rather than deferred

Fifteen declines were authored on the two log nodes before this was raised, each on the node's own
words and each carrying its `--impact`. They are not withdrawn: they are true, and two of them
stopped a pack overwriting a measurement the node's record already states
(`timber-panel`'s framed-wall thickness against a stated *"Hewn wall thickness 6-9 inches"*). The
nodes are left short of fixpoint deliberately, so the queue this entry describes is still visible
to the next reader in `--unendorsed`.
