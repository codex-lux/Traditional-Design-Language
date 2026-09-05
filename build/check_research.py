#!/usr/bin/env python3
"""check_research.py -- how deep the research under each style node goes, measured rather than read.

WP-11.1 (4 Sep 2026). The corpus WAS TEMPLATED on the surface: all 132 buildable nodes carried 2-4
exemplars (90 exactly 4), 4 or 5 sources, exactly 5 constraints and 3 `distinguished_from`, and a
composite of those spread only 1.5x across the whole set. The exemplar clause is a record of what
was found and not a description of today -- WP-11.2 and WP-11.3 took it to 693 exemplars, 3 to 9 a
node -- and the other three clauses are unmoved, which is why the finding stands. Field counts cannot separate a
thoroughly researched node from a skeletal one, and no checker in this tree ever tried. Four
measures DO separate them, and this file computes every one on every run:

  * exemplars carrying a `precedent` -- a locator a checker can resolve (`precedents/`).
  * NODE-SPECIFIC source share. A node whose every cited work is also cited by a sibling was
    written from the survey literature alone; 24 nodes were, on the first run, and the composite
    scores them HIGHER because they cite five books.
  * `measured` kit parameters with no source on the parameter AND none on the slot -- the
    provenance census in check_kits.py counts editorial-bare (0) and had never counted this
    (542), which is the class VISION.md calls the worst thing that can be done to the corpus,
    metered on the other kind. Split again by whether a GENERATOR READS the slot: a figure on a
    slot nothing reads changes what the system says; one on a slot the elevation draws from
    changes the house.
  * constraints that carry a test against those that are `scope: judgment` -- three nodes have
    no executable constraint at all.

THE GENERATOR-READ SLOT SET IS DERIVED, AND IT IS AN UPPER BOUND. No constant lists which slots the
generators read: `elevation.py` resolves the whole kit and then reads by name. So this file walks
the generators' and the critic's ASTs for string constants that are ontology slot ids. A slot
named in a comment string or an error message counts as read, which over-states; a slot read
through a variable does not, which under-states. The set is printed and pinned by equality in a
test so a change is NOTICED, never forbidden. `measured_unsourced_read` therefore falls "for free"
if a generator stops reading a slot, and the test is what makes that visible.

Ratchets in the check_grouping_rules.py shape: ceilings that may only fall, floors that may only
rise, and named sets pinned in tests/test_research.py so a count cannot hide a swap.
"""
import argparse
import ast
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COULD_NOT_EVALUATE = 3

# The files a slot id may be read in to count as "read by a generator or the critic". elevation,
# roof, structure and storeys draw the house; compose, geometry, openings and arrangement place it;
# plan_check and critique judge it; moves edits it. plan_check is INCLUDED because a slot the
# critic reads is one whose figure returns a verdict, which is the other half of "changes what the
# machine does".
GENERATOR_FILES = ("elevation.py", "roof.py", "structure.py", "storeys.py", "compose.py", "geometry.py",
                   "geometry_cp.py", "openings.py", "arrangement.py", "plan_check.py", "critique.py",
                   "moves.py", "revise.py")

# Measured 4 Sep 2026 and thereafter may only improve. Read the entries before moving one.
#
#   measured_unsourced 542       `kind: measured` with no `source` on the parameter and no
#                                `sources[]` on its slot. Falls when somebody SOURCES one; never
#                                by re-kinding it `editorial` in bulk, which destroys the claim
#                                that it was measured (and moves test_provenance's 202).
#   measured_unsourced_read 272  The subset on a slot the generators or the critic read. A hand
#                                list of 31 slots gave 230; the AST walk finds 35 and 272, and
#                                the instrument's figure is the one pinned.
#   editorial_read 69            Editorial parameters on a read slot (the hand list said 55).
#   shared_only_nodes 24         Nodes whose every source is shared with another node.
#   untested_nodes 3             Nodes with constraints and not one carrying a test.
#   exemplars_with_precedent 171 A FLOOR: exemplars naming a `precedents/` record.
#   nodes_with_a_precedent 27    A FLOOR.
RATCHET = {
    "measured_unsourced": 542,
    "measured_unsourced_read": 272,
    "editorial_read": 69,
    "shared_only_nodes": 24,
    "untested_nodes": 3,
    "exemplars_with_precedent": 505,    # FLOOR -- may only RISE (4 at seeding; Tranche 1 landed 171,
                                        # Tranche 2 505 -- WP-11.3, North America complete)
    "nodes_with_a_precedent": 86,       # FLOOR -- may only RISE (3 at seeding, 27 after Tranche 1)
}
FLOORS = ("exemplars_with_precedent", "nodes_with_a_precedent")


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def ontology_slots():
    sd = _load(os.path.join(ROOT, "elements", "slots.json"))
    return {s["id"] for g in sd["groups"] for s in g["slots"]}


def generator_read_slots():
    """slot id -> the generator files whose source carries it as a string constant. An UPPER
    BOUND; see the module docstring."""
    ont = ontology_slots()
    found = collections.defaultdict(set)
    for name in GENERATOR_FILES:
        p = os.path.join(ROOT, "build", name)
        if not os.path.exists(p):
            continue
        tree = ast.parse(open(p, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in ont:
                found[node.value].add(name)
    return dict(found)


def pack_strengths():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = _load(p)
        out[d.get("id")] = (d.get("authority") or {}).get("strength", "unstated")
    return out


def measure():
    """Everything a ratchet, a test or check_counts.py reads. Pure."""
    styles = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = _load(p)
        styles[d["id"]] = d
    kits = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        d = _load(p)
        kits[d["style"]] = d
    strengths = pack_strengths()
    read = generator_read_slots()

    cited_by = collections.Counter()
    for d in styles.values():
        for s in d.get("sources") or []:
            cited_by[s] += 1

    per = {}
    for nid, d in styles.items():
        ex = d.get("exemplars") or []
        srcs = d.get("sources") or []
        cons = d.get("constraints") or []
        row = {
            "rank": d.get("rank"),
            "confidence": d.get("confidence"),
            "exemplars": len(ex),
            "exemplars_with_precedent": sum(1 for e in ex if e.get("precedent")),
            "exemplars_with_standing": sum(1 for e in ex if e.get("standing")),
            "sources": len(srcs),
            "sources_unique": sum(1 for s in srcs if cited_by[s] == 1),
            "shared_only": bool(srcs) and all(cited_by[s] > 1 for s in srcs),
            "constraints": len(cons),
            "judgment": sum(1 for c in cons if c.get("scope") == "judgment"),
            "tested": sum(1 for c in cons if c.get("test")),
            "packs_bound": len(d.get("proportion_packs") or []),
            "pack_strength": collections.Counter(
                strengths.get(b.get("pack"), "unknown") for b in d.get("proportion_packs") or []),
            "kit": nid in kits,
            "kit_params": 0, "measured": 0, "measured_unsourced": 0, "measured_unsourced_read": 0,
            "editorial": 0, "editorial_read": 0,
        }
        kit = kits.get(nid)
        if kit:
            for sid, s in (kit.get("slots") or {}).items():
                slot_sourced = bool(s.get("sources"))
                for pk, pv in (s.get("parameters") or {}).items():
                    if not isinstance(pv, dict):
                        continue
                    row["kit_params"] += 1
                    k = pv.get("kind")
                    if k == "measured":
                        row["measured"] += 1
                        if not pv.get("source") and not slot_sourced:
                            row["measured_unsourced"] += 1
                            if sid in read:
                                row["measured_unsourced_read"] += 1
                    elif k == "editorial":
                        row["editorial"] += 1
                        if sid in read:
                            row["editorial_read"] += 1
        per[nid] = row

    tot = collections.Counter()
    for k in ("exemplars", "exemplars_with_precedent", "exemplars_with_standing", "kit_params",
              "measured", "measured_unsourced", "measured_unsourced_read", "editorial", "editorial_read"):
        tot[k] = sum(r[k] for r in per.values())
    tot["nodes"] = len(per)
    tot["nodes_with_a_precedent"] = sum(1 for r in per.values() if r["exemplars_with_precedent"])
    tot["sourceless_nodes"] = sorted(n for n, r in per.items() if r["sources"] == 0)
    tot["shared_only_nodes"] = sorted(n for n, r in per.items() if r["shared_only"])
    tot["untested_nodes"] = sorted(n for n, r in per.items() if r["constraints"] and r["tested"] == 0)
    tot["zero_param_kits"] = sorted(n for n, r in per.items() if r["kit"] and r["kit_params"] == 0)
    tot["no_kit_nodes"] = sorted(n for n, r in per.items() if not r["kit"])
    tot["read_slots"] = sorted(read)
    tot["distinct_sources"] = len(cited_by)
    tot["pack_strengths"] = collections.Counter(strengths.values())
    return {"per_node": per, "totals": tot}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true", help="a broken ratchet fails")
    ap.add_argument("--node", help="print one node's row and stop")
    ap.add_argument("--table", action="store_true", help="print every buildable node's row")
    a = ap.parse_args()

    m = measure()
    per, tot = m["per_node"], m["totals"]

    if a.node:
        print(json.dumps({a.node: per.get(a.node)}, indent=1, default=lambda o: dict(o)))
        return 0

    print("research depth over %d nodes: %d exemplars, %d with a `precedent` (%d nodes), %d with a standing; "
          "%d distinct sources." % (tot["nodes"], tot["exemplars"], tot["exemplars_with_precedent"],
                                    tot["nodes_with_a_precedent"], tot["exemplars_with_standing"],
                                    tot["distinct_sources"]))
    print("  kit parameters: %d, of which %d measured; %d measured with NO SOURCE on the parameter or "
          "its slot, %d of those on a slot a generator or the critic reads; %d editorial, %d on a read slot."
          % (tot["kit_params"], tot["measured"], tot["measured_unsourced"], tot["measured_unsourced_read"],
             tot["editorial"], tot["editorial_read"]))
    print("  generator-read slots (an UPPER BOUND, from string constants in %s): %d of %d: %s"
          % (", ".join(GENERATOR_FILES), len(tot["read_slots"]), len(ontology_slots()), " ".join(tot["read_slots"])))
    print("  pack authority strengths: %s." % ", ".join("%s %d" % kv for kv in sorted(tot["pack_strengths"].items())))
    print("  %d node(s) cite no source (all higher rank): %s" % (len(tot["sourceless_nodes"]), " ".join(tot["sourceless_nodes"])))
    print("  %d node(s) cite only works a sibling also cites: %s" % (len(tot["shared_only_nodes"]), " ".join(tot["shared_only_nodes"])))
    print("  %d node(s) carry constraints and not one with a test: %s" % (len(tot["untested_nodes"]), " ".join(tot["untested_nodes"])))
    print("  %d kit(s) with zero parameters: %s" % (len(tot["zero_param_kits"]), " ".join(tot["zero_param_kits"])))
    print("  %d node(s) with no kit file: %s" % (len(tot["no_kit_nodes"]), " ".join(tot["no_kit_nodes"])))

    worst = sorted((r["measured_unsourced_read"], n) for n, r in per.items() if r["measured_unsourced_read"])
    print("  most unsourced measured figures on read slots: %s"
          % ", ".join("%s %d" % (n, c) for c, n in sorted(worst, reverse=True)[:12]))

    if a.table:
        print("\n%-40s %-9s ex prec src uniq cons tst jdg kit  meas unsrc read edit" % ("node", "rank"))
        for n, r in sorted(per.items(), key=lambda kv: (kv[1]["rank"] not in ("style", "variant"), -kv[1]["measured_unsourced_read"], kv[0])):
            print("%-40s %-9s %2d %4d %3d %4d %4d %3d %3d %4d %5d %5d %4d %4d" % (
                n, r["rank"], r["exemplars"], r["exemplars_with_precedent"], r["sources"], r["sources_unique"],
                r["constraints"], r["tested"], r["judgment"], r["kit_params"], r["measured"],
                r["measured_unsourced"], r["measured_unsourced_read"], r["editorial"]))

    failed = []
    got = {
        "measured_unsourced": tot["measured_unsourced"],
        "measured_unsourced_read": tot["measured_unsourced_read"],
        "editorial_read": tot["editorial_read"],
        "shared_only_nodes": len(tot["shared_only_nodes"]),
        "untested_nodes": len(tot["untested_nodes"]),
        "exemplars_with_precedent": tot["exemplars_with_precedent"],
        "nodes_with_a_precedent": tot["nodes_with_a_precedent"],
    }
    for key, pin in RATCHET.items():
        if key in FLOORS:
            if got[key] < pin:
                failed.append("%s FELL: %d -> %d; fewer exemplars resolve, which is not more research" % (key, pin, got[key]))
        elif got[key] > pin:
            failed.append("%s: %d -> %d" % (key, pin, got[key]))
    if failed:
        print("\nRATCHET BROKEN — " + "; ".join(failed))
    if a.strict:
        return 1 if failed else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
