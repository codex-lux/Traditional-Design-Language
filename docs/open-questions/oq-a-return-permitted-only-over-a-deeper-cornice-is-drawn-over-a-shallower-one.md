# oq/a-return-permitted-only-over-a-deeper-cornice-is-drawn-over-a-shallower-one — a conditional permission, and a house that fails the condition

*Status: IN PROGRESS (ruled 30 September 2026, B4; executed by WP-16.9) · Raised in: WP-16.5, one cornice and the gable end (30 September 2026)*

**colonial-revival permits a cornice return on a condition, and the cornice this elevation draws
fails it on six of the seven shipped plans that inherit the record.** The record binds the full
return `permitted`, with nothing canonical. It states `min_cornice_projection_for_return` as 10 in,
measured, from the style's own constraint c04: *"A cornice return is permitted only where the eave
carries a full classical cornice of at least 10 in. projection continuing around the corner."*
Five more nodes receive the record through the cascade: dutch-colonial-revival, garrison-revival,
georgian-revival, neoclassical-revival and new-classical. Four of the six are styles the elevation
draws.

**The drawn cornice is the envelope's** (OQ 79, R9: facade-classical's module/14):

- 8.61 in on the spec Colonial, bad-01, bad-02 and bad-07 (colonial-revival);
- 9.57 in on bad-05 (colonial-revival) and good-02 (georgian-revival);
- 11.48 in on good-07 (new-classical), the one plan that meets the condition.

**What WP-16.5 does.** Under R8, a return the kit permits and does not settle keeps the band across
the gable end, and the sheet says the return is unstated. The words said the kit "PERMITS ONE",
which the record's own condition makes false on six of those houses.

- `resolve_kit.return_at` now reports the condition and who wrote it (`min_cornice_in`,
  `min_cornice_by`).
- The sheet and the DXF say it beside the drawn figure: *"RETURN UNSTATED — COLONIAL-REVIVAL'S KIT
  PERMITS ONE ONLY OVER A CORNICE OF AT LEAST 10 IN, AND THIS ONE PROJECTS 8.6 IN; THE CORNICE IS
  DRAWN ACROSS THE GABLE END"*.
- The drawing does not change.

**Why the drawing does not change.** The band across the gable end is the cornice carried round
the corner and across it, which is what c04 permits only over a 10 in cornice. So the sheet draws,
under words that say so, a thing its kit's condition does not permit. Reading a failed condition
as a ban would draw the end profile instead, as R8 does for a forbidden return. But that carries
A3's reading of a dated ban to another axis, and a ruling is not extended by analogy here. It would
also move six shipped plans. `return-that-never-returns` would then convict all six (serious); its
`severity_by_style` names colonial-revival as *"Where this fault lives"*.

**Three readings, each with its cost.**

1. **A failed condition is a ban.** The six draw the end profile, and the fault convicts them.
2. **The band stays, said honestly**, as now. The condition is a note on the sheet.
3. **The cornice is too shallow for the style.** c04's 10 in outranks the envelope's module/14 on
   these houses, and the cornice is drawn deeper. That reopens R9 for one family, and needs a
   ruling on which record governs a cornice's depth.

**What is wanted.** Which reading governs a conditional permission whose condition the drawn house
fails. `min_cornice_projection_for_return` is the only condition `return_at` reads, so the answer
decides these six plans and the four drawn styles that carry the record.

## Asked and answered 30 September 2026 (Lucas, asked directly): B4

Put to Lucas on the evening of 30 September 2026 and answered by 18:13 UTC.

### The question, as put

*"colonial-revival's own constraint c04 permits a cornice return only over a cornice of at least
10 in. The elevation draws the envelope's cornice (R9): 8.6 in on the spec Colonial, bad-01, bad-02
and bad-07, and 9.6 in on bad-05 and good-02. The band kept across their gable ends is what c04
conditions. How should that permission be read?"* Four readings were offered:

- **the style's 10 in governs** (recommended; reading 3 above);
- a failed condition forbids it (reading 1). Here `return-that-never-returns` convicts all six, and
  its correct practice (*"there is no house so plain that this rule does not apply"*) contradicts
  c04 on these houses;
- the band stays and the sheet says so (reading 2, the drawing as WP-16.5 left it);
- the plain 6-12 in mitred return the fault names as the minimum for a plainer house, which reads
  c04 as governing only the full return.

### Lucas's answer

**B4: the style's 10 in governs.**

> Where a style's kit states a minimum cornice for its return, the cornice is drawn at least that
> deep. On these six that is 10 in, deeper by 0.4 to 1.4 in, in projection only; the heights are
> kept. The condition is then met, the band stays under R8, and the sheet's words agree with the
> drawing. It is an exception to R9 for colonial-revival and the five styles that inherit its
> record.

### What executing it needs (WP-16.9)

- **`return_at`'s condition feeds the cornice's depth.** The eave cornice is scaled into the
  larger of the envelope's figure and the kit's minimum. The bed mould stays at 2½ in (R9a), and the
  members above take the rest.
- **The sheet and the DXF name both figures and who wrote the minimum.** The words for a failed
  condition stay for a record whose cornice cannot be deepened.
- **Measured on the six plans:** the cornice and the inset move in projection only. The roof, the
  eave height and every other figure are unmoved.
