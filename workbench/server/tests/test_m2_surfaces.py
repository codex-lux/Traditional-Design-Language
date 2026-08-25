"""Milestone 2 endpoints: the pack list, member-level dimensioning, and the
cross-check that the HTTP numbers are the engine's own — no drift between what the
surface shows and what proportion_engine computes."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_pack_list_leads_with_material_modules(client):
    r = client.get("/api/proportions").json()
    assert r["count"] == 36
    kinds = [p["kind"] for p in r["packs"]]
    # the non-classical packs are equal citizens, and they lead
    assert kinds[0] == "module-system"
    assert kinds.index("order-system") > kinds.index("module-system")


def test_members_match_engine(client):
    r = client.get("/api/proportions/gibbs-doric",
                   params={"column_diameter": 12, "members": True}).json()
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    pe = modcache.load("pe", os.path.join(ROOT, "build", "proportion_engine.py"))
    pk = pe.resolve("gibbs-doric")
    d = pe.dimension(pk, 12 * pe.diameters_per_module(pk))
    assert r["totals"] == d["totals"]
    api_cornice = next(a for a in r["assemblies"] if a["id"] == "cornice")["members"]
    eng_cornice = next(a for a in d["assemblies"] if a["id"] == "cornice")["members"]
    assert [(m["id"], m["height_in"]) for m in api_cornice] == \
           [(m["id"], m["height_in"]) for m in eng_cornice]


def test_authorities_at_common_diameter(client):
    r = client.get("/api/authorities/doric", params={"column_diameter": 12}).json()
    assert r["at_common_column_diameter_in"] == 12
    assert len(r["authorities"]) == 5
    assert [a["authority"] for a in r["authorities"]] == \
           ["vignola", "palladio", "gibbs", "chambers", "benjamin"]


def test_style_record_all_sections(client):
    r = client.get("/api/styles/tidewater-georgian",
                   params={"sections": "summary,description,characteristics,lineage,"
                           "proportion,massing,constraints,exemplars,sources"}).json()
    for k in ("diagnostic_tells", "distinguished_from", "constraints", "exemplars",
              "sources", "massing_affinities", "proportion_packs"):
        assert k in r, k


def test_judgment_constraints_stay_distinct(client):
    # georgian-colonial-american carries a scope:judgment constraint; the record must
    # let the client keep the three states apart (test present / absent / judgment)
    r = client.get("/api/styles/georgian-colonial-american",
                   params={"sections": "constraints"}).json()
    scopes = {c.get("scope") for c in r["constraints"]}
    assert "judgment" in scopes
    j = [c for c in r["constraints"] if c["scope"] == "judgment"]
    assert all("test" not in c or not c["test"] for c in j)
