#!/usr/bin/env python3
import json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

nodes = {}
for f in sorted(glob.glob("styles/*.json")):
    n = json.load(open(f)); nodes[n["id"]] = n
slots_doc = json.load(open("elements/slots.json"))
massings = {m["id"]: m for m in json.load(open("massings/catalog.json"))}

TRAD_ORDER = ["classical-mediterranean","british-isles","northern-european-vernacular",
              "iberian-mediterranean","north-american"]

def cascade(i, seen=None):
    seen = seen or set(); out=[]
    for e in sorted(nodes[i].get("lineage",[]), key=lambda e:-e.get("weight",1)):
        if not e.get("inherits_kit"): continue
        t=e["target"]
        if t in seen or t not in nodes: continue
        seen.add(t); out.append(t); out.extend(cascade(t,seen))
    return out

# ordered row list
rows=[]
def fs(i): return nodes[i]["period"]["floruit_start"]
for t in TRAD_ORDER:
    rows.append({"kind":"tradition","id":t})
    fams=sorted([i for i,n in nodes.items() if n.get("member_of")==t], key=fs)
    for fam in fams:
        rows.append({"kind":"family","id":fam})
        sts=sorted([i for i,n in nodes.items() if n.get("member_of")==fam], key=fs)
        for st in sts:
            rows.append({"kind":"node","id":st})
            for v in sorted([i for i,n in nodes.items() if n.get("member_of")==st], key=fs):
                rows.append({"kind":"node","id":v})

placed={r["id"] for r in rows}
orphans=[i for i in nodes if i not in placed]

out=[]
for i,n in nodes.items():
    out.append({
      "id":i,"name":n["name"],"aka":n.get("aka",[]),"rank":n["rank"],
      "member_of":n.get("member_of"),"status":n.get("status","historical"),
      "p":[n["period"]["floruit_start"],n["period"]["floruit_end"],n["period"].get("origin"),n["period"].get("decline_end")],
      "rev":n["period"].get("revival_periods",[]),
      "geo":n["geography"],"lin":n.get("lineage",[]),
      "s":n["description"]["short"],"l":n["description"]["long"],
      "dc":n.get("defining_characteristics",[]),"dt":n.get("diagnostic_tells",[]),
      "df":n.get("distinguished_from",[]),"ps":n.get("proportional_system",{}),
      "ma":n.get("massing_affinities",[]),"cn":n.get("constraints",[]),
      "ex":n.get("exemplars",[]),"src":n.get("sources",[]),"conf":n.get("confidence","medium"),
      "casc":cascade(i)
    })

DATA={"nodes":out,"rows":rows,"orphans":orphans,
      "groups":[{"id":g["id"],"name":g["name"],"note":g.get("note",""),
                 "slots":[{"id":s["id"],"name":s["name"],"note":s.get("note",""),"cardinality":s.get("cardinality"),"value_type":s.get("value_type")} for s in g["slots"]]}
                for g in slots_doc["groups"]],
      "massings":{k:{"name":v["name"],"desc":v["description"],"foot":v["footprint"],"st":v["stories"],"exp":v.get("expansion_logic","")} for k,v in massings.items()},
      "traditions":TRAD_ORDER}

tpl = open("build/template.html").read()
html = tpl.replace("/*__DATA__*/null", json.dumps(DATA, separators=(",",":"), ensure_ascii=False))
open("dist/taxonomy.html","w").write(html)
print("rows",len(rows),"orphans",orphans,"size MB",round(os.path.getsize('dist/taxonomy.html')/1e6,2))
