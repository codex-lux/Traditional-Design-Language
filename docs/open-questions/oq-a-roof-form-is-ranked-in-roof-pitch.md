# oq/a-roof-form-is-ranked-in-roof-pitch — two kits rank roof forms in the pitch slot, and B1 reads the form slot

*Status: OPEN · Raised in: WP-16.9, the roof, the rake and the deeper cornice (1 October 2026)*

**english-georgian and new-england-georgian each rank roof forms as variants of their `roof_pitch`
slot.** english-georgian's `roof_pitch` makes `side-gable` canonical, `hip` permitted, `mansard`
atypical and `gambrel` forbidden, noted *"An American and Dutch answer, not an English one."*
new-england-georgian's makes `side-gable` canonical and `hip` and `gambrel` permitted. Both slots
also state the pitch itself (`pitch_min`, `pitch_max`, `pitch_typical`).

**B1 reads `roof_form`.** So each ranking is read by nothing that draws a roof, and nothing holds the
two slots together. On english-georgian they already disagree: Lucas's answer B11 (30 September
2026) made the hip canonical in `roof_form`, beside the side gable, and `roof_pitch` keeps it
permitted. On new-england-georgian the two agree on the three forms `roof_pitch` ranks.

**What is not ruled.** Whether the form rows leave `roof_pitch` (the ontology separates the form
from the pitch), stay as a second statement held to `roof_form` by a check, or are read by B1's
reader as well.
