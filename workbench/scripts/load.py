#!/usr/bin/env python3
"""Where the workbench's concurrency ceiling actually is, measured rather than assumed.

Standard library only, like everything else in build/ — a collaborator can run this on a
clone with no install beyond the server's own requirements.

Two questions, and they need different instruments:

  --sweep  How does latency degrade as concurrent callers rise? Fires a fixed number of
           requests at a set of endpoints across a concurrency ladder and reports the
           percentiles. The knee is the answer to "how many users before it lags."

  --sse    Does an open event stream cost a thread? Holds N compose streams open and asks
           whether /api/health still answers. This is a different failure from slowness:
           past the anyio threadpool limit the server does not get slower, it stops, and
           /api/health is what the platform healthcheck polls — so the visible symptom is
           the container being restarted rather than anything naming SSE.

Run it against a server you started yourself:

    python3 -m uvicorn workbench.server.app:app --port 8178 &
    python3 workbench/scripts/load.py --sweep --url http://127.0.0.1:8178

Percentiles come from three runs per point by default; the spread is printed beside them,
because a knee read off one sample is a guess with a decimal place on it.
"""
import argparse
import gzip
import json
import os
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ------------------------------------------------------------------ the calls

# ACCEPT-ENCODING, because urllib sends none by default and that quietly invalidated a whole
# measurement pass: every sweep — including the "after" run used to say the fixes cost nothing
# — exercised the UNCOMPRESSED path, so the one change most likely to move per-request CPU was
# never touched by the instrument used to bless it. A real browser always asks for gzip.
_HEADERS = {"accept-encoding": "gzip"}


def _read(r):
    """The body, decompressed if the server compressed it. Timing INCLUDES the decompress,
    which is what a client actually pays."""
    body = r.read()
    if (r.headers.get("content-encoding") or "").lower() == "gzip":
        body = gzip.decompress(body)
    return body


def _post(url, path, payload, timeout=120):
    req = urllib.request.Request(url + path, data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", **_HEADERS})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, _read(r)


def _get(url, path, timeout=120):
    req = urllib.request.Request(url + path, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, _read(r)


def _plan():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


def _brief():
    return json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))


_UNIQ = [0]
_UNIQ_LOCK = threading.Lock()


def _fresh_plan():
    """A plan no solve has seen before.

    build/geometry.py keys `_SOLVE_CACHE` on a sha256 OF `json.dumps(plan, sort_keys=True)`
    — it was the raw string when this comment was first written, and the mechanism is the
    same either way — so replaying one identical plan measures the cache and not the solver. The first version
    of this harness did exactly that and reported POST /api/drawings/plan at 5.0 ms p50 —
    faster than a kit lookup, for an endpoint that solves a plan and renders an SVG. Any
    change to the record busts the key; the id is the one field nothing else reads.
    """
    plan = _plan()
    with _UNIQ_LOCK:
        _UNIQ[0] += 1
        n = _UNIQ[0]
    plan["id"] = f"{plan.get('id', 'plan')}-load-{n}"
    return plan


def endpoints(url):
    """Five calls spanning the cost range, cheapest first. Each returns a thunk."""
    return [
        ("GET  /api/health", lambda: _get(url, "/api/health")),
        ("GET  /api/search/index", lambda: _get(url, "/api/search/index")),
        ("GET  /api/kit/tidewater-georgian", lambda: _get(url, "/api/kit/tidewater-georgian")),
        ("POST /api/plan/evaluate", lambda: _post(url, "/api/plan/evaluate",
                                                  {"plan": _fresh_plan(), "place": True,
                                                   "candidates": 250})),
        ("POST /api/drawings/plan", lambda: _post(url, "/api/drawings/plan",
                                                  {"plan": _fresh_plan(), "candidates": 250})),
    ]


# ------------------------------------------------------------------ the sweep

def _one_round(thunk, concurrency, requests):
    """Fire `requests` calls with `concurrency` in flight. Returns latencies in ms."""
    lat, errs = [], []
    lock = threading.Lock()

    def call(_):
        t0 = time.perf_counter()
        try:
            status, _body = thunk()
            dt = (time.perf_counter() - t0) * 1000
            with lock:
                (lat if status == 200 else errs).append(dt if status == 200 else status)
        except Exception as e:                                   # noqa: BLE001
            with lock:
                errs.append(type(e).__name__)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(call, range(requests)))
    return lat, errs


def _pct(xs, p):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def sweep(url, ladder, requests, runs):
    print(f"\n{'endpoint':38s} {'conc':>5s} {'n':>5s} {'p50':>9s} {'p95':>9s} "
          f"{'p99':>9s} {'rps':>8s} {'err':>5s}   spread(p95)")
    print("-" * 108)
    results = {}
    for name, thunk in endpoints(url):
        for c in ladder:
            p50s, p95s, p99s, rpss, errc = [], [], [], [], 0
            for _ in range(runs):
                t0 = time.perf_counter()
                lat, errs = _one_round(thunk, c, requests)
                wall = time.perf_counter() - t0
                errc += len(errs)
                if lat:
                    p50s.append(_pct(lat, 50)); p95s.append(_pct(lat, 95))
                    p99s.append(_pct(lat, 99)); rpss.append(len(lat) / wall)
            if not p50s:
                print(f"{name:38s} {c:5d} {requests:5d} {'ALL FAILED':>39s} {errc:5d}")
                continue
            spread = (max(p95s) - min(p95s)) if len(p95s) > 1 else 0.0
            print(f"{name:38s} {c:5d} {requests:5d} "
                  f"{statistics.median(p50s):9.1f} {statistics.median(p95s):9.1f} "
                  f"{statistics.median(p99s):9.1f} {statistics.median(rpss):8.1f} "
                  f"{errc:5d}   +/-{spread:.1f} ms")
            results[(name, c)] = {"p50": statistics.median(p50s),
                                  "p95": statistics.median(p95s),
                                  "p99": statistics.median(p99s),
                                  "rps": statistics.median(rpss), "errors": errc}
    return results


# ------------------------------------------------------------------ the SSE case

def _job_alive(url, job):
    try:
        _s, b = _get(url, f"/api/jobs/{job}", timeout=10)
        return json.loads(b).get("status") in ("queued", "running")
    except Exception:                                            # noqa: BLE001
        return False


def sse_exhaustion(url, streams, health_timeout=10.0, jobs_deep=6):
    """Hold `streams` compose event streams open, then time /api/health.

    A stream that costs a threadpool token contends for the shared anyio pool (40 by
    default) with every sync `def` endpoint — health included. A stream that costs nothing
    but a coroutine does not.

    THE GUARD MATTERS MORE THAN THE MEASUREMENT. The streams only hold anything while
    there is a job for them to watch, and a compose finishes in seconds. The first version
    of this function slept three seconds, probed health, and printed a number — and at 80
    and 120 streams it printed FOUR MILLISECONDS, faster than the eight-stream case,
    because the job had already finished, every stream had closed, and it was timing an
    idle server. A load test that reports its most-loaded points as its fastest is
    measuring nothing, so this checks the job is still running on BOTH sides of the probe
    and reports COULD NOT EVALUATE rather than a number it cannot stand behind.
    """
    print(f"\n— holding {streams} event streams open, then asking /api/health")

    # Several composes, not one: the pool is one worker wide, so they queue and the last
    # one keeps the registry busy long enough to probe under load.
    job = None
    try:
        for _ in range(jobs_deep):
            _s, body = _post(url, "/api/compose", {"brief": _brief(), "candidates": 8})
            job = json.loads(body)["job_id"]                     # watch the LAST one
    except Exception as e:                                       # noqa: BLE001
        print(f"  COULD NOT EVALUATE — no job to attach to: {type(e).__name__}: {e}")
        return None

    held, stop = [], threading.Event()

    def hold():
        try:
            r = urllib.request.urlopen(f"{url}/api/jobs/{job}/events", timeout=90)
            held.append(r)
            while not stop.is_set():
                if not r.readline():
                    break
        except Exception:                                        # noqa: BLE001
            pass

    threads = [threading.Thread(target=hold, daemon=True) for _ in range(streams)]
    for t in threads:
        t.start()
    time.sleep(3.0)                      # let the streams actually attach
    attached = len(held)
    alive_before = _job_alive(url, job)

    t0 = time.perf_counter()
    try:
        status, _ = _get(url, "/api/health", timeout=health_timeout)
        dt = (time.perf_counter() - t0) * 1000
        verdict, ok = f"answered {status} in {dt:.0f} ms", True
    except Exception as e:                                       # noqa: BLE001
        dt = (time.perf_counter() - t0) * 1000
        verdict, ok = f"DID NOT ANSWER within {health_timeout:.0f}s ({type(e).__name__})", False
    alive_after = _job_alive(url, job)

    stop.set()
    for r in held:
        try:
            r.close()
        except Exception:                                        # noqa: BLE001
            pass

    print(f"  streams attached: {attached}/{streams}")
    if not (alive_before and alive_after):
        print("  COULD NOT EVALUATE — the job finished during the probe, so the streams "
              "had closed and this would have timed an idle server")
        return {"streams": streams, "attached": attached, "unjudged": True,
                "reason": "job not running across the probe"}
    print(f"  /api/health: {verdict}")
    return {"streams": streams, "attached": attached, "health_ms": dt, "ok": ok,
            "unjudged": False}


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("LOAD_URL", "http://127.0.0.1:8178"))
    ap.add_argument("--sweep", action="store_true", help="the concurrency ladder")
    ap.add_argument("--sse", action="store_true", help="the event-stream exhaustion case")
    ap.add_argument("--ladder", default="1,2,4,8,16,32",
                    help="comma-separated concurrency levels")
    ap.add_argument("--requests", type=int, default=24, help="requests per point")
    ap.add_argument("--runs", type=int, default=3, help="repeats per point")
    ap.add_argument("--streams", type=int, default=48,
                    help="open streams for --sse (default 48: past anyio's 40)")
    ap.add_argument("--json", help="write the numbers here as well as printing them")
    a = ap.parse_args()

    if not (a.sweep or a.sse):
        ap.error("nothing to do — pass --sweep and/or --sse")

    try:
        _get(a.url, "/api/health", timeout=10)
    except Exception as e:                                       # noqa: BLE001
        print(f"no server at {a.url} ({type(e).__name__}). Start one:\n"
              f"  python3 -m uvicorn workbench.server.app:app --port 8178", file=sys.stderr)
        return 2

    out = {"url": a.url}
    if a.sweep:
        ladder = [int(x) for x in a.ladder.split(",") if x.strip()]
        got = sweep(a.url, ladder, a.requests, a.runs)
        out["sweep"] = {f"{k[0]}|{k[1]}": v for k, v in got.items()}
    if a.sse:
        out["sse"] = sse_exhaustion(a.url, a.streams)

    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
