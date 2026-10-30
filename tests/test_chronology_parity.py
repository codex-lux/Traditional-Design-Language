"""Phase 17 (WP-17.12): the family tree's chronology exception is build/validate.py's own warning.

The tree flags a `descends_from` or `regional_of` edge whose descendant flourishes more than
twenty-five years before its ancestor; `workbench/app/src/lineage/lanes.js` carries the rule and
this holds it to the validator's, over the corpus, so the page and the build cannot disagree about
which edges break the chronology."""
import json
import os
import re
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _validator_warnings():
    out = subprocess.run(["python3", "build/validate.py"], cwd=ROOT, capture_output=True, text=True)
    pairs = set()
    for m in re.finditer(r"(\S+) \(\d+\) starts well before ancestor (\S+) \(\d+\)", out.stdout + out.stderr):
        pairs.add((m.group(1), m.group(2)))
    return pairs


def _js_rule():
    taxa, edges = [], []
    for name in sorted(os.listdir(os.path.join(ROOT, "styles"))):
        if not name.endswith(".json"):
            continue
        n = json.load(open(os.path.join(ROOT, "styles", name), encoding="utf-8"))
        taxa.append({"id": n["id"], "floruit_start": n["period"]["floruit_start"]})
        for e in n.get("lineage", []):
            edges.append({"from": n["id"], "to": e["target"], "type": e["type"]})
    src = ("import { chronologyExceptions } from './workbench/app/src/lineage/lanes.js';"
           f"console.log(JSON.stringify(chronologyExceptions({json.dumps(taxa)}, {json.dumps(edges)})));")
    out = subprocess.run(["node", "--input-type=module", "-e", src], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return {(e["from"], e["to"]) for e in json.loads(out.stdout)}


def test_the_tree_and_the_validator_flag_the_same_edges():
    if not shutil.which("node"):
        pytest.skip("COULD NOT EVALUATE: node is not on PATH, so the tree's rule cannot be run")
    warned = _validator_warnings()
    assert warned, "the premise: the corpus carries a documented chronology exception"
    assert _js_rule() == warned
