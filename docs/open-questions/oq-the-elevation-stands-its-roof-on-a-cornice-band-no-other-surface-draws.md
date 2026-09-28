# oq/the-elevation-stands-its-roof-on-a-cornice-band-no-other-surface-draws — one ridge, two heights

*Status: OPEN · Raised in: WP-14.6, the adversarial audit of Phase 14 (27 Sep 2026)*

**OPEN — the elevation draws every roof it draws 2.5 to 3.4 ft higher than the section, the roof
record and the model do, and which height is right is a ruling rather than a fix.**

`build/elevation.py` computes `grade_to_true_eave_in` as roof.py's `grade_to_eave_ft` **plus** the
frieze and the cornice (`eave_cornice()`'s `frieze_height_in + cornice_height_in`), and
`build/render_elevation.py` lifts the whole roof silhouette -- and every chimney stack on it -- by
that band. `build/structure.py` and `build/roof.py` model no frieze or cornice at all, so the
section prints roof.py's eave and ridge and `build/scene.py` builds its roof planes there. The
elevation's own record has said so since WP-3.2 (*"Not fed back into those files' own records;
recorded here as this file's own number"*) and `docs/elevation.md` repeats it. Nothing measured it,
and the sheet said nothing until WP-14.6.

Measured by census row V19 on every plan whose elevation draws (the entrance face; every face
carries the same lift):

| plan | eave drawn | roof record, section, model | band | ridge drawn / record |
|---|---|---|---|---|
| `tidewater-georgian-careful` | 28.51 ft | 25.44 ft | 36.8 in | 41.79 / 38.72 |
| `good-03-parlor-drawing-room-house` | 17.35 | 14.28 | 36.8 | 24.55 / 21.48 |
| `good-05-lobby-gallery-mansion` | 31.02 | 27.67 | 40.2 | 37.46 / 34.11 |
| `good-07-diamond-plan-house` | 18.74 | 15.39 | 40.2 | unjudged |
| `good-02-portico-library-house` | 15.95 | 13.16 | 33.5 | unjudged |
| `bad-05-two-story-spec-colonial` | 26.00 | 23.21 | 33.5 | unjudged |
| `spec-builder-colonial` | 23.49 | 20.98 | 30.1 | unjudged |
| `bad-01`, `bad-02`, `bad-07` | 14.56 | 12.05 | 30.1 | unjudged |
| `bad-03-narrow-lot-townhome` | 34.09 | 31.58 | 30.1 | unjudged |

**Where it shows.** The Drawing Set puts the section (EAVE 25'-5", RIDGE 38'-9" on the Tidewater
plan) beside an elevation whose roof springs from 28'-6" and peaks at 41'-9". The Round lays the
elevation plate over the model at each named view, so the plate's roofline stands 3.07 ft above
the model's roof planes, and its stacks 3.07 ft above the model's chimney axes (46.72 ft in the
record, 49.79 ft on the plate). The DXF elevation takes the elevation's height as well
(`export_dxf.py` reads `grade_to_true_eave_in`).

**The corpus's own words point the other way, and they are evidence, not a ruling.**
`facade-classical`'s frieze rule places the frieze *"between the top-storey window heads and the
bed of the cornice. This band exists to give the cornice somewhere to sit and the upper windows
somewhere to stop ... above about 18 in the top of the wall reads as a blank attic and the building
has grown a storey it does not have."* That puts the band INSIDE the wall the storeys build, below
the eave, not stacked above it. Measured on the drawn sheets, the gap from the entrance front's top
window heads to the cornice bed is **45.2 in** on the Tidewater plan and **36.4 to 52.8 in** on the
six other fronts whose top window stands in the storey under the eave (on `bad-03` and `good-05`
the front's top window is a storey lower, and `bad-02` and `good-03` put none on the entrance
front, so theirs are not comparable) -- every one outside the pack's own 6 to 18 in. Part of that is the
wall itself (32.9 in from the Tidewater upper heads to roof.py's eave, which `sash-light`'s
0.75-0.82 head rule produces); the other part is the band stacked on top.

**What must be ruled before anything moves:**

1. Is the eave the top of the wall the storeys build (roof.py's, and the section's and the model's
   today), with the frieze and cornice hung on the wall below it -- or is it the top of a cornice
   stacked above that wall (the elevation's)? The first is what `facade-classical` describes; the
   second is what WP-3.2 built.
2. If the first: the elevation's frieze and cornice move down into the wall, the roof and stacks
   come down 2.5 to 3.4 ft on every sheet, and the head-to-cornice gap is then the WALL's, which on
   the Tidewater plan is still 32.9 in against 6 to 18 -- a separate question about the upper
   storey's head height that this one surfaces and does not answer.
3. If the second: roof.py, the section and the scene each need the band, and roof.py's
   `grade_to_eave_ft` stops meaning what its name says.

Either way the fault corpus moves: `wall_height_water_table_to_cornice_in` is measured from
`grade_to_true_eave_in`, and the elevation's roof measurements are read off the lifted silhouette.

**What WP-14.6 did, and deliberately did not do.** It measured the lift (census V19, pinned by
identity on all eleven plans, and strict: a disagreement the sheet SAYS is still a disagreement),
and it made every elevation say so beside the roof -- the eave and ridge the roof record, the
section and the model state, the ones drawn, and NOT RECONCILED. It moved no roof, because moving
one is choosing an answer to (1).
