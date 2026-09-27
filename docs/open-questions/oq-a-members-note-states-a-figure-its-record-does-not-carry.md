# oq/a-members-note-states-a-figure-its-record-does-not-carry — thirteen figures the notes beside them contradict

*Status: OPEN · Raised in: WP-14.5, the source leg (27 September 2026)*

**Census N1 reads 265 order-pack members whose note states a figure about a recorded one, and 14
of them disagree.** One is the Palladio Doric base, which has its own question
(`oq/four-attic-bases-project-a-third-of-a-diameter`). This file is the other thirteen, across
nine packs.

- Each is pinned BY IDENTITY in `tests/fixtures/ink_known_disagreements.json`, so none can move
  without the census saying so.
- None is fixed. The rule is OQ 81's: correct a record only where the corpus's own quotation
  proves it. Each of these rests on a reading that a plate would settle.

They fall into five shapes. Figures are in each pack's own parts.

## 1. Two authorities in one note, presented as agreeing

- **`vignola-doric`, base plinth: 5 parts of projection recorded.** The note reads:

  > *"Ware's Doric table gives 1/6 D for both the height and the projection of the plinth - 4
  > parts. Vignola gives the whole base 1 module of height and 5 parts of projection, 'poco meno
  > della quinta parte del diametro'. Base and plinth totals agree between sources."*

  - The heights agree. The projections are 4 and 5, and the note does not say so.
  - The Italian gloss means *a little less than a fifth of the diameter*. A fifth of the 24-part
    diameter is 4.8, and 5 is a little more than that. The gloss contradicts the figure it glosses
    in direction as well as in value.
- **`vignola-doric`, capital abacus: 5 1/2 parts recorded.** The note reads: *"Capital projection
  5 1/2 parts. Ware: the abacus projects one sixth on each side beyond the upper diameter of the
  shaft."*
  - A sixth of the diameter is 4 parts, or 3 1/3 if it is a sixth of the 20-part upper diameter.
  - One reading would reconcile the two authorities: the plain abacus face at Ware's figure, and
    the cyma crowning it at Vignola's.
  - The record carries neither. The abacus, its cyma and its top fillet all get the same 5 1/2, so
    the crown stands no further out than the face it crowns.
- **`vignola-tuscan`, capital abacus: 5 parts recorded.** The note reads: *"Ware: the abacus is
  7/6 D across, not counting the fillet above it, and projects its own height from the face of the
  architrave."*
  - The abacus is 3 parts high, so *its own height* gives 3.
  - *7/6 D across* is 28 parts, which is 4 beyond the radius of the 20-part upper diameter.
  - The pack's own top-level notes say the capital's 5 parts are *"firmly sourced and agreed by
    three independent witnesses"*, and Ware is one of them.
  - As this note quotes him, Ware gives 3 or 4, never 5. At 3, the abacus would stand inside the
    4-part ovolo below it, which is itself evidence that the quotation is being read against the
    wrong face.

## 2. A note whose own arithmetic contradicts its words

- **`vignola-corinthian`, capital: the two acanthus rows and the caulicoli are recorded at 12 parts
  each.** The note reads: *"Bell 2 modules (36 parts) ... Ware divides the bell into three equal
  sixths of a diameter: lower leaves, upper leaves, caulicoli."*
  - Three sixths of the 36-part diameter would be 6 parts each, filling only half the bell.
  - Three equal divisions of the note's own 36-part bell are 12 each, which is two sixths apiece.
  - The record keeps the division and not the stated unit.
  - The pack's top-level notes repeat the phrase word for word, and then call it *"how the 12 : 12 :
    12 : 6 encoded here is arrived at"*.
  - It is very probably a slip for thirds. It is not corrected here, because the phrase is written
    as Ware's and no page of Ware has been read.

## 3. A division the note quotes and the stack does not carry: Gibbs's Ionic capital

- **The ovolo and the bead.** The note reads: *"divide the height B C into eight parts, two of them
  give the Ovolo, one the Bead"*. That makes the ovolo twice the bead. The record carries 4 1/2 and
  1 1/2, which is three times.
- **The abacus.** The note reads: *"divide into two parts, and the upper half into four, of which
  you must give three to the Ovolo, and one to the Lift"*.
  - The record's two abacus members, the ovolo at 2 1/4 and the lift at 3/4, keep the three to one.
  - There is no member for the plain lower half. Either the two members are the whole abacus given
    over to its upper half's mouldings, in which case the note's figures would be 1 1/8 and 3/8, or
    the record has dropped a plain face of 3 parts.
  - All four members are apportioned and marked low confidence.

## 4. A projection rule quoted and not followed: Gibbs's architraves and pedestal caps

### The architrave

- **The Corinthian and the Composite.** `gibbs-corinthian`'s note quotes Plate XXVI: *"'The
  Architrave projects one fourth of its height' in the Tuscan and Doric and half of it in the other
  three orders"*. `gibbs-composite`'s note says the same. Their architraves are 21.6 parts high,
  so half is 10.8. The records carry 4, both in the member stack and in the entablature summary.
- **The Ionic.** `gibbs-ionic`'s own note quotes the quarter for the Ionic, which the Corinthian
  note places among the "other three" orders. **The corpus's two readings of one plate disagree
  about which orders the half applies to.** The Ionic records 4 in its stack and 5 in its summary,
  against a quarter of 19.44, which is 4.86.
- **The Tuscan.** `gibbs-tuscan` records 1 1/2 on the listel against the quarter's 3, while its own
  entablature summary records 3.
- **The open reading.** A plate would settle what an architrave's projection is measured from, and
  what *"half of it"* refers to.

### The pedestal cap

- **The rule.** `gibbs-composite`'s note reads: *"Gibbs, Plate XXIV, on all pedestal caps: 'their
  projection is to their height as two to three.'"* Two thirds of an eighth of the pedestal is a
  twelfth, which is the base's height. That is why `gibbs-tuscan`'s note can also say *"The Cap
  projects the same as the Base"*.
- **Measured across all five orders:**
  - The Tuscan (4 3/8) and the Doric (5) follow the rule.
  - The Ionic records 7 against the rule's 8.1, the Corinthian 8 against 9, and the Composite 8
    against 9. Each is short by about a part.
  - In each of those three, the base projects the same short figure as its cap.
- **Only the Composite reaches N1**, because only its note quotes the rule. **A note that states
  nothing cannot disagree, so the census's population is bounded by what the transcriber chose to
  quote.** The Ionic's and Corinthian's shortfall is recorded here and nowhere else.

## 5. A figure stated in words over an illegible plate: Benjamin's Doric

- **What the notes say.** The necking's note in `benjamin-doric` quotes Benjamin: *"the face of
  the architrave is in a vertical line with the upper fillet of the capital, which projects three
  and a half minutes from the neck of the column"*. The abacus's note repeats it in its own words.
  The plate's numerals are *"not legible in any scan reached"*, as the necking's note says.
- **What the record carries.** The capital's only fillets are its two annulets, and the record gives
  the annulets 2, apportioned. The member is marked `high` confidence, but that is about its
  2 1/2-minute height, which Benjamin does state.
- **The reading.** Taking "the upper fillet" as the upper annulet is a reading, not a quotation.
- **A second consequence.** If the reading holds, Benjamin puts the architrave face 3 1/2 minutes
  outside the neck.

## Why none of these is fixed

- **Each rests on a reading.** The open readings are:
  - which member a phrase names;
  - what a projection is measured from;
  - whether a sixth is of the lower diameter or the upper;
  - whether a phrase is the author's words or the transcriber's slip.
- **The craftsman casing was a different kind.** It was corrected in the same package because its
  note cited a stock series (*"1x4 (3 1/2), 1x6 (5 1/2)"*) and the record carried the nominal size
  instead. That record contradicted its own citation. These records contradict a reading of one.
- **Notes are not edited to match their records.** Changing the Corinthian note's "sixths" so that
  it agrees with its record would destroy the only evidence that the two were ever read
  differently.

## What settles each

The pages are listed under class 0 of `Plan Examples/Plates/WANTED.md`, under each book:

- **Vignola, *Regola* (1562):** the Doric base and capital (Tavole X–XV) and the Tuscan capital
  (Tavole IV–VIII), with Ware's American edition beside them.
- **Gibbs, *Rules for Drawing* (1732):** Plates X–XI (the Ionic capital), XXIV (the pedestals) and
  XXVI (the architraves).
- **Benjamin, *The Practical House Carpenter* (1830):** Plate VI, fig. 2.
- **Ware's Corinthian chapter:** the bell's division.

## Where it lives

- Census N1.
- `build/note_figures.json`: each claim, with the reading it rests on.
- `build/plate_review.py`.
- The packs named above.
