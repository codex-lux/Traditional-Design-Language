"""The image installs a pinned closure, and CI tests the same pins.

Deployment-readiness review, 27 Nov 2026 (DR-02). `workbench/requirements.txt` states floors, and
the Dockerfile installed it directly, so the image resolved afresh on every build: it could ship
versions no CI job had run, and rebuilding an old commit did not rebuild the old image. The
file's own comments record two breaks of that kind (the `mcp` 2.0 rename, `anthropic` 0.x).

These tests read files only. They need no network and no installer.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
WB = os.path.join(ROOT, "workbench")

PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s\\;]+)", re.M)


def _read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def _norm(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _pins(lock_name):
    return {_norm(n): v for n, v in PIN.findall(_read(WB, lock_name))}


def _top_level(req_name):
    """The package names a requirements file asks for itself (not through `-r`)."""
    out = []
    for line in _read(WB, req_name).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        out.append(_norm(re.split(r"[\[<>=!~ ]", line, maxsplit=1)[0]))
    return out


def test_every_runtime_requirement_is_pinned_in_the_lock():
    pins = _pins("requirements.lock")
    asked = _top_level("requirements.txt")
    assert asked, "requirements.txt names no package: the reader is broken, not the lock"
    missing = [n for n in asked if n not in pins]
    assert not missing, f"asked for in requirements.txt and not pinned in requirements.lock: {missing}"


def test_every_pin_carries_a_hash():
    for lock in ("requirements.lock", "requirements-dev.lock"):
        text = _read(WB, lock)
        blocks = re.split(r"\n(?=[A-Za-z0-9])", text)
        bare = [b.split("==")[0] for b in blocks if "==" in b and "--hash=sha256:" not in b]
        assert not bare, f"{lock}: pinned without a hash, so --require-hashes refuses the file: {bare}"


def test_ci_tests_the_versions_the_image_ships():
    """requirements-dev.lock is the runtime lock plus the test packages, at the SAME versions."""
    run, dev = _pins("requirements.lock"), _pins("requirements-dev.lock")
    assert len(run) > 20, "the runtime lock holds too few pins to be a whole closure"
    drift = {n: (v, dev.get(n)) for n, v in run.items() if dev.get(n) != v}
    assert not drift, f"runtime pin against dev pin (run `make lock`): {drift}"
    for name in _top_level("requirements-dev.txt"):
        assert name in dev, f"{name} is asked for in requirements-dev.txt and not pinned"
        assert name not in run, f"{name} is a test package and is pinned into the image"


def test_the_dockerfile_installs_the_lock_and_not_the_floors():
    docker = _read(ROOT, "Dockerfile")
    installs = [l.strip() for l in docker.splitlines()
                if l.strip().startswith("RUN") and "pip install" in l]
    assert installs, "the Dockerfile has no pip install line: the reader is broken"
    for line in installs:
        assert "--require-hashes" in line and "workbench/requirements.lock" in line, line
        assert "requirements.txt" not in line, f"the image installs unpinned floors: {line}"


def test_ci_installs_the_dev_lock_for_the_server_suite():
    ci = _read(ROOT, ".github", "workflows", "ci.yml")
    job = ci.split("\n  workbench:\n", 1)[1].split("\n  image:\n", 1)[0]
    runs = [l.strip() for l in job.splitlines() if l.strip().startswith("run: pip install")]
    assert runs == ["run: pip install --require-hashes -r workbench/requirements-dev.lock"], runs

