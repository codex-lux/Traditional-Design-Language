#!/usr/bin/env python3
"""Write a gzipped sibling beside every compressible file in the built frontend.

Run after `npm run build`; the Dockerfile does it as part of the image. Standard library
only, like the rest of the toolchain.

WHY THIS EXISTS. The server used to gzip these on the fly. Measured against the real app,
`/assets/coastlines-fine-*.js` (1.19 MB) cost 38 ms compressed against 8 ms plain — 4.6x —
and it ran ON THE EVENT LOOP, because FileResponse streams in 64 KiB chunks and Starlette
only hands a chunk to a worker thread at 128 KiB or more. That route is outside the auth
gate (the shell has to load in order to draw the password screen) and outside the rate
limiter, so one anonymous caller at 26 requests a second saturated the core — making a
static GET more expensive than /api/plan/evaluate, which the infrastructure audit calls the
server's ceiling.

The files are content-hashed and served immutable, so their bytes never change. Compressing
them once at build time costs nothing per request and can afford level 9, which is a better
ratio than the level 4 the dynamic path had to settle for.
"""
import gzip
import os
import shutil
import sys

# Text formats only. Compressing an already-compressed format (png, woff2, jpg) spends CPU
# to make the file bigger, and the server would then serve the larger one.
COMPRESS = (".js", ".css", ".html", ".json", ".svg", ".map", ".txt", ".xml")
MIN_BYTES = 1024          # below this the gzip header is most of the file


def precompress(root):
    made, skipped, total_in, total_out = 0, 0, 0, 0
    # sorted: tests/test_determinism.py forbids an unsorted directory read anywhere in
    # the tree, because readdir order is machine-specific and this prints a manifest.
    # dist/ is four files deep, so materialising the walk costs nothing here.
    for base, _dirs, files in sorted(os.walk(root)):
        for name in sorted(files):
            if name.endswith(".gz") or not name.endswith(COMPRESS):
                continue
            path = os.path.join(base, name)
            size = os.path.getsize(path)
            if size < MIN_BYTES:
                skipped += 1
                continue
            with open(path, "rb") as f_in, gzip.open(path + ".gz", "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
            out = os.path.getsize(path + ".gz")
            if out >= size:                 # incompressible: a .gz that is bigger helps nobody
                os.remove(path + ".gz")
                skipped += 1
                continue
            made += 1
            total_in += size
            total_out += out
            print(f"  {os.path.relpath(path, root):48s} {size:9d} -> {out:8d}  "
                  f"{size / out:.1f}x")
    if made:
        print(f"\n  {made} file(s) precompressed, {skipped} skipped: "
              f"{total_in / 1048576:.2f} MB -> {total_out / 1048576:.2f} MB "
              f"({total_in / total_out:.1f}x)")
    else:
        print(f"  nothing to compress under {root} ({skipped} skipped)")
    return 0


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "dist")
    if not os.path.isdir(root):
        print(f"no such directory: {root}\nbuild the app first: "
              f"cd workbench/app && npm run build", file=sys.stderr)
        sys.exit(1)
    sys.exit(precompress(root))
