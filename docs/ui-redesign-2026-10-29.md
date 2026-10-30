# The Workbench, redrawn — design handoff (29 Oct 2026)

Canvas: **TDL Workbench UI** in Claude Design (15 artboards, 1440 wide, five rows).
Companion to `Design System/UISPEC.md` (24 Aug) — this note records the decisions the
canvas embodies, so the app can be changed to match without re-deriving them.

## What was wrong with the Front Door (and the shell)

Lucas's words: *extraordinarily bland, dense and impossible to intuitively navigate.* Read off the
screenshot of 29 Oct:

1. **One register.** Chrome and content shared the same vellum and the same Garamond at nearly one
   size. Nothing had figure/ground; the drawings — the product's one beautiful asset — were absent
   from the landing page. The Front Door was a text page *about* a drawing instrument.
2. **The navigation appeared three times**: sidebar, two cards, and an index list repeated below
   the fold.
3. **State strings in the nav** (`stated`, `needs a plan`, `no plan on the bench`) set in mono
   read as error output, not as progress.
4. **The AI rail spent a fifth of the width describing itself** with no conversation in it.
5. **Three persona paragraphs** were marketing copy on an instrument; the reader is one of them
   and had nowhere to go first.

## Rulings taken (AskUserQuestion, 29 Oct)

- Scope: every surface.
- Register: **dark instrument, vellum plates** — the UISPEC §10 proposal, which the build had not
  taken. The chrome is coal/heavy/ink; drawings, cards and columns sit on vellum and are the
  brightest objects on screen.
- Front Door spine: **the journey, drawn** — Brief → Candidates → Plan → Drawings → Export as five
  stations, with a real plate as the hero.
- Tokens: the repo's own `tokens.css` (Drawn Language), not Hearthstead. Type unchanged:
  EB Garamond + Courier Prime.
- Shell holds; carry it to every surface. The AI rail opens **only when summoned** (52 px strip).
- Round 3 led with the Style Dossier + Kit, which set the cross-cutting components.

## The system

**Grounds.** Sidebar, top bar and rail `--coal #221F1A`; main ground `--heavy #2E2A23`; panels
`#262219` (a half-step, to be named in tokens.css — proposed `--heavy-2`); inset fields `#1A1714`
(proposed `--coal-deep`). Vellum `--paper #F1EBDB` for every plate, card and column; `--paper-lit`
for a focused field. Hairline rules on dark: `rgba(241,235,219,.12)`; borders `.22`.

**Ink on dark.** Primary `--paper`; secondary `--ink-4 #A69D89` (6.3:1 on coal — passes at 11 px);
the one struck highlight `--gilt #AF8D49` for the active station, the active library row, links,
and nothing else. Never `--ink-3` for text on dark (fails contrast).

**Marks.** Severity is a ladder of inks, never a traffic light: fatal `--brick #AF6B50`, serious
`--salmon-deep #C08066`, minor `--gilt`, advisory/info graphite outline; cleared `--green-deep
#6B7C5C`. **Unjudged is a form, not a colour**: an open ring hatched at 45° in `--ink-4`, the same
size as pass and fail, used on findings, constraints, candidate standing, sheet banners, score
axes, brief feasibility, and the transcription record. Refused is a brick band with a sentence.

**Journey marks (sidebar + Front Door tiles).** Done = filled vellum disc / vellum tile. Current =
gilt ring with a gilt dot / dark tile with a gilt border. Not yet = dashed graphite ring / dashed
outline tile. Status text is italic serif prose, never mono.

**Source chips** (every number): measured (pale green), editorial (pale sepia), derived (pale
green-grey), invented (brick, conspicuous), code (ink). **Variant ladder**: canonical (green-deep
fill), permitted (green fill), atypical (outline), forbidden (brick fill). **Binding chips**:
specified (vellum fill), extends (vellum outline), forbidden (brick fill), open (nothing).

**Type.** Eyebrows 10.5 px / 600 / .24 em caps in `--ink-4`, gilt when they name the page's
subject. Display 46–62 px Garamond 400. Body 15 / 1.55; prose paragraphs 16.5–17 / 1.55 where the
corpus's own sentences are shown (symptoms, tells, trades-away, household). Mono for every id,
count, dimension and URL. Dimensions always feet-and-inches.

**Plates.** Vellum, 10 px mat, double border (1.5 px heavy + 0.5 px hair), a drop shadow only to
lift the plate off the dark ground. Captions in mono caps below, the loupe (fit · 1:1 · ±) in the
plate's own header. Overlays on plates are construction weight (`--hair`, dashed).

## The shell

- **Sidebar (236 px)**: wordmark · *The house on the bench* (name, one mono line, the five-station
  spine) · *The library* (five rows with mono counts; sub-rows only under the open section) ·
  search + keys pinned at the foot. On library surfaces the spine collapses to five dots.
- **Top bar (48 px)**: crumbs as eyebrow, the URL grammar in mono, one *Ask the corpus* button.
- **Rail**: a 52 px strip with a vertical label; opens to ~320 px on ask. No self-description.
- Every artboard is a PAGE (fluid, `flex-wrap`), so the sidebar stacks at phone width.

## Surface by surface (what each board decides)

1. **Front Door** — thesis as the headline; one primary action (continue the house) and one
   secondary (new brief); the engine's own Tidewater plan sheet as the hero plate; the five
   stations as a strip with a rule through them; the library as five cards with a drawn glyph and
   a count; the closing statement as furniture with the corpus counts.
2. **Candidate Set** — four vellum columns. Score (`66.3 of 100 · 94 of 100 weight judged`) and
   nativeness are separate marks; the eight axes listed in mono; `trades away` always visible;
   the refused native diagram ranks last with a brick band and *disqualified* beside its score;
   the unplaced candidate wears the unjudged ring (*may be refused*). Decision log as a receipt.
3. **Plan Workbench** — plate fills the bench; findings pinned where they fall; relaxations as gilt
   diamonds with the running count printed on the drawing; findings grouped by layer with a
   severity threshold (density first); one card open (statement · why · fix · *assert
   not-visible-from*); *Judge this plan as [style]* in the toolbar as a feature; *Re-solve · 250 ·
   hill-climb* and *Prove placement · CP-SAT* side by side; "searched, not proved" under the plate.
4. **Brief** — the household as a real paragraph; the site as a drawn diagram with a compass
   control that accepts diagonals; live feasibility with three-state marks; the silences counted
   before composing.
5. **Drawing Set** — sheet tabs, the one-building banner with the placement digest, an overlay
   toggle for the governing pack's datums, and a disclosures panel: `83 of 177` evaluated,
   refusals with their reasons, judgments labelled editorial, and the composition/placement
   disagreement stated rather than resolved.
6. **Details & Export** — ships today (record, five sheets, DXF, IFC, brief + report) on vellum;
   named-not-built (guidelines, details library, PDF set) as dashed cards with WP numbers; a
   modelling-conventions plate (clear vs structural dimensions).
7. **Style Dossier** — plaque, drawn period bar (origin/floruit/decline/revival), nine-section
   rail with four open by default; tells and `distinguished_from` before the description; massing
   affinities as a ladder; constraints in three states with the judgment row offering to put the
   question to the human; exemplars with verified/unverified; unsourced images as a stated object.
8. **Kit** — the cascade as a first-class column (29 levels, bars for bindings, bans credited to
   their writer); slot rows with binding, source · distance, variants and parameters with source
   chips; one row expanded with rule, parameters, variant ladder, provenance trace, governing
   packs and faults filed; `forbidden` rendered as knowledge; `invented` conspicuous.
9. **Fault Corpus** — index by element with severity dots; the fault typeset as its name, with
   akas; two severity axes (reads / lives); **the style's exception above the general rule**;
   symptom at reading size; cause with driver and cost_saved; three fixes named right / cheap /
   dishonest with the cheap one struck in gilt; the test beside the statement; the image pair as
   a specified, unsourced record.
10. **Phylogeny** — broken time axis (2,300 years in 240 px, 426 in 760); five tradition lanes in
    the tradition hues; cascade-carrying edges heavy and solid, claimed ancestry dashed hair;
    `member_of` as a dotted drawer; the documented chronology exception flagged as such; an
    honest empty lane for the missing peer trunks; selected-node card with typed edges.
11. **Proportions** — material modules listed before the orders; the order drawn live with member
    labels and dimension strings; authorities compared at a common column diameter; invariants
    proved against the data (the false Vignola pedestal rule); a pack-conflict card with ranked
    honest and dishonest substitutions.
12. **Elements** — the eight groups as tabs; one slot with its authoring note first; who binds it
    across 164 styles as a bar (specified / extends / forbidden / open); faults filed; governing
    pack; the value on the bench.
13. **Compare** — the record's own discriminators as rows, each measurable; same rows folded;
    where the two part in the graph.
14. **Glossary** — the term, its basis quoted and build-verified, how it is drawn, where it
    appears, and its neighbours.
15. **Transcription** — the pinned drawing faint under the tracing; every wall drawn by the user;
    the record forming at the right with unjudged marks for what is unstated and *traced* /
    *name it* chips on rooms; "what the critic will not see yet".

## Honesty notes on the mockups

- Candidate 1's figures are the real ones from `docs/compose.md`. Candidates 2–4 use real partis
  and real trades-away text where the corpus has it, with illustrative scores (the composer took
  more than three minutes in the design sandbox).
- The plan plates are `FIGURED.png` (the bench's own render) as an image; in the app they are the
  live SVG. The elevation and the Doric order on the canvas are hand-drawn schematics in the
  language, not engine output.
- Counts follow the live app (164 · 97 · 57 · 210 · 252 · 27 tools) where the sidebar shows them
  and the spec elsewhere (95 slots, 660/295, 209 faults).

## Implementation notes (for Claude Code)

- Add the two dark half-steps to `tokens.css` under names with a duty, per the extension protocol
  (`--heavy-2` panels, `--coal-deep` inset fields), and a `--rule-on-dark` alpha token. Everything
  else on the canvas is an existing token.
- `nav/navModel.js` keeps its ids; the sidebar renderer changes shape (house-on-the-bench block,
  then library), the status words move from mono to italic prose through glossary records.
- The journey spine replaces `JourneyBar` in the sidebar; the Front Door's five tiles read the same
  `journeyState`. OQ *the journey bar's Next jumps rows when the strip wraps* goes away with it.
- The rail becomes a collapsible aside, closed by default on every surface, opened by the one
  button; its self-description is deleted and its first line is the prompt.
- The unjudged mark is one SVG symbol (hatched ring) used everywhere; add it to the `--mark-*`
  key with a glossary record.
- The Candidate Set column adapter already carries standing (refused / placed / unjudged); the
  column design maps those three to the brick band, the green dot and the hatched ring.
- Fault page: render `exceptions[style in view]` above `rule_violated` when the URL carries a
  style; the cheap fix card takes the gilt rule.
