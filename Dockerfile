# The Workbench, containerised.
#
# Two stages because workbench/app/dist is gitignored — the built frontend is an
# artifact, never a committed file, so the image has to produce it rather than copy it.
#
# The corpus itself needs no stage: it is JSON in the repo, read-only at runtime, and
# baked into the image. There is no database, no volume and no migration step. See
# docs/deployment.md.

# ---------------------------------------------------------------- stage 1: the app
FROM node:20-alpine AS frontend

WORKDIR /build
# package files first so `npm ci` caches across changes to the source.
COPY workbench/app/package.json workbench/app/package-lock.json ./
RUN npm ci
COPY workbench/app/ ./
RUN npm run build

# ---------------------------------------------------------------- stage 2: the server
FROM python:3.11-slim AS server

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WORKBENCH_HOST=0.0.0.0

WORKDIR /app

COPY workbench/requirements.txt workbench/requirements.txt
RUN pip install --no-cache-dir -r workbench/requirements.txt

# The corpus, the toolchain, mcp_server/core.py — everything the server reads.
# .dockerignore keeps .git, Plan Examples/ and dist/ out; none is read at runtime.
COPY . .

# The built app, from stage 1. app.py mounts it only if the directory exists.
COPY --from=frontend /build/dist ./workbench/app/dist

# Nothing here writes to the image, and the corpus is read-only at runtime, so there is
# no reason to run as root. It also bounds what any future file-serving mistake can
# reach — the SPA catch-all was an unauthenticated arbitrary file read until this pass.
RUN useradd --create-home --uid 10001 workbench && chown -R workbench:workbench /app
USER workbench

# PORT is injected by the platform; __main__ prefers it over WORKBENCH_PORT.
EXPOSE 8177
CMD ["python3", "-m", "workbench.server"]
