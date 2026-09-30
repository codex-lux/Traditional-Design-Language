# OQ 79 — two sourced rules give the eave cornice two different projections, and nothing is entitled to choose

*Status: CLOSED 30 September 2026 (ruled 29 September 2026; executed by WP-16.5) · Raised in: From the geometry layer (WP-5.11, 26 Aug 2026)*

**OPEN — two sourced rules give the eave cornice two different projections, and nothing is entitled to choose.** `eave_cornice()` sizes Gibbs's Ionic cornice so its HEIGHT fills `facade-classical`'s domestic envelope (2 parts of the bay module, 24.56 in here). Gibbs's own rule then fixes its projection: *"The projection of the Cornice equal to its height"*, which he holds for every order but the Doric — so the order projects **24.56 in**. `facade-classical`'s own `cornice/projection` rule says `module / 14`, which at this storey height is **10.53 in**. Both are sourced, both are about the same cornice on the same wall, and they differ by a factor of 2.3. This is the OQ 48 class — two packs meaning different quantities at one address — but at the CASCADE scope OQ 48 explicitly did not close, and it is not a naming collision that a `quantity` field can separate: they genuinely disagree about how far the thing sticks out. The record now carries both (`order_relief_beyond_frieze_in`, `envelope_projection_in`) with a `projection_disagreement_note`, the detail inset draws the order's own profile and the elevation band draws the envelope's figure, and the sheet prints both and says both are sourced. That is disclosure, not resolution. A ruling would say which governs a domestic front — most likely the envelope, with the order read as the profile's SHAPE and not its depth, but that is a judgment about what "reducing an order" means and it belongs to Lucas. Nothing should silently pick one before then.

**AMENDED 28 SEP 2026 (Phase 15, WP-15.7): the face now draws the members, and the question is
unchanged.** Lucas, of the drawn Tidewater front: *"the cornice not being represented on this
export"*. The face drew one box at the envelope's figure, with the frieze inside it at the same
projection. It now draws, from `elevation.cornice_marks`:

- the frieze flush, as facade-classical's own member states it;
- the cornice's box, still at the ENVELOPE's figure;
- a line at every member division inside the box, at the height the order's record states.

So the member HEIGHTS are drawn and the member PROJECTIONS are not, because the projections are
this question. The corner of the box is a boxed cornice's corner, which is what facade-classical
calls this band (*"a boxed modillion or dentil cornice at domestic scale"*). Ten of the 159
resolved kits bind the envelope's rule as their own `cornice.projection_in` (module / 14,
`source: facade-classical`). They are the American Georgian and Federal line, Tidewater's among
them; none of the English Georgian nodes does. That is evidence for the reading this entry calls
most likely, and not a ruling. The inset's caption now says which surface draws which: *"THE FACE DRAWS THE
ENVELOPE'S, THIS PROFILE THE ORDER'S (OQ 79)"*. Drawing the order's profile at the face's corners
means choosing, and waits on the ruling this entry asks for.

## Ruled 29 September 2026 (Lucas, asked directly): the envelope's depth, the order's shape, and a 2½ in bed mould

- **The projection.** *Envelope depth, order shape*: the envelope (module/14) governs how far a
  domestic cornice projects. Gibbs's profile is scaled into that depth, so the face and the inset
  draw one cornice with the order's proportions. Member heights are kept and projections scaled.
  This is the reading the entry above called most likely.
- **The bed mould.** *Hold it at 2½ in*: the bed mould keeps the 2½ in that the fault's own note
  gives for a real bed mould (after Benjamin). The members above share the rest of the envelope's
  depth in Gibbs's proportions. The figure is labelled a judgment on the inset and in the record.
  This was asked because a uniform scale makes the bed mould 1.2 in on Tidewater and 1.0 in on the
  spec Colonial, under `bed-mould-omitted`'s 1.5 in floor.

Executed by WP-16.5. This entry closes when that package lands.

## Executed 30 September 2026 (WP-16.5): one cornice

- **The envelope's depth in the order's shape.** `elevation.scale_into_envelope` keeps each
  member's height and maps its relief in two linear pieces:
  - the bed mould's members onto [0, 2½ in], so the bed group's outer face stands at 2½ in;
  - every member above onto [2½ in, the envelope], so the order's greatest relief lands on the
    envelope.

  On Tidewater the order's own 24.56 in becomes the envelope's 10.52 in. On the spec Colonial,
  20.09 in becomes 8.61.
- **One cornice on every surface.** The face's box and the inset's profile stand at one figure.
  The inset's caption says what was scaled and that the bed mould is a judgment, and the DXF says
  the same beside its profile. The record carries the order's own figure (`order_own_relief_in`)
  beside the envelope's, and `projection_ruling` in place of the disagreement note.
- **The bed mould is a judgment and is not published.** `bed_mould_projection_in` is in
  `elevation.NOT_MODELLED`: a figure chosen to keep `bed-mould-omitted`'s floor cannot be the
  measurement that fault is judged on. The fault stays clear on its governing test, and the clear
  names the unrun secondary.

**A correction to the question's figures (30 September 2026).** The question said a uniform scale
makes the bed mould 1.2 in on Tidewater and 1.0 on the spec Colonial. Those were the cyma's
figures, because the elevation published the first bed member as the bed mould's projection. The
ruling is executed on the bed group's outer face, the fillet, as the plan specified: how far a bed
mould stands out is how far its outermost member does. Under a uniform scale the fillet would stand
at 1.62 in on Tidewater and 1.33 on the spec Colonial:
under the fault's 1.5 in floor on seven of the eleven drawn plans, not on all. The ruling holds the
outer face at 2½ in either way, and the cyma stands at 1.875 in beneath it.

**Both halves of the ruling are executed, so this question is closed.** Report:
`docs/reports/wp-16.5-one-cornice-and-the-gable-end.md`.
