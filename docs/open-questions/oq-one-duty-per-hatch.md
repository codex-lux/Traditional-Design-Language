# oq/one-duty-per-hatch — the unjudged hatch carries five meanings, the 45° hatch six, and a key cannot be drawn for a mark that means several things

*Status: OPEN · Raised in: WP-14.0 (24 September 2026)*

**The finding.** Phase 14's reader asked for keys. A key says what a mark MEANS, so it can only be
written for a mark with one meaning, and the workbench's marks were never assigned one each. Every
figure below was measured on this tree by reading `workbench/app/src/theme/tokens.css` and every
file under `workbench/app/src` that names the token; test files excluded.

## The unjudged hatch — five duties

`--hatch-unjudged` (`tokens.css:205`), aliased as `--judge-unjudged-fill` (`:367`) under a comment
that calls it *"Unjudged is a FORM … Never a colour"* (`:362-363`):

| duty | where |
|---|---|
| could not evaluate | `components/JudgmentMark.jsx:22-25` via `PlanWorkbench.jsx:684`; the masthead's *N unjudged* (`Chrome.jsx:92`); the assistant's unjudged block (`components/AiRail.jsx:108`) |
| yours to decide (`scope: judgment`, a rule flagged `judgment`) | `PlanWorkbench.jsx:679`, `StyleRecord.jsx:152`, the assistant's *for you to decide* (`AiRail.jsx:78`), a derived rule the sources do not determine (`Proportions.jsx:318-319`) |
| not applicable (every test preconditioned on a measurement the house does not meet) | `PlanWorkbench.jsx:689` |
| loading | `BriefIntake.jsx:267` — *"native partis unknown · reading the corpus…"* |
| low confidence | `surfaces/Phylogeny.jsx:279`, a style record's `confidence: low` |

The first three are three of the four states the corpus insists must never collapse — *could not
evaluate*, *a judgment put to the human*, *not applicable* — drawn as one square. The fourth and
fifth are not verdicts at all. And the words that would separate them do not reach a screen reader:
`JudgmentMark` holds them in `words` (`:26-30`), renders the square `aria-hidden` (`:32`), and
prints the word only as a `title` on the label-less form (`:39`); with a label, the only thing
telling *could not evaluate* from *yours to decide* at `PlanWorkbench.jsx:679` and `:684` is the
reason prose beside it.

## The 45° hatch — six duties

`--hatch-45` (`tokens.css:200`):

| duty | where |
|---|---|
| an image record with no file yet | `components/UnsourcedImageRecord.jsx:33` |
| diagrams the lot dropped before placement | `surfaces/CandidateSet.jsx:261` |
| a thing that happens on another surface (*conflict set · on the bench, not here*) | `surfaces/BriefIntake.jsx:309` |
| designed and not built (*forthcoming*) | `surfaces/ExportDetails.jsx:210` |
| traditions the taxonomy acknowledges it lacks | `surfaces/Phylogeny.jsx:295` |
| a style deliberately unbound to any pack — *a named exception, not a hole* | `surfaces/StyleRecord.jsx:194` |

**The forthcoming card uses the 45° hatch while `--hatch-forthcoming` (`:207`) exists for it and is
read by no component.** Neither are `--hatch-135`, `--hatch-cross`, `--hatch-masonry`,
`--hatch-crosshatch` or `--hatch-water` (`:201-208`): six of the ten hatch tokens are defined and
unused, while two carry eleven duties between them.

**And a docstring claims a hatch the code does not draw.** `surfaces/phylo/MapView.jsx:15-18` says
country-precision marks are *"drawn as hollow hatched rings, the same hatch the product uses
everywhere for 'not judged'"*; the mark at `:410-415` is a hollow DASHED ring
(`strokeDasharray '2 1.6'`) with no hatch at all.

## Colour, the same shape

- `--gilt-deep` (`tokens.css:78`) is aliased ten times (`:332`, `:341`, `:344`, `:346`, `:353`,
  `:377`, `:383`, `:388`, `:405`, `:415`): accent text, the focus ring, links (twice), MINOR
  severity, a canonical variant, a canonical massing affinity, an editorial source, a cheap fix,
  and brass. Counting the two links and the two canonicals once each, **eight duties**; it is also
  named directly on 70 lines outside the token file.
- **Tradition hue `--t3` is `#AF6B50`** (`:90`), byte-identical to `--brick` (`:75`), which the
  token file annotates *"and the UI's fatal"* and aliases as `--sev-fatal`, `--judge-fail`,
  `--bind-forbidden`, `--var-forbidden`, `--aff-forbidden`, `--kind-invented`. `--t3` is Iberian
  Mediterranean (`surfaces/Phylogeny.jsx:34`): every style of that tradition is drawn in the colour
  of failure. (`--t0` equals `--sepia` too, which is a material colour and not a verdict.)
- **Pass and fail differ by 1.08 : 1 in luminance** — `--green-deep #6B7C5C` against `--brick
  #AF6B50` — so the JudgmentMark's two filled states are separated by hue alone.

## What each answer would change

1. **One duty per hatch, ruled as a table** — each of the four judgment states its own form
   (the three the corpus names plus *not applicable*), loading and low confidence moved off the
   judgment hatch altogether, the 45° hatch split between *not built* (`--hatch-forthcoming`, which
   exists) and *elsewhere / absent by design*, and a product-wide key written from glossary records
   once each mark has one meaning. This moves marks on at least eleven files and the browser walk's
   pen and hatch checks.
2. **A duty per CONTEXT** — keep the tokens and key each surface separately. Cheaper, and it
   leaves the same square meaning *could not evaluate* on the bench and *yours to decide* one
   click away, which is the ambiguity the reader complained of.
3. **Tradition hue separately** — reassign `--t3` from the existing palette. Graphic Standard No. 1
   admits no new colours, so this is a choice among named inks and the ruling decides which duty
   yields.

The first is what a key needs; the ruling is about whether the marks are the corpus's vocabulary
(then they are records, like everything else) or the app's.

## What tranche 1 does meanwhile

No token changes (WP-14.8 owns `tokens.css` and adds only focus and reflow rules). No product-wide
key. WP-14.9's plate keys its own marks in-frame, worded from glossary records, and needs one it
has no single-duty hatch for — *wall, drawn nominal* — so that key names what the hatch means on
that plate and claims nothing for it elsewhere. WP-14.6's `judgment.js` gives the judgment states
their names in code, and WP-14.9 reads it where `Proportions.jsx:530` maps `holds: null` to *fail*
today (latent: no invariant in the corpus is `null` now) — the words are fixed before the marks
are.
