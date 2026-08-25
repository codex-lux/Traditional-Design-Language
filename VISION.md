# Traditional Design Language — The Vision

*What this project aspires to be, and why. Written to be read whole, in one sitting, by
someone who has never opened the repository.*

**This document deliberately carries no counts, no percentages, and no status.** Those live in
`STATE-OF-THE-PROJECT.md` and go stale within weeks — the project's own reviews have twice
caught its numbers drifting. What follows is meant to still be true when every number in the
repository has changed. If a sentence here needs revising, it is because the *aim* moved, and
that is worth a commit of its own.

---

## I. The line this belongs to

For four centuries, the way architectural fluency reached people who could not apprentice
under a master was a book.

Vignola published the *Regola delli cinque ordini* in Rome in 1562: five orders, each reduced
to a module and a table of parts, so that a competent mason who would never see Rome could set
out a correct entablature. Palladio's *Quattro Libri* followed in Venice in 1570. Gibbs
published *Rules for Drawing the Several Parts of Architecture* in London in 1732 — the book
whose plates a Virginia joiner actually owned, and whose Ionic order is therefore the one
standing on Chesapeake porches today. Chambers wrote his *Treatise* in 1759. And Asher
Benjamin, working for American carpenters rather than English gentlemen, published *The
American Builder's Companion* in 1806 as a Federal manual and *The Architect, or Practical
House Carpenter* in 1830 as a Grecian one — same author, same audience, same trade, new
plates. A style changed across a continent because a book changed.

These were not aesthetic treatises. They were **transmission technology**: a way of moving
accumulated judgment from the people who had it to the people who needed it, at a scale
apprenticeship could never reach. They worked. The proof is standing in every American town
that predates the war.

Then the line broke. The twentieth century replaced the pattern book with the millwork
catalog, the catalog with the plan service, the plan service with the production builder's
back catalogue — and at each step the thing being transmitted got thinner. A catalog transmits
*parts*. A pattern book transmitted *why the parts go together*. Somewhere between the two,
the reasoning fell out, and what remained was a kit with no grammar: a house assembled from
correct components that is nonetheless wrong.

**This project is the resumption of that line in an executable medium.** Not a book about
traditional architecture. The next pattern book, written so that a machine can read it and a
human can still argue with it.

---

## II. What went wrong, stated precisely

It is tempting to say that production houses are bad because builders do not know better. The
data in this project says something more interesting, and more useful.

The corpus catalogues named, testable errors — the things that make a house read as wrong to
someone fluent. Every one records its *cause*. Of the two hundred–odd errors in the corpus,
**exactly one is caused by ignorance.** The rest are caused by stock sizes, trade sequences,
catalog defaults, code minima, material substitutions, drafting conventions, maintenance
avoidance, and — most of all — cost.

The four-foot porch is the type specimen. A porch runs the width of the house, has columns, a
rail, a ceiling and a roof, and is five feet deep, so nobody can sit on it: a rocking chair is
thirty-odd inches deep and needs room behind it to rock and room in front of it to pass. The
house advertises an outdoor room and does not provide one. Why? Because porch depth is the
cheapest thing on a set of drawings to reduce and the last thing anyone measures; because
porches are excluded from appraised area, so a porch is pure cost against the loan; because
three more feet of depth pushes the house back on the lot and costs rear yard. Every one of
those decisions was rational. The elevation drawing, which shows the porch in silhouette,
never changed.

**Nobody was ignorant. Nobody was holding the whole.**

That reframes the problem entirely. This is not an education product and it is not a scolding.
It is **instrumentation** — a way of making visible, at the moment of decision, the
consequences that are currently only visible forty years later to someone standing on the
sidewalk. The house that does not belong is not the product of bad taste. It is the product of
two hundred locally sensible economies, none of which was ever priced against what it cost the
whole.

### What "belongs" means

Used throughout this project in a specific, non-nostalgic sense. A house belongs when it is
answerable to three things:

- **Its place** — the lot, the street, the settlement pattern, what the neighbours did and why.
- **Its climate** — why the Chesapeake stayed single-pile a century past the North, and it was
  cross-ventilation, not fashion.
- **Its lineage** — the actual line of practice it descends from, as distinct from whatever it
  quotes.

None of that requires the house to be old, or to pretend to be. A house that belongs is one
whose decisions have reasons that survive being asked about.

---

## III. The thesis

**A traditional house is a sentence in a language, and the language can be written down.**

That claim is the whole project, and everything in the repository is a consequence of it.

- **Elements are the alphabet.** A universal set of element slots that every style draws from
  and none owns. A style does not *have* a cornice; it *specifies* one. The test of the
  ontology is that adding a style should never require adding a slot — if it does, the
  alphabet was incomplete, not the style exotic.
- **Proportioning systems are the grammar.** Not tables of numbers but *functions*: give one a
  module and a context and it emits a fully dimensioned assembly, member by member. And not
  only the classical orders — brick course, timber bay, sash light, storey graduation and log
  module are grammar too, because most traditional buildings were proportioned from a material
  unit rather than from a column.
- **A style is a vocabulary** — a set of bindings and constraints on that universal alphabet.
  Choosing a style is not choosing a look; it is choosing which values the slots take, which
  variants are forbidden, and which proportional systems govern at what precedence.
- **A room is a word, a grouping is a phrase, a parti is a sentence pattern, a plan is a
  sentence.** Groupings — the hall-and-parlor pair, the centre-passage core, the entry
  sequence, the service core — are the scale people actually design at, and they are the hinge
  that makes rooms and volumetric skeletons composable.
- **And there are solecisms.**

That last one is the layer nearly every system omits, and it is the whole differentiator.

---

## IV. Why the solecisms are the centre of the project

A solecism is an error that breaks no written rule. The half-width shutter — a shutter that
could not cover its window if it closed, on a house where shutters have not closed in a
century — violates no code, fails no inspection, and is wrong. Anyone fluent sees it
instantly. Nobody fluent can easily say *which rule* it breaks, because the rule was never
written down. It lived in a trade.

Encoding a language without encoding its solecisms produces a system that can generate houses
and cannot recognise its own failures — what Chomsky called *colorless green ideas sleeping
furiously*: syntactically flawless, and dead. A generator with no critic will produce a
plausible house every time and a good house never, and it will have no way of knowing the
difference.

So the errors are named, and the naming matters. *The Four-Foot Porch. The Half-Width Shutter.
The Square Window. The Chimney That Is Not One. The Cardboard Gable. Dormers Off the Rhythm.
The Blank Wall On The Public Side.* A builder can say those out loud in a meeting. That is the
point of naming them: a fault with a name can be argued about, priced, and refused.

Three commitments follow, and each is load-bearing:

**Errors hang off elements, not styles.** The half-width shutter is wrong on every house that
has shutters. Filing it under a style would mean rewriting it once per style and letting the
copies drift.

**Style enters as an exception, and the exceptions matter as much as the rules.** A Georgian
five-foot portico is a fatal error by Craftsman rules and correct by its own. A system that
recites the rule without checking the exception is worse than no system, because it is
confidently wrong at a client.

**Every error carries three tiers of fix — the right one, the cheap one, and the dishonest
one — named that plainly.** The cheap fix is what actually gets built, so refusing to name it
is refusing to be useful. Naming the dishonest one is how the corpus stays honest while
staying useful: it does not pretend the substitution is unavailable, it says what it costs.

---

## V. What kind of thing this is

Not a taxonomy. Not a style guide. Not a plan generator with a historical veneer.

**A compiler.** The metaphor is exact, and it is worth taking literally because it tells you
what to build next:

| Compiler part | Here |
|---|---|
| Language specification | the schemas |
| Linters | the data checkers |
| Type checker | the plan validator |
| Front end | the composer and the geometry solver |
| Intermediate representation | a plan record — sized, placed, adjacency-legal, with every compromise annotated |
| Back end | walls, structure, roof, elevation, details |
| Object code | drawings a builder can price and permit |
| Runtime | the server through which a human or an agent drives the whole thing |

The intended pipeline, end to end:

> **A brief** — area, bedrooms, lot, style, and a paragraph about the household — resolves the
> **style** to its **kit**, its **constraints** and its **proportional systems**; the **partis**
> native to that style seed candidate **plans**, assembled from **groupings** of **rooms** on a
> **massing**; the **validator** scores each against rooms, adjacency, privacy, daylight,
> servicing, code, style constraints and the fault corpus; the **composer** repairs and returns
> several contrasting candidates, each with what it trades away; **geometry** places and
> dimensions them on the structural bay grid; **structure, roof and elevation** give them walls,
> a covering and a composed front; and **documents** come out the other end that a builder can
> price and a drafter can open.

A brief goes in one end. A house that belongs comes out the other. Everything in the
repository is either a layer of that pipeline or a check on one.

---

## VI. The architecture the thesis forces

Nine layers, each a precondition for the one above it. The order they were built in — spine
first, then breadth — is itself one of the project's most consequential decisions.

1. **The alphabet.** Element slots, volumetric massings, and room types. Three catalogues that
   every style draws from and none owns. Each massing carries **expansion logic** — how the
   type grows without breaking — which is the property a generative system most needs and
   which formal style descriptions almost never state. Each room carries the furniture that
   has to fit, with real clearances, a privacy rank, daylight depth, and typed directional
   adjacency, because a room is defined by what it must hold and who may pass through it.
2. **The grammar.** Proportional systems as functions, with one authority as the spine and the
   others as overlays carrying only their deltas. Each states its own invariants as evaluable
   expressions, and each records its **conflicts with building today** — the eight-foot ceiling
   against a Corinthian entablature, the insulated glass unit that cannot take true divided
   lites — with a severity and a ranked set of honest and dishonest substitutions.
3. **The vocabulary.** The style graph: a directed acyclic graph of traditions, families,
   styles and variants across two and a half millennia, related by typed edges.
4. **The bindings.** One kit per node, materialising every slot, so that selecting a style
   resolves to a directory of specified, inherited, open or forbidden elements — **with a
   source column showing which ancestor each value came from.** This is where a style becomes
   buildable rather than merely describable.
5. **The solecisms.** The fault corpus (§IV).
6. **The phrase layer.** Groupings, and the canonical plan diagrams that give a composer
   somewhere to start. Diagrams specify topology and roles only; dimensions are always pulled
   from the room catalogue, so nothing can drift.
7. **The critic.** The plan validator — built *before* the composer, on purpose, because a
   composer needs a fitness function and this is it.
8. **The generator.** The composer and the geometry solver.
9. **The interfaces.** A server an agent consults mid-conversation; interactive tools a human
   drives; a workbench for the people who develop plans for a living.

---

## VII. The commitments

These are what make the project distinctive rather than merely systematic. They are not
engineering preferences. They are a stance about knowledge, and they are the reason the output
can be trusted.

### On knowing, and on not knowing

**Unjudged is not passed.** Every check distinguishes evaluated-and-failed,
evaluated-and-passed, and *could-not-evaluate* — and is forbidden from collapsing the third
into the second. This is the single rule the project would least survive breaking. A system
that reports silence as approval is not conservative; it is lying by omission, at scale, about
things nobody will notice until the house is built.

**A rule the sources do not determine is deferred to the human, never invented.** Slots and
constraints marked as judgment calls are marked, not filled. A large fraction of the corpus's
rules are honestly in this category, and that fraction is a feature: it is where the tool hands
the decision back. *A rules engine that cannot admit ignorance will produce houses that violate
no constraint and are still dead.*

**Sources, or an honest mark.** Every number carries a source or is explicitly labelled as an
editorial judgment. Where no precedent exists at all, the value is labelled *invented* and the
label is conspicuous. Laundering a guess as a measurement is the worst thing that can be done
to this corpus, because it is undetectable later and it poisons everything downstream.

**Prose stays beside the test.** Making a rule executable *adds* a test; it never replaces the
human-readable statement. The sentence is what a person argues with; the test is what a machine
enforces; losing the sentence would make the corpus unauditable within a year.

**Open questions are numbered, not silently decided.** Every judgment call that could have gone
another way is written down with a number and left visible until someone rules on it. The
register of unresolved questions is a feature of the project, not a backlog to be embarrassed
by.

**Findings matter as much as code.** Every piece of work ends with what was built, what was
*found*, and what was deliberately not done. The findings are frequently worth more than the
diff — the discovery that a rule with no named intermediary forbids the very room invented to
satisfy it changed the corpus's model of adjacency, and it came out of a failure, not a
feature.

### On modelling

**A graph, not a tree.** Styles do not descend cleanly, and a folder tree can encode only one
parent. Shingle Style has at least four ancestors of comparable weight arriving by four
different mechanisms; name any one of them *the* parent and the building stops making sense.

**Claimed ancestry is not transmitted practice, and only the second one inherits.** This is the
most important modelling decision in the project. Greek Revival *references* Periclean Athens —
no American builder had a line of transmission from Greece. It *descends from* Federal
carpentry — the same carpenters, the same shops, the same author publishing a Federal manual
and then a Grecian one. Only descent carries the kit. A model that cannot express that gap will
quietly produce wrong buildings: a Greek Revival house detailed with genuinely Greek
construction is not a Greek Revival house, it is an archaeological reconstruction.

**Massing is not style. Rooms are not style.** A Foursquare can be dressed Craftsman, Colonial
Revival, Prairie or Mission with no change to the volume. Ornament and volume inherit along
different axes, and collapsing them is the error that makes generated architecture look
generated.

**Identifiers are permanent.** A wrong id is superseded, never renamed. Anything else breaks
every reference that was ever made to it, including the ones outside this repository.

### On building it

**The validator before the composer.** Build the critic first, always. It is the fitness
function, and a generator built before its critic optimises for nothing.

**The drawing is a render of the data.** Nothing is drawn that is not in the record, so the
drawing and the data cannot disagree. There is no decorative linework anywhere in this system.

**Several candidates, never one — and never call a plan good.** The generator returns
contrasting options, ranked, each stating *what it trades away*, and it declines to endorse
any of them. *The corpus can say what is wrong. It cannot say what is alive.* That division of
labour is enforced structurally rather than promised, because a system that names a winner has
quietly taken a judgment that belongs to a person.

**The generator refuses, and refusals are content.** It will not invent a room the diagram has
no place for. It will not drop a room that is load-bearing for a rule. It will not present an
assumption as a fact — everything the brief left silent is logged as a decision the machine
made, not a fact about the world. A refusal is the system working.

**Compromises are counted and reported.** When a room cannot be made to fit the structural
grid, the cut is allowed off it — and counted, because a cut off the bay line is a joist run
that does not land on a bearing wall. *Eleven upper wall lines do not continue to a wall below;
each is a transfer beam* is a sentence a builder can price. Hiding it would be cheaper and
would make the system worthless.

---

## VIII. Why now, and not in 1970

Two things have changed, and only one of them is obvious.

The obvious one: enough of building practice is documented — treatises, measured surveys, HABS
drawings, preservation briefs, trade literature — that the language *can* be encoded without
inventing it.

The one that matters more: **an encoded language is now consultable.** Vignola could publish a
table. He could not publish something that would answer a question. A pattern book on a shelf
transmits fluency only to the reader disciplined enough to look things up, in the right order,
before deciding — which is to say, almost nobody, almost never, and certainly not at the moment
a value engineer is shaving a porch.

A corpus that an agent can consult mid-conversation is a different kind of object from a book
with the same contents. It can be asked. It can answer *"that is a fault everywhere except in
this style, and here is why"* at the moment the decision is being made rather than in a review
six months later. It can say *"I cannot evaluate that"* — which no book has ever done.

This is why the machine-readable form is not a distribution channel for the knowledge. **It is
the thing that makes writing the knowledge down worth doing again.**

---

## IX. Who this is for, and what changes for them

**The production builder.** A very large market builds houses that are structurally sound,
code-compliant, sellable, and do not belong anywhere. Not because anyone chose that, but
because fluency does not scale and every cost decision is made locally. What changes: the
consequences become visible before the drawings are released, in the builder's own units —
dollars saved, dollars cost, and which fix is the cheap one.

**The plan-development lead.** The person who actually owns the catalogue. Fluent in plans,
framing, cost and code; not fluent in classical proportion, and under no obligation to become
so. What changes: they can ask for four plans and get four plans with an honest account of what
each gives up — and they can move a wall and watch what it breaks.

**The architect and the classicist.** The people whose knowledge this is. The system is not
built to replace them; it is built so that their judgment is available in rooms they are not
in. What changes: their reasoning becomes auditable and arguable rather than authoritative —
every claim reaches its source, and disagreeing with the corpus is a normal, supported act.

**The people who live there.** They will never see any of this, and they are the point. They
will notice only that the porch can be sat on, that the rooms have light at the back, that the
front door is where a front door goes, and that the house looks like it has been there. None
of that is style. All of it is fluency.

**The discipline.** A side effect worth naming: writing this down makes traditional
architecture *falsifiable*. Rules become tests, tests can fail, and judgment calls are numbered
and await a ruling. That is a rare and healthy condition for a body of knowledge that has
mostly been transmitted by assertion.

---

## X. What this is not

- **Not the automation of the architect.** The system is built to refuse, to defer, and to
  present options it will not choose between. Every one of those is a place where a person is
  required by design.
- **Not style policing.** The corpus records what a style *does*, with its exceptions, and it
  records honest and dishonest substitutions side by side rather than forbidding the cheap one.
- **Not historical reconstruction.** The aim is houses that belong, built now, with today's
  code, today's materials and today's budgets. The recorded conflicts between historical
  systems and contemporary building are treated as the central problem, not as an embarrassment.
- **Not a compliance engine.** The code layer is advisory model text and is labelled as such.
  Rendering advice as compliance would be the one failure with legal consequences.
- **Not complete, and not pretending to be.** Several of the world's building traditions are
  absent, some layers are thinner than others, and the corpus says so in its own documentation
  rather than in a footnote.

---

## XI. The horizon

Directions the thesis implies, stated as directions rather than as a plan:

**Proof, not preference.** A generator that can only hill-climb toward a good answer cannot
tell you that a brief is *impossible* in a given diagram, and why. That is the single thing a
plan-development partner most needs to hear early, and hearing it late is expensive. The system
should be able to return a named conflict set — *these three requirements cannot hold at
once* — rather than the least-bad plan with no warning.

**Leaving the system.** An intermediate representation that cannot leave in a format a drafter
opens is an unfulfilled promise. Drawings, models, and a details library — generated from the
data rather than written, so they cannot drift from it.

**Reading drawings, not just writing them.** The system cannot yet read a plan. A path from a
drawing to a record is what would let historical surveys, a builder's back catalogue, and the
reference corpus of good and bad examples flow into the critic at volume — which is also the
fastest way to find out where the critic is blind.

**Peer trunks.** Several traditions are modelled in depth and several major ones are absent
entirely. The schema extends to them without modification, and one node in the graph already
points at an ancestor the graph cannot name. The claim to have written down *a language of
building* is not earned until the alphabet can say what a longhouse and a hall-house have in
common.

**Cost as a first-class layer.** The seed exists: some errors already record what was saved by
getting them wrong. A cost model over a composed plan is what would let a builder compare
candidates in the only currency that ever decides anything — and it should wait until there is
a partner with real numbers, because inventing them would violate §VII.

---

## XII. What success looks like

Not a taxonomy. Not a complete corpus. Not a generator that impresses architects.

**Success is that a production builder can speak the language.** That a brief goes in one end
and a drawing comes out the other that a builder can price, a drafter can open, an inspector
can pass, and a classicist can criticise on the merits rather than dismiss on sight. That the
system says *I don't know* often enough to be trusted when it says anything else. That every
number in a house can be traced to who said it and why.

And, finally, the only test that matters, which no checker in this repository can run:

**A house built in this language should feel, to the people who live there, like it belongs.**

Everything else is instrumentation for that.
