/* THE APP WRITES FEWER EXPLANATIONS AND FEWER COUNTS, NEVER MORE (WP-14.8, PRD §J.4).

   Ruled 24 Sep 2026: every definition the workbench shows is a glossary record, and figures come
   from the API or the payload in hand. Two kinds of app-written copy break that and both already
   exist in the tree, so neither can simply be forbidden — they are RATCHETED, BY IDENTITY:

     EXPLANATIONS  a `title=` whose string literals carry EIGHT or more words. A tooltip that
                   long is explaining something, and an explanation belongs in a glossary record
                   a checker reads rather than in a JSX attribute nothing does. Eight is where
                   the shipped tree's labels end and its explanations begin, measured: the
                   longest title naming an act ("Give the atlas the whole window") is seven
                   words, and the shortest explanation is eight.
     COUNTS        a number, or a number word up to twenty, followed by a plural noun, in a
                   `.jsx` file's live source — `9 sections`, `209 faults`, `five authorities`
                   (the PRD's own list). A count typed into the page is true on the day it is
                   typed and silently false after, which is how the Kit's header said 95 slots
                   against an ontology holding 97.

   BY IDENTITY, NOT BY COUNT, so one change cannot net out another: removing an old explanation
   and adding a new one in the same commit leaves a total unchanged and is still a new
   explanation. Every current row must be in the baseline (a new one fails, naming itself), and
   every baseline row must still exist (a removed one fails too, asking for the baseline line to
   be deleted) — so the baseline can only shrink, and it shrinks in the commit that earns it.
   A row is (file, the literal text), so a moved line is not a new row and an edited one is.

   `COPY_RATCHET_PRINT=1 node --test src/copy_ratchet.test.mjs` prints the current rows as the
   baseline's JSON, for the commit that removes one. Adding a row to the baseline to make a new
   explanation pass is the move this file exists to refuse; the glossary is where it goes.

   THE BASELINE IS EMPTY (WP-14.31), SO THE RATCHET IS A BAN NOW. Its last fourteen titles became
   glossary records read through `describeTerm`/`useTermDescription`, and its six counts were
   either read from the payload in hand ("100 points" is the score's own two halves, "eight axes"
   the result's `score_model`) or went with the sentence that carried them.
   AND THE SCANNERS WERE WIDENED FIRST, BECAUSE AN EMPTY LIST FROM A BLIND READER IS NOT EMPTY.
   Measured on the tree before this package, the old readers missed a tooltip written as a
   `title:` property (the compiled components pass props as an object -- FindingRow's two), a
   count with an irregular plural ("filter 164 taxa"), one with adjectives between the number and
   its noun ("all 262 recorded pack conflicts", "660 style constraints"), and one written as a
   share ("86 of them", "295 of 660"). Each form is a fixture below, and a word that merely ends
   in s ("1 is", "100 and higher is") is not a plural.

   A THIRD SCANNER, PROSE, IS A RATCHET AND NOT A BAN (WP-14.33). Paragraphs the app writes are
   mostly its own voice and stay, so their baseline is not empty: it holds each one BY IDENTITY with
   a class, and a new one fails until it is either classed or -- where it states a corpus fact --
   derived or recorded instead. Its own header is below, beside the reader. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { read, stripComments } from './sourceReader.mjs';

const SRC = fileURLToPath(new URL('./', import.meta.url));
const TITLE_WORDS = 8;

/* Comments are stripped, and PROSE and STRINGS read, by `sourceReader.mjs`, the lexer both copy
   ratchets share (WP-14.33's audit); its header says what the regular expressions it replaced
   could not see. */

/* The `{ ... }` expression starting at `i`, braces balanced and strings skipped. */
function balanced(src, i) {
  let depth = 0;
  for (let j = i; j < src.length; j += 1) {
    const c = src[j];
    if (c === "'" || c === '"' || c === '`') {
      let k = j + 1;
      while (k < src.length && src[k] !== c) { if (src[k] === '\\') k += 1; k += 1; }
      j = k;
      continue;
    }
    if (c === '{') depth += 1;
    else if (c === '}') { depth -= 1; if (depth === 0) return src.slice(i, j + 1); }
  }
  return src.slice(i);
}

function literals(expr) {
  const out = [];
  for (const m of expr.matchAll(/'((?:\\.|[^'\\\n])*)'|"((?:\\.|[^"\\\n])*)"|`((?:\\.|[^`\\])*)`/g)) {
    out.push(m[1] ?? m[2] ?? (m[3] || '').replace(/\$\{[^}]*\}/g, ' '));
  }
  return out;
}

const letterWords = (s) => s.split(/\s+/).filter((w) => /[A-Za-z]/.test(w)).length;
const squash = (s) => s.replace(/\s+/g, ' ').trim();

/* The value of an object property starting at `i`: up to the first comma, `}` or `)` at its own
   depth, strings skipped -- `title: on ? 'a' : 'b',` is the whole conditional. */
function valueEnd(src, i) {
  let depth = 0;
  for (let j = i; j < src.length; j += 1) {
    const c = src[j];
    if (c === "'" || c === '"' || c === '`') {
      let k = j + 1;
      while (k < src.length && src[k] !== c) { if (src[k] === '\\') k += 1; k += 1; }
      j = k;
      continue;
    }
    if (c === '(' || c === '[' || c === '{') depth += 1;
    else if (c === ')' || c === ']' || c === '}') { if (depth === 0) return src.slice(i, j); depth -= 1; }
    else if (c === ',' && depth === 0) return src.slice(i, j);
  }
  return src.slice(i);
}

/* source → the title rows: [text] for every tooltip whose literals total `min` words or more --
   a JSX `title=` attribute, or a `title:` property (a compiled component passes its props as an
   object, which is how FindingRow's two explanations were invisible to this reader). */
function titleRows(source, min = TITLE_WORDS) {
  const src = stripComments(source);
  const rows = [];
  for (const m of src.matchAll(/\btitle(=|:\s*)/g)) {
    const at = m.index + m[0].length;
    let lits = [];
    if (m[1] === '=') {
      if (src[at] === '"' || src[at] === "'") lits = [src.slice(at + 1, src.indexOf(src[at], at + 1))];
      else if (src[at] === '{') lits = literals(balanced(src, at));
    } else {
      lits = literals(valueEnd(src, at));
    }
    if (lits.reduce((n, l) => n + letterWords(l), 0) >= min) rows.push(squash(lits.join(' | ')));
  }
  return rows;
}

const NUMBER_WORDS = 'two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen'
  + '|fifteen|sixteen|seventeen|eighteen|nineteen|twenty';
const N = String.raw`(?<![\w.$#\-/])(?:\d+|${NUMBER_WORDS})`;
/* A word ending in s that is not a plural: a count is never followed by one of these. */
const NOT_PLURAL = String.raw`(?!(?:is|was|has|this|its|as|us|thus|yes|his|less|always|plus|across|perhaps|whereas|unless|does|goes)\b)`;
/* The words that join a phrase and never qualify a noun, so "100 and higher is" is not a count. */
const JOIN = String.raw`(?!(?:and|or|of|the|a|an|to|in|on|at|by|for|is|are|was|be|than|then|if|as|so|but|with|from|that|this|it)\b)`;
const PLURAL = String.raw`${NOT_PLURAL}[a-z][a-z-]*s\b`;
const COUNT_FORMS = [
  new RegExp(String.raw`${N}\s+${PLURAL}`, 'gi'),                               // 9 sections
  new RegExp(String.raw`${N}\s+(?:taxa|criteria|data|people|feet|inches|men|women|children)\b`, 'gi'),
  new RegExp(String.raw`${N}(?:\s+${JOIN}[a-z][a-z-]*){1,2}\s+${PLURAL}`, 'gi'), // 262 recorded pack conflicts
  new RegExp(String.raw`${N}\s+of\s+(?:\d+|them|these|those|${NUMBER_WORDS})\b`, 'gi'), // 86 of them
  // `all 8`: a whole-set count with its noun left to the label beside it -- the Kit's slot-group
  // filter summary typed the eight its own `groups.length` held (WP-14.33's audit). Only where no
  // word follows: `all 262 recorded pack conflicts` is the form above's, and `all 12 px` a size.
  new RegExp(String.raw`\ball\s+${N}\b(?!\s*[A-Za-z%])`, 'gi'),
];

/* source → the count rows: [phrase] for every count in the live source, in source order, one row
   per place (the first form to match a place names it). */
function countRows(source) {
  const src = stripComments(source);
  const at = new Map();
  for (const re of COUNT_FORMS) {
    for (const m of src.matchAll(re)) if (!at.has(m.index)) at.set(m.index, squash(m[0]));
  }
  return [...at.entries()].sort((a, b) => a[0] - b[0]).map(([, t]) => t);
}

/* PROSE (WP-14.33, ruled 26 Sep 2026). A JSX paragraph of TWELVE or more words is one the app
   wrote, and a paragraph stating a CORPUS FACT -- what the corpus holds or lacks, a count, a value
   a record carries -- is derived from the payload in hand or recorded in the glossary, never typed;
   a sentence about how the workbench or its generators behave is the workbench's own voice and
   stays. The Phylogeny's "Japanese, Islamic, South Asian and African traditions are absent" was
   the case: true on the day it was typed, read by no check, and silent the day a peer trunk arrives.

   A PARAGRAPH IS AN ELEMENT'S TEXT, READ OFF THE ELEMENT TREE: its text runs, `{…}` for each
   expression, and the text of every inline child (`<em>`, `<Term>`, a link) joined into one, with a
   block child (`<p>`, `<div>`, a list) ending it. The first reader was a regular expression over
   runs between a `>` and the next `<` or `{`, and WP-14.33's audit walked three things past it:
   text after a `}` that closes an expression holding JSX (`{on && (<b/>)} and twelve more words`),
   a paragraph split by inline tags into runs under twelve words each (the removed sentence with
   `<em>absent</em>` in it passed), and a paragraph held in a string -- which is STRINGS, below.

   Twelve words is the threshold the open question was measured at, and it is not a clean gap: the
   seven-to-eleven band held thirty-seven runs on the tree this was written on, nearly all status and
   error lines ("the style list could not be read"), read by hand and holding no corpus fact -- a
   reading of that tree, not something this scanner will go on saying.

   The baseline carries a CLASS on every row -- `voice` (how the workbench or its generators
   behave), `disclosure` (a statement about the payload in hand, its figures read from it) or
   `not-prose` (a reader false positive) -- and there is NO `corpus` class, so a new corpus fact
   fails, naming itself, until it is derived or recorded. The class is a CLAIM a reviewer reads: no
   reader can tell a corpus fact from the workbench's voice, and baselining one as `voice` to get it
   past is a false line in a file whose every other line is checked. */
const PROSE_WORDS = 12;

function proseRows(source, min = PROSE_WORDS) {
  return read(source).paras.map(squash).filter((t) => letterWords(t) >= min);
}

/* STRINGS (WP-14.33's audit). A sentence the app shows need not be JSX text: it can be a string
   constant (`DrawingSet.jsx`'s captions), a prop, a `.js` module's message (`overlayRules.js`
   said "no room in the corpus carries it"), a `{'literal'}` child, an attribute value, or an
   argument to `React.createElement` in one of the compiled components, whose text no JSX reader
   sees. Every string literal of twelve or more natural-language words, a `+` chain joined into one
   with `{…}` for each operand, in every non-test module under src/. Natural-language words, so a
   path or a class list is not a sentence. The same classes, and the same rule. */
const WORD = /^[("'“‘]?[A-Za-z][A-Za-z'’-]*[)"'”’.,;:!?—]*$/;
const naturalWords = (s) => s.split(/\s+/).filter((w) => WORD.test(w)).length;

function stringRows(source, min = PROSE_WORDS) {
  return read(source).literals.map(squash).filter((t) => naturalWords(t) >= min);
}

function jsxFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) jsxFiles(p, out);
    else if (f.endsWith('.jsx')) out.push(p);
  }
  return out;
}

/* Every non-test module under src/, for STRINGS: a `.js` module's message reaches a page too. */
function moduleFiles(dir = SRC, out = []) {
  for (const f of readdirSync(dir).sort()) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) moduleFiles(p, out);
    else if (/\.(jsx|js|mjs)$/.test(f) && !/\.test\.mjs$/.test(f)) out.push(p);
  }
  return out;
}

function current(minTitle = TITLE_WORDS, minProse = PROSE_WORDS) {
  const titles = [];
  const counts = [];
  const prose = [];
  const strings = [];
  for (const p of jsxFiles()) {
    const rel = p.slice(SRC.length);
    const src = readFileSync(p, 'utf8');
    for (const t of titleRows(src, minTitle)) titles.push([rel, t]);
    for (const c of countRows(src)) counts.push([rel, c]);
    for (const r of proseRows(src, minProse)) prose.push([rel, r]);
  }
  for (const p of moduleFiles()) {
    const rel = p.slice(SRC.length);
    for (const r of stringRows(readFileSync(p, 'utf8'), minProse)) strings.push([rel, r]);
  }
  return { titles, counts, prose, strings };
}

/* The baseline, measured on this tree at WP-14.8. It may only lose rows. WP-14.13 took out six:
   the masthead's unjudged tooltip (the count is a `Term` now), the rail's "9 sections" and
   "4 formats" (its figures are the API's), and the three stale "209 faults" against a corpus
   of 210 (read from the API). WP-14.17 took out one more: the Fault Card's "three tiers" went with
   the heading that carried it, every label on the card being a glossary record now. WP-14.25 took
   out Brief Intake's "132 styles": the advisory that carried it said three styles had no native
   parti, and since WP-14.19 lists lineage partis all three have plan types, so the sentence, its
   typed count and its three hand-named styles went together. WP-14.31 took out the last fourteen
   titles and six counts, and the eight rows the widened scanners found on the way (two `title:`
   properties and six counts, every one of them removed rather than baselined). */
// BASELINE-BEGIN
const BASELINE = {
  titles: [],
  counts: [],
  /* [file, class, text]: `voice` or `disclosure` or `not-prose`, and never `corpus` (WP-14.33).
     Re-read at WP-14.33's audit, when the reader moved from a regular expression to the element
     tree: 21 rows kept their text, 17 grew to the whole paragraph they had been a fragment of,
     and 5 were new -- among them two the first reader could not see at all, a refusal after a
     template ternary in RevisionPanel and a wall-drag paragraph after a fragment in the bench. */
  prose: [
    ["components/ConflictSet.jsx", "disclosure",
      "This refusal names no fact, no conflict and no sentence. That is a defect in the refusal, not a small refusal: it is being shown as it arrived rather than dressed up."],
    ["components/ConflictSet.jsx", "disclosure",
      "Nothing is drawn from this placement. The record still carries the search&rsquo;s least-bad arrangement — it is what the conflict set above is an explanation of — and no surface draws it and no export may take it. {…} The brief or the parti is what changes. {…}"],
    ["components/RevisionPanel.jsx", "disclosure",
      "The placement the loop stopped on is still refused {…} : no sheet, export or model is drawn from it. The brief or the parti is what changes."],
    ["components/RevisionPanel.jsx", "disclosure",
      "The placement was refused when the loop started and is not now: the type’s own facts hold on the house it ended with."],
    ["dossier/Evidence.jsx", "disclosure",
      "no precedent record yet — a name a reader can find and a checker cannot resolve"],
    ["palette/ShortcutCard.jsx", "voice",
      "Everything in the corpus has one address, written kind:id. The rail cites in it, the palette prints it beside every result, and a URL is that address written down — so any view can be refreshed, gone back from, or handed to somebody else."],
    ["surfaces/BriefIntake.jsx", "voice",
      "brief intake only style and target area are required — everything else absent becomes a logged decision"],
    ["surfaces/CandidateSet.jsx", "voice",
      "The composer returns several contrasting candidates, fatal-free first and then by score, and never calls one good. Start at Brief Intake."],
    ["surfaces/CandidateSet.jsx", "voice",
      "A plan with no fatal findings is not therefore good. The corpus can tell you what is wrong and cannot tell you what is alive."],
    ["surfaces/CandidateSet.jsx", "voice",
      "What the composer chose where the brief was silent. Read it — those are the assumptions, not facts."],
    ["surfaces/DrawingSet.jsx", "voice",
      "The drawing set is generated from the plan record on the workbench. Load or compose one first."],
    ["surfaces/DrawingSet.jsx", "disclosure",
      "A refusal is content: this record does not carry what the {…} generator needs, and it says so rather than inventing it."],
    ["surfaces/ExportDetails.jsx", "voice",
      "The IR itself — the record every drawing and finding renders from. Clear dimensions, declared walls, doors, assertions. JSON against schema/plan.schema.json."],
    ["surfaces/ExportDetails.jsx", "voice",
      "The brief as typed, and the validator's latest full report — counts, findings, constraint summary and the could-not-judge list, none of it collapsed."],
    ["surfaces/ExportDetails.jsx", "voice",
      "Every sheet the generators produce, in the Drawn Language. The drawing is a render of the record; export re-renders, it never snapshots the screen."],
    ["surfaces/ExportDetails.jsx", "voice",
      "Layered DXF per sheet, in inches, the record riding on the entities as XDATA — round-trip proven: DXF → plan record → validator gives the same findings. And an IFC4 model: walls, slabs, openings, roof and spaces, every product carrying its TDL ids in a TDL property set."],
    ["surfaces/FaultCorpus.jsx", "disclosure",
      "No fault matches. The corpus holds {…} ; the filters above are hiding all of them."],
    ["surfaces/FaultCorpus.jsx", "disclosure",
      "No image records are filed against this fault yet — the record is the object until one is."],
    ["surfaces/FaultCorpus.jsx", "disclosure",
      "{…} Of the {…} solecisms listed, exactly {…} name {…} {…} ignorance. This is a system explaining an economy, not scolding a builder."],
    ["surfaces/PlanWorkbench.jsx", "voice",
      "Open one of the corpus's example plans, compose candidates from a brief, or paste a record. The drawing is a render of the record — nothing is drawn that is not in it."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "Each line is a count the placement record already carried and no surface read. A proof against a relaxed hard set is a proof of a different question."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "The record still declares the full size; only the placement is short, and nothing downstream reads these coordinates — so without this panel the trade is invisible. A room below its band is a defect that survives the life of the building. {…} Prove placement refuses the trade outright."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "This placement was refused, not drawn: the conflict set above names what could not hold. The record still carries the search&rsquo;s least-bad arrangement — nothing here draws it and no export may take it. {…}"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "This placement was proved feasible by CP-SAT, not searched: it held the record's own declared facts as hard constraints and returned {…} {…} . {…}"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "This placement was found feasible by CP-SAT, not proved: the solver returned {…} inside its budget — a placement that holds the declared facts it kept, with optimality never established, so nothing on this sheet is a proof. {…}"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "The fast search places the same house at {…} demerits against this drawing's {…} , and breaks {…} {…} declared fact(s) this one holds ( {…} ). A lower score is not on its own a better house: choosing the search is choosing a better composition over a feasibility CP-SAT found, and that is the choice."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "Its composition was not evaluated. The solve ran out of budget before the compositional objective, so no term for the front, the axis or the stack was scored on this drawing — it is the first feasible placement, not the best one. {…}"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "Where a set of them could not all hold, the ones it had to give up are named in what this placement gave up above."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "The refused placement carries its own engine and status in the conflict set above; no engine is named for a sheet, because there is none."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "No placement is on this sheet yet, so no engine is named for it."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "This placement came from the fast search, which is a hill-climb and not an optimiser: seconds-cheap, not deterministic across runs, and nothing it draws asserts that feasibility was proved. {…} Prove placement (CP-SAT) above is the act that proves it."],
    ["surfaces/PlanWorkbench.jsx", "voice",
      "{…} {…} {…} {…} A wall drag deliberately re-scores on the fast search — a hill-climb, not an optimiser — because a gesture cannot wait for a proof; every other edit takes the proof where it can be had. Either engine trades a room's size away when it must, and says so under the drawing rather than silently. A plan with no fatal findings is still not therefore good."],
    ["surfaces/Proportions.jsx", "disclosure",
      "{…} Half the order in section: every band is a member the engine emitted, run from the axis to the outer face this pack states — none traced. This pack measures its projections {…} , and says so {…} . {…} {…} {…} Hover a band for its record."],
    ["surfaces/Proportions.jsx", "disclosure",
      "Drawn at the pack’s own , {…} : the pack does not bind its module to a measure of your building, so no slider moves this drawing."],
    ["surfaces/Proportions.jsx", "disclosure",
      "The record holds no to draw: this pack gives rules, not an assembly, and no plate is drawn."],
    ["surfaces/Proportions.jsx", "disclosure",
      "No zone string: the record gives no assembly of this pack zones."],
    ["surfaces/Transcription.jsx", "voice",
      "Trace rooms over a scanned drawing, or start from a drafter's DXF — its extraction arrives as candidates with the gaps named, and a human fills every one. Nothing is guessed into the record."],
    ["surfaces/Transcription.jsx", "voice",
      "drag on the canvas to trace a room; click one to edit it"],
    ["surfaces/Transcription.jsx", "not-prose",
      "the record provenance — where this came from why this style — the reasoning rides with the record from a drafter's DXF {…} {…} {…} {…} {…} {…} {…} {…}"],
    ["surfaces/phylo/MapView.jsx", "disclosure",
      "{…} of the {…} country-wide marks are country-wide because the corpus says so rather than because this drawing failed: a family or a tradition is an abstraction over styles and has no birthplace, and a style whose hearth reads \"no design hearth\" is telling you something true."],
    ["surfaces/phylo/MapView.jsx", "disclosure",
      "{…} lineage {…} not drawn: both ends share a hearth, so the transmission happened inside one place and has no line to occupy."],
    ["surfaces/phylo/MapView.jsx", "disclosure",
      "Fetching the {…} outline for this scale; what is drawn is still the {…} one."],
    ["surfaces/phylo/MapView.jsx", "disclosure",
      "The {…} outline could not be fetched ( {…} ), so this is the {…} one at a scale it cannot carry — the facets are the simplification, not the shore. {…} try again"],
  ],
  /* [file, class, text] for STRINGS, on the same terms. */
  strings: [
    ["Gate.jsx", "voice",
      "This deployment has no password set — it accepts an API token only, so there is nothing to type here. Set WORKBENCH_PASSWORD to allow browser access."],
    ["Gate.jsx", "voice",
      "A shared password, not an account — everyone who has it sees the same corpus."],
    ["candidateOrder.js", "voice",
      "Any plan carrying a fatal finding sorts last whatever it scores, and says so on its own column."],
    ["candidateOrder.js", "voice",
      "Ordered by whether the diagram is native to the style, then by score — so the column numbered 1 is the most native, not the highest scoring. {…}"],
    ["candidateOrder.js", "voice",
      "Fatal findings decide the order before the score does — a plan carrying two sorts below a plan carrying one, and both below a plan carrying none."],
    ["components/CandidateColumn.jsx", "disclosure",
      "could not be evaluated on this plan. They are outside the fraction, not counted as passed."],
    ["components/CandidateColumn.jsx", "disclosure",
      "Scored over {…} of {…} points of evidence — {…} could not be evaluated on this plan, and are dropped rather than passed."],
    ["components/ConflictSet.jsx", "disclosure",
      "The drawing below is the heuristic’s least-bad relaxation, labelled — not a solution."],
    ["components/ConflictSet.jsx", "disclosure",
      "This record was placed by a server that does not state a refusal verdict, so nothing here is drawn from it and nothing here claims it could be."],
    ["components/RevisionPanel.jsx", "disclosure",
      "The findings above are of the placement this key was measured on — the loop’s own, as it ended."],
    ["components/RevisionPanel.jsx", "disclosure",
      "The sheet above is the placement this key was measured on — the loop’s own, drawn as it ended."],
    ["components/RevisionPanel.jsx", "disclosure",
      "The sheet above is a fresh solve of the revised record; the loop’s own key was measured {…} , and the two can differ."],
    ["plate/assemblyLayout.js", "disclosure",
      "turned across the jamb, it projects nothing from the wall plane; nothing to draw at no depth"],
    ["rail/RailHost.jsx", "voice",
      "No ANTHROPIC_API_KEY is attached to the server, so the AI assistant is off. Everything else works without it — set the key and restart to turn the assistant on."],
    ["rail/RailHost.jsx", "voice",
      "I am an AI assistant: a language model reading this corpus for you. Ask the corpus. Every claim I make carries a citation that navigates this canvas, the tools I consult are shown as I use them, and I will say what I could not evaluate — unjudged is not passed."],
    ["revision.js", "disclosure",
      "stopped before the first round: the placement could not be evaluated, so no round could be judged"],
    ["round/Round.jsx", "disclosure",
      "this browser reports no WebGL context, so the model cannot be drawn here — the flat plates below are unaffected"],
    ["round/overlays.js", "disclosure",
      "the record states no bay module, so no grid can be drawn"],
    ["round/overlays.js", "disclosure",
      "each storey lifted by {…} × its own height; the roof rides on the top storey"],
    ["round/overlays.js", "disclosure",
      "concentric with the main block: the record states no direction to separate it along"],
    ["search/staticEntries.js", "not-prose",
      "front door home landing welcome about introduction what is this start here begin overview"],
    ["search/staticEntries.js", "not-prose",
      "style record styles record full record tells diagnostic constraints sources exemplars characteristics period geography dossier find a style index the kit kit bindings cascade inheritance specified forbidden open extends provenance parts vocabulary"],
    ["search/staticEntries.js", "not-prose",
      "the phylogeny phylogeny lineage descent ancestry tree family graph taxa taxonomy evolution origins time axis map geography where styles came from"],
    ["search/staticEntries.js", "not-prose",
      "brief intake new start begin requirements program rooms wanted site budget client wishes commission"],
    ["search/staticEntries.js", "not-prose",
      "plan workbench bench plan drawing rooms layout solve placement geometry critique findings edit the plan floor plan"],
    ["search/staticEntries.js", "not-prose",
      "transcription transcribe ingest import bring in drawing to record trace digitise digitize scan upload dxf in"],
    ["search/staticEntries.js", "not-prose",
      "drawing set drawings sheets elevation section roof bearing plate print draw in the round model"],
    ["search/staticEntries.js", "not-prose",
      "details export download save out json svg dxf ifc cad bim autocad revit file take out"],
    ["search/staticEntries.js", "not-prose",
      "proportions proportion packs modules orders classical ratios dimensions rules measure geometry column diameter entablature"],
    ["search/staticEntries.js", "not-prose",
      "fault corpus faults solecisms errors mistakes problems wrong bad practice anti-patterns diagnosis what not to do"],
    ["search/staticEntries.js", "not-prose",
      "elements element slots slot alphabet ontology parts of a building catalogue records rooms room types massings groupings partis plan types plan diagrams"],
    ["search/staticEntries.js", "not-prose",
      "help shortcuts keys keyboard hotkeys commands citation grammar how do i what can i type question mark"],
    ["sheet/Sheet.jsx", "disclosure",
      "The compositional objective did not run, so no term for the front, the axis or the stack was evaluated on it."],
    ["sheet/Sheet.jsx", "disclosure",
      "this placement was refused; it is drawn only because a wall drag asked for the fast search by name, and it may not be exported"],
    ["sheet/Sheet.jsx", "disclosure",
      "placed by the fast search behind a gesture, and it may not be exported"],
    ["sheet/Sheet.jsx", "disclosure",
      "{…} ft off the bay line — this cut is a joist run that does not land on a bearing wall"],
    ["sheet/Sheet.jsx", "disclosure",
      "A WORKING SKETCH, not a drawing — placed by the fast search behind a wall drag {…} ; it may not be exported."],
    ["sheet/Sheet.jsx", "disclosure",
      "Walls {…} : envelope {…} in outside the placed rooms, partitions {…} in centred on them; room figures are the record's clear extents."],
    ["sheet/Sheet.jsx", "disclosure",
      "The record states no wall assembly, so the walls are drawn at this sheet's conventional {…} in and {…} in — a convention, not a reading."],
    ["sheet/Sheet.jsx", "disclosure",
      "{…} cut(s) the solver located on no wall of this level — counted, not drawn."],
    ["sheet/Sheet.jsx", "disclosure",
      "Clear span not evaluated — the construction catalogue could not be read; no span is claimed clear."],
    ["sheet/Sheet.jsx", "disclosure",
      "{…} clear span(s) over the framing capacity, worst {…} ft — at least that many: a bearing line is credited across the whole plate however short the wall runs."],
    ["sheet/Sheet.jsx", "disclosure",
      "0 clear span(s) over the framing capacity — at least none found: a bearing line is credited across the whole plate however short the wall runs."],
    ["sheet/Sheet.jsx", "disclosure",
      "{…} declared window(s) had no clear run left on their wall beside its doors — declared, not drawn."],
    ["sheet/Sheet.jsx", "disclosure",
      "{…} room(s) are drawn at a size the record does not declare — worst {…} {…} {…} % by area, marked ∗."],
    ["sheet/Sheet.jsx", "disclosure",
      "{…} exterior door(s) carry no placement in the record and are drawn at conventional mid-wall position, on a wall inferred from the room’s declared exterior walls."],
    ["sheet/derive.js", "disclosure",
      "no declared exterior wall of this room is on its own massing element's boundary here"],
    ["sheet/overlayRules.js", "disclosure",
      "privacy_rank {…} is outside the ramp this sheet draws ( {…} to {…} ), and where it belongs on the ramp is unruled"],
    ["surfaces/BriefIntake.jsx", "voice",
      "Who lives here and how they use a house — the thing that decides whether the dining room gets built and never used."],
    ["surfaces/BriefIntake.jsx", "voice",
      "Left blank — {…} — each becomes a composer decision, reported in the decision log. An assumption, not a fact."],
    ["surfaces/DrawingSet.jsx", "voice",
      "The elevation generator models a part of the photograph-measurable fault corpus and no more; the rest have no model at this layer yet (disclosed rather than closed by fabricating data), and what it could not measure is absent from the measurements rather than reported as zero. Sash lights are set for the declared date; the cornice is the style’s own entablature reduction at the real storey height."],
    ["surfaces/DrawingSet.jsx", "voice",
      "Cut from the same record as the plan. Storey heights come from the storey-graduation pack; nothing is drawn that is not in the section record."],
    ["surfaces/DrawingSet.jsx", "voice",
      "Every upper wall line that does not continue to a wall below is a transfer beam — a number a builder prices. Over-spans are flagged by the generator itself."],
    ["surfaces/DrawingSet.jsx", "voice",
      "Wing ridges step down; the pitch sits inside the style band; chimneys satisfy the style constraint or say so."],
    ["surfaces/DrawingSet.jsx", "voice",
      "The geometry solver’s own render — the workbench sheet redrawn by build/render_plan.py from the same coordinates, for the set. Relaxations are counted in the header."],
    ["surfaces/ExportDetails.jsx", "disclosure",
      "the bench is showing a working sketch from a wall drag — a sketch is never a file"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "the {…} exception could not be judged ( {…} ), and its own test says {…} where the general rule says {…}"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "the record changed while the corrective rounds ran — the revision was not applied"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "the record changed while the loop ran — the revision was not applied"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "· worst {…} ft — each is a joist run that does not land on a bearing wall"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "this critique is of an earlier evaluation — the record has changed; run it again"],
    ["surfaces/PlanWorkbench.jsx", "voice",
      "each finding row carries its class; a move answers it, or it is the engine's, the critic's own, or the architect's. Nothing here calls the plan good."],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "A working sketch is drawn below it because a wall drag asked for the fast search by name and a gesture cannot wait for a proof. It is a sketch, not a drawing, and it may not be exported."],
    ["surfaces/PlanWorkbench.jsx", "voice",
      "⌘/ctrl-scroll to zoom · drag to pan · a wall handle still drags the wall"],
    ["surfaces/PlanWorkbench.jsx", "disclosure",
      "The sketch above is the wall drag’s, and is labelled as one."],
    ["surfaces/Proportions.jsx", "disclosure",
      "{…} member {…} state no projection at all and are drawn at the naked — that is an absent figure, not a flush face."],
  ],
};
// BASELINE-END

/* a − b as multisets of rows, so two identical rows in one file are two rows. */
function minus(a, b) {
  const left = new Map();
  for (const r of b) left.set(JSON.stringify(r), (left.get(JSON.stringify(r)) || 0) + 1);
  const out = [];
  for (const r of a) {
    const k = JSON.stringify(r);
    if (left.get(k)) left.set(k, left.get(k) - 1);
    else out.push(r);
  }
  return out;
}

if (process.env.COPY_RATCHET_PRINT) {
  console.log(JSON.stringify(current(), null, 2));
}

test('the scanner finds an explanation in every form a title is written, and not in a label or a comment', () => {
  const twelve = 'this tooltip explains in twelve words what the glossary should be saying instead';
  const fixture = [
    `<a title="${twelve}" />`,
    `<a title='${twelve}' />`,
    `<a title={'${twelve}'} />`,
    `<a title={on ? '${twelve}' : 'short'} />`,
    `<a title={\`${twelve} \${n}\`} />`,
    '<a title="Give the atlas the whole window" />',           // seven words: a label
    `/* <a title="${twelve}" /> */`,
    `// <a title="${twelve}" />`,
    '<a title={someVariable} />',
  ].join('\n');
  const rows = titleRows(fixture);
  assert.equal(rows.length, 5, `found ${JSON.stringify(rows)}`);
  assert.ok(rows.every((r) => r.startsWith('this tooltip explains')));
});

test('the scanner finds a tooltip written as a title: property, which is how a compiled component writes one', () => {
  const twelve = 'this tooltip explains in twelve words what the glossary should be saying instead';
  const fixture = [
    `React.createElement("span", { "data-tag": "", title: "${twelve}", style: { font: 'x' } })`,
    `h("a", { title: on ? '${twelve}' : 'short', href: x })`,
    "h('b', { title: describeTerm(glossary, 'finding-class').title })",   // a record's: nothing to find
    "const card = { title: 'The plan record' };",                        // a label
  ].join('\n');
  const rows = titleRows(fixture);
  assert.equal(rows.length, 2, `found ${JSON.stringify(rows)}`);
  assert.ok(rows.every((r) => r.startsWith('this tooltip explains')));
});

test('the scanner finds a count written as a digit or a word, and not a size, a time or a comment', () => {
  const fixture = [
    '<p>the 9 sections of a dossier</p>',
    "const meta = '4 formats';",
    '<span>five authorities · at</span>',
    "style={{ width: 12, padding: '2px 7px' }}",               // sizes are not counts
    "<p>{n} faults</p>",                                        // a count from data: the point
    '// 36 styles in a comment',
    '<p>1.5 metres</p>',                                        // a decimal is a measurement
  ].join('\n');
  assert.deepEqual(countRows(fixture), ['9 sections', '4 formats', 'five authorities']);
});

test('the scanner finds the counts the first reader missed, and not a word that merely ends in s', () => {
  const fixture = [
    '<input placeholder="filter 164 taxa" />',                               // an irregular plural
    "'with all 262 recorded pack conflicts'",                                // adjectives between
    '<p>corpus-wide, 295 of 660 style constraints carry no test</p>',        // a share
    '<span>(86 of them priced in dollars)</span>',
    '<p>column numbered 1 is the most native</p>',                           // "is" is not a plural
    '<p>Score is out of 100 and higher is better</p>',                       // nor is a joined phrase
    '<p>{n} of {m} findings shown</p>',                                      // counts from data
    "summary={group || 'all 8'}",                                            // a whole-set count
    "summary={group || `all ${groups.length}`}",                             // the same, from data
  ].join('\n');
  assert.deepEqual(countRows(fixture),
    ['164 taxa', '262 recorded pack conflicts', '295 of 660', '660 style constraints', '86 of them',
      'all 8']);
});

/* THE BASELINE IS EMPTY, SO THIS IS WHAT STOPS AN EMPTY RESULT FROM BEING A BLIND ONE. A scanner
   that read no file, or no title, or no count-shaped text, would report the same empty lists as
   a clean tree. So: the walk reads the components; the title reader, asked for shorter titles,
   finds the labels the tree does carry (they are what an explanation would be written beside);
   and the tree carries counts written from DATA -- `{n} findings` -- which the count reader
   deliberately passes, so it is reading JSX text and choosing. */
test('the premise: the scan reads the app’s components, its titles and its count-shaped text', () => {
  const files = jsxFiles();
  assert.ok(files.length > 20, 'the walk found the components');
  assert.ok(current(3).titles.length > 10, 'the title reader sees the short titles the tree carries');
  const fromData = files.map((p) => stripComments(readFileSync(p, 'utf8')))
    .reduce((n, s) => n + [...s.matchAll(/\}\s+[a-z][a-z-]*s\b/g)].length, 0);
  assert.ok(fromData > 10, 'the tree writes counts from data, which the count reader passes by design');
});

test('no new app-written explanation in a title=', () => {
  const added = minus(current().titles, BASELINE.titles);
  assert.deepEqual(added, [],
    'a title= of eight or more words is an explanation: write it as a glossary record and show it '
    + 'with <Term> or useTermDescription, not as a tooltip nothing checks');
});

test('no new count literal in JSX', () => {
  const added = minus(current().counts, BASELINE.counts);
  assert.deepEqual(added, [],
    'a count typed into a page goes stale silently: take it from the API or the payload in hand');
});

test('the prose reader finds a paragraph the app wrote, and not a label, a comment or code', () => {
  const fixture = [
    '<p>Japanese, Islamic, South Asian and African traditions are absent, and the schema extends to them.</p>',
    '<p>No fault matches. The corpus holds {n}; the filters above are hiding all of them.</p>',
    '<p>The corpus records where a style arose in prose and not in coordinates at all.\n  {abstract > 0 && (<b>x</b>)}</p>',
    '<span>the style list could not be read</span>',                           // a short status line
    '{/* <p>a commented paragraph of well over twelve words that no reader shows anyone</p> */}',
    '// <p>a line comment holding a paragraph of well over twelve words nobody reads</p>',
    'if (a.length > b.length && first.kind === second.kind && ok(first, second, third, fourth, '
      + 'fifth, sixth, seventh, eighth, ninth, tenth)) { go(); }',
  ].join('\n');
  assert.deepEqual(proseRows(fixture), [
    'Japanese, Islamic, South Asian and African traditions are absent, and the schema extends to them.',
    'No fault matches. The corpus holds {…} ; the filters above are hiding all of them.',
    'The corpus records where a style arose in prose and not in coordinates at all. {…}',
  ]);
});

/* EACH SHAPE WP-14.33's AUDIT WALKED PAST THE FIRST READER, driven. Every fixture carries the
   sentence R5 removed, so a reader gone blind to any one shape lets the ruling's own case back. */
const REMOVED = 'Japanese, Islamic, South Asian and African traditions are absent, and the schema extends to them without modification.';
test('the audit\'s shapes: after a closing brace, split by inline tags, and in a string', () => {
  // text after `}` closing an expression that holds JSX
  assert.equal(proseRows(`<p>{on && (<b>note</b>)} ${REMOVED}</p>`).length, 1);
  assert.equal(proseRows(`<p>{a ? <>x</> : <i>y</i>} ${REMOVED}</p>`).length, 1);
  // a paragraph split by inline elements into runs under twelve words each
  const split = '<p>Japanese, Islamic, South Asian and African traditions are <em>absent</em>, and the '
    + '<Term id="schema">schema</Term> extends to them without <code>modification</code>.</p>';
  assert.equal(proseRows(split).length, 1, 'an inline tag does not end a paragraph');
  // a block child does end one, and each side is read on its own
  assert.equal(proseRows('<div>short words here<p>and a short paragraph here too</p></div>').length, 0);
  // in a string: a literal child, an attribute, a createElement argument, a constant, a `+` chain
  assert.equal(stringRows(`<p>{'${REMOVED}'}</p>`).length, 1);
  assert.equal(stringRows(`<p aria-label="${REMOVED}" />`).length, 1);
  assert.equal(stringRows(`h("p", null, "${REMOVED}")`).length, 1);
  assert.equal(stringRows(`const NOTE = \`${REMOVED}\`;`).length, 1);
  assert.deepEqual(stringRows("const t = 'Japanese, Islamic, South Asian ' + n + ' and African "
    + "traditions are absent, and ' + 'the schema extends to them.';"),
  ['Japanese, Islamic, South Asian {…} and African traditions are absent, and the schema extends to them.']);
  // and code is not a sentence: an import, a path, a class list
  assert.deepEqual(stringRows("import x from './a/b/c.js'; const c = 'tdl-a tdl-b tdl-c tdl-d';"), []);
});

test('a comment is found as a comment, and the characters of one inside a string are not one', () => {
  // the shipped defect: a file-type pattern in an attribute opened a "comment" that ran on
  const src = '<input accept="image/' + '*" />\n<p>' + REMOVED + '</p>\n{/' + '* a real one *' + '/}';
  assert.equal(proseRows(src).length, 1, 'the paragraph after the attribute is read');
  assert.ok(stripComments(src).includes('African traditions'), 'and is not blanked as a comment');
  assert.ok(!stripComments(src).includes('a real one'), 'while the real comment is');
  // a comment between two attributes, and an apostrophe in JSX text, which is a letter
  assert.equal(proseRows('<div a={1} /' + '* note *' + '/ b="2"><p>' + REMOVED + '</p></div>').length, 1);
  assert.equal(proseRows(`<p>It's the reader's own ${REMOVED}</p>`).length, 1);
  // a regular expression holding quotes and a brace is not a string or a block
  assert.equal(proseRows(`const r = /['{]/g; const el = <p>${REMOVED}</p>;`).length, 1);
});

/* An empty result from a blind reader looks exactly like a tree with no paragraphs, so the premise
   is asserted: the tree's own voice is found, and a lower threshold finds strictly more. */
test('the premise: the prose and string readers see what the tree carries', () => {
  const now = current();
  assert.ok(now.prose.length > 30, `the reader found ${now.prose.length} paragraphs`);
  assert.ok(now.strings.length > 30, `the string reader found ${now.strings.length} sentences`);
  const lower = current(TITLE_WORDS, 7);
  assert.ok(lower.prose.length > now.prose.length, 'a lower threshold finds the status lines too');
  assert.ok(new Set(now.strings.map(([f]) => f)).size > 10, 'the string reader reads .js modules and .jsx alike');
  assert.ok(now.strings.some(([f]) => f.endsWith('.js')), 'a .js module is read');
});

test('every baselined paragraph and sentence carries a class, and none is a corpus fact', () => {
  const CLASSES = new Set(['voice', 'disclosure', 'not-prose']);
  const bad = [...BASELINE.prose, ...BASELINE.strings].filter((r) => r.length !== 3 || !CLASSES.has(r[1]));
  assert.deepEqual(bad, [],
    'a prose or string row is [file, class, text] and its class is voice, disclosure or not-prose. '
    + 'There is no corpus class: a corpus fact is derived from the payload or recorded in the glossary');
});

test('no new app-written paragraph', () => {
  const baseline = BASELINE.prose.map(([f, , t]) => [f, t]);
  const added = minus(current().prose, baseline);
  assert.deepEqual(added, [],
    'a paragraph of twelve or more words the app wrote: if it states a corpus fact, derive it from '
    + 'the payload in hand or record it in glossary/; if it is the workbench\'s own voice or a '
    + 'disclosure about the payload, add it to BASELINE.prose with that class');
});

test('no new app-written sentence in a string', () => {
  const baseline = BASELINE.strings.map(([f, , t]) => [f, t]);
  const added = minus(current().strings, baseline);
  assert.deepEqual(added, [],
    'a string of twelve or more words the app shows: the same rule as a paragraph -- derive or record '
    + 'a corpus fact, and add anything else to BASELINE.strings with its class');
});

test('the baseline only shrinks: a row that is gone must leave the baseline in the same commit', () => {
  const now = current();
  const gone = [...minus(BASELINE.titles, now.titles), ...minus(BASELINE.counts, now.counts),
    ...minus(BASELINE.prose.map(([f, , t]) => [f, t]), now.prose),
    ...minus(BASELINE.strings.map(([f, , t]) => [f, t]), now.strings)];
  assert.deepEqual(gone, [],
    'these baseline rows no longer exist in the tree; delete them from BASELINE so the ratchet '
    + 'cannot be refilled by a new row of the same text');
});
