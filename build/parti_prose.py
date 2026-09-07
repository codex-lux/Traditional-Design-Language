#!/usr/bin/env python3
"""parti_prose.py — everything a parti says that nothing executes (WP-11.11).

`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` Part VI is a table of twenty statements
the corpus makes about ONE parti and can execute none of. It was assembled by hand, and WP-11.9
then worked it — 6 of the twenty were already executable, 5 were made so, 9 are refused with a
reason. **The expensive part was not the executing; it was the ENUMERATING**, and that is what
this file does, so the next twenty partis get their Part VI generated rather than read out.

    python3 build/parti_prose.py centre-passage-double-pile [--md] [--all]

WHAT IT READS, and every one of these is reached FROM the parti rather than swept corpus-wide,
because a Part VI is about one diagram:

  * its `groupings[]` -> each `internal_rules` entry, sorted three ways: carries a `test`,
    REPORTS through `measures.reported_by`, or is handed to a human. WP-11.9's fix is what makes
    the third bucket visible at all: the grouping layer's no-test branch read `elif hard`, so
    every `strong` and `preferred` rule in the corpus emitted nothing and read exactly like a
    rule that passed.
  * its `massing` -> `constraints[]`, `structural_logic`, `expansion_logic`. WP-9.2 measured the
    readers: `structural_logic` has ZERO, `expansion_logic` has a counter and an HTML dump, and
    `constraints` is an array of prose nothing parses.
  * its `rooms[]` -> each room record's `dimensions.critical_dimension`, for figures in a band's
    own units that neither end of that band carries. **The meter is `check_grouping_rules.py`'s,
    imported rather than transcribed** -- that file's own docstring records what its first
    version cost, and a second spelling of a crude regex is how a corpus ends up with two
    different upper bounds for one question.
  * its `rooms[]` -> `daylight.orientation`, which WP-11.9 made executable and which is therefore
    reported as EXECUTED here rather than omitted. A row that has moved out of this table is the
    only evidence the table is worth generating.

IT COUNTS AND DOES NOT JUDGE. A rule with no test is not a defect: the facade ruling
(`oq/the-facade-is-a-result-not-an-input`) made one a REPORT on purpose, several are genuinely a
human's to check, and WP-11.9's §IV names nine that cannot be executed until a fact exists that
does not. **A SLUG MUST NOT WRAP**: `check_citations.py` reads line by line, so the first draft of
this paragraph broke `oq/the-facade-is-a-result-not-an-input` across a newline and the checker
reported half of it dangling -- the same line-by-line reading CLAUDE.md records for the code span
straddling a newline in WP-8.5's commit subject. The number is
a work list in leverage order, which is what `check_inheritance.py --unendorsed` is for the pack
cascade, one layer over.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    return modcache.load(name, path)


def _load():
    CGR = _mod("check_grouping_rules", os.path.join(ROOT, "build", "check_grouping_rules.py"))
    partis, groupings, rooms = {}, {}, {}
    import glob
    for p in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        d = json.loads(open(p).read())
        partis[d["id"]] = d
    for p in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        d = json.loads(open(p).read())
        groupings[d["id"]] = d
    for p in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        d = json.loads(open(p).read())
        rooms[d["id"]] = d
    massings = {}
    mp = os.path.join(ROOT, "massings", "catalog.json")
    raw = json.loads(open(mp).read())
    for m in (raw if isinstance(raw, list) else raw.get("massings") or []):
        massings[m["id"]] = m
    return CGR, partis, groupings, rooms, massings


# The three states a grouping rule can be in, and they are not a pass/fail pair.
EXECUTED = "executed"          # carries a `test` the grouping layer evaluates
REPORTED = "reported"          # carries `measures.reported_by`; measured, deliberately not required
BY_HAND = "by hand"            # named to the reader, executed by nobody


def grouping_rules(parti, groupings):
    out = []
    for gid in parti.get("groupings") or []:
        g = groupings.get(gid)
        if not g:
            out.append((gid, None, BY_HAND, f"no grouping record `{gid}` — the parti names one "
                                            f"that does not exist"))
            continue
        for i, ru in enumerate(g.get("internal_rules") or []):
            if ru.get("test"):
                state = EXECUTED
            elif (ru.get("measures") or {}).get("reported_by"):
                state = REPORTED
            else:
                state = BY_HAND
            out.append((f"{gid}[{i}]", ru.get("severity"), state, ru["statement"]))
    return out


def massing_prose(parti, massings):
    """The massing's own sentences, with the reader count WP-9.2 measured beside each."""
    m = massings.get(parti.get("massing"))
    if not m:
        return []
    out = []
    for c in (m.get("constraints") or []):
        out.append((f"{m['id']}.constraints", None, BY_HAND, c))
    for field, note in (("structural_logic", "zero readers (WP-9.2)"),
                        ("expansion_logic", "a counter, an HTML dump and an API echo; "
                                            "nothing acts on it (WP-9.2)")):
        if m.get(field):
            out.append((f"{m['id']}.{field}", note, BY_HAND, m[field]))
    return out


def room_figures(parti, rooms, groupings, CGR):
    """Figures a room's own prose states that no band this parti's groupings test carries.

    The meter is `check_grouping_rules.prose_meter`'s, scoped to this parti's rooms. It is a
    CRUDE REGEX and an upper bound and that file says so; the way to lower it is to author the
    figure into a test, never to tighten the pattern until the number looks better.
    """
    # THE ROOM FILTER IS INERT TODAY AND IS KEPT WITH ITS REASON RATHER THAN DELETED.
    # Measured: on this parti, scoping the rooms and passing the whole corpus return the SAME
    # seven rows, because `prose_meter`'s room population is keyed on `bands_used`, which it
    # derives from the GROUPINGS it is given -- so the grouping scope below already constrains
    # the rooms it can reach (it reaches `bedroom` and `centre-passage`, both named by this
    # parti). A mutation replacing this line with `dict(rooms)` therefore leaves the suite green,
    # which is a BLIND GUARD and is recorded as one rather than being patched over with a test
    # that would pass for the wrong reason. It stays because the function's contract is "scoped
    # to this parti" and a reader must not have to prove that from another file's internals.
    want = {r["type"] for r in (parti.get("rooms") or []) if r.get("type")}
    sub_rooms = {k: v for k, v in rooms.items() if k in want}
    sub_groupings = {gid: groupings[gid] for gid in (parti.get("groupings") or [])
                     if gid in groupings}
    return [row for row in CGR.prose_meter(sub_groupings, sub_rooms)]


def orientation_rows(parti, rooms):
    """`daylight.orientation`, EXECUTED since WP-11.9. Reported rather than omitted, because a
    row that has left this table is the only evidence generating it was worth doing."""
    want = sorted({r["type"] for r in (parti.get("rooms") or []) if r.get("type")})
    out = []
    for rid in want:
        rm = rooms.get(rid)
        if not rm:
            continue
        dl = rm.get("daylight") or {}
        if not dl.get("orientation"):
            continue
        a = dl.get("aspect")
        if not a:
            out.append((f"rooms/{rid}.daylight.orientation", None, BY_HAND, dl["orientation"]))
        elif a.get("applies"):
            out.append((f"rooms/{rid}.daylight.orientation", a.get("strength"), EXECUTED,
                        a["basis"]))
        else:
            out.append((f"rooms/{rid}.daylight.orientation", "declines", REPORTED,
                        a.get("note") or a["basis"]))
    return out


def survey(pid, partis, groupings, rooms, massings, CGR):
    p = partis[pid]
    return {
        "parti": pid,
        "grouping_rules": grouping_rules(p, groupings),
        "massing_prose": massing_prose(p, massings),
        "room_figures": room_figures(p, rooms, groupings, CGR),
        "orientation": orientation_rows(p, rooms),
    }


def counts(s):
    c = {EXECUTED: 0, REPORTED: 0, BY_HAND: 0}
    for row in s["grouping_rules"] + s["massing_prose"] + s["orientation"]:
        c[row[2]] += 1
    c["prose figures nothing carries"] = len(s["room_figures"])
    return c


def _trim(t, n=150):
    t = " ".join(str(t).split())
    return t if len(t) <= n else t[: n - 1] + "…"


def report(s, md=False):
    L = []
    if md:
        L.append(f"## Part VI — what `{s['parti']}` says and cannot execute\n")
        L.append("*Generated by `build/parti_prose.py`. A rule with no test is not a defect: "
                 "several are a human's to check, one is a REPORT by ruling, and WP-11.9's §IV "
                 "names nine that cannot be executed until a fact exists that does not.*\n")
        L.append("| where | severity | state | statement |")
        L.append("|---|---|---|---|")
        for where, sev, state, text in (s["grouping_rules"] + s["massing_prose"]
                                        + s["orientation"]):
            L.append(f"| `{where}` | {sev or '—'} | {state} | {_trim(text)} |")
        L.append("")
        if s["room_figures"]:
            L.append("### Figures stated in prose that no band or test carries\n")
            L.append("| kind | where | figure | the sentence |")
            L.append("|---|---|---|---|")
            for kind, where, fig, sent in s["room_figures"]:
                L.append(f"| {kind} | `{where}` | {fig} | {_trim(sent, 120)} |")
            L.append("")
        c = counts(s)
        L.append(f"**{c[EXECUTED]} executed, {c[REPORTED]} reported, {c[BY_HAND]} handed to a "
                 f"reader, {c['prose figures nothing carries']} prose figure(s) nothing "
                 f"carries.**")
        return "\n".join(L)
    L.append(f"=== {s['parti']} ===")
    for title, rows in (("grouping rules", s["grouping_rules"]),
                        ("massing prose", s["massing_prose"]),
                        ("room orientation", s["orientation"])):
        L.append(f"\n-- {title} --")
        for where, sev, state, text in rows:
            L.append(f"  [{state:<8}] {where:<38} {_trim(text, 90)}")
    if s["room_figures"]:
        L.append("\n-- figures in prose no band carries --")
        for kind, where, fig, sent in s["room_figures"]:
            L.append(f"  {kind:<5} {where:<28} {fig:<7} {_trim(sent, 80)}")
    c = counts(s)
    L.append(f"\n{c[EXECUTED]} executed, {c[REPORTED]} reported, {c[BY_HAND]} by hand, "
             f"{c['prose figures nothing carries']} prose figure(s) nothing carries.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parti", nargs="?")
    ap.add_argument("--md", action="store_true", help="emit the Part VI markdown section")
    ap.add_argument("--all", action="store_true", help="one summary line per parti")
    a = ap.parse_args()
    CGR, partis, groupings, rooms, massings = _load()
    if a.all:
        for pid in sorted(partis):
            c = counts(survey(pid, partis, groupings, rooms, massings, CGR))
            print(f"{pid:<34} executed {c[EXECUTED]:>3}  reported {c[REPORTED]:>3}  "
                  f"by hand {c[BY_HAND]:>3}  prose figures {c['prose figures nothing carries']:>3}")
        return 0
    if not a.parti:
        ap.error("name a parti, or pass --all")
    if a.parti not in partis:
        print(f"no parti `{a.parti}`", file=sys.stderr)
        return 2
    print(report(survey(a.parti, partis, groupings, rooms, massings, CGR), md=a.md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
