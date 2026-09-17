"""A duplicate JSON key is invisible to every reader in this tree (WP-11.16).

FOUND IN ORDINARY WORK. `plans/tidewater-georgian-careful.json` carried `"stacks_over"` TWICE on
each of two upper rooms -- `landing` and `upperpassage` -- and had done since WP-11.6, whose own
entry in CLAUDE.md says it "now declares the two `stacks_over` claims its own parti had always
made". It declared them twice. `json.loads` keeps the LAST occurrence and drops the rest without
a word, so every reader in this corpus saw one; both values were identical, so nothing any reader
saw was ever wrong.

**NOTHING IN THIS TREE COULD SEE IT.** `jsonschema` validates the PARSED object, and by then the
duplicate is gone. `validate.py`, `check_plans.py`, `check_stacking.py` and every test parse
first too. It surfaced only because a round-trip through `json.dumps` collapsed the pair and the
git diff showed two lines removed that nobody had edited -- which is a tell you get once.

The swept figure at the time: **2 duplicates in 1,437 committed JSON files**, both in that one
plan, both with identical values. This test is the cheap corpus-wide guard that was missing, and
it is a TEST rather than a checker on purpose -- WP-11.6's precedent, so `TOTAL_CHECKS` does not
move for a hygiene invariant that costs under a second.

WHY IT MATTERS EVEN WHEN THE VALUES AGREE: a record edit that writes a key already present is a
silent no-op the author believes landed, and the day the two values DIFFER the file says one
thing and means another. That is the same shape as this repository's own "an edit that reports
success and changes nothing", one layer down in the data.
"""
import collections
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _json_paths():
    """Every tracked .json file, `dist/` excluded -- it is generated on every build."""
    out = subprocess.run(["git", "ls-files", "*.json"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return [ROOT / f for f in out if not f.startswith("dist/")]


def _duplicates(text):
    """Every (key, count, values) an object in this document states more than once.

    `object_pairs_hook` is the ONLY way to see this from Python: by the time the dict exists the
    duplicate has been resolved away. The hook must still RETURN a dict, or the parse changes
    meaning under the test that is checking it."""
    found = []

    def hook(pairs):
        counts = collections.Counter(k for k, _ in pairs)
        for k, n in counts.items():
            if n > 1:
                found.append((k, n, [v for kk, v in pairs if kk == k]))
        return dict(pairs)

    json.loads(text, object_pairs_hook=hook)
    return found


def test_no_tracked_json_record_states_a_key_twice():
    paths = _json_paths()
    # the population is asserted first: a `git ls-files` that matched nothing would make every
    # assertion below vacuous, which is this repository's most-recorded shape of bad guard
    assert len(paths) > 1000, f"only {len(paths)} json file(s) found -- the sweep is not running"
    hits = []
    for p in paths:
        for k, n, vals in _duplicates(p.read_text(encoding="utf-8")):
            same = len({json.dumps(v, sort_keys=True) for v in vals}) == 1
            hits.append(f"{p.relative_to(ROOT)}: {k!r} stated {n} times"
                        f"{'' if same else ' WITH DIFFERENT VALUES'}")
    assert hits == [], (
        "a tracked JSON record states a key more than once. `json.loads` keeps the last and "
        "drops the rest in silence, so a reader sees one value and the file states two -- and "
        "where the values differ, the record means something nobody wrote:\n  "
        + "\n  ".join(hits))


def test_the_detector_sees_a_duplicate_that_json_loads_hides():
    """A guard that cannot fire is not a guard, and this one runs over a corpus that is clean --
    so the detector is driven on the exact shape it was written for, including the case the
    corpus had (identical values) and the sharper one it did not (different values)."""
    same = '{"a": 1, "stacks_over": "stair", "b": 2, "stacks_over": "stair"}'
    assert json.loads(same) == {"a": 1, "stacks_over": "stair", "b": 2}, (
        "json.loads no longer resolves a duplicate silently; re-read this whole file")
    got = _duplicates(same)
    assert [(k, n) for k, n, _v in got] == [("stacks_over", 2)]

    differ = '{"stacks_over": "stair", "stacks_over": "passage"}'
    assert json.loads(differ) == {"stacks_over": "passage"}, "the LAST one wins"
    assert [(k, n) for k, n, _v in _duplicates(differ)] == [("stacks_over", 2)]

    # nested, and in a list -- the corpus's duplicates were inside a room inside a level
    deep = '{"levels": [{"rooms": [{"id": "x", "id": "y"}]}]}'
    assert [(k, n) for k, n, _v in _duplicates(deep)] == [("id", 2)]

    # and a document with no duplicate returns nothing, or the test above passes on everything
    assert _duplicates('{"a": 1, "b": {"a": 2}, "c": [{"a": 3}]}') == []
