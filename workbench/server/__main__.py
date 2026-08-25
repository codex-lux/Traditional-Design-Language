"""python3 -m workbench.server — the single command that starts the instrument."""
import os
import socket
import sys

PORT = int(os.environ.get("WORKBENCH_PORT", "8177"))


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
        probe.bind(("127.0.0.1", PORT))
    except OSError as e:
        print(f"Cannot bind 127.0.0.1:{PORT} — {e.strerror or e}.")
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

    print(f"The Workbench · http://127.0.0.1:{PORT}")
    uvicorn.run("workbench.server.app:app", host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
