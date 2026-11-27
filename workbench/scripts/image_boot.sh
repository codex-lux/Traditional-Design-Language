#!/usr/bin/env bash
# Start the built image and prove it serves (deployment-readiness review, DR-11).
#
#   bash workbench/scripts/image_boot.sh <image> [<git-sha>]
#
# Two runs, because the image makes two promises:
#   1. With no password it does NOT start. The image binds 0.0.0.0, and DR-01 made a public bind
#      with no gate a refusal; an image that boots open has lost that.
#   2. With a password it comes up, reports the commit it was built from, refuses a signed-out
#      caller, serves the built app and signs a caller in (boot_check.py).
#
# The password and secret are random and live for this run only. Neither is printed.
set -euo pipefail
cd "$(dirname "$0")/../.."

IMAGE="${1:?usage: image_boot.sh <image> [<git-sha>]}"
SHA="${2:-}"
PORT="${BOOT_PORT:-18177}"
NAME="tdl-boot-$$"

echo "— 1. no password: the image must refuse to start"
set +e
out="$(timeout 60 docker run --rm -e PORT=8177 "$IMAGE" 2>&1)"
code=$?
set -e
if [ "$code" -eq 0 ] || [ "$code" -eq 124 ]; then
  echo "FAIL: the image started (or kept running) with no WORKBENCH_PASSWORD (exit $code)"
  echo "$out" | tail -20
  exit 1
fi
if ! echo "$out" | grep -q "WORKBENCH_PASSWORD"; then
  echo "FAIL: the image exited $code without naming the variable it wants:"
  echo "$out" | tail -20
  exit 1
fi
echo "ok · exit $code, and the message names WORKBENCH_PASSWORD"

echo "— 2. with a password: up, gated, the right build"
PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
docker run -d --name "$NAME" -p "127.0.0.1:$PORT:8177" \
  -e PORT=8177 -e WORKBENCH_PASSWORD="$PASSWORD" -e WORKBENCH_SECRET="$SECRET" "$IMAGE" >/dev/null
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

args=("http://127.0.0.1:$PORT" --password "$PASSWORD" --wait 90)
if [ -n "$SHA" ]; then args+=(--sha "$SHA"); fi
if ! python3 workbench/scripts/boot_check.py "${args[@]}"; then
  echo "— the container's own log:"
  docker logs "$NAME" 2>&1 | tail -40
  exit 1
fi
if [ "$(docker inspect -f '{{.Config.User}}' "$NAME")" = "root" ] || [ -z "$(docker inspect -f '{{.Config.User}}' "$NAME")" ]; then
  echo "FAIL: the image runs as root"
  exit 1
fi
echo "ok · the image runs as $(docker inspect -f '{{.Config.User}}' "$NAME")"
