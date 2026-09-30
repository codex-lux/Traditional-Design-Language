# oq/the-roof-is-drawn-side-gabled-whatever-the-style-says — which roof a house gets when its record names none

*Status: IN PROGRESS (ruled 30 September 2026, B1 and B2; executed by WP-16.9) · Raised in: WP-16.5, one cornice and the gable end (30 September 2026)*

**Where a plan declares no roof form, the roof is drawn side-gabled, and the style's own kit is
never asked.** `threshold.roof_form_for` takes the plan's `declared.roof_form`. Failing that, it
takes the massing's first `roof_default`, and failing that the module's constant,
`DEFAULT_ROOF_FORM = "side-gable"`. It never reads the style's resolved `roof_form` slot. The note
it writes names a massing even where there is none: *"No roof_form declared; used massing
'None''s first default ('side-gable')."*

**Measured on the sixteen shipped plans** (30 Sep 2026, `9dd0fbf`, the heuristic engine):

- 3 declare a form: Tidewater and the spec Colonial declare `side-gable`, bad-04 `gable`.
- None of the other 13 states a massing, so all 13 take the constant.
- The drawn form is canonical in the style's resolved kit on 4 plans (bad-03, good-03, good-04,
  good-06). It is not canonical on 12, and forbidden on none.

**Over the 164 nodes**, the constant is:

- canonical on 26;
- not canonical on 73, of which 23 make `hip` canonical;
- forbidden on 9: california-mission-colonial, english-baroque, monterey-colonial,
  new-mexico-adobe, queen-anne-american, queen-anne-free-classic, queen-anne-patterned-masonry,
  queen-anne-spindled and spanish-colonial-american.

The other 56 resolve no `roof_form` variant at all.

**Over the 41 styles the elevation draws**, the constant is canonical on 18, not canonical on 20
and forbidden on one (english-baroque); two state nothing. Eleven of the 41 make `hip` canonical.
The census's style sweep draws every style on the Tidewater plan, whose record declares
`side-gable`, so each of the eleven is swept with two gable ends its own kit does not describe.

**Why it matters now.** WP-16.5 (R8) draws the gable end by what the resolved kit says of
`cornice_return`. good-05 is italian-renaissance-revival, and A4 bound its return forbidden on its
own roof: *"This style's own roof leaves a return nowhere to stand"*. The record quotes two
sources for that:

- its `constraints[2]`: *"Roof pitch 3:12 to 5:12, clay tile only, with no gable facing any
  principal elevation."*;
- its kit's `roof_form` rule: *"Low-pitched hipped roof with no gable facing any principal
  elevation (c03)."*

good-05 declares no form, so its roof is drawn side-gabled. The elevation draws its two gable ends
as the kit asks, with the cornice's end profile at each corner and no return. So
`return-that-never-returns` (serious, `applies_to: universal`) goes from could-not-evaluate to
PRESENT: the corpus convicts a gable end the style says the house does not have.

- The fault excepts five styles whose kits refuse the return: shingle-style, craftsman,
  prairie-school, tudor-revival and mission-revival. The Italianate family, which A4 bound
  forbidden, is not among them.
- Its `severity_by_style` marks four of the five `not-applicable`, and that value is read by
  nothing: `oq/a-fault-marked-not-applicable-to-a-style-still-convicts-it`.

**Not done, and why.**

- **The fallback is not changed.** Reading the style's canonical form would move the roof on up to
  seven shipped plans. The fallback draws nine in a form their kit does not make canonical, and two
  of those (bad-06, good-07) resolve no canonical form. Every figure built on the roof moves with
  it: the pitch, the ridge height, the stacks' heights and the truss-depth ratio
  (`oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced`). Which form a record that names
  none should get is a ruling.
- **The fault gains no exception.** WP-16.2's plan listed this as a question to put to Lucas
  (*"whether `return-that-never-returns` gains exceptions for styles whose kits truly state no
  return"*). It was not among the ten questions asked and answered on 30 Sep.
- **The note's wording is not changed.** It names a massing where there is none. Correcting it
  moves the roof record's text on thirteen plans, so it belongs with whatever is ruled here.

**What is wanted.**

1. Where a plan declares no roof form, should the roof take the style's own canonical `roof_form`,
   before the massing's default and the module's constant?
2. Where a style's kit forbids the return because its roof has no gable, should
   `return-that-never-returns` be not applicable to it, by an exception like the five? Or does (1)
   answer it: a hip has no gable end, so the fault would have nothing to judge.

## Asked and answered 30 September 2026 (Lucas, asked directly): B1 and B2

Both halves of this question were put to Lucas on the evening of 30 September 2026, beside the
questions in `oq/the-rake-is-drawn-as-an-edge-and-carries-no-member` and
`oq/a-return-permitted-only-over-a-deeper-cornice-is-drawn-over-a-shallower-one`. They were answered
by 18:13 UTC. Each question is given as it was put, with the readings offered, and then the answer.

### The questions, as put

1. *"Where a plan declares no roof form, which roof should it get? Today a constant draws
   side-gable on 13 of the 16 shipped plans without asking the style's kit. That is how good-05
   (italian-renaissance-revival, whose own kit makes hip canonical) gets two gable ends and a
   serious conviction."* Three readings were offered:
   - **the style's kit, adjudicated first** (recommended);
   - the resolved kit as it stands, which draws seven shipped roofs in a new form, five of them
     gambrels through shingle-style's record;
   - side-gable kept, with the sheet saying so.
2. *"Should return-that-never-returns excuse the four styles whose own kits forbid the return
   because their roofs have no gable (italian-renaissance-revival, italianate-townhouse,
   second-empire, renaissance-revival-american, bound under A4), as it excuses five others?"*
   Three readings were offered:
   - **no new exception, and the fault gated on a drawn gable end** (recommended);
   - the four added to the fault's five exceptions;
   - the fault spared wherever the resolved kit refuses the return.

**Found while putting the question, and put with it.** colonial-revival and georgian-revival write
no `roof_form` record of their own. Both resolve shingle-style's, whose canonical row is `gambrel`
(*"The Colonial inheritance."*), so the resolved kit would draw a gambrel on bad-01, bad-02, bad-05,
bad-07 and good-02. new-classical already overrides that record in its own kit: *"Overrides the
cascade's inherited value (shingle-style, via colonial-revival's family)."*

### Lucas's answers

- **B1: the style's kit, adjudicated first.**

  > After the plan's own declaration and before the massing's default, the roof takes the
  > canonical roof_form of the style's resolved kit, read through a closed table onto the forms
  > the roof layer draws. Inherited roof records a style contradicts are first corrected in its own
  > kit, as WP-16.2 did the bans. colonial-revival and georgian-revival resolve shingle-style's
  > gambrel today. Composed candidates move too; the ranking is re-measured before it lands.

  The reading's preview, which Lucas saw with it, set out two cases more. Where side-gable is
  already canonical it is kept. A style with no canonical form keeps the fallback, and the sheet
  says so.
- **B2: no new exception; the fault is gated on a drawn gable end.**

  > No new exception. The fault is not applicable where no gable end is drawn, a gate like
  > WP-16.1's storey and dormer gates, so a hipped house has nothing to answer. A house drawn with
  > a gable end is judged, whatever its kit says of the return.

### What executing it needs (WP-16.9)

- **The adjudication comes first.** Every style whose canonical `roof_form` row another node wrote
  is tabled against its own record, on WP-16.2's template: grouped by (writer, form) and checked
  independently. Where the records do not decide, the case goes to Lucas.
- **A closed table.** A kit names roofs in its own words (`hip-roof-classical-composition`,
  `low-hip-suppressed`, `gable-front`, `mansard-block` and more). The roof layer draws seven forms:
  gable, side-gable, front-gable, hip, gable-on-hip, cross-gable and gambrel. Each mapping quotes the
  row it reads. A form the roof layer cannot draw is said, as `roof.py` already says of a mansard.
- **Composed candidates.** On 17 of the 21 partis, the massing's first roof default is not
  canonical for the parti's first native style. The composer's returned sets are measured before
  and after.
- **The roof note stops naming a massing that is not there.**
