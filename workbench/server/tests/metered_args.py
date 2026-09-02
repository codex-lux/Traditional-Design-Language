"""The minimum each metered MCP tool needs to get PAST argument validation -- the SDK
validates required arguments before the tool body runs, so an empty {} never reaches the
limiter. Lives in its own module so the pin against mcp_mount.METERED can run WITHOUT the
SDK: test_mcp_http.py skips whole at import where `mcp` is absent, and its copy of this dict
sat at three tools against a set of five for a package, green-by-absence (WP-9.4)."""

METERED_MIN_ARGS = {"tdl_check_plan": {"plan": {}},
                    "tdl_compose": {"brief": {}},
                    "tdl_place_plan": {"plan": {}},
                    "tdl_critique_plan": {"plan": {}},
                    "tdl_revise_plan": {"plan": {}}}
