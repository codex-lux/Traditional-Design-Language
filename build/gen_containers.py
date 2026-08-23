import json, os
S='styles'
os.makedirs(S, exist_ok=True)

def node(**kw):
    n = {"id":kw["id"],"name":kw["name"],"rank":kw["rank"],"member_of":kw.get("member_of"),
         "status":kw.get("status","historical"),
         "period":{"origin":kw.get("origin"),"floruit_start":kw["fs"],"floruit_end":kw["fe"],
                   "decline_end":kw.get("decline"),"circa":True,"revival_periods":kw.get("revivals",[])},
         "geography":{"regions":kw["regions"]},
         "lineage":kw.get("lineage",[]),
         "description":{"short":kw["short"],"long":kw["long"]},
         "defining_characteristics":kw["dc"],
         "confidence":kw.get("conf","high"),
         "tags":kw.get("tags",["container"])}
    if kw.get("aka"): n["aka"]=kw["aka"]
    if kw.get("hearth"): n["geography"]["hearth"]=kw["hearth"]
    json.dump(n, open(f"{S}/{kw['id']}.json","w"), indent=2, ensure_ascii=False)

T = [
dict(id="classical-mediterranean",name="Classical Mediterranean",rank="tradition",member_of=None,fs=-600,fe=1900,origin=-700,
 regions=["Greece","Italy","France","Mediterranean basin"],status="living",
 short="The trunk of column, entablature, and proportional order that runs from archaic Greece through Rome and the Renaissance into every classical revival since.",
 long=("This is the longest continuous design tradition in Western building, and the only one that has ever been written down as a system. Its distinguishing property is not a set of shapes but a set of relations: a module is chosen — classically the diameter of the column at its base — and every other dimension in the building is derived from it. The result is that a Doric temple and a Georgian farmhouse can share a grammar while sharing almost no dimensions.\n\n"
  "The tradition survives three near-deaths and three resurrections. Rome absorbs and industrializes the Greek orders, adding the arch and the vault that Greek trabeated construction could not produce. The Latin West largely loses the system for a millennium, keeping fragments as spolia and half-remembered proportion. Fifteenth-century Florence recovers it by measuring ruins and reading Vitruvius, and Palladio converts the recovered system into a design method transmissible by book — the decisive act, because a book crosses oceans and a guild does not.\n\n"
  "What makes the classical stream matter for a kit of parts is precisely that it was always already a kit of parts. The orders are a parametric system with inheritance: choose Tuscan or Corinthian and a hundred subordinate dimensions follow. Any attempt to encode traditional design as software is, whether it admits it or not, re-implementing something Vitruvius, Serlio, and Gibbs each attempted with the tools of their century."),
 dc=["Proportional derivation from a governing module rather than from absolute dimensions",
     "The orders as a graduated system of character, from robust Tuscan to delicate Corinthian",
     "Trabeated expression — the visible logic of support and load, retained even where it is no longer structural",
     "Bilateral symmetry as the default state of a composition",
     "Transmission by treatise and pattern book, making the system portable across geography and craft tradition"]),

dict(id="british-isles",name="British Isles",rank="tradition",member_of=None,fs=1000,fe=1940,origin=900,
 regions=["England","Scotland","Wales","Ireland"],status="living",
 short="The insular stream that fused Norman masonry, medieval timber framing, and imported classicism into the pattern-book culture that furnished colonial America with most of its architecture.",
 long=("Britain's building tradition is a hybrid from the start: Romanesque masonry from Normandy laid over Anglo-Saxon timber practice, then Gothic, then a late and reluctant Renaissance arriving through Netherlandish intermediaries rather than directly from Italy. The reluctance matters. English classicism is never purely classical; it is classicism negotiated with a stubborn vernacular of steep roofs, tall chimneys, and small-paned windows suited to a cold, wet, cloudy island.\n\n"
  "The decisive British contribution to world architecture is not a style but a medium: the pattern book. Beginning in the early eighteenth century, builders' guides by Gibbs, Langley, Swan, and later Asher Benjamin in America converted architectural knowledge from guild apprenticeship into printed, purchasable instruction. A carpenter in rural Connecticut who had never seen a classical building could execute a correct Ionic door surround from a plate. This is the historical precedent for what a design platform now attempts, and it is worth studying closely — including its failures, which were mostly failures of proportion at unusual scales.\n\n"
  "The second British contribution is the picturesque: the deliberate composition of irregular, asymmetrical, historically allusive buildings for their visual and emotional effect. This is the ancestor of Gothic Revival, Queen Anne, Shingle Style, and eventually of the entire Anglo-American suburban imagination."),
 dc=["Steep roof pitches and prominent chimney stacks as climatic and compositional constants",
     "Classicism absorbed and domesticated rather than adopted wholesale",
     "Pattern-book transmission of design knowledge from the early 18th century onward",
     "A strong parallel vernacular of local stone, brick, and timber that never fully surrenders to fashion",
     "The picturesque as a legitimate compositional method alongside the classical"]),

dict(id="northern-european-vernacular",name="Northern European Vernacular",rank="tradition",member_of=None,fs=1200,fe=1900,origin=1100,
 regions=["Netherlands","Belgium","Germany","France","Scandinavia","Alps"],status="living",
 short="The continental traditions of timber frame, steep roof, and hard climate that arrived in America with Dutch, German, French, and Scandinavian settlers.",
 long=("Continental northern Europe produced building traditions shaped by long winters, abundant timber, and dense agricultural settlement rather than by treatise. Their logic is material and climatic before it is compositional: a roof pitched steeply enough to shed snow, a frame exposed and infilled because timber was the scarce and expensive part, a house and byre under one roof because a cow in the next room is a heat source.\n\n"
  "These traditions reached North America through settlement rather than through books, which changes everything about how they behave. A pattern book transmits a style intact and abstract; a settler transmits what he can remember and build with the materials at hand. Dutch framing survives in the Hudson Valley as a gambrel roof and a particular way of hanging a door, German framing survives in Pennsylvania as a bank-set stone house with a forebay, and both lose their surface identity within two generations while keeping their structural habits.\n\n"
  "For a design system this is instructive: the durable inheritance is rarely the ornament. It is the section, the roof pitch, the relationship to grade, and the position of the hearth."),
 dc=["Steep pitches and large roof volumes doing significant work in the section",
     "Exposed structural framing as both economy and expression",
     "House and agricultural function integrated rather than separated",
     "Transmission by settlement and craft memory rather than by treatise",
     "Strong grade relationships — banked, cellared, or raised — responding to slope and frost"]),

dict(id="iberian-mediterranean",name="Iberian & Mediterranean",rank="tradition",member_of=None,fs=800,fe=1900,origin=750,
 regions=["Spain","Portugal","North Africa","Mexico","Spanish Americas"],status="living",
 short="The courtyard, thick wall, and tile tradition of the Iberian peninsula, carrying an Islamic inheritance into the Americas by way of Mexico.",
 long=("The Iberian tradition is the one Western stream shaped decisively by Islamic building culture. Eight centuries of al-Andalus left a permanent inheritance: the inward-turned courtyard, water as an architectural element, geometric surface ornament in tile, the blind street wall, and a fundamentally different relationship between house and public realm than anything in the Anglo world. A Georgian house presents its best face to the street. An Andalusian house presents a wall and a door, and keeps its face for itself.\n\n"
  "Carried to the Americas by conquest and mission, the tradition met adobe construction, indigenous labor, and a scarcity of skilled masons, producing a simplified, massive, plain-surfaced architecture that has almost nothing in common with the Baroque churches of Spain except its plan diagrams and its tile. That simplification is not a loss — it is the emergence of a genuinely new regional language, and the direct ancestor of Mission Revival, Spanish Colonial Revival, and the entire architecture of California and the Southwest.\n\n"
  "The tradition's hot-dry climate logic — thermal mass, small openings, deep shade, courtyards, cross-ventilation at night — is now the most technically relevant traditional inheritance available to builders in the American Sun Belt."),
 dc=["Inward orientation: courtyard and patio as the organizing void, street elevation substantially closed",
     "Massive wall construction — adobe, rammed earth, rubble stone, brick — with deep window reveals",
     "Small, deeply-set openings and generous shaded transitional space",
     "Low-pitched or flat roofs, clay tile, parapets",
     "Surface ornament concentrated at the entry and in tile rather than distributed over the facade"]),

dict(id="north-american",name="North American",rank="tradition",member_of=None,fs=1600,fe=2026,origin=1565,
 regions=["United States","Canada"],status="living",
 short="Four centuries of transplanted European traditions hybridizing with new climates, new materials, new technologies, and a new social order to produce the world's most stylistically promiscuous residential architecture.",
 long=("North American residential architecture is not a style but a laboratory. Every European tradition arrives, meets a climate it was not designed for and a labor market that cannot supply its craft, and mutates. The mutations are the interesting part: the Georgian box grows a porch it never had in England, the Dutch gambrel outlives the Dutch, the Spanish courtyard opens up when it reaches a wetter latitude, and the log pen from Scandinavia becomes the substrate of an entire Appalachian building culture.\n\n"
  "Three technological ruptures organize the whole story. Balloon framing and machine-cut nails around 1840 make complex irregular massing cheap for the first time, and the Victorian era is the immediate consequence. The railroad and the mail-order catalog around 1890 make a house in Iowa identical to a house in Oregon, which produces both national styles and the first crisis of placelessness. The automobile after 1930 reorganizes the plan around the garage and the lot around the driveway, a problem no traditional style solved because none had to.\n\n"
  "The fourth rupture is happening now, and it is worth naming plainly: design knowledge is moving from the drafting room into software. The question this taxonomy exists to answer is whether that movement carries the traditional grammar with it or leaves it behind. Every previous rupture that democratized building — the pattern book, the catalog, the tract plan — degraded proportion while extending access. There is no law requiring the next one to do the same."),
 dc=["Continuous hybridization of transplanted traditions under new climatic and economic conditions",
     "The porch, the ell, and the accretive plan as characteristically American adaptations",
     "Technological ruptures (balloon frame, catalog, automobile) as primary drivers of stylistic change",
     "Revivalism as a permanent condition rather than an episode",
     "Regional variation of national styles as the level at which real buildability lives"]),
]
for t in T: node(**t)
print("traditions:", len(T))
