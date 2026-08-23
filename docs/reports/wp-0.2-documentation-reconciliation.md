# WP-0.2 — Documentation reconciliation

*Executed 23 August 2026, overnight autonomous session, immediately following WP-0.1.*

## What was built

`build/gen_readme_counts.py` computes 33 figures directly from the data (slot/group/room/grouping/parti/pack/kit/fault/style/constraint/exemplar/affinity/image/MCP-tool counts, including a populated-vs-empty kit split and a specified-vs-open slot split) and rewrites the marked block at the top of `README.md`. Every count the header line makes now matches what the script computes; nothing in that line is typed.

`README.md` body prose was corrected in four places that the header line's own accuracy had masked: "82 universal slots" → 93; "materializing all 89 slots" → 93 (with kit count added: 132 total, 3 populated); the Georgian Colonial paragraph's six embedded statistics (was quoting 89/398/402/30, all stale) recomputed directly from `kits/georgian-colonial-american.kit.json` (now 93/417/417/33, plus 88 specified-or-forbidden and the 172/14 editorial/invented parameter split that `check_kits.py` already reports); the `mcp_server/` table row's "17 tools" → 23. The Tidewater Georgian and English Georgian override counts (24 and 8 non-open slots respectively) were verified against the actual kit files rather than copied from the state-of-project review, and matched it exactly.

`mcp_server/README.md`'s tool count and table were rebuilt from `server.py` directly (`@mcp.tool()` count and each function's docstring first line via `ast.parse`, not by hand), and regrouped from one flat list of 17 into ten sections matching the project's own layer stack (orientation, vocabulary, alphabet, bindings, grammar, solecisms, phrase layer, critic, generator, evidence) so the table also does double duty as a map of the architecture, not just a tool index.

`docs/open-questions.md` items 1, 2, 12, 13, 17, 23, 24, 25 are marked RESOLVED with the ruling recorded inline and a pointer to where it took effect (1 and 2 from Lucas's prior rulings recorded in project memory; 12, 13, 17, 24 from tonight's clarifying-question round; 23 and 25 because the layers they describe as missing — rooms/groupings, faults — have existed since v0.6). Item 16 is marked IN PROGRESS with a note that it needed no ruling (the operator's shape was already declared in schema 0.2.1). Item 20 is marked "now a test rather than a decision," matching how the Plan of Action itself frames it.

`docs/README.md` is a new index in stack order, one row per layer, pointing at the doc that covers it (and flagging the three that don't exist yet — `structure.md`, `elevation.md`, `site.md` — with the work package that will add them, so a missing link reads as "not built yet" rather than "broken").

`CHANGELOG.md` is new, starting at v0.5-and-earlier, with v0.6 and an "Unreleased" section for this session's work so far.

## What was found

The zip's `README.md` — which WP-0.1 correctly chose as the base over the disk's older, less complete root copy — had *internal* drift, not just staleness relative to the data: its own header line already said "93 element slots · 23 MCP tools" while three lines later the body said "82 universal slots," and the `mcp_server/` table row said "17 tools" — six lines apart, contradicting itself. This is a stronger version of the finding the 23 Aug review made (README says 82/17 against reality 93/23): the header had already been hand-corrected at some point and the body prose had not, which is exactly the failure mode a generated block is meant to make structurally impossible going forward.

The Georgian Colonial kit's own statistics had drifted too, in the other direction — the README undersold it. The prose said 398 variant records and 402 parameters; the actual file has 417 of each, 119 forbidden variants (not 117), and 33 slots with pack precedence (not 30). The state-of-project review's Appendix inventory table matches the corrected figures exactly (417/119/33 would need re-deriving from its own text, which doesn't state them at this granularity) — this was authored fresh from the kit file, not copied from either source, and it happens to agree with the review's narrative numbers where the review gives narrative numbers (24-slot Tidewater override, 8-slot English Georgian override) and corrects the README's number where the README's number was simply wrong.

## What was deliberately not done

The README's former "Open questions" section (six numbered items, its own separate numbering from `docs/open-questions.md`'s 25) was replaced with a short paragraph pointing at `docs/open-questions.md`, rather than kept in sync by hand. Keeping two copies of the same judgement-call list, numbered differently, with different wording, is the same failure mode as the slot-count drift — it was going to happen again the first time a question got resolved in one copy and not the other. This is a slightly larger edit than "regenerate the counts block," but it's in the spirit of "doc drift was one of the findings of the review — do not add to it" from the Plan of Action's operating rules, and it was flagged rather than done silently: this paragraph is that flag.

No data file was touched. The four remaining unresolved slot-scattering and cascade-depth questions (14, 15, 18, 19, 21) were left exactly as open as they were found — this package reconciled documentation against the schema/data reality as it stood at the time, and recorded rulings 12, 13, 16, 17 (already made) with a pointer to WP-1.3 as the package that would execute them.

**Correction, 23 Aug 2026 (written while migrating constraints in WP-1.1):** the line above originally said WP-1.1 and WP-1.3 were "running concurrently... actively changing" the schema/data reality this package reconciled against. That was wrong on two counts: the packages ran sequentially, not concurrently (WP-0.3 and WP-1.1 both landed between this package and now), and WP-1.3 has not run at all — items 12, 13, 16, 17 in `docs/open-questions.md` originally claimed WP-1.3 had already executed their rulings, which was also false and has been corrected there directly. This package's own reconciliation work (the counts, the prose corrections, the RESOLVED/OPEN status legend) is unaffected and still accurate; only the framing sentence about concurrent future work was wrong, and is left here struck through by this note rather than silently edited, since the report itself is a record of what this package believed at the time it ran.

## Open questions raised

None new.
