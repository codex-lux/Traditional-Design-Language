# oq/the-assistant-is-blind-to-the-page — the pane is named now, and it is still told nothing about what the reader has selected

*Status: IN PROGRESS — ruled 25 Sep 2026, executed by WP-14.22 · Raised in: WP-14.0 (24 September 2026)*

**What was ruled and what was not.** On 24 September Lucas ruled that the right-hand pane is
named — *"Ask the corpus · AI assistant"*, worded from a glossary record, on the pane head and the
folded spine — and that its CONTEXT waits for a later tranche. So the naming half of the audit's
finding is settled and is not this question. This question is the other half: the assistant a
reader is now told they are talking to cannot see the page they are asking about, and changing
that edits `workbench/server/rail.py`, which tranche 1 keeps byte-stable.

## The evidence, measured on this tree

- **The shell has the selection and does not pass it.** `workbench/app/src/App.jsx:55` destructures
  `{ surface, selection }` from the route and hands `selection` to every surface through `shared`
  (`:154`); the rail is mounted at `:182` with `surface`, `plan` and `lastEval` only.
- **What the client sends** (`workbench/app/src/rail/RailHost.jsx:42-51`): `surface` (a surface
  id), the bench `plan`, a three-key cut of `last_eval`, and `candidate_count`. Nothing names the
  style, pack, slot, fault, term or candidate on screen. A reader on `#/proportions/trim-classical`
  asking *"why is the dado so low?"* is described to the model as *"The user is looking at the
  proportions surface"* (`rail.py:163-164`) — which pack, the model is not told.
- **The server reads a key the client never sends, and the client sends one the prompt never
  reads.** `rail.py:171-172` appends `candidate_summaries` to the context block; no file in
  `workbench/app/src` produces that key. `candidate_count` goes the other way: `rail.py`'s context
  block ignores it and `workbench/server/citations.py:92` reads it only to validate a
  `candidate:N` citation. So the candidate set a reader is comparing never reaches the prompt at
  all, on a route whose code says it does.
- **No tool answers the reverse relation a reader asks first on a pack page.** "Which styles use
  this?" — `tdl_get_proportions` (`mcp_server/server.py:117`) returns `assemblies, authority,
  conflicts, derived_rules, diameters_per_module, hint, invariants, judgment_rules, module_in,
  name, pack, part_in, parts, resolved_from, totals` and no binder list; no other of the 27 tools
  inverts it. For `trim-classical` the corpus's answer has four parts that a tool would have to
  keep apart: named in 36 styles' `proportion_packs`, opted in by 6 through `inherits_packs`,
  declined by 6 through `declined_packs`, and listed in 42 by the pack's own `applies_to`.
- **The byte-stable prompt is already stale, which is what byte-stability preserves.** `rail.py:118`
  tells the model *"of 209 fault causes in this corpus, exactly one is ignorance"*; `faults/`
  holds 210 records, 210 causes, one with `driver: ignorance`. `build/check_counts.py` reads
  Markdown and never opens `rail.py`, so nothing polices the figure. And `rail.py:113-117` tells the
  model it is *"the rail"* speaking to *"a plan-development lead at a production builder"* — the
  pane will now say AI assistant and the prompt will not.

## What each answer would change

1. **Send the selection** — the client adds the route's own citation of what is on screen
   (`style:…`, `pack:…`, `fault:…`, `term:…`, the candidate set's summaries) and `_context_block`
   reads it. This edits `rail.py` and `RailHost.jsx`, moves the prompt every turn carries, and has
   to answer a budget question: `_context_block` already truncates the plan at 6,000 characters and
   the candidates at 4,000, and a dossier section is larger than either.
2. **Send the citation only, and let the model fetch** — one line, the route's `citeFor` output,
   and the model calls a tool for the record. Cheapest on tokens and it reuses the citation grammar
   rather than a fourth spelling of it; it needs a tool that answers pack → styles (above), which
   changes the MCP surface.
3. **Starter questions per page** — offered by the pane from the page's own glossary `surface`
   record rather than written in the app, since Phase 14 forbids app-written explanation. Useful
   only after 1 or 2: a starter question about a page the model cannot see is a question it will
   answer about a different page.
4. **Leave it** — and say so on the pane: *"The assistant is not told what this page shows; name
   the record you are asking about."* That is a sentence the app would have to write, which is why
   even the refusal needs a glossary record.

Whichever is chosen, the stale `209` and the *"the rail"* self-description are the prompt's to fix
in the same commit, because tranche 1 is the reason they were not.

## What tranche 1 does meanwhile

Names the pane from its glossary record (WP-14.13: the pane head, the folded spine, the greeting and
the off-state copy in `RailHost.jsx`), folds it by default below about 1500 px where the reader has
stored no choice, and leaves `rail.py`, what it is sent, and `/api/rail/messages` byte-stable. The
dossier's *used by* list (WP-14.4's `used_by`) is served to the page and not to the assistant.

## Related

- `oq/mcp-proportions-serve-no-assemblies-for-non-order-packs` — the other place a machine client
  of this corpus receives less than the page shows.

## Ruled 25 September 2026

**The page's citation, plus starter questions (answers 1 and 3, in the citation form).** The context gains one line naming the record in view. The line is written only when the server's own citation validator accepts it, and the model fetches the record with the tools it already has. Starter questions come from each page's `surface-*` glossary record. The same commit corrects the prompt's stale facts: the typed fault figure, "the rail", and the missing citation kinds. The contract is `docs/prd/phase-14-tranche-2.md` §C.8. The tranche-1 freeze on `rail.py` is lifted for this item alone. The question closes when WP-14.22 lands.
