"""The password gate.

A shared password, because that is what a small private reference needs — not accounts.
Three states, kept distinct in the same way the rest of the system keeps its three:

  configured and satisfied  → the request proceeds
  configured and not met    → 401, and the client shows the password screen
  not configured at all     → the server is OPEN, and /api/health says so out loud

The third is the local-development default and must never be reported as if it were the
first. An unset password is not a passed check; it is an absent one.

Identity is a separate question from authorisation, and this module answers both because
the rail's rate limiter needs a stable per-caller string. A shared password gives no real
user identity, so each successful login mints a random subject: two people who typed the
same password still get separate rate-limit budgets, and one person's browser keeps its
budget across reloads.

A Cloudflare Access header outranks all of that — but ONLY when `WORKBENCH_TRUST_PROXY_AUTH`
says a proxy that sets it is really in front. That flag exists because the first version of
this module trusted the header unconditionally, which on a bare deployment with nothing in
front is not an identity at all: it is a string the caller chose, and sending one walked
straight past the password. A header is only evidence of who someone is when something
upstream is guaranteed to have overwritten whatever they sent.
"""
import hmac
import os
import secrets
import time
from hashlib import sha256

from . import limits

COOKIE = "wb_session"
TTL_S = 30 * 24 * 3600  # 30 days

# Paths that must answer before a caller could possibly hold a session.
OPEN_PATHS = ("/api/health", "/api/login")

# Set once per process when WORKBENCH_SECRET is absent. Sessions then die on restart,
# which is a visible inconvenience rather than a silent weakening of the signature.
_EPHEMERAL_SECRET = secrets.token_bytes(32)


def password():
    return os.environ.get("WORKBENCH_PASSWORD") or ""


def api_token():
    return os.environ.get("WORKBENCH_API_TOKEN") or ""


def required():
    """True when anything at all guards this server."""
    return bool(password() or api_token())


def _secret():
    configured = os.environ.get("WORKBENCH_SECRET")
    return configured.encode() if configured else _EPHEMERAL_SECRET


def _sign(payload):
    return hmac.new(_secret(), payload.encode(), sha256).hexdigest()


def mint(subject=None):
    """A signed session token. The subject is random by default — see the module note."""
    sub = subject or secrets.token_urlsafe(9)
    exp = int(time.time()) + TTL_S
    payload = f"{sub}.{exp}"
    return f"{payload}.{_sign(payload)}"


def verify(token):
    """Return the subject of a valid unexpired token, else None."""
    if not token or token.count(".") != 2:
        return None
    sub, exp, sig = token.split(".")
    if not hmac.compare_digest(sig, _sign(f"{sub}.{exp}")):
        return None
    try:
        if int(exp) < time.time():
            return None
    except ValueError:
        return None
    return sub


def check_password(candidate):
    """Constant-time comparison against the configured password.

    Encoded first: hmac.compare_digest raises TypeError on str containing non-ASCII, so
    comparing raw strings turned an accented password — typed by a user, or configured by
    the operator — into a 500 that the login screen rendered as "not accepted".
    """
    configured = password()
    if not configured:
        return False
    return hmac.compare_digest(str(candidate or "").encode("utf-8"),
                               configured.encode("utf-8"))


def bearer(request):
    header = request.headers.get("authorization") or ""
    return header[7:].strip() if header.lower().startswith("bearer ") else ""


def check_bearer(request):
    """Same encoding rule as check_password — and it matters more here, because this runs
    inside the gate middleware, so a non-ASCII byte in an Authorization header would turn
    every /api/* request into a 500 rather than a 401."""
    configured = api_token()
    if not configured:
        return False
    return hmac.compare_digest(bearer(request).encode("utf-8"),
                               configured.encode("utf-8"))


def trust_proxy_auth():
    """Whether an upstream proxy's identity header may be believed.

    OFF by default, and that default is the security property. `Cf-Access-…` headers
    are only meaningful when Cloudflare Access actually fronts the app, because Access
    strips any copy a client sent and sets its own. With nothing in front — a bare
    platform deployment, which is the default here — the header is just a string the
    caller chose, and trusting it unconditionally let anyone past the password by
    sending one. Turn this on ONLY when a proxy that overwrites the header is
    guaranteed to be in front of every request.
    """
    return (os.environ.get("WORKBENCH_TRUST_PROXY_AUTH") or "").strip().lower() in (
        "1", "true", "yes", "on")


def access_email(request):
    """The proxy-asserted user, or "" when there is no reason to believe it."""
    if not trust_proxy_auth():
        return ""
    return (request.headers.get("cf-access-authenticated-user-email") or "").strip()


def source_address(request):
    """The caller's address as reported by the LAST proxy hop.

    Deliberately the last entry, not the first. Each proxy appends the address it saw,
    so the final entry is the one our own proxy wrote and the earlier ones are whatever
    the client sent. uvicorn runs with forwarded_allow_ips="*" (the platform's proxy
    address is not knowable in advance), and its always-trust path takes entry [0] —
    which a caller controls. Reading the last hop ourselves means a caller cannot mint a
    fresh rate-limit identity per request by varying the header.

    This bounds abuse; it is not an authentication boundary and nothing here treats it
    as one. Everyone behind one NAT still shares a bucket, which is the accepted cost.
    """
    fwd = request.headers.get("x-forwarded-for") or ""
    if fwd:
        hops = [h.strip() for h in fwd.split(",") if h.strip()]
        if hops:
            return hops[-1]
    return getattr(getattr(request, "client", None), "host", "") or "unknown"


def identity(request):
    """A stable per-caller string for rate limiting.

    Order matters: a Cloudflare Access email is a verified identity and outranks
    everything; a session subject is per-browser; an address is the last resort and is
    shared by everyone behind one NAT, which is why it is not relied on alone.
    """
    email = access_email(request)
    if email:
        return f"access:{email}"
    sub = verify(request.cookies.get(COOKIE))
    if sub:
        return f"session:{sub}"
    if api_token() and check_bearer(request):
        return "token:api"
    return f"addr:{source_address(request)}"


def authorised(request):
    """Is this request allowed past the gate?"""
    if not required():
        return True  # open by configuration, and /api/health reports it
    if access_email(request):
        return True
    if verify(request.cookies.get(COOKIE)):
        return True
    return check_bearer(request)


def login_attempts_per_hour():
    """Read lazily, like every knob in limits.py — a constant bound at import time is
    invisible to anything that sets the environment afterwards, tests included."""
    try:
        return int(os.environ.get("WORKBENCH_LOGIN_ATTEMPTS", "") or 20)
    except ValueError:
        return 20


def login_allowed(request):
    """Throttle password guessing. Returns (ok, retry_after_seconds)."""
    return limits.take(f"login:{source_address(request)}",
                       limit=login_attempts_per_hour(), window_s=3600)


def state():
    """What /api/health reports. Never collapses 'open' into 'protected'."""
    if not required():
        return {"required": False,
                "note": "no WORKBENCH_PASSWORD is set — this server is open to anyone "
                        "who can reach it"}
    # `password` is reported separately from `required` because WORKBENCH_API_TOKEN alone
    # also makes required() true — and then the browser is gated by something no password
    # can satisfy. Without this the Gate showed a box that could never succeed.
    return {"required": True, "password": bool(password()),
            "bearer": bool(api_token()), "trusts_proxy_header": trust_proxy_auth()}
