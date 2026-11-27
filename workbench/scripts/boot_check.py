#!/usr/bin/env python3
"""Is a started Workbench the one that was built, and is it gated?

Deployment-readiness review, 27 Nov 2026 (DR-11). CI built the image and never started it, so a
container that could not boot passed. `image_boot.sh` starts the image and runs this against it.
The same checks are the pre-launch checklist's step 5, so this can be pointed at any base URL an
operator may probe:

    python3 workbench/scripts/boot_check.py http://127.0.0.1:8177 --password ... [--sha abc1234]

Standard library only: it runs in the bare `image` job, which installs nothing.

It reads; the one write is a sign-in with the password it was given. It prints no secret.
"""
import argparse
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.request


class Http:
    """One cookie jar, no redirects followed blindly, every answer as (status, headers, body)."""

    def __init__(self, base, timeout=20):
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def __call__(self, method, path, body=None, cookies=True):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"content-type": "application/json"} if data else {})
        opener = self.opener if cookies else urllib.request.build_opener()
        try:
            with opener.open(req, timeout=self.timeout) as r:
                return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
        except urllib.error.HTTPError as e:
            return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read()


def wait_for_health(fetch, seconds, sleep=time.sleep, clock=time.monotonic):
    """The first 200 from /api/health, or None. A refused connection is the server not up yet."""
    end = clock() + seconds
    while True:
        try:
            status, _h, body = fetch("GET", "/api/health", cookies=False)
            if status == 200:
                return json.loads(body)
        except (OSError, ValueError):
            pass
        if clock() >= end:
            return None
        sleep(1.0)


def check(fetch, health, password=None, sha=None):
    """Every failure as a sentence. An empty list is a pass; nothing here stops at the first."""
    bad = []

    def want(ok, sentence):
        if not ok:
            bad.append(sentence)

    want(health.get("ok") is True, f"/api/health does not say ok: {health.get('ok')!r}")
    want((health.get("auth") or {}).get("required") is True,
         "the server is OPEN: /api/health reports auth.required is not true")
    want((health.get("mcp") or {}).get("mounted") is True, "/mcp is not mounted")
    want((health.get("prover") or {}).get("available") is True,
         "the prover is not available (ortools did not import in this build)")
    want((health.get("counts") or {}).get("styles", 0) > 0, "the corpus loaded no styles")
    if sha:
        got = str(health.get("sha") or "")
        want(bool(got) and (got.startswith(sha) or sha.startswith(got)),
             f"this is not the build asked for: sha {got!r}, wanted {sha!r}")
    for key in ("allowed_hosts", "allowed_origins"):
        want(key not in (health.get("mcp") or {}), f"signed out, /api/health serves mcp.{key}")

    status, _h, _b = fetch("GET", "/api/overview", cookies=False)
    want(status == 401, f"signed out, /api/overview answered {status}, not 401")

    status, headers, body = fetch("GET", "/", cookies=False)
    page = body.decode("utf-8", "replace")
    want(status == 200 and "text/html" in headers.get("content-type", ""),
         f"/ did not serve the app: {status} {headers.get('content-type')!r}")
    csp = headers.get("content-security-policy", "")
    want("script-src 'self'" in csp, "the page carries no content security policy")
    want(headers.get("x-frame-options", "").upper() == "DENY", "the page may be framed")
    scripts = re.findall(r'<script[^>]+src="(/assets/[^"]+)"', page)
    want(bool(scripts), "the page names no built script: the app was not built into this image")
    for src in scripts[:1]:
        s, _h2, b = fetch("GET", src, cookies=False)
        want(s == 200 and len(b) > 1000, f"the app's script {src} answered {s}, {len(b)} bytes")
    outside = re.findall(r'(?:href|src)="((?:https?:)?//[^"]+)"', page)
    want(not outside, f"the page loads from outside the app: {outside}")

    if password:
        status, _h, _b = fetch("POST", "/api/login", {"password": password + "-wrong"}, cookies=False)
        want(status == 401, f"a wrong password answered {status}, not 401")
        status, _h, _b = fetch("POST", "/api/login", {"password": password})
        want(status == 200, f"the right password answered {status}, not 200")
        status, _h, body = fetch("GET", "/api/overview")
        want(status == 200, f"signed in, /api/overview answered {status}")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base")
    ap.add_argument("--password", help="sign in with it and read one gated route")
    ap.add_argument("--sha", help="the commit this build must report")
    ap.add_argument("--wait", type=float, default=60.0, help="seconds to wait for the first 200")
    a = ap.parse_args(argv)
    fetch = Http(a.base)
    health = wait_for_health(fetch, a.wait)
    if health is None:
        print(f"FAIL: {a.base}/api/health did not answer 200 within {a.wait:.0f} s")
        return 1
    bad = check(fetch, health, password=a.password, sha=a.sha)
    for line in bad:
        print("FAIL:", line)
    if bad:
        return 1
    print(f"OK: {a.base} is up, gated and serving the app"
          + (f" at {health.get('sha')}" if health.get("sha") else "")
          + ("" if a.password else " (no password given: sign-in not tried)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
