#!/usr/bin/env python3
"""family_specimens.py -- a family's type specimens, DERIVED from its members' icons.

WP-11.6, executing Ruling B (5 Sep 2026): *"Families carry type specimens, DERIVED from members'
`standing: icon` exemplars -- a report of the members, not a second authoring. The 5 traditions stay
empty."* Cardinality ruled the same day: ONE PER MEMBER NODE, deduplicated by building.

**THIS FILE EXISTS SO THE DERIVATION CAN BE RE-RUN, AND THAT IS THE WHOLE POINT.** A derived record
nothing can re-derive is a snapshot, and a snapshot of somebody else's judgment goes stale the
moment that judgment moves -- `oq/a-baked-pack-value-is-a-second-delivery-path` is the same shape
one layer down. A member that changes which building it calls its icon changes what its family
stands for, and `check_precedents.py` fails the build when the two disagree.

The `why` REPORTS and does not restate. It names the member and points at that node for the reason
rather than copying the member's own sentence, because a copied sentence is a second spelling that
drifts from the one it came from -- the defect this repository has met in `required_wall_ft`, in the
citation grammar and in the riser divisor. Nothing new is asserted about any building here.

Run `python3 build/family_specimens.py` to see the drift; `--apply` to write it.
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLES = os.path.join(ROOT, "styles")

# Styles before their own variants, ids ascending -- a stable order, so a re-derivation on an
# unchanged corpus is byte-identical and a diff means something moved.
RANK_ORDER = {"style": 0, "variant": 1}

WHY = ("Derived, not authored: `%s`, a %s of this family, names it its icon, and the reason for "
       "that judgment is recorded on that node rather than restated here.")


def load_nodes():
    out = {}
    for f in sorted(glob.glob(os.path.join(STYLES, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        out[d["id"]] = (f, d)
    return out


def members_of(nodes, fid):
    """Every descendant through `member_of`, in the reading order above. A family's members are its
    styles and their variants; `member_of` is the rank tree and not the lineage DAG, which is the
    right edge here -- Ruling B says a family reports ITS MEMBERS, not everything it influenced."""
    kids = collections.defaultdict(list)
    for nid, (_, d) in nodes.items():
        if d.get("member_of"):
            kids[d["member_of"]].append(nid)

    def walk(n):
        out = []
        for k in sorted(kids.get(n, [])):
            out.append(k)
            out += walk(k)
        return out

    mem = walk(fid)
    mem.sort(key=lambda m: (RANK_ORDER.get(nodes[m][1].get("rank"), 9), m))
    return mem


def derive(nodes=None):
    """family id -> the exemplar rows it should carry. Pure: reads, never writes."""
    nodes = load_nodes() if nodes is None else nodes
    out = {}
    for fid in sorted(nid for nid, (_, d) in nodes.items() if d.get("rank") == "family"):
        rows, taken = [], set()
        for m in members_of(nodes, fid):
            _, mn = nodes[m]
            for ex in mn.get("exemplars") or []:
                if ex.get("standing") != "icon":
                    continue
                pid = ex.get("precedent")
                key = pid or ("%s|%s" % (ex["name"], ex.get("location", "")))
                if key in taken:
                    continue                     # this building already stands for an earlier member
                taken.add(key)
                row = {"name": ex["name"]}
                if ex.get("location"):
                    row["location"] = ex["location"]
                if ex.get("year") is not None:
                    row["year"] = ex["year"]
                if pid:
                    row["precedent"] = pid
                row["standing"] = "canonical"
                row["why"] = WHY % (m, mn.get("rank", "member"))
                rows.append(row)
                break                            # ONE PER MEMBER NODE -- the ruled cardinality
        out[fid] = rows
    return out


def nodes_gained(nodes=None):
    """precedent id -> the family ids that must appear in its `nodes[]`. `check_precedents.py`
    holds an exemplar's `precedent` against the record's own `nodes`, in both directions, so a
    specimen the record does not claim is a dangling reference."""
    nodes = load_nodes() if nodes is None else nodes
    out = collections.defaultdict(set)
    for fid, rows in derive(nodes).items():
        for r in rows:
            if r.get("precedent"):
                out[r["precedent"]].add(fid)
    return out


def drift(nodes=None):
    """(family id, 'expected'/'found' summary) for every family whose stored rows are not the
    derived ones. Empty is the only passing state."""
    nodes = load_nodes() if nodes is None else nodes
    bad = []
    for fid, want in derive(nodes).items():
        got = nodes[fid][1].get("exemplars") or []
        if got != want:
            bad.append((fid, len(want), len(got)))
    return bad



def _write_atomic(path, doc):
    """Write a corpus record the way `build.py` writes a kit: beside it, then rename.

    `open(path, "w")` TRUNCATES first, so a process killed mid-write leaves the record truncated on
    disk. `build.py:54` fixed exactly this on 28 Aug 2026 -- "corpus data loss from a command whose
    job is to regenerate, not to destroy" -- and the fix was never generalised, so both writers
    added since carried it back in. These files are worse than the kits build.py was protecting:
    a kit regenerates, an authored `precedents/` record does not. os.replace is atomic within a
    filesystem."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def apply(nodes=None):
    nodes = load_nodes() if nodes is None else nodes
    want = derive(nodes)
    written = 0
    for fid, rows in want.items():
        path, fam = nodes[fid]
        if (fam.get("exemplars") or []) == rows:
            continue
        fam["exemplars"] = rows
        _write_atomic(path, fam)
        written += len(rows)
    added = 0
    for pid, fids in sorted(nodes_gained(nodes).items()):
        path = os.path.join(ROOT, "precedents", pid + ".json")
        rec = json.load(open(path, encoding="utf-8"))
        ns = list(rec.get("nodes") or [])
        new = [f for f in sorted(fids) if f not in ns]
        if not new:
            continue
        rec["nodes"] = ns + new
        _write_atomic(path, rec)
        added += len(new)
    return written, added


def main(argv):
    nodes = load_nodes()
    want = derive(nodes)
    total = sum(len(v) for v in want.values())
    if "--apply" in argv:
        w, a = apply(nodes)
        print("family specimens: %d row(s) written over %d families; %d family name(s) added to "
              "precedent records." % (w, len(want), a))
        return 0
    for fid in sorted(want):
        print("%-35s %3d specimen(s)" % (fid, len(want[fid])))
    d = drift(nodes)
    print("\n%d specimen(s) over %d families, from %d member icons."
          % (total, len(want), total))
    if d:
        print("DRIFT: %d famil(y/ies) do not carry their derived specimens: %s"
              % (len(d), ", ".join("%s (want %d, have %d)" % x for x in d)))
        return 1
    print("every family carries exactly its derived specimens.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
