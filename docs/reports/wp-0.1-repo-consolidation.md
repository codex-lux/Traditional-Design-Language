# WP-0.1 — Repository consolidation

*Executed 23 August 2026, overnight autonomous session.*

## What was built

`traditional-design-language.zip` (v0.6, 19 Aug) was extracted and used as the base tree — it turned out to already be the complete, current v0.6 repository (README.md, all data catalogs, `mcp_server/`, `build/`), not a delta on top of the disk's 18 Aug state. `Plan Examples/` (26 images: 18 good, 8 bad — not part of the zip) was folded in from the desktop folder. Git was initialized and the result committed as "v0.6 consolidated". The full check suite (`validate.py`, `check_orders.py`, `check_modules.py`, `check_systems.py`, `check_kits.py`, `check_faults.py`, `check_rooms.py`, `proportion_engine.py selftest`, `plan_check.py` on both shipped plans, `compose.py` on the Georgian brief, `build.py`) is green.

## What was found

**The disk root README.md is stale and should not be revived.** It predates the zip's README.md — it lacks the rooms, fault-corpus, plan-validator and composer sections entirely, and states old counts (89 slots, no room/fault mention). The zip's README.md is the correct base, but it is itself only *partially* updated: its header line correctly says "93 element slots ... 23 MCP tools" but body text three lines down still says "82 universal slots" and the `mcp_server/` table row still says "17 tools". This is exactly the doc-drift the state-of-project review flagged — left untouched here and handed to WP-0.2, which fixes it mechanically from a generated counts script rather than by hand-editing prose that will drift again.

**Four of the five loose root Markdown files were exact, byte-identical duplicates** of files already in `docs/` or `mcp_server/`: `COMPOSER.md` = `docs/compose.md`, `GEOMETRY.md` = `docs/geometry.md`, `PLAN-VALIDATOR.md` = `docs/plans.md`, `MCP-SERVER-SETUP.md` = `mcp_server/README.md` (diff-verified, zero lines of difference on all four). `OPEN-QUESTIONS.md` was also identical to `docs/open-questions.md`. None needed folding in — they were simply not carried into the consolidated tree.

**Root-level `taxonomy.html`, `orders.html`, `tidewater-georgian-plan.svg` are stale pre-v0.6 builds**, confirmed by md5: they do not match the current `dist/` outputs the zip ships. They were not carried forward; `dist/` is now the single home for built artifacts, as the work package specifies.

**`_to_delete/` was confirmed fully superseded** — `old_kits/`, `old_styles/`, `old_build/`, `old_dist/`, `old_docs/`, `old_elements/`, `old_massings/`, `old_schema/`, plus scratch `_gen/` (8 generator scripts) and `_stage2/` (one file, `README.md`) — every one of these is an earlier generation of something the current tree already has in full. Nothing from it was recovered.

## What was deliberately not done

**The stale material was not deleted from the user's actual disk.** This session's device-bridge access can move files (`mv`) but not delete them (`rm`/`unlink` require a permission grant only a person can approve, and that tool wasn't available this session). Rather than leave the stale copies sitting at the root where they'd shadow the new consolidated tree, they were moved into a single clearly-named folder — `_SAFE_TO_DELETE_2026-08-23/` — for Lucas to delete by hand when he's back. See the delivery note in the conversation for the exact contents.

**No git remote was configured.** No `.git` existed on disk and none was mentioned; this session set up git locally only. If a GitHub (or other) remote should hold this, that's Lucas's call and his credentials — flagged, not done.

## Open question raised

None new. This package only executes decisions already settled in the Plan of Action.
