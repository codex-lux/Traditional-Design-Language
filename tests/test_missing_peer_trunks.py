"""The record of what the tree lacks may not name what the tree holds (WP-14.33's audit).

R5 of 26 Sep 2026 moved the Phylogeny's "Japanese, Islamic, South Asian and African traditions are
absent" out of the JSX and into `glossary/missing-peer-trunks.json`, and derived the traditions the
tree DOES hold from its own tradition-rank nodes. That fixed where the sentence lives and not what
made it dangerous: the absent list is still editorial prose, checked by `check_glossary` against the
README it quotes and against nothing in `styles/`. The day a `japanese` tradition node lands, the
page would list it under the held trunks and print, a line below, that Japanese building would be a
peer trunk beside them. This holds the two against each other: no word of a tradition node's name
may appear in the record's account of what is missing.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD = os.path.join(ROOT, "glossary", "missing-peer-trunks.json")
# Words a tradition's name may share with the record's own framing without naming a tradition.
GENERIC = {"vernacular", "tradition", "traditions", "building", "architecture", "style", "styles"}


def traditions():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        if d.get("rank") == "tradition":
            out.append((d["id"], d.get("name") or d["id"]))
    return out


def contradictions(record, nodes):
    """`[(node id, word)]` for every word of a held tradition's name the record names as missing."""
    text = " ".join(str(record.get(k) or "") for k in ("definition", "more")).lower()
    found = []
    for nid, name in nodes:
        for w in sorted(set(re.findall(r"[a-z]+", (name + " " + nid.replace("-", " ")).lower()))):
            if len(w) >= 4 and w not in GENERIC and re.search(r"\b%s\b" % re.escape(w), text):
                found.append((nid, w))
    return found


def test_the_record_names_no_tradition_the_tree_holds():
    nodes = traditions()
    assert len(nodes) >= 5, "the premise: the tree's tradition-rank nodes are read"
    record = json.load(open(RECORD, encoding="utf-8"))
    assert record["definition"], "the premise: the record states what is missing"
    assert contradictions(record, nodes) == []


def test_a_tradition_that_lands_contradicts_the_record_by_name():
    """Driven: the case the guard exists for, which the corpus does not hold today."""
    record = json.load(open(RECORD, encoding="utf-8"))
    assert contradictions(record, [("japanese", "Japanese")]) == [("japanese", "japanese")]
    assert contradictions(record, [("islamic-world", "Islamic World")]) == [("islamic-world", "islamic")]
    # and a held tradition sharing only the record's framing words is not one it names
    assert contradictions(record, [("x", "Northern European Vernacular")]) == []
