# Traditional Design Language — MCP server

24 tools that let an AI consult the corpus while advising a human on a real house.

## Install

```bash
pip install "mcp[cli]" jsonschema
claude mcp add tdl -- python3 /absolute/path/to/mcp_server/server.py
```

Or add to any MCP client's config:

```json
{ "mcpServers": {
    "tdl": { "command": "python3", "args": ["/absolute/path/to/mcp_server/server.py"] } } }
```

No auth, no network. It reads the repository beside it.

## The tools

Grouped by the layer of the stack each one reads from — see `docs/model.md` for the full stack. Regenerate this table's tool count with `python3 build/gen_readme_counts.py` if it ever drifts from `server.py` again; do not hand-count.

**Orientation**

| Tool | For |
|---|---|
| `tdl_overview` | **Start here.** ~1,300 tokens: the model, the edge semantics, and the order to call the rest in. |

**The vocabulary — style graph**

| Tool | For |
|---|---|
| `tdl_find_style` | Search 164 taxa by name, region, year, rank or tradition |
| `tdl_get_style` | One style, by section — ask for what you need, not everything |
| `tdl_compare_styles` | Disambiguate two styles a client or a photograph is between |

**The alphabet — slots, massings, rooms**

| Tool | For |
|---|---|
| `tdl_get_slot` | One element slot: which styles specify it, every fault against it |
| `tdl_get_massing` | The 40-type volumetric skeleton catalogue, with expansion logic |
| `tdl_find_room` | Search 58 room types, style-independent like massings |
| `tdl_get_room` | Furniture with clearances, adjacency rules, the critical dimension and why |

**The bindings — kits**

| Tool | For |
|---|---|
| `tdl_resolve_kit` | The resolved kit with a source column — which ancestor each binding came from |

**The grammar — proportion packs**

| Tool | For |
|---|---|
| `tdl_get_proportions` | Dimension any pack at a real size, member by member |
| `tdl_compare_authorities` | The same order as Vignola, Palladio, Gibbs, Chambers and Benjamin drew it |

**The solecisms — fault corpus**

| Tool | For |
|---|---|
| `tdl_find_faults` | Search 209 named errors, with per-style exceptions surfaced |
| `tdl_get_fault` | Cause, correct practice, three tiers of fix, detection |
| `tdl_measurement_vocabulary` | Exactly what to measure, and what to call it — fault- and constraint-sourced |
| `tdl_check_measurements` | **Evaluate the fault corpus against real numbers.** |
| `tdl_check_style_constraints` | **Evaluate one style's own constraints against real numbers**, without a whole plan record (WP-1.2) |

**The phrase layer — groupings and partis**

| Tool | For |
|---|---|
| `tdl_get_grouping` | 16 groupings and how each attaches to a massing |
| `tdl_list_partis` | The 12 canonical plan diagrams the composer seeds from |

**The critic — plan validator**

| Tool | For |
|---|---|
| `tdl_plan_schema` | The plan record format, plus the shipped example plans |
| `tdl_check_plan` | Validate a plan across five layers and return every violation found |

**The generator — composer and geometry**

| Tool | For |
|---|---|
| `tdl_brief_schema` | The brief format for `tdl_compose`, plus the shipped example briefs |
| `tdl_compose` | Compose several contrasting plans from a brief, scored by the validator |
| `tdl_place_plan` | Place room rectangles in a footprint, coordinates, both levels solved together |

**The evidence layer — images**

| Tool | For |
|---|---|
| `tdl_find_assets` | Image records and shot specs, including the ones with no file yet |

## Four things an agent using this should know

**Progressive disclosure is deliberate.** `tdl_overview` is small on purpose and `tdl_get_style` defaults to four sections out of nine. Ask for more when you need it.

**Call `tdl_find_faults` before recommending a detail, not after.** And read `EXCEPTION_FOR_THIS_STYLE` before repeating a rule at a client — several styles legitimately do what is a fault everywhere else.

**Unjudged is not passed.** `tdl_check_measurements` and `tdl_check_style_constraints` both separate a failed test from one they could not evaluate. Tell the human which is which.

**Judgment slots are the point, not a gap.** Rules flagged `judgment: true` are not determined by the sources. Put them to the human rather than inventing a number. A rules engine that cannot admit ignorance will produce houses that violate no constraint and are still dead.

## Testing without a client

```python
import sys; sys.path.insert(0, "mcp_server")
import core
core.overview()
core.check_measurements({"shutter_leaf_width_in": 12, "window_opening_width_in": 32},
                        style="colonial-revival")
```

`core.py` is pure functions with no protocol dependency, so it is usable from a notebook or a platform directly.
