"""/api/health names the build that answered, and never with a blank (WP-13.2).

WP-13.1 could not say which build drew the sheet Lucas read: the health endpoint reported what
the server could do and nothing about what it WAS. The key is `sha`; `sha_source` says which of
three sources answered -- the image's stamp (`TDL_GIT_SHA`), git at the checkout, or neither, in
which case the sha is the word "unknown". A named unknown, never an empty string.

Three things are held here that no single assertion covers:
  * the ROUTE carries the key and it is non-empty, whatever this machine can answer;
  * the READER prefers the stamp, falls through a blank stamp, asks git where it can, and
    lands on "unknown" when neither answers -- each branch driven, not inferred;
  * the value is read ONCE at import, so a variable changed under a running process does not
    make the endpoint describe two builds;
  * the Dockerfile's `ENV` names the same variable the server reads. Two spellings in two
    languages, held together the way test_grammar_agreement.py holds the citation grammar.
"""
import os
import re
import shutil
import subprocess

import pytest

from workbench.server import app as appmod
from workbench.server import corpus

SHA_SHAPE = re.compile(r"^(?:[0-9a-f]{7,40}|unknown)$")


def _git_short_head(root):
    """An INDEPENDENT reading of the checkout, so the test is not the code under test."""
    if not shutil.which("git"):
        return None
    r = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


# ---------------------------------------------------------------- the route
def test_health_carries_a_build_sha_and_it_is_never_empty(client):
    body = client.get("/api/health").json()
    assert "sha" in body, "the health payload no longer names the build"
    sha = body["sha"]
    assert isinstance(sha, str) and sha.strip() == sha and sha, (
        f"sha must be a non-empty string with no padding; got {sha!r}")
    assert SHA_SHAPE.match(sha), (
        f"sha is neither a hex commit nor the word 'unknown': {sha!r}")
    assert body["sha_source"] in ("env", "git", None), body["sha_source"]
    # the two fields agree: an unknown sha has no source, and a known one names its source
    assert (sha == appmod.SHA_UNKNOWN) == (body["sha_source"] is None), (sha, body["sha_source"])


def test_the_served_sha_is_what_this_checkout_can_answer(client):
    """Not a fixed literal: what git says about THIS tree, or 'unknown' where git cannot."""
    body = client.get("/api/health").json()
    expected = _git_short_head(corpus.ROOT)
    if os.environ.get(appmod.SHA_VAR, "").strip() not in ("", appmod.SHA_UNKNOWN):
        pytest.skip(f"{appmod.SHA_VAR} is set in this environment, so the stamp outranks git "
                    f"here -- the env branch is driven below")
    if expected is None:
        assert body["sha"] == appmod.SHA_UNKNOWN and body["sha_source"] is None
    else:
        assert body["sha"] == expected and body["sha_source"] == "git"


# ---------------------------------------------------------------- the reader, each branch
def test_the_stamp_outranks_git(monkeypatch):
    monkeypatch.setenv(appmod.SHA_VAR, "  deadbee ")
    assert appmod._build_sha() == ("deadbee", "env"), "a stamped sha is stripped and preferred"


@pytest.mark.parametrize("blank", ["", "   ", "unknown", " unknown "])
def test_a_blank_or_default_stamp_falls_through_to_git(monkeypatch, blank):
    """The Dockerfile's ARG default IS the word 'unknown', so an unstamped image sets the
    variable to it: that must fall through, not be reported as a sha somebody chose."""
    monkeypatch.setenv(appmod.SHA_VAR, blank)
    sha, source = appmod._build_sha()
    expected = _git_short_head(corpus.ROOT)
    if expected is None:
        assert (sha, source) == (appmod.SHA_UNKNOWN, None)
    else:
        assert (sha, source) == (expected, "git")


def test_no_checkout_and_no_stamp_is_the_named_unknown(monkeypatch, tmp_path):
    monkeypatch.delenv(appmod.SHA_VAR, raising=False)
    assert appmod._build_sha(root=str(tmp_path)) == (appmod.SHA_UNKNOWN, None)


def test_no_git_binary_is_the_named_unknown_too(monkeypatch, tmp_path):
    """A container without git must not raise at import, and must not answer ''."""
    monkeypatch.delenv(appmod.SHA_VAR, raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))          # nothing on it, git included
    sha, source = appmod._build_sha()
    assert sha == appmod.SHA_UNKNOWN and source is None
    assert sha != ""


# ---------------------------------------------------------------- read once
def test_the_sha_is_read_once_at_import_not_per_request(client, monkeypatch):
    """A build identity that moved under a running process would be one endpoint describing
    two builds. The served value is the module constant, whatever the environment says now."""
    before = client.get("/api/health").json()["sha"]
    monkeypatch.setenv(appmod.SHA_VAR, "0badf00d")
    after = client.get("/api/health").json()["sha"]
    assert before == after == appmod.BUILD_SHA
    assert after != "0badf00d"


# ---------------------------------------------------------------- the Dockerfile agrees
def test_the_dockerfile_stamps_the_variable_the_server_reads():
    """`ENV TDL_GIT_SHA=$GIT_SHA` in the image and `SHA_VAR` in the server are one variable
    spelled twice. This is the seam: a rename on either side leaves the image stamping a
    variable nobody reads and /api/health answering 'unknown' on every deploy, silently."""
    path = os.path.join(corpus.ROOT, "Dockerfile")
    text = open(path, encoding="utf-8").read()
    arg = re.search(r"^ARG\s+(\w+)=(\S+)\s*$", text, re.M)
    assert arg, "the Dockerfile declares no ARG for the build sha"
    assert arg.group(2) == appmod.SHA_UNKNOWN, (
        f"the ARG default must be the server's own unknown word so an unstamped image falls "
        f"through; it is {arg.group(2)!r}")
    env = re.search(r"^ENV\s+(\w+)=\$" + re.escape(arg.group(1)) + r"\s*$", text, re.M)
    assert env, f"no ENV line carries ${arg.group(1)} into the image"
    assert env.group(1) == appmod.SHA_VAR, (
        f"the image stamps {env.group(1)} and the server reads {appmod.SHA_VAR}")
