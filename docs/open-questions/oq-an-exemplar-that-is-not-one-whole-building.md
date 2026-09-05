# oq/an-exemplar-that-is-not-one-whole-building — an archive, a body of work and a phase, and none of the three can carry a precedent

*Status: RULED 5 Sep 2026, the same day it was raised · Raised in: WP-11.3, Tranche 2 of the precedent bench (5 Sep 2026)*

**THIS ENTRY OVERSTATED ITS CASE AND THE CORRECTION CAME BEFORE THE RULING.** It framed the archive
and the body of work as a STRUCTURAL LIMIT -- "a precedent record is ONE BUILDING: that is the whole
design of `precedents/`". That is false about the corpus it describes. **Thirteen records already are
not one whole building**, each written deliberately and each saying so in its own `note`: six historic
districts (`bungalow-heaven-landmark-district`, `brooklyn-heights-historic-district`,
`south-end-historic-district-boston`, `henderson-place-historic-district`,
`east-alvarado-historic-district`, `richmond-heights-pioneer-historic-district`), two developer type
models (`levittown-ranch-model`, `levittown-cape-cod-model`), four documented groups
(`villard-houses`, `project-row-houses`, `woodward-development-houses-chestnut-hill`,
`faubourg-marigny-and-bywater-shotgun-rows`) and one magazine house
(`life-magazine-eight-houses-wills-house`). The corpus had answered the question thirteen times before
it was asked, and `check_precedents.py`'s `DISTRICT_RE` exemption in the duplicate-archival-id rule
was already that practice encoded. **Found by executing a classification over all 693 exemplars, not
by re-reading the sentence** -- WP-9.5's rule, inside the entry that needed it.

**RULED 5 SEP 2026 BY LUCAS, on the corrected question: RATIFY THE PRACTICE AND ADD A `no_precedent`
REASON FIELD.**

1. **A precedent record may be a `building`, a `district`, a `type-model` or a `group`**, declared in
   a new optional `record_kind` on the record rather than inferred from a note and a regex over a
   title. For `minimal-traditional` and `ranch-style` -- post-war tract types outside HABS's charter
   entirely -- a district or model listing is the ONLY archival record that exists, so forbidding the
   class would have destroyed the best evidence those nodes have.
2. **`no_precedent` is a CLOSED enum on the exemplar** -- `archive`, `body-of-work`, `phase`,
   `not-yet-researched` -- because today NOTHING separates a stated refusal from an unresearched row.
   One number carries both, and after Tranche 3 it will read about 191 whether that is 191 gaps or
   188 gaps and 3 decisions. A `why` is prose and no counter can read it.

**What the ruling leaves standing.** The exact-name join stays exact and `aka` is NOT widened to
admit a phase: `precedents/gaineswood.json` is the finished 1842-1861 mansion whose survey is silent
on the dogtrot substrate, so `dogtrot-vernacular` keeps `no_precedent: phase` rather than a join that
would hand its reader the wrong card. Europe needs the field immediately -- `swiss-chalet`'s
*"Chalet-Museum / farmhouses of the Simmental"* and `tuscan-vernacular`'s *"Leopoldine farmhouses of
the Val di Chiana"* are the same shape, unlinked, waiting on Tranche 3.


**OPEN — a ruling on what an exemplar row may name.** A precedent record is ONE BUILDING: that is the
whole design of `precedents/`, and it is what lets one record be shared by every node that names it and
lets an archival id be a duplicate test. Tranche 2 finished North America with **505 of 693 exemplars
carrying a `precedent`** and 86 of 164 nodes covered, and on the 58 nodes it worked, exactly **three**
exemplars could not be linked. Not one of the three is a research gap. Each names something real that is
not one whole building, and they fail in three different ways:

- **An ARCHIVE.** `garrison-revival` names *"Royal Barry Wills Associates garrison designs"*, located
  *"Boston, Massachusetts (office)"* — collection AR029 at Historic New England. The type's design
  standards really do descend from that office, and there is no building to point at.
- **A BODY OF WORK.** `monterey-revival` names *"Cliff May's early Monterey-mode houses"*. The exemplar's
  own `why` names two candidate addresses and declines to pick one without a reading that says which is
  Monterey-mode.
- **A PHASE.** `dogtrot-vernacular` names *"Gaineswood (original core)"* — and `precedents/gaineswood.json`
  exists, for the same building, cited by `greek-revival-southern-plantation`. This is the sharp one,
  because a link is available and is wrong: the record is the finished Greek Revival mansion of 1842-1861,
  whose 1930s survey names porticoes and a porte cochere and states not one dimension, and the dogtrot
  substrate is a phase that survey is silent about. Joining them would hand a `dogtrot-vernacular` reader
  the mansion's card as the dogtrot's evidence.

**All three are STATED rather than silent, which is the interim position and not the answer.** Each of the
three carries a `standing` and a `why` beginning with the refusal, in the form `monterey-revival` set. A
reader of the node sees why no record is named. Nothing counts them.

**What is not ruled.**
1. **May an exemplar name something that is not a building at all?** Two of the three do. If yes, the
   schema should say so and the refusal should be a FIELD rather than a sentence inside `why`, so it can
   be counted and so `check_precedents.py` can tell a stated refusal from an unresearched row — today it
   cannot, and 188 unlinked exemplars on the European trunk are indistinguishable from these three.
2. **May two exemplars name two phases of one building?** If yes, the phase needs somewhere to live. The
   exact-name join is deliberate (`check_assets.py` reads the exemplar name as a harvest key), so the
   available mechanism is `aka` — and *"Gaineswood (original core)"* is not an also-known-as, it is a
   qualified reference to a part. Admitting it would weaken the name join for all 415 records to serve
   one row. The alternative is a `phase` field on the exemplar, read by nothing yet.
3. **Does a refusal need a standing?** All three carry `documentary`, which reads oddly on an archive: the
   drawings ARE documentary, the exemplar is not a building of documentary standing. The vocabulary was
   written for buildings.

**Recommended: (1) as a field, and refuse (2).** A `no_precedent` reason on the exemplar — a closed
vocabulary of `archive`, `body-of-work`, `phase`, `not-yet-researched` — makes the refusal countable,
lets the checker separate a stated refusal from a gap, and costs one schema field. Refusing (2) keeps the
name join exact, which is worth more than one link; the phase stays a sentence in `why`, where a reader
gets the whole argument rather than a join that quietly asserts the wrong building.

**Do not close this by linking Gaineswood.** The link is the cheap move and it is the one that puts a
false card in front of a reader, which is the failure mode this whole layer exists to prevent.
