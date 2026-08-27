"""OQ 18 -- how much of this corpus is our own convention rather than a sourced fact.

The entry has carried a hand-counted figure since the migration and it went stale twice. It is
a real number about the corpus's standing, and a number that matters that much should not depend
on someone remembering to recount it. `build/check_kits.py` computes it on every run.

The figure that matters is not `editorial`. An editorial call with a note saying what it rests on
is the corpus working exactly as designed -- "sources or kind: editorial" is the rule, and the
second half is a legitimate answer. What cannot be defended is editorial with NEITHER a source
NOR a note: a number nobody can check and nobody said anything about.
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def census():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        for s in (json.load(open(p))["slots"] or {}).values():
            for pv in (s.get("parameters") or {}).values():
                if not isinstance(pv, dict): continue
                out[pv.get("kind")] = out.get(pv.get("kind"), 0) + 1
                if pv.get("kind") == "editorial" and not pv.get("source") and not pv.get("note"):
                    out["bare"] = out.get("bare", 0) + 1
    return out


def test_the_census_is_printed_by_the_checker_and_the_percentages_are_of_one_denominator():
    """`editorial-bare` shares the counter and is a SUBSET of `editorial`; summing every key
    would count those parameters twice and inflate the denominator every percentage uses."""
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_kits.py")],
                          cwd=ROOT, capture_output=True, text=True)
    line = next(l for l in proc.stdout.splitlines() if "parameters by provenance" in l)
    total = int(line.split("(")[1].split(" ")[0])
    c = census()
    assert total == sum(v for k, v in c.items() if k != "bare")
    assert "editorial with NEITHER a source NOR a note" in proc.stdout


def test_no_parameter_is_left_unlabelled():
    """A parameter with no `kind` is the worst case of all: it is not even claiming to be a
    guess."""
    assert census().get(None, 0) == 0


def test_the_one_editorial_number_the_corpus_already_sourced_now_cites_it():
    """Found by matching every unsourced editorial number against every numeric threshold its
    own style states -- on the constraint's expression NAME as well as its value. Of 166 such
    numbers this was the only match, which is itself the finding: the editorial numbers are
    genuinely unsourced, not sourced-and-uncited."""
    k = json.load(open(os.path.join(ROOT, "kits", "georgian-colonial-american.kit.json")))
    wt = k["slots"]["water_table"]["parameters"]["measured_band_in"]
    assert wt["kind"] == "measured"
    assert wt["source"] == "georgian-colonial-american.c05"
    c = next(x for x in json.load(open(os.path.join(
        ROOT, "styles", "georgian-colonial-american.json")))["constraints"]
        if x["id"] == "georgian-colonial-american.c05")
    assert [c["test"]["threshold"], c["test"]["upper"]] == wt["range"], \
        "the citation must still agree with what it cites"


def test_a_garage_number_is_invented_and_not_editorial():
    """Two different claims. The schema defines editorial as 'our considered convention' and
    invented as 'no precedent exists', and `garage_strategy`'s own ontology note says in its
    first sentence that no historical precedent exists. A number about the garage door itself
    cannot be a convention drawn from tradition, because the tradition has no garage."""
    ont = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    slot = next(s for g in ont["groups"] for s in g["slots"] if s["id"] == "garage_strategy")
    assert "no historical precedent" in slot["note"].lower()

    INVENTED = {"max_door_width", "door_count_preferred", "door_orientation",
                "attachment", "habitable_room_above", "door_head_datum"}
    n = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        s = (json.load(open(p))["slots"].get("garage_strategy") or {})
        for pn, pv in (s.get("parameters") or {}).items():
            if pn in INVENTED and isinstance(pv, dict):
                assert pv.get("kind") != "editorial", (p, pn)
                n += 1
    assert n == 14, n   # pinned at the achieved count; `>= 11` left three units of slack


def test_the_editorial_parameters_carried_forward_are_still_the_known_number():
    """Not an aspiration and not a ratchet -- a pin, so the figure in docs/open-questions.md #18
    and the corpus cannot drift apart again without a test saying so. Update it deliberately,
    with the reason, the way every other count in this suite is updated."""
    c = census()
    # 202, not 201: WP-5.10 authored ONE editorial parameter, `colonial-revival`'s dormer
    # `sash_pattern`. The style bound its dormer slot `open` and inherited an English cottage's
    # (OQ 87), which stated no pattern, so the elevation had to draw that style's dormer sash as
    # bare glass and say so on the sheet. A count parity and an alignment rule were drafted
    # alongside it and DROPPED: neither changes what is drawn, and both would have added unsourced
    # editorial calls to OQ 18's debt for documentation's sake. The corpus reports those two as
    # not stated, which is true.
    assert c["editorial"] == 202, c["editorial"]
    # 199 -> 201 on 27 Aug 2026 (WP-5.9): two shutter panel counts authored on
    # `tidewater-georgian`'s shutter slot when that slot was adjudicated. The style had bound the
    # slot EMPTY, so the cascade delivered its parent's raised-panel pair and every elevation of
    # a solid-brick Chesapeake house was drawn with exterior shutters four independent records
    # say it never had. Both new parameters are editorial, judgment, and carry the unverified-at-
    # source idiom this package introduced: the Colonial Williamsburg and NPS documents they rest
    # on were read as search-index excerpts and could not be opened from here (the proxy block
    # that holds OQ 7-11). They are the honest kind of editorial -- a figure the corpus needs,
    # marked as a judgment, with its basis quoted -- and not the kind this same package deleted
    # from build/elevation.py, which were ratios with no author at all.
    # 164 -> 162 on 24 Aug 2026 (OQ 46): splitting the Georgian and Tidewater window heads
    # against the new `arch` slot put those two slots under OQ 19's determined_by check, which
    # requires a note on an editorial number sitting where a determination should be. Two got
    # one. That is the ratchet working -- a rule added for one reason tightening another.
    # 162 -> 0 on 25 Aug 2026 (OQ 18, half closed). Every one of the 162 gained a note saying that
    # no source is recorded, quoting the basis its SLOT states, and naming which of four forms the
    # figure takes. NOT ONE GAINED A SOURCE -- that half is environment-blocked with OQ 7-11, and a
    # note is not a citation. The pin is now zero and should stay there: a new editorial parameter
    # with neither a source nor a note is an author skipping the corpus's own rule.
    assert c.get("bare", 0) == 0, c.get("bare")
