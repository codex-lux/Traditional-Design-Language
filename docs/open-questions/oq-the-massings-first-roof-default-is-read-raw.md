# oq/the-massings-first-roof-default-is-read-raw — eleven of forty massings name a roof the roof layer does not draw first

*Status: OPEN · Raised in: WP-16.9, the roof, the rake and the deeper cornice (1 October 2026)*

**Where a plan declares no roof and its style's kit decides nothing the roof layer draws, the
massing's first-listed `roof_default` decides it, and it is read raw.** Under Lucas's answer B1 (30
September 2026) the order is the plan's declaration, then the style's canonical `roof_form` read
through the closed table `build/roof_vocabulary.py`, then the massing's default, then the roof
layer's own default. The kit's rows go through the table. The massing's default does not:
`threshold.roof_form_reading` hands `roof_default[0]` to the roof layer as written.

**Measured on 1 October 2026: 11 of the 40 massing records name a first default that is not one of
the seven forms `build/roof.py` draws.**

- Three map to a drawn form through the table and are not drawn as it: `low-hip` on
  `prairie-cruciform`, `courtyard-full` and `octagon`. The table maps `low-hip` to `hip`. Read raw,
  the roof layer says *"Roof form 'low-hip' is not one of gable/hip/gambrel/cross-gable -- geometry
  not modelled"*.
- Three are spelled with a space and are in no table at all: `low side-gable` on `ranch-linear` and
  `split-level`, and `low cross-gable` on `ranch-l`.
- Five name forms the roof layer does not draw: `saltbox`, `mansard` (`mansard-block`),
  `pyramidal` (`foursquare`, `pyramidal-cottage`) and `flat-parapet` (`townhouse-row`). Each is
  said as unmodelled, which is honest.

**And the ban check reads the raw id against the kit's drawn forms.** B8 (no roof, said, where the
fallback is forbidden) looks up `roof_default[0]` in `kit_roof`'s `forbidden` map, which is keyed
by the form the table maps each forbidden row to. A massing whose first default is `low-hip`, under
a kit forbidding the hip, is not refused, because `low-hip` is not a key. No shipped plan reaches this today.

**Who reaches the fallback.** Over the 164 nodes, `kit_roof` reads `kit` on 73, `silent` on 58,
`undrawable` on 25 and `several` on 8. A plan on any of the last three that names a massing falls to
that massing's default. Fourteen of the sixteen shipped plans name no massing
(`oq/fourteen-of-sixteen-plans-name-no-massing`); the composer's candidates name one.

**What is not ruled.** Whether the massing's default goes through the same table as the kit's rows,
and whether the three spaced spellings are corrected in their massing records or mapped. Reading it
through the table would draw `prairie-cruciform`, `courtyard-full` and `octagon` hipped where they
are unmodelled today. That moves drawings, so it is not done without a ruling.
