#!/usr/bin/env python3
"""gen_plate_wants.py -- the plates a person must fetch, generated from the packs (WP-14.5).

    python3 build/gen_plate_wants.py            # write Plan Examples/Plates/WANTED.md
    python3 build/gen_plate_wants.py --check    # fail if the committed file is not current

WHY THIS EXISTS. Phase 14's third decision (27 Sep 2026): the source leg of the fidelity audit is
internal checks now, plus a list a person can take to a library, on the precedent of
`Plan Examples/HABS/WANTED.md`. Every host the order packs cite refuses a CONNECT from this
container, so no figure here can be held against its plate. What CAN be done is to say exactly
which figures a plate would settle, and this file says it from the records rather than from a
reading of them.

FIVE CLASSES, in the order a person's time is best spent:
  0. A figure the record carries and a note in the corpus states otherwise -- census N1's pinned
     disagreements, read from `plate_review.member_entries()` so this list and the census cannot
     differ about which figures are disputed. One look at the page settles a contradiction the
     corpus already knows it has.
  1. An assembly whose every member publishes no projection -- the record has the heights and not
     one face, so its profile is drawn as a ghost at the naked on every surface (WP-14.2).
  2. A member publishing no projection, in an assembly whose other members do.
  3. A height the transcriber APPORTIONED -- the author's total is stated and the division among
     the members was read off an engraving or divided by eye. The word is the transcribers' own
     marker (`Apportioned.`), written on 110 member notes; it is read as their statement and
     never inferred from anything else.
  4. A member marked `confidence: low` that none of the three classes above already lists.

THE COUNT IS WHERE THE FIGURE IS STATED. An overlay that inherits Vignola's cornice inherits its
gaps too, and listing the gap under every overlay would count one missing figure several times
and send a person to the wrong book for it. So every row is attributed to the pack that STATES
the assembly (`proportion_engine.assembly_owner`), and the book is that pack's authority.

A SUMMARY ASSEMBLY IS NOT A GAP. An `entablature` whose members are the pack's own architrave,
frieze and cornice carries their heights as a division of the whole; its projection is the
detailed assembly's, which is listed under that assembly if it is missing. Counting the summary
too would double the entablature rows.
"""
import argparse
import collections
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
PR = modcache.load("plate_review", os.path.join(ROOT, "build", "plate_review.py"))
OUT = os.path.join(ROOT, "Plan Examples", "Plates", "WANTED.md")

# Re-probed 27 Sep 2026 through this container's proxy, which answered 403 to CONNECT for each.
# A statement about one day, dated as one; nothing below claims a host is reachable.
PROBED = ("archive.org", "www.loc.gov", "babel.hathitrust.org", "commons.wikimedia.org",
          "www.polito.it")
PROBED_ON = "27 September 2026"

# The open questions that are waiting on a legible facsimile rather than on a ruling. Their own
# files say what is needed; the list names them so a person fetching the book knows which gap
# the plate closes.
FACSIMILE_QUESTIONS = {
    "palladio": ["007"],
    "chambers": ["008"],
    "vignola": ["009"],
    "benjamin": ["010"],
}


def _order_packs():
    return sorted(p for p, r in PE.PACKS.items() if (r.get("kind") or "") == "order-system")


def _book(pid):
    """The book a pack's figures come from: authority source and url, and a folder name."""
    a = PE.PACKS[pid].get("authority") or {}
    return a.get("url") or a.get("source") or pid


# A folder per author, named as a person would look for it. Two packs are not named for theirs.
FOLDER = {"greek-doric": "stuart-revett", "moorish-arch": "jones-goury"}


def _folder(pid):
    return FOLDER.get(pid, pid.split("-")[0])


def _is_summary(pid, aid, a):
    """True when every member of the assembly is another assembly of the pack AS RESOLVED.

    As resolved, because an overlay may state its entablature's division and inherit the detailed
    architrave, frieze and cornice it divides: `palladio-ionic` does, and reading its own file
    alone called the division a gap."""
    ids = {m.get("id") for m in a.get("members", [])}
    others = set(PE.resolve(pid).get("assemblies") or {}) - {aid}
    return bool(ids) and ids <= others


def _unpublished(m):
    return m.get("projection_parts") is None


def _apportioned(m):
    return "apportion" in (m.get("note") or "").lower()


def disputed():
    """Class 0: a figure a record carries that a note in the corpus states otherwise.

    One row per FIGURE and not per note: two notes stating one figure (Benjamin's Doric states
    its annulet's projection under the necking and again under the abacus) are one page to read.
    A claim a note makes about ANOTHER pack's record (`palladio-corinthian` on the Doric base) is
    listed under the pack that states that figure, because that is the book that settles it."""
    found = collections.OrderedDict()
    for e in PR.member_entries():
        if e["verdict"] != "disagrees":
            continue
        for c in e["claims"]:
            if c["agrees"]:
                continue
            asm = c.get("target_assembly") or e["assembly"]
            pack = PE.assembly_owner(c.get("target_pack") or e["pack"], asm)
            r = found.setdefault((pack, asm, c["target"]), {
                "cls": 0, "pack": pack, "assembly": asm, "member": c["target"],
                "record": c["record"], "notes": []})
            r["notes"].append({"value": c["note"], "quote": c["quote"],
                               "in": "%s/%s/%s" % (e["pack"], e["assembly"], e["member"])})
    return list(found.values())


def rows():
    """Every wanted figure, attributed to the pack that states its assembly."""
    out = disputed()
    for pid in _order_packs():
        raw = PE.PACKS[pid]
        # THE PACK'S OWN FILE, and that is the attribution: an assembly in it is one the pack
        # states (`proportion_engine.assembly_owner` returns the pack for every one of them).
        # A filter on the owner here was written first and could never be false.
        for aid, a in (raw.get("assemblies") or {}).items():
            members = a.get("members") or []
            summary = _is_summary(pid, aid, a)
            wholly = bool(members) and not summary and all(_unpublished(m) for m in members)
            if wholly:
                out.append({"cls": 1, "pack": pid, "assembly": aid,
                            "members": [m.get("name") or m["id"] for m in members]})
            listed = set()
            for m in members:
                if not summary and not wholly and _unpublished(m):
                    out.append({"cls": 2, "pack": pid, "assembly": aid, "member": m["id"],
                                "name": m.get("name") or m["id"]})
                    listed.add(m["id"])
                if _apportioned(m):
                    out.append({"cls": 3, "pack": pid, "assembly": aid, "member": m["id"],
                                "name": m.get("name") or m["id"], "note": m.get("note") or ""})
                    listed.add(m["id"])
            for m in members:
                if m.get("confidence") == "low" and m["id"] not in listed and not wholly:
                    out.append({"cls": 4, "pack": pid, "assembly": aid, "member": m["id"],
                                "name": m.get("name") or m["id"]})
    return out


def _first_clause(note, limit=160):
    """The note's own words to its first clause, and the elision marked when anything is cut --
    WP-11.5's rule for a quoted basis, after OQ 18's first version cut 148 notes mid-word."""
    t = " ".join(note.split())
    head = t
    for stop in (". ", "; "):
        i = head.find(stop)
        if i != -1:
            head = head[:i]
    head = head.rstrip(".")
    if len(head) > limit:
        head = head[:limit].rsplit(" ", 1)[0]
    return head + (" …" if head != t.rstrip(".") else "")


def _num(x):
    return "%g" % round(float(x), 4)


def _md_cell(t):
    return str(t).replace("|", "\\|").replace("\n", " ")


def render():
    R = rows()
    by_book = collections.OrderedDict()
    for pid in _order_packs():
        by_book.setdefault(_book(pid), []).append(pid)
    counts = {}
    for book, pids in by_book.items():
        c = collections.Counter(r["cls"] for r in R if r["pack"] in pids)
        counts[book] = c
    # Books in the order a person's time is best spent: the most wholly unpublished assemblies,
    # then the most unpublished members, then the most apportioned heights.
    order = sorted(by_book, key=lambda b: (-counts[b][1], -counts[b][2], -counts[b][3],
                                           -counts[b][4], by_book[b][0]))
    tot = collections.Counter(r["cls"] for r in R)
    L = []
    w = L.append
    w("# Order plates wanted — the figures the proportion packs could not read")
    w("")
    w("*Generated by `build/gen_plate_wants.py` from the order packs; `--check` holds this file "
      "to them, so edit the packs and regenerate rather than editing here.*")
    w("")
    w("**For Lucas.** Phase 14's third decision was that the source leg of the fidelity audit is "
      "internal checks now, plus a list you can take to a library — the precedent is "
      "`Plan Examples/HABS/WANTED.md`. This is that list for the orders and their mouldings.")
    w("")
    w("**Nothing here was verified reachable.** Re-probed on %s through this container's proxy, "
      "every host tried answered 403 to CONNECT: %s. No URL below has been opened from here; each "
      "is copied from the pack that cites it." % (PROBED_ON, ", ".join("`%s`" % h for h in PROBED)))
    w("")
    w("**Where to put them:** `Plan Examples/Plates/<author>/`, e.g. `Plan Examples/Plates/palladio/`. "
      "Keep the plate, leaf or page number in the filename (`ware-1738-book1-leaf-35.jpg`), because "
      "a transcription cites the plate and a scan with no number cannot be cited.")
    w("")
    w("**Rights.** Do not write a `license` field for these, and do not let anyone else. Copy the "
      "holding library's rights statement verbatim into a text file beside the scans, with the URL "
      "it was read from. A scan of a book printed before 1900 is ordinarily unrestricted, but the "
      "statement is evidence to record and not clearance to publish — the HABS list says why in "
      "more detail.")
    w("")
    w("**What each class means**, in the order your time is best spent:")
    w("")
    w("0. **A figure a note in the corpus disputes.** The record carries one figure and a note "
      "beside it states another, and nothing in the corpus can say which is the author's. Census "
      "N1 holds each as a pinned disagreement; "
      "`docs/open-questions/oq-a-members-note-states-a-figure-its-record-does-not-carry.md` and "
      "`docs/open-questions/oq-four-attic-bases-project-a-third-of-a-diameter.md` set them out. "
      "Look for these first on any plate you open: one look settles a contradiction the corpus "
      "already knows it has.")
    w("1. **An assembly with no projection published at all.** The record has every height and not "
      "one face, so every surface draws its profile as a dashed ghost at the naked (WP-14.2). One "
      "plate settles the whole assembly.")
    w("2. **A member with no projection**, in an assembly that publishes the others.")
    w("3. **A height the transcriber apportioned.** The author's total is stated and the division "
      "among the members was read off the engraving or divided by eye; the note says `Apportioned`. "
      "The plate's own figures would replace a reading with a measurement.")
    w("4. **A member marked low confidence** that none of the three classes above already lists.")
    w("")
    w("Every row is listed under the pack that STATES the assembly, so a gap an overlay inherits "
      "from Vignola is listed once, under Vignola, and sends you to Vignola's book. A summary "
      "`entablature` whose members are the pack's own architrave, frieze and cornice is not listed: "
      "its projection is the detailed assemblies'.")
    w("")
    w("## The books, in the order to fetch them")
    w("")
    w("Books are ordered by their gaps (classes 1 to 4) and not by their disputes, because a "
      "dispute is one figure and a gap can be a whole profile.")
    w("")
    w("| book | packs | 0. figures a note disputes | 1. assemblies with no projection | "
      "2. members with no projection | 3. apportioned heights | 4. other low-confidence members |")
    w("|---|---|---:|---:|---:|---:|---:|")
    for b in order:
        c = counts[b]
        a = PE.PACKS[by_book[b][0]].get("authority") or {}
        w("| %s (%s) | %s | %d | %d | %d | %d | %d |" % (
            _md_cell(a.get("author") or by_book[b][0]), a.get("year") or "?",
            ", ".join("`%s`" % p for p in by_book[b]), c[0], c[1], c[2], c[3], c[4]))
    w("| **total** | %d packs | **%d** | **%d** | **%d** | **%d** | **%d** |" % (
        len(_order_packs()), tot[0], tot[1], tot[2], tot[3], tot[4]))
    w("")
    for b in order:
        pids = by_book[b]
        a = PE.PACKS[pids[0]].get("authority") or {}
        c = counts[b]
        if not any(c.values()):
            continue
        folder = _folder(pids[0])
        w("## %s, %s" % (a.get("author") or pids[0], a.get("year") or "?"))
        w("")
        w("**Put the scans in** `Plan Examples/Plates/%s/`. **Scan cited by the packs:** %s" % (
            folder, ("<%s>" % a["url"]) if a.get("url") else "none recorded"))
        w("")
        for pid in pids:
            pa = PE.PACKS[pid].get("authority") or {}
            w("- `%s` cites: %s" % (pid, _md_cell(pa.get("source") or "no source recorded")))
        for q in FACSIMILE_QUESTIONS.get(folder, []):
            f = next((x for x in sorted(os.listdir(os.path.join(ROOT, "docs", "open-questions")))
                      if x.startswith(q + "-")), None)
            if f:
                title = open(os.path.join(ROOT, "docs", "open-questions", f)).readline()
                w("- **Also closes** %s: `docs/open-questions/%s`" % (
                    _md_cell(title.lstrip("# ").strip()), f))
        w("")
        mine = [r for r in R if r["pack"] in pids]
        zero = [r for r in mine if r["cls"] == 0]
        if zero:
            w("### 0. Figures a note in the corpus disputes (%d)" % len(zero))
            w("")
            w("| pack | assembly | figure | the record | a note states | the note's words |")
            w("|---|---|---|---:|---|---|")
            for r in zero:
                w("| `%s` | %s | `%s` | %s | %s | %s |" % (
                    r["pack"], r["assembly"], _md_cell(r["member"]), _num(r["record"]),
                    "; ".join("%s (`%s`)" % (_num(n["value"]), n["in"]) for n in r["notes"]),
                    _md_cell(" / ".join(sorted({"*%s*" % n["quote"] for n in r["notes"]})))))
            w("")
        one = [r for r in mine if r["cls"] == 1]
        if one:
            w("### 1. Assemblies with no projection published (%d)" % len(one))
            w("")
            w("| pack | assembly | members |")
            w("|---|---|---|")
            for r in one:
                w("| `%s` | %s | %s |" % (r["pack"], r["assembly"], _md_cell("; ".join(r["members"]))))
            w("")
        two = [r for r in mine if r["cls"] == 2]
        if two:
            w("### 2. Members with no projection (%d)" % len(two))
            w("")
            w("| pack | assembly | member |")
            w("|---|---|---|")
            for r in two:
                w("| `%s` | %s | %s (`%s`) |" % (r["pack"], r["assembly"], _md_cell(r["name"]), r["member"]))
            w("")
        three = [r for r in mine if r["cls"] == 3]
        if three:
            w("### 3. Heights the transcriber apportioned (%d)" % len(three))
            w("")
            w("| pack | assembly | member | the note, to its first clause |")
            w("|---|---|---|---|")
            for r in three:
                w("| `%s` | %s | %s | %s |" % (r["pack"], r["assembly"], _md_cell(r["name"]),
                                              _md_cell(_first_clause(r["note"]))))
            w("")
        four = [r for r in mine if r["cls"] == 4]
        if four:
            w("### 4. Other low-confidence members (%d)" % len(four))
            w("")
            w("| pack | assembly | member |")
            w("|---|---|---|")
            for r in four:
                w("| `%s` | %s | %s (`%s`) |" % (r["pack"], r["assembly"], _md_cell(r["name"]), r["member"]))
            w("")
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if the committed file is not current")
    a = ap.parse_args()
    text = render()
    if a.check:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
        if have != text:
            print("%s is not current; run build/gen_plate_wants.py" % os.path.relpath(OUT, ROOT))
            return 1
        print("%s is current." % os.path.relpath(OUT, ROOT))
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, OUT)
    tot = collections.Counter(r["cls"] for r in rows())
    print("wrote %s: %d figures a note disputes, %d assemblies with no projection, %d members "
          "with no projection, %d apportioned heights, %d other low-confidence members"
          % (os.path.relpath(OUT, ROOT), tot[0], tot[1], tot[2], tot[3], tot[4]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
