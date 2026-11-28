"""Which addresses are this machine talking to itself.

One spelling, with no imports, because two readers need it and one of them (`__main__`) must run
before the web dependencies are known to be installed: the start-up refusal of an open public
bind (DR-01), and the gate on the developer's reload route (DR-13). Two copies of this list
would be two answers to "is this a deployment".
"""
import os

LOOPBACK = ("127.0.0.1", "localhost", "::1")
HOST_VAR = "WORKBENCH_HOST"
HOST_DEFAULT = "127.0.0.1"


def host():
    """The address this process was started to serve on. The Dockerfile sets 0.0.0.0."""
    return os.environ.get(HOST_VAR) or HOST_DEFAULT


def is_loopback(h):
    return h in LOOPBACK
