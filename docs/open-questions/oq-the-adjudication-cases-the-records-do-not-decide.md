# oq/the-adjudication-cases-the-records-do-not-decide — 152 gaps where the node's own words settle nothing, grouped by the pack that settles them all at once

*Status: OPEN · Raised in: WP-8.7, the adjudication of OQ 51's backlog (2 Sep 2026)*

**OPEN — every gap in the OQ 51 backlog has now been read, and these are the ones a record cannot
close.** 244 (node, pack) pairs were adjudicated one node at a time against the pack's own stated
subject, under a rule the repo owner set: endorse or decline ONLY where a sentence in the node's own
record affirms or contradicts what the pack says it is for; everything else comes here. 89 declines
and 3 endorsements were written. **These 152 are what is left, and they need a person.**

Twenty-one of them arrived here by being REFUSED rather than by being undecided: an adjudicator
proposed a decline, an independent adversarial check refused it, and the disagreement is itself the
evidence that the record does not settle the case. Those rows are marked ↺.

## How to use this

**Rule by PACK, not by row.** The rows are grouped by the pack that delivers them because one
judgment about a pack settles every node under it — that is the whole leverage in this backlog.
`opening-proportion` and `storey-graduation` are 42 of the 152 between them.

**Five packs are LIVE GATES** (marked ⚡): endorsing a node into `storey-graduation`, `timber-bay`,
`opening-proportion`, `facade-classical` or `gibbs-ionic` switches on real generated behaviour —
`graduation_check`, `span_check`'s capacity basis, the elevation generator. Run
`python3 build/sweep_gates.py <pack> --json` before and after and diff it. Baselines for all five
were taken before this package's first change.

**The elevation gate is an AND**, and it no longer arms nothing: `folk-victorian` and
`greek-revival-upland-vernacular` are inside `opening-proportion` already, so endorsing them into
`facade-classical` would start the generator composing a classical front for them.

**A decline is not free either.** Roughly one decline in five is half-defeated by a baked ancestor
parameter (`oq/a-baked-pack-value-is-a-second-delivery-path`), and a decline can hand a slot to a
pack that suits the node worse — `appalachian-log-house` declining `brick-course` passes
`steps_and_stoop` to a Renaissance order.


## `opening-proportion` ⚡ — 21 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `american-farmhouse-vernacular` | opening | `greek-revival-american` | Does 'classical proportion survives only as inherited habit in bay spacing and opening alignment' hand Palladio's opening rectangle -- its ratio, its head datum and a surround at one sixth to one fifth of the void -- real authority over a type whose own casing figure is 4-5 inches, and should that e |
| `california-mission-colonial` | opening | `italian-renaissance` | Should a Palladian opening-rectangle system dimension the secondary doors, window heads and sills of a single-storey adobe mission range whose own record states no opening proportion at all — knowing that endorsing arms the classical elevation generator's scope gate for the style and declining leave |
| `cape-dutch` | opening | `roman-classical` | Does Palladio's opening rectangle govern the small-paned Cape casement -- set in a 450-600 mm plastered earth wall and rationed by cape-dutch.c03 to about 15 percent of the north-west elevation -- or do entry_door, secondary_door, special_window, transom_sidelight and window_head_wood here want a Ca |
| `chateauesque` | opening | `beaux-arts-french` | Should a load-bearing ashlar style whose window heads are stone arches and lintels take its wood-trade head datum and its secondary-door graduation from the classical opening pack, given that endorsing also arms half the `build_elevation` scope gate for every Chateauesque plan? |
| `churrigueresque` | opening | `italian-renaissance` | Does a style record that is wholly silent about window rectangles, head datums, sills and transoms — an ecclesiastical Spanish and New Spanish style whose record speaks only of the portada — take the Palladian Anglo-American opening rectangle by default, given that endorsing it here also arms the el |
| `egyptian-revival` | opening | `greek-revival-american` | May a style whose opening proportions are stated to be copied from temple plates take Palladio's opening rectangle anyway, given nothing else in the corpus would dimension its secondary door? |
| `french-eclectic` | opening | `beaux-arts-american` | Does French Eclectic take the Palladian opening rectangle as the authority behind its own stated casement proportions, given that endorsing also arms half of build_elevation's scope gate on a node that binds no classical facade pack -- and if not, is losing all dimensioning on secondary_door and win |
| `french-normandy-revival` | opening | `beaux-arts-american` | Should opening-proportion's rectangle rules govern grouped casements on a picturesque asymmetrical elevation — accepting that endorsing it arms half of build_elevation's classical scope gate — or should secondary_door and window_head_wood stay undimensioned until a casement-grouping pack exists? |
| `italian-baroque` | opening | `italian-renaissance` | Does italian-baroque's stated inversion of Palladio -- enumerated as wall, rhythm, column plane and pediment -- reach Palladio's own door-and-window chapters, and is the corpus content for an endorsement here to stand as the pre-armed half of build_elevation's AND gate against the day facade-classic |
| `italian-villa-vernacular` | opening | `roman-classical` | Does a node that states its own graded-by-storey window ratios yet calls itself non-treatise take Palladio's opening rectangle for the four slots it has not dimensioned itself (window_sill, window_head_wood, secondary_door, transom_sidelight), noting that endorsing arms only half of build_elevation' |
| `mexican-colonial` | opening | `italian-renaissance` | Does this record's seismic wide wall-to-opening ratio, together with its declared independence of the portada from the fenestration, amount to a refusal of Palladio's head datum and opening rectangle for a New Spain courtyard house -- or is it silence about openings, in which case a Palladian rule d |
| `mexican-hacienda` | opening | `italian-renaissance` | Does 'no elevation is composed as a whole — the composition is a plan' refuse this pack's single-head-datum-across-an-elevation rule, given that an endorsement here also arms the build_elevation scope gate (half of an AND with facade-classical) for every plan of the style? |
| `mudejar` | opening | `roman-classical` | Should the Anglo-Palladian opening rectangle -- head datum, storey diminution, transom and sidelight, and a wood window head -- dimension the doors and windows of a brick-and-carved-plaster tradition whose openings of consequence are arches under an alfiz, bearing in mind that endorsing also arms th |
| `neo-eclectic` | opening | `minimal-traditional` | Does neo-eclectic's constraint c03, which restates opening-proportion's own head-datum rule as an enforcement against the style's named failure, endorse this pack as an authority for the node — or does the node's record only quote the rule as the thing it fails, with the datum authority already assi |
| `new-mexico-adobe` | opening | `italian-renaissance` | Should a classical opening-rectangle authority delivered from italian-renaissance at cascade depth 7, with no lineage edge, govern the openings of a flat-roofed adobe house — and is arming the elevation generator for this style acceptable on a record that states its window band without stating a rul |
| ↺ `norman-romanesque-english` | opening | `roman-classical` | JUDGMENT RIGHT, EVIDENCE WRONG. The quote is verbatim (and `check_declines` would accept it -- it only tests presence in the node file, so the build is not the guard here), but it does not bear on this pack's subject with the force the reason claims, and it is the weakest sentence available for the  |
| `scottish-baronial` | opening | `regency` | Does the node's stated 1.6:1 to 2:1 window at 10-16 per cent glazed area, explicitly set apart from any contemporary classical house, refuse Palladio's opening rectangle for this style, or does the record's own insistence that the sash windows and construction are Regency keep the pack — and is a wo |
| `shotgun-house` | opening | `creole-cottage-vernacular` | Does a type whose openings are governed by alignment and stack ventilation take its door and window rectangles from the Palladian canon, or should entry_door, secondary_door and window_head_wood stand undimensioned until a vernacular opening pack exists? |
| `spanish-colonial-american` | opening | `italian-renaissance` | Does spanish-colonial-american take its head datum, sill count, transom/sidelight sizing and secondary-door graduation from a Palladian aperture system, or do those four slots go undimensioned until the mass-wall opening pack this node's own binding note already calls a genuine absence actually exis |
| `spanish-plateresque` | opening | `italian-renaissance` | Does 'the plain wall around it has no proportional system at all' refuse a Palladian head datum and sill for this style's windows, or only refuse regulating where those windows are placed — and if it refuses, what dimensions the four slots instead? |
| `tuscan-vernacular` | opening | `roman-classical` | Does a mezzadria farmhouse whose openings are cut by internal need through a half-metre rubble wall take its head datum, sill heights, secondary-door graduation and sidelight/Venetian-window dimensions from Palladio's opening system, or should those six slots be left with no dimensioning at all? |

## `storey-graduation` ⚡ — 21 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `arts-and-crafts-american` | massing | `english-georgian` | Does "the system is dimensional rather than ratio-based" refuse the storey diminution itself, or only the twelfth-part module that derives it — given that "at the principal floor" concedes the principal storey is distinguished, and that endorsing arms a storey-to-storey ratio check every plan of thi |
| `arts-and-crafts-british` | massing | `english-georgian` | Does an Arts and Crafts house, whose upper storey is compressed by an eave brought below first-floor head height rather than by any rank between floors, take a storey-graduation ratio -- and can this pack be declined at all while an ancestor's kit binding still names it on height_proportion? |
| `cotswold-cottage-revival` | massing | `english-georgian` | Does a one-and-a-half-storey picturesque cottage whose record says nothing about storey-to-storey ratio owe the Georgian graduation rule, and should graduation_check be armed against its plans? |
| `craftsman` | massing | `english-georgian` | Does a style of one or one and a half storeys, dimensioned in absolute lengths off a single wall plate, fall under a graduated-stack pack, given that endorsing arms build/structure.py's graduation_check -- called from build_section, so every Craftsman plan gains the finding and can now fail it? |
| ↺ `dogtrot-vernacular` | massing | `english-georgian` | Quote is VERBATIM (checker prints VERBATIM; it is proportional_system.typical_ratios[3]), but the judgment is wrong and the quote does not bear on the pack's mechanism. The pack's own notes say its subject is the RELATION between storeys in a stack -- sills constant, heads following the storey, uppe |
| `egyptian-revival` | massing | `greek-revival-american` | Does a style whose own record says it is almost never a house take a rule the pack itself calls a house rule, when endorsing arms graduation_check on every plan of the style and declining leaves stair_type with no dimensioning at all? |
| ↺ `english-baroque` | massing | `palladian` | Quote is VERBATIM (checker prints VERBATIM) and the field path is right: distinguished_from[1].node == "english-georgian". The reason's supporting argument also checks out — c03 pins glazing bars "not thinner than 25 mm", the keyed segmental head is a diagnostic tell, and the giant order is defining |
| `french-eclectic` | massing | `beaux-arts-american` | Does a roof-dominant style whose record never mentions storey height take the graduated stack as its section rule -- knowing that endorsing arms graduation_check for every French Eclectic plan? |
| `french-normandy-revival` | massing | `beaux-arts-american` | Does a picturesque roof-dominant Norman revival, whose record states no storey-to-storey ratio at all, want graduated storey heights checked on every plan — or is the equal-stack negative case simply not a claim this style makes? |
| `german-pennsylvania-colonial` | massing | `english-georgian` | Should a house that composes its elevation from its rooms be held to a Georgian storey-over-storey height diminution at all -- and is this record's silence on storey heights enough to arm graduation_check on every plan of the style? |
| `gothic-revival-american` | massing | `english-georgian` | Does American Gothic Revival take the Anglo-American storey-diminution rule -- as its parent gothic-revival-british and its child carpenter-gothic already are endorsed to -- when its own record fixes no floor-to-floor heights and its elevation is generated by rooms rather than by a storey line, and  |
| `jacobethan-revival` | massing | `english-georgian` | Does a style whose vertical regulator is stated to be the gable parapet profile, and whose principal windows are continuous mullioned and transomed walls of glass rather than punched openings, make a storey-diminution claim firm enough to arm graduation_check on every plan of the style? |
| `mediterranean-revival` | massing | `italian-renaissance-revival` | Is "upper-storey openings are fewer and smaller than lower" an affirmation of storey-height graduation, sufficient to arm `graduation_check` (build/structure.py, via build_section) on every Mediterranean Revival plan, when the node attributes the smaller upper openings to wall mass rather than to a  |
| `modern-farmhouse-traditional` | massing | `colonial-revival` | Is a stated 9-to-10-foot ground plate with no upper-storey figure anywhere in the record enough to affirm a graduated section for this style, given that endorsing arms build/structure.py::graduation_check and every Modern Farmhouse plan thereafter gains a storey-ratio finding it can fail? |
| `neo-eclectic` | massing | `colonial-revival` | Does 'the 8- or 9-foot plate' as a named module amount to the node declaring an ungraduated stack — which would be a contradiction of this pack — or is the node simply silent on storey-to-storey ratio, and should graduation_check be armed for a style whose own record disclaims an operative proportio |
| `queen-anne-american` | massing | `english-georgian` | Does this node's lightening-upward reading of the wall, which the record makes about texture and ornament only, extend to the floor-to-floor diminution storey-graduation writes into chair_rail, height_proportion and window_sill -- enough to arm graduation_check for every Queen Anne plan? |
| `queen-anne-free-classic` | massing | `english-georgian` | Does a free classic Queen Anne of 1890-1918 -- a picturesque body that bought classical trim from a millwork catalogue -- graduate its storeys the way its Georgian ancestor does, when the node's own record is silent on storey heights and the pack currently governs its chair_rail, height_proportion a |
| `queen-anne-spindled` | massing | `english-georgian` | Two things need ruling together: whether the American Queen Anne's graduated storeys should be affirmed for this node when its own record is silent on storey heights and endorsing arms a check that can fail every plan of the style; and whether a decline would even take effect here, since --impact re |
| `rural-gothic-villa` | massing | `english-georgian` | Does a style that explicitly permits window heads and sills to differ on one elevation still take storey-graduation for its SECTION -- the diminishing storey its own record neither states nor denies -- or does losing the pack's stated visible mechanism refuse the pack entire? |
| `stick-style` | massing | `english-georgian` | Does a Stick Style stack graduate -- is the second storey shorter than the first, with the stick band at each floor line following it -- or does the stick grid leave storey heights to the plan, and if this pack is declined must the baked storey-graduation entries in the inherited chair_rail, height_ |
| `storybook-style` | massing | `english-georgian` | Does the record's refusal of a facade datum refuse a pack whose subject is the storey-height ratio and whose delivery here is chair_rail and height_proportion, given that a decline is measured to change no dimension at all? |

## `sash-light` — 11 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `andalusian-spanish-revival` | opening | `richardsonian-romanesque` | Should window_type on this node keep coming from the Anglo-American glass-supply sequence, or does the corpus owe the Spanish branch a casement-and-reja window vocabulary before sash-light can be declined without stranding the slot? |
| `appalachian-log-house` | opening | `german-pennsylvania-colonial` | Does this node's own `proportion_packs` note, which names sash-light and calls binding it actively wrong on the strength of log-module's `window_surround_wood` rule, amount to a decline of the pack on the three slots it actually governs here -- shutter, transom_sidelight and window_type -- or only o |
| `dogtrot-vernacular` | opening | `german-pennsylvania-colonial` | Does a Southern log (or later frame) dogtrot take its window_type and shutter from the Anglo-American glass-trade sequence, on a record that describes only doors, chimneys, the loft and the passage and never once mentions a window? |
| `log-vernacular-american` | opening | `german-pennsylvania-colonial` | Does a log pen whose record says it requires no glass nonetheless take its window type, light count and shutter dimensioning from the Anglo-American glass-trade sequence delivered by its direct Pennsylvania German ancestor -- and if not, is losing all dimensioning on `shutter` and `window_type` the  |
| `mission-revival` | opening | `richardsonian-romanesque` | Does Mission Revival carry shutters at all, and if not, should `shutter` be bound empty on this node rather than left to sash-light's leaf-width and panel-count rules arriving through richardsonian-romanesque? |
| `modern-farmhouse-traditional` | opening | `minimal-traditional` | Does a pack whose whole mechanism is the historical glasshouse's pane limit still govern a style glazed with 2010s stock aluminium and vinyl units -- and if it does, should it keep governing `shutter` on a style that states it carries no shutters, given that declining strands both `shutter` and `win |
| `new-jersey-dutch-gambrel` | opening | `dutch-colonial-american` | Does a Dutch-tradition Bergen sandstone house take its sash type, light pattern, shutters and transom from the Anglo-American glass-supply sequence, or does the Dutch/Flemish glazing tradition -- casements and leaded quarries before the sash arrives -- need its own authority for this node's early fl |
| `pennsylvania-bank-house` | opening | `german-pennsylvania-colonial` | Are this variant's small irregular openings glazed as sash, in which case sash-light's stile, shutter and sidelight arithmetic governs them, or as the earlier Germanic casements, for which none of the three rules applies? |
| `pueblo-revival` | opening | `richardsonian-romanesque` | Does a style built and glazed 1908-1950, whose openings are sized by wall mass and a timber lintel rather than by joinery, still take its light count from the glasshouse pane sequence like any other building of those decades -- or is window kind something this style deliberately leaves unfixed? |
| `ranch-style` | opening | `minimal-traditional` | Does the node's own statement that large float glass gave it the picture window place the ranch inside sash-light's authority or name the technology that ended it -- and if the latter, what dimensions `shutter` and `window_type`, both of which lose all dimensioning on a decline? |
| `spanish-colonial-revival` | opening | `richardsonian-romanesque` | Does a twentieth-century revival that specifies multi-light double-hung sash take its light count from the pack's glass-supply arithmetic, or is multi-light here an archaism chosen for style, which the pack expressly says light count never is? |

## `facade-gable` — 9 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `arts-and-crafts-british` | secondary | `gothic-revival-british` | Does 'no shaped gable' refuse the whole of facade-gable on this node, when the only rule reaching it is the Cotswold kneeler for a roof-end gable -- a detail this node's own Cotswold descent supports -- and a decline leaves cornice_return with no dimensioning at all? |
| `california-bungalow` | secondary | `gothic-revival-british` | Should a node whose gable is stated as the end of a roof with an exposed truss take a gable-geometry pack whose dimensioned cases are largely parapet and screen gables, when the node's own Mission hybrid note admits a shaped parapet on the common Los Angeles product? |
| `carpenter-gothic` | secondary | `gothic-revival-british` | Does a bargeboarded softwood rake take facade-gable's geometry half -- apex ratio, gable count, hierarchy, dormer-as-gable -- while its stone kneeler, coping and apex assembly is refused, or is the whole pack a masonry pack that should not reach a plank-built cottage at all? |
| `german-pennsylvania-colonial` | facade | `flemish-vernacular` | Should a plain Pennsylvania German masonry gable -- a roof end with no parapet or coping anywhere in its record -- take facade-gable's kneeler as its cornice_return, or should that slot stand undimensioned until a pack for the plain masonry verge exists? |
| `hudson-valley-dutch` | facade | `dutch-urban-gable-house` | Does the Hudson Valley stone gable's rake take facade-gable's stone kneeler-and-coping, or does the mouse-tooth vlechtingen tumbling the node names for its Kingston and Albany town houses replace it — and if the pack is right only for the urban brick front, should it be endorsed for the townhouse-ro |
| `pennsylvania-bank-house` | facade | `flemish-vernacular` | Does a Pennsylvania bank house's gable end carry a coped, kneelered verge that cornice_return can be dimensioned from, or does the roof oversail a plain stone gable -- and if the latter, what dimensions cornice_return instead? |
| `queen-anne-american` | secondary | `gothic-revival-british` | Should a masonry parapet and crow-step gable pack reach a balloon-framed American Queen Anne whose only stated gable treatment is a shingle-filled roof end, given that the node's stated 9:12-14:12 pitch puts its apex ratio below the pack's own 0.55-1.05 band? |
| `queen-anne-spindled` | secondary | `gothic-revival-british` | Does a wooden cross-gable filled with cut shingles count as a roof end for facade-gable's purposes, making its height-to-width and gable-count rules applicable while its masonry members stay simply inert -- or is a masonry-derived gable pack the wrong authority for a shingled timber gable regardless |
| `stick-style` | secondary | `gothic-revival-british` | Does facade-gable's material-neutral half -- the apex-height-over-width ratio, the gables-per-front count and the hierarchy rule that calls equal gable widths a builder's composition -- govern a Stick Style front whose own c05 requires gables of comparable weight, or does this pack reach the node on |

## `room-vernacular` — 9 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `arts-and-crafts-american` | room | `arts-and-crafts-british` | Does a movement whose own record abolishes the parlour still take its public/private room inequality and its service-room breadth from the Anglo-American vernacular room — arriving on the direct arts-and-crafts-british edge — and if not, is service_zone_strategy losing all dimensioning (public_priva |
| `cotswold-cottage-revival` | room | `tudor-revival` | Does a revival that reproduces the small, hearth-dominated vernacular room as a drawn effect take the vernacular pack's constraint-derived dimensions, or is the resemblance an outcome without the mechanism? |
| `craftsman` | room | `arts-and-crafts-british` | Is a servantless, centrally heated, open-plan bungalow governed by the pre-central-heating vernacular room system, when declining sends public_private_gradient to room-harmonic (english-georgian) -- the treatise pack this one exists to contradict -- and leaves service_zone_strategy with no dimension |
| `modern-farmhouse-traditional` | room | `minimal-traditional` | Does a pack whose surviving claim is the daylight-depth rule still govern the eight room slots it holds here -- ceiling_height_rule, circulation_parti, fireplace_surround, hearth_position, public_private_gradient, room_adjacency_overrides, service_zone_strategy and stair_position -- for a style whos |
| `neo-eclectic` | room | `minimal-traditional` | Does neo-eclectic's plan generator — a marketable room schedule against a cost-per-square-foot target, with the truss removing the span cap and central heating the hearth cap — refuse room-vernacular's span/hearth/daylight constraint logic, given that declining sends six of its eight slots to log-mo |
| `new-urbanist-traditional` | room | `folk-victorian` | Does a 1979-onward, code-governed house whose record is silent on interiors inherit a hall-and-parlour public/private gradient and an ell-span service zone, or should public_private_gradient fall through to room-harmonic and service_zone_strategy go undimensioned? |
| `prairie-school` | room | `arts-and-crafts-british` | Does a Prairie house take its service-zone breadth and its public/private room inequality from the Anglo-American vernacular lean-to and hall-and-parlor logic, or does an architect-designed open plan on wide-span framing need a room pack of its own — accepting that a decline leaves service_zone_stra |
| `raised-creole-plantation` | room | `french-provincial-farmhouse` | Whether the Creole four-room plan takes the Anglo vernacular room pack at all, given that the record contradicts its corridor and window rules outright while saying nothing about the room proportion the pack's own notes claim as its subject, and that a decline hands five of the eight slots to timber |
| `ranch-style` | room | `minimal-traditional` | Does a pack whose own note says two of its three constraints were removed by exactly the technologies this node is built from still govern its eight room slots on the strength of the surviving daylight rule alone -- given that declining sends five of them to log-module (swiss-chalet) and strips serv |

## `chambers-ionic` — 8 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `california-bungalow` | primary | `english-georgian` | Should a node whose only stated support is a tapered post on a rough masonry base receive a classical Ionic order at all, given that declining this authority merely hands `frieze` to another one (palladio-ionic)? |
| ↺ `cotswold-cottage-revival` | primary | `english-georgian` | The quote is verbatim (checker returns VERBATIM; styles/cotswold-cottage-revival.json:262) and it is genuinely on-subject — --pair confirms chambers-ionic's own note is Chambers's Ionic order and that it governs cornice, door_surround and frieze at this node, so this is not a name match or the sash- |
| `craftsman-bungalow` | primary | `english-georgian` | Should any classical order dimension a Craftsman bungalow's frieze at all -- since declining Chambers only hands the slot to Palladio's Ionic -- or does the exposed porch-beam frieze of this type need a rule of its own? |
| ↺ `italianate-american` | primary | `english-georgian` | The quote is verbatim (confirmed by the checker command), but the judgment is wrong on the pack's actual subject and on the node's own file. (1) chambers-ionic's own notes say the module figures are Vignola's, inherited, and that "His departures are therefore about WHICH FORM, not about how big" — t |
| ↺ `italianate-townhouse` | primary | `english-georgian` | Quote is VERBATIM (exact substring at lineage[1].note, the descends_from edge to renaissance-revival-american), but the judgment does not hold under the narrow rule. WHY NOT: the word carrying the decline, "astylar", is an adjective on the noun phrase "facade RULES", and the sentence's own predicate |
| `italianate-villa` | primary | `english-georgian` | Should a classical order govern the cornice, frieze and door surround of a bracketed sawn-wood Italianate villa at all -- and if some classical authority is to dress its incidental trim, is it Chambers's Ionic, the palladio-ionic that would replace it on a decline, or the plainest Tuscan register th |
| `jacobethan-revival` | primary | `english-georgian` | May an order overlay reaching this node only through english-georgian at cascade depth 7 govern its building-wide cornice, frieze and pilaster when the style's own governing_logic admits a classical order solely as a quotation at the entrance porch — and if an order pack must govern them, is Chamber |
| `storybook-style` | primary | `english-georgian` | Should a style whose governing logic is stated as pictorial rather than conventional decline the inherited classical order chain as a whole -- chambers-ionic and the palladio-ionic that takes door_surround and frieze the moment it does -- or is an inherited order harmless on a node that draws no col |

## `room-harmonic` — 8 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `charleston-single-house` | room | `georgian-colonial-american` | Quote is VERBATIM (exact substring of the raw file and of proportional_system.governing_logic, no normalisation needed), and it does bear on the pack's subject -- room-harmonic really does derive room length from breadth and ceiling height from the plan dimensions, so this is not the sash-light cate |
| `creole-cottage-vernacular` | room | `roman-classical` | Does a node stating a climatic and structural generator for its room size and ceiling height thereby refuse a proportional pack that generates those same two quantities, when the shape it lands on is in that pack's own list of seven and its ceiling band mostly sits inside the domestic tolerance the  |
| `egyptian-revival` | room | `greek-revival-american` | Should a style the record says never developed a domestic vocabulary inherit Palladian room proportion by default, or be left with none? |
| `french-colonial-american` | room | `roman-classical` | Does 'the room as an independent, cross-ventilated cell', with a ceiling band stated flat and climatically rather than derived from the plan, refuse the Palladian mean-derived section and the ranked enfilade -- or is the record simply silent on proportion it never used? |
| `french-eclectic` | room | `beaux-arts-american` | Does an interwar American revival with a corridor plan inherit the Beaux-Arts harmonic room, or is its interior proportion an unstated matter the corpus should leave to the architect? |
| `french-normandy-revival` | room | `beaux-arts-american` | Is a Palladian harmonic ceiling-height rule an acceptable default for an informally planned picturesque revival, or should such nodes carry no room-system pack at all? |
| `moorish-andalusian` | room | `roman-classical` | Does a tradition that sets its plan out by rotating a square -- irrational ratios, compass and straightedge, no absolute module -- nonetheless take Palladio's seven shapes and his three-mean ceiling heights, given that its own stated court band of 1:1.5 to 1:2 falls inside the pack's ratios and its  |
| ↺ `mudejar` | room | `roman-classical` | Quote is verbatim (checker returns VERBATIM; it is the second sentence of mudejar.c02's statement) and it does bear on the pack's object — the ceiling — so the failure is in the judgment, not the citation mechanics. But the quoted sentence forbids a SUSPENDED CEILING BELOW A SEPARATE ROOF, which is  |

## `trim-classical` — 8 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `egyptian-revival` | interior | `greek-revival-american` | Does c02's ban on dentils 'anywhere on the building' reach the interior trim, and if it does, is the pack's dentil-free Greek Revival family enough to satisfy it or must the whole pack go? |
| `german-pennsylvania-colonial` | interior | `english-georgian` | Does the post-1770 Anglicization -- 'the same house, wearing a different face' -- reach the interior trim family, in rooms whose 7 ft 0 in to 8 ft 6 in ceilings sit at or below trim-classical's own stated calibration floor? |
| `mediterranean-revival` | interior | `italian-renaissance-revival` | Does "window jamb splayed or returned in stucco with no applied casing" describe only the exterior reveal, or does a genuinely thick plastered wall carry the no-casing rule inside as well -- and if so, does that refuse this pack's `casing` and `window_surround_wood` rules while leaving its baseboard |
| `pennsylvania-bank-house` | interior | `english-georgian` | Does the Stube level of a Pennsylvania bank house take a classical interior trim family at all, and if it does, does the pack's own eight-foot resolution apply to a house whose storey heights are set by the cross-slope rather than by a stud length? |
| `queen-anne-british` | interior | `english-georgian` | Does a Queen Anne (British) interior take the Georgian 4:12:3 pedestal-column-entablature trim derivation as an acknowledged approximation, or should trim_family go undimensioned until an Aesthetic-movement dado-fill-frieze trim pack exists — given that declining strands trim_family with nothing whi |
| ↺ `ranch-style` | interior | `colonial-revival` | Quote is VERBATIM (styles/ranch-style.json, proportional_system.typical_ratios[3]) — that leg passes. The judgment does not. The reason's central claim, "the node states the exact ceiling the pack disowns," misreads the pack: trim-classical's eight-foot conflict is with COST, and its resolution is i |
| `richardsonian-romanesque` | interior | `beaux-arts-french` | Should a Richardsonian interior take its trim family from beaux-arts-french's inherited Vignola pedestal-column-entablature arithmetic, or should trim_family stand undimensioned until a heavy-oak-and-inglenook trim system exists to supply it? |
| `scottish-baronial` | interior | `regency` | Does 'None classical' reach the INTERIOR of a house whose own record calls it a Regency house in costume with rooms that are large, square, plastered and comfortable, or is the classical trim family the right dimensioning for a Burn-and-Bryce interior even where the elevation refuses the order? |

## `timber-bay` ⚡ — 7 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `california-bungalow` | massing | `jacobean` | The quote IS verbatim (checker returns VERBATIM, and it is genuinely at proportional_system.governing_logic), so the build would not fail on the citation. The judgment is what is wrong. (1) The reason reads bay_rhythm selectively: it quotes only the porch clause and drops the principal one, "Grouped |
| `creole-cottage-vernacular` | massing | `french-provincial-farmhouse` | Does a Louisiana colombage frame -- cypress posts with briquette-entre-poteaux or bousillage infill, cells sized by the cypress beam at 15-19 ft -- belong inside timber-bay's English box-frame authority, given that endorsing puts every plan of the style on the 20 ft hand-framed span capacity in buil |
| `folk-victorian` | massing | `american-farmhouse-vernacular` | Does a node whose record says its body follows "folk framing practice" with rooms of 12 to 16 ft inherit the English box-frame bay of 16 to 20 ft as its module -- and is that enough to arm span_check's bay-module span capacity on every Folk Victorian plan, given that the alternative on a decline is  |
| `french-colonial-american` | massing | `french-provincial-farmhouse` | Does Creole colombage -- closely set poteaux-en-terre / poteaux-sur-sol with bousillage infill -- resolve into the English 16-20 ft box-frame bay this pack dimensions, such that this style's floor spans may be taken from the bay module rather than the light-frame joist table? |
| `french-manoir` | primary | `norman-vernacular` | Does timber-bay's box-frame bay module reach the stone logis of a manoir at all -- the record says the frame is inherited from norman-vernacular and that this is not a timber-framed type -- and if it does, may it set roof pitch, eave projection and stack width against this node's own hard 50-60 degr |
| `french-renaissance-chateau` | primary | `norman-vernacular` | Does a French travee -- set out at the floor framing's spacing but dividing a stone wall with no bents in it -- count as the same module timber-bay dimensions, and should endorsing it switch span capacity from the light-frame joist table to the bay module's own for every chateau plan? |
| `raised-creole-plantation` | massing | `french-provincial-farmhouse` | Does a French colonial colombage frame on Norman trusses over a masonry service storey carry the Anglo box-frame bay module at all — and if it does not, can the pack's 6 in eave rule (range 2–12 in, 'a box frame gives you no overhang for free') stand on a house whose single roof breaks pitch and run |

## `facade-medieval-english` — 6 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `cape-cod-colonial` | facade | `english-medieval-timber-frame` | Does this node's own binding note -- 'No facade-system pack is bound', reasoned on the front not being composed -- refuse a facade-system pack whose own thesis is that the front is not composed, and is stripping all dimensioning from composition_parti and gable_treatment the right price for stopping |
| `cotswold-vernacular` | facade | `english-gothic` | The pack's own notes state its subject as "THE PACK'S CLAIM IS THAT THE FACADE IS GENERATED FROM BEHIND", with a module measured principal post to principal post or vault respond to vault respond, and the node affirms that principle nearly verbatim -- its bay_rhythm says openings "are placed where r |
| `english-cottage-vernacular` | facade | `english-medieval-timber-frame` | Does a record that states this pack's thesis in its own words thereby take the pack's authority -- Norman arch rises, Gothic and Norman pier ratios and a Jacobean shaped gable, reconstructed from six gentry and ecclesiastical styles -- onto a cob-and-thatch labourer's cottage that states its own nar |
| `garrison-colonial` | facade | `english-medieval-timber-frame` | Does a node whose own record states this pack's governing principle -- the front generated by post position rather than composed -- take the pack's English medieval masonry and Jacobean shaped-gable figures for `arch`, `composition_parti` and `gable_treatment`, when its own binding note says in term |
| `new-england-colonial` | facade | `english-medieval-timber-frame` | Does this node's deliberate 'no facade-system pack' exclusion -- written against facade-classical's composed elevation -- also exclude facade-medieval-english, whose whole claim is that the elevation is generated from the frame behind, which is the very thing this node's bay_rhythm asserts? |
| `saltbox-colonial` | facade | `english-medieval-timber-frame` | Does a First Period New England front whose bays are set by post positions endorse this pack's authority, or only the general proposition that the facade is a result -- given that the node's own binding note offers that same proposition as its reason for binding no facade-system pack at all? |

## `trim-craftsman` — 5 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `andalusian-spanish-revival` | interior | `mission-revival` | Does a Spanish Revival interior take its trim family from the Craftsman milled-board catalogue arriving via mission-revival, or must a Spanish/Mediterranean trim pack exist first, given that declining strips built_ins and newel_balustrade of all dimensioning and sends trim_family to trim-classical,  |
| `french-eclectic` | interior | `tudor-revival` | May the lineage cascade install trim-craftsman as this node's `interior` trim authority when the node's own record deliberately holds both trim families at `optional` and says asserting one would overstate the sources -- and if not, who dimensions built_ins and newel_balustrade? |
| `neo-eclectic` | interior | `shingle-style` | Does the node's defining_characteristic of trim in extruded polymer, vinyl or aluminum reach the INTERIOR slots this pack governs (built_ins, newel_balustrade, stair_type), or does it describe applied exterior trim only, leaving the node silent on Craftsman board carpentry? |
| `new-urbanist-traditional` | interior | `folk-victorian` | Should a code-governed New Urbanist house take its built-in and baluster dimensions from the Craftsman board module arriving through folk-victorian, or from the trim of the regional vernacular its own code names — given that the node's record says nothing whatever about interiors? |
| `spanish-colonial-revival` | interior | `mission-revival` | Does the Craftsman board-trim family carry across the mission-revival edge into Spanish Colonial Revival interiors, or must it be scoped off door_surround, newel_balustrade and stair_type, where the node states a carved or cast entrance surround with columns, wrought-iron stair rails and tiled stair |

## `facade-arcade` — 4 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `churrigueresque` | secondary | `spanish-plateresque` | Does bay_rhythm's "outside it there is none" describe only the entrance facade outside the portada frame, or the whole building — and if the whole building, how does that stand beside the same record making enclosed arcaded courts the canonical massing? |
| `italian-baroque` | facade | `italian-renaissance` | Does the Roman palazzo cortile persisting under a Baroque face -- 'the Baroque changes its face and its stair, not its skeleton' -- make facade-arcade's pier-and-span authority the right one for this style, given the record names only trabeated colonnades and the pack's own span band stops at 12 ft  |
| `monterey-revival` | secondary | `richardsonian-romanesque` | Does a Monterey Revival house have a ground-floor arcade at all, and if it does not, what should govern its arch and circulation_parti -- given that declining facade-arcade hands arch to opening-pointed, a Gothic arch pack from gothic-revival-british, and circulation_parti to timber-bay, while the n |
| `spanish-colonial-revival` | secondary | `richardsonian-romanesque` | Is the arcade an organising system for this style — the corredor as the plan's whole circulation, which is what the pack claims — or only a local element (portal, patio walk) the style may carry on its garden side while its street elevation stays blank and irregular? |

## `gibbs-doric` — 4 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `charleston-single-house` | primary | `charleston-georgian` | Quote is verbatim (confirmed), but it does not bear on the pack's subject AT THIS NODE, and the decline's stated rationale misdescribes it. gibbs-doric governs exactly one slot here, `pediment` — Gibbs's Plate XXXVIII DOORCASE construction (pediment_rise = opening_width * 0.1340, judgment: true). Th |
| ↺ `minimal-traditional` | secondary | `colonial-revival` | Quote is VERBATIM (confirmed). The judgment is not sound, on three grounds. (a) THE PACK'S BLOCKER IS QUOTED WITH ITS ESCAPE CLAUSE CUT OFF. proportions/overlays/gibbs-doric.json:435 reads in full: "If the plan governs, do not use Doric - use Gibbs's Tuscan, which has no repeating ornament and toler |
| ↺ `neo-eclectic` | secondary | `colonial-revival` | Quote is VERBATIM (checker confirms it in proportional_system.governing_logic), but the judgment does not hold and the reason's central factual claim about the pack is false. gibbs-doric governs exactly ONE slot on neo-eclectic, pediment, and that rule is `opening_width * 0.1340` — not "a size rule  |
| ↺ `ranch-style` | secondary | `colonial-revival` | Quote is VERBATIM (checker passes), but it does not bear on the pack's subject at this address, and the contradiction is not real. On ranch-style gibbs-doric governs exactly one slot, pediment, via `pediment_rise = opening_width * 0.1340` — and both the rule's authority_note and its own note say the |

## `jetty-overhang` — 4 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `dogtrot-vernacular` | secondary | `german-fachwerk` | Quote is verbatim (confirmed by the checker and by dumping constraints[3]; dogtrot-vernacular.c04 contains "Each pen is limited to 16-20 feet between notched corners" as an exact substring, no trailing period). The judgment is probably right as architecture, but it is not established by the sentence |
| `german-pennsylvania-colonial` | secondary | `german-fachwerk` | Does this style's documented but short-lived half-timbered phase inherit german-fachwerk's jetty dimensions, or is the pent eave the Pennsylvania answer at the second-floor line and the jetty a thing the tradition left in the Rhineland? |
| `new-england-colonial` | secondary | `english-medieval-timber-frame` | The pack's notes state its subject and exclude this node in the same breath: a jetty is a cantilever dimensioned by the joist that makes it, with drops that are the cut-off ends of the posts above, and `new-england-colonial` 'carries a jetty only in one example record, a two-phase Ipswich house whos |
| `saltbox-colonial` | secondary | `english-medieval-timber-frame` | Does a type that names a jettied hybrid among its exemplars and calls that hybrid common take the jetty pack's authority for the whole style, or is it the same one-example case for which the pack already excluded new-england-colonial -- and if the answer is 'only in the hybrid', is that not the bind |

## `balcony-gallery` — 3 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `octagon-house` | secondary | `italianate-american` | Is an octagon's ground-level veranda -- wrapping five or more faces at a depth its own geometry fixes uniformly, with no carrying strategy stated anywhere in the record -- one of this pack's applied decks, such that its rail, supports, ceiling and eave projection should be dimensioned from four coas |
| `second-empire` | secondary | `italianate-american` | Does the Italianate body that Second Empire takes wholesale below the curb cornice bring balcony-gallery's applied-deck system with it -- the pack italianate-american itself binds -- or do the pack's four coastal traditions make it the wrong authority for the depth, rail and floor-length windows of  |
| `shotgun-house` | secondary | `creole-cottage-vernacular` | Is the shotgun's full-width front porch -- 5-8 ft deep, on piers, roofed under or attached to the front gable -- a balcony-gallery deck in the posted-to-grade regime, or a roofed porch this pack was never built to dimension? |

## `brick-course` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `andalusian-spanish-revival` | massing | `richardsonian-romanesque` | Is this style's lime-plastered wall coursed brick underneath -- so the brick rod is its real vertical module even where no brick is visible -- or rubble and adobe masonry with no course to count? |
| ↺ `pueblo-revival` | massing | `richardsonian-romanesque` | Quote is VERBATIM (confirmed against styles/pueblo-revival.json, diagnostic_tells[3]) and the DECLINE verdict is right, but the cited sentence does not bear on this pack's subject, so the binding must not ship with it. brick-course's own module.name defines the unit as "four brick courses, each cour |

## `facade-peristyle` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `mudejar` | facade | `roman-classical` | Does a Mudejar patio or cloister arcade of brick piers under horseshoe arches take its bay from the classical intercolumniation module, and if not, what should dimension composition_parti, porch_type, steps_and_stoop, foundation_expression and window_grouping_rule -- all five of which this pack curr |
| `shotgun-house` | facade | `roman-classical` | May a node's stated governing logic -- that the street gable is proportioned by the porch -- refuse a facade pack whose module is the axial intercolumniation, when declining leaves composition_parti, porch_type and steps_and_stoop with no dimensioning at all? |

## `facade-picturesque` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `new-urbanist-traditional` | primary | `folk-victorian` | Quote is VERBATIM and sits in the field claimed (proportion_packs[0].note), and it genuinely bears on the pack's subject — the pack's notes say "In a classical front the axis does the ordering... In a picturesque front there is no axis," its module note says "a picturesque elevation has no bay - tha |
| ↺ `pueblo-revival` | facade | `spanish-colonial-revival` | The quote IS verbatim (defining_characteristics[6], checker returns VERBATIM), but it fails checks 2 and 3. BEARING: check_inheritance --pair shows the pack governs only 5 slots here -- entry_sequence, material_change_rule, porch_type, roof_form, secondary_cladding. The quoted sentence is about eave |

## `moorish-arch` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `mexican-colonial` | secondary | `spanish-plateresque` | Does the alfiz survive into New Spanish practice as the governing frame for a window surround at the Alhambra's measured projection, or is it named in this record only as imported Andalusian cargo whose Mexican descendant is a dressed chiluca surround that the Plateresque portada system governs? |
| `mexican-hacienda` | secondary | `spanish-plateresque` | Does the alfiz belong on a hacienda window when the node's record neither names nor excludes it — and is silence enough ground to leave window_surround_masonry dimensioned from Cordoba and the Alhambra? |

## `palladio-tuscan` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `churrigueresque` | primary | `italian-renaissance` | Does governing_logic's "There is no classical module" refuse order packs at MEMBER scale (balustrade, casing, crown, frieze, step riser) as well as at composition scale, given the same file says the classical apparatus is "quoted precisely" — and if it does, is the answer a decline of palladio-tusca |
| `spanish-plateresque` | primary | `italian-renaissance` | May the cascade's Palladian Tuscan overlay govern this node's entablature and balustrade members when the node's own record names Vignola as its only order authority and confines it to the patio arcade shaft? |

## `stone-course` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `english-gothic` | primary | `norman-romanesque-english` | Does english-gothic's stated inversion of the Norman mass wall -- material gathered into piers and buttresses, the wall between becoming window -- reach the domestic manor wall this corpus dimensions, refusing stone-course's rubble-field rules; or is it a claim about the ecclesiastical structure alo |
| `french-renaissance-chateau` | secondary | `french-manoir` | When a node affirms stone-course's dressed-work-against-a-plainer-field rule but denies its premise that the stone wall governs -- thin wall, unusually large croisees, the travee and the applied order doing the proportioning -- does the pack still dimension it, or does it hold only the dressings and |

## `vignola-corinthian` — 2 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `chateauesque` | primary | `french-neoclassical` | Does the node's explicit choice of vignola-composite as its order authority exclude the inherited Corinthian outright, or should Corinthian stand behind it for the order slots Composite does not carry -- `pilaster`, currently taken by an inherited chambers-ionic? |
| ↺ `french-eclectic` | secondary | `beaux-arts-american` | Quote is VERBATIM (checker script prints VERBATIM; it sits in proportion_packs[2].note, so check_pack_bindings' raw-file grep would pass). It also plainly BEARS on the pack's subject: `--pair` confirms vignola-corinthian is the order-system pack whose own notes say "THE MODILLION AND THE DENTIL BELO |

## `chambers-doric` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `charleston-georgian` | secondary | `english-georgian` | Which authority dimensions Charleston's superimposed piazza orders — the Gibbs pair the node binds and whose books its own record names as arriving through the port, or the Chambers pair english-georgian binds — given that the node requires both tiers to come from one authority and both complete pai |

## `facade-classical` ⚡ — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `egyptian-revival` | facade | `greek-revival-american` | Does a frontal, strictly bilateral A-B-A pylon front count as a composed classical elevation for facade-classical's purposes, when the pack's headline arithmetic is the five-bay march this node explicitly refuses? |

## `facade-portada` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `new-mexico-adobe` | facade | `spanish-colonial-american` | Does a New Mexico adobe front carry a portada at all — and if the record's residual-composition sentence refuses it, is handing `composition_parti` to `facade-peristyle` from roman-classical, the measured fallback, an improvement or a worse dimension? |

## `gibbs-ionic` ⚡ — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `cape-cod-revival` | primary | `colonial-revival` | Quote is VERBATIM (confirmed exact substring; constraints[4].id really is cape-cod-revival.c05), and it genuinely bears on part of the pack's subject: gibbs-ionic's own cornice note says "GIBBS GIVES TWO IONIC CORNICES AND THIS PACK ENCODES THE FIRST... Gibbs's principal Ionic cornice has modillions |

## `opening-mullioned` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `cotswold-cottage-revival` | opening | `tudor-revival` | Does an American cottage revival that groups leaded casements under one head, but dimensions its leaf in its own measured band and reserves its arch for the door, take the Tudor counted-light authority or only its appearance? |

## `opening-pointed` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `storybook-style` | opening | `gothic-revival-british` | Does 'low arched opening' in this record name the depressed four-centred arch that opening-pointed's own notes say it cannot express, and so refuse the pack for the 11 slots it governs here? |

## `timber-panel` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| ↺ `jacobean` | secondary | `tudor` | Quote is VERBATIM (defining_characteristics[2], confirmed by the checker script), so the build would pass — but the judgment is wrong and the decline should be TABLE. The pack's subject is what FILLS a timber frame: "this pack holds what fills the frame -- the panel, the studding, the timber's own s |

## `vignola-doric` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `mediterranean-revival` | secondary | `italian-renaissance-revival` | Does this node's refusal of "the modillioned overhang" extend to a Doric mutule band, or is the record simply silent on the Doric order for a style that states no portico? |

## `vignola-ionic` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `folk-victorian` | secondary | `greek-revival-american` | Has a Renaissance treatise Ionic order any standing on a node that has already elected Benjamin's 1816 Companion as its only order authority and refused a room-as-an-order interior derivation -- given that the pack governs 0 slots here, so endorsing and declining are equally free of consequence? |

## `vignola-tuscan` — 1 node(s)

| node | role | arrives from | what a ruling has to decide |
|---|---|---|---|
| `italian-villa-vernacular` | primary | `roman-classical` | Does a type that names Tuscan as its own loggia column while refusing the module and the entablature take Vignola's Tuscan for its trim, balustrade and support slots, or should the binding be scoped to the loggia arcade alone? |

## What this does not ask

It does not ask whether pack inheritance should become opt-in. That is OQ 51's second half and its
own package; this list is what the first half produced. It does not ask about the packs a node
already binds itself, nor about gaps whose pack `applies_to` already names the node — those are
endorsed and were never in the backlog.

## The one that should be ruled first

`storey-graduation` and `opening-proportion`, because they are the largest and because both are
gates: every row under them is a behavioural change waiting on a judgment, not bookkeeping. The
sweeper and its baselines exist so that whichever way they are ruled, the effect can be shown rather
than argued.


## Surfaced by this package's own declines, and NOT YET READ

**73 pairs.** These did not exist when the adjudication started. Declining a pack promotes the
next one in the chain into the role it vacated, so working the backlog creates backlog: 244 pairs
read and 114 declined produced these. They are listed separately because calling them "cases the
records do not decide" would be false — nobody has looked at them yet. A second round is the
obvious next step and will itself refill; `oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times`
asks whether that loop is the right shape at all.

- `american-farmhouse-vernacular` / `greek-doric` — secondary role, from `greek-revival-american`
- `andalusian-spanish-revival` / `vignola-corinthian` — primary role, from `french-neoclassical`
- `appalachian-log-house` / `facade-peristyle` — facade role, from `english-palladian`
- `appalachian-log-house` / `palladio-doric` — secondary role, from `italian-renaissance`
- `arts-and-crafts-american` / `chambers-doric` — secondary role, from `english-georgian`
- `arts-and-crafts-american` / `palladio-tuscan` — primary role, from `italian-renaissance`
- `arts-and-crafts-british` / `palladio-tuscan` — primary role, from `italian-renaissance`
- `california-mission-colonial` / `palladio-doric` — secondary role, from `italian-renaissance`
- `cape-cod-colonial` / `stone-course` — secondary role, from `english-cottage-vernacular`
- `cape-cod-revival` / `facade-gable` — secondary role, from `gothic-revival-british`
- `cape-dutch` / `timber-panel` — primary role, from `german-fachwerk`
- `carpenter-gothic` / `palladio-tuscan` — primary role, from `italian-renaissance`
- `craftsman` / `chambers-doric` — secondary role, from `english-georgian`
- `craftsman` / `facade-peristyle` — facade role, from `english-palladian`
- `craftsman-bungalow` / `brick-course` — massing role, from `richardsonian-romanesque`
- `craftsman-bungalow` / `chambers-doric` — secondary role, from `english-georgian`
- `dogtrot-vernacular` / `facade-gable` — facade role, from `flemish-vernacular`
- `dutch-urban-gable-house` / `timber-panel` — secondary role, from `flemish-vernacular`
- `egyptian-revival` / `benjamin-ionic` — primary role, from `federal-style`
- `egyptian-revival` / `greek-doric` — secondary role, from `greek-revival-american`
- `elizabethan` / `vignola-tuscan` — primary role, from `roman-classical`
- `folk-victorian` / `facade-classical` — facade role, from `greek-revival-american`
- `french-normandy-revival` / `vignola-corinthian` — primary role, from `french-neoclassical`
- `gothic-revival-american` / `palladio-ionic` — primary role, from `english-palladian`
- `gothic-revival-british` / `palladio-tuscan` — primary role, from `italian-renaissance`
- `greek-revival-upland-vernacular` / `facade-classical` — facade role, from `greek-revival-american`
- `greek-revival-upland-vernacular` / `greek-doric` — secondary role, from `greek-revival-american`
- `italianate-townhouse` / `facade-gable` — secondary role, from `gothic-revival-british`
- `jacobean` / `greek-doric` — primary role, from `greek-classical`
- `jacobethan-revival` / `jetty-overhang` — secondary role, from `tudor-revival`
- `jacobethan-revival` / `room-harmonic` — room role, from `english-georgian`
- `jacobethan-revival` / `trim-classical` — interior role, from `english-georgian`
- `log-vernacular-american` / `facade-peristyle` — facade role, from `english-palladian`
- `log-vernacular-american` / `palladio-corinthian` — secondary role, from `english-palladian`
- `mediterranean-revival` / `vignola-composite` — primary role, from `beaux-arts-american`
- `minimal-traditional` / `brick-course` — massing role, from `richardsonian-romanesque`
- `minimal-traditional` / `facade-picturesque` — primary role, from `shingle-style`
- `minimal-traditional` / `trim-sawn` — interior role, from `queen-anne-american`
- `mission-revival` / `storey-graduation` — massing role, from `beaux-arts-french`
- `mission-revival` / `vignola-composite` — primary role, from `beaux-arts-french`
- `mission-revival` / `vignola-ionic` — secondary role, from `french-neoclassical`
- `modern-farmhouse-traditional` / `chambers-ionic` — primary role, from `english-georgian`
- `modern-farmhouse-traditional` / `facade-gable` — secondary role, from `gothic-revival-british`
- `monterey-colonial` / `facade-arcade` — facade role, from `mexican-colonial`
- `monterey-revival` / `facade-portada` — facade role, from `spanish-colonial-revival`
- `monterey-revival` / `storey-graduation` — massing role, from `beaux-arts-french`
- `neo-eclectic` / `chambers-ionic` — primary role, from `english-georgian`
- `new-jersey-dutch-gambrel` / `timber-panel` — secondary role, from `flemish-vernacular`
- `new-mexico-adobe` / `moorish-arch` — secondary role, from `spanish-plateresque`
- `new-urbanist-traditional` / `greek-doric` — secondary role, from `greek-revival-american`
- `north-german-hall-house` / `facade-gable` — facade role, from `flemish-vernacular`
- `prairie-school` / `chambers-doric` — secondary role, from `english-georgian`
- `prairie-school` / `facade-peristyle` — facade role, from `english-palladian`
- `queen-anne-american` / `facade-peristyle` — facade role, from `english-palladian`
- `queen-anne-british` / `palladio-ionic` — primary role, from `english-palladian`
- `queen-anne-free-classic` / `facade-peristyle` — facade role, from `english-palladian`
- `queen-anne-patterned-masonry` / `facade-peristyle` — facade role, from `english-palladian`
- `queen-anne-patterned-masonry` / `trim-classical` — interior role, from `english-georgian`
- `queen-anne-spindled` / `facade-peristyle` — facade role, from `english-palladian`
- `ranch-style` / `brick-course` — massing role, from `richardsonian-romanesque`
- `ranch-style` / `chambers-ionic` — primary role, from `english-georgian`
- `richardsonian-romanesque` / `facade-classical` — facade role, from `beaux-arts-french`
- `rural-gothic-villa` / `palladio-ionic` — primary role, from `english-palladian`
- `scottish-baronial` / `palladio-tuscan` — primary role, from `italian-renaissance`
- `shingle-style` / `chambers-doric` — secondary role, from `english-georgian`
- `shingle-style` / `facade-peristyle` — facade role, from `english-palladian`
- `shotgun-house` / `vignola-tuscan` — primary role, from `roman-classical`
- `spanish-colonial-revival` / `storey-graduation` — massing role, from `beaux-arts-french`
- `spanish-colonial-revival` / `vignola-corinthian` — primary role, from `french-neoclassical`
- `stick-style` / `facade-peristyle` — facade role, from `english-palladian`
- `storybook-style` / `jetty-overhang` — secondary role, from `tudor-revival`
- `tudor` / `vignola-tuscan` — primary role, from `roman-classical`
- `tudor-revival` / `palladio-tuscan` — primary role, from `italian-renaissance`
