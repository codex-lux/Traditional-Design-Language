# oq/the-roof-layer-draws-no-complex-or-polygonal-roof — Queen Anne's ridge, the octagon's eight hips, a cross-gable's wing and a gablet

*Status: OPEN · Raised in: WP-16.9, the roof, the rake and the deeper cornice (1 October 2026), on Lucas's answer B15 (R-5) of 30 September 2026*

**The roof layer draws seven forms over one rectangle: gable, side-gable, front-gable, hip,
gable-on-hip, cross-gable and gambrel.** B1 now reads each style's canonical form, so the forms it
cannot draw are reached, and each is said rather than guessed.

- **Queen Anne's complex ridge.** Four Queen Anne nodes (queen-anne-american, -free-classic,
  -patterned-masonry and -spindled) make several forms canonical, none of them the side gable, so B7
  draws the fallback. Their fallback is forbidden, so B8 draws no roof and says so. Lucas's answer
  B15 leaves it there: no roof, said, and no record changes.
- **The octagon's eight hips.** octagon-house's own record (WP-16.9) makes `low-hip` canonical, *"A
  low eight-hipped roof converging on a flat deck or a cupola"*. The table maps `low-hip` to `hip`,
  and the placer draws the house as a rectangle, so the roof is drawn as a four-hipped roof over it.
  The elevation does not draw octagon-house; its roof plan and model would.
- **A cross-gable's wing.** Twelve nodes are drawn cross-gabled. roof.py draws one centred wing with
  no valley geometry, and the elevation's gable ends are the main ridge's two (`elevation.gable_faces`
  reads `W` and `E` for a ridge on x). The wing's own gable is not drawn on the face it fronts. None
  of the twelve is among the 41 styles the elevation draws, so this is latent there.
- **A gable-on-hip's gablet.** The elevation draws a gable-on-hip as a hip (no gable faces), and
  roof.py refuses its end stacks as for a hip. No node is drawn in this form today.

**What is not ruled.** Whether any of these is drawn, and from which record. Each needs geometry no
record states: the ridge plan of an irregular roof, an octagonal footprint, a wing's position and
valley, a gablet's height.
