# oq/the-plate-does-not-read-the-disclosure-module-it-imports — one spelling, two surfaces, and only one of them reads it

*Status: OPEN · Raised in: WP-12.9 (9 September 2026)*

**`build/render_plan.py` imports `build/disclosures.py` at line 20 and, before WP-12.9, called
nothing from it.** The module it imports opens by saying:

> ONE SPELLING, TWO SURFACES. `build/render_plan.py` draws these lines on the plate; the
> workbench gets the same list through `core.placement_summary` and renders it in the disclosure
> strip, so the app displays what Python computed rather than re-deriving it in JavaScript.

Half of that sentence is true. `mcp_server/core.py:1661` really does call
`_disclosures().banner(...)`, so the bench strip is the module's output. The **printed plate** is
not: `render_plan.py` builds its own `schedule` list and spells the lines itself.

## The measurement

Taken over the tree as it stands, by name:

| function in `disclosures.py` | called by `render_plan.py`? |
|---|---|
| `engine_line` | no |
| `walls_set_aside` | no |
| `objective_not_run` | no |
| `alternative_offered` | no |
| `windows_not_drawn` | no |
| `transfers` | no |
| `style_disagreement` | no |
| `banner` | no |
| `stack_plan_judgment` | **yes** — added by WP-12.9, and the only one |

And the duplicated text, which is how it was found:

- `disclosures.py:322` and `render_plan.py:611` both spell `N CUT(S) OFF THE BAY LINE`.
- `disclosures.py:372` and `render_plan.py:656` both spell the unlocated-cut line.
- **`export_dxf.py:217` spells the first one a THIRD time.**

`CLAUDE.md` records this module as *"the ONE spelling of every banner line ... **Do not add a
third.**"* There are three.

## Why it matters, and it is not tidiness

The two lists have already diverged in both directions:

- `render_plan.py`'s schedule carries lines `disclosures.py` does not have at all — the WP-11.12
  span-capacity block with its floor caveat, and the stair refusal.
- `disclosures.py` carries lines the plate does not draw — WP-12.9's stack judgment was one until
  that package wired it, and it reached the bench strip and not the printed plate for as long as
  it existed.

So a reader comparing a printed sheet against the same house on the bench is comparing two
different disclosure sets, and neither surface says so. That is WP-6.4's *"a drawing set is ONE
building"* applied to what the drawing says about itself rather than to what it draws — and the
failure mode is the one this project names first: **a disclosure absent from one surface reads
there as a fact that was not worth stating, rather than as a fact that surface does not carry.**

## What it would cost, which is why it is a question and not a patch

Routing `render_plan.py`'s whole schedule through `banner()` is not a refactor with no output:

- the two lists are not the same set, so the plate would gain and lose lines;
- the plate paints by `L["brick"] / L["salmon_deep"] / L["green_deep"]` and the module returns
  `iron / copper / verd`, so a mapping has to be authored and is a decision about the plate;
- the plate WRAPS a long line to the sheet width (`_wrap_banner`) and reserves height per ROW,
  so a changed line set changes every sheet's canvas height;
- **all sixteen shipped sheets move**, and WP-12.9 measured that even a single added row moves
  one sheet by 296 bytes and shifts every row below it.

## What must be ruled before it is built

1. **Which list is right.** The plate's extra lines (span capacity, stair) are real disclosures
   the bench does not make. Does `banner()` gain them — making the bench strip longer — or does
   the plate keep a tail of its own, in which case "one spelling" is a claim about part of the
   set and the module must say which part?
2. **Who owns the tone mapping.** A tone is a decision about a surface, and there are two
   surfaces; putting it in `disclosures.py` makes that module know about the plate's palette.
3. **`export_dxf.py`'s third spelling.** The DXF marker is a different medium with a size cap
   (XDATA is capped near 16 KB per entity), so it may be right that it states less — but that is
   a ruling, and today it is a copied string.

## What is NOT the answer

Deleting `render_plan.py`'s own lines to make the module's list authoritative, without first
ruling item 1, would silently drop the span-capacity caveat from the printed sheet — a line
WP-11.12 added precisely because *"a quantity a SCORE knows about and a CHECKER does not is
invisible in exactly the surfaces a person reads"*. Removing it from the surface a person prints
would be that finding committed again by the package tidying it up.
