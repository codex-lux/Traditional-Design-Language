# oq/the-window-surround-slots-were-never-split — the record says which surround a wall takes, in a sentence its slots do not carry

*Status: OPEN · Raised in: WP-14.3, trim, openings, eave, section, roof (27 September 2026)*

**Twenty-two of the 41 styles the elevation draws reach a window-surround slot that makes a flat
architrave AND a bare masonry reveal both canonical, so the elevation cannot say which the house
has, and says so on the sheet.** All 22 are masonry walls, and all 22 read the slot from
`georgian-colonial-american`.

That node's own record answers the question, in its rule sentence:

> On a frame wall the window has a flat architrave of 5 to 6 in with a crown moulding; on a
> masonry wall it has no surround at all and its expression is the reveal and the arch.

Its note says why the slots do not carry the answer:

> MIGRATED 0.3.0 from 'window_surround', which conflated two trades. This record was carried into
> both heirs unchanged and NEEDS SPLITTING BY HAND: keep only what belongs to
> window_surround_masonry.

So `window_surround_masonry` and `window_surround_wood` carry the same variants, and on the node
itself they list `none-masonry-reveal` twice, once permitted and once canonical. On 15 of the 22
the two resolved slots are identical.

## What WP-14.3 did

Nothing to the record. The elevation reads the slot its wall uses and never the sentence, so its
refusal names the slot: *"WINDOW SURROUND NOT DRAWN — THE KIT'S WINDOW SURROUND MASONRY SLOT MAKES
FLAT ARCHITRAVE WITH CROWN AND NONE MASONRY REVEAL BOTH CANONICAL, AND DOES NOT SAY WHICH THIS
HOUSE HAS"*. The scene files the same refusal. Census check V16 holds the sheet to it. The reveal
is its own slot (`reveal_masonry`) and is drawn. So what is drawn on all 22 is what the rule
sentence gives a masonry wall; only the words disagree with the record's prose.

## Why this is a question and not a patch

The split the note asks for is half given by the rule sentence and half not:

- The two canonical variants split cleanly. `none-masonry-reveal` belongs to the masonry slot, and
  `flat-architrave-with-crown` with its 5 to 6 in band belongs to the wood slot. Done, the 22
  refusals disappear, and a frame style inheriting the wood slot has one canonical architrave, of
  a width stated as an editorial band. No surface draws that yet.
- The two permitted variants are not placed by any sentence. `rubbed-brick-jamb` reads as masonry
  and `backband-architrave` as joinery, but that is a reading of the ids, and it is the kind of
  call this corpus writes down as editorial or refers to a person.
- It moves the resolved kit of every node that inherits the slot, not just the 22 drawn here.

## Where it lives

`kits/georgian-colonial-american.kit.json` (`window_surround_masonry`, `window_surround_wood`) and
its source; `build/elevation.py::window_surround`; `build/render_elevation.py` and `build/scene.py`
for the refusal; census check V16.
