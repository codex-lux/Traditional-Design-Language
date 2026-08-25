"""Package marker so the workbench can `import mcp_server.server` and mount it.

The module was always importable by path; making it a package means one import of
`core` shared with workbench/server/corpus.py rather than two copies of a 27 MB corpus.
"""
