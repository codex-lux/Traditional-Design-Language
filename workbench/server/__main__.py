"""python3 -m workbench.server — the single command that starts the instrument.

Local default is unchanged: 127.0.0.1:8177, the address `make workbench` has always
printed. A container overrides both — WORKBENCH_HOST=0.0.0.0 (set in the Dockerfile)
and PORT, which is injected by the host platform and takes precedence over
WORKBENCH_PORT so a local override never fights a deployed one.
"""
import os
import socket
import sys

HOST = os.environ.get("WORKBENCH_HOST", "127.0.0.1")
# PORT is what Railway/Heroku-style platforms inject; WORKBENCH_PORT stays the local knob.
PORT = int(os.environ.get("PORT") or os.environ.get("WORKBENCH_PORT") or 8177)


def main():
    try:
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError:
        print("The workbench server needs its dependencies:")
        print("    pip install -r workbench/requirements.txt")
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
        print(f"    WORKBENCH_PORT={PORT + 1} python3 -m workbench.server")
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
