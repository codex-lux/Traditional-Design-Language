# oq/the-facade-layer-counts-a-dependencys-windows-as-bays-of-the-front — an eighth layer reads the main block as the whole house

*Status: OPEN · Raised in: WP-13.5, the container (16 September 2026)*

**`axis.front_openings` sweeps every room on a level and keeps every window and exterior door
whose `wall` is the entrance front, with no element filter of any kind; `facade.rhythm` then
derives the bay centres across `footprint.bays` and the MAIN BLOCK's own width, saying so in its
own comment — *"Bay centres across the block's OWN width"*. So the moment a plan has a west wing
with south-facing windows, the wing's openings are measured against the main block's rhythm and
convicted of standing between its bays.**

Measured on `plans/tidewater-georgian-careful.json` with the service programme in its dependency
(`engine="heuristic"`, deterministic, one run):

    front-opening-in-no-bay   0 -> 4       ALL FOUR in the wing
      breakfast's window at -27.905 ft on the S front
      kitchen's   window at -18.405 ft
      kitchen's   door   at -14.405 ft
      kitchen's   window at -10.405 ft
    main block: 45.0 ft wide, 5 bays, x from 0.0

Every one of those coordinates is NEGATIVE — they are west of the main block's west wall, in a
dependency that starts at x = −34.0. The finding's own words are *"more than half a bay from
every one of the 5 bay centres the plan implies"*, which is true and is not a defect in the
house: **a dependency's windows are not bays of the front.** A five-part Palladian's wings are
not counted into the main block's five.

**On `engine="cp"` the same plan produces 0 of these, and the reason is worth reading rather
than the count.** `axis.front_openings` returns nine placed openings on the heuristic and FIVE on
CP — `drawing` ×2, `passage` ×2, `porch` ×1, every one of them in the main block — with
`declared_but_unplaced` at 3 and **7** respectively. The wing's south openings are not seated
somewhere the check forgives; on that placement they are REFUSED outright, so the facade layer
never sees them. So the COUNT is engine-dependent and the layer's blindness is not: the same
function would convict them the moment a placement drew them.

## Why this is not simply another item of an existing question

`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` named six layers, WP-11.6
taught all six, and `geometry_report.multi_element.not_element_aware` has read `[]` since. Then
WP-11.14 found a SEVENTH — the drawing — and this is an EIGHTH. `build/facade.py` and
`build/axis.py` were both written at WP-11.7, after the six were counted and after the
disclosure that counts them stopped being able to grow. A falling counter that reached zero is
not a proof that nothing else reads the footprint as the building; it is a proof that the six
named in 2026-09-04's ruling do not. **The list was closed and the tree kept growing.**

## What a ruling has to settle

1. **Which openings compose the front?** The obvious answer — only the main block's — is not
   obviously right: a five-part front IS read as one composition, wings included, and
   `groupings/dependency-and-hyphen.json` says the dependency *"repeats the main block's window
   proportion and cornice at reduced scale"*, which is a statement about the whole elevation.
2. **If wings compose, against what rhythm?** The wing has its own width and its own bay count;
   the main block's module may or may not govern it. Nothing in the corpus states a rule.
3. **And is `front-bay-with-no-opening` measuring the same population?** On the same edited
   record that count fell 11 → 3 under CP, which is the rhythm getting shorter with the block
   rather than the front getting better; the two findings are two halves of one comparison and
   whichever way (1) is ruled, both must read the same set of rooms.

## What must not be done

Do not silence the finding by filtering `front_openings` to untagged rooms before the ruling.
That is one of the three answers to question 1 and is being presented here as a question
precisely because the corpus states the opposite in `dependency-and-hyphen`'s own prose. And do
not read the heuristic's 4 as the size of the problem: it is one engine's placement of one plan,
and the population it is drawn from is every window a wing puts on the entrance front.

---

## Amendment, 17 September 2026 — it is not only a reporting defect; it decides the composer's product

This question was raised against the shipped plan, where the four convictions are findings a
reader sees on a sheet. Measured since, on `briefs/family-georgian.json` with `revise=False`: the
same blindness convicts the COMPOSED `centre-passage-double-pile` candidate, and there the
findings are FATAL — *"The Bay That Broke the Symmetry: 4 against at-most 0"*, against **2** on a
`git archive` of `c39f3f8`, the commit before the container.

`compose._sort_key`'s primary key is the fatal count, so those two extra fatals are two thirds of
what took the brief's own native diagram from second place to **out of the returned set entirely**
(fit 7.0, score 69.7, against a returned leader at fit 3.6 and score 56.5). The full series and
the other three fatals are in
`oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room`'s own amendment.

**So this question's priority is not a reader's convenience.** Until `axis.front_openings` takes
an element filter, a house with a service wing cannot be offered by the composer for a brief whose
style is the wing's own — and the reason never reaches any surface, because the finding says the
window is off the bay rather than that the instrument measured the wrong building.
