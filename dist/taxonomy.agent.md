# Traditional Design Language — taxonomy digest

164 nodes. Ranks: tradition > family > style > variant. `member_of` is the browsing container; `lineage` is the real graph.
Edge types: descends_from (real transmission), references (claimed ancestry, no descent), reacts_against, hybridizes_with, regional_of, revives.
Select a node id to enter its kit-of-parts directory at kits/<id>.kit.json.

## antique-classical  [family]
**Antique Classical** · 600 BC–400 · Greece, Italy, Roman Mediterranean · in: classical-mediterranean
The Greek and Roman architecture of antiquity, in which the orders were first codified and the proportional method invented.
- lineage: —

## classical-mediterranean  [tradition]
**Classical Mediterranean** · 600 BC–1900 · Greece, Italy, France · in: root
The trunk of column, entablature, and proportional order that runs from archaic Greece through Rome and the Renaissance into every classical revival since.
- lineage: —

## greek-classical  [style]
**Greek Classical** · 600 BC–100 BC · Greece, Aegean, Ionia (western Anatolia) · in: antique-classical
The first Western architecture to treat proportion as an explicit, written, transmissible system, worked out in trabeated stone at the scale of a single civic building.
- lineage: —
- tells: Doric columns stand directly on the stylobate with no base - if there is a moulded base under a Doric column, it is Roman or later, not Greek | The Doric frieze alternates triglyphs and metopes, and the triglyphs at the corner are pushed to the very edge of the frieze with the last two bays visibly contracted | The pediment is shallow: roughly 12 to 16 degrees, so the gable looks almost flat compared with any post-medieval revival | Column shafts are fluted with sharp arrises and no fillet between flutes in Doric (twenty flutes); Ionic has twenty-four flutes separated by flat fillets
- massings: courtyard-full, hall-single-cell, townhouse-row

## roman-classical  [style]
**Roman Classical** · 150 BC–330 · Italy, Mediterranean basin, Gaul · in: antique-classical
The Greek order system industrialised, freed from structure by the arch and concrete, and turned into an applied grid for articulating walls, vaults and cities across an empire.
- lineage: descends_from greek-classical
- tells: Half-columns or pilasters engaged into a wall or pier that is itself doing the structural work - the giveaway that this is Roman and not Greek | Temple standing on a podium 2 to 4 m high with steps only on the entrance front, and engaged columns down the flanks | Roman Doric and Tuscan columns have bases; Greek Doric never does | Coffered vaults and domes, and the Composite capital (Ionic volutes on a Corinthian bell), neither of which exists in Greek work
- massings: courtyard-full, courtyard-u, townhouse-row

## iberian-islamic  [family]
**Iberian Islamic** · 750–1614 · Al-Andalus, Spain · in: iberian-mediterranean
Eight centuries of Islamic building in Iberia and its continuation as Mudejar craft under Christian rule.
- lineage: —

## moorish-andalusian  [style]
**Moorish Andalusian** · 785–1492 · Spain, Portugal, North Africa · in: iberian-islamic
The architecture of eight centuries of Islamic Iberia: an inward-turned world of courtyards, water, arcades and stratified geometric surface built behind walls that give the street nothing.
- lineage: descends_from roman-classical
- tells: An arch whose curve continues below its springing line by a quarter to a third of the radius — the true horseshoe | A rectangular moulded frame (alfiz) enclosing an arch, so the arch never floats free on a wall | A hard horizontal line at 1.5-2.0 m where tile stops and carved plaster begins, on every wall in the room | Muqarnas — stalactite vaulting in plaster — filling the transition from a square room to a dome
- massings: courtyard-full, courtyard-u

## iberian-mediterranean  [tradition]
**Iberian & Mediterranean** · 800–1900 · Spain, Portugal, North Africa · in: root
The courtyard, thick wall, and tile tradition of the Iberian peninsula, carrying an Islamic inheritance into the Americas by way of Mexico.
- lineage: —

## british-isles  [tradition]
**British Isles** · 1000–1940 · England, Scotland, Wales · in: root
The insular stream that fused Norman masonry, medieval timber framing, and imported classicism into the pattern-book culture that furnished colonial America with most of its architecture.
- lineage: —

## medieval-british  [family]
**Medieval British** · 1066–1540 · England, Scotland, Wales · in: british-isles
Norman masonry, English Gothic, and the timber-framed hall — the substrate every later British style either extended or rebelled against.
- lineage: —

## norman-romanesque-english  [style]
**Norman Romanesque (English)** · 1070–1190 · England, Wales, Scotland · in: medieval-british
The masonry architecture the Conquest imposed on England: round-arched, immensely thick-walled, cut rather than assembled, and in its domestic form a defensible stone hall raised over a vaulted undercroft.
- lineage: descends_from roman-classical
- tells: A round arch and a cushion capital in the same building, with no pointed arch anywhere — the moment a pointed arch appears you are in the Transitional or in Early English Gothic | Window reveals splayed so steeply that the internal opening is two or three times the external one; the wall's thickness is legible from inside | Chevron (zigzag) cut around an arch order — an ornament essentially confined to Anglo-Norman work and its revivals | Domestic entrance at first-floor level with a blind or barred undercroft below, no ground-floor front door at all
- massings: hall-single-cell, townhouse-row

## nordic-alpine-vernacular  [family]
**Nordic & Alpine Vernacular** · 1100–1900 · Scandinavia, Switzerland, Alps · in: northern-european-vernacular
Log building and the deep-eaved chalet — timber traditions from regions with long winters, heavy snow, and abundant softwood.
- lineage: —

## english-gothic  [style]
**English Gothic** · 1180–1540 · England, Wales, Scotland · in: medieval-british
Four centuries of pointed-arched masonry in which the English worked out how to concentrate structure into piers and buttresses so that the wall between them could become window, and which in domestic use produced the open-roofed great hall.
- lineage: descends_from norman-romanesque-english
- tells: Pointed arch plus tracery plus a hood mould with carved label stops — the combination is decisive and appears nowhere else | Buttresses that step back and weather as they rise, rather than the flat pilaster strips of Norman work | In a house: an off-centre entrance leading into a passage across the low end of a tall room, with two or three service doorways in the wall opposite | Perpendicular window mullions running unbroken from sill to arch head and crossed by horizontal transoms, dividing the light into rectangular panels
- massings: h-plan-manor, hall-single-cell, courtyard-full

## germanic-vernacular  [family]
**Germanic Vernacular** · 1200–1900 · Germany, Austria, Pennsylvania · in: northern-european-vernacular
The half-timbered Fachwerk town house and the great hall-house of the north German plain, and their descendants in Pennsylvania stone.
- lineage: —

## iberian-vernacular  [family]
**Iberian Vernacular** · 1200–1900 · Andalusia, Spain, Portugal · in: iberian-mediterranean
The whitewashed courtyard house of southern Spain — thick walls, small openings, deep shade, and a patio that does the work of a room.
- lineage: —

## mediterranean-vernacular  [family]
**Mediterranean Vernacular** · 1200–1900 · Tuscany, Italy, Mediterranean basin · in: classical-mediterranean
The unwritten farmhouse and villa building of the Italian countryside, whose plain massing and tile roofs supplied the twentieth century with an entire romantic idiom.
- lineage: —

## mudejar  [style]
**Mudejar** · 1200–1550 · Spain, Portugal · in: iberian-islamic
Islamic building craft continuing under Christian and Jewish patronage in reconquered Spain — the same brick, plaster, tile and carpentry, applied to churches, synagogues and palaces for four centuries after the political power that produced it was gone.
- lineage: descends_from moorish-andalusian
- tells: Brick ornament made of whole bricks set on edge or on point — dogtooth, dentil and interlace bands — with no carved or moulded profile anywhere | A flat or shallowly pitched boarded timber ceiling with a geometric interlace of small applied timbers, in a building with a Christian plan | A square brick bell tower with the same panelled elevations on all four faces and no buttresses | An alfiz frame around a Gothic or round-headed arch — the two vocabularies stacked without any attempt to reconcile them
- massings: courtyard-full, courtyard-u, townhouse-row

## northern-european-vernacular  [tradition]
**Northern European Vernacular** · 1200–1900 · Netherlands, Belgium, Germany · in: root
The continental traditions of timber frame, steep roof, and hard climate that arrived in America with Dutch, German, French, and Scandinavian settlers.
- lineage: —

## scandinavian-log-vernacular  [style]
**Scandinavian Log Vernacular** · 1200–1900 · Norway, Sweden, Finland · in: nordic-alpine-vernacular
The corner-notched horizontal log building of the Nordic forests, in which every dimension is set by the length of a trunk and the farm is a cluster of small single-purpose buildings rather than a single house.
- lineage: —
- tells: Log ends projecting past the corner, notched and visible — the notch profile identifies the valley | A small storehouse standing on stone or timber posts with a projecting upper storey and carved gable boards | Turf growing on the roof, with a birch-bark layer visible at the eave and a log or board holding the sod at the edge | Doors and windows with a visible slip joint above the head
- massings: hall-single-cell, double-pen

## french-vernacular  [family]
**French Vernacular** · 1300–1900 · Normandy, Brittany, France · in: northern-european-vernacular
Norman half-timber, provincial stone farmhouse, and the small manoir — the source material for French Eclectic and Norman Revival in America.
- lineage: —

## english-medieval-timber-frame  [style]
**English Medieval Timber Frame** · 1350–1600 · England, Wales, Scottish Borders · in: medieval-british
The native carpentry tradition of lowland Britain, in which a jointed frame of oak carries the whole building and the wall between the timbers is merely infill.
- lineage: hybridizes_with english-gothic
- tells: Timbers of irregular section and slight curvature, wide panels in the south-east and small close studding in East Anglia — the closer the studs, the wealthier the builder, since close studding is a deliberate waste of oak | Carpenters' assembly marks (chiselled Roman numerals) at the joints, and empty peg holes where members have been reused from an earlier frame | A jetty that returns around a corner with a dragon beam set diagonally at 45 degrees — a detail that cannot be faked convincingly and is absent from all applied half-timbering | Wall panels that are not rectangles: curved braces cutting across the panel field, and quatrefoil or herringbone patterned panels in Cheshire and the Welsh Marches
- massings: h-plan-manor, hall-single-cell, hall-and-parlor, townhouse-row

## german-fachwerk  [style]
**German Fachwerk** · 1350–1750 · Germany, Alsace, Switzerland · in: germanic-vernacular
The exposed load-bearing timber frame of central Germany, in which the pattern of posts, rails and braces on the wall is not decoration but a legible diagram of how the building stands up.
- lineage: references italian-renaissance
- tells: Every infill panel framed on all four sides — if a timber runs across a panel without a joint at each end, the frame is fake | Floor beam ends visibly projecting at each storey line, with a carved sill beam running across them | Braces meeting posts at real joints (mortice-and-tenon with a visible peg), not butted | Panels of daub or brick, whitewashed or ochre, sitting proud of or flush with the timber — never behind it
- massings: townhouse-row, gable-front, hall-single-cell, linear-ell-farmhouse

## british-vernacular  [family]
**British Vernacular** · 1400–1900 · England, Wales · in: british-isles
The unselfconscious regional building of the English countryside — Cotswold limestone, thatch, cob, and brick — later mined by revivalists for a whole century of cottage imagery.
- lineage: —

## flemish-vernacular  [style]
**Flemish Vernacular** · 1400–1750 · Belgium, Netherlands, Northern France · in: low-countries-vernacular
The brick, stone-banded and timber-framed building culture of Flanders and Brabant, whose stepped gable, long-facade farmstead and enclosed square farm were the common architecture of the richest agricultural region in medieval Europe.
- lineage: hybridizes_with german-fachwerk; references italian-renaissance
- tells: Crow steps with stone or tile capping, on a gable that is genuinely the end of a roof rather than a screen in front of one | Horizontal white stone banding through red-orange brick — the 'bacon' wall | A farm reading as a closed rectangle from outside, with one arched gate and no other opening in the outer face | Pantiles (golfpannen) rather than flat tiles, and a roof that comes down to about head height over the byre side
- massings: linear-ell-farmhouse, courtyard-full, courtyard-u, townhouse-row, hall-single-cell

## french-manoir  [style]
**French Manoir** · 1400–1650 · France, Normandy, Brittany · in: french-vernacular
The fortified-then-domesticated country seat of the minor French nobility: a single-pile hall range with a projecting stair turret, standing with its chapel, dovecote, gatehouse and press inside a walled or moated cour.
- lineage: descends_from norman-vernacular; references french-renaissance-chateau
- tells: A stair tower on the inner (courtyard) face rather than the outer face, and taller than the ridge it abuts | Cross-mullioned windows with the transom well above centre, roughly two-thirds up the opening | Dormers whose bases cut through the eave line and stand on the wall below, not perched on the roof slope | A freestanding colombier — round or square, with a conical roof and a ring of flight holes — in the same enclosure
- massings: h-plan-manor, courtyard-u, linear-ell-farmhouse

## low-countries-vernacular  [family]
**Low Countries Vernacular** · 1400–1900 · Netherlands, Belgium, South Africa · in: northern-european-vernacular
Dutch and Flemish brick building — the gabled canal house, the farmhouse, and their remarkable export to the Hudson Valley and the Cape of Good Hope.
- lineage: —

## norman-vernacular  [style]
**Norman Vernacular** · 1400–1800 · France, Normandy · in: french-vernacular
The close-studded oak frame, clay-and-straw infill and steep thatched or tiled roof of the Norman bocage, produced by an apple-and-dairy economy on wet clay ground with no good building stone and a great deal of oak.
- lineage: hybridizes_with english-medieval-timber-frame
- tells: Vertical studs far closer together than structure requires, with almost no visible bracing on the front face | A stone base course carrying the whole frame clear of the ground, always visible, never hidden by planting in an authentic example | Panels that are white or ochre earth on early work, red-and-black brick chequer on later work — the two rarely mixed on one elevation | A separate pressoir or colombier standing free in the same enclosure
- massings: hall-single-cell, linear-ell-farmhouse

## north-german-hall-house  [style]
**North German Hall House** · 1400–1850 · Germany, Netherlands, Denmark · in: germanic-vernacular
A single vast three-aisled timber hall entered through a wagon door in the gable, in which people, cattle, harvest and hearth occupy one undivided smoke-filled volume.
- lineage: hybridizes_with german-fachwerk; hybridizes_with flemish-vernacular
- tells: An enormous door filling the lower half of a thatched gable, wide enough for a hay wagon | Crossed horse-head (Pferdekopfe) finials at the gable apex | A thatch eave you can touch, carried far below the internal ceiling height | A carved and dated lintel beam running the full width above the Grootdor, with the owners' names in Low German
- massings: linear-ell-farmhouse, hall-single-cell, gable-front

## tuscan-vernacular  [style]
**Tuscan Vernacular** · 1400–1900 · Tuscany, Umbria, central Italy · in: mediterranean-vernacular
The stone farmhouse of the central Italian sharecropping estate: an accretive, tower-marked, tile-roofed block housing one family and its animals on one podere, with no composed facade at all.
- lineage: descends_from roman-classical
- tells: Ground-floor openings are wide and low with segmental brick heads (cart and stall doors), while upper-floor openings are small and vertical - the two storeys have visibly different logics | A straight vertical joint in the masonry where an added cell butts the original; the roof usually steps at the same line | Openings that do not stack: a window on the upper floor sitting over solid wall below is normal here and is a hard error in any composed classical style | A tower with rows of small square pigeon holes near its top, and a projecting tile course under them
- massings: linear-ell-farmhouse, villa-tower, courtyard-u

## italian-renaissance  [style]
**Italian Renaissance** · 1420–1600 · Italy, Tuscany, Rome and Lazio · in: renaissance-classical
The deliberate reconstruction of the Roman proportional system as a written, teachable design method, applied for the first time to the private urban palace and the country villa.
- lineage: descends_from roman-classical; references greek-classical
- tells: Every window on a facade is the same size and the same distance apart, including the ones next to the door | Rustication is graded by storey - heavy channelled or rock-faced below, progressively flatter above - and stops at a string course, never mid-wall | The cornice projection is enormous relative to the wall (roughly 1/12 to 1/15 of total facade height) and has no gable behind it; the roof is invisible from the street | Round-headed arches only, springing from an impost, with the arch rise exactly half the span - no segmental, pointed or elliptical arches
- massings: courtyard-full, townhouse-row, courtyard-u

## renaissance-classical  [family]
**Renaissance Classical** · 1420–1700 · Italy · in: classical-mediterranean
The fifteenth- and sixteenth-century Italian recovery of antique proportion, and its conversion by Palladio into a transmissible design method.
- lineage: —

## italian-villa-vernacular  [style]
**Italian Villa Vernacular** · 1450–1850 · Tuscany, Lombardy, Veneto · in: mediterranean-vernacular
The Italian country house in its informal, non-treatise form: a compact rendered block with a low bracketed tile roof, an arcaded loggia and a belvedere or dovecote tower, balanced rather than symmetrical.
- lineage: descends_from tuscan-vernacular; hybridizes_with italian-renaissance
- tells: A low hipped roof with a wide bracketed eave over a plain rendered wall - the two together are near-conclusive | A square tower placed at the inner angle of an L or beside the entrance rather than on the centre line | Semicircular arches with the arch rise exactly half the span, springing from a simple impost band with no capital | Openings that align in columns but are graded in height by storey, with the top storey noticeably squarer and smaller
- massings: villa-tower, four-over-four, courtyard-u

## tudor-jacobean  [family]
**Tudor & Jacobean** · 1485–1625 · England · in: british-isles
The transitional century in which English building acquired Renaissance ornament without surrendering its medieval plan and silhouette.
- lineage: —

## spanish-classical  [family]
**Spanish Classical** · 1490–1800 · Spain, Mexico, Spanish Americas · in: iberian-mediterranean
Plateresque and Churrigueresque — Spanish Renaissance and Baroque, in which classical structure carries an ornament of unmatched density.
- lineage: —

## andalusian-courtyard-vernacular  [style]
**Andalusian Courtyard Vernacular** · 1500–1900 · Spain, Andalusia, Portugal · in: iberian-vernacular
The whitewashed, plant-filled patio house of Cordoba and Seville: a blind street wall, one controlled entry, and an entire domestic life turned inward around a court that is the household's principal room for eight months of the year.
- lineage: descends_from moorish-andalusian; descends_from roman-classical; hybridizes_with mudejar
- tells: A patio fully visible from the street through an iron gate, and completely inaccessible | Whitewash carried over every surface including the wall base, with a coloured (usually ochre or blue) skirting band 800-1000 mm high | Wrought-iron window grilles that bow outward from the wall face rather than sitting flush | Plant pots fixed to the courtyard walls in banks, at heights that require a watering cane
- massings: courtyard-full, townhouse-row, courtyard-u

## spanish-plateresque  [style]
**Spanish Plateresque** · 1500–1560 · Spain, Mexico, Spanish Americas · in: spanish-classical
A Spanish ornamental system in which Italian Renaissance detail is compressed into a bounded, altarpiece-like panel of extraordinary density set against an otherwise blank ashlar wall.
- lineage: descends_from italian-renaissance; hybridizes_with mudejar; references roman-classical
- tells: A wall that is more than half empty, with all the carving in one vertical strip around the door | Relief so deeply undercut that at midday the portada reads black | Coats of arms of a size that makes no compositional sense unless you understand they are the point | Scallop-shell niches and roundel portrait medallions used as repeating units within a register
- massings: courtyard-full, courtyard-u

## swiss-chalet  [style]
**Swiss Chalet** · 1500–1900 · Switzerland, Austria, Germany · in: nordic-alpine-vernacular
The horizontally-logged, shallow-roofed, deeply overhanging alpine farmhouse whose entire form is dictated by the length of a log, the settlement of a log wall, and the need to keep snow and water off both.
- lineage: hybridizes_with german-fachwerk
- tells: Log courses visibly continuous across the whole wall, with the corner notching exposed and projecting at the corners | Window heads with a visible gap or slip joint above the frame — the settlement allowance | Purlin ends stepping outward in a stack of three to five, each shorter than the one below, to carry the overhang | A masonry or stone ground storey under a timber upper storey, with the change of material sharp and unconcealed
- massings: gable-front, gallery-house, hall-single-cell

## tudor  [style]
**Tudor** · 1500–1558 · England, Wales · in: tudor-jacobean
The last Gothic style in England and the first secular one: red brick, four-centred arches, gatehouse courtyards and extravagant chimney stacks, with Renaissance ornament stuck on like jewellery to a suit of armour.
- lineage: descends_from english-gothic; descends_from english-medieval-timber-frame; descends_from italian-renaissance
- tells: Four-centred arch under a square label mould with carved or moulded spandrels — the single most reliable Tudor signature | Diaper patterning in dark burnt headers across a red brick field; the pattern is structural bond, not applied render, and can be read on the wall's raking sunlight | Chimney stacks with individually moulded and spiralled shafts rising from a shared moulded base — a chimney treated as sculpture | An oriel window directly over the entrance arch, corbelled out on moulded stone brackets, marking the great chamber inside
- massings: h-plan-manor, courtyard-full, hall-and-parlor

## french-renaissance-chateau  [style]
**French Renaissance Chateau** · 1515–1600 · Loire Valley, Ile-de-France, Burgundy · in: continental-baroque-neoclassical
Italian classical ornament grafted onto the steep-roofed, tower-punctuated, vertically bayed French manor, producing a half-century of unresolved and extraordinarily productive collision.
- lineage: hybridizes_with french-manoir; descends_from italian-renaissance
- tells: The roof is as tall as the wall - if the roof is subordinate, it is a later French classical building, not a Renaissance chateau | Dormers with full stone surrounds, pilasters and pediments sitting on the wall plane rather than set back on the roof slope | Classical pilasters running past a string course or dying into a moulding rather than carrying an entablature - the ornament does not know what it is holding up | Cylindrical corner turrets with conical roofs on a building that is otherwise symmetrical and undefended
- massings: courtyard-u, courtyard-full, h-plan-manor

## colonial-iberian-americas  [family]
**Colonial Iberian Americas** · 1520–1910 · Mexico, Central America, Southwest United States · in: iberian-mediterranean
Three centuries of Spanish building in the Americas, where Iberian plans met indigenous labour, adobe, and a continent of new conditions.
- lineage: —

## palladian  [style]
**Palladian** · 1540–1580 · Veneto, Vicenza, Venice · in: renaissance-classical
Andrea Palladio's synthesis of the Roman temple front with the working farm villa, generated from a plan of harmonically proportioned rooms and made globally transmissible by a single illustrated book.
- lineage: descends_from italian-renaissance; references roman-classical; hybridizes_with italian-villa-vernacular
- tells: A pediment over a house rather than over a church - the single fastest identifier | Steps up to the principal floor on the outside, with the ground storey treated as a plinth and given smaller, plainer openings | Flanking arcaded wings that are lower AND use a simpler order than the centre; if the wings match the centre in order and height, it is not Palladian | The serliana (Palladian window: arched centre light flanked by two square-headed lights on columns) used as a compositional event, not as a repeated window type
- massings: five-part-palladian, temple-front-with-wings, four-over-four

## cotswold-vernacular  [style]
**Cotswold Vernacular** · 1550–1730 · England · in: british-vernacular
A limestone building culture in which walls, roof, gutters, gateposts and field boundaries all come out of the same quarry, and a Perpendicular Gothic window detail survives in working use until the eighteenth century.
- lineage: descends_from english-gothic; descends_from tudor
- tells: Graded stone slates diminishing course by course from eaves to ridge — visible from a hundred metres and impossible to fake convincingly with a uniform slate | Wall dormers whose front face is continuous with the wall below, breaking the eaves line, rather than dormers set back on the roof slope | Kneeler stones at the base of every gable and a coping standing proud of the slates, so gables have a raised stone edge instead of a timber barge board | Ovolo-moulded stone mullions with a hood mould above, still in use on buildings of 1680 and later — a Perpendicular detail running two centuries past its own period
- massings: hall-and-parlor, h-plan-manor, townhouse-row

## dutch-urban-gable-house  [style]
**Dutch Urban Gable House** · 1550–1720 · Netherlands, Belgium, North Germany · in: low-countries-vernacular
The narrow, tall, gable-fronted brick house of the Dutch canal towns, in which an entire architecture is generated by a taxed street frontage, a swampy building ground, and the need to hoist goods into an attic warehouse.
- lineage: hybridizes_with flemish-vernacular; references italian-renaissance
- tells: Facade visibly out of plumb, leaning toward the street — never a settlement failure, always intentional | A steel or timber hoisting beam still in place under the gable peak | White or sandstone horizontal bands (speklagen) crossing dark brick, and a gable that steps or scrolls rather than raking straight | Windows that occupy well over half the front wall, in a masonry building — impossible if the front wall were bearing
- massings: townhouse-row, side-hall-double-pile, gable-front

## english-cottage-vernacular  [style]
**English Cottage Vernacular** · 1550–1840 · England, Wales · in: british-vernacular
The small house of the English labourer and husbandman: one and a half storeys of cob, rubble or timber frame under deep thatch, built low to the ground with a stack that is the largest thing in it.
- lineage: descends_from english-medieval-timber-frame; hybridizes_with cotswold-vernacular
- tells: No hard edges anywhere: rounded eaves, swept dormers, rolled hips, and wall corners visibly curved because cob will not hold a sharp arris | Eaves low enough to touch, with the upper-floor windows sitting in the roof rather than in the wall | A stack that is out of scale with the building, standing well above a low ridge, often with the front door opening directly against its side | Openings placed by internal need and never in vertical alignment between floors — the opposite of every classical rule
- massings: hall-and-parlor, hall-single-cell, saltbox, linear-ell-farmhouse

## mexican-colonial  [style]
**Mexican Colonial** · 1550–1800 · Mexico, Guatemala, Central America · in: colonial-iberian-americas
Three centuries of building in New Spain, in which Andalusian craft, Italian-derived ornament and indigenous labour and masonry tradition met a seismic, high-altitude, resource-rich continent and produced something with no European equivalent.
- lineage: descends_from spanish-plateresque; descends_from mudejar; descends_from churrigueresque; hybridizes_with andalusian-courtyard-vernacular
- tells: Dark red-brown vesicular tezontle field walls framed and trimmed in pale chiluca limestone | A church set within a large walled forecourt with a raised open-air chapel, rather than on the street line | Buttresses on a single-naved church that are visibly oversized for the vault they carry | Flat-relief carving in which the background is worked as pattern rather than left as ground (tequitqui)
- massings: courtyard-full, courtyard-u, gallery-house, townhouse-row

## elizabethan  [style]
**Elizabethan** · 1570–1603 · England, Wales · in: tudor-jacobean
The first English style to compose an entire house as a symmetrical object rather than a set of accreted ranges, spending its new wealth on glass, height and silhouette rather than on defence or ornament.
- lineage: descends_from tudor; references italian-renaissance; descends_from flemish-vernacular
- tells: More window than wall on a principal elevation, with the glazing in a regular mullion-and-transom grid — the single quickest Elizabethan identification | Strapwork cresting standing free above the parapet line, often incorporating the owner's initials or device in cut stone | Superimposed orders stacked on the entrance bay of a facade that is otherwise entirely unclassical, with the entablatures stopping abruptly at the edges of the frontispiece | Rooftop banqueting turrets and a leaded roof walk — the house is meant to be occupied on top as well as inside
- massings: h-plan-manor, courtyard-full

## continental-baroque-neoclassical  [family]
**Continental Baroque & Neoclassical** · 1600–1900 · France, Italy, Continental Europe · in: classical-mediterranean
The French-led sequence from Baroque grandeur through Neoclassical restraint to the Beaux-Arts system that trained a generation of American architects.
- lineage: —

## french-provincial-farmhouse  [style]
**French Provincial Farmhouse** · 1600–1900 · France, Provence, Brittany · in: french-vernacular
The thick-walled, shuttered, low-tiled rural house of southern and central France, whose plan and orientation are dictated by wind, sun and the storage of a crop rather than by any compositional idea.
- lineage: descends_from tuscan-vernacular; hybridizes_with norman-vernacular
- tells: A long facade of openings on one side and an almost blank wall on the other, on the same building | Genoise: two to four courses of round tile corbelled out under the eave, with no fascia, gutter or soffit board | Round canal tiles at a pitch visibly lower than any northern European roof | Shutters that are solid boarded below and louvred above, hinged directly to the masonry reveal, not to a frame
- massings: linear-ell-farmhouse, courtyard-u, hall-single-cell

## italian-baroque  [style]
**Italian Baroque** · 1600–1750 · Rome and Lazio, Piedmont, Sicily · in: renaissance-classical
The classical order retained intact while the wall it governs is bent, layered and accelerated, producing an architecture of continuous surface and controlled emotional effect.
- lineage: descends_from italian-renaissance; reacts_against palladian; references roman-classical
- tells: A facade whose plan line is curved - if you can see the wall bend, no earlier classical style will account for it | Entablature that breaks forward and back over each change of column plane rather than running as a single straight band | Giant order of two-plus storeys with a small subordinate order tucked beneath it in the same bay | Pediments split at the apex, or a segmental pediment nested inside a triangular one
- massings: courtyard-full, courtyard-u, townhouse-row

## north-american  [tradition]
**North American** · 1600–2026 · United States, Canada · in: root
Four centuries of transplanted European traditions hybridizing with new climates, new materials, new technologies, and a new social order to produce the world's most stylistically promiscuous residential architecture.
- lineage: —

## spanish-colonial-american  [style]
**Spanish Colonial American** · 1600–1821 · New Mexico, Texas, Arizona · in: american-colonial
Massive earth and rubble construction, small openings, deep shade and an inward turn to a courtyard, built at the far edge of a supply line so long that the architecture arrived stripped to its diagram.
- lineage: descends_from mexican-colonial; descends_from andalusian-courtyard-vernacular; descends_from moorish-andalusian
- tells: Wall depth visible at every reveal: the window is a tunnel, not a hole | No gable roof anywhere in the compound | The building presents a nearly blind wall to the public side and opens entirely on the court side | Ornament appears once, at the entrance, and nowhere else
- massings: courtyard-u, courtyard-full, linear-ell-farmhouse, hall-single-cell

## jacobean  [style]
**Jacobean** · 1605–1640 · England, Wales, Ireland · in: tudor-jacobean
Elizabethan composition thickened, curved and darkened under James I: shaped Dutch gables, columned porches, heavy strapwork, and interiors of carved oak and pendant plaster.
- lineage: descends_from elizabethan; descends_from flemish-vernacular; references italian-renaissance
- tells: The shaped Dutch gable — concave and convex scrolls stepping up to a pediment — repeated across a front. Elizabethan gables are straight-sided and finialled; Jacobean gables curve | A columned porch standing proud of the wall plane with a chamber above it, rather than the flat applied frontispiece of Elizabethan work | Red brick with stone dressings as the default great-house material in the lowlands, where the Elizabethan default was ashlar or coursed stone | Strapwork that has thickened into deep, fleshy, three-dimensional cartouches and pendants rather than the flat interlaced bands of the 1580s
- massings: h-plan-manor, courtyard-full

## american-colonial  [family]
**American Colonial** · 1607–1780 · United States, Canada · in: north-american
The first American architecture: four European building cultures transplanted to four different climates, each mutating within two generations.
- lineage: —

## new-mexico-adobe  [variant]
**New Mexico Adobe** · 1610–1850 · upper Rio Grande valley, New Mexico, Taos and the Sangre de Cristo foothills, Santa Fe and Chimayó · in: spanish-colonial-american
Flat-roofed mud building on the upper Rio Grande, in which Spanish plan diagrams and moulded adobe brick were laid over a Puebloan earth-building tradition six centuries older, largely by Puebloan builders.
- lineage: regional_of spanish-colonial-american; descends_from mexican-colonial
- tells: Canales projecting through the parapet — a flat roof that visibly drains through the wall | No straight lines: mud plaster over adobe produces rounded arrises, undulating planes and no true corner | Room depth constant throughout the building, because it is the length of a beam | Corner fireplace with a small arched opening, set diagonally across the corner of the room
- massings: courtyard-u, linear-ell-farmhouse, courtyard-full, hall-single-cell

## english-classical  [family]
**English Classical** · 1620–1840 · England, Scotland, Ireland · in: british-isles
Two centuries of English classicism, from Jones and Wren through the Palladian, Georgian, Adam, and Regency phases, transmitted worldwide by pattern book.
- lineage: —

## french-baroque  [style]
**French Baroque** · 1630–1715 · Ile-de-France, Paris, France · in: continental-baroque-neoclassical
The French absorption of the classical order into a national manner of flat walls, projecting rectangular pavilions, tall roofs and absolute axial control, invented for and by the seventeenth-century French state.
- lineage: descends_from french-renaissance-chateau; reacts_against italian-baroque; references italian-renaissance
- tells: Three or five distinct roof masses on one building - end pavilions and a centre, each with its own hipped or mansard roof and its own ridge | Coupled columns (pairs set half a diameter to a diameter apart) rather than evenly spaced single columns | A flat wall with a deep shadow line at the centre because the avant-corps steps forward as a block, not because the wall curves | Segmental-headed or square-headed dormers set into the lower mansard slope with full stone surrounds, evenly spaced
- massings: courtyard-u, mansard-block, five-part-palladian, townhouse-row

## new-england-colonial  [style]
**New England Colonial** · 1630–1730 · Massachusetts, Connecticut, Rhode Island · in: american-colonial
The post-medieval English timber house rebuilt in a colder country around a single enormous masonry chimney, stripped of ornament by Puritan taste and by the total absence of a leisured client.
- lineage: descends_from english-medieval-timber-frame; descends_from english-cottage-vernacular
- tells: One chimney, in the middle, and it is enormous — if the chimneys are at the gable ends you are looking at a Southern colonial or a post-1740 Georgian house | Front door opens onto a chimney stack four feet away, not into a passage | Window heads within a few inches of the eave, with no frieze band; a wide frieze means Georgian influence has arrived | Casement openings (or the ghost of them in the framing) rather than sash on anything pre-1700
- massings: hall-single-cell, hall-and-parlor, saltbox, cape-cod-massing, garrison-block

## dutch-colonial-american  [style]
**Dutch Colonial American** · 1640–1790 · Hudson Valley, New York, Long Island and Brooklyn, northern New Jersey · in: american-colonial
The building culture of New Netherland — anchor-beam framing, jambless fireplaces, and steep unbroken gables in stone and brick — which outlived Dutch rule by a century and a half and then was misremembered by its own revival.
- lineage: descends_from dutch-urban-gable-house; descends_from flemish-vernacular
- tells: A jambless fireplace, or the flat unbroken chimney breast that remains after one has been rebuilt, is decisive and occurs in no other American tradition | Exposed transverse anchor beams with wedged through-tenons projecting past the post | Wrought-iron wall anchors on a masonry gable, sometimes forming a date | Dressed and coursed stone on the entrance elevation only, with rubble on the other three
- massings: hall-and-parlor, hall-single-cell, gambrel-block

## hudson-valley-dutch  [variant]
**Hudson Valley Dutch** · 1650–1790 · Ulster County, New York, Albany and Rensselaer counties, New York, Greene and Columbia counties, New York · in: dutch-colonial-american
The one-and-a-half-storey stone house of the mid and upper Hudson: two to two-and-a-half feet of coursed limestone, a steep unbroken gable, gable-end hearths, and a plate you can touch.
- lineage: regional_of dutch-colonial-american; descends_from dutch-urban-gable-house
- tells: A flat, unbroken chimney wall in the principal room with no projecting breast — the jambless fireplace, or its ghost | Coursed ashlar on one elevation, rubble on the other three | Anchor-beam tenons projecting through the posts, visible from below | Iron anchors and date irons on the gable masonry
- massings: hall-and-parlor, hall-single-cell

## mexican-hacienda  [style]
**Mexican Hacienda** · 1650–1910 · Mexico, American Southwest, Central America · in: colonial-iberian-americas
The walled rural estate of New Spain and independent Mexico: a working precinct of casa grande, chapel, granaries and workers' quarters organised by arcaded corredores around one or more courts, sized by an economy of silver, sugar, pulque or henequen.
- lineage: descends_from mexican-colonial; hybridizes_with andalusian-courtyard-vernacular; references french-neoclassical
- tells: An arcade of more than eight identical bays running in a straight line | A tall stone or brick base band 1.2-1.8 m high under a plastered adobe wall, unrendered and clearly a different material | A twin-belfry chapel facade standing inside a walled compound rather than on a street or plaza | A monumental gateway with a carved name and coat of arms, in a wall that is otherwise entirely blank for a hundred metres
- massings: courtyard-full, gallery-house, courtyard-u

## garrison-colonial  [variant]
**Garrison Colonial** · 1660–1730 · Massachusetts, Connecticut, Rhode Island · in: new-england-colonial
A two-storey New England house whose second floor projects on a framed overhang, with carved drop pendants at the posts — an English timber-framing survival that American folklore has misread as a defensive device for three hundred years.
- lineage: regional_of new-england-colonial; descends_from english-medieval-timber-frame
- tells: A continuous shadow line across the facade at the second-floor level, with turned drops at four points | Where the overhang is hewn rather than framed, the projection is only 2–6 in — look for the shadow, then measure | Central chimney plus two full storeys plus jetty: the combination occurs nowhere else | No openings in the overhang soffit — the absence of loopholes is itself the diagnostic against the defensive story
- massings: garrison-block, hall-and-parlor, saltbox

## saltbox-colonial  [variant]
**Saltbox Colonial** · 1660–1750 · Massachusetts, Connecticut, Rhode Island · in: new-england-colonial
A two-storey New England house with a single-storey lean-to across the rear, producing an asymmetric roof whose long rear slope runs almost to the ground.
- lineage: regional_of new-england-colonial; descends_from english-medieval-timber-frame
- tells: From the gable end the roof is visibly lopsided — this is the only First Period type you can identify from a single oblique view | The rear eave is at head height while the front eave is at eighteen feet | A pitch change part-way down the rear slope means the lean-to was added; an unbroken slope means it was framed integrally | Rear windows are small, few, and set at odd heights because the ceiling is following the rafters
- massings: saltbox, hall-and-parlor

## english-baroque  [style]
**English Baroque** · 1690–1730 · England, Scotland, Ireland · in: english-classical
England's brief, heavy, self-invented Baroque: giant orders, banded rustication and sculpted skylines composed for shadow and mass, by three men who had never seen Rome.
- lineage: descends_from jacobean; descends_from palladian; hybridizes_with french-baroque; references italian-baroque; references roman-classical
- tells: A giant order running through two storeys — the single detail that Palladianism abolished after 1715, and therefore the fastest way to date a facade to before 1730 | Rustication banded across pilasters and columns as well as walls, so that the vertical members appear to be built of the same courses as the field | Keystones enlarged out of all proportion and often carried up into the string course above | Balustraded parapet with urns, concealing the roof entirely, on a building whose plan is nonetheless English and double-pile
- massings: five-part-palladian, four-over-four, courtyard-u, townhouse-row

## american-folk-vernacular  [family]
**American Folk Vernacular** · 1700–1930 · United States · in: north-american
Log, shotgun, farmhouse, and the other unstyled house types that most Americans actually lived in.
- lineage: —

## cape-cod-colonial  [variant]
**Cape Cod Colonial** · 1700–1850 · Cape Cod and the Islands, eastern Massachusetts, coastal Maine and New Hampshire · in: new-england-colonial
A one-and-a-half-storey, low-eaved, central-chimney cottage built to present as little surface as possible to the wind, and grown one bay at a time as a family could afford it.
- lineage: regional_of new-england-colonial; descends_from english-cottage-vernacular
- tells: Window heads almost touching the cornice — the single most reliable Cape tell, and the one the revival always gets wrong | A door that is not centred, with a chimney that is not centred either but in a different place | The entire house reads as roof: the wall is roughly one-third of the elevation height, the roof two-thirds | Rake trim of 4–6 in with a plain 6–12 in return at the corner, not a full modillion cornice return
- massings: cape-cod-massing, hall-and-parlor, hall-single-cell

## cape-dutch  [style]
**Cape Dutch** · 1700–1830 · South Africa, Western Cape · in: low-countries-vernacular
The whitewashed, thatched, centrally gabled homestead of the Cape winelands, produced by Dutch gable practice, Huguenot farm craft and enslaved Cape Malay and African labour meeting a Mediterranean climate at the far end of a shipping route.
- lineage: descends_from dutch-urban-gable-house; hybridizes_with french-provincial-farmhouse; hybridizes_with north-german-hall-house; references french-neoclassical
- tells: Front gable rising clear of a thatched roof, moulded in plaster and usually dated in relief | Whitewash over a wall whose corners are visibly rounded and soft — plastered earth brick, not stone | The eave of a thatch roof cut square and level over a stoep supported on plain plastered piers | Green or dark-painted shutters and joinery against uniform white — the only colour on the building
- massings: h-plan-manor, courtyard-u, linear-ell-farmhouse

## churrigueresque  [style]
**Churrigueresque** · 1700–1780 · Spain, Mexico, Spanish Americas · in: spanish-classical
The last and most extreme phase of Spanish Baroque, in which an ornamental portada built around the estipite pilaster is compressed against a plain wall until the classical orders visibly dissolve.
- lineage: descends_from spanish-plateresque; descends_from italian-baroque; hybridizes_with mudejar; references roman-classical
- tells: A pilaster that is narrower at the bottom than at the top and is visibly a stack of dissimilar blocks | A cornice that returns on itself three or four times across a single portada | Deep red-brown volcanic stone field with pale limestone ornament, in Mexican examples | Niche-pilasters — a niche with a figure cut into the body of the pilaster itself
- massings: courtyard-full, courtyard-u

## english-georgian  [style]
**English Georgian** · 1720–1800 · England, Scotland, Wales · in: english-classical
The most transmissible traditional style ever devised: a symmetrical brick or stone box of vertically aligned sash windows, graduated storey heights and a single elaborated doorcase, buildable anywhere from a printed plate by a builder who had never seen a classical building.
- lineage: descends_from english-palladian; descends_from english-baroque; descends_from dutch-urban-gable-house
- tells: Storey heights that visibly diminish upward: the first-floor window is shorter than the ground-floor window and the second-floor window shorter again. Equal window heights on all floors is the fastest way to spot a fake | Sash boxes set back at least 100 mm from the face of the brickwork, throwing a deep shadow at every opening; from 1709 in London the boxes are also concealed behind the reveal | A doorcase carrying the entire ornamental budget of the house — pilasters or columns, entablature and pediment, and after about 1760 a radiating fanlight — on a facade otherwise devoid of ornament | Gauged brick flat arches in rubbed and cut brick over the openings, with fine joints of lime putty barely a millimetre wide against the 6-10 mm joints of the field brickwork
- massings: four-over-four, townhouse-row, side-hall-double-pile, five-part-palladian

## english-georgian-townhouse  [variant]
**English Georgian Town House** · 1720–1820 · England, Scotland, Ireland · in: english-georgian
The rated, party-walled, leasehold-built terrace house whose individual facade is deliberately unremarkable so that the street wall can be magnificent.
- lineage: regional_of english-georgian; descends_from english-baroque
- tells: First-floor windows taller than ground-floor windows — the reverse of the country-house rule and the quickest way to identify an urban Georgian elevation | A parapet with no visible eaves, and dormers set back behind it so the garret is invisible from the opposite pavement | The area: a sunken open trench across the front with railings above and a bridge to the front steps, admitting light to the basement kitchen | Round cast-iron coal plates set into the pavement in front of each house, marking the vaults beneath
- massings: townhouse-row, side-hall-double-pile

## english-palladian  [style]
**English Palladian** · 1720–1760 · England, Scotland, Ireland · in: english-classical
A rule-governed classicism imported from Vicenza by book and drawing, in which a temple portico stands on a rusticated basement and every dimension in the building can in principle be justified from a published plate.
- lineage: descends_from palladian; reacts_against english-baroque; descends_from english-baroque; references roman-classical
- tells: A pedimented portico standing on a rusticated basement with an exterior stair — if the entrance is at grade, the house is Georgian rather than Palladian | Window aedicules (pediment on consoles or pilasters) on the piano nobile only, with the storeys above and below left completely plain — the vertical hierarchy of ornament is the style's signature | A Venetian window centred in a shallow projecting bay, usually under a relieving arch and often flanked by blind niches | A Diocletian half-round window in a pavilion or attic, semicircular and divided by two mullions
- massings: five-part-palladian, four-over-four, temple-front-with-wings

## french-colonial-american  [style]
**French Colonial American** · 1720–1820 · Louisiana, Mississippi Gulf Coast, Mobile, Alabama · in: american-colonial
The one colonial tradition that solved a hot wet climate from first principles: a raised floor, a deep encircling gallery, a steep hipped roof, and a plan with no corridor and no room that does not cross-ventilate.
- lineage: descends_from french-provincial-farmhouse; descends_from norman-vernacular
- tells: A visible pitch break where the main roof meets the gallery roof — the single fastest tell of the whole tradition | French doors, not windows, as the standard opening: two leaves, glazed to the floor, with exterior louvred blinds | The rear elevation shows a recessed open loggia with a small square room at each end | Roof hipped on all four sides with no gable end anywhere
- massings: creole-cottage, raised-cottage, gallery-house

## georgian-colonial-american  [style]
**Georgian Colonial American** · 1720–1780 · New England, Mid-Atlantic, Chesapeake · in: american-colonial
The first American architecture designed rather than accumulated — a symmetrical, proportioned, classically detailed box whose grammar arrived not with craftsmen but in books.
- lineage: descends_from english-georgian; descends_from english-palladian; references palladian
- tells: Five bays, door dead centre, and the same window rhythm carried around to the rear | A doorway that is plainly copied from a plate — pilasters or engaged columns carrying a pediment, or a Gibbs surround with alternating blocks | Windows shorter on the second floor than the first by roughly 15%, and shorter again in the attic | A modillion or dentil cornice with a full return across the gable end (not a clipped 'pork chop')
- massings: center-passage-single-pile, four-over-four, five-part-palladian

## german-pennsylvania-colonial  [style]
**German Pennsylvania Colonial** · 1720–1830 · southeastern Pennsylvania, Maryland piedmont, Shenandoah Valley, Virginia · in: american-colonial
The Continental stone and log house of the Palatine and Swiss migration: a three-room asymmetric plan around a central chimney serving a closed iron stove, built into a hillside wherever the ground allowed.
- lineage: descends_from german-fachwerk; descends_from north-german-hall-house; hybridizes_with scandinavian-log-vernacular; descends_from english-georgian
- tells: A pent roof band across the facade at the second-floor line, with no posts under it | Windows that do not line up floor to floor, in a house otherwise carefully built — the plan is winning the argument with the elevation | Very large squared quoin stones against smaller coursed wall stone | A door at the gable end entering the kitchen, plus a second door on the facade — two entrances of unequal status
- massings: hall-and-parlor, four-over-four, hall-single-cell

## tidewater-georgian  [variant]
**Tidewater Georgian** · 1720–1780 · Tidewater Virginia, Northern Neck and the Rappahannock, Maryland Eastern Shore · in: georgian-colonial-american
Brick laid in glazed-header Flemish bond, tall gable-end chimneys, a low hipped or gabled roof, and a plan one room deep with its service buildings pushed out into the yard as separate structures.
- lineage: regional_of georgian-colonial-american; descends_from english-palladian
- tells: Tall gable-end chimneys standing well clear of the roof, frequently paired and linked — visible from a mile away and conclusive against New England | Glazed-header Flemish bond producing a visible chequer across the front wall | Front and rear doors aligned on the passage axis, so the house can be seen straight through from the approach | A separate brick kitchen thirty to eighty feet from the house instead of a service ell
- massings: center-passage-single-pile, five-part-palladian, four-over-four, telescope-house

## log-vernacular-american  [style]
**American Log Vernacular** · 1730–1900 · Mid-Atlantic, Pennsylvania, Appalachia · in: american-folk-vernacular
Horizontal hewn-log building as the standard American frontier construction from Pennsylvania to Texas - a Northern European craft transplanted, simplified, and married to Anglo room plans, whose dimensions are set almost entirely by how long a log two people can lift.
- lineage: descends_from scandinavian-log-vernacular; descends_from german-fachwerk; descends_from german-pennsylvania-colonial
- tells: Logs hewn flat on two faces rather than left round - the mark of the historic tradition, and the fastest way to distinguish it from a twentieth-century milled-log kit | Corner notching visible at the pen ends, with log ends projecting a few inches beyond the joint | Wall length that stops abruptly at 16-20 feet and starts again as a second pen: the type never spans further | Openings cut after the wall was raised, with sawn jambs pegged to the log ends and no header over the opening
- massings: hall-single-cell, double-pen, dogtrot, i-house, hall-and-parlor

## mid-atlantic-georgian  [variant]
**Mid-Atlantic Georgian** · 1730–1790 · southeastern Pennsylvania, Delaware, New Jersey · in: georgian-colonial-american
The masonry Georgian of the Delaware Valley and the Chesapeake head: schist, limestone or brick with a moulded belt course, a pent eave on earlier work, and a shallow pedimented pavilion on the best.
- lineage: regional_of georgian-colonial-american; descends_from english-palladian
- tells: A pent roof — a floating shed band across the facade with nothing holding it up — is regionally unique and effectively conclusive | A belt course at the second-floor line, present in some form on nearly all good work | Keystoned flat brick arches over the openings, with rubbed and gauged voussoirs | Coursed ashlar on the entrance elevation and rubble on the sides, on stone houses
- massings: four-over-four, five-part-palladian, center-passage-single-pile

## new-england-georgian  [variant]
**New England Georgian** · 1730–1790 · eastern Massachusetts, coastal New Hampshire and southern Maine, Rhode Island · in: georgian-colonial-american
The Georgian grammar executed in wood by shipwrights' carpenters: clapboard or rusticated board walls, paired chimneys set inboard of the ridge, steep Northern roof pitches and the most elaborately carved doorways in colonial America.
- lineage: regional_of georgian-colonial-american; descends_from new-england-colonial
- tells: Two chimneys emerging from the roof slope well inboard of the gable ends — the single fastest discriminator against every Southern Georgian variant | A wooden wall imitating stone: scored flush boarding, sometimes with sand in the paint, and wooden quoins at the corners | Full deep cornice returns, not the clipped triangular 'pork chop' of later work | A big pedimented doorway with no fanlight
- massings: four-over-four, center-passage-single-pile, gambrel-block

## new-jersey-dutch-gambrel  [variant]
**New Jersey Dutch Gambrel** · 1730–1820 · Bergen County, New Jersey, Passaic and Hudson counties, New Jersey, Somerset and Middlesex counties, New Jersey · in: dutch-colonial-american
The Bergen County sandstone house: a low gambrel-roofed block whose lower roof slope sweeps out past the wall on a concave curve, shading the front and eventually becoming a porch.
- lineage: regional_of dutch-colonial-american; descends_from flemish-vernacular
- tells: The eave is a curve, not an angle — sight along the roof edge and the concave sweep is unmistakable | Masonry quality drops with each elevation as you walk around the house | Gambrel with no dormer at all; if there is a continuous dormer the building postdates 1890 | Red-brown stone with wide white lime joints, laid in courses of unequal height
- massings: gambrel-block, hall-and-parlor, center-passage-single-pile

## british-picturesque  [family]
**British Picturesque & Revival** · 1740–1910 · England, Scotland · in: british-isles
The deliberate composition of irregular, historically allusive buildings for visual and emotional effect — the intellectual origin of nearly all Anglo-American suburban architecture.
- lineage: —

## charleston-georgian  [variant]
**Charleston Georgian** · 1740–1790 · South Carolina Lowcountry, Georgia coast · in: georgian-colonial-american
The Georgian system as rebuilt for a subtropical port city, where the house turns its narrow end to the street and gives its long southern flank to a stacked open piazza.
- lineage: regional_of georgian-colonial-american; descends_from english-georgian; references english-palladian
- tells: A false door in the street wall or garden wall that opens onto a piazza, not into a room | Ceiling heights visibly greater than any Northern colonial house of equivalent status | Superimposed classical orders on the piazza — Tuscan or Doric below, Ionic above | Stuccoed and scored brick imitating ashlar on the principal elevation of the grandest houses
- massings: charleston-single, four-over-four, gallery-house, side-hall-double-pile

## charleston-single-house  [style]
**Charleston Single House** · 1740–1890 · Lowcountry South, Charleston peninsula, Coastal South Carolina · in: american-folk-vernacular
A house one room wide turned end-on to the street, with a multi-storey piazza down its south or west flank behind a false street door - the most thoroughly climate-determined dwelling type in Anglo-America, wearing Federal trim over a plan that is essentially a machine for moving air.
- lineage: hybridizes_with federal-style; descends_from charleston-georgian; descends_from adam-style
- tells: A door in a garden wall or screen that sits in the street facade but opens sideways onto a porch - unmistakable and unique to the type | The street elevation is a gable end two or three bays wide, with the long piazza visible in perspective down the lot | Piazza consistently on the south or west flank across a whole street, regardless of which side of the street the house is on | Near-windowless flank wall on the north or east side, tight to the property line
- massings: charleston-single

## english-georgian-country-house  [variant]
**English Georgian Country House** · 1740–1800 · England, Scotland, Ireland · in: english-georgian
The compact classical box in a park: five or seven bays, hipped roof, pedimented or slightly advanced centre, service wing pushed to one side, and a plan of resolvable rooms around a hall and stair.
- lineage: regional_of english-georgian; descends_from english-palladian
- tells: Five or seven bays with a three-bay centre advanced by a few hundred millimetres and topped by a pediment — the standard signature, and instantly distinguishable from the flat continuous front of a terrace | A service wing that is symmetrical about nothing, joined to a main block that is symmetrical about everything | Storey heights diminishing upward from the ground floor, which is the opposite of the town house's arrangement and identifies the building as rural at a glance | A Venetian window on the stair landing or in the centre of a side elevation — the one Palladian survival that persists to the end of the century
- massings: four-over-four, five-part-palladian, courtyard-u

## pennsylvania-bank-house  [variant]
**Pennsylvania Bank House** · 1740–1850 · Lancaster, Berks, Lebanon and Montgomery counties, Pennsylvania, Maryland piedmont, Shenandoah Valley, Virginia · in: german-pennsylvania-colonial
A Pennsylvania German stone house set across a hillside so that its lower storey opens at grade on the downhill side and is buried on the uphill side, giving a cool service level and two front doors at two different levels.
- lineage: regional_of german-pennsylvania-colonial; descends_from german-fachwerk
- tells: Two front doors at two different levels on two different elevations — decisive, and visible from a passing road | An arched opening at the base of the downhill wall with water running out of it | The uphill gable shows a one-and-a-half-storey house; the downhill gable shows two-and-a-half | No basement windows on the uphill side, and often no openings at all in that wall below the first floor
- massings: hall-and-parlor, four-over-four, hall-single-cell

## french-neoclassical  [style]
**French Neoclassical** · 1750–1830 · Paris, Ile-de-France, France · in: continental-baroque-neoclassical
The reduction of French classicism to geometric primary volumes, archaeologically correct detail used sparingly, and an ethic that every classical member must be justified by structure.
- lineage: descends_from french-baroque; reacts_against french-baroque; references roman-classical; references greek-classical
- tells: No visible roof: a balustrade or blocking course runs along the cornice line and the low hipped roof behind it is invisible from the ground | Column shafts unfluted, or fluted only in the upper two-thirds, and set widely apart with plain wall between | Windows cut into the wall as clean rectangles with a flat architrave, no aedicular surround, and no keystone drama | A giant portico of four or six free-standing columns applied to an otherwise entirely plain block
- massings: four-over-four, townhouse-row, courtyard-u, temple-front-with-wings

## creole-cottage-vernacular  [variant]
**Creole Cottage** · 1760–1860 · New Orleans (Vieux Carré, Faubourg Marigny, Tremé), Mississippi Gulf Coast, Mobile, Alabama · in: french-colonial-american
A one-storey four-room house with no hallway, two or four equal front doors, and a roof that either extends over a shallow gallery or projects as a bracketed abat-vent, built at the front lot line from the Gulf Coast to the bayous.
- lineage: regional_of french-colonial-american; descends_from norman-vernacular
- tells: Two front doors of identical size with no window between them, and no way to tell which is 'the' entrance | An abat-vent — a roof overhang with brackets or rods and no posts — over the sidewalk | Rear elevation showing a recessed open bay with a small square room at each end | Exterior louvred blinds on doors rather than on windows, because the openings are doors
- massings: creole-cottage, gallery-house

## adam-style  [style]
**Adam Style** · 1762–1792 · England, Scotland, Ireland · in: english-classical
A decorative revolution conducted inside the Georgian box: flattened, delicate, polychrome ornament and rooms shaped into apses, ovals and screened recesses, by an architect who designed everything down to the doorknob.
- lineage: descends_from english-georgian; descends_from english-palladian; reacts_against english-palladian; references roman-classical; references italian-renaissance
- tells: A radiating spider-web fanlight in fine lead or wrought iron over a six-panel door, far more elaborate and much thinner in section than a mid-Georgian fan | Low-relief plaster ceilings laid out as a geometric field of roundels, fans and octagons, colour-picked rather than left white — the inverse of the Palladian deep-coffered ceiling | A screen of two or four attenuated columns across the end of a room, defining a recess that is neither a separate room nor part of the main volume | Ornament repeating at small scale across every surface — the same honeysuckle in the frieze, the chair back, the fire grate and the carpet
- massings: four-over-four, townhouse-row, five-part-palladian

## raised-creole-plantation  [variant]
**Raised Creole Plantation House** · 1770–1830 · the Mississippi River parishes above and below New Orleans, Pointe Coupee and the False River, Bayou Lafourche and Bayou Teche · in: french-colonial-american
The Creole plan lifted a full storey onto a brick service floor and wrapped in a gallery eight to fourteen feet deep, with an exterior stair and a broad hipped roof that breaks pitch at the gallery.
- lineage: regional_of french-colonial-american; descends_from norman-vernacular
- tells: The column change at the gallery floor line — heavy masonry below, thin wood above — visible from any angle | An exterior stair as the only way to the principal floor | A visible pitch break in the roof where the gallery begins | Dormers set into the main roof slope rather than above the gallery
- massings: raised-cottage, gallery-house

## appalachian-log-house  [variant]
**Appalachian Log House** · 1780–1900 · Appalachia, Blue Ridge, Great Smoky Mountains · in: log-vernacular-american
The hewn-log single or double pen of the southern mountains: half-dovetail notched oak or chestnut, a stone gable-end chimney, a loft under a steep riven-shingle roof, and an expansion grammar that produced every named Upland South folk house type.
- lineage: regional_of log-vernacular-american; descends_from german-pennsylvania-colonial
- tells: Half-dovetail notching with the log ends sloping outward and downward - the southern mountain signature, distinct from the square notching of the Ozarks and the V-notch of Pennsylvania | Chimney standing entirely outside the gable wall, tapering in field stone | Eave overhang of 24-36 inches on a building with no other refinement whatever | Openings that stop at least two feet short of every corner
- massings: hall-single-cell, double-pen, dogtrot

## california-mission-colonial  [variant]
**California Mission Colonial** · 1780–1834 · coastal California from San Diego to Sonoma, the Camino Real corridor, Baja California frontier · in: spanish-colonial-american
The Franciscan mission quadrangle of Alta California: adobe walls under low half-round clay tile, arcaded corredors on square piers, and all the province's ornament spent on one church front.
- lineage: regional_of spanish-colonial-american; descends_from mexican-colonial
- tells: Square piers, not columns, under semicircular arches, with no capitals and often no imposts | The arcade faces the court and stops at the corners; the outer face of the quadrangle is largely blind | Tile roof with a shallow pitch and a very short eave — the roof reads as a lid, not as a shelter | Whitewashed plaster that visibly undulates over the adobe beneath it
- massings: courtyard-full, courtyard-u, hall-single-cell

## early-republic  [family]
**Early Republic** · 1780–1860 · United States · in: north-american
Federal, Jeffersonian, and Greek Revival — the one period when American architecture was explicitly and self-consciously ideological.
- lineage: —

## federal-style  [style]
**Federal** · 1785–1820 · New England, Mid-Atlantic, Chesapeake · in: early-republic
The classicism of the new republic: Georgian bones stripped of their Baroque weight and re-dressed in the thin, linear, attenuated ornament of Robert Adam, built in brick and clapboard from Portsmouth to Savannah between the Peace of Paris and the Missouri Compromise.
- lineage: descends_from georgian-colonial-american; descends_from adam-style; references roman-classical
- tells: At fifty feet, Federal versus Georgian is a muntin-width and cornice-depth judgement: if the sash grid looks thin and the cornice casts almost no shadow, it is Federal | Fanlight elliptical rather than semicircular, and set flush in the wall rather than under a projecting pedimented hood | A shallow curved or polygonal bay pushing out of an otherwise flat rear or garden elevation | Third-storey windows noticeably shorter than the second, giving the facade a downward graduation Georgian rarely bothers with
- massings: four-over-four, townhouse-row, side-hall-double-pile, five-part-palladian

## jeffersonian-classicism  [style]
**Jeffersonian Classicism** · 1785–1826 · Chesapeake, Virginia Piedmont, Upland South · in: early-republic
Thomas Jefferson's Roman republicanism built in Virginia brick: correct antique orders taken directly from measured plates of Rome and from Palladio as their transcriber, deliberately bypassing the English intermediary that every other American builder was still working through.
- lineage: references roman-classical; references palladian; descends_from tidewater-georgian; descends_from french-neoclassical; reacts_against english-georgian; reacts_against adam-style
- tells: A house that appears to be one storey but is demonstrably two, with small square mezzanine windows tucked directly under the cornice | Octagonal or semi-octagonal room projections in plan, visible as canted bays on the elevation | Portico entablature of correct Roman depth (roughly a fifth of column height) where a Federal house of the same date would have a thin cornice and no portico at all | Chinese-lattice roof railing or a balustrade concealing a nearly flat roof
- massings: five-part-palladian, octagon, four-over-four

## dogtrot-vernacular  [variant]
**Dogtrot** · 1790–1900 · Upland South, Appalachia, Deep South · in: log-vernacular-american
Two log pens under one continuous roof with an open, unheated passage between them - the coolest place on a Southern farm in August, and the clearest case in American building of a room whose only programme is moving air.
- lineage: regional_of log-vernacular-american; descends_from appalachian-log-house
- tells: One roof ridge running continuously over what are visibly three volumes, the middle one open | Chimneys at the two far gable ends and nothing in the middle - the widest chimney spacing of any American folk house of its size | Two front doors facing each other across the passage rather than facing the yard | In an enclosed example: a center hall with an odd floor level or an odd width, chimneys unusually far apart, and weatherboard seams where the passage walls were infilled
- massings: dogtrot, double-pen

## new-england-federal  [variant]
**New England Federal** · 1790–1825 · New England, Coastal Maine, Boston Basin · in: federal-style
The Federal style executed in white-painted clapboard and Charlestown brick by the housewrights of Boston, Salem and the Maine coast, at its best a wooden architecture pretending, very thinly, to be a masonry one.
- lineage: regional_of federal-style; descends_from new-england-georgian; descends_from adam-style
- tells: Wood imitating masonry: flat pilasters at the corners, rusticated or quoined boards, all painted white | A semicircular or elliptical entrance portico so small and slender it shelters nothing - it is a frame, not a roof | Palladian window stacked directly over the fanlight door, a New England signature the South used far less | Balustrade or captain's walk on a low hip roof, in a region whose colonial houses had steep gables and a huge central chimney
- massings: four-over-four, townhouse-row, side-hall-double-pile

## southern-federal  [variant]
**Southern Federal** · 1790–1830 · Chesapeake, Virginia Piedmont, Maryland · in: federal-style
The Federal vocabulary applied to a Southern plan discipline that had already solved for heat: brick or frame, one room deep where it can be, high-ceilinged, porched, and organised around a through-passage that works as a ventilation device.
- lineage: regional_of federal-style; descends_from tidewater-georgian; descends_from adam-style; hybridizes_with jeffersonian-classicism
- tells: Exterior-end chimney stacks standing away from the gable wall - a Southern habit New England never adopted | One-room-deep main block with a through-passage, where a Northern Federal house of the same status would be double-pile | Ceiling heights visibly taller than Northern work at the same date, readable from outside in the window-to-storey proportion | Low flanking dependencies joined by hyphens, stepping down from the main block
- massings: four-over-four, five-part-palladian, center-passage-single-pile, i-house

## regency  [style]
**Regency** · 1800–1837 · England, Scotland, Ireland · in: english-classical
Georgian construction rendered in stucco and opened to the garden: bow fronts, floor-length windows, cast-iron balconies under tented canopies, wide bracketed eaves, and Greek detail applied with a light hand.
- lineage: descends_from english-georgian; descends_from adam-style; reacts_against adam-style; references greek-classical; hybridizes_with french-neoclassical
- tells: A cast-iron balcony with an ogee-tented copper hood over a floor-length window — the single most reliable Regency signature and one that appears in no earlier style | Stucco scored with ruled joints at the ground floor and left smooth above, so that a rendered wall imitates a rusticated base under ashlar | Wide eaves projecting 450-750 mm on brackets over a shallow slate roof, where Georgian would have a parapet or a modillion cornice tight to the wall | Glazing bars of 12-18 mm, thinner than anything before, sometimes with a narrow margin light framing the main panes
- massings: townhouse-row, four-over-four, side-hall-double-pile

## greek-revival-american  [style]
**Greek Revival** · 1825–1860 · New England, Mid-Atlantic, Upstate New York · in: early-republic
The first American national style: a Greek temple, known only from measured drawings and carpenters' handbooks, pressed into service as farmhouse, bank, courthouse and plantation seat across two-thirds of a continent between 1825 and 1860.
- lineage: references greek-classical; descends_from federal-style; reacts_against federal-style; descends_from regency; reacts_against roman-classical
- tells: Small horizontal windows set into the frieze board directly under the eave: no other American style does this, and it settles the identification instantly | Greek Revival versus Colonial Revival portico at fifty feet - Greek Revival columns run the full facade height and carry a deep entablature; the Colonial Revival entry porch is one storey against a two-storey wall and has a thin cornice | Doric columns without bases, sitting directly on the porch deck; a base under a Doric column means Roman, which means Jeffersonian or a later revival | Door transom rectangular, not elliptical - the single fastest Federal/Greek Revival discriminator on a plain house
- massings: temple-front-with-wings, gable-front, side-hall-double-pile, four-over-four, i-house, townhouse-row

## american-farmhouse-vernacular  [style]
**American Farmhouse Vernacular** · 1830–1920 · New England, Mid-Atlantic, Upstate New York · in: american-folk-vernacular
The un-styled American workhorse: a gable-front-and-wing or two-storey single-pile house with minimal trim and whatever ornament the local mill happened to stock, built in enormous numbers between 1830 and 1920 and now the substrate the 'modern farmhouse' market imitates.
- lineage: descends_from greek-revival-american; descends_from log-vernacular-american; descends_from georgian-colonial-american; references gothic-revival-american
- tells: Descending ridge line across three or four attached volumes - the family's economic history in silhouette | Porch in the inside corner of the L rather than across the gable front, and facing the farm drive rather than the public road | Exactly one piece of ornament on an otherwise plain building: a jigsawn gable bracket, a pointed window, a run of turned posts | 2/2 sash after about 1870 (cheap large glass) where the same house form of 1845 would have 6/6
- massings: gable-front-and-wing, i-house, gable-front, linear-ell-farmhouse

## greek-revival-northern  [variant]
**Northern Greek Revival** · 1830–1860 · New England, Upstate New York, Western Reserve · in: greek-revival-american
The Greek Revival as a settlement architecture: white clapboard temple fronts and gable-front cottages built by New England carpenters along the Erie Canal and across the Western Reserve, at a density that makes it the default historic house of the northern countryside.
- lineage: regional_of greek-revival-american; descends_from new-england-federal
- tells: Clipped cornice returns on a gable-front white clapboard house - the cheapest possible pediment and the most common Greek Revival gesture in North America | Frieze-band windows under the eave in place of dormers | Side-hall doorway pushed to the end bay of a gable front, its asymmetry accepted because the pediment supplies the symmetry | Corner pilaster boards 10-14 inches wide where a Federal house of the same size had a 4-inch corner board
- massings: gable-front, gable-front-and-wing, temple-front-with-wings, side-hall-double-pile, townhouse-row

## greek-revival-southern-plantation  [variant]
**Southern Plantation Greek Revival** · 1830–1861 · Deep South, Gulf South, Lower Mississippi Valley · in: greek-revival-american
The colossal colonnade as a shading machine: Greek orders wrapped around a Southern single-pile plan with twelve-foot ceilings and floor-length openings, built on cotton and sugar wealth and on the labour of enslaved people between 1830 and the Civil War.
- lineage: regional_of greek-revival-american; descends_from southern-federal; hybridizes_with french-colonial-american; descends_from regency
- tells: Columns on more than one elevation - a Northern Greek Revival house never wraps its colonnade | Floor-length windows (triple-hung or jib) opening onto a gallery, unmistakable from outside by the sill line running down to the deck | Stuccoed and whitewashed brick columns rather than built-up wood staves, particularly in the Gulf | Belvedere, cupola or roof monitor over the stair, present for ventilation rather than for view
- massings: temple-front-with-wings, four-over-four, gallery-house, raised-cottage

## romantic-revivals  [family]
**Romantic Revivals** · 1830–1890 · United States · in: north-american
Gothic, Italianate, and their companions — the moment when American architecture abandoned classical symmetry for association, irregularity, and moral argument.
- lineage: —

## scottish-baronial  [style]
**Scottish Baronial** · 1830–1900 · Scotland, Northern England, Ireland · in: british-picturesque
The nineteenth-century revival of the Scottish tower house — crow-stepped gables, corbelled bartizans with conical roofs and harled or granite walls — composed picturesquely and built with entirely Victorian technology.
- lineage: descends_from regency; references french-renaissance-chateau; hybridizes_with gothic-revival-british
- tells: Crow-steps and a conical-roofed corbelled turret on the same building — the combination is diagnostic of Scotland and of nowhere else | A corbel course stepping the wall outward at the head, so the top of the building is wider than its base | Dormers rising through the eaves with carved and dated stone pediments, frequently initialled for the owner | Two plain storeys of unornamented wall below a wall head that is entirely ornament — a vertical distribution the English Gothic Revival never uses
- massings: massed-picturesque, villa-tower, h-plan-manor

## egyptian-revival  [style]
**Egyptian Revival** · 1835–1855 · United States Northeast, Mid-Atlantic, Upper South · in: romantic-revivals
A narrow, short-lived, and almost entirely institutional American style of battered walls, cavetto cornices, and lotus columns, adopted for prisons, cemeteries, medical colleges, and a handful of churches because it read as permanent, solemn, and pre-Christian.
- lineage: descends_from greek-revival-american; references roman-classical; reacts_against gothic-revival-american
- tells: Walls that lean inward as they rise: no other nineteenth-century American style batters its walls | The cornice curves outward in a concave sweep rather than stepping out in mouldings; this alone identifies the style at a hundred yards | Columns are wider at the base than a Greek Doric and shorter, typically four to five diameters, and stand in antis between battered piers rather than in a projecting portico | The building will almost certainly be a cemetery gate, a prison, a medical or scientific institution, a synagogue, or a church; a domestic Egyptian Revival is vanishingly rare
- massings: temple-front-with-wings

## greek-revival-upland-vernacular  [variant]
**Upland Vernacular Greek Revival** · 1835–1870 · Upland South, Appalachia, Tennessee Valley · in: greek-revival-american
The Greek Revival reduced to its cheapest legible signals - a heavy doorway, wide corner boards, a frieze under the eave - applied to the ordinary two-storey single-pile farmhouse of the Upland South and the Ohio Valley, frequently over a log core.
- lineage: regional_of greek-revival-american; descends_from southern-federal; hybridizes_with log-vernacular-american
- tells: A courthouse-scale doorway on a farmhouse-scale building - the surest sign of the stratum | Corner boards 10-12 inches wide with a simple capital, and no columns anywhere on the building | Two-storey, one-room-deep silhouette (I-house) with a heavy eave band - it is a facade from the road and a wall from the side | Porch posts chamfered with a lamb's-tongue stop instead of turned or classical columns
- massings: i-house, center-passage-single-pile, gable-front-and-wing, double-pen

## monterey-colonial  [variant]
**Monterey Colonial** · 1835–1850 · Monterey and the Salinas Valley, California, San Francisco Bay Area, Sonoma and Petaluma · in: spanish-colonial-american
A genuine two-culture hybrid of Mexican and early American California — Hispanic adobe walls below, New England frame carpentry above, and a two-storey cantilevered wooden balcony running the length of the facade.
- lineage: regional_of spanish-colonial-american; hybridizes_with spanish-colonial-american; hybridizes_with new-england-colonial
- tells: The balcony floats: no posts, no brackets to the ground, the deck simply projecting from the wall | Shingle, not tile, on a low hip roof over an adobe building | Sash windows in a wall two feet thick — an unmistakable collision of two building cultures at every opening | The wall plane steps back at the second floor; sight up the corner and it is obvious
- massings: gallery-house, four-over-four

## gothic-revival-british  [style]
**Gothic Revival (British)** · 1836–1885 · England, Scotland, Wales · in: british-picturesque
The moral revival of the pointed arch: a style that quoted medieval Gothic from books while descending entirely from Georgian building practice, and which invented the modern idea that construction should be visible and honest.
- lineage: references english-gothic; descends_from english-georgian; descends_from regency; reacts_against english-palladian; revives english-gothic
- tells: Banded structural polychromy — courses of red and black brick or two stones alternating — which is a High Victorian invention and appears in no medieval English building | Machine-sharp mouldings and perfectly repeated carving, against the tolerant irregularity of genuine medieval stonework | A steeply gabled asymmetrical front with a projecting buttressed porch, a bay window and an entrance placed wherever the plan required it | Clustered polygonal chimney shafts on a moulded base, taken from Tudor precedent and used at three times the frequency any Tudor house had them
- massings: massed-picturesque, cross-gable-victorian, villa-tower, h-plan-manor

## gothic-revival-american  [style]
**Gothic Revival (American)** · 1840–1870 · United States Northeast, Mid-Atlantic, Great Lakes · in: romantic-revivals
The first American style built for emotional and moral effect rather than for correctness, in which steep gables, bargeboards, and pointed windows were sawn out of pine by machine and sold as an argument about how a family should live.
- lineage: descends_from gothic-revival-british; references english-gothic; descends_from greek-revival-american; reacts_against greek-revival-american; revives english-gothic
- tells: If the roof pitch is steeper than 12:12 and the siding runs vertically, it is Gothic Revival and not Italianate, which is always low-pitched and horizontally sided | Bargeboard on the rake with no bracket under the eave: Gothic Revival. Brackets under a wide eave with no bargeboard: Italianate | A pointed window in the gable of an otherwise plain farmhouse is Carpenter Gothic, not Gothic Revival proper; look for whether the plan is irregular | Label mouldings that stop with square returns rather than continuing as a string course distinguish it from the Tudor Revival of the 1920s
- massings: gable-front-and-wing, massed-picturesque, cross-gable-victorian, i-house

## rural-gothic-villa  [variant]
**Rural Gothic Villa** · 1840–1870 · Hudson Valley, United States Northeast, Mid-Atlantic · in: gothic-revival-american
The full-dress Gothic Revival country house: an architect-composed, genuinely irregular villa of towers, oriels, clustered chimneys and unequal gables, sited to be read in silhouette against trees and sky.
- lineage: regional_of gothic-revival-american; descends_from gothic-revival-british; references english-gothic
- tells: The plan is irregular, not merely the ornament. Walk the building; if the footprint has fewer than six external corners it is a Carpenter Gothic cottage wearing villa clothes | No two gables are the same width; equal gables indicate a builder's composition | Chimneys are designed objects with expressed flues, octagonal or clustered shafts, and moulded caps | Tracery has real depth and profile, cut in stone or in thick timber, and casts a modelled shadow rather than a flat one
- massings: massed-picturesque, cross-gable-victorian, villa-tower

## carpenter-gothic  [variant]
**Carpenter Gothic** · 1845–1885 · United States Northeast, Mid-Atlantic, Midwest · in: gothic-revival-american
Gothic Revival executed entirely in sawn softwood by ordinary carpenters, in which stone tracery becomes pierced board, the buttress becomes a batten, and the whole style is reduced to a purchasable set of profiles.
- lineage: regional_of gothic-revival-american; descends_from greek-revival-american; references english-gothic
- tells: Ornament is flat. Sight along the wall: everything projects less than about two inches, because everything came off a plank | A central gable rising through the eave line of an otherwise symmetrical two-storey farmhouse is the commonest American Carpenter Gothic composition, and separates it from the irregular architect-designed villa | Pointed sash in the gable but square-headed sash everywhere else: the owner bought one Gothic window | Bargeboard patterns repeat on a short module (12 to 24 in) because they were cut from a template
- massings: gable-front-and-wing, i-house, cross-gable-victorian, gable-front

## italianate-villa  [variant]
**Italianate Villa** · 1845–1880 · United States Northeast, Mid-Atlantic, Midwest · in: italianate-american
The freestanding Italianate country house: an L-shaped, low-hipped, deeply bracketed villa with a square campanile in the inner angle and a veranda facing the view, sold as the house of a cultivated gentleman.
- lineage: regional_of italianate-american; references italian-villa-vernacular; references italian-renaissance; hybridizes_with rural-gothic-villa
- tells: Square tower in the inner angle of an L, capped by a low hipped or pyramidal roof with its own brackets: the type's signature and the fastest identification in American architecture | The tower roof is low and wide, never a spire and never a mansard; a mansarded tower makes it Second Empire | Bracket spacing continues unchanged across the tower, the main block, and the wing, at the same module | Windows are paired within a single hood or surround, giving a two-light rhythm no other style of the period uses so consistently
- massings: villa-tower, massed-picturesque

## renaissance-revival-american  [style]
**Renaissance Revival (American)** · 1846–1880 · United States Northeast, Mid-Atlantic, Midwest cities · in: romantic-revivals
The disciplined, symmetrical, astylar palazzo mode adopted for American libraries, clubs, banks, and merchant houses from the mid-1840s, in which correctness of profile replaced picturesque effect.
- lineage: references italian-renaissance; hybridizes_with italianate-american; descends_from greek-revival-american; descends_from federal-style; references roman-classical
- tells: If the cornice is carried on modillions or dentils rather than on sawn scroll brackets, it is Renaissance Revival and not Italianate | Alternating triangular and segmental window pediments in a row is a Renaissance signature and appears in no other American style of the period | The ground floor is treated differently from the floors above (rustication, larger openings, darker stone); Italianate treats all floors alike | Facade symmetry is exact. If any part of the composition is picturesquely off-balance, it is Italianate
- massings: townhouse-row, side-hall-double-pile, four-over-four

## beaux-arts-french  [style]
**Beaux-Arts (French)** · 1850–1914 · Paris, France, Europe · in: continental-baroque-neoclassical
Composition taught as a transmissible method - parti, marche and poche - producing large, richly sculptural, axially planned public buildings whose elevations are direct projections of their plans.
- lineage: descends_from french-neoclassical; descends_from french-baroque; references italian-baroque; references italian-renaissance
- tells: Coupled columns, usually of a giant order, marking a projecting central pavilion on a symmetrical front | A skyline populated with sculpture, quadrigae, cartouches and gilt attic figures above the main cornice | Deeply rusticated ground storey with heavy vermiculated or channelled blocks and segmental-arched openings | A grand exterior or interior stair treated as the principal architectural event, larger than any single room it serves
- massings: townhouse-row, mansard-block, courtyard-u, four-over-four

## italianate-american  [style]
**Italianate (American)** · 1850–1880 · United States Northeast, Mid-Atlantic, Midwest · in: romantic-revivals
The most-built American style of the mid-nineteenth century: a low-hipped, wide-eaved, heavily bracketed villa or townhouse whose round-arched windows and optional tower promised a Mediterranean life to people living through Ohio winters.
- lineage: references italian-villa-vernacular; references italian-renaissance; references tuscan-vernacular; descends_from gothic-revival-american; reacts_against greek-revival-american
- tells: Brackets under a wide eave with a low roof: Italianate. Add a mansard over the same brackets and it is Second Empire, which is the single most common misidentification | Round or segmental window heads with hoods, versus the pointed heads of Gothic Revival and the flat lintels of Greek Revival | If the tower stands in the reentrant angle of an L and rises a full storey above the main cornice, it is an Italianate villa; a tower rising from the centre of a symmetrical front is more likely Second Empire or Renaissance Revival | Cast-iron or wooden porch posts with chamfered or turned shafts and scrolled brackets at the head, never classical columns with entasis
- massings: villa-tower, townhouse-row, side-hall-double-pile, massed-picturesque

## italianate-townhouse  [variant]
**Italianate Townhouse** · 1850–1880 · New York City, Brooklyn, Philadelphia · in: italianate-american
The party-wall Italianate city house: a brownstone or brick row with a high stoop, a raised parlour floor of eleven-foot windows, arched heads with heavy hoods, and a bracketed cornice that runs continuously across the whole block.
- lineage: regional_of italianate-american; descends_from renaissance-revival-american; descends_from greek-revival-american; descends_from federal-style
- tells: Arched window heads with hoods on the parlour floor and square heads above: the storey hierarchy is the fastest identification | The cornice line is continuous across the whole row; a break in cornice height means either a later infill or a different builder | Stoop of six to ten risers with cast-iron rails and newels, and an areaway with an iron fence at the sidewalk | Compare with Greek Revival rows: flat lintels, lower stoops, and a plain fascia cornice with no brackets
- massings: townhouse-row, side-hall-double-pile

## octagon-house  [style]
**Octagon House** · 1850–1860 · United States Northeast, Hudson Valley, Midwest · in: romantic-revivals
An eight-sided house type promoted by the phrenologist Orson Squire Fowler in A Home for All (1848) on the argument that an octagon encloses more floor area per foot of wall than a rectangle, and adopted by several thousand American builders before it died of its own geometry.
- lineage: hybridizes_with italianate-american; descends_from greek-revival-american; reacts_against greek-revival-american
- tells: Eight exterior walls; there is no near-miss identification available | A cupola or belvedere at the roof apex, present in the large majority of surviving examples because the eight hips demand a termination | Wall construction is frequently lime-and-gravel concrete, board-formed in lifts, per Fowler's second thesis; look for horizontal form lines under the stucco | The ornament will date the house rather than the type, and it will almost always be Italianate bracketwork
- massings: octagon

## shotgun-house  [style]
**Shotgun House** · 1850–1930 · Gulf South, Lower Mississippi Valley, Deep South · in: american-folk-vernacular
A house one room wide and three to five rooms deep, gable and porch to the street, its doors aligned on a single axis - a New Orleans type with documented West African and Haitian plan antecedents, not an Anglo economization of a narrow lot.
- lineage: descends_from creole-cottage-vernacular; hybridizes_with french-colonial-american; references raised-creole-plantation
- tells: Sight line straight through the house from the front door to the back door - no other American type does this | Front facade of one or two openings only, a door and a window, under a gable | Porch full width and at least 5 feet deep, raised on brick or cypress piers with an open crawl beneath | Camelback profile: a house that is one storey from the street and two from the alley
- massings: shotgun

## victorian  [family]
**Victorian** · 1855–1910 · United States, Canada · in: north-american
The high era of American picturesque: Second Empire, Stick, Queen Anne, Richardsonian, Shingle, and the Folk Victorian that carried it to every small town.
- lineage: —

## british-arts-and-crafts  [family]
**British Arts and Crafts** · 1860–1915 · England · in: british-isles
The reform movement that rejected industrial ornament in favour of honest material, visible craft, and the dignity of the vernacular cottage.
- lineage: —

## second-empire  [style]
**Second Empire** · 1860–1885 · United States Northeast, Mid-Atlantic, Midwest · in: victorian
The mansard-roofed style of the 1860s and 1870s, in which an Italianate body is crowned by a full habitable storey of steep slate roof with dormers, and which was fashionable rather than revivalist because its source was contemporary Paris.
- lineage: descends_from italianate-american; references french-baroque; references french-renaissance-chateau; hybridizes_with renaissance-revival-american
- tells: If it is bracketed and arched and there is a mansard, it is Second Empire; if it is bracketed and arched and there is not, it is Italianate. There is no third possibility | The mansard runs all the way around; a mansard only on the street front is a twentieth-century commercial device, not this style | Dormer count equals bay count, and the dormers line up with the windows below | The tower, where present, has a steeper and taller mansard than the main roof, usually concave or with a distinct convex bell
- massings: mansard-block, villa-tower, townhouse-row, side-hall-double-pile

## stick-style  [style]
**Stick Style** · 1865–1885 · United States Northeast, Coastal New England, Mid-Atlantic · in: victorian
A short-lived wooden style of the 1860s and 1870s in which flat boards applied over the clapboard in horizontal, vertical, and diagonal bands claim to express the frame beneath, producing the most linear and least massive architecture America has built.
- lineage: descends_from gothic-revival-american; descends_from swiss-chalet; references english-medieval-timber-frame; hybridizes_with italianate-american
- tells: Straight lines only. If the applied woodwork curves, turns, or scrolls, the building has moved to Queen Anne or Eastlake | The stickwork is continuous and encircles the building; trim that stops at the front corner is Folk Victorian | Diagonals in the gable panels, forming a truss that carries nothing, is the single most reliable tell | Compared with Queen Anne, there is no dominant mass and no round tower; the Stick Style composition is a set of gables of comparable weight
- massings: cross-gable-victorian, massed-picturesque, gable-front-and-wing

## queen-anne-british  [style]
**Queen Anne (British)** · 1870–1900 · England, Scotland, Ireland · in: british-picturesque
The red-brick, white-painted, sunlit reaction against High Victorian Gothic: sash windows, shaped gables, tall thin chimneys and a picturesque plan, quoting an English brick vernacular that had nothing to do with Queen Anne.
- lineage: descends_from gothic-revival-british; reacts_against gothic-revival-british; references english-baroque; hybridizes_with dutch-urban-gable-house; descends_from english-cottage-vernacular
- tells: Red brick with white-painted woodwork as an absolute rule — the colour pairing is the style's fastest identification at any distance | A sash whose upper leaf is divided into six, eight or more small panes over a single-pane lower leaf: a Victorian window pretending to be a 1700 window and not quite managing it | Cut and rubbed brick sunflowers, swags and pilaster panels — the sunflower is practically the movement's trademark | Chimney stacks that are tall, thin and numerous, well out of proportion to the flues they carry, used as vertical accents in the composition
- massings: massed-picturesque, cross-gable-victorian, townhouse-row

## arts-and-crafts-british  [style]
**Arts and Crafts (British)** · 1880–1914 · England, Scotland, Wales · in: british-arts-and-crafts
A house built from the materials of its own county, planned from the inside out around a hall and a hearth, and detailed so that every visible thing is doing structural work — the last coherent traditional style in Britain, and the one that stopped quoting.
- lineage: descends_from gothic-revival-british; reacts_against gothic-revival-british; descends_from english-cottage-vernacular; descends_from cotswold-vernacular; hybridizes_with queen-anne-british
- tells: Horizontal bands of small leaded casements under one long lintel — the exact inverse of the Georgian vertical punched opening, and instantly readable at distance | Eaves brought down unusually low, often with a sweeping catslide over an entrance or an outshot, so the roof dominates the elevation | Battered (sloping) buttresses and chimney bases, with roughcast render carried over them in one continuous white or cream surface — the Voysey signature | A chimney stack that is the largest single element of the composition and is placed where the fire is, not where the elevation wants it
- massings: massed-picturesque, linear-ell-farmhouse, h-plan-manor

## chateauesque  [style]
**Chateauesque** · 1880–1910 · United States, Canada · in: eclectic-revivals
The briefest and most expensive American revival: a full-scale reconstruction of the sixteenth-century Loire chateau in load-bearing cut stone, built for perhaps two hundred families between 1880 and 1910 and effectively impossible thereafter.
- lineage: references french-renaissance-chateau; references english-gothic; descends_from beaux-arts-french; descends_from richardsonian-romanesque; descends_from second-empire; revives french-renaissance-chateau
- tells: If the dormers stop at the eave rather than cutting through it, it is not Chateauesque; the through-cornice wall dormer is the style's signature move. | Stone is load-bearing and coursed with joints under 3/8 in.; any veneered or cast-stone wall places the building in a later, cheaper style borrowing the imagery. | The roof is taller than the top storey it covers. A Second Empire mansard is flat-topped and boxy; the Chateauesque roof is a steep hip or a set of steep hips that come to ridges and points. | Ornament is late Gothic in vocabulary - crockets, finials, tracery - but the openings underneath are Renaissance and round-arched. That specific collision dates the reference to about 1520.
- massings: massed-picturesque, h-plan-manor

## colonial-revival  [style]
**Colonial Revival** · 1880–1955 · United States, Canada · in: eclectic-revivals
The first and longest-running American revival, in which Beaux-Arts-trained offices and millwork catalogs recomposed a half-remembered Georgian and Federal vocabulary into houses larger, looser, and more emphatic than anything the colonies ever built.
- lineage: revives georgian-colonial-american; references new-england-colonial; references federal-style; descends_from shingle-style; descends_from queen-anne-free-classic; descends_from beaux-arts-french; reacts_against queen-anne-american
- tells: The entrance is the largest well-made element on the facade. On a genuine Georgian house it is among the smallest. | Sash runs 6/6, 8/8, or 6/1 with muntins 7/8 in. or wider in flat, uniform glass; eighteenth-century sash runs 9/9 or 12/12 with muntins nearer 5/8 in. and visibly irregular glass. | Cornice returns are short decorative stubs applied to the gable end rather than the full eaves carried around a framed roof. | Shutters are roughly half the width they would need to be to close, and are screwed flat to the siding without pintles or holdbacks.
- massings: four-over-four, side-hall-double-pile, foursquare, gambrel-block

## eclectic-revivals  [family]
**Eclectic Revivals** · 1880–1945 · United States · in: north-american
The period-revival era, in which professionally trained architects reproduced historical styles with increasing archaeological accuracy — and gave American suburbia its permanent vocabulary.
- lineage: —

## folk-victorian  [style]
**Folk Victorian** · 1880–1910 · United States nationwide, Deep South, Midwest · in: victorian
The ordinary American folk house of the late nineteenth century wearing factory-made Victorian ornament, in which a plain gable-front-and-wing, I-house, or pyramidal cottage receives a spindled porch, sawn brackets, and a decorated gable ordered from a catalogue and delivered by rail.
- lineage: descends_from american-farmhouse-vernacular; descends_from queen-anne-american; descends_from italianate-american; descends_from gothic-revival-american
- tells: Simple massing plus fancy porch is the whole diagnosis: if you can describe the footprint in one sentence and the porch takes three, it is Folk Victorian | The ornament stops where the porch stops; walk to the side elevation and it is a plain farmhouse | Roof pitch and plan are those of the local vernacular of thirty years earlier, not of any fashionable style | Compared with Queen Anne: no tower, no bay above the first floor, no texture change, no wall projection, and the ridge is a simple rectangle or L
- massings: gable-front-and-wing, i-house, gable-front, pyramidal-cottage

## queen-anne-american  [style]
**Queen Anne (American)** · 1880–1900 · United States nationwide, San Francisco Bay Area, Pacific Northwest · in: victorian
The dominant American house style of the 1880s and 1890s: an irregular, multi-textured, tower-bearing composition around one dominant mass, wrapped in porches and covered in machine-made ornament shipped by rail.
- lineage: descends_from queen-anne-british; descends_from stick-style; references colonial-revival; reacts_against second-empire; descends_from georgian-colonial-american
- tells: Round or polygonal corner tower with a conical or bell roof: the single fastest identification, though many Queen Annes have none | Cut shingles in fish-scale or diamond patterning filling a gable above clapboarded walls | Wraparound porch turning a corner, often widening into a round porch pavilion at the corner itself | Compared with Stick Style: curves are present. Turned posts, spindles, round towers, and arched porch openings all say Queen Anne
- massings: cross-gable-victorian, massed-picturesque, villa-tower, townhouse-row

## queen-anne-patterned-masonry  [variant]
**Queen Anne, Patterned Masonry** · 1880–1900 · Baltimore, Philadelphia, Boston · in: queen-anne-american
The urban masonry Queen Anne, in which the multi-texture rule of the parent style is satisfied by brick of contrasting colours, moulded and rubbed brickwork, terra cotta panels, and stone trim rather than by clapboard and cut shingle.
- lineage: regional_of queen-anne-american; descends_from queen-anne-british; hybridizes_with richardsonian-romanesque
- tells: Terra cotta or moulded brick panels set into a brick field, often with sunflower, foliate, or geometric motifs: the clearest single tell | Two brick colours in a designed relationship rather than in a repair patch, with the change on a horizontal line | Corbelled chimney caps projecting several inches and stacks carried high above the ridge | Compared with Richardsonian Romanesque: the wall is articulated into zones with belt courses and the arches are segmental or flat rather than full semicircles, and there is far more opening area
- massings: cross-gable-victorian, townhouse-row, massed-picturesque

## queen-anne-spindled  [variant]
**Queen Anne, Spindlework** · 1880–1900 · United States nationwide, San Francisco Bay Area, Pacific Northwest · in: queen-anne-american
The lathe-turned expression of the American Queen Anne, in which porches carry turned posts, spindle friezes, and pierced valances, and gables are filled with cut-shingle patterning, all of it purchased ready-made.
- lineage: regional_of queen-anne-american; descends_from stick-style; descends_from italianate-american
- tells: The spindle frieze is the single tell. No other American subtype hangs a band of turned members beneath the porch head | Every ornamental member is round in section because it came off a lathe; Stick Style members are all flat and rectangular | Cut-shingle gable over clapboarded wall, with the change at the second-floor line | Where you find a classical column or a Palladian window on an otherwise Queen Anne house, you are in the free classic subtype instead
- massings: cross-gable-victorian, massed-picturesque, villa-tower, townhouse-row

## richardsonian-romanesque  [style]
**Richardsonian Romanesque** · 1880–1895 · United States Northeast, Chicago and the Midwest, Great Lakes · in: victorian
H. H. Richardson's personal manner and its national imitation: rock-faced ashlar, deep round arches springing from squat columns or from the ground, and a wall so heavy and continuous that the building reads as a single geological mass.
- lineage: references norman-romanesque-english; descends_from beaux-arts-french; reacts_against second-empire; reacts_against gothic-revival-american
- tells: The arch springs from the ground or from a column no more than three diameters tall; a tall slender column under a round arch indicates a later commercial imitation | Rock-faced stone with quarry tooling left visible, laid in broken-range or random coursing, with the face projecting 2 to 4 in beyond the joint | Window openings grouped in bands of three or five under a single relieving arch or lintel, rather than distributed one per bay | The tower, if any, is round and squat with a conical cap and is engaged into the corner of the mass; a slender detached tower is a different style
- massings: massed-picturesque, villa-tower, townhouse-row

## shingle-style  [style]
**Shingle Style** · 1880–1900 · Coastal New England, Newport and Narragansett Bay, Long Island · in: victorian
The one genuinely original American style of the nineteenth century: an irregular, freely planned house wrapped in a continuous unbroken skin of wooden shingles that runs across storey lines, around corners, and over the roof as a single surface.
- lineage: descends_from queen-anne-american; descends_from queen-anne-british; references colonial-revival; references new-england-colonial; hybridizes_with richardsonian-romanesque; references arts-and-crafts-british
- tells: Run your eye along a corner: if the shingles wrap the corner with no corner board, it is Shingle Style. A corner board makes it Queen Anne | Eaves are shallow, 6 to 12 in, and cut tight; deep bracketed eaves belong to Italianate or Stick Style | Window trim is 2 to 3 in wide or absent, and openings look punched rather than framed | Shingle butts are plain and uniform; patterned fish-scale or diamond coursing over more than a small panel indicates Queen Anne
- massings: massed-picturesque, gambrel-block, cross-gable-victorian

## beaux-arts-american  [style]
**American Beaux-Arts** · 1885–1930 · United States · in: eclectic-revivals
The high academic classicism of the American Gilded Age: monumental, richly sculptural, and rigorously planned on Ecole des Beaux-Arts principles of axis and hierarchy, built for the largest fortunes and the greatest public commissions between 1885 and 1930.
- lineage: descends_from beaux-arts-french; references french-neoclassical; references roman-classical; references italian-renaissance; references palladian; reacts_against richardsonian-romanesque
- tells: Paired or coupled columns and pilasters. Neoclassical Revival uses single columns; pairing is the fastest Beaux-Arts marker. | The skyline is populated - balustrades, urns, statuary, attic cartouches. Neoclassical Revival stops at the cornice. | Facade relief: the wall advances and recedes in pavilions of 18-36 in. Colonial and Neoclassical Revival keep the wall flat. | Rusticated ground storey with vermiculated or banded joints, under a smooth ashlar upper wall.
- massings: four-over-four, temple-front-with-wings, five-part-palladian

## dutch-colonial-revival  [variant]
**Dutch Colonial Revival** · 1890–1940 · United States · in: colonial-revival
The gambrel-roofed variant of Colonial Revival, in which a Hudson Valley barn profile is stretched to enclose a full second storey and becomes, between 1910 and 1930, the most economically efficient two-storey house in the American suburb.
- lineage: regional_of colonial-revival; references dutch-colonial-american; references hudson-valley-dutch; descends_from shingle-style; revives dutch-colonial-american
- tells: A gambrel with a full-length shed dormer is Dutch Colonial Revival essentially by definition; almost nothing else in American housing produces that profile. | Look for the eave kick: a 12-24 in. flare below the lower slope. Its presence marks an architect or a good builder; its absence marks a catalog house. | The lower slope is steep - 20:12 to 24:12 - and the upper is shallow - 6:12 to 9:12. If both slopes are near-equal the roof is a mansard and the building is Second Empire. | Compared with genuine Dutch colonial buildings: the originals are one-and-a-half storeys of stone with an unbroken roof sweep and no centre passage; the revival is two full storeys of frame with a 20 ft dormer in it.
- massings: gambrel-block, four-over-four, side-hall-double-pile

## italian-renaissance-revival  [style]
**Italian Renaissance Revival** · 1890–1935 · United States · in: eclectic-revivals
The academic American palazzo: a symmetrical masonry block with a low tile-hipped roof, a heavy bracketed or modillioned cornice, differentiated storeys with arcaded openings below and diminishing windows above, built as the sober alternative to Beaux-Arts display.
- lineage: references italian-renaissance; references palladian; descends_from beaux-arts-american; descends_from beaux-arts-french; descends_from italianate-american; reacts_against richardsonian-romanesque; revives italian-renaissance
- tells: Storey heights diminish upward and windows shrink with them. Colonial and Neoclassical Revival keep storey heights nearly equal and windows identical between floors. | The cornice overhang is 1/12 to 1/16 of the total wall height and is carried on visible modillions - much deeper than any Colonial Revival cornice and much plainer than any Beaux-Arts one. | No portico and no columns in front of the wall. The order, where present, is engaged as pilasters within the wall plane. | Tile roof plus a symmetrical flat-walled block plus arched ground-floor openings. Take away the symmetry and the arcade wraps a courtyard, and it becomes Mediterranean Revival.
- massings: four-over-four, courtyard-u

## queen-anne-free-classic  [variant]
**Queen Anne, Free Classic** · 1890–1910 · United States nationwide, Northeast, Midwest · in: queen-anne-american
The Queen Anne after 1890, in which classical columns, Palladian windows, and dentilled cornices replace turned spindlework while the irregular massing, dominant mass, and wrapping porch of the parent style are retained.
- lineage: regional_of queen-anne-american; references colonial-revival; descends_from queen-anne-british; references roman-classical; references georgian-colonial-american
- tells: Classical columns on an asymmetrical house is the whole diagnosis; if the facade were symmetrical it would be Colonial Revival | Dentils or modillions on a Queen Anne body, and critically, the cornice returning on the rake rather than running as a plain bargeboard | One Palladian window, placed in the principal gable or over the stair, and only one | Porch columns are grouped, two or three on a single pedestal, which is a free classic habit that classical Colonial Revival avoids
- massings: cross-gable-victorian, massed-picturesque, pyramidal-cottage

## tudor-revival  [style]
**Tudor Revival** · 1890–1940 · United States, Canada · in: eclectic-revivals
The dominant American picturesque revival of the interwar suburb, in which steeply pitched cross-gables, decorative half-timbering, and massive chimneys assemble a fantasy of English medieval building on a balloon-framed house with a two-car garage.
- lineage: references tudor; references english-medieval-timber-frame; references cotswold-vernacular; descends_from arts-and-crafts-british; descends_from beaux-arts-american; descends_from queen-anne-american; hybridizes_with shingle-style; reacts_against colonial-revival; revives tudor
- tells: Half-timbering that describes no possible frame: timbers that stop mid-wall, do not meet at corners, or run past window heads without a lintel. Genuine box-frame timbering always resolves into posts, sills, plates and braces. | Timbering thickness is the giveaway - revival boards are 1 to 2 in. thick nailed to sheathing; real English frames are 4 to 8 in. members with the stucco or brick nogging set between them and behind their face. | A cross-gable whose rake meets the wall in a straight line without a return, and an entrance arch of cast stone with a visible mould seam. | Windows are grouped in threes and fours with a single continuous head; Colonial and Georgian revivals keep windows single and evenly spaced.
- massings: massed-picturesque, cross-gable-victorian, h-plan-manor

## mission-revival  [style]
**Mission Revival** · 1893–1920 · United States · in: eclectic-revivals
California's first self-consciously regional style, built c. 1890-1920 from the silhouette of the ruined Franciscan missions: smooth stucco, a curvilinear shaped parapet, an arcaded porch, and almost no ornament at all.
- lineage: references california-mission-colonial; references spanish-colonial-american; descends_from richardsonian-romanesque; descends_from beaux-arts-french; descends_from shingle-style; reacts_against queen-anne-american; revives california-mission-colonial
- tells: The shaped parapet is the whole diagnosis. A curvilinear or stepped parapet on smooth stucco is Mission Revival and almost nothing else. | No ornament at the entrance. If there is a carved or cast surround around the front door, the building is Spanish Colonial Revival, not Mission Revival. | Wide overhanging eaves with exposed rafter tails - Spanish Colonial Revival usually has minimal overhang and closed eaves. | Composition is symmetrical or simply rectilinear; Spanish Colonial Revival breaks into asymmetrical masses at varied heights.
- massings: four-over-four, foursquare, courtyard-u

## georgian-revival  [variant]
**Georgian Revival** · 1895–1945 · United States, Canada · in: colonial-revival
The scholarly, usually brick, high-style wing of Colonial Revival, which after about 1915 replaced free invention with measured accuracy drawn from the Georgian houses of Virginia, Philadelphia and England.
- lineage: regional_of colonial-revival; revives georgian-colonial-american; references english-georgian; references tidewater-georgian; references adam-style; descends_from beaux-arts-american
- tells: Flemish bond with glazed or darker headers, a moulded water table, and a belt course together indicate the accurate phase; running bond with no water table indicates general Colonial Revival. | Sash carries 9 or 12 lights per unit rather than 6, with muntins near 3/4 in. - this variant is where the revival actually tries to match the original's glazing. | The doorcase is elaborate but never more than about 8 ft wide overall. If the entrance grows into a two-storey portico, the building has become neoclassical-revival. | Dormers are pedimented or arched with pilastered cheeks, not shed or gabled boxes.
- massings: four-over-four, five-part-palladian, side-hall-double-pile

## jacobethan-revival  [variant]
**Jacobethan Revival** · 1895–1935 · United States, Canada · in: tudor-revival
The formal, symmetrical, masonry wing of the English revival, quoting Elizabethan and Jacobean prodigy houses: parapeted and curvilinear gables, mullioned and transomed window walls, strapwork, and an E- or H-plan.
- lineage: regional_of tudor-revival; references elizabethan; references jacobean; references english-gothic; descends_from beaux-arts-american; revives jacobean
- tells: Parapeted gable - the wall carries up past the roof plane and is capped with coping stones. Tudor Revival gables end at the rake with a barge or a bargeboard. | Windows are mullioned bands rather than punched openings; the glass area on a principal elevation may exceed the stone. | No half-timbering anywhere. Its presence moves the building back to picturesque Tudor Revival. | The plan is symmetrical and the front door is on the centre line, which almost never happens in Tudor Revival.
- massings: h-plan-manor, courtyard-u

## neoclassical-revival  [style]
**Neoclassical Revival** · 1895–1950 · United States · in: eclectic-revivals
The academic classicism launched by the 1893 World's Columbian Exposition, in which a colossal columnar portico - two storeys tall, correctly ordered, and almost always structurally unnecessary - becomes the standard American emblem of institutional and personal permanence.
- lineage: revives greek-revival-american; references roman-classical; references greek-classical; descends_from beaux-arts-american; descends_from beaux-arts-french; hybridizes_with colonial-revival; reacts_against richardsonian-romanesque; revives roman-classical
- tells: Columns run two full storeys. One-storey columns on an otherwise similar house make it Colonial Revival, not Neoclassical. | The order is correct - the shaft tapers, the capital is turned or cast to a published profile - where Colonial Revival will accept an untapered box column. | Roof pitch is low, 4:12 to 6:12, and often invisible behind a balustrade; Greek Revival originals carry a shallow pediment as the roof itself rather than hiding one. | The cornice runs continuously around the whole building at one height, including the rear, which no Greek Revival or Colonial house bothers to do.
- massings: temple-front-with-wings, four-over-four, five-part-palladian

## arts-and-crafts-american  [style]
**American Arts and Crafts** · 1897–1920 · United States, Canada · in: american-arts-and-crafts
The American branch of the Arts and Crafts reform, which held that ornament must arise from construction and that a house, its furniture, and its site are a single commission, and which reorganized the middle-class plan around an open hearth-centred living room.
- lineage: descends_from arts-and-crafts-british; descends_from shingle-style; descends_from richardsonian-romanesque; reacts_against queen-anne-american
- tells: Exposed rafter tails and knee braces that continue the actual framing rather than being screwed on | Battered (tapered) porch piers standing on heavy masonry bases at least two feet wide | Wide flat unpainted trim, a plate rail at door head height, and bookcases built into the wall flanking the fireplace | Art glass in rectilinear, non-floral geometry, usually confined to upper sash and cabinet doors
- massings: bungalow-linear, foursquare

## american-arts-and-crafts  [family]
**American Arts and Crafts** · 1900–1935 · United States · in: north-american
Craftsman, bungalow, and Prairie — the American translation of the British reform argument into a mass-market house that millions actually bought.
- lineage: —

## prairie-school  [style]
**Prairie School** · 1900–1917 · United States, Canada · in: american-arts-and-crafts
The Chicago-centred style that answered the exhaustion of Victorian building by dissolving the house into horizontal planes gathered about a central chimney, and in doing so became the point at which the American tradition begins arguing with itself.
- lineage: descends_from arts-and-crafts-american; descends_from shingle-style; descends_from richardsonian-romanesque; reacts_against queen-anne-american; reacts_against colonial-revival
- tells: The eave soffit is clean: no rafter tails, no knee braces, no brackets. This is the fastest separation from Craftsman. | Roman brick — brick roughly twice as long and half as tall as standard — laid with raked horizontal and flush vertical joints so only the horizontal reads | Casement windows in continuous ribbons, with art glass in rectilinear geometry and no curves | The chimney is visibly the fattest object in the composition and the plan turns around it
- massings: prairie-cruciform, foursquare

## california-bungalow  [variant]
**California Bungalow** · 1905–1930 · United States · in: craftsman
The Southern Californian bungalow in which the Craftsman grammar was first assembled, distinguished from the national type by lower pitches, deeper shading eaves, stucco and boulder masonry, and a set of genuinely outdoor rooms — sleeping porch, pergola, court — that only its climate permits.
- lineage: regional_of craftsman; hybridizes_with mission-revival; hybridizes_with spanish-colonial-revival; hybridizes_with swiss-chalet
- tells: Roof pitch visibly below 5:12 with an overhang deep enough to stand under | Arroyo boulder or clinker brick used raw against smooth machined woodwork on the same porch | A pergola, trellis, or extended open beam structure continuing the roof plane past the enclosed wall | Sleeping porch on the upper level, screened rather than glazed, often with its own small hipped roof
- massings: bungalow-linear, airplane-bungalow

## craftsman  [style]
**Craftsman** · 1905–1925 · United States, Canada · in: american-arts-and-crafts
The American Arts and Crafts programme reduced to a reproducible builder's grammar of low gable roofs, deep exposed eaves, battered porch piers and hearth-centred open plans, distributed nationally by Gustav Stickley's The Craftsman and by the plan-book and mail-order trade that copied it.
- lineage: descends_from arts-and-crafts-american; descends_from arts-and-crafts-british; hybridizes_with swiss-chalet; descends_from shingle-style; reacts_against queen-anne-american
- tells: Four-over-one or three-over-one double-hung sash — vertical muntins in the upper sash only. This single detail separates Craftsman from every neighbour in the graph. | Battered porch piers: the support is wider at the bottom than at the top, on a base wider still | Knee braces under the gable overhang, and rafter tails visible along the eave, both structurally continuous | The porch roof is geometrically part of the main roof, not a separate element pinned to the wall below it
- massings: bungalow-linear, airplane-bungalow, foursquare

## craftsman-bungalow  [variant]
**Craftsman Bungalow** · 1908–1925 · United States, Canada · in: craftsman
The Craftsman grammar compressed into a one-to-one-and-a-half storey, nine-hundred-to-fourteen-hundred square foot house sold as a plan book design or a precut kit, and built across the United States in numbers that made it the first genuinely national American house type.
- lineage: regional_of craftsman; hybridizes_with folk-victorian
- tells: Front door opens directly into the living room with no vestibule — the plan's fingerprint | Porch piers of clinker brick or fieldstone carrying tapered wood posts, with a solid porch balustrade of the same masonry | Shed dormer set well back from the eave line, with its own small overhang | Three- or four-over-one sash, and a wide flat casing 4 to 5 in deep around every opening
- massings: bungalow-linear, airplane-bungalow

## french-eclectic  [style]
**French Eclectic** · 1915–1945 · United States · in: eclectic-revivals
The interwar American reading of the French provincial manor and farmhouse, distinguished from its English-derived neighbours by a tall hipped roof of near-equal pitch on all sides, flared at the eave, and by dormers that break the cornice line.
- lineage: references french-manoir; references french-provincial-farmhouse; references norman-vernacular; references french-neoclassical; descends_from beaux-arts-american; descends_from arts-and-crafts-british; hybridizes_with tudor-revival
- tells: Hipped roof of equal pitch on all four sides with no front gable. One dominant cross-gable and the house is Tudor Revival, not French Eclectic. | The eave flare: a change of rafter angle in the bottom 18-30 in. of the roof, producing a visible upward curve. Nothing English does this. | Dormers cut through the wall head so that their cheeks are masonry continuous with the wall below, rather than sitting entirely on the roof slope. | Windows are casements, not double-hung, and their proportion is tall - 1:2.5 or better - with the head often segmental or round.
- massings: massed-picturesque, four-over-four, h-plan-manor

## pueblo-revival  [style]
**Pueblo Revival** · 1915–1950 · United States · in: eclectic-revivals
The Santa Fe style: flat-roofed, parapeted, earth-coloured buildings with battered walls, projecting vigas, and stepped massing, invented between 1908 and 1917 by Anglo architects and boosters assembling a marketable regional identity from Puebloan and Hispano New Mexican building.
- lineage: references new-mexico-adobe; references california-mission-colonial; hybridizes_with spanish-colonial-revival; descends_from arts-and-crafts-american; descends_from beaux-arts-american; references mission-revival; revives new-mexico-adobe
- tells: Flat roof plus vigas plus rounded corners. Any one of the three alone is inconclusive; all three together are decisive. | The parapet top is not level. A dead-straight parapet indicates a Territorial or commercial building rather than Pueblo Revival. | Vigas are round peeled logs 8-12 in. in diameter projecting 12-24 in. Square sawn timbers projecting from a wall are Territorial or Spanish Colonial Revival, not Pueblo Revival. | No brick coping. A brick dentil course capping the parapet marks the Territorial Revival variant, which is a distinct and equally common New Mexican type.
- massings: massed-picturesque, courtyard-u, gallery-house

## spanish-colonial-revival  [style]
**Spanish Colonial Revival** · 1915–1942 · United States · in: eclectic-revivals
The style launched by Bertram Goodhue's 1915 Panama-California Exposition in San Diego, which replaced Mission Revival's austerity with the full Spanish and Latin American repertoire: elaborately carved entrances against blank walls, wrought iron, decorative tile, low-pitched red tile roofs, and freely asymmetrical massing.
- lineage: references spanish-colonial-american; references churrigueresque; references andalusian-courtyard-vernacular; references mexican-colonial; references moorish-andalusian; references mudejar; descends_from mission-revival; descends_from beaux-arts-american; revives spanish-colonial-american
- tells: Ornament is concentrated in one place and absent everywhere else. Evenly distributed ornament means a later imitation. | Roof planes meet at different heights and the ridges do not align. Mission Revival keeps a single roof line and a symmetrical front; Mediterranean Revival keeps a uniform hip. | No curvilinear shaped parapet. If there is one, the building is Mission Revival, or a hybrid. | Eave overhang under 12 in. with a closed soffit or a plastered edge, versus Mission Revival's 24-42 in. of exposed rafter tail.
- massings: courtyard-u, massed-picturesque, courtyard-full

## mediterranean-revival  [style]
**Mediterranean Revival** · 1918–1942 · United States · in: eclectic-revivals
The resort and estate style of the American subtropics, in which a symmetrical or lightly asymmetrical stuccoed block with a low tile roof opens through loggias and arcades onto terraces and courtyards, mixing Italian villa formality with Spanish and Moorish detail.
- lineage: references italian-villa-vernacular; references andalusian-courtyard-vernacular; references moorish-andalusian; descends_from italian-renaissance-revival; descends_from beaux-arts-american; hybridizes_with spanish-colonial-revival
- tells: Wall reveals are deep: 6 in. minimum and often 12-18 in., so every window sits in a visible shadow box. This single measurement separates a real example from a stucco-clad frame house at fifty feet. | The roof is hipped, low, and continuous around the whole building; Spanish Colonial Revival breaks its roof into varied planes at varied heights and often uses gables. | Composition is broadly symmetrical or axial even when the plan rambles - the entrance sits on an axis that continues through the house to a garden feature. | Cornices and eaves are minimal or absent; where present they are a simple moulded band, never the modillioned overhang of Italian Renaissance Revival.
- massings: courtyard-u, courtyard-full, four-over-four

## cotswold-cottage-revival  [variant]
**Cotswold Cottage Revival** · 1920–1940 · United States · in: tudor-revival
The small, all-stone or stone-and-stucco wing of the English revival, imitating the Gloucestershire cottage: very steep roofs with rolled or swept eaves, a massive chimney on the entrance facade, tiny casements, and an arched door under a catslide.
- lineage: regional_of tudor-revival; references cotswold-vernacular; references english-cottage-vernacular; descends_from arts-and-crafts-british; descends_from arts-and-crafts-american; revives cotswold-vernacular
- tells: Rolled eaves. If the roof edge curves around the corner or over a dormer rather than terminating in a straight fascia, this is the variant. | The chimney is on the front and it is disproportionately large - often 1/4 to 1/3 of the elevation's width. | No half-timbering. Its presence returns the building to the parent Tudor Revival. | A catslide - one roof plane running much further down than the other, often to below head height - over the entrance or a side wing.
- massings: massed-picturesque, cross-gable-victorian

## french-normandy-revival  [variant]
**French Normandy Revival** · 1920–1940 · United States · in: french-eclectic
The Norman farmhouse variant of French Eclectic, identified by a round or polygonal entrance tower with a conical roof set at the junction of two wings, combined with steep hipped roofs, half-timbering, and mixed brick, stone and stucco walls.
- lineage: regional_of french-eclectic; references norman-vernacular; references french-provincial-farmhouse; references french-manoir; hybridizes_with tudor-revival; descends_from arts-and-crafts-british; revives norman-vernacular
- tells: The conical-roofed round tower at an inside corner is decisive; nothing else in American domestic architecture places one there. | Steep hipped roofs with no dominant front gable, plus half-timbering. Tudor Revival gives you the timbering with gables; the parent French Eclectic gives you the hips without timbering. | Wall material changes vertically and abruptly - stone below, stucco and timber above - at a floor line or a jetty. | Casements, not double-hung, and a segmental or round-headed dormer.
- massings: massed-picturesque, cross-gable-victorian

## andalusian-spanish-revival  [variant]
**Andalusian Spanish Revival** · 1922–1940 · Southern California, Santa Barbara, Arizona · in: spanish-colonial-revival
The rural, whitewashed, deliberately plain branch of Spanish Colonial Revival, taken from Andalusian farmhouses rather than from Spanish churches, and centred on Santa Barbara in the 1920s.
- lineage: regional_of spanish-colonial-revival; references andalusian-courtyard-vernacular; references moorish-andalusian; hybridizes_with mexican-hacienda; descends_from beaux-arts-american
- tells: Window reveals deep enough to throw a hard shadow at midday — 8 to 14 inches, expressing wall mass | Asymmetrical, apparently accidental fenestration on a formally composed plan | No visible gutters, no fascia board, tile running directly to a plastered edge | A single ornamental event on an otherwise silent elevation
- massings: courtyard-u, courtyard-full, gallery-house

## storybook-style  [style]
**Storybook Style** · 1922–1935 · United States · in: eclectic-revivals
A knowingly theatrical Los Angeles idiom of the 1920s in which the English and Norman cottage was rebuilt in studio plaster with its irregularities deliberately exaggerated — sagging ridges, rolled eaves, oversized chimneys, undersized doors — to make a house that performs a narrative.
- lineage: descends_from cotswold-cottage-revival; descends_from tudor-revival; hybridizes_with french-eclectic; references english-cottage-vernacular; reacts_against tudor-revival; reacts_against cotswold-cottage-revival; reacts_against craftsman-bungalow
- tells: Shingle courses rolled and curled around the eave and rake edge — the fake-thatch move, and the fastest positive identification | A roof that sweeps down to within 6 or 7 ft of the ground on one side (catslide) while the opposite eave stays high | Half-timbering that does not meet at the corners or align across a floor line | A round or polygonal turret whose conical roof is too tall and too steep for its diameter
- massings: massed-picturesque, gable-front-and-wing

## monterey-revival  [variant]
**Monterey Revival** · 1929–1955 · California, Southwest United States, Texas · in: spanish-colonial-revival
The 1930s revival of California's brief Anglo-Hispanic hybrid, defined by a full-width second-storey cantilevered balcony running across a two-storey block under a low-pitched tile or shingle roof.
- lineage: regional_of spanish-colonial-revival; revives monterey-colonial; hybridizes_with colonial-revival; hybridizes_with andalusian-spanish-revival; descends_from beaux-arts-american
- tells: The balcony runs the entire elevation without interruption — a partial or centred balcony is a different and lesser thing | Stucco below and wood siding above, with the material change occurring exactly at the balcony floor line | Shutters and double-hung sash appearing on a tile-roofed stuccoed house | A slender, almost thin balcony rail and posts, quite unlike the heavy iron of the parent style
- massings: four-over-four, side-hall-double-pile, gallery-house

## cape-cod-revival  [variant]
**Cape Cod Revival** · 1930–1960 · United States, Canada · in: colonial-revival
The small, steep-roofed, one-and-a-half-storey frame house that Royal Barry Wills and the FHA between them made the default American starter home from 1935 to 1960, and the one revival in this branch that shrank its model rather than inflating it.
- lineage: regional_of colonial-revival; revives cape-cod-colonial; references new-england-colonial; hybridizes_with minimal-traditional
- tells: Second-floor windows sit in dormers or in the gable ends, never in a full-height side wall. A full second storey makes it a Colonial Revival, not a Cape. | Roof pitch 8:12 to 10:12 with the eave nearly touching the upper window heads; a 6:12 roof with a tall wall is Minimal Traditional. | The chimney is on the ridge at or near the centre. A gable-end chimney is acceptable in pairs; an off-centre single stack is a builder's compromise. | No cornice, no returns, no frieze board. The presence of a modillioned cornice means the house has left this variant.
- massings: cape-cod-massing, saltbox

## mid-century-traditional  [family]
**Mid-Century Traditional** · 1930–1975 · United States · in: north-american
Minimal Traditional, Ranch, and their relatives — the era when the traditional kit of parts was systematically cost-engineered out of the American house.
- lineage: —

## garrison-revival  [variant]
**Garrison Revival** · 1935–1970 · United States · in: colonial-revival
The mid-century builder's Colonial: a rectangular two-storey box whose upper floor projects 8 to 18 inches over the lower on the front elevation, decorated with turned drops, and derived from a seventeenth-century framing condition that the twentieth century reproduced with no structure behind it.
- lineage: regional_of colonial-revival; references garrison-colonial; references new-england-colonial; hybridizes_with cape-cod-revival; revives garrison-colonial
- tells: The overhang appears on the front elevation only and stops at the corners. Genuine seventeenth-century jetties usually turn the corner and continue on the gable ends. | Drops are turned wooden or cast pendants applied to the soffit; on originals they are the carved lower ends of continuous corner posts and are therefore structurally continuous with the frame above. | Overhang depth is the whole diagnosis: 8-18 in. reads correctly, 4-6 in. reads as a siding error, over 24 in. is implausible as joist cantilever. | Everything else on the house is standard Colonial Revival, including the attached garage that dates it after 1935.
- massings: garrison-block, four-over-four

## minimal-traditional  [style]
**Minimal Traditional** · 1935–1950 · United States, Canada · in: mid-century-traditional
The smallest complete house the American mortgage system could underwrite: traditional in silhouette, symmetrical enough to be legible, and stripped of overhang, porch, profile depth, and every other element that cost money — the direct ancestor of the ranch and the moment the traditional kit of parts was cost-engineered out of the American house.
- lineage: descends_from colonial-revival; references cape-cod-revival; descends_from tudor-revival; reacts_against craftsman
- tells: A recognizably traditional shape with essentially no eave — the roof surface stops at the wall surface and the two meet without a shadow line | Shutters roughly half the width of the sash they flank, fixed flat to the wall | The front door lies in the plane of the wall with a reveal of an inch or less and no projecting surround | A single small gabled or hipped entry projection or bay as the only three-dimensional event on the whole elevation
- massings: cape-cod-massing, gable-front-and-wing

## ranch-style  [style]
**Ranch** · 1945–1970 · United States, Canada · in: mid-century-traditional
The long, low, single-storey suburban house of postwar America, and the first house type in the world organized around the automobile — a reorganization it accomplished by attaching the garage to the street elevation, a problem it never solved and bequeathed to every traditional style built since.
- lineage: descends_from minimal-traditional; descends_from prairie-school; descends_from craftsman; references monterey-colonial
- tells: The garage door is the largest single element on the street elevation | A picture window composed as a wide fixed centre light flanked by narrow operable sash | Roof ridge running unbroken for 40 ft or more at a pitch under 5:12 | Finish floor within about 12 in of exterior grade, with one or two steps at the entry rather than a raised stoop
- massings: ranch-linear, ranch-l, split-level

## neo-eclectic  [style]
**Neo-Eclectic** · 1970–2000 · United States, Canada · in: mid-century-traditional
The production-builder idiom of the late twentieth century, in which historical motifs were selected from an elevation menu and applied to a plan generated independently of them — the point at which the traditional grammar decoupled from its own logic.
- lineage: descends_from ranch-style; descends_from minimal-traditional; references colonial-revival; references tudor-revival; references second-empire; references french-eclectic
- tells: Brick front with a 6-to-12-inch return onto the side elevation, then vinyl | Shutters at roughly half the width of the window, present on windows that are ganged or arched | A half-round or 'Palladian' window filling a gable, unrelated in width to anything below it | Three or more different window shapes — rectangular, arched, half-round, octagonal — on one elevation
- massings: cross-gable-victorian, ranch-l, split-level

## contemporary-traditional  [family]
**Contemporary Traditional** · 1980–2026 · United States · in: north-american
New Classical, New Urbanist, and the current market idioms — the living attempt to recover traditional design logic under contemporary economics.
- lineage: —

## new-classical  [style]
**New Classical** · 1980–2026 · United States, United Kingdom, Canada · in: contemporary-traditional
The reconstitution of classical architecture as a live, taught, and practised discipline from the late 1960s onward, in which the orders are used as a working proportional system rather than quoted as motifs, and in which the pattern book and the code have returned as the medium of transmission.
- lineage: descends_from palladian; descends_from beaux-arts-american; descends_from colonial-revival; revives english-georgian; revives georgian-colonial-american; references greek-revival-american
- tells: Window reveal depth of four inches or more in masonry — a shadow at the edge of every opening | A cornice that casts a hard continuous shadow line across the whole facade | Correct entablature subdivision, with architrave, frieze, and cornice in canonical proportion rather than as three arbitrary bands | A brick wall with a genuine water table, belt course, and moulded cap, all returning around every corner
- massings: five-part-palladian, center-passage-single-pile, temple-front-with-wings, townhouse-row

## new-urbanist-traditional  [style]
**New Urbanist Traditional** · 1981–2026 · United States, Canada · in: contemporary-traditional
The traditional architecture produced under form-based codes in walkable new towns from Seaside onward, in which the street section, the build-to line, the frontage type, and the relegation of the garage are specified before style, and the style itself is drawn from a single regional vernacular.
- lineage: descends_from folk-victorian; descends_from charleston-single-house; descends_from greek-revival-american; descends_from colonial-revival; hybridizes_with new-classical; reacts_against neo-eclectic; reacts_against ranch-style
- tells: No garage doors visible from the street anywhere on the block | Front porches at eight feet or more of depth, at setbacks of twelve to eighteen feet, occupied by actual furniture | A hard build-to line: adjacent facades line up within a foot or two, and the fence or hedge continues the line across the gaps | Streets narrow enough that two moving cars must negotiate, with parking on both sides
- massings: gable-front-and-wing, charleston-single, townhouse-row, linear-ell-farmhouse

## modern-farmhouse-traditional  [style]
**Modern Farmhouse** · 2014–2026 · United States, Canada · in: contemporary-traditional
The market-dominant American idiom of the 2010s and 2020s: white board-and-batten or lap siding with black windows and black metal accents under a simple gable, descending in silhouette from the farmhouse vernacular, in economy from minimal traditional, in apparatus from the production builder, and in section from contemporary open planning.
- lineage: references american-farmhouse-vernacular; descends_from minimal-traditional; descends_from neo-eclectic; reacts_against neo-eclectic; descends_from ranch-style
- tells: Black windows in a white wall, with no trim colour in between | Board-and-batten to the gable or upper storey over lap siding below, with the change occurring at a floor line | A standing-seam shed roof over the entry, in a different plane and material from the main roof | Overhangs under 12 in, boxed, with no rake return at the gable corner
- massings: linear-ell-farmhouse, gable-front-and-wing, ranch-l
