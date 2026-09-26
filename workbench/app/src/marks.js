/* ONE MEANING PER MARK, AND THE FORM EACH ONE IS DRAWN IN (WP-14.29, PRD tranche 2 §D).

   Ruled 25 Sep 2026: one meaning per hatch, one product key. Until then the unjudged hatch drew
   five things on screen (could not evaluate, yours to decide, not applicable, loading, low
   confidence) and the 45° hatch six, so a key could not be written for either: a key says what a
   mark MEANS, and a mark that means five things means none of them.

   THREE PLACES SAY ONE THING, AND `src/marks.test.mjs` HOLDS THEM TOGETHER:
     theme/tokens.css   each `--mark-*` custom property, whose value is the paint of its form
     glossary/*.json    each record whose `mark` names that property -- exactly one per mark
                        (`build/check_glossary.py` rule 13) -- and whose term is the mark's word
     this file          the FORM each mark is drawn in, which a custom property cannot state

   A form is not a word, so this file writes none: the word a mark means is its record's, read
   through the glossary by whoever draws it (`components/JudgmentMark.jsx`,
   `components/MarkKey.jsx`). What is here is geometry: a filled square, an open one, a hatched
   one, a dashed one, a rule, a field of lines, or no glyph at all (`word`, for loading, which is
   not a state of anything and so borrows no state's square).

   Pure; imports nothing. */

/* Every duty token, and its form. A token missing here is a mark nobody can draw, and a form
   here for a token the stylesheet does not declare is a form for nothing: both fail the test. */
export const MARK_FORMS = Object.freeze({
  '--mark-unjudged': 'hatched-square',
  '--mark-yours-to-judge': 'open-square',
  '--mark-not-applicable': 'rule',
  '--mark-passed': 'filled-square',
  '--mark-failed': 'filled-square',
  '--mark-refused': 'heavy-open-square',
  '--mark-loading': 'word',
  '--mark-low-confidence': 'dashed-square',
  '--mark-not-built': 'field',
  '--mark-wanted': 'field',
  '--mark-set-aside': 'field',
  '--mark-forbidden': 'field',
});

/* A field hatch is drawn in `currentColor`; the ink each consumer gives it, so the key draws it
   the way the surface does. `--mark-not-built`'s hatch names its own ink and takes none. */
const FIELD_INK = Object.freeze({
  '--mark-wanted': 'var(--unsourced)',
  '--mark-set-aside': 'var(--ink-3)',
  '--mark-forbidden': 'var(--var-forbidden)',
});
const FIELD_GROUND = Object.freeze({
  '--mark-forbidden': 'var(--bind-forbidden-field)',
});

/* The states `components/JudgmentMark.jsx` draws, each to its duty token and to the glossary
   record whose word it is. The first three keys are `judgment.js`'s `JUDGMENT_MARK` values
   (pass, fail, unjudged), which every existing caller already passes; the other three are the
   states the unjudged square used to stand in for. */
export const JUDGMENT_MARKS = Object.freeze({
  pass: Object.freeze({ token: '--mark-passed', record: 'judgment-passed' }),
  fail: Object.freeze({ token: '--mark-failed', record: 'judgment-failed' }),
  unjudged: Object.freeze({ token: '--mark-unjudged', record: 'judgment-unjudged' }),
  'yours-to-judge': Object.freeze({ token: '--mark-yours-to-judge', record: 'judgment-yours-to-judge' }),
  'not-applicable': Object.freeze({ token: '--mark-not-applicable', record: 'judgment-not-applicable' }),
  refused: Object.freeze({ token: '--mark-refused', record: 'judgment-refused' }),
});

/* THE PRODUCT KEY'S ROWS, READ FROM THE GLOSSARY AND FROM NOTHING ELSE. Every record carrying a
   `mark`, grouped by family in the order the payload lists families, each group in the payload's
   own record order. `components/MarkKey.jsx` draws exactly this; it lives here, pure, so
   `src/marks.test.mjs` can hold the key to the records without a browser. A family whose records
   carry no mark is not a group. */
export function markKeyGroups(lookup) {
  if (!lookup || typeof lookup.families !== 'function') return [];
  return lookup.families()
    .map((family) => ({ family, rows: lookup.family(family).filter((r) => typeof r.mark === 'string') }))
    .filter((g) => g.rows.length > 0);
}

/* The inline style that draws `token` at `size` px. Null for a token with no form, which a
   caller draws as nothing rather than as some other mark. `word` returns the style the word is
   set in; the caller supplies the word. */
export function markGlyph(token, size = 13) {
  const form = MARK_FORMS[token];
  const paint = `var(${token})`;
  const box = { width: size, height: size, flex: 'none', display: 'block', boxSizing: 'border-box' };
  switch (form) {
    case 'filled-square':
      return { ...box, backgroundColor: paint };
    case 'open-square':
      return { ...box, border: `1px solid ${paint}` };
    case 'heavy-open-square':
      return { ...box, border: `2px solid ${paint}` };
    case 'hatched-square':
      return { ...box, border: '1px solid var(--judge-unjudged)', backgroundImage: paint };
    case 'dashed-square':
      return { ...box, border: `1px dashed ${paint}` };
    case 'rule':
      // an em rule: as wide as the square would be, one medium line, centred where it stands
      return { width: size, height: 0, flex: 'none', display: 'block', alignSelf: 'center',
        borderTop: `var(--lw-medium) solid ${paint}` };
    case 'field':
      return { width: size * 2.2, height: size, flex: 'none', display: 'block', boxSizing: 'border-box',
        border: '1px solid var(--rule)', color: FIELD_INK[token] || 'var(--ink-2)',
        backgroundColor: FIELD_GROUND[token] || 'var(--paper)', backgroundImage: paint };
    case 'word':
      return { color: paint, font: 'italic var(--fw-reg) var(--fs-body-s)/1.4 var(--serif)' };
    default:
      return null;
  }
}
