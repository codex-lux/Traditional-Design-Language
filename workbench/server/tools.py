"""The 26 rail tools — mcp_server/server.py's own wrappers, loaded without the mcp
package. A stub FastMCP collects the decorated functions, so the names, docstrings
(the product's actual tool prose, encoding the operating rules) and argument
signatures cannot drift from the MCP server: they ARE the MCP server's.
"""
import importlib.util
import inspect
import os
import sys
import types
import typing

from . import corpus

_REGISTRY = {}
_LOAD_LOCK = __import__("threading").Lock()


class _StubMCPServer:
    """Stands in for mcp.server.MCPServer when the SDK is not installed.

    Tracks the real class's surface only as far as server.py uses it: the `tool()`
    decorator, which must return the function unchanged so the module-level names stay
    callable. Renamed from _StubFastMCP when the SDK's v2.0.0 renamed the real class and
    removed mcp.server.fastmcp outright.
    """
    def __init__(self, name=None, **kw):
        self.name = name

    def tool(self, *a, **kw):
        def deco(fn):
            _REGISTRY[fn.__name__] = fn
            return fn
        return deco

    def run(self, *a, **kw):  # server.py only calls this under __main__, but be safe
        raise RuntimeError("stub MCPServer cannot run")


def _load_server_tools():
    if _REGISTRY:
        return _REGISTRY
    with _LOAD_LOCK:
        return _load_server_tools_locked()


def _load_server_tools_locked():
    if _REGISTRY:
        return _REGISTRY

    # The SDK is a workbench dependency now (it serves the same tools over HTTP), so the
    # ordinary import is the right path and the only one that shares a module instance
    # with the mounted server. It also avoids the stub's real hazard: putting a fake `mcp`
    # into sys.modules poisons the genuine package for everything that imports it later
    # in the same process — which is exactly what the MCP HTTP tests hit.
    try:
        from mcp_server import server as mod
    except ImportError:
        return _load_via_stub()

    for name, fn in vars(mod).items():
        if name.startswith("tdl_") and callable(fn):
            _REGISTRY[name] = fn
    return _REGISTRY


def _load_via_stub():
    """Fallback for an environment without the SDK — the rail still works there.

    Two concurrent first rail turns would otherwise both mutate sys.modules and race
    each other's finally-restore, so the caller holds a lock and this runs once.
    """
    stub_pkg = types.ModuleType("mcp")
    stub_server = types.ModuleType("mcp.server")
    stub_server.MCPServer = _StubMCPServer
    stub_pkg.server = stub_server
    already = "mcp" in sys.modules
    saved = {k: sys.modules.get(k) for k in ("mcp", "mcp.server")}
    sys.modules["mcp"] = stub_pkg
    sys.modules["mcp.server"] = stub_server
    try:
        path = os.path.join(corpus.ROOT, "mcp_server", "server.py")
        spec = importlib.util.spec_from_file_location("tdl_mcp_server_tools", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            if v is not None:
                sys.modules[k] = v
            elif not already:
                sys.modules.pop(k, None)
    return _REGISTRY


_JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean",
               dict: "object", list: "array"}


def _schema_for(fn):
    sig = inspect.signature(fn)
    props, required = {}, []
    hints = typing.get_type_hints(fn)
    for name, p in sig.parameters.items():
        t = hints.get(name, str)
        origin = typing.get_origin(t)
        if origin is typing.Union:  # e.g. list[str] | None
            args = [a for a in typing.get_args(t) if a is not type(None)]
            t = args[0] if args else str
            origin = typing.get_origin(t)
        if origin in (list, typing.List):
            prop = {"type": "array", "items": {"type": "string"}}
        else:
            prop = {"type": _JSON_TYPES.get(t, "string")}
        props[name] = prop
        if p.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}


def tool_definitions():
    """Anthropic-API-shaped tool list."""
    tools = _load_server_tools()
    out = []
    for name, fn in tools.items():
        out.append({
            "name": name,
            "description": inspect.getdoc(fn) or name,
            "input_schema": _schema_for(fn),
        })
    return out


def run_tool(name, args):
    """Execute one tool. Returns the wrapper's JSON string (they all J(...) their
    result), or an error string the model can act on."""
    tools = _load_server_tools()
    fn = tools.get(name)
    if not fn:
        return f'{{"error": "unknown tool {name}"}}'
    try:
        return fn(**(args or {}))
    except TypeError as e:
        return f'{{"error": "bad arguments: {e}"}}'
    except Exception as e:  # a tool crash is content for the model, not a 500
        return f'{{"error": "{type(e).__name__}: {str(e)[:300]}"}}'
