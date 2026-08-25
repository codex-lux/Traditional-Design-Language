"""python3 -m workbench.server — the single command that starts the instrument."""
import os
import sys


def main():
    try:
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError:
        print("The workbench server needs its dependencies:")
        print("    pip install -r workbench/requirements.txt")
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(os.path.dirname(here), "app", "dist")
    if not os.path.isdir(dist):
        print("note: no built app found at workbench/app/dist —")
        print("      cd workbench/app && npm install && npm run build")
        print("      (the JSON API will serve regardless)")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("note: ANTHROPIC_API_KEY is not set — the AI rail will say so and stay off.")

    print("The Workbench · http://127.0.0.1:8177")
    uvicorn.run("workbench.server.app:app", host="127.0.0.1", port=8177, log_level="warning")


if __name__ == "__main__":
    main()
