#!/usr/bin/env python3
"""Traditional Design Language — MCP server.

Exposes the taxonomy, the proportion grammar, the kit directories and the fault corpus as
tools an agent can call while advising a human on a real house.

Run:  python3 mcp_server/server.py            (stdio)
Register with Claude Code:
      claude mcp add tdl -- python3 /abs/path/to/mcp_server/server.py

The same 24 tools are also served over HTTP when the workbench mounts this module at
/mcp — see docs/deployment.md. Nothing here knows which transport it is answering on.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from mcp.server import MCPServer

mcp = MCPServer("traditional-design-language")
J = lambda o: json.dumps(o, ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- metering hook
# Three of the 24 tools reach heavy core functions; the rest are corpus lookups. Served
# over HTTP those three want a cap, and over stdio they do not — one local agent driving
# the CLI is not a shared resource. So the limiter is INJECTED rather than imported:
# mcp_server must not depend on anything in workbench/, and the default of None keeps
# stdio and the tests unmetered. Same seam as rail.set_client_factory.
_limiter = None


def set_limiter(fn):
    """fn(tool_name) -> None to allow, or a string reason to refuse."""
    global _limiter
    _limiter = fn


def _metered(tool_name):
    """Returns a refusal JSON string when the caller is over its cap, else None."""
    if _limiter is None:
        return None
    reason = _limiter(tool_name)
    if not reason:
        return None
    # A refusal is content, at the same weight as a result — the corpus's own discipline.
    return J({"refused": True, "tool": tool_name, "reason": reason,
              "note": "This is a rate limit on this deployment, not a judgment about the "
                      "plan or the corpus. Nothing was evaluated."})

@mcp.tool()
def tdl_overview() -> str:
    """START HERE. What this corpus is, how the model works, what it contains, and the order to
    call the other tools in. About 1,300 tokens. Read it before answering any question about
    traditional architecture from this corpus, because the edge semantics and the judgment-slot
    convention change how the rest of the data should be reported to a human."""
    return J(core.overview())

@mcp.tool()
def tdl_find_style(query: str = "", rank: str = "", region: str = "", year: int = 0,
                   tradition: str = "", limit: int = 20) -> str:
    """Search 164 style taxa. query matches name, aka, description, characteristics and tells.
    rank: tradition | family | style | variant. year finds styles being built in that year.
    tradition: one of classical-mediterranean, british-isles, northern-european-vernacular,
    iberian-mediterranean, north-american. Returns compact cards; follow with tdl_get_style."""
    return J(core.find_style(query, rank or None, region or None, year or None, tradition or None, limit))

@mcp.tool()
def tdl_get_style(style_id: str, sections: list[str] | None = None) -> str:
    """Full record for one style. sections defaults to summary, description, characteristics and
    lineage; ask for proportion, massing, constraints, exemplars or sources when you need them
    rather than pulling everything. Lineage includes the kit cascade — the ancestors this style
    inherits parts from, nearest first."""
    return J(core.get_style(style_id, sections))

@mcp.tool()
def tdl_compare_styles(a: str, b: str) -> str:
    """Disambiguate two styles a client or a photograph is between. Returns any explicit
    disambiguation recorded in the corpus, both sets of diagnostic tells, shared ancestry, and
    whether one descends from the other."""
    return J(core.compare_styles(a, b))

@mcp.tool()
def tdl_get_slot(slot_id: str) -> str:
    """One element slot: what it is, which group it belongs to, which styles specify it, and every
    fault recorded against it. Slots are universal — a style does not own a cornice, it specifies
    one — so this is the right entry point when the question is about an element rather than a style."""
    return J(core.get_slot(slot_id))

@mcp.tool()
def tdl_resolve_kit(style_id: str, group: str = "", slot: str = "",
                    only_specified: bool = True) -> str:
    """The resolved kit of parts for a style: what it specifies, what it forbids, and which
    ancestor each binding came from. Filter by group (one of the eight slot groups) or ask for a
    single slot to get its full record including parameters, code conflicts and proportion-pack
    bindings. Provenance shows how much is inherited versus locally decided."""
    return J(core.resolve_kit(style_id, group or None, slot or None, only_specified=only_specified))

@mcp.tool()
def tdl_get_proportions(pack_id: str, column_diameter: float = 0, module: float = 0,
                        ceiling_height: float = 108.0, opening_width: float = 36.0,
                        assembly: str = "", include_rules: bool = True) -> str:
    """Dimension a proportion pack at a real size. Order packs are <authority>-<order>, e.g.
    gibbs-ionic, vignola-doric, benjamin-corinthian. System packs include trim-classical,
    trim-craftsman, opening-proportion, facade-classical, room-harmonic, brick-course, sash-light.
    Give column_diameter for an order (never a module — authorities do not share one) and
    ceiling_height for a trim or opening system. assembly='cornice' returns member-by-member
    dimensions with mouldings. derived_rules are how the order governs trim, casing and openings;
    anything flagged judgment is NOT determined by the sources and should be put to the human."""
    return J(core.get_proportions(pack_id, column_diameter or None, module or None,
                                  ceiling_height, opening_width, include_rules, assembly or None))

@mcp.tool()
def tdl_compare_authorities(order: str, column_diameter: float = 12.0) -> str:
    """The same order as five authorities drew it, at one column diameter. Use when a client or a
    builder asks 'how tall should the entablature be' and the honest answer is that it depends
    which book you are building from."""
    return J(core.compare_authorities(order, column_diameter))

@mcp.tool()
def tdl_find_faults(style: str = "", slot: str = "", group: str = "", severity: str = "",
                    frequency: str = "", measurable_from: str = "", query: str = "",
                    limit: int = 25) -> str:
    """Search 209 named errors. Faults are ELEMENT-FIRST: most are universal and style is a facet.
    Filter by slot, group, severity (fatal|serious|minor), frequency (endemic|common|occasional),
    or measurable_from (photograph|elevation|plan|section|site-visit). Passing style also surfaces
    EXCEPTION_FOR_THIS_STYLE and INVERTED_FOR_THIS_STYLE — check those before repeating a rule at a
    client, because several styles legitimately do what is a fault everywhere else. Call this
    BEFORE recommending a detail, not after."""
    return J(core.find_faults(style or None, slot or None, group or None, severity or None,
                              frequency or None, measurable_from or None, query or None, limit))

@mcp.tool()
def tdl_get_fault(fault_id: str, style: str = "") -> str:
    """Full fault record: symptom, why it happens and what the shortcut saves, the rule violated,
    correct practice, three tiers of fix (right, cheap, and the dishonest one that looks like a fix
    and is not), how to detect it, and the exceptions. Pass style to get the severity and any
    exception or inversion that applies to that style specifically."""
    return J(core.get_fault(fault_id, style or None))

@mcp.tool()
def tdl_measurement_vocabulary(slot: str = "", style: str = "", include_constraints: bool = True) -> str:
    """Every variable name the corpus can test on — the fault corpus, counted by actual test
    usage, plus (by default) a style's migrated constraint tests (schema/constraint.schema.json,
    WP-1.1) — with units, measurable_from, and which corpus (source) tests on each. Call this
    before tdl_check_measurements or tdl_check_style_constraints so you measure the right things
    and name them correctly — the tests are exact-match on variable name."""
    return J(core.measurement_vocabulary(slot or None, style or None, include_constraints))

@mcp.tool()
def tdl_check_measurements(measurements: dict, style: str = "", slot: str = "",
                           limit: int = 40) -> str:
    """Evaluate the fault corpus against real numbers. Give a dict of measurements — from a
    photograph, an elevation, or a tape — and get back which faults are PRESENT (a test actually
    failed, with the value, the threshold and the fix), which are CLEAR, and which COULD NOT BE
    JUDGED for want of a number. Anything unjudged is unknown, never passed; say so to the human.
    Style-specific exceptions are applied automatically, so a five-foot Georgian portico will not
    be reported as the four-foot-porch fault. Use tdl_measurement_vocabulary for the variable names.
    For a style's own hard/soft constraints rather than the element-level fault corpus, use
    tdl_check_style_constraints instead."""
    return J(core.check_measurements(measurements, style or None, slot or None, limit=limit))

@mcp.tool()
def tdl_check_style_constraints(style: str, measurements: dict) -> str:
    """Evaluate one style's own constraints (schema/constraint.schema.json, WP-1.1 — 140 of ~660
    migrated so far) against a dict of measurements, without building a whole plan record. Give
    a dict like {"roof_pitch_rise_per_12": 9} and get back which constraints are PRESENT
    (violated — a test actually failed, with the value and what was required), which are CLEAR,
    which COULD NOT BE JUDGED for want of a variable, and which are judgment_only (a hard
    constraint the sources don't determine numerically, listed for hand review, never silently
    passed). Anything unjudged is unknown, never passed. Use tdl_measurement_vocabulary(style=...)
    for the variable names this style's constraints reference. tdl_check_plan runs the same
    evaluation as part of a full plan check; use this tool when you only have a style and some
    numbers, not a whole plan."""
    return J(core.check_style_constraints(style, measurements))

@mcp.tool()
def tdl_get_massing(massing_id: str = "", style: str = "") -> str:
    """The volumetric skeleton catalogue — 40 types with their structural logic and, importantly,
    their expansion logic: how each grows without breaking. Massing is NOT style; a Foursquare
    wears Craftsman or Colonial Revival with no change of volume. Pass style to get its affinities."""
    return J(core.get_massing(massing_id or None, style or None))

@mcp.tool()
def tdl_find_assets(slot: str = "", style: str = "", fault: str = "", role: str = "",
                    status: str = "", limit: int = 20) -> str:
    """Image records — correct/incorrect pairs, diagrams and measured details. role:
    correct | incorrect | comparison | diagram | reference. Most records are status 'wanted',
    meaning the record exists and the file does not; their alt_text is written to be reasoned from,
    so use it and tell the human the picture is still outstanding."""
    return J(core.find_assets(slot or None, style or None, fault or None, role or None,
                              status or None, limit))

@mcp.tool()
def tdl_find_room(query: str = "", function_class: str = "", style: str = "",
                  massing: str = "", limit: int = 25) -> str:
    """Search 58 room types. Rooms are style-independent, like massings — what a room constrains is
    dimension, daylight, adjacency and servicing, and those are physical before they are stylistic.
    function_class: public | living | dining | service | sleeping | sanitary | work | storage |
    circulation | threshold | outdoor. Passing style surfaces IN_THIS_STYLE, including rooms that
    style does not have at all."""
    return J(core.find_room(query, function_class or None, style or None, massing or None, limit))

@mcp.tool()
def tdl_get_room(room_id: str, style: str = "") -> str:
    """Full room record: history and what killed or made it, the furniture that has to fit with real
    clearances, the critical dimension and why, daylight depth, typed adjacency rules with their
    exceptions, privacy rank, servicing, code, and how the room differs by style. The furniture list
    is the part most plans are missing — a dining room can dimension correctly and still not seat eight."""
    return J(core.get_room(room_id, style or None))

@mcp.tool()
def tdl_get_grouping(grouping_id: str = "", massing: str = "", style: str = "",
                     scale: str = "", limit: int = 20) -> str:
    """Room groupings — the middle scale, and the one people actually design at. A hall-and-parlor
    pair, a centre-passage core, an entry sequence, a service core, a primary suite. Each carries its
    own internal rules with hard/strong/preferred severities and, importantly, attaches_to: how the
    grouping lands in a massing. That join is what makes rooms and skeletons composable. Call with no
    id to list; filter by massing to see what fits a given skeleton."""
    return J(core.get_grouping(grouping_id or None, massing or None, style or None, scale or None, limit))

@mcp.tool()
def tdl_plan_schema() -> str:
    """The plan record format, plus the example plans in the repository. Read this before
    authoring a plan to pass to tdl_check_plan."""
    return J(core.plan_schema())

@mcp.tool()
def tdl_check_plan(plan: dict, strict: bool = False) -> str:
    """Validate a plan across five layers and return every violation found.

    ROOM: dimension bands, ceiling minimums, furniture fit with real clearances, daylight depth
    against window head. ADJACENCY: typed directional rules with their style exceptions, honouring
    two-hop connection through a hall because that is how houses actually work. PRIVACY: the
    public-to-private gradient, with circulation treated as rank-transparent. GROUPING: declared
    groupings' required rooms and massing fit. FAULT: the 209-fault corpus against whatever
    measurements the plan supplies. CODE: IRC model text, ADVISORY and jurisdictional — never a
    permit review. STYLE: forbidden variants the plan declares, and the style's own migrated
    constraints evaluated present/clear/unjudged (WP-1.2) — a constraint without a test yet is
    still listed for hand review, exactly as before.

    Findings come back with severity, layer, the rule's reasoning, and a fix. Absence of a room type
    is reported separately as 'completeness' rather than as a failure, because a plan record that does
    not model closets is coarse, not wrong; pass strict to treat absence as a failure.

    This is also the fitness function a plan composer needs, which is why it exists before one."""
    refused = _metered("tdl_check_plan")
    return refused or J(core.check_plan(plan, strict))

@mcp.tool()
def tdl_brief_schema() -> str:
    """The brief format for tdl_compose, plus the example briefs in the repository. Only style and
    target area are required; everything else the composer decides and reports as an assumption."""
    return J(core.brief_schema())

@mcp.tool()
def tdl_list_partis(style: str = "", massing: str = "") -> str:
    """The 12 canonical plan diagrams the composer seeds from — centre-passage double and single pile,
    hall-and-parlor, side-hall town house, Cape with central chimney, Foursquare, Charleston single with
    piazza, Creole gallery, bungalow, tripartite ranch, five-part Palladian, gable-front-and-wing. Each
    carries what it trades away and how it grows, which is the useful part."""
    return J(core.list_partis(style or None, massing or None))

@mcp.tool()
def tdl_compose(brief: dict, candidates: int = 4, include_plans: bool = False) -> str:
    """Compose several contrasting plans from a brief, scored by the validator.

    Seeds from the canonical partis native to the style, sizes every room from the room catalogue,
    repairs against the validator until it stops improving, reclaims the area the repair spent, and
    returns candidates fatal-free first and then by score.

    `score` is out of 100 and HIGHER IS BETTER. It is a weighted composite of eight axes, not a total
    of what is wrong: each axis is the share of its own denominator that came back clean, so a bigger
    house is not marked down for being checked more times. `score_axes` itemises it — weight, share
    and the denominator the share was taken over. An axis nothing could be evaluated on has its weight
    DROPPED and the total renormalised, never counted as a pass; `score_weight_unevaluated` says how
    much of the hundred that was. A fatal finding forfeits the score entirely: `score` is null and
    `score_forfeit` says why, with the axes still measured. `demerits` is the superseded
    lower-is-better total and ranks nothing.

    Read `trades_away` before `score` — every diagram gives something up, and the best-scoring plan is
    not always the one the client wants. Read `decisions` too: those are what the composer chose where
    the brief was silent, and they are assumptions rather than facts.

    A plan with no fatal findings is not therefore good. The corpus can say what is wrong; it cannot
    say what is alive, and that judgement belongs to the human. Pass include_plans to get the full
    records for tdl_check_plan."""
    refused = _metered("tdl_compose")
    return refused or J(core.compose(brief, candidates, include_plans))

@mcp.tool()
def tdl_place_plan(plan: dict, parti: str = "", candidates: int = 250, svg_path: str = "",
                   engine: str = "auto") -> str:
    """Place room rectangles in a footprint and return coordinates, both levels solved together.

    Bay-grid slicing: rooms snap to the parti's structural bay module, because traditional houses
    are built on one — joists span it, windows centre on it, the facade composes from it. Cuts may
    be taken off the grid where a room otherwise will not fit, and every such relaxation is counted
    and reported rather than hidden.

    Levels are scored as a PAIR on vertical alignment — bearing lines that continue, wet rooms that
    stack — so an upper layout that would score better alone is rejected when it leaves walls
    unsupported. When rooms will not fit, the footprint grows a bay before any room is compromised.

    Pass svg_path to also write a drawing. The drawing is a render of the coordinates, never the
    source of them. Returns coordinates in feet, origin at the south-west corner.

    engine: "auto" (CP-SAT proof when OR-Tools is available, heuristic fallback stated),
    "cp" (prove or refuse — a ~25s solve), or "heuristic" (the fast hill-climb)."""
    refused = _metered("tdl_place_plan")
    return refused or J(core.place_plan(plan, parti or None, candidates, svg_path or None, engine=engine))

if __name__ == "__main__":
    mcp.run()
