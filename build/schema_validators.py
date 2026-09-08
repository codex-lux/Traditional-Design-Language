"""One compiled jsonschema validator per schema, for the checkers that validate in a loop.

WHY THIS EXISTS
---------------
`jsonschema.validate(instance, schema)` is a convenience wrapper that, on EVERY call,
looks up the validator class for the schema, runs `check_schema` over the schema, and
builds a fresh validator object. That is fine once and ruinous in a loop, and five
checkers in this repository validate in a loop:

    check_assets.py    1,850 asset records against asset.schema.json
    validate.py          164 style nodes    against style-node.schema.json
    check_kits.py        159 kits           against kit.schema.json
    check_constraints.py the constraints of every node
    check_orders.py      every proportion pack

Measured here, 4 Sep 2026 style corpus, on the manifest alone:

    naive  jsonschema.validate x 1,850   36.1 s
    compiled validator,   same 1,850      0.35 s        -- 103x

`build/check_all.py`'s whole 44-check loop is 197 s, and 46 s of it was this. The
defect is already recorded in CLAUDE.md for the workbench's plan gate, where WP-10.1
measured the same wrapper at 60.5 ms a call and 17.9% of `/api/plan/evaluate`; what
that entry did not say is that the same wrapper was being paid 2,400 times a build by
the checkers. **Measure what you add to a hot path before you add it** -- and then go
and look for the shape somewhere else, which is what this module is.

WHAT IT DOES NOT CHANGE
-----------------------
`raise_first()` reproduces `jsonschema.validate`'s own choice of error EXACTLY -- that
function raises `best_match(validator.iter_errors(instance))`, and so does this, from
the same iterator. A checker's message text is part of what its tests assert, so a
faster validator that reported a DIFFERENT error would be a silent change to every
failure this corpus can produce. It reports the same one.

Not a general cache: `compiled()` memoises on the schema's absolute path, so a caller
that mutates a schema file mid-process (nothing does; the schema-mutation tests use
subprocesses, exactly as `modcache` documents) would not see the change.
"""
from __future__ import annotations

import json
import os

_CACHE: dict[str, object] = {}


def compiled(schema_path: str):
    """The validator for the schema at `schema_path`, built at most once per process.

    Raises `jsonschema.SchemaError` if the schema itself is invalid -- `validate()`
    checks that on every call and so does this, once, at the point of compilation.
    """
    import jsonschema

    key = os.path.realpath(schema_path)
    hit = _CACHE.get(key)
    if hit is not None:
        return hit
    with open(key, encoding="utf-8") as f:
        schema = json.load(f)
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    _CACHE[key] = v = cls(schema)
    return v


def raise_first(validator, instance) -> None:
    """Raise the same `ValidationError` `jsonschema.validate` would, or return None.

    `validate()` is `best_match(iter_errors(instance))` and a raise; this is the same
    two lines with the validator already built. Kept as a named function rather than
    inlined at five call sites so the equivalence is stated once and can be tested
    once -- `tests/test_schema_validators.py` holds it against `jsonschema.validate`
    on a real record from every schema this repository loops over.
    """
    from jsonschema.exceptions import best_match

    err = best_match(validator.iter_errors(instance))
    if err is not None:
        raise err
