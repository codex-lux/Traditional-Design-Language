#!/usr/bin/env python3
"""Generate the wanted-asset manifest — the shot list.

An asset record is authored BEFORE the image exists. The record carries the meaning;
the file is swappable, and can be a sketch now and a HABS photograph later. Because the
alt_text is written to be reasoned from, an agent can use the record while the file is
still missing, and a photographer can shoot from it.

Sources of wanted records:
  forbidden variant   -> an incorrect/correct PAIR, which is the unit that does the teaching
  invented slot       -> a diagram, because there is no precedent to photograph
  code_conflict       -> a comparison of the period dimension against the code one
  proportion members  -> a measured detail, generated from the engine
"""
import json, os, glob, re, importlib.util, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
spec = importlib.util.spec_from_file_location("pe", "build/proportion_engine.py")
pe = importlib.util.module_from_spec(spec); spec.loader.exec_module(pe)

SLOTS = {}
for g in json.load(open("elements/slots.json"))["groups"]:
    for s in g["slots"]: SLOTS[s["id"]] = {**s, "group": g["id"], "group_name": g["name"]}
STYLES = {json.load(open(f))["id"]: json.load(open(f)) for f in sorted(glob.glob("styles/*.json"))}

HIGH_VALUE_GROUPS = {"openings", "envelope", "massing-and-roof", "threshold"}

def slug(*parts):
    s = "-".join(str(p) for p in parts).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)[:80].strip("-")

def take(seq, n): return seq[:n]

assets, pairs = [], 0
for kf in sorted(glob.glob("kits/*.kit.json")):
    kit = json.load(open(kf))
    sid = kit["style"]
    style = STYLES.get(sid)
    if not style: continue
    sname = style["name"]
    for slot_id, slot in (kit.get("slots") or {}).items():
        meta = SLOTS.get(slot_id, {})
        grp = meta.get("group", "")
        canon = next((v for v in slot.get("variants", []) if v.get("status") == "canonical"), None)
        rule = slot.get("rule") or meta.get("note") or ""

        for v in slot.get("variants", []):
            if v.get("status") != "forbidden": continue
            base = slug(sid, slot_id, v["id"])
            bad, good = f"{base}-wrong", f"{base}-right"
            pri = "critical" if slot.get("code_conflict") else ("high" if grp in HIGH_VALUE_GROUPS else "normal")
            why = v.get("note") or f"Forbidden in {sname}."
            assets.append({
                "id": bad, "kind": "photograph", "role": "incorrect", "pair_with": good,
                "depicts": {"nodes": [sid], "slots": [slot_id]},
                "caption": f"{sname}, {meta.get('name', slot_id).lower()}: {v.get('name') or v['id']} — wrong, and why.",
                "alt_text": (f"A {sname} house showing {meta.get('name', slot_id).lower()} executed as "
                             f"{(v.get('name') or v['id']).lower()}. This is the error condition. {why} "
                             f"The frame must be close enough that the {meta.get('name', slot_id).lower()} reads at full "
                             f"detail and wide enough to show what it sits against, so the viewer can see the mistake in context "
                             f"rather than as an abstraction.")[:1400],
                "shot_spec": {
                    "subject": f"{meta.get('name', slot_id)} on a {sname} house, executed wrongly as {v.get('name') or v['id']}",
                    "vantage": "square-on to the element, no perspective convergence on the horizontal lines",
                    "must_show": [f"the {meta.get('name', slot_id).lower()} in full", "enough adjacent wall or trim to judge scale",
                                  "the junction where the error is legible"],
                    "must_avoid": ["foliage or cars across the element", "heavy shadow across the profile", "wide-angle distortion"],
                    "lighting": "raking light so profile depth reads; overcast is acceptable for masonry, not for mouldings",
                    "scale_cue": "an adjacent door, sash, or brick course"
                },
                "provenance": {"license": "unknown"}, "file": None,
                "status": "wanted", "priority": pri,
                "tags": ["fault", grp, slot_id]
            })
            assets.append({
                "id": good, "kind": "photograph", "role": "correct", "pair_with": bad,
                "depicts": {"nodes": [sid], "slots": [slot_id]},
                "caption": f"{sname}, {meta.get('name', slot_id).lower()}: the same element done correctly.",
                "alt_text": (f"A {sname} house showing {meta.get('name', slot_id).lower()} executed correctly"
                             + (f", as {(canon.get('name') or canon['id']).lower()}" if canon else "")
                             + f". Shot to pair with {bad}: same vantage, same distance, same framing, so the two images "
                             f"differ only in the thing being taught. {rule}")[:1400],
                "shot_spec": {
                    "subject": f"{meta.get('name', slot_id)} on a {sname} house, correctly executed",
                    "vantage": "identical to the paired incorrect image — the pair is worthless if the framing differs",
                    "must_show": [f"the {meta.get('name', slot_id).lower()} in full", "the same adjacent context as the pair"],
                    "must_avoid": ["a different scale of building from the pair", "restoration work of doubtful accuracy"],
                    "lighting": "match the pair", "scale_cue": "match the pair"
                },
                "provenance": {"license": "unknown"}, "file": None,
                "status": "wanted", "priority": pri,
                "tags": ["exemplar", grp, slot_id]
            })
            pairs += 1

        if slot.get("invented"):
            assets.append({
                "id": slug(sid, slot_id, "diagram"), "kind": "line-diagram", "role": "diagram",
                "depicts": {"nodes": [sid], "slots": [slot_id]},
                "caption": f"{sname}, {meta.get('name', slot_id).lower()}: an authored position, not a retrieved one.",
                "alt_text": (f"A measured diagram of the {meta.get('name', slot_id).lower()} strategy proposed for {sname}. "
                             f"No historical precedent exists for this slot, so there is nothing to photograph and the drawing "
                             f"has to carry the argument. {rule} Dimensions must be shown, because the whole claim is that the "
                             f"proposal follows rules the style already contains.")[:1400],
                "shot_spec": {"subject": f"{meta.get('name', slot_id)} strategy diagram",
                              "vantage": "plan and street elevation together, at a stated scale",
                              "must_show": ["dimensions", "the relationship to the main block", "the street elevation consequence"],
                              "must_avoid": ["rendering that flatters the proposal", "omitting the car"],
                              "lighting": "n/a", "scale_cue": "a dimensioned bar and a figure"},
                "provenance": {"license": "owned"}, "file": None,
                "status": "wanted", "priority": "critical", "tags": ["invented", "judgment", slot_id]
            })

        for cc in slot.get("code_conflict", []) or []:
            assets.append({
                "id": slug(sid, slot_id, "code"), "kind": "detail-drawing", "role": "comparison",
                "depicts": {"nodes": [sid], "slots": [slot_id]},
                "caption": f"{sname}, {meta.get('name', slot_id).lower()}: the period dimension against the code minimum.",
                "alt_text": (f"A dimensioned comparison drawing. Period: {cc.get('period_value')}. Code: "
                             f"{cc.get('code_requirement')}{' (' + cc['code_ref'] + ')' if cc.get('code_ref') else ''}. "
                             f"Resolution: {cc.get('resolution')}. Both conditions drawn at the same scale and overlaid, "
                             f"so the size of the compromise is visible rather than argued.")[:1400],
                "provenance": {"license": "owned"}, "file": None,
                "status": "wanted", "priority": "critical", "tags": ["code-conflict", slot_id]
            })

# measured details generated by the engine — these can be produced without a camera
#
# EVERY PACK, not the five this list used to name. Those five were a sample from when the layer
# was authored, and nothing said so: the corpus holds 25 packs that dimension a base, a capital,
# a cornice or an entablature, and the other twenty were as drawable as these all along. 11
# records became 73.
#
# The ASSEMBLY filter below is left exactly as it was. It is an authored judgment about which
# assemblies earn a detail plate, and widening it to architrave and pedestal would add another
# 46 records and take this package past WP-4.4's "at least 100 sourced" acceptance line. Hitting
# an acceptance number by widening somebody else's filter is not the same as meeting it, so the
# figure is reported at 73 and the line is not met by profiles alone.
for pid in sorted(pe.PACKS):
    if pid not in pe.PACKS: continue
    pk = pe.resolve(pid)
    d = pe.dimension(pk, 12 * pe.diameters_per_module(pk))
    for asm in d["assemblies"]:
        if asm["id"] not in ("cornice", "capital", "base", "entablature"): continue
        assets.append({
            "id": slug(pid, asm["id"], "profile"), "kind": "detail-drawing", "role": "diagram",
            "depicts": {"packs": [pid], "members": [f"{pid}.{asm['id']}"]},
            "caption": f"{pk['name']}: {asm['id']} profile, {len(asm['members'])} members, {asm['height_in_stated']:.2f} in at a 12 in column.",
            "alt_text": (f"A measured section through the {asm['id']} of {pk['name']}, drawn at a 12 inch column diameter. "
                         f"Members bottom to top: " + ", ".join(f"{m['name']} ({m['height_parts']}p)" for m in take(asm['members'], 12)) +
                         ". Every dimension is generated by the proportion engine from the pack, so the drawing and the data "
                         "cannot silently disagree.")[:1400],
            "generated_from": {"pack": pid, "module_in": 12 * pe.diameters_per_module(pk),
                               "parameters": {"assembly": asm["id"]}, "engine_version": pe.ENGINE_VERSION},
            "provenance": {"source": (pk.get("authority") or {}).get("source"), "license": "owned"},
            "file": None, "status": "wanted", "priority": "high", "tags": ["profile", "generated", pid]
        })

os.makedirs("assets", exist_ok=True)

# THIS IS A GENERATOR OVER A FILE THREE OTHER TOOLS WRITE, AND IT USED TO OVERWRITE THEM ALL.
#
# Rebuilding from scratch silently discarded: WP-4.4's 161 hand-added `provenance.building` names
# (commit 347d0ab), the eleven `file` blocks and `sourced` statuses build/render_profile.py
# writes, the asset-to-fault links build/link_asset_faults.py derives, and anything
# build/harvest_habs.py --write ever recorded. Every one would have reset to `wanted` with no
# warning, in a 601 KB diff that reads as a reformat. Nothing caught it: this script is in
# neither build/check_all.py nor the Makefile, so the loss would have happened on somebody's
# laptop and arrived as a commit.
#
# The division is the whole of the fix. This generator OWNS what it can derive from the corpus --
# the record's identity, what it depicts, and the words describing the picture that should exist.
# It does NOT own what somebody or something else went and found out. Those are carried forward
# by id.
GENERATED_FIELDS = ("id", "kind", "role", "pair_with", "caption", "alt_text", "shot_spec",
                    "priority", "tags", "generated_from")
CARRIED_FIELDS = ("provenance", "file", "status", "review_note")

prior = {}
if os.path.exists("assets/manifest.json"):
    try:
        prior = {a["id"]: a for a in json.load(open("assets/manifest.json")).get("assets", [])}
    except Exception as e:                      # a corrupt file must not silently become an empty one
        raise SystemExit("assets/manifest.json exists but could not be read (%s). Refusing to "
                         "regenerate over it: that would discard whatever it holds." % e)

carried = 0
for a in assets:
    old_rec = prior.get(a["id"])
    if not old_rec:
        continue
    for k in CARRIED_FIELDS:
        if k in old_rec and old_rec[k] not in (None, {}, ""):
            a[k] = old_rec[k]
            carried += 1
    # `depicts` is generated, but its `faults` array is derived by link_asset_faults.py and is
    # not this script's to know.
    prior_faults = (old_rec.get("depicts") or {}).get("faults")
    if prior_faults:
        a.setdefault("depicts", {})["faults"] = prior_faults
        carried += 1

by_status = {}
for a in assets:
    by_status[a["status"]] = by_status.get(a["status"], 0) + 1

manifest = {"schema": "schema/asset.schema.json", "version": "0.1.0",
            "counts": {"total": len(assets), "pairs": pairs,
                       "by_priority": {p: sum(1 for a in assets if a["priority"] == p) for p in ("critical","high","normal","low")},
                       "by_status": by_status},
            "note": "A record is WANTED until a file lands: specified, with a shot spec and alt text. "
                    "That is the design — the gap is visible, the shot list exists, and an agent can already reason "
                    "from the record. `sourced` means a file is present and unreviewed; `approved` means a human has "
                    "checked it. build/gen_assets.py regenerates the specification and CARRIES FORWARD provenance, "
                    "file, status, review_note and depicts.faults, which it does not own.",
            "assets": assets}
json.dump(manifest, open("assets/manifest.json", "w"), indent=2, ensure_ascii=False)
print(f"carried forward {carried} field(s) this generator does not own")

import jsonschema
sch = json.load(open("schema/asset.schema.json"))
bad = 0
for a in assets:
    try: jsonschema.validate(a, sch)
    except jsonschema.ValidationError as e:
        print("  x", a["id"], e.message); bad += 1
# "N wanted records" was printed for every record whatever its status, which stopped being true
# the moment anything was sourced -- the summary line said 1,850 wanted while 73 had files.
_status_line = ", ".join(f"{n} {k}" for k, n in sorted(by_status.items()))
print(f"assets: {len(assets)} records ({_status_line}), {pairs} good/bad pairs, {bad} invalid")
print(f"by priority: {manifest['counts']['by_priority']}")
