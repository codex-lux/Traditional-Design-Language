# oq/the-model-draws-only-a-gable-roof — B1 hands two shipped plans a hip and a gambrel, and the model and the IFC draw neither

*Status: OPEN · Raised in: WP-16.9, the roof, the rake and the deeper cornice (1 October 2026)*

**The scene and the IFC construct a roof for the gable family only, and say so for the rest.**
`scene._roof` reads *"GABLE ONLY"*: for a hip, a gambrel or a cross-gable it writes a `not_modelled`
entry naming the form, because roof.py gives a hip's lines in plan only, a gambrel's break offsets
and no valley for a cross wing. `export_ifc` models roof geometry for `gable`, `side-gable` and
`front-gable` (`GABLE_FORMS`) and carries the others' form and pitch as properties with a geometry
note.

**Until B1 no shipped plan reached the refusal: every one was drawn side-gabled.** Under B1 the
style's kit decides, and two shipped plans are no longer gabled:

- good-01 (shingle-style) is drawn as a gambrel. The model carries no roof planes and names *"roof
  planes for form 'gambrel'"*: *"roof.py states the form and its pitch; the planes of a gambrel are
  not dimensioned by any record this layer reads"*.
- good-05 (italian-renaissance-revival) is drawn hipped, with the same entry for the hip.

Before B1 both models carried a side-gabled roof their kits do not make canonical. Now they carry
none, and say why. That is the honest direction, and it is a loss a person sees in the Round.

**What is not ruled.** Whether the model constructs a hip and a gambrel from roof.py's figures (a
hip's planes follow from its eave, its pitch and its ridge; a gambrel's from its break and its two
pitches), and which records state the figures it would need.
