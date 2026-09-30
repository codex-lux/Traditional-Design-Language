# oq/the-rake-is-drawn-as-an-edge-and-carries-no-member — the half of the gable end nobody ruled

*Status: IN PROGRESS (ruled 30 September 2026, B3; executed by WP-16.9) · Raised in: WP-16.5, one cornice and the gable end (30 September 2026)*

**The gable end's roof edge is a line, and no record the elevation reads dimensions anything
there.** This is the half of `oq/the-gable-end-draws-a-full-cornice-whatever-the-kit-says-of-the-return`
that the ruling of 29 September left open (*"the rake half of this entry is not ruled"*).

**What WP-16.5 draws at the rake.**

- Where no band crosses the gable end, the gable wall runs up to the rake as one outline, and its
  coursing runs up with it.
- The rake is the roof's own edge: one line, drawn in the roof's pen (the SVG's `.rk`, the DXF's
  roof polyline).
- It carries no raking cornice, no bed mould and no overhang. The roof record models no rake
  overhang, so every surface draws the roof stopping at the gable wall.

**What it stopped publishing.** Since WP-3.2 (`f3d89f6`, 23 Aug 2026), `rake_overhang_in` had
published the EAVE cornice's projection as the rake's overhang:

- on the spec Colonial and four other plans, 8.612 in;
- on bad-05 and good-02, 9.568;
- on Tidewater and good-03, 10.525;
- on good-05 and good-07, 11.481.

`flush-rake` (The Cardboard Gable, serious) holds that figure to a 4 to 8 in band in a secondary
test. Every figure was outside the band, and a failed test makes a fault present (R4), so the
fault convicted all eleven drawn plans on a figure nobody measured. The name is in
`elevation.NOT_MODELLED` now. The fault's governing test reads
`rake_member_projection_from_siding_face_in`, the raking member's THICKNESS (*"not overhang"*),
which nothing supplies either. So the fault is could-not-evaluate on all eleven, which is the
honest verdict for a member no layer draws.

**What the corpus says about a raking cornice, and why it is not drawn.**

- georgian-colonial-american's `pediment.raking_cornice` reads *"the full cornice profile raked,
  with the corona level and the bed mould raked"*. It is editorial, and it describes a PEDIMENT's
  raking cornice, not the verge of a plain gable.
- No pack dimensions a gable's rake, its overhang or its raking member.
- Drawing one would choose its depth and its profile, which is the laundering this corpus
  refuses.

**What is wanted.**

1. Whether the gable end draws a raking member at all. If it does, which record states its
   profile, its thickness proud of the wall and its overhang: the eave cornice's profile raked, a
   plain verge board, or something the style's kit says.
2. Whether a plain gable's verge is a different question from a pediment's raking cornice, or the
   same rule applied at a different scale.

Until it is ruled, the rake is drawn as the roof's edge, `rake_overhang_in` stays withheld, and
The Cardboard Gable stays could-not-evaluate.

## Asked and answered 30 September 2026 (Lucas, asked directly): B3

Put to Lucas on the evening of 30 September 2026 and answered by 18:13 UTC.

### The question, as put

*"The gable end's rake is drawn as a bare roof edge, and no record dimensions a raking member.
Should the gable end draw one, and from which record? This also decides whether a plain gable's
verge and a pediment's raking cornice are one rule or two."* Three readings were offered:

- **the fault's own rake**, drawn as a judgment (recommended);
- the edge kept until a pack or a plate dimensions the rake, with the sheet saying so. Until then
  every drawn gable end shows the flush rake The Cardboard Gable names;
- the eave cornice's whole profile raked on every gable end, as georgian-colonial-american's
  editorial pediment rule describes.

### Lucas's answer

**B3: the fault's own rake.**

> Draw what The Cardboard Gable's correct practice states for a colonial or Georgian rake. A
> raking board 6-8 in deep stands 1 1/4 in proud of the wall and carries the eave's bed mould and
> crown, with no corona or modillions, at 0.5-0.7 of their size, 4-8 in beyond the wall. Drawn at
> the midpoints, labelled a judgment and withheld from the fault, as R8a and R9a were. Styles the
> fault excepts keep the edge. A pediment keeps its own rule.

The figures are the fault's own, from `flush-rake`'s `correct_practice`, its governing test
(`rake_member_projection_from_siding_face_in` at least 1.25 in) and its secondary band (4 to 8 in).
Being a judgment drawn from the fault, the member is withheld from it, so The Cardboard Gable stays
could-not-evaluate. The drawing stops committing the defect the fault names. The second half of
the question is answered too: a plain gable's verge and a pediment's raking cornice are two rules.

### What executing it needs (WP-16.9)

- **One spelling of the rake**, drawn by every surface that draws the roof: the gable faces, the
  eave faces (where the roof now overhangs the corner), the roof plan, the DXF and the scene. Or a
  surface says it does not draw it.
- **The styles the fault excepts** (craftsman, swiss-chalet, tudor-revival, cotswold-vernacular,
  spanish-colonial-revival, minimal-traditional) keep the edge until their own kit states a rake.
- **A hip has no rake.** Where no gable end is drawn, `flush-rake`'s question does not arise, and
  WP-16.9 gates the fault there as WP-16.1 gated the storey and dormer faults. That is the plan's
  own reading of a feature that is not there. It is not B3's answer, and not B2's carried over; B2
  rules the return fault alone.
