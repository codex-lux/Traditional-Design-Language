#!/usr/bin/env python3
"""family_source_hazard.py -- what a higher-rank node's source list must and must not contain.

WP-11.7. Authoring a family's literature can REDDEN THE BUILD in TWO ways, and the second one
inverts the advice the package was planned with. `check_research.py` builds `cited_by` over ALL 164
nodes and marks a node `shared_only` when EVERY one of its sources is cited by somebody else;
`RATCHET["shared_only_nodes"]` is a ceiling of 24 run `--strict` by `check_all.py`.

  1. THE OTHER NODE. Citing, on a family, the one work that is some buildable node's ONLY unique
     citation flips THAT node into `shared_only`. 38 strings are hazardous this way.

  2. THE NODE ITSELF, AND THIS IS THE BIGGER ONE. `per` is computed over all 164 nodes, families
     included, so a family whose sources are ALL works the corpus already cites becomes
     `shared_only` ITSELF. Measured: giving `english-classical` a single already-shared source
     (Summerson, 10 nodes) took `--strict` from green to RED on the first run.

     THE PLAN SAID THE OPPOSITE. It read "prefer a work the corpus already cites -- 95 strings are
     pre-vetted and automatically safe", which is exactly backwards, and no amount of re-reading
     would have shown it: it died the first time the mutation was applied and the real checker run.
     The meter is right and the protocol was wrong. A family that cites only what its members
     already cite has done no research of its own, which is precisely what `shared_only` exists to
     say.

SO THE RULE IS A PROPERTY OF THE LIST, NOT OF A STRING: every higher-rank node needs AT LEAST ONE
work that, in the finished corpus, no other node cites -- and no string from the hazard set.

    python3 build/family_source_hazard.py                       # the 38 strings nobody may cite
    python3 build/family_source_hazard.py --check <node>        # judge a node's list as it stands
    python3 build/family_source_hazard.py --sweep               # judge every higher-rank node
"""
import argparse
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDABLE = ("style", "variant")
HIGHER = ("family", "tradition")


def load_nodes():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        out[d["id"]] = d
    return out


def cited_by(nodes):
    """How many nodes cite each string, over ALL ranks -- the population `check_research.measure`
    counts. A guard reading a different population is a guard about a different corpus, which is
    how the first version of this file came to give the opposite advice."""
    c = collections.Counter()
    for d in nodes.values():
        for s in d.get("sources") or []:
            c[s.strip()] += 1
    return c


def shared_only(nodes, counts=None):
    """Every node -- ANY rank -- whose every source is cited by somebody else. Mirrors
    check_research.py's `shared_only` exactly, including that families are in the population."""
    counts = cited_by(nodes) if counts is None else counts
    out = set()
    for i, n in nodes.items():
        srcs = [s.strip() for s in (n.get("sources") or [])]
        if srcs and all(counts[s] > 1 for s in srcs):
            out.add(i)
    return out


def hazards(nodes=None):
    """source string -> the buildable node it would flip, if a second node cited it."""
    nodes = load_nodes() if nodes is None else nodes
    counts = cited_by(nodes)
    already = shared_only(nodes, counts)
    out = {}
    for i, n in nodes.items():
        if n.get("rank") not in BUILDABLE or i in already:
            continue
        uniq = [s.strip() for s in (n.get("sources") or []) if counts[s.strip()] == 1]
        if len(uniq) == 1:
            out[uniq[0]] = i
    return out


def judge_list(node_id, proposed, nodes=None):
    """(verdict, reasons) for a whole proposed source list on one higher-rank node.
    Three verdicts, never a bool: `ok` / `unsafe` / `could-not-judge`."""
    nodes = load_nodes() if nodes is None else nodes
    if node_id not in nodes:
        return "could-not-judge", ["no such node: %s" % node_id]
    srcs = [s.strip() for s in proposed if s and s.strip()]
    if not srcs:
        return "could-not-judge", ["no sources proposed; a node citing nothing is the gap, not a flip"]

    haz = hazards(nodes)
    counts = cited_by(nodes)
    # the corpus AS IT WOULD BE with this list in place
    after = collections.Counter(counts)
    for s in set(srcs) - set(x.strip() for x in (nodes[node_id].get("sources") or [])):
        after[s] += 1

    why = []
    bad = [s for s in srcs if s in haz]
    for s in bad:
        why.append("UNSAFE: flips %s -- that node's only unique citation" % haz[s])
    own = [s for s in srcs if after[s] == 1]
    if not own:
        why.append("UNSAFE: every source is cited by another node, so %s becomes `shared_only` "
                   "itself. At least one work must be this node's alone." % node_id)
    else:
        why.append("holds %d source(s) no other node cites: %s" % (len(own), "; ".join(x[:60] for x in own)))
    return ("unsafe" if bad or not own else "ok"), why


def set_sources(node_id, proposed, nodes=None):
    """Write a higher-rank node's `sources`, REFUSING an unsafe list rather than landing it.

    The writer enforces the guard on purpose. Tranche 4 WAS authored by six parallel agents, and a
    rule that lives only in a prompt is a rule six agents can each read differently; a rule in the
    one function that writes the field is a rule none of them can get past. Returns (written,
    verdict, reasons).

    `sources` is placed directly after `exemplars`, which is where a buildable node carries it, and
    every other key keeps its position so the diff is the field and nothing else."""
    nodes = load_nodes() if nodes is None else nodes
    n = nodes.get(node_id)
    if n is None:
        return False, "could-not-judge", ["no such node: %s" % node_id]
    if n.get("rank") not in HIGHER:
        return False, "could-not-judge", [
            "%s is rank %r; this writer is for families and traditions. A buildable node's sources "
            "are authored with its own research, not here." % (node_id, n.get("rank"))]
    srcs = [s.strip() for s in proposed if s and s.strip()]
    if len(set(srcs)) != len(srcs):
        return False, "unsafe", ["the list repeats a source; each work is named once"]

    verdict, why = judge_list(node_id, srcs, nodes)
    if verdict != "ok":
        return False, verdict, why

    path = os.path.join(ROOT, "styles", "%s.json" % node_id)
    doc = json.load(open(path, encoding="utf-8"))
    out, placed = {}, False
    for k, v in doc.items():
        if k == "sources":
            continue
        out[k] = v
        if k == "exemplars":
            out["sources"] = srcs
            placed = True
    if not placed:
        out["sources"] = srcs
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return True, verdict, why


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    a.add_argument("--check", metavar="NODE", help="judge this node's sources as they stand")
    a.add_argument("--sweep", action="store_true", help="judge every family and tradition")
    ns = a.parse_args(argv)
    nodes = load_nodes()

    if ns.check or ns.sweep:
        targets = [ns.check] if ns.check else sorted(
            i for i, n in nodes.items() if n.get("rank") in HIGHER)
        bad = 0
        for t in targets:
            srcs = (nodes.get(t) or {}).get("sources") or []
            v, why = judge_list(t, srcs, nodes)
            if v == "could-not-judge" and not srcs:
                # `check_research.RATCHET["sourceless_nodes"]` is pinned tight at 0, so no node
                # reaches this branch today and one that does is a regression rather than a
                # backlog. Said here because `check_counts.py` reads markdown and never opens
                # `build/*.py`: a claim printed by a checker is outside every guard in the tree.
                print("  %-34s CITES NOTHING -- a regression: the ceiling is 0" % t)
                continue
            print("  %-34s %s" % (t, v.upper()))
            for w in why:
                print("        %s" % w)
            bad += v == "unsafe"
        if bad:
            print("\n%d node(s) UNSAFE -- `check_research.py --strict` would break its ceiling." % bad)
        return 1 if bad else 0

    h = hazards(nodes)
    print("%d source string(s) no second node may cite; each is the single unique citation of the "
          "node named beside it." % len(h))
    for s, i in sorted(h.items(), key=lambda kv: kv[1]):
        print("  %-34s %s" % (i, s[:96]))
    print("\nAND every higher-rank node needs at least one work of its OWN -- a list made entirely "
          "of already-cited\nworks makes that node `shared_only` itself. Run --sweep after authoring.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # `| head` closes the pipe; a traceback there is a CLI convicting itself of a fault it does
        # not have -- the display half of the tri-state lesson (WP-10.1).
        os._exit(0)
