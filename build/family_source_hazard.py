#!/usr/bin/env python3
"""family_source_hazard.py -- what a higher-rank node's source list must and must not contain.

WP-11.7. Authoring a family's literature can REDDEN THE BUILD in TWO ways, and the second one
inverts the advice the package was planned with. `check_research.py` builds `cited_by` over ALL 164
nodes and marks a node `shared_only` when EVERY one of its sources is cited by somebody else;
`RATCHET["shared_only_nodes"]` is a ceiling of 24 run `--strict` by `check_all.py`.

  1. THE OTHER NODE. Citing, on a family, the one work that is some buildable node's ONLY unique
     citation flips THAT node into `shared_only`. Run the tool with no arguments for the
     live list; the count is NOT written here, because a corpus figure inside `build/*.py`
     is outside every CLAIM in `check_counts.py`, which reads markdown only (WP-8.14).

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

    python3 build/family_source_hazard.py                       # the strings nobody may cite
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
    how the first version of this file came to give the opposite advice.

    IT DOES NOT STRIP, AND THAT IS THE POINT RATHER THAN AN OVERSIGHT. `check_research.py:160`
    counts `cited_by[s] += 1` on the raw string; this counted `s.strip()`, so a source carrying
    whitespace would be MERGED here and counted apart there, and the two modules would disagree
    about `shared_only` while every test stayed green -- 0 strings in the corpus need stripping
    today, so they agreed by luck and not by construction. The untrusted side is the human-typed
    PROPOSED list, and that is where `judge_list` and `set_sources` strip. One rule, counted one
    way, on the side that owns it."""
    c = collections.Counter()
    for d in nodes.values():
        for s in d.get("sources") or []:
            c[s] += 1
    return c


def shared_only(nodes, counts=None):
    """Every node -- ANY rank -- whose every source is cited by somebody else. Mirrors
    check_research.py's `shared_only` exactly, including that families are in the population."""
    counts = cited_by(nodes) if counts is None else counts
    out = set()
    for i, n in nodes.items():
        # NOT stripped, for the reason `cited_by` states: the corpus side is counted exactly as
        # check_research counts it, so the two cannot drift on a whitespace-carrying string.
        srcs = list(n.get("sources") or [])
        if srcs and all(counts[s] > 1 for s in srcs):
            out.add(i)
    return out


def hazards(nodes=None, ranks=None):
    """source string -> the node it would flip, if a second node cited it. ADVISORY ONLY: the
    verdict comes from `judge_list`, which simulates the whole corpus. This is the printed list.

    `ranks` DEFAULTS TO EVERY RANK, and it used to be hard-coded to BUILDABLE -- which is the same
    population mistake this module's own docstring says it was written to fix. `shared_only()` was
    corrected to run over all 164 nodes and this was left reading the buildable half, so the tool's
    headline ("N source strings no second node may cite") could not see the 32 nodes the package
    had just authored. Measured at the time: 38 printed against a true 40, and the two missing were
    `northern-european-vernacular`'s *Nightlands* and `mid-century-traditional`'s Clark 1986 -- the
    two nodes the package's own report names as holding exactly one work of their own. The tool
    built to stop somebody reddening the ceiling would have told them those strings were safe.

    Pass `ranks=BUILDABLE` when the population must EXCLUDE the nodes under test -- the sweep in
    `tests/test_research.py` does, because a hazard set derived from the same nodes it is checking
    is a set defined to exclude its own violations."""
    nodes = load_nodes() if nodes is None else nodes
    counts = cited_by(nodes)
    already = shared_only(nodes, counts)
    out = {}
    for i, n in nodes.items():
        if (ranks is not None and n.get("rank") not in ranks) or i in already:
            continue
        uniq = [s for s in (n.get("sources") or []) if counts[s] == 1]
        if len(uniq) == 1:
            out[uniq[0]] = i
    return out


def judge_list(node_id, proposed, nodes=None):
    """(verdict, reasons) for a whole proposed source list on one higher-rank node.
    Three verdicts, never a bool: `ok` / `unsafe` / `could-not-judge`.

    THE VERDICT IS A SIMULATION OF THE WHOLE CORPUS, NOT A LOOKUP OF 38 STRINGS. The first version
    tested each proposed string against `hazards()` and had three holes, all found by an audit
    reverting the code rather than reading it:

      * `hazards()` admits only BUILDABLE victims, so a higher-rank node's only unique work was
        never in the set. Measured: citing `northern-european-vernacular`'s sole unique work
        (Norberg-Schulz, *Nightlands*) from another family was judged `ok`, and taking that advice
        put `shared_only` at 26 against a ceiling of 24. The package's own report names that node
        as having zero headroom, and the guard written in the same commit could not see it.
      * A victim with TWO unique works was invisible, because neither string alone is a hazard.
        Cite both and it flips anyway -- **43 buildable nodes** were exposed this way.
      * A repeated string counted twice toward "works of its own", so a duplicated list read `ok`
        while `cited_by` counted the node as citing one work twice.

    All three are one mistake: the invariant is a property of the CORPUS AFTER THE WRITE, and it
    was being approximated string by string. So build the corpus as it would be and re-run
    `shared_only` -- the same function `check_research` agrees with -- and refuse if anybody is
    `shared_only` who was not before, or if this node would be. The docstring at the top of this
    file always said "THE RULE IS A PROPERTY OF THE LIST, NOT OF A STRING"; this is that sentence
    implemented. `hazards()` stays as the CLI's advisory listing of the commonest way to trip it.

    The rank gate lives here rather than only in `set_sources`, because `--check` reads this and
    printed "UNSAFE ... `--strict` would break its ceiling" for buildable nodes that are ALREADY
    ratcheted `shared_only` and perfectly green."""
    nodes = load_nodes() if nodes is None else nodes
    if node_id not in nodes:
        return "could-not-judge", ["no such node: %s" % node_id]
    if nodes[node_id].get("rank") not in HIGHER:
        return "could-not-judge", [
            "%s is rank %r. This rule is about a family or a tradition citing what its members "
            "already cite; a buildable node's `shared_only` state is ratcheted, not judged here."
            % (node_id, nodes[node_id].get("rank"))]
    if proposed is None:
        return "could-not-judge", ["no list proposed (None); three verdicts, never a crash"]
    srcs = [s.strip() for s in proposed if s and s.strip()]
    if not srcs:
        return "could-not-judge", ["no sources proposed; a node citing nothing is the gap, not a flip"]

    why = []
    if len(set(srcs)) != len(srcs):
        # Caught BEFORE the simulation: a repeat would otherwise read as two citations of one work
        # and inflate the count of works the node holds alone.
        return "unsafe", ["the list repeats a source; each work is named once"]

    before = shared_only(nodes)
    after_nodes = {i: n for i, n in nodes.items()}
    after_nodes[node_id] = dict(nodes[node_id])
    after_nodes[node_id]["sources"] = srcs
    after = shared_only(after_nodes)

    flipped = sorted(after - before - {node_id})
    for i in flipped:
        why.append("UNSAFE: flips %s -- it would be left citing only works other nodes cite" % i)
    if node_id in after:
        why.append("UNSAFE: every source is cited by another node, so %s becomes `shared_only` "
                   "itself. At least one work must be this node's alone." % node_id)
    if not flipped and node_id not in after:
        counts = cited_by(after_nodes)
        own = [s for s in srcs if counts[s] == 1]
        why.append("holds %d source(s) no other node cites: %s"
                   % (len(own), "; ".join(x[:60] for x in own)))
    return ("unsafe" if (flipped or node_id in after) else "ok"), why


def set_sources(node_id, proposed, nodes=None, root=None):
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

    # BASENAME, and a seam. Two things this line lacked:
    #   * `node_id` reached a path join unsanitised. It must already be a key of `load_nodes()`, so
    #     it is a real node's `id` and `validate.py` pins id == basename -- not exploitable. But
    #     `mcp_server/core.py` says of its own join "THE ONLY WAY a caller-supplied id may become a
    #     path -- call this, never build the path yourself", and this was a fourth copy of it.
    #     `set_sources` has no CLI entry, so nothing proves the id was ever validated.
    #   * `root` is injectable because the READS all take a `nodes` dict and the WRITE did not, so
    #     the only way to exercise this function's write was to write to the real `styles/`. That
    #     is not theoretical: mutation-testing the refusals -- removing the gates that were keeping
    #     the writer away from the corpus -- destroyed authored research in three style files. A
    #     writer whose only test target is the live corpus is a writer whose tests are the hazard.
    path = os.path.join(root or ROOT, "styles", "%s.json" % os.path.basename(str(node_id)))
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
    # ATOMIC, as `build.py` writes a kit: open(path, "w") TRUNCATES first, so a process killed
    # mid-write leaves an authored `styles/*.json` truncated on disk -- and these are hand-authored
    # research, where build.py was only protecting a regenerable kit. Worse here than there: this
    # truncation happens AFTER the safety gate above has passed, so the failure reads as "the guard
    # approved the write and the write destroyed the record". Write beside it and rename;
    # os.replace is atomic within a filesystem. Same idiom as build.py, deliberately not a second
    # spelling of it.
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
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
        bad = unjudged = 0
        for t in targets:
            # A NODE THAT DOES NOT EXIST IS NOT A NODE CITING NOTHING, and the first version of
            # this loop could not tell them apart: it read `(nodes.get(t) or {})`, got `[]` for a
            # typo, and printed "CITES NOTHING -- a regression" for `--check no-such-node-xyz`,
            # exiting 0. That is a mistyped argument reported as corpus damage, and reported as
            # success -- both directions wrong at once, in the branch added to fix a different
            # spent claim. `judge_list` already returns the right reason; print it.
            if t not in nodes:
                print("  %-34s COULD NOT JUDGE -- no such node" % t)
                unjudged += 1
                continue
            srcs = nodes[t].get("sources") or []
            v, why = judge_list(t, srcs, nodes)
            print("  %-34s %s" % (t, v.upper().replace("-", " ")))
            for w in why:
                print("        %s" % w)
            if v == "unsafe":
                bad += 1
            elif v == "could-not-judge":
                unjudged += 1
        if bad:
            print("\n%d node(s) UNSAFE -- `check_research.py --strict` would break its ceiling." % bad)
        if unjudged:
            # Unjudged is not passed, and it is not failed either: it exits 2, the code
            # `check_all.py` uses for COULD NOT EVALUATE.
            print("\n%d node(s) COULD NOT BE JUDGED -- that is neither a pass nor a fault." % unjudged)
        return 1 if bad else (2 if unjudged else 0)

    h = hazards(nodes)
    print("%d source string(s) no second node may cite; each is the single unique citation of the "
          "node named beside it." % len(h))
    for s, i in sorted(h.items(), key=lambda kv: kv[1]):
        print("  %-34s %s" % (i, s[:96]))
    print("\nAND every higher-rank node needs at least one work of its OWN -- a list made entirely "
          "of already-cited\nworks makes that node `shared_only` itself. Run --sweep after authoring.")
    return 0


if __name__ == "__main__":
    # A BROKEN PIPE IS A COULD-NOT-EVALUATE AND EXITS 2, NEVER 0. The first version answered 0
    # whatever the run had found, so `--sweep | head` reported SUCCESS with nodes UNSAFE. The
    # comment cited WP-10.1's "a CLI convicting itself of a fault it does not have"; the inverse --
    # ACQUITTING itself of one it does have -- is the direction that matters, because a green exit
    # is the one a caller acts on. The pipe can close mid-loop, before the verdict exists, so this
    # cannot report the run's answer either: it reports that there is no answer, which is the third
    # state this project requires rather than a guess at one of the other two.
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(2)
