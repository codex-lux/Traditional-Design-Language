# The workbench made legible — a first-principles analysis of the interface, 24 September 2026

**Status: WP-14.0's analysis (24 September 2026). It opens Phase 14.** Commissioned by Lucas the
same day against a screenshot of the Proportions surface; the eight scoping questions it raised
were ruled the same day and are recorded in §II. The build it leads to is WP-14.1 through
WP-14.15, each of which ends with its own report.

*Every figure below that describes the code or the corpus was re-derived on the tree at `d565dea`
on 24 Sep 2026, by the command or the file:line given beside it. Where the re-derivation differs
from the audit that preceded it, this report publishes its own figure and says what the audit
said. A figure this report could not re-derive is labelled as the audit's. The measurements are
collected in the appendix, §XI.*

---

## I. What Lucas read, and what on that one page made it read that way

His words, verbatim:

> This traditional design language encyclopedia has become rather difficult to navigate. I admit
> I don't fully know where I'm going or what I'm looking at when I'm browsing these menus and kits
> and items. It's all just a bunch of text, and I'm not sure how it all relates to each other.
> I'm afraid I need a lot tooltips, keys, visuals, etc. I want you to do a full first-principles
> analysis of the user interface, the UX ... and how it can be arranged and formatted in a much
> more accessible, intuitive manner. I also want to consider the people that are just coming to
> the website with no idea what it is and what it's for.

The screenshot was the Proportions surface on the pack `trim-classical`. Across the top, the
masthead: `centre-passage-double-pile-tidewater · tidewater-georgian · 4 unjudged`. Down the left,
the surface rail in five groups — START / READ THE CORPUS / COMPOSE / TAKE IT OUT / BRING IT IN —
with metas like `164 taxa`, `9 sections`, `210 solecisms` and `and its criticism`. Beside it, a
second column of 57 monospace pack ids. In the reading pane, the pack opens on the eyebrow
`INVARIANTS · PROVED AGAINST THE DATA` and ten green squares, each a sentence over an engine
expression. **No drawing.**

Every element of that screen has a mechanical cause, and they are worth setting out one by one,
because the analysis that follows generalises from them.

1. **There is no drawing because the plate is gated to order packs.**
   `Proportions.jsx:410` reads
   `const hasPlate = isOrder && (data?.assemblies || []).some((a) => (a.members || []).length);`
   and `trim-classical` is a `trim-system` pack. Measured over all 57 packs, **25 draw a plate
   today** — every order pack except `moorish-arch` — and **32 draw nothing**.
2. **Removing the gate would still draw nothing, because the server serves no assemblies.**
   `workbench/server/corpus.py:328` dimensions the pack with
   `pe.dimension(pk, out["module_in"], None)`, and `mcp_server/core.py:459` does the same for the
   MCP tool. With `include=None` the
   engine stacks only what `stack_for` knows, which is order assembly names; for `trim-classical`
   it returns **zero assemblies**. Asked one assembly at a time, the same engine returns the
   Georgian, Federal and Greek Revival wall sections and casings — **20, 21, 12, 7, 7 and 4
   members, 71 in all**. Corpus-wide, **27 packs have assemblies and an empty stack** (the 26
   non-order packs that have assemblies, plus `moorish-arch`, an order pack whose impost, arch and
   alfiz no stack names), holding **50 assemblies and 237 members** that no surface can draw.
   Five packs have no assemblies at all.
3. **And if it were served, it would be drawn in the wrong place.** `build/profiles.py:522` sets
   the datum as `R = lower_diameter_in / 2`. For `trim-classical` the engine's totals carry
   `lower_diameter_in: 228`, so every wall section's naked stands at **x = 114 in** — the 9′-6″
   ceiling module read as a column radius. A trim plate needs a wall-plane datum before it can be
   drawn at all.
4. **And the drawing would disagree with the table beside it.** The rules are evaluated at the
   ceiling slider, which defaults to 108 in (`Proportions.jsx:367`), while the module stays at the
   pack's default 114 in, because `core.get_proportions` derives the module only from `module` or
   `column_diameter` (`core.py:457-458`). `trim-classical`'s rules are `ceiling_height`
   expressions: the baseboard is `ceiling_height * 1.5 / 19`. **A naively served plate would draw
   a 9″ baseboard beside a rules table reading 8 1/2″** (`proportion_engine._fmt_in` of 8.5263).
   The slider moves the table and not the wall.
5. **The page opens on proof because proof is what it renders first.** The record's order is
   head (`:500-523`), invariants under `invariants · proved against the data` (`:525-535`),
   authorities (`:537-571`), the 18 rules (`:583-597`), and the conflicts last (`:599-624`).
   `trim-classical` carries **10 invariants, 18 rules and 6 conflicts**, and the first conflict in
   its own record is the `blocking` one — the eight-foot ceiling against a full classical trim
   family, which the pack itself calls its defining conflict. It is drawn at the foot of the page.
   All **313 invariants in the corpus hold**; each is printed with its engine expression as the
   caption (`:530-531`).
6. **The green squares carry no word, and the one mapping behind them is wrong.** Each is a
   `JudgmentMark` whose square is `aria-hidden`, so the verdict is colour alone: pass
   (`--green-deep`) and fail (`--brick`) differ by **1.08:1 in luminance**. And `:530` reads
   `state={iv.holds ? 'pass' : 'fail'}`, so `holds: null` — which
   `build/proportion_engine.py:654` writes when an invariant cannot be evaluated — is drawn as a
   fail. It is latent today (0 of 313 are null) and it breaks the rule this corpus holds above all
   others: unjudged is not failed.
7. **The 57 ids are ids because the list prints `p.id`.** `Proportions.jsx:463-470` renders each
   pack's id in `--type-data-s`, which is Courier, although `pack_list` serves each pack's name
   (`corpus.py:306`). The list is grouped under plain kind labels (`KIND_LABEL`, `:21-25`) while
   the record's own first eyebrow prints the raw enum, `trim-system` (`:500`).
8. **The address bar did not know which pack was on screen.** A pack click calls only
   `setPackId` (`:463`, and the authority rows at `:558`); `Proportions` takes
   `{onCite, selection}` and never the `setSelection` every surface is handed (`:360`). A refresh or a
   shared link therefore shows `gibbs-doric` (`DEFAULT_PACK`, `:19`), which is **43rd of 57** in
   the list — off-screen. `onCite` is received and never called, so nothing on the page links
   anywhere.
9. **The masthead is the bench's state, unlabelled, over a reference page.** `Chrome.jsx:85-86`
   prints `plan.id` and `plan.style` as bare Courier spans — the style in `--ink-4`, which is
   2.26:1 on the paper — and `:87-94` adds `N unjudged` from `lastEval`, which only the Plan
   Workbench sets (`App.jsx:160`, `PlanWorkbench.jsx:224`) and nothing clears, with its meaning in
   a `title` attribute (`:90`). On the Proportions page that line reads as the page's subject.
   The style it names, `tidewater-georgian`, does not bind `trim-classical` — it binds
   `brick-course`, `storey-graduation`, `timber-bay` and `sash-light` — though it is one of six
   styles that opt into it through `inherits_packs`. Beside it, the Export and Settings icons
   (`:96-98`) look like controls and do nothing.
10. **The rail's metas are jargon or fragments, and one is typed by hand.** `164 taxa` (`:37`),
    `9 sections` (`:38`, a literal), `210 solecisms` (`:41`), `and its criticism` (`:44`). The
    rail holds **twelve** entries in five groups (`Chrome.jsx:33-56`): the Overview under START
    and eleven more.
11. **What the page never says is what a practitioner came for.** `trim-classical` is bound by
    **36** styles, opted into by **6**, and its own `applies_to` names **42** — thirteen that do
    not bind it and seven binders it does not name. Nothing in the payload says so and nothing on
    the page asks.

**So the screen Lucas read is not a page missing its tooltips.** It is a drawing machine behind a
text interface (items 1-4), a disclosure order run backwards (5-6), machine names where
architectural names are served (7), an address that forgets (8), a landmark that belongs to a
different task (9), and a relation that is never shown (11). The rest of this report is those six
causes found everywhere else.

---

## II. The eight rulings, 24 September 2026

Lucas answered the scoping questions the analysis raised on the day it was written. Recorded
verbatim from the approved plan's decisions table:

| Question | Ruling |
|---|---|
| Who the front door speaks to first | **Practitioners first** — architects, designers, plan developers, builders. A newcomer still gets a plain-language front door and a guided example; the instrument is not simplified. |
| Where definitions live | **New glossary records** — a versioned `glossary/` record set in the corpus, plain definition + analogy + sources where they exist, a checker, served by the API. Every tooltip reads it. |
| How much structure changes | **Rebuild the navigation now** — reorganise around a Style dossier and a House journey (brief → candidates → plan → drawings); the current surfaces become indexes. |
| Deliverable this session | **Report + plan, then build tranche 1**, with tests. |
| Dossier section names | **Unambiguous**: Identify · Filed under this · Lineage · Kit · Proportions · Plan types · Constraints · Faults · Evidence (URL ids stay `members`/`plans`/`rules`). |
| The AI pane | **Name it now, context later**: "Ask the corpus · AI assistant" from a glossary record (pane head + folded spine); `rail.py` and what it is sent unchanged until tranche 2. |
| Laptop width | **Fold the assistant on narrow screens**: below ~1500px with no stored preference it starts folded (a stored choice wins); front door and Glossary reflow; working surfaces keep their minimum. |
| The Gate | **Yes, one sentence**: ungate exactly `GET /api/glossary/about-tdl` and show its definition on the Gate; no other corpus text becomes public. |

Four of these were rulings on questions the audit had proposed to file as open questions — the
section names, naming the assistant, the narrow-screen fold and the Gate sentence. They are
recorded here as rulings and are **not** filed.

---

## III. Method, and what the adversarial pass corrected

**The audit was read-only and ran in five layers**, on 24 Sep 2026:

1. **Eleven inventories**, one per part of the product: the shell, the Phylogeny, the Style
   Record and Kit, Proportions, the Fault Corpus, the compose path, the Plan Workbench, the
   output surfaces, the visual system, the domain vocabulary, and the history of rulings that bind
   the interface.
2. **Five lenses** read across all of them: the newcomer's first five minutes, the practitioner's
   journeys, the information architecture, the visual system, and help and definitions.
3. **Fourteen themes** merged the lenses' findings.
4. **Fourteen adversarial verifications**, one per theme, each re-checking every claim against
   the source and naming what the theme overstated, understated or missed. Six themes came back
   **confirmed** (T05, T07, T09, T10, T12, T14) and eight **partly** (T01, T02, T03, T04, T06,
   T08, T11, T13). **None was refuted.** The findings in §V carry the corrected statements, not
   the themes' originals.
5. **Three competing redesigns** (dossier-journey, language-map, practitioner-desk), **two
   independent judges** (a reader and an engineer), and **one synthesis**. §VII.

This report then re-derived the load-bearing figures on `d565dea` itself (§XI).

**What the verification pass corrected, and it is worth reading before trusting any first
reading of this interface — including one's own:**

- **"Unjudged is not passed" is not hover-only.** It is visible body text in three places:
  `PlanWorkbench.jsx:699-701`, `CandidateColumn.jsx:104-110` (whose comment says it is "never left
  to a tooltip") and the AI pane's greeting, `RailHost.jsx:20-22`. The masthead's `title` at
  `Chrome.jsx:90` is a fourth. What is true is narrower: the masthead count's meaning is hover-only,
  and nothing explains the solid pass/fail squares.
- **Buttons do keep a focus ring.** They keep the browser's default. What is missing is a global
  `:focus-visible` rule (`tokens.css:442` styles only `a`), three text inputs that set
  `outline: none` with no replacement (`StylePicker.jsx:75`, `FilterInput.jsx:57`,
  `CommandPalette.jsx:129`), and keyboard access to candidate columns (a `<section onClick>`,
  `CandidateColumn.jsx:128-131`), map marks and sheet rooms.
- **The fault card does have a right way.** `FaultCard.jsx:234` renders three fix tiers named
  right, cheap and dishonest. What it never renders is `correct_practice` (the right way in full)
  or `detection` (how to spot it): **all 210 fault records carry both, and a grep of
  `workbench/app/src` for either field returns nothing.** The card is not in the wrong order; it
  omits.
- **`moorish-arch` is an order pack with no stack.** A gate written as "dimension each assembly
  when the pack is not an order" would still leave it undrawn; the gate has to be "the stack is
  empty and the pack has assemblies".
- **`composite` has four authorities, not five.** `Proportions.jsx:540` prints the literal
  `five authorities`; `core.compare_authorities` returns five rows for tuscan, doric, ionic and
  corinthian and **four** for composite (there is no `benjamin-composite`).
- **42 `hybridizes_with` edges carry the kit.** All 42 have `inherits_kit: true`, and
  `EdgeGlyph.jsx`'s type table (`CARRIES`, `:6-9`) knows only `descends_from` and `regional_of`, so
  its caption (`:65`) tells the reader those 42 edges carry nothing. The Phylogeny's and the Style
  Record's one plain explanation of what an edge does is wrong on 42 edges.
- **The first-time visitor never sees the masthead's ids.** `planDoc` starts null and fills only
  from localStorage; the false landmark afflicts returning readers — Lucas — not the newcomer,
  whose problem is the absence of any page name.
- **The Brief does not open blank.** It opens on Tidewater Georgian with the family brief's
  numbers copied in and nothing saying they are defaults (`BriefIntake.jsx:42-48`).
- **The corpus's "plain" model is not plain.** `core.overview().the_model` addresses an agent
  ("Say so to the human") in DAG vocabulary, and `how_to_use_it` is a list of MCP tool calls. Any
  front door built from them would repeat the agent-voice defect; the glossary has to be written,
  not copied.
- **The homeowner is not a reader of this tool.** A first remedy proposed a front-door line for
  the homeowner "condensed from VISION IX". VISION IX says of the people who live there: *"They
  will never see any of this, and they are the point"* (`VISION.md:359`). That line was struck.
- **The 73 generated profile plates reach no surface at all**, which is worse than the theme said:
  the only component that mounts an image record (`UnsourcedImageRecord`) is mounted by the Fault
  Corpus for fault assets, and none of the 73 depicts a fault. All 73 are order-pack plates.
- **The DXF export already names its face** (`export_dxf.py:679`); the same-name download bug is
  the Drawing Set's SVG (`DrawingSet.jsx:203`). The Export surface has no face control at all.
- **The URL does drive the screen; the screen never writes back.** Proportions re-syncs from
  `selection.pack` (`:378`); what fails is every pick going to local state. And a consequence the
  theme missed: after a local pick, a citation to the record the URL still names does nothing,
  because `nav.write` returns early when the hash has not changed (`nav.js:63`).
- **`test_grammar_agreement.py` pins character classes, not kinds or routes.** A section
  vocabulary pinned by it is new scope, not an extension.
- **Two claims the audit made could not be reproduced and are not published here**: "291 enum
  descriptions across five UI-facing schemas" (the verifier found about 92 of 390 enum values
  named in any description) and "8 style-specific faults for Tidewater Georgian" (it reproduces
  under one definition of "specific" only).

**The lesson is the one this repository keeps relearning.** Each theme was written by a reader
who had read the code, and eight of fourteen still overstated something — almost always in the
direction that made the theme's own remedy look more needed. The verifiers also found
understatements (the plates that reach no surface; the URL that cannot be moved back to by a
citation), so the pass was not merely a discount. Re-derive the number; do not re-read the
sentence.

---

## IV. First principles

### The five questions

A reader at any page needs five answers, in this order:

1. **Where am I?**
2. **What is this thing?**
3. **What does it mean for me** — at my building, for my house?
4. **How does it relate** to what I care about?
5. **What can I do next?**

The workbench answers the fourth and fifth well **for a machine** — every record is citable, the
URL is the citation grammar, ⌘K reaches 666 named things — and answers the first three for almost
nobody.

| Question | What the workbench answers today | What tranche 1 answers |
|---|---|---|
| Where am I? | The rail's `aria-current` bar, until the rail folds. `document.title` never changes (`index.html:6`); `SurfaceHead` is exported and imported by nothing (`Chrome.jsx:316`); no breadcrumb; the wordmark is a `div` (`Chrome.jsx:64-67`). The masthead's only persistent content is another task's state. | A crumb strip from `member_of`, a page title per place, a wordmark that goes home, "On the bench: *plan name*" as a labelled link. |
| What is this? | A surface name in four strip eyebrows; nothing on the other eight. About 40 corpus words (the audit's count) appear undefined — taxon, rank, kit, slot, binding, cascade, pack, module, invariant, parti, massing, solecism, unjudged. | A page head on every surface, and every word a `Term` that opens its glossary record. |
| What does it mean for me? | Proof first; the answer at your building last or absent; decimal inches. | Picture → numbers at your building → warnings → sources → proof, folded. Feet and inches to the sixteenth. |
| How does it relate? | One way at best. The pack page does not say who uses it; the Kit prints packs as strings; 138 of the 666 palette results land on a "searched" banner. | Relations both ways: a pack's users, a style's packs by how they arrive, a relations panel on the dossier. |
| What next? | Eleven equal doors; a house path split over three rail groups with no stepper; three of four budget options refused. | Two spines — a style read whole, a house taken from brief to drawings — each saying where you are in it and what the next step needs. |

### The frame: a building you can find your way around

The corpus describes itself as a language — *"A traditional house is a sentence in a language,
and the language can be written down"* (`VISION.md:95`) — and it is organised the way a pattern
language is: elements that recur, relations between them, and a grammar that governs their
combination. **The interface ought to be navigable the way a well-planned building is**, and the
vocabulary for that already exists. Kevin Lynch named what makes a place legible to someone
moving through it: **paths**, **districts**, **landmarks**, **nodes** and **edges**. Each has an
architectural counterpart a practitioner uses without thinking, and each is either missing or
misleading here.

| Lynch | In a well-planned house | In the workbench today | In the rebuild |
|---|---|---|---|
| **Paths** — the routes you move along | The enfilade; the stair; the passage from front door to garden | The URL grammar is excellent; but every rail click drops the reader's style (`nav.js:86-91`), so no path carries you from one room of a subject to the next | Two spines: a Style (identify → lineage → kit → proportions → … → evidence) and a House (1 Brief → 5 Export), with the style carried in the URL |
| **Districts** — areas with a recognisable character | The public rooms, the service wing, the chambers above | Twelve surfaces of one visual form under five groups sorted by record type and by errand | Three named districts — Styles, A house, Library — plus a front door |
| **Landmarks** — fixed points you orient by | The hall's stair; the chimney breast; the one room you always return to | One false landmark: the bench plan's ids, bare, on every page. The worked house (Tidewater Georgian) is everywhere and is never named as the example | "On the bench: *plan name*"; the style in hand named in the rail; Tidewater Georgian labelled as the guided example; the drawing at the head of a pack page |
| **Nodes** — the decision points | The hall where you choose a door | The Overview: eleven equal doors, one agent-voiced sentence, a schema version | The front door: what this is, two entrances in the reader's words, the libraries third |
| **Edges** — the boundaries, and the openings in them | The line between the public rooms and the service wing, and the door through it | Reading and composing are islands; no bridge from a style to a brief | "Design a house in this style" from the dossier; the journey's step bar blocking — with its reason — where a refused placement stands |

And on every door a plaque: **a crumb, a page title, a "what this is" head, and every word
defined where it stands.** That is the whole of the design in one sentence, and §VII is its
detail.

**Two cautions keep the analogy honest.** First, a building metaphor is a way of reasoning about
the plan, not a word to put on the screen — the rejected practitioner-desk design put "the desk"
on screen beside the existing "bench" and gave the reader two pieces of furniture for one house
(§VII). Second, the corpus is its own authority on its own structure: VISION's nine layers
(`VISION.md:196-223`) are the right words for a Glossary group and the wrong words for a rail,
because a practitioner does not navigate by how the corpus was built.

### The rules the rebuild keeps

- **The URL decides what is read.** Per-browser memory — the style in hand, folds, seen flags —
  may offer links and never fills a bare URL.
- **Every definition is a glossary record; the app writes none.** `Term` has no definition prop
  and no fallback.
- **Picture, then the answer at your building, then warnings, then sources, then proof** — folded,
  never removed, and counting unjudged separately.
- **Unjudged is never collapsed.** `holds: null` is unjudged; the journey keeps fatal, serious and
  unjudged as three counts; refused is its own state and never a link forward.
- **Names first, the id as a Courier margin note; feet and inches to the sixteenth.**
- **Counts come from the API**, never from a JSX literal or a test literal.
- **The citation grammar stays spelled in exactly three places.** Routes change; the regexes do
  not.
- **Machine surfaces stay byte-stable in tranche 1**: MCP payloads, `core.overview()`, `rail.py`,
  `/api/health`; `auth.OPEN_PATHS` gains exactly the one ruled path.
- **Draw only what the record holds**, captioned so; refuse out loud what it cannot support.
- **Graphic Standard No. 1 is kept**: no new colours or inks, and no readable text in `--ink-4`
  in new code.

---

## V. The fourteen findings

Each finding is stated as the adversarial pass left it, with its figures re-derived where this
report could, the file:line behind it, who it hurts, and the tranche-1 package that answers it.
Severity is the theme's own after verification: **blocking** where the reader cannot do the thing
the surface exists for, **major** where the reader can do it with difficulty.

### 1. Nothing says what this is or how the parts relate — blocking

**The landing's only product-level paragraph is written to an AI agent.** `Overview.jsx:92-96`
renders `core.overview().what_this_is`, which reads *"An evolutionary taxonomy of traditional
architecture with an executable proportioning grammar, a kit-of-parts directory per style, and a
corpus of named errors. Built to be consulted mid-conversation while advising a human on a real
house"* (`core.py:124-127`). It is the MCP orientation string, and the AI pane feeds the same
object into its system prompt (`rail.py:272`). It never says one can compose, check or draw a
house here.

- The inventory prints **164 styles** for what are 5 traditions, 27 families, 90 styles and 42
  variants; `by_rank` is served and not shown, and the same page calls the number `164 taxa`.
- There is no diagram, no image and no `title` on the whole page.
- The page-wide comment `Not one number, claim or sentence on this page is written in the app`
  (`Overview.jsx:8-10`) is false — the eleven `DOORS` (`:24-54`) are app-written — and
  `The rail groups by the same three` (`:22-23`) is false: the rail has five groups.
- VISION IX and X answer the newcomer's questions (who this is for; what it is not) and are
  served nowhere.

**Who it hurts:** every cold visitor; Lucas, who has no picture of how style, kit, proportions,
faults and the house fit together; colleagues he shows it to.
**Answered by:** WP-14.14 (the front door: `about-tdl`, reader lines from VISION IX without the
homeowner, two entrances, the two-spine map as ruled rows of links), WP-14.1/14.2 (the records it
reads), WP-14.3 (the one ungated sentence), and WP-14.14 again (the Gate shows it).

### 2. The navigation is a card catalogue, and every hop drops your style — blocking

**This, more than missing tooltips, is why the pages feel unrelated.** Rail items call
`onGo(it.id)` with no selection (`Chrome.jsx:166`); `nav.go` writes `selection || {}` and empty
params, and its comment says selection deliberately does not cross a surface boundary
(`nav.js:86-91`). Each surface then falls back to its own hard-coded record without saying it is a
fallback:

| Surface | Default | Where it sits |
|---|---|---|
| Style Record, Kit | `DEFAULT_STYLE = 'tidewater-georgian'` (`StyleRecord.jsx:15`, `KitSurface.jsx:17`) | — |
| Phylogeny | `DEFAULT_TAXON = 'tidewater-georgian'` (`Phylogeny.jsx:20`) | row 73 of 164 |
| Brief Intake | `style: 'tidewater-georgian'` (`BriefIntake.jsx:43`) | — |
| Proportions | `DEFAULT_PACK = 'gibbs-doric'` (`Proportions.jsx:19`) | 43rd of 57 |
| Fault Corpus | `DEFAULT_FAULT = 'porch-too-shallow-to-inhabit'` (`FaultCorpus.jsx:16`) | row 100 of 210 |

A reader studying Craftsman who clicks *The Kit* is shown Tidewater's kit. **Testing with
Tidewater hides the defect**, because Tidewater is the default everywhere a style is involved.

- **The Phylogeny sorts by date and indents by rank** (`Phylogeny.jsx:87-92`, `:270`), so
  **111 of its 159 non-tradition rows sit under a row that is not their parent**. The right order
  exists in `build/render_html.py:24-35`.
- **Family and tradition records render empty.** `core.get_style` never inverts `member_of`
  (`core.py:218-224`): **32 of 32** family and tradition records return no lineage and no
  descendants, `american-colonial` among them though six styles are filed under it, and
  `StyleRecord.jsx:213` then hides the whole section. These include the five traditions, which are
  the Overview's only style links.
- StylePicker opens on 60 names and shows no rank; Brief Intake's style select lists all 164 raw
  ids, families and traditions included (`BriefIntake.jsx:56,163-164`).

**Who it hurts:** Lucas studying any style but the default; practitioners comparing styles;
newcomers, who conclude the product is about one style.
**Answered by:** WP-14.12 (the Style Dossier at `#/style/<id>/<section>`, the Styles index as an
outline tree, the slot panel, `#/kit` as an alias), WP-14.13 (the rail from one `navModel`),
WP-14.5 (sections and context carry in the addresses), WP-14.4 (the dossier summary), WP-14.6
(`styleTree.js` ported from `render_html.py`).

### 3. No term is defined where it appears, and there is nowhere to put a definition — blocking

**The product has no definition layer.** There is no `glossary/` directory, and a grep of
`workbench/app/src` finds **no** `aria-describedby`, `role="tooltip"`, `aria-live` or
`role="status"` — the only live region is the Gate's `role="alert"` (`Gate.jsx:80`). All
explanation is **58 `title=` attributes and props** in `.jsx` files (the audit counted about 57)
and **9 SVG `<title>` elements**, every one hover-only and so invisible to touch and keyboard.
`SourceChip.jsx`, which does define the parameter source kinds, is imported by no file — while
`SlotRow.jsx:173-181` prints those kinds on every expanded Kit row with no definition.

- **Three app-written catalogues describe the same destinations and disagree**: the rail
  (`Chrome.jsx:33-56`), the Overview's `DOORS` and the palette's entries (`staticEntries.js:12-78`).
  One record type is `solecisms`, `named` and `faults`; the palette marks Brief Intake
  `start here` (`:45`) while the rail's START holds only the Overview; the palette has no Overview
  entry; the Fault Corpus filter says `209 faults` (`FaultCorpus.jsx:101-102`) against 210 records.
- **Homonyms collide**: *variant* (a rank; an option in a slot), *source* (the supplying ancestor;
  a bibliographic entry), *candidates* (composed houses; placement attempts), *invariant* (a
  validator invariant in `docs/model.md`; a pack invariant on Proportions), and "the Workbench" is
  both the product (tab title, masthead) and one surface. A glossary keyed on the bare word would
  make these worse.
- **The glosses that do exist are app-written**, and ruling 2 retires them: EdgeGlyph's captions,
  the Kit's "a thin kit is correct" and "massing is not style", Proportions' hatch sentence,
  Spotlight notes, the ShortcutCard's addressing key.

**Who it hurts:** Lucas, fluent in architecture and not in this corpus's words; newcomers;
keyboard, touch and screen-reader readers.
**Answered by:** WP-14.1 (schema, checker, registration), WP-14.2 (the tranche-1 records, homonyms
split by id), WP-14.3 (served, `term` citation kind, search), WP-14.8 (`Term`, `PageHead`,
`RecordLink`, the Glossary surface).

### 4. No page says where you are — major

- `document.title` is fixed at *The Workbench — Traditional Design Language* (`index.html:6`) and
  nothing writes it, so every tab and bookmark reads the same.
- `SurfaceHead` (eyebrow, title, note) is exported (`Chrome.jsx:316-330`) and imported by nothing.
- The wordmark is a `div` (`Chrome.jsx:64-67`); once the rail folds, no one-click way home remains.
- Proportions opens on a filter field; its record's first eyebrow is `trim-system`.

**The false landmark is real and narrower than first stated**: it appears only when a plan is on
the bench, so it misleads returning readers, and it can be internally inconsistent — `lastEval`
is never cleared, so a newly loaded plan's id can sit beside the previous plan's unjudged count.
**Credit where due**: the rail marks the current surface with `aria-current`, four surfaces label
themselves in their strip, and records carry plain-name `h2` titles.

**Who it hurts:** the colleague who opens a shared link; Lucas, reading bench ids as the page's
subject; anyone with several tabs.
**Answered by:** WP-14.13 (crumbs, titles, the linked wordmark, "On the bench" masthead, `lastEval`
reset, a visible Keys button, the cold-link banner), WP-14.8 (`PageHead` from `surface-*` records
on every surface).

### 5. Relations run one way and forget the style — blocking

- **Pack → styles is not served.** Neither `/api/proportions/{id}` path carries `used_by` or
  `applies_to`; `trim-classical`'s 36 binders, 6 opt-ins and 42-name `applies_to` are invisible.
- **Proportions receives `onCite` and never calls it** (`:360`); CandidateSet does the same.
- **The Kit prints governing packs as strings** — `${p.pack} · precedence ${p.precedence}`
  (`KitSurface.jsx:50`) — while the Style Record links them.
- **`api.slot` has no caller** (`client.js:81`), though `/api/slots/cornice` answers with 35
  specifying styles and 9 faults; a `slot:` citation lands on Tidewater's kit
  (`citations.js:38`).
- **Rooms, massings, partis and groupings — 138 of the 666 palette results — end on a "searched"
  banner** (`citations.js:45-48`). Detail routes exist for massings, rooms and groupings; partis
  have only a list route.
- **Context is dropped**: `nav.cite` writes only the routed selection (`nav.js:131`), so a fault
  opened from the Craftsman kit loses Craftsman. The receiving side already works (the router
  carries unknown keys in the query, and the Fault Corpus reads `?style`), so the carry is a change
  to `nav.cite` alone.
- **The Phylogeny's comparison prints `JSON.stringify(d)`** for entries shaped
  `{node, difference}` (`Phylogeny.jsx:346`).
- **Nothing links from reading to composing.** Brief Intake ignores its selection.

**Who it hurts:** anyone asking the encyclopedia's basic questions — which styles use this trim
family, and why; how do these two styles differ; what does this style ask of this fault.
**Answered by:** WP-14.4 (`used_by`, the style's packs by provenance), WP-14.5 (`CONTEXT_KEYS`,
`nav.cite(ref, ctx)`), WP-14.9 (Used by on the pack page, the `?style` chip), WP-14.12
(RelationsPanel, "Design a house in this style"), WP-14.8 (`RecordLink`).

### 6. The house journey has no spine and breaks at step one — blocking

**Step one fails in practice.** Brief Intake offers the budget tiers `entry`, `move-up`, `custom`
and `estate` (`BriefIntake.jsx:238`); the schema's enum is `value`, `mid`, `custom`, `unlimited`
(`schema/brief.schema.json:31`); `jobs.py:261-262` validates the brief before a job exists.
**Driven against the schema, 3 of the 4 options refuse the whole brief** and only `custom`
passes. The refusal is displayed; the menu offers no valid alternative.

- The path brief → candidates → plan → drawings → export is split over three rail groups with
  static metas (`Chrome.jsx:43-56`); its order is stated once, in an Overview blurb
  (`Overview.jsx:38`), plus scattered one-hop links.
- Compose is a filter `Chip` (`BriefIntake.jsx:133`); a failed compose job goes to
  `error: () => {}` (`CandidateSet.jsx:112`); an errored job found on reattach is dropped without a
  reason.
- Opening a candidate keeps no record of the job, candidate or brief (`CandidateSet.jsx:170-179`),
  so the bench cannot say where its plan came from.
- The two example briefs are listed by `/api/schema/brief` and cannot be loaded; `api.briefSchema`
  has no caller.
- The first picture of the house is the Drawing Set's default `model` view (`DrawingSet.jsx:100`),
  a metered heavy call.
- The Export surface has no face control and never sends one (`ExportDetails.jsx:85`), so its
  elevations are always the entrance front.

**Who it hurts:** designers, builders and plan developers using the tool for its main purpose.
**Answered by:** WP-14.10 (`JourneyBar` mounted once above `<main>`, budget tiers from the schema,
StylePicker, `?style` and `?example` seeding, Compose as a button, compose errors recorded,
`session.planFrom`), WP-14.6 (`journey.js`), WP-14.4 (the example-brief route). The Export face
picker waits for tranche 2.

### 7. A drawing machine behind a text interface — blocking

§I items 1-4 are this finding on Lucas's page. Beyond it:

- **The 73 engine-drawn profile plates in `assets/generated/` reach no surface.** All are order
  plates; none depicts a fault, and the fault page is the only mount for image records.
- **`DimensionString.jsx` is imported by nothing**; `POST /api/check/measurements` has no caller.
- The Style Record, the Kit, the fault card, the candidate columns and the Overview draw nothing.
- **The honesty constraint binds any remedy**: 1,777 of the 1,850 image records are `wanted`, no
  precedent record holds a file, and `render_profile.py` stamps its plates as not drawings of a
  real building. "Add visuals" must not become invented imagery.

**Credit where due**: the Phylogeny draws a tree and a map with a precision legend; EdgeGlyph draws
lineage by weight; the fault page's hatched "specified, unsourced" cards are already the honest
form of a wanted figure.

**Who it hurts:** architects and builders, who read drawings before prose; newcomers, whose first
impression is small grey type; Lucas, whose screenshot is this.
**Answered by:** WP-14.4 (per-assembly dimensioning gated on an empty stack;
`pack_geometry(..., datum='wall')` with the default byte-identical;
`module.equals: "ceiling_height"` on `trim-classical`, lie-checked by `check_systems`), WP-14.6
(`assemblyLayout.js`), WP-14.9 (`AssemblyPlate`, plate first).

### 8. Marks mean things with no key; tokens are overloaded — blocking

- **The hatch tokens carry many duties.** `--hatch-unjudged` means could-not-evaluate (the
  masthead, `JudgmentMark`), low confidence (`Phylogeny.jsx:279`), a rule deferred to you
  (`Proportions.jsx:319`) and loading (`BriefIntake.jsx:267` draws an unjudged `JudgmentMark`
  while partis load). `--hatch-45` has six uses; `--hatch-forthcoming` is defined
  (`tokens.css:207`) and used nowhere.
- **Hue duties overlap**: `--gilt-deep` and `--green-deep` each carry about eight (the audit's
  count), and tradition hue t3 is `--brick`, the UI's fatal.
- **Verdicts are colour alone** on the invariant squares (1.08:1 pass against fail), and
  `JudgmentMark` hides its square from assistive technology; its own verdict words are dead code,
  because every call site passes a label.
- **Keys exist in more places than first reported** — the plan sheet's furniture key and its
  ∗/△ caption, Proportions' hatch sentence, the Phylogeny's axis-break label, the taxon panel's
  edge samples — and the Kit's binding and kind colours sit on the printed word, so what is missing
  there is the definition, not a colour key. **Genuinely unkeyed**: variant status in `SlotRow`,
  the tradition swatches, the tree's dash and opacity encodings, the plate's dashed confidence
  outline, and the sheet overlays.
- **Dashes are overloaded too** (claims-only edges, country-only map rings, the plate's confidence
  outline, the axis break), so "low confidence → dashed outline" cannot be the fix on the tree.

**Who it hurts:** practitioners reading a Kit row, a plate or a sheet; colour-blind and
screen-reader readers; newcomers, who cannot even ask what a mark means.
**Answered by:** WP-14.6 (`judgment.js`: `holds: null` → unjudged), WP-14.9 (the in-frame plate
key, worded from the glossary), WP-14.11 (EdgeGlyph read from `inherits_kit`), WP-14.8 (focus and
Eyebrow). **A key for every mark and one duty per hatch wait** for a ruling:
`oq/one-duty-per-hatch`.

### 9. The corpus holds one complete worked house and never presents it as one — major

Tidewater Georgian has everything a worked example needs: the shipped brief *Family house,
Tidewater Georgian*; the shipped plan *Tidewater Georgian, five bays, carefully planned*; exemplars
with precedent records; the Four-Foot Porch, which VISION calls the type specimen (`VISION.md:59`),
as the Fault Corpus default; `gibbs-ionic` with generated plates. It is the default on four
surfaces and reads as an arbitrary one.

- Example plans are filename chips (`PlanWorkbench.jsx:387-390`); loading one sets
  `reviseNextRef` and runs a solve plus `INLINE_REVISE_ROUNDS = 2` (`:96`) before anything is
  shown, and the revision panel sits unfolded above the plate.
- The Georgian portico exception matches only its exact style id, so Tidewater never sees it.
- **The worked house's plan does not place**: both shipped plans are refused at placement (§X).

**Who it hurts:** newcomers, who need one concrete case; Lucas, demonstrating the tool;
practitioners, who learn an instrument fastest by watching it work on a familiar house.
**Answered by:** WP-14.14 (the guided example labelled as such on the front door), WP-14.13 (the
rail's "Tidewater Georgian · the guided example" when no style is in hand), WP-14.10 (the example
brief). The house half of the example waits: `oq/the-worked-house-has-no-plan-that-places`.

### 10. Machine language where names and draughtsman's notation belong — major

- **Courier has become the primary label face.** Of **405** `font`/`fontFamily` declarations in
  `.jsx` files, **223 set Courier** (the audit counted 203 of 382; the ratio, about 55%, holds
  under both methods). `tokens.css:96-101` charters Courier for "token names, hex values, counts
  and ids — the typewritten margin".
- **Ids where names are served**: the 57 pack ids; Kit rows; the masthead; Brief Intake's raw-id
  select; finding rows ending in room ids while the sheet letters room names; title blocks.
- **Numbers in machine form**: `8.5263 in`, `18 parts of 0.3333″`, unitless ranges, a rules table
  with no header row.
- **Build history in reader copy**: `(⑤ → ⑥)` (`PlanWorkbench.jsx:381`), `(⑦)`
  (`Transcription.jsx:520,565`), `CP-SAT solver landed (WP-2.3)` (`BriefIntake.jsx:315`), a panel
  narrating `WP-4.5` (`BriefIntake.jsx:271`), `DXF & IFC (WP-5.1)` (`ExportDetails.jsx:170`),
  `(OQ 29)` (`StyleRecord.jsx:197`), `(OQ 65 …)` (`Proportions.jsx:295`), and one sentence that
  narrates its own past bug, `until WP-11.1 …` (`PlanWorkbench.jsx:960`). **Correction**:
  `Chrome.jsx` rules WP numerals out of the rail only and deliberately keeps them on the Export
  cards, which `walk.mjs` asserts; widening the numeral check means overturning that on purpose.
- **The name-first pattern already exists twice** — StylePicker and the command palette — and
  is to be extracted, not reinvented.

**Who it hurts:** every practitioner, who works in names and in feet, inches and fractions;
newcomers, who read ticket numbers as an unfinished product.
**Answered by:** WP-14.6 (`fmt.js`, a port of `_fmt_in` held to it by a parity test; `names/`),
WP-14.8 (`RecordLink`; the copy ratchet at today's baseline), WP-14.9 (names-first pack list and
rules table with a header row).

### 11. Proof before answer — major

On Proportions the invariants come first and the conflicts last (§I item 5); on order packs at
ordinary widths the plate sits beside the invariants, and on the 32 packs with no plate nothing
does. The fault card omits `correct_practice`, `detection` and its sources and shows the test as a
monospace string in which nothing says the direction is the pass condition. The Plan Workbench can
stack up to six conditional panels above the plate and states the engine three times.

**Credit where due**: the revision panel's `<details>` with a count in its summary, per-browser fold
state in `state/layout.js`, and FilterGroup's "folding never hides an active filter" are the
precedents the fix reuses.

**Who it hurts:** practitioners digging for working figures and the right way; newcomers, who give
up before the answer.
**Answered by:** WP-14.9 (pack head → plate → conflicts → rules at your building → authorities →
used by → sources → "How this was checked", folded, counting unjudged), WP-14.11 (the fault card's
Right way and How to spot it first, the exception verdict from `for_this_style`).

### 12. The URL falls behind the screen — major

Picks that change which record is read go to local state and never reach the URL: the pack list
and authority rows (`Proportions.jsx:463,558`), Style Record descendants (`StyleRecord.jsx:226`),
Phylogeny descent (`Phylogeny.jsx:403`) and compare, Kit slot expansion (`KitSurface.jsx:237`),
the candidate column (`CandidateSet.jsx:232`), bench rooms and findings, and the Drawing Set's
sheet and face (`DrawingSet.jsx:100,119`). The grammar also has dead or colliding kinds:
`constraint:` and `asset:` route to surfaces that read nothing, `plan:` means a placed room while
`room:` means a room type, and there is no `term` kind.

**This is not a missing rule** — "push for a change of place, replace for a change of view" is
written down (`nav.js:58-59`) — **it is surfaces not following it.**

**Who it hurts:** anyone citing, sharing or pressing Back; the AI pane's citations.
**Answered by:** WP-14.9 (pack clicks, filter and at-values in the URL), WP-14.12 (kit slot and
dossier section in the URL), WP-14.5 (the address layer: sections, `term:`, `constraint:` to its
style's Constraints section, the legacy `#/kit` alias). Every other pick writing the URL is
tranche 2.

### 13. Faint type, uneven focus, no shared status — major

- **283 of 405 font declarations are 12.5px or smaller** and 9 are 15px (the audit: 283 of 382).
  Body text inherits 15px from `body`, so this is a count of declared labels, not of all text.
- `--ink-4` measures **2.26:1** on the paper and is chartered for "hairline: construction, grids,
  disabled" (`tokens.css:55`); **106 lines** in `.jsx` set a text colour with it (the audit: about
  107). `--ink-3` is **3.15:1** and is the Eyebrow's default tone (`Eyebrow.jsx:8,17`).
- **Status**: if `/api/health` rejects, `locked` stays null and `App` renders nothing — a permanent
  blank page (`App.jsx:74,162`). The Style Record's fetch error sets the same value as loading, so
  "reading the record…" stays up for ever and hides its own style picker (`StyleRecord.jsx:44-50`).
  There is no `role="status"` anywhere.
- **Width**: `#root` has `min-width: 1380px` (`tokens.css:455`) with the surface list (236px) and
  the assistant (344px) open by default (`layout.js:39-40`). At 1366px that is 14px of sideways
  scroll; at 1280px, 100px.
- **Credit where due**: the Splitter is a keyboard-operable `role="separator"`; many surfaces do
  state their own loading and failure; `prefers-reduced-motion` is honoured.

**Who it hurts:** Lucas on a laptop; anyone reading at projector distance or over forty;
keyboard, touch and screen-reader readers; a stranger given the URL during a slow boot.
**Answered by:** WP-14.8 (global `:focus-visible`, Eyebrow at `--ink-2`, front door and Glossary
reflow), WP-14.13 (boot Status with Retry; the assistant folded below about 1500px when nothing is
stored).

### 14. The AI assistant is unnamed — major

The right-hand pane is a language-model assistant that never says so. Its eyebrow reads
`the rail` (`AiRail.jsx:135`); folded it is a vertical `THE RAIL` spine (`App.jsx:186`); its
greeting (`RailHost.jsx:15-24`) states its rules in the first person and never says AI or
assistant. **Correction**: open, it is plainly something one types questions into — the greeting
begins "Ask the corpus" and the field's placeholder is "Ask the corpus…" — so the confusing case is
the folded spine. Each turn sends `{surface, plan, last_eval, candidate_count}`
(`RailHost.jsx:41-51`); the shell's `selection` never reaches it, so it cannot know which style,
pack or fault the reader is looking at. The tool count is stated two ways: `rail.py:114` says 27
and `workbench/server/tools.py:1` says 26; there are 27.

**Who it hurts:** newcomers, who do not know an AI is on the page; practitioners, who must describe
the page to it.
**Answered by:** WP-14.13 (pane head and folded spine read "Ask the corpus · AI assistant" from a
glossary record; `rail.py` and its context unchanged, as ruled). What it is sent waits:
`oq/the-assistant-is-blind-to-the-page`.

---

## VI. What already works, and is kept

The rebuild is a re-arrangement around things that are right. None of these is replaced:

- **The URL as citation grammar and the ⌘K palette** — every place is a link a human can open, and
  666 named things are one keystroke away. The grammar's three spellings stay three.
- **The loupe** (`PlateViewer`), which scales the whole plate so the wall handles keep working.
- **The label fitter** on both plan renderers.
- **`EdgeGlyph`**'s "carries the cascade / claims only" captions — corrected for the 42 edges it
  gets wrong, and worded from the glossary.
- **`StyleRecord`'s linked `distinguished_from` cards**, lifted into the dossier.
- **`Spotlight`**, the "searched" banner, which stays until tranche 2 gives those kinds pages.
- **`StylePicker`** and the palette's name-first rows, which become `RecordLink`.
- **The `ShortcutCard` key** — reachable today only by `?` or a typed palette query; it gets a
  visible **Keys ?** button in the masthead.
- **The plan sheet's furniture key and its ∗/△ caption.**
- **The map's precision legend** — the one full legend in the app, and the model for the plate key.
- **The three-state verdict discipline** — evaluated-and-failed, evaluated-and-passed,
  could-not-evaluate — which every new component carries and none collapses.

---

## VII. The chosen design — two spines and a library

### What it is

**One front door; two spines — a STYLE (read one style whole) and a HOUSE (write one house, brief
→ drawings); a LIBRARY of indexes; and a plaque on every page.**

The rail, fed by one pure `src/nav/navModel.js` that also feeds the crumbs, the front door's map,
the palette and the walk:

- **START** — the front door (`#/`).
- **STYLES** — Find a style (`#/style`, an outline tree tradition › family › style › variant); the
  style in hand by name, or "Tidewater Georgian · the guided example"; its dossier sections
  nested with live counts; the family tree and map (`#/phylogeny`).
- **A HOUSE** — 1 Brief · 2 Candidates · 3 Plan · 4 Drawings · 5 Export, on the unchanged paths,
  with metas from `journeyState`; "or trace a drawing" under step 3.
- **LIBRARY** — Proportions · Faults · Glossary.

The dossier's sections, in the corpus's own consulting order, with the ruled labels: **Identify ·
Filed under this · Lineage · Kit · Proportions · Plan types · Constraints · Faults · Evidence**. The
URL ids stay `members`, `plans` and `rules`; the labels are unambiguous because the obvious ones
collide with words one click away — a pack's moulding *members*, a pack's derived *rules*, and
journey step *3 Plan*. **None of the 97 slot ids collides with a section id**, measured.

### Why it was chosen

Both judges chose it independently.

| Proposal | Judge | Newcomer | Practitioner | Relations | Fidelity to rulings | Tranche-1 buildability |
|---|---|---|---|---|---|---|
| dossier-journey | Reader | 7.5 | 7.5 | 9 | 9 | 7 |
| dossier-journey | Engineer | 7.5 | 8.5 | 8.5 | 9 | 7.5 |
| practitioner-desk | Reader | 7.5 | 8.5 | 7.5 | 7.5 | 5.5 |
| practitioner-desk | Engineer | 8 | 8.5 | 8 | 7.5 | 6 |
| language-map | Reader | 5.5 | 6.5 | 7.5 | 6 | 4.5 |
| language-map | Engineer | 8 | 6.5 | 7.5 | 6 | 5 |

The reader's verdict: **"Clearest overall answer to the five questions, with the fewest new ideas
to learn"**, named in words a practitioner already uses. The engineer's: **the closest literal
reading of ruling 3**, with every grammar claim checked — the router-unit identity holds, section
names are a pinned vocabulary and not a regex, the regexes are untouched, and no MCP or `rail.py`
payload moves.

### Why language-map was not chosen

It made VISION's layers the navigation: six layer groups in the rail, a six-word locator on every
page, a front-door plate.

- **It broke the house journey it was meant to carry**: Faults, under CRITICISM, sat between step 3
  and step 4, so the numbered steps ran 1, 2, 3, Faults, 4, 5 across three groups — the audit's own
  finding 6 brought back.
- **Its layer names were not VISION's.** VISION names nine layers (`VISION.md:196-223`: alphabet,
  grammar, vocabulary, bindings, solecisms, phrase layer, critic, generator, interfaces);
  *Dialects*, *Composition*, *Criticism* and *Drawing* were coinages presented as the corpus's own,
  and its claim that the journey follows "VISION's own order" was false (the critic precedes the
  generator).
- **Lucas's page would have read "Grammar › Proportions"**, which an architect has to translate.
- **It slipped two policy changes into tranche 1** — corpus text on the ungated `/api/health` and
  an edit to `rail.py`'s system prompt — and carried the heaviest tranche.

**Grafted from it**: rendering only the dossier section in view; the copy ratchet; the boot Status
and the `lastEval` reset; the authorities count from the API; gating per-assembly dimensioning on
an empty stack rather than on kind; the front door and Glossary reflowing below 1380px; and
VISION's own layer words as editorial glossary records, grouped in the Glossary and kept out of the
rail and off every page.

### Why practitioner-desk was not chosen

It was the richest practitioner experience and scored highest on practitioner efficiency.

- **It added a second furniture metaphor for one house**: "On the desk" in the masthead beside the
  existing bench, and a desk style that could differ from the page's `for <style> ×` chip.
- **Its tour promised a house it could not show**: "Follow one house" had six stops, all on the
  style side, and the house half hatched "not built yet".
- **It offered "Start a brief from this parti"**, which the brief schema cannot carry: it is
  `additionalProperties: false` with no `parti` property, and `/api/compose` passes only the brief.
- **It changed a machine payload**: `glossary_terms` in `core.overview().counts`, which is the
  `tdl_overview` MCP payload, the assistant's system prompt and the ungated health response.
- **It mounted the JourneyBar inside six surface files that tests read by path**, and missed a
  count `check_counts.py` polices.
- **It carried the widest tranche**: thirteen packages including the tour, the banners, the keys,
  the fault rework and the face picker.

**Grafted from it**: the Styles index at a bare `#/style` (`styleTree.js` from `render_html.py`,
with a test that no row is orphaned); `module.equals: "ceiling_height"` on `trim-classical`,
restating its own `module.name` (*"The finished ceiling height of the room"*) and lie-checked in
`check_systems`; the fault card's Right way and How to spot it before the test; EdgeGlyph's weight
from `inherits_kit`; the one-time banner for a cold deep link; `PageHead` on every surface; the
no-invented-sources rule for glossary sources; summary cards on Identify; the JourneyBar's Next as a
link only when the step can proceed; a StylePicker in the dossier head; an interim slot panel at
`#/style/-/kit/<slot>` on the unused `/api/slots/{id}`; and `citeFor` normalising the default
section so it never mints a `style:x#identify` alias.

### The defects the judges found in the chosen design, and how the plan answers each

| Defect in dossier-journey as proposed | The plan's answer |
|---|---|
| On Lucas's own page the plate (module 114 in) and the rules (slider 108 in) describe two walls: 9″ against 8 1/2″ | `module.equals: "ceiling_height"` on `trim-classical`; the server takes the module from the ceiling when no module is given, so the slider moves both (WP-14.4); walk asserts `?ceiling=108` moves plate and baseboard row together (WP-14.9) |
| "Find a style" landed on the Phylogeny, 111 of 159 rows misparented | The Styles index as an outline tree at `#/style` (WP-14.12) |
| Kept the `five authorities` literal, false for composite | The heading counts the API's rows; the walk asserts the count against `/api/authorities` (WP-14.9) |
| A `slot:` citation landed on a bare chooser | The interim slot panel on `/api/slots/{id}` (WP-14.12) |
| Per-assembly dimensioning gated on `kind != order-system` missed `moorish-arch` | Gated on `not stack_for(pk) and pk.get('assemblies')` (WP-14.4) |
| `citeFor` could mint `style:x#identify` | Identify and an absent section normalise to `style:<id>`, asserted in router-unit (WP-14.5) |
| Laptop width deferred; screenshots only at 1380 and 1680 | Front door and Glossary reflow; the assistant starts folded below ~1500px; the walk shoots 1280, 1440 and 1680 (WP-14.8, 14.13, 14.15) |
| `PageHead` on four surfaces only | On every surface, from its `surface-*` record (WP-14.8, 14.13) |
| No package reports, no open-question files | Every package ends with its report; WP-14.0 files the deferred rulings as slug files (§IX) |
| Section labels collided with words one click away | Ruled labels (§II); ids unchanged |
| `Term` popovers use `role=dialog`, which the walk uses to find the palette | The palette is found by its aria-label; popovers close on navigation and palette open (WP-14.7, 14.8) |
| Embedding the Kit tempts removing `PANES.kit`, which `layout.test.mjs` pins | `PANES.kit` kept (WP-14.12) |
| The pack filter and at-values stay in React state, so a shared link cannot carry the ceiling | Through `useSurfaceFilters` with replace; the pack through `setSelection` with push (WP-14.9) |
| An editorial basis verified only by `check_basis`'s default could pass on a short or absent quote | `check_glossary` requires at least one verified verbatim quote of 25 characters or more per editorial record, and a mutation proves it (WP-14.1) |

---

## VIII. The tranche plan

### Sixteen packages in five waves

| WP | Package | Verified by |
|---|---|---|
| **Wave 0** | | |
| 14.0 | This analysis; the phase PRD's frozen contracts (glossary fields, payloads, term-id list, `DOSSIER_SECTIONS`, navModel ids, route and cite tables, journeyState vocabulary, prefs keys); `PLAN-OF-ACTION.md` Phase 14; the deferred rulings filed as slug files | `check_ids`, `gen_open_questions --check`, `check_counts`, `check_citations`; the baseline `check_all` reds recorded (§XI) |
| **Wave 1** — five parallel lanes | | |
| 14.1 | Glossary schema, `build/check_glossary.py`, `check_openings.check_basis(rec_re=)` with callers byte-identical, registration | Checker exits 0, or 3 without `jsonschema`; five basis-checkers' stdout unchanged; twelve mutations |
| 14.2 | The ~115 tranche-1 records, in four disjoint family batches | Checker green; a one-word basis mutation fails |
| 14.4 | Server: every drawable pack, module = ceiling, `used_by`, a style's packs, the dossier summary, example briefs | Order geometry byte-identical (`test_render_profile`, `check_orders`, the `render_profile` dry run); MCP `get_proportions` unchanged and asserted; all expectations computed |
| 14.3 | Serve the glossary; the `term` kind; section fragments; the one ungated sentence (after 14.4, same lane) | Server suite unchanged; `test_zz_auth_leak_guard` extended — signed out, `about-tdl` answers and every other term is 401; `overview()` has no glossary key |
| 14.5 | Addresses, additive: sections, glossary, constraint and term routes, context carry | Router-unit identity holds; a `style:x#identify` mutation fails |
| 14.6 | The pure half: `fmt.js`, `judgment.js`, `names/`, `glossary/lookup.js`, `placePopover.js`, `journey.js`, `taxa.js` + `styleTree.js`, `assemblyLayout.js` | `npm test` including `no_bare_imports` and `refusal`; a null→failed mutation fails |
| 14.7 | Walk prep: navigate by address, find the palette by name | The walk green on the unchanged app |
| **Wave 2** | | |
| 14.8 | Definitions on screen: `Term`, `PageHead`, `RecordLink`, prefs, the Glossary surface, Eyebrow, focus and reflow | `npm run build`; `check_frontend` (bundle ceiling; the glossary fetched, not bundled); the walk's definitions block |
| 14.9 | Proportions, plates first (parallel with 14.10 and 14.11) | Bands = served members; x ≥ 0; plate before proof; `?ceiling=108` moves plate and baseboard row together |
| 14.10 | The house journey | Every budget option in the schema enum; a refused plan → Drawings and Export blocked, not links |
| 14.11 | Two truths: what an edge carries; what a fault card answers | Restoring the old `CARRIES` table fails the lineage check |
| **Wave 3** | | |
| 14.12 | The Style Dossier, the Styles index, the slot panel, `#/kit` → alias | Member counts = API; a cold `#/kit/craftsman` canonicalises and survives refresh; a bare `#/style` never shows a record |
| 14.13 | The shell: navModel rail, crumbs, masthead, page titles, boot Status, cold-link banner, the named assistant, the narrow-screen fold | Crumbs = the `member_of` chain; titles differ per place; full screen hides crumbs, head and bar; the banner shows once; `layout.test.mjs` extended |
| 14.14 | The front door and the Gate (parallel with 14.13, merged after) | `about-tdl` rendered on both; no horizontal scroll at 1280px |
| **Wave 4** | | |
| 14.15 | Integration: the walk at 1280/1440/1680 with screenshots beside Lucas's, `docs/workbench.md` navigation rewritten, figures via `check_counts --fix`, the tranche report | The full verification: `npm test`, router-unit and search-unit, `check_frontend`, pytest with CAD and server libraries installed so nothing skips, `check_glossary`, `check_ids`, `check_counts`, `check_systems`, `check_orders`, `check_all` at 54 with no red absent from the baseline, `walk.sh` exit 0 (exit 3 is not a pass) |

### Lanes, order and ownership

Each lane is its own agent in its own git worktree. The merge order is 14.7 → 14.6 → 14.5 → 14.1 →
14.4 → 14.2 → 14.3, then 14.8 → {14.9, 14.10, 14.11} → 14.12 → 14.13 → 14.14 → 14.15. The work is
sequential only where files collide: 14.4 then 14.3 (one server agent); 14.1 before 14.2 merges
(14.2's four batches author against the contract in parallel); 14.8 before 14.9-14.11; 14.12
before 14.13; 14.13 before 14.14's merge. **Shared files have one owner each**: `App.jsx` (14.8
one line, 14.10 one hunk, 14.12 the surfaces map, 14.13 the rest), `api/client.js` append-only,
`walk.mjs` per-block after 14.7 and never the `engineClaim`-pinned lines, `tokens.css` 14.8 only.
Registering `check_glossary.py` moves `TOTAL_CHECKS` from **53 to 54**, and `CLAUDE.md` moves with
it in the same commit.

### The guards that move, and the property each is re-cut to

**A guard moves with its subject and is re-cut to the property it protects, never re-pinned to a
new string**, and each re-cut is proved able to fail.

| Guard today | Re-cut to | Package |
|---|---|---|
| The walk's rail block ("all twelve surfaces in the rail", a live style count) | Every navModel item renders under `nav[aria-label="surfaces"]` and reaches its href | 14.13 |
| The walk's "corpus describes itself" (`what_this_is` on the landing) | The front door renders the `about-tdl` record — the landing sentence is corpus-served, not app-written | 14.14 |
| Fourteen rail-label clicks in the walk | `visit(hash)`, with reachability asserted once in a loop | 14.7 |
| Kit, Style and Proportions text anchors, including `five authorities` | Counts equal their API figures | 14.9, 14.12 |
| `readPlate` clicking a button named by the pack id | Clicks `[data-cite]` and asserts `location.hash` | 14.9 |
| The `#/kit/craftsman` refresh | Canonicalises to the dossier's kit section and survives refresh | 14.12 |
| The palette found as `[role="dialog"]` | Found by its aria-label, because `Term` popovers are dialogs too | 14.7 |
| Router-unit's `constraint:` and `#/kit` shapes | The constraint lands on its style's Constraints section; kit paths under `#/style` plus a legacy parse | 14.5, 14.12 |
| Search-unit synonyms `kit` | Point to `style`, because a kit is read per style | 14.12 |
| `test_grammar_agreement.py` | Gains `DOSSIER_SECTIONS` agreement and an AssemblyPlate entry — "no plate derives arcs", not "these two files" | 14.3, 14.9 |
| `test_search_index`, `test_citations`, `test_compression_and_caching` | Cover the `term` kind and clear the glossary cache | 14.3 |
| `check_counts` search-index figure | Moves with `--fix`; two new rows police the unpoliced copies (§XI) | 14.3 |
| `test_counts_guard` | 53 → 54 | 14.1 |
| `test_zz_auth_leak_guard` | Extended for exactly the one ungated path | 14.3 |
| `layout.test.mjs` | Extended, not re-pinned: narrow and nothing stored → folded; stored open → open | 14.13 |

**Unchanged by design**: the refusal-contract checks, the `PANES` labels and `PANES.kit`, every
file a test reads by path, `Spotlight`, and the `?` card.

---

## IX. What waits, and why

### Refused out loud in tranche 1

- **No `4 + 12 + 3` dimension string** on the trim plate: the pack does not structure its zones; the
  invariant sentence stays in the proof fold.
- **No rotated casings**: every assembly is drawn upright from the wall plane and captioned so.
- **No picture for the five packs with no assemblies**; they say they give rules, not an assembly.
- **No drawing at the reader's building for a pack that does not declare its module a building
  input.**
- **No arc or sweep arithmetic in JavaScript, and no change to `OrderPlate`.**
- **No photographs or precedent images without files.**
- **No change to an MCP payload.**

### Tranche 2 and 3

Record pages for slot, room, massing, grouping and parti (retiring the "searched" banner); comparing
two styles (`#/compare/<a>/<b>/<section>`); the guided tour through the house half; the parti
bridge; keys for every mark and one duty per hatch; Faults read for one style, a gauge per fault
and a parti diagram per candidate; an Elements index; the Drawing Set and Export keeping sheet and
face in the URL; the assistant told what the reader is looking at, with starter questions; MCP
parity for proportions; plate declarations (casing orientation, zone divisions, wall-datum
thumbnails); the copy ratchet driven to zero; every pick writing the URL; the instrument surfaces
reflowing below 1380px. Tranche 3: an answer-first Plan Workbench, and the glossary beyond tranche
1.

### The questions filed by this package

Each is a new file in `docs/open-questions/`, named by slug; none is numbered.

| Question | What it blocks |
|---|---|
| `oq/a-brief-cannot-name-a-parti` | "Start a brief from this parti" on the dossier. The brief schema is closed and has no `parti`; the compose route passes only the brief. Until it is ruled, native partis are listed as information only. |
| `oq/the-assistant-is-blind-to-the-page` | Telling the assistant what the reader has selected, and offering starter questions. Its name is ruled and ships; what it is sent changes `rail.py`, which tranche 1 keeps byte-stable. |
| `oq/casings-are-measured-across-and-drawn-upright` | Turning the casings on the plate and dimensioning the wall as 4 + 12 + 3. Today both live only in member notes and an invariant sentence. |
| `oq/one-duty-per-hatch` | Any product-wide key. `--hatch-unjudged` carries at least four meanings and the new plate needs a hatched "wall, drawn nominal". |
| `oq/mcp-proportions-serve-no-assemblies-for-non-order-packs` | MCP parity: `tdl_get_proportions` still returns zero assemblies for `trim-classical`, and changing that changes a machine payload. |
| `oq/the-worked-house-has-no-plan-that-places` | The house half of the guided example. Both shipped plans are refused at placement (§X). |
| `oq/which-packs-module-is-a-building-input` | Extending `module.equals` beyond `trim-classical` — `opening-proportion`'s module is the principal door leaf, and there may be others. |

---

## X. The docs call the worked house clean and it is not

`README.md:51` says of the plan validator: *"Two worked examples ship with it: a deliberately
ordinary production Colonial (4 fatal) and the same corpus applied carefully (0 fatal)."*
`STATE-OF-THE-PROJECT.md:62` says *"Two worked examples ship — a deliberately ordinary production
Colonial and the same corpus applied carefully"*; it states no count, and it presents the second
as the corpus applied carefully. **The count is `README.md`'s alone; the claim that it is the
worked example is both files'.**

Measured on `d565dea`, 24 Sep 2026:

| Record | As written — `python3 build/plan_check.py <plan>` | Placed on the search, `engine="heuristic"` (deterministic), then `plan_check.check` |
|---|---|---|
| `plans/tidewater-georgian-careful.json` | **fatal 3 · serious 30 · minor 76 · info 29** | fatal 13 · serious 65 · minor 102 · info 28 — **refused** for `bearing`, `hearth`, `stacks` |
| `plans/spec-builder-colonial.json` | fatal 5 · serious 60 · minor 80 · advisory 1 · info 25 | fatal 15 · serious 100 · minor 97 · advisory 1 · info 26 — **refused** for `bearing`, `stacks` |

**The careful plan's three as-written fatals are all elevation faults**: *The Front With No Centre*
(`even-bay-front`, 0 against equals 1), *The Bay That Broke the Symmetry*
(`one-bay-symmetry-break`, 3 against at-most 0) and *Windows That Do Not Stand On Each Other*
(`storeys-out-of-vertical-alignment`, 90.0 against at-most 2.0). On an unplaced record
`plan_check` derives its elevation from a fresh heuristic placement and says so
(`plan_check.py:2592-2594`), so even "as written" is a statement about one placement. **The
production Colonial is 5 fatal as written, not 4.**

**Why it matters to the interface and not only to the docs**: the guided example is this house.
Loading it on the bench runs a solve and two corrective rounds (the explicit-solve ruling recorded
in `docs/reports/wp-13.9-the-first-pass-was-the-product.md`), and WP-13.4's refuse-to-draw
contract then refuses the sheet — measured above on the search, and recorded by the browser walk
as refused on `auto` for both shipped plans (`walk.mjs:100`). A newcomer following the example to
its plan meets a refusal, where a reader of `README.md` has been told to expect a clean one. The
front door therefore labels Tidewater Georgian the guided example **for the style and the brief**,
and the house half waits on `oq/the-worked-house-has-no-plan-that-places`.

**Adjacent staleness the same paragraph carries**: `README.md:45` says the fault corpus holds 209
named errors; `faults/` holds 210. `check_counts.py` polices neither figure.

**Not corrected here.** This package writes one file. The correction belongs to the documents'
owners, and the plan records it for WP-14.15's `check_counts --fix` pass and doc rewrite.

---

## XI. Measurement appendix — measured at `d565dea` on 24 Sep 2026

Every figure published above, with the command or file it was measured by. Where the audit's figure
differs, both are given; the report publishes the left-hand column.

| Figure | Measured | Audit's figure | How |
|---|---|---|---|
| Proportion packs, by kind | 57: 26 order, 13 module, 8 facade, 4 opening, 4 trim, 2 room | 57 | `proportion_engine.PACKS` |
| Packs drawn as a plate today | **25** (every order pack but `moorish-arch`) | "the 26 order packs" | `corpus.proportions_with_members` + the `hasPlate` predicate of `Proportions.jsx:410` |
| Packs served no member | **32 of 57** | 31 | same |
| Packs with assemblies and an empty stack | 27 (26 non-order + `moorish-arch`); 50 assemblies; 237 members | 27 / 50 / 237 (synthesis); 26 / 47 / 231 (judges, `moorish-arch` excluded) | `pe.dimension(pk, None, [aid])` per assembly |
| Packs with no assemblies | 5: `opening-proportion`, `room-harmonic`, `room-vernacular`, `storey-graduation`, `timber-bay` | 5 | same |
| `trim-classical`, `dimension(pk, None, None)` | 0 assemblies | 0 | same |
| `trim-classical`, per assembly | 20, 21, 12, 7, 7, 4 = 71 | same | same |
| `trim-classical` geometry | `lower_diameter_in` 228; `lower_radius_in` 114.0; the Georgian wall section's naked at 114.0 | 114 | `profiles.pack_geometry` |
| Baseboard, `ceiling_height * 1.5 / 19` | 8.5263 in at 108 → `8 1/2"`; 9.0 in at 114 → `9"` | 8.53 / 9 | `proportion_engine._fmt_in` |
| `trim-classical` invariants · rules · conflicts | 10 · 18 · 6; the first conflict `blocking`, against cost | 10 · 18 | `corpus.proportions_with_members` |
| Invariants, corpus-wide | 313; 313 hold, 0 fail, 0 null | 313 | `core.get_proportions` over all packs |
| `trim-classical`'s users | bound by 36; opted into by 6 (`inherits_packs`); `applies_to` names 42; 13 named and not binding; 7 binding and not named | 36 / 42 | `styles/*.json` |
| Tidewater Georgian's packs | binds `brick-course`, `storey-graduation`, `timber-bay`, `sash-light`; `inherits_packs` `facade-classical`, `gibbs-ionic`, `opening-proportion`, `trim-classical` | binds the four | `styles/tidewater-georgian.json` |
| `gibbs-doric` in the pack list | 43rd of 57 | 43rd | `corpus.pack_list()` order |
| Default fault's row | 100 of 210 | 100 of 210 | `core.find_faults(limit=250)` |
| Phylogeny rows under a non-parent | 111 of 159; Tidewater at index 72 (the 73rd row) | same | the sort of `Phylogeny.jsx:87-92` reproduced over `corpus.phylogeny()` |
| Taxa by rank | 5 tradition · 27 family · 90 style · 42 variant = 164 | same | `core.overview()` |
| Family and tradition records with no lineage and no descendants | 32 of 32 | 32 | `core.get_style` |
| Search index | 666: style 164, slot 97, fault 210, pack 57, room 60, massing 40, grouping 17, parti 21; 138 banner-only | 666 / 138 | `corpus.search_index()` |
| Stale copies of that count | 665 at `workbench/README.md:18`, `docs/workbench.md:178`, `Spotlight.jsx:3` | 665 vs 666 | grep |
| Citation kinds routed · indexed | 15 · 8 | 8 of 15 | `citations.js:33-51` |
| Slots · slot ids colliding with a section id | 97 · 0 | 97 · 0 | `elements/slots.json` |
| `title=` attributes and props in `.jsx` | **58** | about 57 | grep for `title={` and `title="` over `workbench/app/src/**/*.jsx` |
| SVG `<title>` in `.jsx` | 9 | 9 | grep |
| `aria-describedby`, `role="tooltip"`, `aria-live`, `role="status"` | 0; one `role="alert"` (`Gate.jsx:80`) | 0 | grep |
| `font`/`fontFamily` declarations in `.jsx` | **405**; 283 at ≤12.5px; **223** Courier; 9 at 15px | 382; 283; 203; 9 | a parse of each declaration against the size and family tokens of `tokens.css:100-139` |
| Lines setting a text colour in `--ink-4` | **106** | about 107 | `grep -rnE 'color:\s*[^,}]*--ink-4' --include=*.jsx` |
| Contrast on `--paper` | ink 9.48 · ink-2 4.85 · ink-3 3.15 · ink-4 2.26 · salmon-deep 2.71 · gilt-deep 4.09 | same | WCAG 2 relative luminance |
| Pass against fail square | 1.08:1 (`--green-deep` against `--brick`) | 1.08:1 | same |
| Lineage edges with `inherits_kit: true` | descends_from 202 of 202 · regional_of 42 of 42 · **hybridizes_with 42 of 57** | 42 | `styles/*.json` |
| Authorities per order | tuscan, doric, ionic, corinthian 5 · composite **4** | 4 | `core.compare_authorities` |
| Budget options the schema accepts | 1 of 4 (`custom`) | 3 of 4 refused | each option driven through `jsonschema` on `briefs/family-georgian.json` |
| Generated profile plates | 73 SVGs, all order packs; 0 depict a fault | 73 | `assets/generated/`, `assets/manifest.json` |
| Image records | 1,850: 1,777 wanted, 73 sourced | same | `assets/manifest.json` |
| Fault records carrying `correct_practice` and `detection` · references in `app/src` | 210 of 210 · 0 | same | `faults/*.json`; grep |
| `/api/slots/cornice` | 35 specifying styles · 9 faults | same | `core.get_slot` |
| Faults that apply to Tidewater Georgian | 206 of 210 | 206 | `core.find_faults(style=...)` |
| `tdl_*` tools | 27; `workbench/server/tools.py:1` says 26 | same | `mcp_server/server.py` |
| Checks | 50 in the loop + 3 appended = `TOTAL_CHECKS` 53 | 53 | `check_all.CHECKS`, `check_all.TOTAL_CHECKS` |
| Open-question register | 212 entries (213 files including the README) | 213 files | `docs/open-questions/` |
| Rail entries · Overview doors | 12 in five groups · 11 in three | "eleven" (this report's brief) · 11 | `Chrome.jsx:33-56`; `Overview.jsx:24-54` |
| Worked plans | §X | 3 fatal, 30 serious | `build/plan_check.py`; `geometry.solve(..., engine="heuristic")` |

### The unchanged tree's build

The full `build/check_all.py` on the unchanged tree was still running, in an isolated worktree, when this report was committed. Its result is recorded in a follow-up amendment to this section before any Wave 1 package merges, so that every later package can be held to "no red absent from the baseline". The browser walk on the unchanged tree WAS measured: `workbench/scripts/walk.sh` returned **215 ok, 0 FAIL, 4 COULD NOT EVALUATE, exit 3** (the four: good-03's fallback line, its gable-end stacks, its entrance stoop, and the Drawing Set caption gated on `date_of_representation`), which is the state `CLAUDE.md` records for WP-13.9.
