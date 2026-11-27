"""python3 -m workbench.server — the single command that starts the instrument.

Local default is unchanged: 127.0.0.1:8177, the address `make workbench` has always
printed. A container overrides both — WORKBENCH_HOST=0.0.0.0 (set in the Dockerfile)
and PORT, which is injected by the host platform and takes precedence over
WORKBENCH_PORT so a local override never fights a deployed one.
"""
import os
import socket
import sys

from .bind import LOOPBACK, host as _host   # no dependencies: safe before the import check

HOST = _host()
# PORT is what Railway/Heroku-style platforms inject; WORKBENCH_PORT stays the local knob.
PORT = int(os.environ.get("PORT") or os.environ.get("WORKBENCH_PORT") or 8177)


ALLOW_OPEN_VAR = "WORKBENCH_ALLOW_OPEN"


def open_bind_refusal(host):
    """Why this bind may not start, or None.

    A PUBLIC BIND WITH NO GATE IS REFUSED (deployment-readiness review, 27 Nov 2026, DR-01).
    `auth.required()` is false when neither WORKBENCH_PASSWORD nor WORKBENCH_API_TOKEN is set,
    and the server is then open: the local default, on purpose. The Dockerfile sets
    WORKBENCH_HOST=0.0.0.0, so in a container one forgotten variable served every /api route,
    /mcp and the assistant -- which spends the operator's Anthropic key -- to anyone who could
    reach it, behind the one-line note below. An absent check is not a passed one, and a note in
    a log nobody is reading is not a refusal.

    Loopback is unchanged. Open on purpose is still expressible, by saying so:
    WORKBENCH_ALLOW_OPEN=1. `auth.required` is asked rather than the two variables read again,
    so this cannot disagree with the gate about what a gate is. WORKBENCH_TRUST_PROXY_AUTH is
    deliberately not one: alone it leaves `required()` false and the server open.
    """
    if host in LOOPBACK:
        return None
    from . import auth
    if auth.required():
        return None
    if (os.environ.get(ALLOW_OPEN_VAR) or "").strip().lower() in ("1", "true", "yes", "on"):
        return None
    return (f"Refusing to serve on {host} with no password: every /api route, /mcp and the AI "
            f"assistant would answer anyone who can reach this address.\n"
            f"    Set WORKBENCH_PASSWORD (and WORKBENCH_API_TOKEN for agents), or\n"
            f"    set {ALLOW_OPEN_VAR}=1 to serve it open on purpose.")


def main():
    try:
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError:
        print("The workbench server needs its dependencies:")
        print("    pip install -r workbench/requirements.txt")
        sys.exit(1)

    # Before the bind probe: a server that will not serve should not touch the port.
    refusal = open_bind_refusal(HOST)
    if refusal:
        print(refusal)
        sys.exit(1)

    # uvicorn.run RETURNS (exit code 0) on a failed bind, which reads as success.
    # Probe the bind first so a taken port fails loudly, with the remedy named.
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind((HOST, PORT))
    except OSError as e:
        print(f"Cannot bind {HOST}:{PORT} — {e.strerror or e}.")
        print("Something else is using the port. Stop it, or pick another:")
        # Name the variable that actually wins, or the advice is a no-op in exactly the
        # case where it is given: PORT outranks WORKBENCH_PORT.
        var = "PORT" if os.environ.get("PORT") else "WORKBENCH_PORT"
        print(f"    {var}={PORT + 1} python3 -m workbench.server")
        sys.exit(1)
    finally:
        probe.close()

    here = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(os.path.dirname(here), "app", "dist")
    if not os.path.isdir(dist):
        print("note: no built app found at workbench/app/dist —")
        print("      cd workbench/app && npm install && npm run build")
        print("      (the JSON API will serve regardless)")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("note: ANTHROPIC_API_KEY is not set — the AI rail will say so and stay off.")
    if not os.environ.get("WORKBENCH_PASSWORD"):
        print("note: WORKBENCH_PASSWORD is not set — the server is OPEN to anyone who "
              "can reach it.")

    shown = "127.0.0.1" if HOST in ("0.0.0.0", "::") else HOST
    print(f"The Workbench · http://{shown}:{PORT}")
    # proxy_headers/forwarded_allow_ips: behind a platform proxy the peer address is the
    # proxy's. Without these X-Forwarded-For is ignored and every caller shares one
    # identity, which would collapse the rail's per-user rate limit into a global one.
    uvicorn.run("workbench.server.app:app", host=HOST, port=PORT, log_level="warning",
                proxy_headers=True, forwarded_allow_ips="*")


if __name__ == "__main__":
    main()
