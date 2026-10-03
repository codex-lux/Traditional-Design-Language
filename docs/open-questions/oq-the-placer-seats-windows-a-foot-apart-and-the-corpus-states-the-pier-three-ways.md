# oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways — which ratio governs the wall between two windows

*Status: CLOSED 1 October 2026 (ruled 29 September 2026; U1–U4 taken as recommended under a standing instruction; executed by WP-16.6; the corner pier is `oq/the-wall-at-the-corner-is-ruled-by-nothing`) · Raised in: Phase 15, WP-15.6, the pier between openings (28 September 2026)*

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

## Ruled 29 September 2026 (Lucas, asked directly): a floor, an aim, and the upper window follows the ground

Five answers, each put as its own question:

- **The governing figure.** *Floor 1.0×, aim 1.4×*:
  - the placer never seats two windows closer than the fault's 1.0 × the wider window;
  - where it can't, it refuses the window by name, as the doorcase rule does;
  - it aims for sash-light's 1.4 × where the wall allows;
  - the Georgian kit's unsourced band is brought into line.
- **Which window yields.** *The centre holds*:
  - windows nearer the entrance keep their places, and on other faces those nearer the face's
    centre do;
  - the outer window moves along its own wall, or is refused by name if it can't.
- **Ganged windows.** *Spare the licensed styles*. The five styles the fault licenses to gang
  windows are spared: craftsman, prairie-school, tudor-revival, richardsonian-romanesque and
  shingle-style. The placer reads the licence's style list, not its checks.
- **Alignment (the amendment above).** *Upper follows the ground*: the ground floor carries the
  doorcase and the entrance, so it sets each bay. The window above moves onto it, or is refused by
  name where its own room cannot take it there.
- **Nothing below.** *Keep it; the fault judges*. An upper window with no ground opening under its
  room's stretch of wall stays where the placer put it, and the alignment fault reports the front.

**Read together, not ruled separately:** an upper window that, once aligned, would break the upper
pier floor cannot be taken there, so it is refused by name.

The corner pier at a doorcase is not ruled and stays open here. Executed by WP-16.6.

## Executed 1 October 2026 (WP-16.6): the floor, the aim, and the upper window on the axis below

- **One reader, `build/window_pier.py`.** It reads three things:
  - the floor, from this fault's primary test (1.0 x the wider window);
  - the aim, sash-light's `opening_width * 1.4`, where that pack is delivered to the style
    (53 of 164 nodes);
  - the spared styles, this fault's `exceptions[].style`, by exact id.

  The placer, the composer's window cap and census V26 read it, and none carries a 1.0 or a 1.4
  of its own.
- **The placer seats each face line from its centre out.** The centre is the entrance door's axis
  on the entrance front, and the face's centre elsewhere.
  - Every unit stands at least the floor from the next window on the line, whichever room it
    lights.
  - A unit takes the aim where that costs no later window.
  - A unit that cannot keep the floor is refused by name, `rule: pier`.
  - The five licensed styles keep the old foot inside one room, and their sheets say so where a
    wall falls under the floor.
- **The upper storey follows the ground.**
  - An upper window whose room has an opening below its run stands exactly on that opening's axis,
    or is refused by name, `rule: alignment`. That covers a room that cannot take the axis, and
    (R5 with R6) a wall to the next window that would fall below the floor.
  - A window with no opening below its room's run stays where the pier rule puts it, and the
    alignment fault judges it.
- **The Georgian kit's band** is brought into line: `pier_measured_ratio` [1.0, 2.0], still
  editorial.
- **This fault reads the drawn pier.** Its primary test had read `adjacent_opening_width_in`,
  which nothing supplies, so it never ran. It reads `narrowest_pier_over_wider_adjacent_window`
  now, glass edge to glass edge as its note asks, and is not applicable on a front with no two
  windows side by side.

**Taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put.** The code met
four choices the ruling's words did not settle, and the recommended option was taken for each:

- **U1.** An upper unit left over when its room's openings below are all taken goes to R6a: it
  stays where the pier rule puts it, and the alignment fault judges it.
- **U2.** The pairing of upper units with the axes below takes the axes the room can take before
  one it cannot. A unit left with an axis its room cannot take is refused by name.
- **U3.** The aim is taken pier by pier, wherever it costs no later window, and never face by face.
- **U4.** Where the widest door on the entrance front is a garage door, the face's centre holds. No
  doorcase frames a garage door, and a garage door is no entrance.

Two more readings are stated rather than chosen:

- R6 applies to every style, because R5b spares the pier floor and nothing else. *(Corrected 2 Oct 2026, WP-16.8, auditor A: false of the code. A licensed style's line keeps the old foot in record order with no aim, so R5b spares R5a's centre-out order and the aim too (U10); and the aim reaches only the 53 nodes sash-light is delivered to, a reading of R5 (U11). Both taken as recommended under Lucas's standing instruction of 1 Oct 2026 and never put.)*
- The composer's cap reads the floor for every style, because the composer composes no band.

*(Added 3 Oct 2026, WP-16.8, the audit of Phase 16, auditor A.)* Two more readings decide a shipped
refusal and were named nowhere. Both are taken as recommended under Lucas's standing instruction of
1 Oct 2026, and neither was put:

- **U12.** A face line that is not the entrance front's, a hyphen's among them, takes its own centre
  and not the entrance axis. The Tidewater hyphen's S line holds about its own centre at -3.5 ft.
- **U13.** Of two units equidistant from the centre, the lower coordinate is seated first. backhall's
  units at -4.667 and -2.333 are equidistant from -3.5, so the unit at -2.333, nearer the entrance,
  is the one refused for the pier. The same key orders the one queue the audit put in place (A1),
  which seats aligned and unaligned units together, nearest the centre first: R5a with the ruled
  "read together", where WP-16.6 seated every aligned unit first and called the order R6.

**Measured on the sixteen shipped plans against `bb3c6de`, on the deterministic engine:**

| | before | after |
|---|---|---|
| window piers drawn | 35 | 24 |
| narrower than 1.0 x the wider window | 24 | 0 |
| narrower than the 1.4 aim | 25 | 8 |
| exactly the old foot | 12 | 0 |
| window units placed | 98 | 85 |

Of the 13 units newly refused, 11 are refused for the floor and 2 for the axis below. Five more,
which the old foot already refused, are now said in the floor's words. The pier fault leaves
could-not-evaluate on 11 plans: clear on four (1.26 to 7.99 x the wider) and not applicable on
seven, whose fronts have no two windows side by side. *(Corrected 3 Oct 2026, WP-16.8: four of those
eleven fronts are incomplete. The placer refused the windows that would break the floor, and the
fault cleared on what was left, or read no pier over rooms declaring two (auditor B). The pier figures
are withheld on an incomplete front now (U8, taken as recommended, never put), and every test of the
fault is gated alike (auditor A). On the sixteen plans the fault is clear on one, not applicable on
three, and could-not-evaluate on twelve.)*

**What the execution raised:**

- `oq/the-centre-holds-and-refuses-a-window-the-floor-would-seat`: 7 of the 16 units refused for
  the floor would stand at it if the inner window moved;
- `oq/the-even-bay-fault-judges-the-drawn-parity-of-an-incomplete-front`;
- `oq/the-wall-at-the-corner-is-ruled-by-nothing`, which carries this entry's corner pier.

**Every ruled half is executed, so this question is closed.** Report:
`docs/reports/wp-16.6-the-pier-and-the-axis-below.md`.
