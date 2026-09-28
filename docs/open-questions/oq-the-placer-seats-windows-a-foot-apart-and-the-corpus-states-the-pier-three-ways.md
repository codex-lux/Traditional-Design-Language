# oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways — which ratio governs the wall between two windows

*Status: OPEN · Raised in: Phase 15, WP-15.6, the pier between openings (28 September 2026)*

**The wall beside the entrance doorcase is ruled now; the wall between two windows is not.**
Lucas, of the drawn Tidewater front (27 Sep 2026): *"there's still no concept of how close windows
can be to doors"*. WP-15.6 applies the rule the corpus states for the doorcase without dispute.
facade-classical's rule for the entrance composition's width says it *"is not allowed to touch the
flanking windows"*, and *"The residual wall each side of the entrance composition should not fall
below about half the ordinary pier"*. The placer reserves that run before it seats a window, and the
elevation measures it and says what it cannot judge. Between two WINDOWS the corpus states the
figure three ways, and the placer uses none of them.

**What the placer does.** `build/openings.py` seats every window `MIN_SOLID_FT = 1.0` ft from its
neighbour. That constant is editorial. Its comment says it is shared with the renderers and the CP
engine's door floor, so that the drawing and the proof agree about what fits. It does not say where
the foot comes from. `build/render_plan.py` holds a second copy of it.

**Measured on the 16 shipped plans** (`engine="heuristic"`, deterministic, after WP-15.6):

- 35 piers between two drawn windows on one storey of one face;
- **24 are narrower than the wider window beside them**, below the fault's floor of 1.0;
- 25 are below sash-light's 1.4;
- **12 are exactly 12 in**, the placer's own foot.

WP-15.6 moved none of these; it moved only the wall beside the doorcase.

**The three statements, each verbatim.**

1. **The packs, 1.2 to 2.0 times the opening, with a 1.4 figure.**
   - `sash-light`, `window_grouping_rule` / `minimum_solid_between_openings` = `opening_width * 1.4`,
     range 24 to 96 in. Its note: *"the number that looks right is a wall pier about 1.2 to 1.6 times
     the opening width, and it is remarkably stable across three centuries and both materials"*. Its
     authority note: *"Pier width between openings on Anglo-American fronts runs 1.2 to 2.0 times the
     opening width; below about 1.0 the wall reads as a colonnade of windows and above about 2.5 the
     openings read as isolated."*
   - `facade-classical`, `window_grouping_rule` / `pier_width` = `module - opening_width`, the pier
     of the ideal rhythm, range 42 to 96 in. Its note: *"Below about 1.0 times the opening the pier
     stops being able to carry an arch in brick, and below about 0.8 it stops reading as wall at
     all."* Its authority note: *"Measured piers between openings on Anglo-American fronts run 1.2 to
     2.0 times the opening width"*.
2. **The Georgian kit, 0.6 to 1.0, and it says it is editorial.** `georgian-colonial-american`'s
   `window_grouping_rule.pier_measured_ratio` is `[0.6, 1.0]`, `kind: editorial`. Its own note opens
   *"EDITORIAL, AND NO SOURCE IS RECORDED (OQ 18 …)"*. The same slot bakes both pack figures beside
   it: `pier_width_in` 72 in from facade-classical, and `pier_alt_in` 50.4 in from sash-light, each
   at a 36 in window.
3. **The fault, a floor of 1.0.** `pier-narrower-than-the-opening` tests `pier_width_in /
   adjacent_opening_width_in` at-least 1.0: *"The measured lower bound across surviving
   Anglo-American fronts."* Its severity is serious, and fatal on `georgian-colonial-american`.

**And the three do not agree.** 0.6 to 1.0 against 1.2 to 2.0 is not a rounding. The fault's 1.0
is the kit's ceiling and the packs' *"below about 1.0"*, where the packs say a front has already
changed character.

**Three things the ruling must also cover, each measured.**

- **The fault clears on a tautology.** On both shipped plans `plan_check` lists
  `pier-narrower-than-the-opening` in `fault_clear_on_a_generator_constant`. Its primary reads
  `adjacent_opening_width_in`, which nothing in this tree produces. The elevation supplies
  `pier_width_in` as the RHYTHM's pier, one bay less the storey's pack window width: 69.35 in on the
  Tidewater front, against drawn piers down to 12 in. So the fault clears on its solid-to-void
  secondary, while 24 of 35 drawn piers stand below its own floor. That is
  `oq/clear-counts-a-pass-and-a-tautology-as-one-thing` for exactly this defect.
- **`pier_width_in` means two things.** In the elevation's measurements it is the rhythm's pier.
  In the style constraints it is several other quantities:
  - a masonry base of at least 24 in (`arts-and-crafts-american`, `craftsman`);
  - 30 to 48 in (`california-mission-colonial`);
  - 18 to 30 in (`mission-revival`);
  - 16 to 24 in, a masonry pier below the gallery floor (`raised-creole-plantation`).

  Reading the drawn piers into that name would be OQ 48's error in a new place. The drawn pier
  wants a name of its own.
- **The composer caps a wall's window count at sash-light's 1.4, and the placer then seats the
  windows a foot apart.** `compose.py` spells the 1.4 inline (`int((run + unit_w * 1.4) // (unit_w
  * 2.4))`) rather than reading the pack, so the count assumes piers the drawing does not give.

**And the corner, which the doorcase rule does not reach.** Both facade-classical sentences are
about the flanking WINDOWS, so the elevation measures a doorcase's corner side and does not judge
it. On `spec-builder-colonial` the doorcase stands **2.74 in from the corner of the house**. Its
composition, 76.4 in with its sidelights, is wider than the 6 ft porch room it serves. The only
other doorcase the shipped plans draw, the Tidewater front's, has a window on one side and the
porch door on the other, and stands nowhere near a corner. The fault's own corner secondary,
`corner_return_pier_width_in / adjacent_opening_width_in`, is stated for the pier at the end of a
run of windows. Whether that reaches a doorcase is part of this ruling too.

**What was changed rather than asked.** Two packs wrote different quantities to one address. On 15
nodes `sash-light` and `timber-bay` both wrote `window_grouping_rule` /
`minimum_solid_between_openings`, under the SAME `quantity` label:

- sash-light's rule is the solid between two openings, 1.4 times the window, 24 to 96 in;
- timber-bay's is *"The minimum clear wall between the face of a post and the jamb of a window:
  about 15 in"*, 8 to 30 in.

That is OQ 48's silent corruption. `check_addresses.py` could not see it, because it judges a
collision by the authored `quantity` label, and the two labels agreed. Following OQ 48's own
procedure, the dominant meaning keeps the address and timber-bay's minority rule moves to
`solid_from_post_face_to_window_jamb` (its dimension and its quantity). Nothing in the tree reads
either address, so no drawing moves.

**What is wanted.** A ruling on which figure governs the wall between two windows, and where:

- per style or per construction;
- a floor, a target, or both;
- whether the placer may refuse a window it cannot seat at that pier.

Refusing is what the doorcase rule now does. It is the placement change with the largest reach in
this corpus: at 1.4 times the window, 25 of 35 drawn piers would have to move or lose a window.

**Until it is ruled, nothing is picked.** The placer keeps its foot, and the elevation measures
every pier and judges only the doorcase's. The fault's wiring is not moved either. Pointing it at
the drawn piers would apply one of the three statements, and choosing one is the ruling.

**Amended 28 Sep 2026 (WP-15.8, the audit of Phase 15; auditor D's D4, re-derived).** The placer
seats each storey on its own, so a window the doorcase moves no longer stands where the window
above it was placed. On `tidewater-georgian-careful`, placed on the heuristic, WP-15.6's reservation
moved the passage window from 177.50 in to 135.44 in along the south face. Its nearest upper
window, the primary bedroom's at 159.50 in, was **18.00 in** off it before the move
(`e8668e6`) and is **24.06 in** off it now (`2467585`). Neither pair stands within the 2.0 in
`storeys-out-of-vertical-alignment` allows, and that fault fires on this front either way, so no
verdict changes. But a rule that moves one storey's window and not the other's makes the
misalignment larger. That is one more thing the ruling above has to say: whether a window
the pier or the doorcase moves takes the window above it along, and which storey gives way.
