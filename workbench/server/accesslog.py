"""One line a request, an id on every response, and the server's own loggers switched on.

Deployment-readiness review, 27 Nov 2026 (DR-07). uvicorn is started at `log_level="warning"`,
which is right for uvicorn's own chatter and left this server with no access log at all: a burst
of failed sign-ins, a route answering 500, a caller looping on a heavy route -- nothing was
written. And the server's own INFO lines (`tdl.rail`'s usage figures) were dropped by the root
logger's default level, so they were produced and never seen.

Two things, and deliberately no more:

  * `AccessLog`, a plain ASGI middleware (the gate's note says why not a BaseHTTPMiddleware:
    three routes stream). It writes one line when a response ENDS, so a stream is timed whole,
    and puts `X-Request-ID` on every response so a person reporting a failure can quote it.
  * `configure()`, which gives the `tdl` logger a handler and a level. `__main__` calls it. A
    process that imports the app another way (the tests, `uvicorn workbench.server.app:app`)
    is left as it was: the lines propagate to whatever logging that process set up.

WHAT A LINE HOLDS, AND WHAT IT LEAVES OUT. Method, path, status, milliseconds, the caller's
address as uvicorn resolved it (the platform proxy's forwarded hop), and the id. NOT the query
string and not a header: a query can carry what a caller typed, and the line is read by whoever
can read the platform's logs. The path is the percent-ENCODED one, so a `%0A` in a URL stays
three characters and cannot start a second, forged line; an inbound id is kept only if it is
short and made of characters that cannot do the same.

WHAT THIS IS NOT. It is not an error tracker, a metric or an alert. Those are a service somebody
chooses and pays for; this is the minimum that lets the platform's own log search answer "what
happened".
"""
import logging
import os
import re
import secrets
import sys
import time

log = logging.getLogger("tdl.access")

LEVEL_VAR = "WORKBENCH_LOG_LEVEL"
ID_HEADER = b"x-request-id"
_SAFE_ID = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")
_PATH_MAX = 200

# A healthy poll of the healthcheck is not news, and the platform sends one every few seconds.
# A healthcheck that FAILS is logged like anything else.
QUIET_WHEN_OK = ("/api/health",)
# Nor is the app's own bundle: one page is a dozen of these, and they say nothing the page's own
# line does not. A missing one (404) is logged.
QUIET_PREFIX_WHEN_OK = ("/assets/",)


def _request_id(scope):
    for name, value in scope.get("headers") or ():
        if name == ID_HEADER:
            try:
                said = value.decode("ascii")
            except UnicodeDecodeError:
                break
            if _SAFE_ID.match(said):
                return said
            break
    return secrets.token_hex(8)


def _path(scope):
    raw = scope.get("raw_path")
    if isinstance(raw, (bytes, bytearray)):
        text = bytes(raw).split(b"?", 1)[0].decode("latin-1")
    else:
        text = str(scope.get("path") or "")
    # Belt and braces: a raw path is already encoded, but nothing printable may be a control.
    text = "".join(ch if 32 < ord(ch) < 127 else "%{:02X}".format(ord(ch) & 0xFF) for ch in text)
    return text[:_PATH_MAX] + ("…" if len(text) > _PATH_MAX else "")


class AccessLog:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        rid = _request_id(scope)
        started = time.monotonic()
        status = [None]

        async def tagged(message):
            if message.get("type") == "http.response.start":
                status[0] = message.get("status")
                headers = [(k, v) for k, v in (message.get("headers") or ()) if k.lower() != ID_HEADER]
                headers.append((ID_HEADER, rid.encode("ascii")))
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, tagged)
        except BaseException:
            # Nothing was answered, or the answer was cut: the caller saw a 500 or a dropped
            # connection. Logged as 500 and re-raised; this layer swallows nothing.
            if status[0] is None:
                status[0] = 500
            self._line(scope, status[0], started, rid)
            raise
        self._line(scope, status[0], started, rid)

    @staticmethod
    def _line(scope, status, started, rid):
        path = _path(scope)
        if status is not None and status < 400 and (
                path in QUIET_WHEN_OK or path.startswith(QUIET_PREFIX_WHEN_OK)):
            return
        client = (scope.get("client") or ("-",))[0]
        ms = int((time.monotonic() - started) * 1000)
        level = logging.WARNING if (status or 500) >= 500 else logging.INFO
        log.log(level, "%s %s %s %dms %s id=%s",
                scope.get("method", "-"), path, status if status is not None else "-", ms, client, rid)


class _Utc(logging.Formatter):
    converter = time.gmtime

    def formatTime(self, record, datefmt=None):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", self.converter(record.created))


_HANDLER_MARK = "_tdl_configured"


def configure(stream=None):
    """Give the `tdl` logger one handler and the operator's level. Returns the level set.

    Idempotent: a second call replaces the handler it made and adds none, so nothing is printed
    twice. `WORKBENCH_LOG_LEVEL` is a standard level name; a word that is not one is INFO, never
    silence, because a typo must not switch the log off. `propagate` is turned off so a root
    handler somebody else installed does not print each line a second time."""
    said = (os.environ.get(LEVEL_VAR) or "").strip().upper()
    level = logging.getLevelName(said) if said else logging.INFO
    if not isinstance(level, int):
        level = logging.INFO
    root = logging.getLogger("tdl")
    for h in list(root.handlers):
        if getattr(h, _HANDLER_MARK, False):
            root.removeHandler(h)
    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(_Utc("%(asctime)s %(levelname)s %(name)s %(message)s"))
    setattr(handler, _HANDLER_MARK, True)
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False
    return level
