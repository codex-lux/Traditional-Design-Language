# oq/the-roof-is-drawn-side-gabled-whatever-the-style-says — which roof a house gets when its record names none

*Status: IN PROGRESS (ruled 30 September 2026, B1 and B2, with B7-B9 and B11-B24 by 1 October; T3-T5, T9 and T10 taken as recommended under a standing instruction; executed by WP-16.9) · Raised in: WP-16.5, one cornice and the gable end (30 September 2026)*

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

## Asked and answered 30 September 2026 (Lucas, asked directly): B7, B8 and B9

Executing B1 raised three cases the ruling does not decide. They were put to Lucas on the evening of
30 September 2026 as direct questions, beside B10 in
`oq/the-rake-is-drawn-as-an-edge-and-carries-no-member`, while the roof and rake tables were being
checked, and answered by 20:11 UTC. Each is given as it was put, then the answer.

### The questions, as put

- **B7.** *"B1 keeps side-gable where it is one of several canonical roof forms. Six styles make
  exactly {cross-gable, hip} canonical and no side-gable: andalusian-spanish-revival,
  spanish-colonial-revival and the four Queen Anne nodes. Greek Revival's corrected record may carry
  {front-gable, hip}. Which is drawn when several canonical forms remain and none is side-gable?"*
  Offered: the fallback, said (recommended); the hip wins; the first canonical row wins.
- **B8.** *"Three styles make only forms the roof layer cannot draw canonical (a flat parapeted
  roof): california-mission-colonial, new-mexico-adobe and spanish-colonial-american. Their own
  resolved kits FORBID side-gable, which is the fallback B1 draws. mexican-hacienda's record says
  'the hacienda has no gable at all'. What is drawn?"* Offered: no roof, said (recommended; R3's
  reading); the fallback drawn and said; the first permitted drawable form.
- **B9.** *"The roof layer runs a side-gable's ridge along the plan's x axis whatever face the
  entrance is on; its own docstring defines front-gable as 'ridge perpendicular to the entrance'.
  good-03's entrance is on the west, so its side-gable roof puts a gable end on the entrance face.
  Should side and front be read relative to the entrance face?"* Offered: relative to the entrance
  (recommended); keep the x axis.

### Lucas's answers

- **B7: the fallback, said.** Where several canonical forms remain and none is side-gable, neither
  is chosen: the roof layer's fallback is drawn, and the sheet names the canonical forms and says
  which is drawn is not ruled.
- **B8: no roof, said.** A fallback the style's resolved kit forbids is refused (R3): no roof is
  drawn above the wall line, and every sheet says the kit's form is not drawn and the fallback is
  forbidden.
- **B9: relative to the entrance.** A side-gable's ridge runs parallel to the entrance wall and a
  front-gable's perpendicular to it.

## Asked and answered 30 September - 1 October 2026 (Lucas, asked directly): B11-B24

B1's adjudication tabled every style whose canonical roof another node wrote: 79 rows over 58 nodes.
An independent check upheld or amended its eighteen drafts. The cases that neither the records nor
B7-B9 decided were put to Lucas as direct questions, in four batches:

- B11-B14: put at 20:43 UTC on 30 September; answered at 21:17.
- B15-B18: put at 21:22; answered at 21:28.
- B19-B22: put at 21:30, and closed unanswered when Lucas asked again for the questions to be put
  directly. The same questions, reworded, were put at 21:46, and answered at 00:26 UTC on 1 October.
- B23-B24: put at 00:27 UTC on 1 October, with B25-B26 in
  `oq/the-rake-is-drawn-as-an-edge-and-carries-no-member`; answered at 00:29.

Each is given as it was put, then the answer. B24 was not in the adjudication table. It was found
while the questions were being written: B11's record reaches adam-style, which is drawn.

### The questions, as put

- **B11 (english-georgian's roof).** *"english-georgian inherits english-palladian's hip as
  canonical. Its own style record says 'a low-pitched hipped or side-gabled roof'. Its own kit ranks
  roof forms, but in the roof_pitch slot, where no roof reader looks: side-gable canonical, hip
  permitted, gambrel forbidden ('An American and Dutch answer, not an English one'). Which roof does
  english-georgian take?"* Offered:
  - *Side-gable, its kit's ranking*: Bind roof_form in its own kit from the roof_pitch ranking:
    side-gable canonical, hip permitted, mansard atypical, gambrel forbidden. Drawn side-gabled.
    english-georgian-country-house and regency, whose own words are hipped, get companion records.
  - *Hip, the inherited row*: The inherited hip stands and is drawn hipped. The roof_pitch ranking
    stays where it is, recorded as an open question (roof forms ranked in the pitch slot).
  - *Both canonical*: Hip and side-gable both canonical; under B1 the side gable is kept and drawn.
    Companions as in the first option.
- **B12 (the row house).** *"Three row-house styles are english-georgian-townhouse,
  italianate-townhouse and renaissance-revival-american. Their canonical massings are the terrace
  and the side-hall double pile, with party walls carried up through the roof. Each inherits a
  freestanding hip (english-palladian's hip, or italianate-american's low-hip-suppressed), and the
  roof layer draws them hipped. What roof does a row house take?"* Offered:
  - *Side-gable, hip at an end* (recommended): Each binds side-gable canonical, the ridge running
    between the party walls, with the hip permitted for the end of a terrace. Drawn side-gabled.
  - *Mansard canonical*: For the garret behind the parapet. The roof layer says it rather than draws
    it, so the fallback side gable is drawn and said.
  - *Keep the inherited hip*: The freestanding hip stands for all three and is drawn hipped, as the
    inherited records say today.
  - *No canonical form*: The house has no silhouette of its own: the fallback side gable is drawn
    and said, with the hip permitted for an end of terrace.
- **B13 (georgian-revival).** *"georgian-revival (good-02): the drafted record makes the hip and the
  side gable both canonical, as its record names them ('hipped or side-gable', hip first). Under B1
  the side gable is kept, so good-02 stays side-gabled. Or the hip alone?"* Offered:
  - *Both canonical* (recommended): As drafted and checked. good-02 stays side-gabled, as today, and
    its four verdicts return to could-not-evaluate. The tree's gambrel reading had cleared them on
    default geometry.
  - *Hip alone canonical*: Side-gable permitted, following the order the record names them each
    time. good-02 is drawn hipped: its gable faults read not applicable, and the roof refuses its
    end stacks, said.
- **B14 (the hip and its stacks).** *"Under B1, tidewater-georgian's kit makes the hip canonical and
  demotes the side gable in its own words ('the hipped roof with tall paired end chimneys is the
  type specimen here'). So the composer's Georgian candidates, which declare no roof, are now
  hipped. The roof layer refuses end stacks on a hip ('no full gable-end wall to run a stack
  through'), so they are drawn with no chimneys. No sheet printed that refusal until this package.
  On the Georgian brief the first three candidates are unchanged, and centre-passage-single-pile
  replaces five-part-palladian at fourth. What lands?"* Offered:
  - *Land B1, stacks said* (recommended): Composed Georgian houses are hipped. Their stacks are
    refused, and the roof's reason is printed on every face and the roof plan. An open question is
    raised to model an end stack rising past a hip.
  - *Model end stacks on a hip*: WP-16.9 stands an exterior end stack against a hipped roof's end
    wall and runs it above the ridge. This is new roof geometry, measured before it lands.
  - *Hold composed at side-gable*: Composed candidates keep the side gable until end stacks on a hip
    are modelled: an exception to B1 for the composer.
- **B15 (Queen Anne).** *"Queen Anne, four nodes (queen-anne-american and three descendants; the
  elevation draws none of them). The kit makes cross-gable and hip canonical and forbids side-gable
  and front-gable, citing c05: 'a simple rectangular hip or gable with applied ornament is Folk
  Victorian'. B7 sends them to the side-gable fallback, B8 refuses a forbidden fallback, so together
  they draw no roof. The roof layer's hip is the simple rectangle c05 names; its cross-gable is one
  centred wing with no valleys, shown on no elevation. What is drawn?"* Offered:
  - *No roof, said* (recommended): B7 and B8 as ruled. Neither canonical form is chosen, the
    fallback is forbidden, and the sheet names both forms and the ban with its writer.
  - *Draw the cross-gable*: The kit's first canonical row, and the nearest to its rule ('at least
    one front-facing gable'). The roof plan shows the centred wing; no elevation shows it.
  - *Draw the hip*: The kit's hip row ('especially in combination with a corner tower'), drawn as a
    plain hip with no tower. The stacks are refused and the sheet says so.
- **B16 (greek-revival-american).** *"greek-revival-american (good-03). The drafted record demotes
  the inherited side gable: the style's tell is the house 'turned gable-end to the road', and it
  contrasts the house that 'faces the road broadside'. It makes front-gable canonical. The inherited
  hip is neither named nor contradicted, so under B1 it stays canonical. Front-gable plus hip then
  falls to B7's fallback side gable, said, and good-03 is drawn as today. egyptian-revival and
  greek-revival-southern-plantation inherit this record. What should it say?"* Offered:
  - *Keep the hip* (recommended): B1 corrects only what the words contradict. good-03 stays
    side-gabled, and the sheet says the canonical forms are front-gable and hip, and that which is
    drawn is not ruled.
  - *Demote the hip*: Hip permitted, as a judgment: both canonical massings (temple-front,
    gable-front) are gable-fronted. good-03 is drawn front-gabled, the one shipped roof the drafts
    move.
- **B17 (greek-revival-southern-plantation).** *"greek-revival-southern-plantation (drawn in the
  census sweep; no shipped plan uses it). Its words: 'Low hipped or shallow-pedimented roof', and
  'Roof pitch 3:12 to 5:12, hipped or low-pedimented'. Today it inherits side-gable and hip, both
  canonical, and the side gable is drawn. Which record?"* Offered:
  - *Inherit Greek Revival's* (recommended): Its words name both a hip and a pediment, which is
    greek-revival-american's record. As answered above, that is front-gable and hip, so B7's
    fallback side gable, said. If the hip is demoted above, it is front-gabled.
  - *Hip alone canonical*: Hip, named first both times, is canonical; the pediment is read as the
    temple front's, so front-gable is permitted. It is drawn hipped, and its stacks are refused and
    said.
  - *Keep the side gable*: A side gable with pedimented ends reads as 'shallow-pedimented'. Its own
    record binds side-gable canonical, and it is drawn as today.
- **B18 (egyptian-revival).** *"egyptian-revival (not drawn). Its record names no roof. It
  'terminates in a cavetto with no pediment ever', and its c02 composes every terminating horizontal
  edge as a torus below a cavetto. It inherits side-gable and hip through greek-revival-american. If
  that draft lands, it inherits front-gable, which 'no pediment ever' refuses. What record should it
  have?"* Offered:
  - *Hip alone* (recommended): Front-gable forbidden ('no pediment ever'). Side-gable atypical: a
    low gable reads as a pediment, which is how Greek Revival uses it. A hip's edges are all
    horizontal, so the cavetto can crown every one. It is drawn hipped, and its stacks are refused
    and said.
  - *Flat parapet*: The cavetto crowns a flat roof, a reading of the temples the style copied rather
    than the record's words. The roof layer says so and draws the fallback side gable, said.
  - *Keep the side gable*: The record refuses a pediment, not a gable. Its own record makes
    side-gable canonical and forbids front-gable, and it is drawn as today.
- **B19 (arts-and-crafts-british).** *"arts-and-crafts-british (not drawn) inherits
  gothic-revival-british's cross-gable-steep as canonical. Its own words: 'Long, low massing with
  large unbroken roof planes at 45-55 degrees'. It rates massed-picturesque and linear-ell-farmhouse
  canonical, and describes Voysey's house as 'the roof hipped over two gabled cross wings'. What is
  its roof?"* Offered:
  - *Cross gable stands* (recommended): The picturesque massing and the cross-winged exemplar are
    its own. No record changes, and the roof layer draws its cross gable.
  - *Side-gable canonical*: 'Large unbroken roof planes' refuse the intersecting gable as the
    default, so cross-gable becomes permitted. tudor-revival then needs a record of its own
    ('prominent front-facing cross-gables'), which three styles inherit.
- **B20 (california-mission-colonial).** *"california-mission-colonial (not drawn) inherits
  spanish-colonial-american's flat parapet roof; the writer's note says that roof is New Mexico's.
  Its own words: 'California pitches a tile roof at 3:12–5:12'. Its kit: 'The great majority of
  ranges and church gables are plain and unshaped, terminating the tile roof'. The inherited record
  also forbids every gable, so under B8 it is refused a roof today. Which record?"* Offered:
  - *Side-gable, as drafted* (recommended): Side-gable canonical, reading the ranges' plain gables
    as a gabled range (a judgment). Front-gable and hip permitted, flat-parapet forbidden. Drawn
    side-gabled.
  - *Hip canonical*: The writer's own row for this region ('The low tile roof of California and
    later Texas'), with the gables permitted. Drawn hipped; the stacks are refused and said.
- **B21 (carpenter-gothic).** *"carpenter-gothic (not drawn) inherits the Gothic villa's irregular
  multi-gable roof, which the roof layer draws as its cross-gable. Its own record calls it 'a
  builder's symmetrical box'. Its commonest form is 'a central gable rising through the eave line of
  an otherwise symmetrical two-storey farmhouse'. It rates gable-front-and-wing and i-house
  canonical. Which record?"* Offered:
  - *Cross-gable canonical* (recommended): A central gable on a symmetrical body is what the roof
    layer's cross-gable draws: one centred cross gable on a side-gabled body. The villa's
    multi-gable row becomes atypical. Drawn as today, now for its own reason.
  - *Side-gable, as drafted*: The i-house body is canonical, with gable-front-and-wing and
    cross-gable permitted. Drawn side-gabled, without the central gable. Making both massings
    canonical draws the same.
  - *Gable-front-and-wing*: Its other canonical massing. The roof layer cannot draw that L, so the
    fallback side gable is drawn, said.
- **B22 (mexican-colonial and andalusian-courtyard-vernacular).** *"mexican-colonial and
  andalusian-courtyard-vernacular (neither drawn) inherit mudejar's par-y-nudillo. It is a carpentry
  ('The ceiling and the roof are the same object'), which the roof layer does not draw, so today the
  fallback side gable is drawn, said. mexican-colonial endorses the carpentry and names two roofs by
  region: 'Flat azotea roofs with parapets and canales on the altiplano; low-pitched clay tile with
  deep overhangs in the wet and hot lowlands'. It adds: 'Mixing the two on one building is a revival
  error.' The Andalusian record reads: 'Curved canal tile roof at a low pitch, or a flat azotea
  terrace'. The corpus does not read a row's regions. What should the records say?"* Offered:
  - *Leave the carpentry* (recommended): par-y-nudillo stays canonical, since neither record
    contradicts it. The fallback side gable is drawn, and the sheet says so.
  - *Low tile, as a hip*: Hip canonical, which is a reading: the records say 'low-pitched clay
    tile', not hip. Flat-parapet and the carpentry are permitted. Drawn hipped.
  - *Flat azotea canonical*: The altiplano's roof, where mexican-colonial's capital stands. The roof
    layer does not draw it, so the fallback side gable is drawn, said.
- **B23 (mexican-hacienda).** *"mexican-hacienda (not drawn) inherits mudejar's par-y-nudillo
  through mexican-colonial, which keeps it (your last answer). The roof layer cannot draw it, so the
  fallback is drawn: a side gable where the plan names no massing. Its own record says 'the hacienda
  has no gable at all and puts everything into an arcade', and names 'Flat azotea roofs with
  parapets and canales on the dry highlands; low-pitched clay tile with deep overhangs where it
  rains'. What record?"* Offered:
  - *Gables forbidden, no roof* (recommended): Its own record forbids every gable form on 'no gable
    at all' and keeps the carpentry canonical. The side-gable fallback is then forbidden, so under
    B8 no roof is drawn, said, as for the flat-parapet styles.
  - *Hip canonical, gables forbidden*: A hip has no gable. Reading 'low-pitched clay tile' as a hip
    is a judgment. It is drawn hipped, and its stacks are refused and said.
  - *Leave it*: The fallback is drawn and said, on a house its record says has no gable.
- **B24 (adam-style).** *"Not in the earlier question: english-georgian's new roof record
  (side-gable and hip both canonical) reaches five nodes. They are itself, the country house and
  regency (both getting hip companions), the townhouse (getting its own record) and adam-style.
  adam-style is drawn and today resolves english-palladian's hip. Its own words: 'A plain parapet
  conceals the roof, exactly as in the retained Georgian shell'. With no companion it inherits both
  canonicals, so it is drawn side-gabled. What does adam-style get?"* Offered:
  - *The Georgian shell's* (recommended): Its words say the roof is 'exactly as in the retained
    Georgian shell'. No companion: it takes english-georgian's record, and the side gable is drawn
    behind its parapet.
  - *A hip companion*: adam-style binds hip canonical itself and keeps today's hipped drawing. The
    parapet hides the roof, so the drawn form is the hidden one either way.

### Lucas's answers

- **B11: both canonical.** english-georgian binds its own `roof_form`. Side-gable and hip are
  canonical, mansard atypical, and gambrel forbidden in its own kit's words ('An American and Dutch
  answer, not an English one.'). B1 keeps side-gable where it is one of several canonical forms, so
  the house is drawn side-gabled. english-georgian-country-house and regency, hipped in their own
  words, bind hip companions. B24 found that the same record reaches adam-style.
- **B12: side-gable, hip at an end.** english-georgian-townhouse, italianate-townhouse and
  renaissance-revival-american each bind side-gable canonical, with the ridge running between the
  party walls. The hip is permitted, for the end of a terrace.
- **B13: both canonical, as drafted.** Hip and side-gable are both canonical, so good-02 stays
  side-gabled.
- **B14: land B1, stacks said.** A composed Georgian candidate takes tidewater-georgian's hip. Its
  stacks are refused, and the reason is printed. Modelling an end stack that rises past a hip is
  raised as a question of its own.
- **B15: no roof, said.** B7 and then B8, as ruled. Neither canonical form is chosen, the fallback
  is forbidden, and the sheet names both forms and the ban with its writer. No record changes.
- **B16: keep the hip.** greek-revival-american's corrected record makes front-gable and hip
  canonical and side-gable permitted. Under B7 the fallback side gable is drawn and said, so good-03
  is drawn as today.
- **B17: inherit Greek Revival's.** greek-revival-southern-plantation binds no record of its own; it
  inherits B16's.
- **B18: hip alone.** egyptian-revival binds its own record. Hip is canonical, front-gable forbidden
  ('no pediment ever') and side-gable atypical. It is drawn hipped, and its stacks are refused and
  said.
- **B19: the cross gable stands.** No record changes.
- **B20: side-gable, as drafted.** Side-gable is canonical, as a judgment. Front-gable and hip are
  permitted, and flat-parapet is forbidden.
- **B21: cross-gable canonical.** The draft is amended. Cross-gable is canonical; side-gable,
  front-gable and gable-front-and-wing are permitted; multi-gable-unequal-width is atypical, as the
  villa's; and low-hip stays forbidden, as inherited. The drawing does not change; it now draws the
  style's own form.
- **B22: leave the carpentry.** par-y-nudillo stays canonical and no record changes. The fallback is
  drawn, and the sheet says so.
- **B23: gables forbidden, no roof.** mexican-hacienda binds its own record. par-y-nudillo stays
  canonical, every gable form is forbidden on 'the hacienda has no gable at all', and the azotea and
  the low tile are permitted. Under B8 no roof is drawn, and the sheet says why.
- **B24: the Georgian shell's.** adam-style binds no companion. It takes english-georgian's record
  ('exactly as in the retained Georgian shell'), and its side gable is drawn behind its parapet.

## Taken as recommended under Lucas's standing instruction of 1 October 2026: T3, T4 and T5

At 00:42 UTC on 1 October 2026 Lucas wrote: *"Proceed with all recommended answers for all future
questions in this session"*.

- **T3 and T4** were put to him at 00:34 UTC, with T1 and T2 in
  `oq/the-rake-is-drawn-as-an-edge-and-carries-no-member`. They were still unanswered when the
  instruction arrived, and it closed them.
- **T5 was never put.**

**None of these is an answer Lucas chose.** Each is the recommended option, taken under his
instruction. Each is given as it was put, or for T5 as it stood in the independent check, then the
option taken.

### The questions, as put

- **T3 (a roof drawn from a judgment-flagged record).** *"Some roof_form records the roof layer now
  draws from are flagged `judgment: true`. They include american-farmhouse-vernacular's side gable
  (good-04, good-06), cape-dutch's hip, and most B1 corrections (colonial-revival's on four shipped
  plans, georgian-revival's on good-02). Should a roof drawn from a judgment-flagged record say
  so?"* Offered:
  - *Said on every surface* (recommended): The elevation, the roof plan and the DXF say the form is
    a judgment and name its writer, in one spelling in disclosures.py, on WP-12.9's precedent for
    the stack's plan size. Sheet words move; the drawings do not.
  - *The record carries it*: The flag stays in the kit record, and the sheets print only which
    record drew the roof.
- **T4 (inherited non-canonical rows a style contradicts).** *"B1 corrects inherited roof records a
  style contradicts. Three contradict only NON-canonical rows, so no drawing moves.
  creole-cottage-vernacular says 'Steep side-gable or hipped roof', against its writer's side gable
  marked atypical. federal-style says 'massing (gambrel, wide dormered roofs) no Federal builder
  used', and new-england-federal calls revival work that 'combines Federal doorways with gambrel
  roofs' an error; both inherit the Georgian record's permitted gambrel. Does B1 reach them?"*
  Offered:
  - *Correct them too* (recommended): Each binds its own row in its own words, without promoting any
    row to canonical: creole's side gable becomes permitted, and the two Federal gambrels become
    forbidden. No drawing moves.
  - *Canonical rows only*: B1 reaches only the rows that decide a drawing. The three are named in
    the report and an open question, and their records are left alone.
- **T5 (specified or extends; never put).** The independent check of B1's drafts, 1 October 2026:
  *"A specified record stops hip_ridge_length_ratio and the two gambrel pitches at five drafts and
  two reached nodes, and principal_pitch_min at carpenter-gothic and octagon-house. None is read by
  any code today, and an extends delta would keep them. Low stakes; the template is WP-16.2's."*
  Recommended: a `specified` record on WP-16.2's template, each note naming the parameters it stops.

### The options taken

- **T3: said on every surface.** The elevation, the roof plan and the DXF say that the roof form is
  a judgment and name its writer, in one spelling in `build/disclosures.py`, on WP-12.9's precedent.
  Sheet words move; the drawings do not.
- **T4: correct them too.** Each binds its own row in its own words, and no row is promoted to
  canonical. creole-cottage-vernacular's side gable becomes permitted, and the two Federal gambrels
  become forbidden. No drawing moves.
- **T5: specified.** Every record drafted over georgian-colonial-american's or
  gothic-revival-american's is `specified`, on WP-16.2's template. Its note names the writer's
  parameters it stops, none of which any code reads.

## Taken as recommended under the same instruction: T9 and T10 (never put)

The independent check of WP-16.9's records (1 October 2026) raised two more questions about roofs,
after the instruction. **Neither was put to Lucas, and neither is an answer he chose.** Each is
given as it stood in the check, then the option taken.

### The questions, as they stood

- **T9 (beaux-arts-american's split words).** The draft made `low-roof-behind-balustrade`
  canonical and `mansard-block` forbidden. The check found the ban contradicted by the node's own
  facade-pavilion binding, *'Bound for the mansard and the pavilion'* and *'The American Beaux-Arts
  house takes the French roof and the projecting end pavilion'*, whose `mansard_lower_slope` governs
  its roof pitch. It amended the record to make the mansard permitted, marked judgment, and wrote:
  *"Alternative: keep the mansard canonical, as inherited, on B16's 'B1 corrects only what the words
  contradict'. The record's words are split, so that is a question for Lucas. No drawing moves either
  way: both ids are undrawable, and the fallback side gable is drawn and said."* The options:
  - *The check's amendment* (recommended): the hidden low roof is canonical, the mansard permitted,
    both marked judgment and both sentences quoted. It keeps what each of the record's sentences
    says, and neither form is drawn.
  - *No record*: the mansard stays canonical as inherited, B16's reading of a silence. But the
    record is not silent here: distinguished_from[2] says the composition *'terminates in a
    balustrade or attic rather than a roof'*.
- **T10 (the Greek Revival records carry the Georgian gambrel past the Federal ban).** The check:
  *"Cross-record, no drawing: its gambrel rows are georgian-colonial-american's (permitted; atypical
  in New England and the Hudson Valley), while federal-style's T4 record of the same batch, which now
  stands between this node and georgian-colonial-american in its cascade, forbids the gambrel. The
  carry is from the d5 writer; whether a Greek Revival record should carry the Georgian permission
  past the Federal ban is a choice no ruling makes."* It reaches greek-revival-american,
  greek-revival-northern, greek-revival-upland-vernacular and egyptian-revival, whose records carry
  the rows, and greek-revival-southern-plantation, which reads greek-revival-american's. The options:
  - *Keep the Georgian permission, and say so* (recommended): the records are silent on the gambrel,
    and federal-style's reason is the Federal builder's own: *'combine Federal doorways with massing
    (gambrel, wide dormered roofs) no Federal builder used'*. Carrying it would hand a ban to another
    style for a reason that is not its own, which is the shape WP-16.2 corrected.
  - *Carry federal-style's ban*: each record forbids the gambrel as federal-style's record does,
    quoting federal-style's words. *(Corrected 1 Oct 2026, on the second independent check: this
    option first said "as its nearest ancestor now does". That is true of greek-revival-american
    alone; the other three sit under greek-revival-american's own record, which permits it.)*

### The options taken

- **T9: the check's amendment.** beaux-arts-american's record makes `low-roof-behind-balustrade`
  canonical and `mansard-block` permitted, both marked judgment, quoting distinguished_from[2], c04
  and its facade-pavilion binding. Its note says the mansard's rank is T9's.
- **T10: the Georgian permission, said.** Each of the four records keeps
  georgian-colonial-american's gambrel rows. Its note names federal-style's ban and its reason, and
  says why it is not carried. No drawing moves: the gambrel is canonical on none of them.
