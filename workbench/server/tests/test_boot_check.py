"""CI starts the image it builds, and the check that reads a started server can fail.

Deployment-readiness review, 27 Nov 2026 (DR-11). The `image` job ran `docker build` and nothing
else, so a container that could not boot passed CI. These hold three things: the job runs the
boot script against the image it built, the script makes both runs (no password must refuse; a
password must serve), and `boot_check.check` reports each fault it exists for.

No Docker here: the script is read, and `check` is driven with a stand-in for the network.
"""
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _boot_check():
    path = os.path.join(ROOT, "workbench", "scripts", "boot_check.py")
    spec = importlib.util.spec_from_file_location("boot_check", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GOOD_HEALTH = {"ok": True, "auth": {"required": True}, "mcp": {"mounted": True},
               "prover": {"available": True}, "counts": {"styles": 164}, "sha": "abc1234"}
PAGE = b'<!doctype html><html><body><script type="module" src="/assets/index-x.js"></script></body></html>'
PAGE_HEADERS = {"content-type": "text/html; charset=utf-8",
                "content-security-policy": "default-src 'self'; script-src 'self'",
                "x-frame-options": "DENY"}


class Server:
    """A healthy gated server, with one thing breakable at a time."""

    def __init__(self, **broken):
        self.broken = broken
        self.signed_in = False

    def __call__(self, method, path, body=None, cookies=True):
        b = self.broken
        if path == "/api/overview":
            if cookies and self.signed_in:
                return 200, {}, b"{}"
            return (200 if b.get("open") else 401), {}, b"{}"
        if path == "/":
            headers = dict(PAGE_HEADERS)
            for gone in b.get("drop_headers", ()):
                headers.pop(gone)
            return 200, headers, b.get("page", PAGE)
        if path.startswith("/assets/"):
            return (404, {}, b"") if b.get("no_bundle") else (200, {}, b"x" * 5000)
        if path == "/api/login":
            right = body["password"] == "pw"
            if b.get("any_password"):
                right = True
            if right and cookies:
                self.signed_in = True
            return (200 if right else 401), {}, b"{}"
        raise AssertionError(f"unexpected request {method} {path}")


def _run(health=None, password="pw", sha="abc1234", **broken):
    return _boot_check().check(Server(**broken), health or GOOD_HEALTH, password=password, sha=sha)


def test_a_healthy_gated_server_passes():
    assert _run() == []
    assert _run(sha="abc1234def5678") == [], "a full sha against the short one it starts with"


def test_each_fault_it_exists_for_is_reported():
    def one(expect, health=None, **broken):
        bad = _run(health=health, **broken)
        assert any(expect in line for line in bad), (expect, bad)

    one("OPEN", health={**GOOD_HEALTH, "auth": {"required": False}})
    one("not the build asked for", health={**GOOD_HEALTH, "sha": "fffffff"})
    one("not the build asked for", health={**GOOD_HEALTH, "sha": ""})
    one("/mcp is not mounted", health={**GOOD_HEALTH, "mcp": {"mounted": False}})
    one("prover is not available", health={**GOOD_HEALTH, "prover": {"available": False}})
    one("mcp.allowed_origins", health={**GOOD_HEALTH, "mcp": {"mounted": True, "allowed_origins": []}})
    one("answered 200, not 401", open=True)
    one("no content security policy", drop_headers=("content-security-policy",))
    one("may be framed", drop_headers=("x-frame-options",))
    one("names no built script", page=b"<html><body>api only</body></html>")
    one("answered 404", no_bundle=True)
    one("loads from outside the app",
        page=PAGE + b'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">')
    one("a wrong password answered 200", any_password=True)


def test_without_a_password_the_sign_in_is_not_tried_and_nothing_else_is_skipped():
    mod = _boot_check()
    assert mod.check(Server(), GOOD_HEALTH, password=None, sha=None) == []


def test_a_server_that_never_answers_is_a_failure_and_not_a_wait_for_ever():
    mod = _boot_check()
    ticks = iter(range(100))
    calls = []

    def refused(method, path, body=None, cookies=True):
        calls.append(path)
        raise ConnectionRefusedError()

    got = mod.wait_for_health(refused, 3, sleep=lambda s: None, clock=lambda: next(ticks))
    assert got is None and calls, "it must try, and must give up"
    up = mod.wait_for_health(lambda *a, **k: (200, {}, json.dumps(GOOD_HEALTH).encode()), 3)
    assert up == GOOD_HEALTH


def test_the_boot_script_makes_both_runs_and_prints_no_secret():
    sh = _read("workbench", "scripts", "image_boot.sh")
    runs = [l for l in sh.splitlines() if "docker run" in l and not l.lstrip().startswith("#")]
    assert len(runs) == 2, runs
    assert "WORKBENCH_PASSWORD" not in runs[0], "the first run must carry no password"
    assert '-e WORKBENCH_PASSWORD="$PASSWORD"' in sh, "the second run must carry one"
    assert "boot_check.py" in sh
    for line in sh.splitlines():
        if line.lstrip().startswith("echo"):
            assert "$PASSWORD" not in line and "$SECRET" not in line, line
    assert "set -x" not in sh, "tracing would print the password"


def test_ci_boots_the_image_it_builds_at_the_commit_it_built():
    ci = _read(".github", "workflows", "ci.yml")
    job = ci.split("\n  image:\n", 1)[1]
    job = job.split("\n  deploy-gate:\n", 1)[0]
    lines = [l.strip() for l in job.splitlines() if l.strip().startswith("run:")]
    build = [l for l in lines if "docker build" in l]
    assert len(build) == 1 and "--build-arg GIT_SHA=" in build[0], build
    tag = build[0].split("-t ", 1)[1].split()[0]
    boot = [l for l in lines if "image_boot.sh" in l]
    assert len(boot) == 1 and tag in boot[0], (tag, boot)
    assert "github.sha" in boot[0], "the boot must hold the image to the commit"
