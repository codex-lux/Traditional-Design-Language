"""The citation grammar: kind:id(#fragment)?  — validated against live corpus ids
before a citation is ever streamed. A citation that navigates nowhere is worse than
none, so an unresolvable ref is downgraded to plain text and reported.
"""
import functools
import glob
import json
import os
import re

from . import corpus

core = corpus.core

# ids allow dots: constraint ids are style-id.cNN
REF_RE = re.compile(r"^([a-z]+):([A-Za-z0-9_.-]+)(?:#([A-Za-z0-9_-]+))?$")


def _known_ids(kind):
    D = core._data()
    if kind in ("style", "kit"):
        return D["styles"]
    if kind == "slot":
        return D["slots"]
    if kind == "fault":
        return D["faults"]
    if kind == "room":
        return D["rooms"]
    if kind == "grouping":
        return D["groupings"]
    if kind == "massing":
        return D["massings"]
    if kind == "pack":
        return D["engine"].PACKS
    if kind == "parti":
        return _parti_ids()
    if kind == "constraint":
        return _constraint_ids()
    return None


@functools.lru_cache(maxsize=1)
def _parti_ids():
    out = set()
    for f in sorted(glob.glob(os.path.join(corpus.ROOT, "partis", "*.json"))):
        try:
            out.add(json.load(open(f))["id"])
        except Exception:
            pass
    return out


@functools.lru_cache(maxsize=1)
def _constraint_ids():
    D = core._data()
    out = set()
    for s in D["styles"].values():
        for c in s.get("constraints", []):
            if c.get("id"):
                out.add(c["id"])
    return out


def validate(ref, context=None):
    """→ (ok, reason). context supplies the session-scoped kinds
    (candidate/finding/plan/constraint/brief/asset), which have no corpus registry."""
    m = REF_RE.match(ref or "")
    if not m:
        return False, "not a kind:id ref"
    kind, ident, frag = m.groups()
    ids = _known_ids(kind)
    if ids is not None:
        if ident not in ids:
            return False, f"unknown {kind} id '{ident}'"
        if frag and kind in ("kit", "style") and frag not in core._data()["slots"]:
            return False, f"unknown slot fragment '{frag}'"
        return True, None
    if kind == "candidate":
        n = (context or {}).get("candidate_count")
        if n is not None and (not ident.isdigit() or not (0 <= int(ident) < n)):
            return False, f"candidate {ident} is not in the current set"
        return True, None
    if kind in ("finding", "plan", "brief", "asset"):
        return True, None  # session- or corpus-file-scoped; the client resolves
    return False, f"unknown citation kind '{kind}'"
