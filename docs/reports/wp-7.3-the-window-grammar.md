# WP-7.3 — two layers decide two different things, and neither may answer for the other

*27 August 2026. Phase 7, package 3 of 3.*

## The question, and why the entry already contained its answer

OQ 78 said a window has a `unit_type` field and nothing fills it, *"because nobody has ruled
where the authority lives"* — and then named the shape of the ruling: *"The question is not
what the types are — the corpus knows them — but which layer decides."*

**The ruling.** `openings/window-grammar.json` decides the window's **ROLE**: whether an
opening is an ordinary lit window, a high transom band, a borrowed light off another room, a
fixed or obscured light in a wet enclosure, or the one deep bay a library takes. That is a
**plan** fact — it follows from what the room is for, which wall it is on and which storey it
sits in, and it is the same in a Georgian house and a Tudor one. **The kit decides the SASH
KIND** — double-hung, casement, leaded casement — which is what `window_type` has always held.
A room may not state a sash kind and a kit may not state a role. Rooms stay silent, so the fact
is not in three places.

## The measurement that corrects this entry and everything built on it

The flat kit files carry `window_type` as `status: empty` on **120 of 159**, and that is the
number I reported to Lucas when scoping this work — three quarters of the corpus apparently
unable to answer even the style question.

**Reading those files is reading the wrong layer.** Resolved through the lineage by
`build/resolve_kit.py`, **119 of 159 styles answer** and 40 do not. `tidewater-georgian` — this
corpus's own worked example — states no `window_type` and inherits `double-hung` from
`georgian-colonial-american`, with six variants forbidden.

A first version of the resolver read the flat file. It would have reported COULD NOT EVALUATE
for three quarters of the styles the corpus answers for perfectly well: **the "unjudged is not
passed" rule run backwards**, which is its own kind of lie and a harder one to notice, because
it looks like caution. The answer now travels with its provenance — `unit_type_from` — because
the cascade delivers what nobody bound (OQ 51) and a reader has to see that Tidewater's sash
kind is its ancestor's rather than its own.

## What was built

- **`openings/window-grammar.json`** — 7 room rules, 4 class defaults, one named default.
  Editorial throughout, `judgment: true`, every rule quoting the room-record prose it reads.
  A sibling of the door grammar and deliberately not part of it: that file's domain is the
  1,890 room pairs, this one's is the room against the wall it is lit from, and
  `schema/opening-grammar.schema.json` locks `opening.type` to the door enum.
- **`build/check_windows.py`** — seven checks, wired into `check_all.py`. It **reuses
  `check_openings.check_basis`** rather than growing a second copy (that function took a
  `source` argument for the purpose), and it **caught three loose transcriptions while this
  file was being written** — quotes I had paraphrased by a word or two. An editorial call
  whose citation cannot be checked is a guess wearing a citation.
- **Totality, published.** All 120 (room type × wall exposure) resolutions land on a named
  rule; **112 of 120 (93.3%) land on a rule that read something** and the 8 fall-throughs are
  printed, exactly as the door grammar prints its 0 of 1,890.
- **`compose.py`** stamps `role`, `role_rule`, `unit_type`, `unit_type_from` and
  `unit_type_unresolved`, and logs a JUDGMENT WITHHELD line for units whose kind nobody
  authored. The kit's variant-level `forbidden` bindings refuse through `resolve_kit`'s
  existing machinery — 17 kits forbid a `window_type` variant by name, 5 forbid
  `special_window` outright.

Measured on a composed Tidewater Georgian: **27 `lit`, 2 `bay` (the library), 2 `obscured`
(the bathrooms)**, all 31 given `double-hung` by the cascade.

### "No window here" had to become an answer

A first cut left interior walls to the last-resort default, so **61 of 120 resolutions read as
an ordinary lit window on an interior wall** — a grammar inventing 61 openings nobody asked
for. `wg-class-interior-none` makes *no window* a stated rule with a basis, and the
fall-through fell to 8.

## Two things refused, and the refusals are the interesting part

**No closed `unit_type` enum.** A first draft published one — `double-hung`, `casement`,
`fixed` — and the kits use **~40 free strings**, several of which are not sash kinds at all:
`clean-rectangle-flat-architrave` (8 styles), `horseshoe-arch` (7), `round-arched-paired` (5)
describe an opening's *shape*, and `double-hung` (22) and `double-hung-sash` (32) are the same
thing spelled twice. An enum here would have been a second spelling of the kits' vocabulary,
drifting the moment either side changed — the failure behind `REF_RE`/`CITE_RE`/`parseCite`.
`unit_type` carries the kit's resolved string verbatim, and `check_windows.py` **fails the
build if this file ever publishes a closed enum again.** Normalising the kit vocabulary is a
change to the kit corpus with its own ruling, and it is the open half of OQ 78 now.

**No bay geometry.** `wg-library-bay` and `wg-hall-dais-window` write the role because the
rooms state it outright — *"The elegant historic answer is the BAY OR ORIEL: one deep window in
a projection lights the room and takes almost no wall from the shelving"* — and nothing in this
corpus draws a projection: `$defs.geometry` is four numbers with `additionalProperties: false`,
and the slicer, the CP model, both renderers and both exporters are all rectangle-only. **The
decision is in the record and the geometry is refused**, which is the honest split. Inventing a
projection depth would be the laundering this corpus exists to prevent.

## What was deliberately not done

- **Rooms do not state a per-opening preference.** The register warned this would put the same
  fact in three places; the two-layer split makes it unnecessary.
- **No normalisation of the kit `window_type` vocabulary** — measured, named, and left to its
  own ruling.
- **No bay, bow or oriel geometry**, and no schema version bump: 0.3.0 stands.
