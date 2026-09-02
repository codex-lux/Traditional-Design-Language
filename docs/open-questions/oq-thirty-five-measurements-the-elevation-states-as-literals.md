# oq/thirty-five-measurements-the-elevation-states-as-literals — the critic convicts every classical plan of the same faults, and the numbers are the generator's

*Status: OPEN · Raised in: WP-9.1, the critique (1 Sep 2026)*

**OPEN — `build/elevation.py::_derive_measurements` states 35 measurement names as bare
numeric literals and four more as a real figure scaled by a literal, and the fault corpus
convicts both shipped reference plans on several of them with identical values.** Measured by
`build/critic_suspects.py`, an AST read of the function, and ratcheted by
`build/check_critic_suspects.py` (35 literals, 4 ratios; both may only go down):

| the finding, on BOTH shipped plans | the number it reads | where |
|---|---|---|
| `surround-that-lies-about-the-wall`: 4.0 against at-least 6.0 | `window_reveal_depth_in: 4.0` | a literal, line 1084 |
| `casing-at-a-third-of-palladio`: 0.6 against at-least 1.05 | `window_casing_width_in = casing * 0.6` | a ratio, line 1083 |
| `doorhead-that-collides-with-the-cornice`: −79 against at-least 12 | `entablature_bed_height_in = surround * 0.3` | a ratio, line 1171 |
| `column-without-entasis`: 1.0 against 0.75–0.87 | upper and lower shaft diameter set equal, because "no entasis rule exists anywhere in this pack, or in this codebase" | the generator's own comment, editorial entry `cs-parallel-shaft` |
| `wing-pitch-drift`: 0.0 against at-least 8.0 | `min_absolute_difference_between_distinct_slope_angles_deg: 0.0` on a ONE-slope roof | a literal, line 1305 — **guarded in data by WP-9.1** (`applies_when` on the slope count) |

A sweep over the 11 in-scope plans (both shipped, nine of the fourteen reference plans that
the generator will front) finds **61 names identical on every plan**, 33 of them not literals
at all — figures read from a pack that never changes (`sash_stile_width_in: 2.0`), counts the
generator asserts by construction (`distinct_head_datums_per_storey_per_elevation: 1` is
opening-proportion's own hardest rule, applied), and a handful nobody has looked at
(`exposed_foundation_height_on_the_principal_elevation_in: 24.0` convicts
`house-without-a-base` on every plan at 30 against 48).

**This is OQ 52's residue.** That question swept twelve INVENTED constants out of the
measurements and guarded the class with `NOT_MODELLED`; what it could not reach is a
constant that is honestly a fact about the generator — a reveal the generator draws at 4 in
because it draws every reveal at 4 in — published under a name the fault corpus reads as a
fact about the house. The corpus is doing exactly what it should with the number it is given.
The number should not be given.

**What WP-9.1 did about it, and what it deliberately did not.** `build/critique.py` marks a
fault whose failing test reads one of these names `critic-suspect`, attaches the instrument,
the value and the line, and the revision loop (WP-9.2) never acts on one — a loop that
obeyed these would spend its rounds chasing the generator. It did NOT withdraw the 35 into
`NOT_MODELLED` or model them, because each is a separate decision: some are measured facts
(`total_shutter_leaves: 0.0` on a house whose kit forbids shutters is a real zero, OQ 89),
some are the pack's rule stated as its own consequence, and some are the generator inventing
a proportion. Being a suspect is not being wrong. `six-eight-door-in-a-tall-room` at 0.638
on an 11 ft ceiling reads no literal and may be a real door.

**The ruling needed:** for each of the 35 + 4, one of — model it (read it from a record or a
pack, so it varies with the house); withhold it (`NOT_MODELLED`, with the reason, so the fault
returns unjudged); or declare it a fact-by-construction (an `applies_when`, or a note on the
fault, so the corpus knows the generator asserts it rather than measures it). The ceilings in
`check_critic_suspects.py` come down as each is decided.
