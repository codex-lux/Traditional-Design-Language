"""The 24 rail tools — mcp_server/server.py's own wrappers, loaded without the mcp
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


class _StubFastMCP:
    def __init__(self, name):
        self.name = name

    def tool(self):
        def deco(fn):
            _REGISTRY[fn.__name__] = fn
            return fn
        return deco

    def run(self):  # server.py only calls this under __main__, but be safe
        raise RuntimeError("stub FastMCP cannot run")


def _load_server_tools():
    if _REGISTRY:
        return _REGISTRY
    stub_pkg = types.ModuleType("mcp")
    stub_server = types.ModuleType("mcp.server")
    stub_fastmcp = types.ModuleType("mcp.server.fastmcp")
    stub_fastmcp.FastMCP = _StubFastMCP
    stub_pkg.server = stub_server
    stub_server.fastmcp = stub_fastmcp
    already = "mcp" in sys.modules
    saved = {k: sys.modules.get(k) for k in ("mcp", "mcp.server", "mcp.server.fastmcp")}
    sys.modules["mcp"] = stub_pkg
    sys.modules["mcp.server"] = stub_server
    sys.modules["mcp.server.fastmcp"] = stub_fastmcp
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
