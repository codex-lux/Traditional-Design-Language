# oq/the-rake-is-drawn-as-an-edge-and-carries-no-member — the half of the gable end nobody ruled

*Status: IN PROGRESS (ruled 30 September 2026, B3, corrected by B5 and B6, with B10 and B25-B30 by 1 October; T1, T2, T6, T7, T8 and T11 taken as recommended under a standing instruction; executed by WP-16.9) · Raised in: WP-16.5, one cornice and the gable end (30 September 2026)*

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

## The question was put on a false premise, and was put again (30 September 2026): B5 and B6

**The question as put said "no record dimensions a raking member", and that was false.** Found by
WP-16.9 while laying out the rake, before any of it was drawn. This entry and the question read
the proportion PACKS, where it is true that nothing dimensions a gable's rake, and never read the
kits' own `rake_condition` slot, where most drawn styles say something. Measured over the 41 styles
the elevation draws, on `54f7e33`:

- **12 resolve georgian-colonial-american's record**: `boxed-rake-with-return` canonical,
  `rake_overhang_in` 4 to 8 in and `rake_to_cornice_ratio` 0.5 to 0.7, both editorial, and the
  rule *"The rake is tight — 4 to 8 in of overhang — and carries a reduced version of the eave
  profile; it must die into the cornice return rather than meeting it in a mitre."* That is B3's
  rake, stated by the kit.
- **13 resolve elizabethan's record by descent**, colonial-revival and georgian-revival among them:
  *"No exposed gable verge in the ordinary sense; the roofline terminates at the parapet, not at a
  projecting gable rake."* colonial-revival's own record describes its cornice as *"returned at the
  rake"*.
- **4 forbid the slot** (italianate-american's binding, on the Italianate family: *"No bargeboard
  vocabulary here."*).
- **cape-cod-colonial states its own**: `rake_width_max` 6 in, measured, *"Rake trim not more than 6
  in wide (c04, soft)."*
- **new-urbanist-traditional resolves american-farmhouse-vernacular's**: *"Plain rake trim 6-8 in,
  occasionally carrying a single jigsawn gable ornament -- one piece of applied decoration, never a
  full profiled rake or bargeboard."*
- **dutch-colonial-american resolves german-fachwerk's** 250 mm minimum gable verge.
- **9 are open.**

So B3 as answered would have drawn the fault's rake over records that state another rake, forbid
one, or were never the style's own. It was put to Lucas again, directly, at about 18:50 UTC, with
two questions.

### The questions, as put

1. *"Should the rake follow the style's resolved `rake_condition`, as the gable end follows
   `cornice_return` under R8?"* Three readings were offered:
   - **kit first, adjudicated** (recommended);
   - the fault's rake as B3 answered, the kits' other rake records not read but said where they
     disagree;
   - the fault's rake only where the kit states it, the edge everywhere else.
2. *"A hip has no rake. Should `flush-rake` be not applicable where no gable end is drawn, the way
   B2 gates the return fault?"* Two readings: gate it (recommended), or leave it could-not-evaluate
   on a hipped house.

### Lucas's answers (by 18:51 UTC)

- **B5: kit first, adjudicated.**

  > The fault's rake where the resolved kit states it or says nothing; a kit that states another
  > rake draws its own (cape-cod-colonial's plain trim of 6 in or less, the farmhouse's plain trim
  > with no mouldings); a forbidden slot is refused under R3. Inherited rake records a style's own
  > words contradict (elizabethan's parapet on the colonial-revival family, german-fachwerk's 250 mm
  > verge on dutch-colonial-american) are corrected in its own kit first, as B1 does for roofs.

  B3's other clauses stand: the rake is drawn at the midpoints of the fault's figures as a judgment
  withheld from the fault, the styles the fault excepts keep the edge, and a pediment keeps its own
  rule.
- **B6: `flush-rake` is gated on a drawn gable end.**

  > Every test of flush-rake is not applicable where the elevation draws no gable end. After B1,
  > good-05's hipped roof reads not applicable for both gable faults instead of could-not-evaluate.

  The gate that the section above calls the plan's own reading is ruled now.

### What executing them needs (WP-16.9)

- **An adjudication of the drawn styles' inherited `rake_condition` records**, on WP-16.2's
  template, beside B1's of `roof_form`: tabled by (writer, record), checked independently, and put
  to Lucas where the records do not decide.
- **One reader of the rake at the house's date** (`resolve_kit`), in the states the kit can say: a
  forbidden slot, the fault's rake, a stated plain trim, or a rake this generator does not draw
  (a bargeboard, a coped parapet), which keeps the edge and says why.
- **A figure a record states only in prose** (the farmhouse's 6-8 in) is drawn only once the
  adjudication transcribes it into the kit, quoted; a prose figure is never read by a pattern.

## Asked and answered 30 September 2026 (Lucas, asked directly): B10

Put to Lucas on the evening of 30 September 2026 beside B7-B9 in
`oq/the-roof-is-drawn-side-gabled-whatever-the-style-says`, and answered by 20:11 UTC.

### The question, as put

*"minimal-traditional is one of the six styles The Cardboard Gable excepts. B3 says excepted styles
keep the edge; B5 says a kit that states another rake draws its own. Its own record states the rake:
'Minimal Traditional has a 1x6 board.' What does its gable end draw?"* Offered: its own board at
6 in, the nominal read as inches, a judgment (recommended); its own board at 5 1/2 in; the edge.

### Lucas's answer

- **B10: its own board, 6 in.** B5's kit-first governs an excepted style whose own kit states its
  rake: minimal-traditional's gable end draws a plain 6 in board, labelled a judgment. An excepted
  style whose kit states The Cardboard Gable's rake, or says nothing, keeps the edge (B3).

## Asked and answered 1 October 2026 (Lucas, asked directly): B25-B30

- B25 and B26 were put at 00:27 UTC with B23-B24 in
  `oq/the-roof-is-drawn-side-gabled-whatever-the-style-says`, and answered at 00:29.
- B27-B30 were put at 00:30, and answered at 00:32.

**B29 is B10 asked again.** B10's recommendation of 6 in rested on a false premise: the draft said
that no record here states the dressed width of a 1x6. trim-craftsman, which minimal-traditional
binds itself, states it. Each is given as it was put, then the answer.

### The questions, as put

- **B25 (cape-cod-revival's rake).** *"cape-cod-revival (drawn in the census sweep) resolves
  elizabethan's parapet rake, which its steep side gable contradicts. It states no rake member. Its
  c05 reads 'a simple 4-6 in. eave moulding', and c05's test reads `rake_trim_width_in` between 4
  and 6, though the test's own note says it tests the eave moulding. B5 says a kit that states
  another rake draws its own. What does its gable end draw?"* Offered:
  - *Its own 4-6 in* (recommended): Its c05 figure, [4, 6] in, transcribed as measured with a note
    saying it is the eave moulding carried to the rake. It is the farmhouse transcription's
    convention, and is drawn plain at the 5 in midpoint.
  - *Cape-cod-colonial's 6 in*: As drafted. The ancestor's 'Rake trim not more than 6 in wide' is
    carried as editorial and judgment, on the revival's note that it reproduces that ancestor's
    dimensions. Drawn plain at 6 in.
  - *The fault's raking board*: Nothing is stated about the member, so The Cardboard Gable's moulded
    rake is drawn. That is more trim than c05 lists.
- **B26 (english-georgian's rake).** *"english-georgian's own side gable is now drawn (your 'both
  canonical'), so its rake matters. It resolves elizabethan's parapet rule: 'the roofline terminates
  at the parapet'. Its record: 'a plain parapet with concealed gutter in town' and 'expressed in the
  country'. Its own roof_pitch slot carries `parapet_conceals_roof: true`. No plan field says town
  or country. Which rake?"* Offered:
  - *Keep the parapet* (recommended): Its own kit conceals the roof, and the town is its record's
    centre. The gable end keeps the edge, and the sheet prints the parapet sentence. The country
    house is its own node, and hipped.
  - *Its own country rake*: A gable rake with the member unstated, so the fault's rake is drawn. It
    reaches 25 nodes (five drawn). The townhouse and adam-style (parapets) need companions, and 20
    undrawn nodes take it.
- **B27 (neoclassical-revival's rake).** *"neoclassical-revival (drawn) binds its own roof, hip and
  side-gable both canonical, so its side gable is drawn. Its rake today is elizabethan's parapet.
  Colonial-revival's corrected rake would reach it: a rake permitted to die into a conditional
  return, with the member unstated, so the fault's rake is drawn. Its own words: 'a low-pitched
  hipped or side-gable roof and a continuous cornice, often with a balustrade or parapet', and
  'often invisible behind a balustrade'. Which rake?"* Offered:
  - *Colonial-revival's* (recommended): No record of its own. The parapet is 'often', and a
    side-gable end under a continuous cornice shows a rake, so the fault's rake is drawn there.
  - *A parapet companion*: It binds its own record keeping the parapet, so its gable end keeps the
    edge and the sheet prints the parapet sentence.
- **B28 (dutch-colonial-american's rake).** *"dutch-colonial-american (drawn; side-gable and gambrel
  canonical) loses german-fachwerk's 250 mm daub verge. Its drafted record states a masonry gable
  ('steep unbroken gables in stone and brick') with a tight verge, and permits the timber barge
  board its pack reads ('often the roofing simply stops on a barge board against the masonry'). It
  names no member, so under B5 the fault's rake is drawn: a 7 in board carrying the eave's bed mould
  and crown at 0.6, 1 1/4 in proud, 6 in beyond the wall. Only the 6 in overhang is dutch-gambrel's;
  the moulded member is Georgian. Which?"* Offered:
  - *The fault's rake, as drafted* (recommended): B5's letter: a record that says nothing of the
    member draws the fault's rake. Its 6 in overhang agrees with the pack's tight verge, and the
    moulded member is labelled a judgment.
  - *Barge board canonical*: The member becomes the pack's plain board against the masonry, not a
    moulded one. No record states that board's depth, so the edge is drawn, and said, until one
    does.
- **B29 (minimal-traditional's board, B10 asked again).** *"Asked again, because my recommendation
  for B10 rested on a false premise. B10 offered 6 in (the nominal 1x6 read as inches, a judgment)
  or 5 1/2 in, and the draft said no record here states the dressed width. One does. trim-craftsman,
  which minimal-traditional binds itself, states '1x6 (5 1/2)' and '1x6 dressed to 5 1/2 in'.
  WP-14.5 corrected craftsman's 6 in head casing to 5.5, measured, on exactly that pack. What width
  does minimal-traditional's board draw?"* Offered:
  - *5 1/2 in, measured* (recommended): Sourced to trim-craftsman's dressed figure, on WP-14.5's
    precedent. It is a measurement rather than a judgment.
  - *Keep 6 in*: B10 as answered: the nominal designation read as inches, editorial and judgment.
    The note names 5 1/2 in as the dressed figure not taken.
- **B30 (jeffersonian-classicism's rake).** *"jeffersonian-classicism (drawn; hipped, so no gable
  end is drawn either way) resolves georgian-colonial-american's rake: the fault's rake, canonical.
  Its own hard c03 conceals the low roof 'behind a balustrade, Chinese railing or parapet at least 3
  feet high', and its kit's parapet rule already overrides the Georgian parent ('here the roof is
  not shown'). How is its own rake record bound?"* Offered:
  - *Forbidden, A4's shape* (recommended): rake_condition is forbidden on its own roof, citing c03,
    and a temple front's pediment keeps its own rule. --forbidden rises 679 to 680 and STRANDING's
    equalities move (5 test_stranding reds), re-pinned in the same commit with attribution. It also
    ends opening-pointed's bargeboard delivery there.
  - *Specified, rule only*: A record stating the concealment in words alone. It reads as unread, so
    the edge is kept and no meter moves, but opening-pointed's 10 1/2 in bargeboard stays governing
    that address.

### Lucas's answers

- **B25: its own 4-6 in.** The c05 figure, [4, 6] in, is transcribed as measured. Its note says it
  is the eave moulding carried to the rake, as the farmhouse transcription carries its fascia's
  figure. It is drawn plain at the 5 in midpoint, with no return (c05).
- **B26: keep the parapet.** english-georgian binds no rake record. Its gable end keeps the edge,
  and the sheet prints the parapet sentence.
- **B27: colonial-revival's.** neoclassical-revival binds no record of its own. colonial-revival's
  corrected rake reaches it, and the fault's rake is drawn.
- **B28: the fault's rake, as drafted.** The 6 in overhang agrees with dutch-gambrel's tight verge,
  and the moulded member is labelled a judgment.
- **B29: 5 1/2 in, measured.** The width is sourced to trim-craftsman's dressed figure, on WP-14.5's
  precedent. This supersedes B10's 6 in; B10's ruling that the style's own board is drawn stands.
- **B30: forbidden, A4's shape.** jeffersonian-classicism binds `rake_condition` forbidden on its
  own roof, citing c03; a temple front's pediment keeps its own rule. FORBIDDEN_RATCHET moves 679 ->
  680, and the stranding pins move in the same commit, with attribution.

## Taken as recommended under Lucas's standing instruction of 1 October 2026: T1, T2 and T6

At 00:42 UTC on 1 October 2026 Lucas wrote: *"Proceed with all recommended answers for all future
questions in this session"*.

- **T1 and T2** were put to him at 00:34 UTC, with T3 and T4 in
  `oq/the-roof-is-drawn-side-gabled-whatever-the-style-says`. They were still unanswered when the
  instruction arrived, and it closed them.
- **T6 was never put.**

**None of these is an answer Lucas chose.** Each is the recommended option, taken under his
instruction. Each is given as it was put, or for T6 as it stood in the independent check, then the
option taken.

### The questions, as put

- **T1 (the refill at ranch-style and modern-farmhouse-traditional).** *"minimal-traditional's new
  rake record (a plain 5 1/2 in board, your answer) refills at slot level. Two descendants whose own
  words state other rakes would inherit it: ranch-style (c03, 'eave and rake overhang between 18 and
  36 in') and modern-farmhouse-traditional (hard c02, 'a returned or moulded termination at every
  gable corner'). Neither is drawn, and today both resolve elizabethan's parapet, which contradicts
  them more. This is A10's shape. What is done?"* Offered:
  - *Draft both companions* (recommended): Each binds its own rake_condition in its own words,
    checked by a fresh agent before it lands, as A10 was for neo-eclectic.
  - *Name the refill only*: No records. The report and an open question name the two refilled nodes
    and the words each would need.
- **T2 (the raking-cornice fault).** *"raking-cornice-that-does-not-match (serious) asks about a
  pediment: 'Count distinct mouldings visible in each cornice at the lower corner of the pediment.'
  The elevation draws no pediment. B3's rake on a plain gable end deliberately carries fewer members
  than the eave, so the raking member count is withheld and the fault reads could-not-evaluate on
  every house. Gate it?"* Offered:
  - *Leave could-not-evaluate* (recommended): The withheld count's reason already says no pediment
    is drawn. A gate on a pediment count would read a zero this generator holds by construction,
    which is the generator-constant shape WP-13.1 named.
  - *Gate on a drawn pediment*: Publish the count of pediments drawn (zero today) and make the fault
    not applicable where none is drawn, as B2 and B6 gated the return and flush-rake faults.
- **T6 (hudson-valley-dutch's tumbled rake; never put).** The independent check, 1 October 2026:
  *"hudson-valley-dutch's town gables, 'its raking edge finished with mouse-tooth tumbling': no
  rake_condition id states a tumbled brick rake. Neither the draft's permitted barge board nor the
  fault's moulded rake is that."* The sentence is description.long's, and it is about the towns: 'In
  the towns the same culture builds in brick with the gable to the street, stepped or spouted, its
  raking edge finished with mouse-tooth tumbling'. B28's record, which reaches hudson-valley-dutch,
  already states the same town gable in its parent's words ('in the towns the gable is turned to the
  street and parapeted'). It also says that no `rake_condition` id states a stepped or spouted
  gable, so that gable is left to the rule. Recommended: an open question naming the vocabulary gap,
  and no record.

### The options taken

- **T1: draft both companions.** ranch-style and modern-farmhouse-traditional each bind their own
  `rake_condition` in their own words, each checked by a fresh agent before it lands, as A10 was.
- **T2: leave could-not-evaluate.** The raking member count stays withheld, and its reason already
  says no pediment is drawn. No gate is added, and no code changes.
- **T6: an open question, and no record.** This answer was first written here as B5 applied: a
  companion in the style's own words, keeping the edge. That rested on a reading that
  hudson-valley-dutch's words contradict the record it would inherit, and they do not: its tumbled
  raking edge is the town gable B28's record already states and leaves to the rule. It was corrected
  before any record landed. The gap is the vocabulary: no `rake_condition` id states a parapeted,
  stepped or spouted masonry gable, or a tumbled raking edge.

## Taken as recommended under the same instruction: T7, T8 and T11 (never put)

The independent check of WP-16.9's records (1 October 2026) raised three more questions, after the
instruction. **None was put to Lucas, and none is an answer he chose.** Each is given as it stood
in the check, in its own words, then the option taken.

### The questions, as they stood

- **T7 (neo-eclectic, reached by ranch-style's T1 record).** The check: *"It is the first record
  neo-eclectic's cascade meets for this slot, and neo-eclectic binds no rake_condition, so
  neo-eclectic now reads this record: state 'silent', with a rake_overhang_in band of 18-36 in.
  neo-eclectic's own words say 'Shallow eave and rake overhang, typically 6 to 12 in'
  (defining_characteristics[7]). Its own kit's eave_condition carries overhang_range_in [6, 12],
  measured. That is A10's refill shape a second time: a companion reaching a node whose words
  contradict it. The amended note says so. The remedy needs a decision: a neo-eclectic companion,
  as T1 did for ranch-style and modern-farmhouse-traditional, or an open question."* The options:
  - *A neo-eclectic companion* (recommended): it binds its own `rake_condition` in its own words,
    A10's precedent and T1's shape, checked independently before it lands.
  - *An open question*: no record. ranch-style's 18 to 36 in reaches neo-eclectic, disclosed in
    ranch-style's note.
- **T8 (folk-victorian, reached by the farmhouse's transcribed trim).** The check: *"folk-victorian
  is not drawn, and is not named. Its own kit permits a `pierced-bargeboard` gable_treatment,
  against this slot's rule 'never a full profiled rake or bargeboard'. That contradiction is
  pre-existing, and is now a drawable 'plain' state."* The options:
  - *Name it, and no record* (recommended): the farmhouse parameter's note names it, and this
    entry carries it. A folk-victorian record of its own would be the record
    new-urbanist-traditional reads ahead of the farmhouse's. new-urbanist-traditional is drawn, on
    bad-03, and folk-victorian is not.
  - *A folk-victorian companion*: it binds its own `rake_condition`, permitting its pierced
    bargeboard and keeping the folk house's plain trim. bad-03's rake would then be read from
    folk-victorian's record, a T-item reaching a shipped plan.
- **T11 (a record that states the rake's overhang and no member).** The check: *"Latent, in code: a
  'silent' state draws the fault's 6 in overhang and says 'THE KIT STATES NO RAKE', although this
  kit states an 18-36 in band. Neither node is drawn."* B5 draws the fault's rake where the kit
  "states it or says nothing", and the kit's own where it "states another rake". A record stating an
  18 to 36 in overhang and no member is neither. The options:
  - *Its own state: the edge kept and the band said* (recommended): the reader reads the record as
    `overhang`. The overhang stands square to a gable face and is not drawn on it, so the face
    draws the roof's edge. The sheet says the kit's band and that no member is stated. Nothing the
    kit does not state is drawn.
  - *The fault's rake, with the kit's band said beside it*: B5's letter for silence. But it draws a
    6 in overhang against a kit stating 18 to 36 in, and the kit comes first.
  - *The kit's overhang with the fault's member*: the overhang is not drawn on a gable face, so
    this is the fault's member under a rake the kit does not describe.

### The options taken

- **T7: a neo-eclectic companion.** neo-eclectic binds its own `rake_condition`: the overhang
  `rake_overhang_in`, 6 to 12 in, measured, transcribed from defining_characteristics[7]. It names
  no member, as ranch-style's does. ranch-style's note now says so in place of the disclosure.
- **T8: named, and no record.** The farmhouse parameter's note names folk-victorian, its pierced
  bargeboard and the reason it is not corrected here, and this entry carries it in this section.
  *(Corrected 1 Oct 2026, on the second independent check: this line first said it "stays in this
  entry's list of rake records left uncorrected", and this entry has no such list.)*
- **T11: its own state.** `resolve_kit.rake_at` reads a record stating `rake_overhang_in` and no
  canonical row and no trim as `overhang`. `elevation.rake_for` keeps the edge and says *"… STATES A
  RAKE OVERHANG OF 18–36 IN AND SETTLES NO MEMBER IN A ROW"*, and the census holds the legend to it.
  ranch-style and neo-eclectic read it; neither is drawn.
  - *Corrected 1 Oct 2026, on the second independent check, before anything landed.* The words
    first said "AND NO MEMBER". A record may name its member in words the reader does not parse, or
    permit one and settle none, so the words claim only what the rows say. And as first written, a
    record PERMITTING The Cardboard Gable's own rake beside its band read as `overhang` and kept the
    flush edge the fault names: it has permitted that member, so it reads as a silence does and the
    fault's rake is drawn. No record in the corpus has either shape.
  - *Read with it, not taken by analogy:* a record that forbids the fault's own rake and settles
    nothing else had read as a silence, and a silence draws the very variant it forbids. It is
    refused by its writer now (R3). No record reaches it.
