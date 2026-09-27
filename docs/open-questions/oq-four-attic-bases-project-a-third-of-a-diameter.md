# oq/four-attic-bases-project-a-third-of-a-diameter — the corpus says Palladio gives his Doric base a sixth

*Status: OPEN · Raised in: WP-14.5, the source leg (27 September 2026)*

**Four order packs record an Attic base whose plinth projects 20 minutes and whose upper torus
projects 16, in a module of 30 minutes to the semidiameter: `palladio-doric`, `chambers-doric`,
`chambers-ionic` and `chambers-corinthian`.** Drawn, each plinth stands out a third of a diameter
from the shaft (4 in on a 12 in column). The corpus's own account of Palladio says he gives the
Doric base a sixth, which in that module is 10 minutes.

## The evidence, all of it the corpus's own

- `palladio-corinthian`'s base note: *"with a projecture of a fifth of a diameter (12 minutes) -
  greater than the sixth Palladio gives the Tuscan and Doric bases"*.
- `palladio-tuscan`'s base note: *"Projection of the whole base a sixth part of the diameter, i.e.
  10 minutes each side"*, and its record carries 10.
- `palladio-doric`'s module is the semidiameter in 30 minutes, Palladio's stated exception, so a
  diameter is 60 minutes and a sixth of it is 10.
- Not one of the four packs' notes states where its 20 and 16 come from. Palladio's Doric base
  notes quote Ware for every HEIGHT. Chambers's give his weathering rule, that a moulding's
  projection stays under the member above, and no figure. The plinths carry `confidence: high`.
- Two authors, four records, identical figures. That reads more like one reading copied than like
  two authors agreeing, but nothing records which.
- For scale, as the plates print it: Palladio's Corinthian base a fifth of a diameter, his Tuscan a
  sixth, Vignola's Doric 0.21 and every other base in the corpus between 0.17 and 0.21.

`palladio-corinthian`'s note is carried in `build/note_figures.json` as a claim on
`palladio-doric`'s record, so census N1 holds it as a pinned disagreement, not a paragraph nobody
re-reads. The Chambers records have no note stating a figure for them to be held to.

## Why this is a question and not a patch

- The sixth is a paraphrase in another pack's note, not a quotation of Ware's Doric chapter. The
  rule for a record that disagrees with its authority is to fix it only where the corpus's own
  quotation proves it (the OQ 81 precedent), and a paraphrase in a sibling is not that.
- Chambers is not Palladio, and nothing here says what Chambers gives the Attic base.
- Setting a plinth to 10 would leave its upper torus's 16 without a basis, and scaling it in
  proportion would invent a figure.

Ware 1738, Book I chapter XV, settles Palladio. Chambers 1759, *Of the Doric Order*, settles
Chambers. Both are in `Plan Examples/Plates/WANTED.md`.

## Where it lives

`proportions/overlays/palladio-doric.json`, `chambers-doric.json`, `chambers-ionic.json`,
`chambers-corinthian.json` (each `base`); `palladio-corinthian.json` (`base_plinth`'s note);
census N1.
