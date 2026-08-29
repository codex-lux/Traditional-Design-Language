# OQ 85 — ruled: the centre bay is blind

*Status: CLOSED 27 AUG 2026 · Raised in: From the dormer layer (WP-5.13, 27 Aug 2026)*

**CLOSED 27 Aug 2026 (WP-5.14) — ruled: the centre bay is blind.** `_face_bays()` now takes the
chimney axes for the face it is laying out and marks any bay a stack stands on `blind`; the renderer
draws no opening there at either storey, because an exterior end stack runs the full height of the
wall. The gable ends read as two glazed bays flanking a blind centre, which is what a Chesapeake end
wall is, and the long faces lose nothing — both stacks are at mid-DEPTH, so they stand in the gable
walls and in neither long wall. **A new fault, `window-on-the-chimney-axis`, catches the collision**
where a record states both, guarded with `applies_when` on the chimney count; the elevation publishes
`count_of_openings_on_the_axis_of_a_chimney_stack` as a MEASURED zero, which is the generator saying
it resolved a collision rather than that one never existed.
**One thing this does not assert, and it is worth carrying forward:** it blinds the bay where THIS
RECORD places a stack, not "a Tidewater gable end always has a blind centre". The kit makes
`paired-and-joined-by-arched-curtain` canonical — *"the tall paired stacks joined above the roof by
an arched brick curtain"* — which is TWO stacks on one gable end with the space between them spanned
by an arch, and `roof.py` places a single stack per end at mid-depth instead. Correct that
simplification and the stacks would flank the centre bay rather than stand on it, and the window
might come back. That is a roof-layer question. An exception on the fault was drafted for it and
removed: `check_faults.py` was right that an unbounded exception on the very style that raised the
problem is a loophole, not a nuance. The original entry follows.<br><br>ORIGINALLY: **a
gable-end-exterior stack at mid-depth stands in front of the centre bay, and no layer asks whether
they collide.** `roof.py` places `tidewater-georgian-careful`'s two stacks at `y_ft` 21.33,
which is exactly half the 42.66 ft depth — on the ridge line, which is right — and the kit's own source
string calls them `gable-end-exterior`. `build/elevation.py` independently gives each gable end three
bays with a window in the centre one. Drawn from grade, the stack runs straight down through the centre
window of both storeys, which is how this was found: WP-5.13 drew it that way for one revision.

It is not a drawing bug. Either the gable end has no centre window, or the stack is not on the centre
line, or (most likely for the type) the stack is a broad breast the flanking windows sit clear of and
the centre bay is blind — which is what a Tidewater end wall usually is. All three are corpus facts and
the corpus states none of them: nothing relates the chimney record's plan position to the elevation's
bay layout. WP-5.13 sidestepped it by drawing only the part above the roof, for an unrelated and
sufficient reason (the breast's width is not stated), so nothing is currently drawn wrongly — but the
conflict is still in the records, and a `chimney-through-the-window` fault would catch it if the two
layers were ever asked about each other.
