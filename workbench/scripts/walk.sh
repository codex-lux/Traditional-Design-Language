#!/usr/bin/env bash
# Serve the built app and walk every surface with a real browser (e2e/walk.mjs), which is
# where the drawing itself is measured: labels inside their rooms, the order contiguous
# and at the right datum, the loupe magnifying, the wall handle still grabbable. Exits
# non-zero on any failed check.
set -euo pipefail
cd "$(dirname "$0")/../.."

PORT="${WALK_PORT:-8179}"
if [ ! -d workbench/app/dist ]; then
  echo "workbench/app/dist is missing — run npm run build in workbench/app first" >&2
  exit 1
fi
python3 -m uvicorn workbench.server.app:app --host 127.0.0.1 --port "$PORT" --log-level error &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
for _ in $(seq 1 60); do
  curl -sf "http://127.0.0.1:$PORT/api/health" >/dev/null && break
  sleep 0.5
done
curl -sf "http://127.0.0.1:$PORT/api/health" >/dev/null || { echo "server never came up" >&2; exit 1; }

cd workbench/app
# Exit 3 is the walk's COULD NOT EVALUATE: something it was asked to judge could not be
# judged. It is not a pass and it is not a code failure; `set -e` above would already stop
# the job, and this says which of the two it was.
#
# IT HAS TWO CAUSES NOW AND THIS LINE NAMED ONLY THE FIRST (WP-13.4). The original was the
# rate limiter — 60 heavy calls an hour per identity, spent by iterating on the walk. The
# second is a server that does not answer WP-13.4's refusal contract, on which the checks
# for a refused placement have no precondition to run against. The walk prints which on
# stderr with the list; this wrapper no longer asserts a cause it cannot know.
WB_URL="http://127.0.0.1:$PORT" node e2e/walk.mjs || {
  rc=$?
  [ "$rc" = 3 ] && echo "walk COULD NOT EVALUATE — not a pass; its own output says what" >&2
  exit $rc
}
