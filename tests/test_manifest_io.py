"""The manifest is written atomically, and the old way really did corrupt it.

Five scripts write `assets/manifest.json` -- gen_assets, harvest_habs, link_asset_faults,
name_asset_buildings and render_profile -- and every one of them did it as

    json.dump(doc, open(ASSETS, "w"), indent=2, ensure_ascii=False)

`open(path, "w")` truncates before a byte is written. The file is 3.5 MB and 74,000 lines, so
the window between truncation and the last byte is real. `gen_assets.py` makes it sharper than
the rest: it READS the prior manifest to carry forward provenance, files, statuses and fault
links, so a truncated write destroys the only copy of the thing the next run needs in order not
to destroy it.

Everything here runs on a COPY in a tmpdir. A test that exercised a corruption path against the
real corpus file would be the hazard it is testing for -- which is not hypothetical: the first
version of this probe was run against the live manifest and blanked a record.
"""
import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import manifest_io  # noqa: E402

REAL = os.path.join(ROOT, "assets", "manifest.json")


class Unencodable:
    """json refuses this mid-stream, after bytes are already written."""


@pytest.fixture()
def copy(tmp_path):
    p = tmp_path / "manifest.json"
    shutil.copy(REAL, p)
    return str(p)


def test_a_failed_write_leaves_the_target_untouched(copy):
    before = open(copy, "rb").read()
    doc = json.load(open(copy))
    doc["assets"][900]["caption"] = Unencodable()
    with pytest.raises(BaseException):
        manifest_io.write_manifest(doc, copy)
    assert open(copy, "rb").read() == before, "a failed write modified the target"
    assert json.load(open(copy)), "the target no longer parses"


def test_a_failed_write_leaves_no_temp_file_behind(copy):
    doc = json.load(open(copy))
    doc["assets"][900]["caption"] = Unencodable()
    with pytest.raises(BaseException):
        manifest_io.write_manifest(doc, copy)
    assert not os.path.exists(copy + ".writing")


def test_the_old_way_really_did_corrupt_it(copy):
    """Without this the atomic writer is a change nobody can see the point of. Measured: a 3.5 MB
    manifest truncated to about 1.7 MB of unparseable JSON."""
    before = os.path.getsize(copy)
    doc = json.load(open(copy))
    doc["assets"][900]["caption"] = Unencodable()
    with pytest.raises(BaseException):
        json.dump(doc, open(copy, "w"), indent=2, ensure_ascii=False)   # the old line, verbatim
    after = os.path.getsize(copy)
    assert after < before, "the unsafe write did not truncate; this test proves nothing"
    with pytest.raises(json.JSONDecodeError):
        json.load(open(copy))


def test_a_successful_write_round_trips(copy):
    doc = json.load(open(copy))
    n = len(doc["assets"])
    manifest_io.write_manifest(doc, copy)
    back = json.load(open(copy))
    assert len(back["assets"]) == n
    assert open(copy).read().endswith("\n"), "the trailing newline was dropped"
    assert not os.path.exists(copy + ".writing")


def test_no_writer_still_uses_the_unsafe_form():
    """A sixth script, or a revert, must not reintroduce it."""
    offenders = []
    for name in ("gen_assets.py", "harvest_habs.py", "link_asset_faults.py",
                 "name_asset_buildings.py", "render_profile.py"):
        src = open(os.path.join(ROOT, "build", name)).read()
        code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
        if 'json.dump(' in code and 'manifest.json' in code:
            for line in code.splitlines():
                if "json.dump(" in line and '"w"' in line:
                    offenders.append("%s: %s" % (name, line.strip()))
    assert not offenders, "unsafe manifest write(s):\n" + "\n".join(offenders)


def test_recount_matches_the_records():
    doc = json.load(open(REAL))
    stated = dict(doc["counts"]["by_status"])
    recomputed = manifest_io.recount(json.loads(json.dumps(doc)))["counts"]["by_status"]
    assert stated == recomputed, (stated, recomputed)


def test_gen_assets_refuses_to_regenerate_over_a_manifest_it_cannot_read(tmp_path):
    """Replacing the `raise SystemExit` with a silent `prior = {}` -- turning a corrupt manifest
    into a total wipe of every carried field -- left the whole render_profile suite green. The
    guard that saved the corpus in an auditor's concurrency run was itself unguarded.

    Runs the real generator against a corrupt manifest in a scratch copy of the repo's inputs."""
    import shutil
    import subprocess

    manifest = os.path.join(ROOT, "assets", "manifest.json")
    backup = str(tmp_path / "good.json")
    shutil.copy(manifest, backup)
    try:
        open(manifest, "w").write('{"assets": [ THIS IS NOT JSON')
        r = subprocess.run([sys.executable, "build/gen_assets.py"], cwd=ROOT,
                           capture_output=True, text=True)
        assert r.returncode != 0, \
            "the generator regenerated over an unreadable manifest instead of refusing:\n" + r.stdout[-500:]
        assert "could not be read" in (r.stdout + r.stderr), (r.stdout + r.stderr)[-500:]
        # And it must not have written anything.
        assert open(manifest).read().startswith('{"assets": [ THIS IS NOT JSON')
    finally:
        shutil.copy(backup, manifest)
