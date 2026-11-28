// The palette takes the keyboard in the commit that shows it.
//
// 28 Nov 2026. `CommandPalette.jsx` focused its input from a `setTimeout(..., 0)` inside a passive
// effect, so the dialog was in the document for a few milliseconds before its input could be
// typed into. Keys pressed in that window went to the page behind, where the global handler
// (`keys.js`) reads `/`, `?`, `[` and `]` as acts, and the query lost its first characters.
// Measured in a browser on this tree and on a build of `ea25d12`: the input held focus at the
// instant the dialog appeared 0 times of 12 on both, and took it a median 3 to 6 ms later.
//
// The browser walk met it twice. At WP-14.23 two of five typed ids went unfound and the walk
// was changed to `fill` the input. Since Phase 18 merged, its check `a newcomer word finds the
// fault corpus` failed on six CI runs of six, having passed on the five before: all eight keys
// of the word landed on <body>, the query stayed empty, and the first row was the front door.
// The ranking was never wrong (`e2e/search-unit.mjs` holds the word to the fault corpus).
//
// THE BEHAVIOUR IS HELD IN THE WALK, which reads `document.activeElement` at the instant the
// dialog enters the document. This file holds the shape that behaviour depends on, where the
// walk does not run: it reads source only and imports nothing from node_modules
// (`no_bare_imports.test.mjs`). It is a weaker guard than the walk's and says so.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { stripComments } from './sourceReader.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const SRC = stripComments(readFileSync(join(here, 'palette', 'CommandPalette.jsx'), 'utf8'));

/* Every call of `callee` in `src`, as [start, end) offsets of its parenthesised arguments.
   Strings and template literals are skipped, so a bracket inside one does not count. */
export function callSpans(src, callee) {
  const spans = [];
  let from = 0;
  for (;;) {
    const at = src.indexOf(`${callee}(`, from);
    if (at === -1) break;
    from = at + callee.length + 1;
    const before = src[at - 1];
    if (before && /[\w$]/.test(before)) continue;        // `resetTimeout(` is not `setTimeout(`
    let depth = 1;
    let i = from;
    let quote = null;
    while (i < src.length && depth > 0) {
      const c = src[i];
      if (quote) {
        if (c === '\\') i += 1;
        else if (c === quote) quote = null;
      } else if (c === '"' || c === "'" || c === '`') quote = c;
      else if (c === '(') depth += 1;
      else if (c === ')') depth -= 1;
      i += 1;
    }
    spans.push([from, i - 1]);
  }
  return spans;
}

const offsetsOf = (src, needle) => {
  const out = [];
  for (let i = src.indexOf(needle); i !== -1; i = src.indexOf(needle, i + 1)) out.push(i);
  return out;
};
const inside = (spans, at) => spans.some(([a, b]) => at >= a && at < b);

/* What the file says about its focus, as a verdict a mutation can be driven through. */
export function focusVerdict(src) {
  const focuses = offsetsOf(src, '.focus()');
  if (!focuses.length) return 'the palette never focuses its input';
  const layout = callSpans(src, 'React.useLayoutEffect');
  const deferred = ['setTimeout', 'requestAnimationFrame', 'queueMicrotask', 'requestIdleCallback']
    .flatMap((name) => callSpans(src, name).map((s) => [name, s]));
  for (const at of focuses) {
    if (!inside(layout, at)) return 'a focus() call is outside a layout effect';
    const late = deferred.find(([, s]) => inside([s], at));
    if (late) return `a focus() call is deferred by ${late[0]}`;
  }
  return null;
}

/* The query is cleared when the palette opens. If that ran after the input could be typed into,
   it would wipe what had just been typed, so it may not live in a passive effect. */
export function resetVerdict(src) {
  const resets = offsetsOf(src, "setQ('')");
  if (!resets.length) return 'the palette never clears its query on opening';
  const passive = callSpans(src, 'React.useEffect');
  return resets.some((at) => inside(passive, at))
    ? 'the query is cleared in a passive effect, after the input can be typed into' : null;
}

test('the reader is reading the palette, with its comments gone', () => {
  assert.match(SRC, /role="dialog"/);
  assert.match(SRC, /role="combobox"/);
  assert.doesNotMatch(SRC, /after paint, or the input is not in the document yet/);
});

test('the palette focuses its input inside a layout effect, with no timer before it', () => {
  assert.equal(focusVerdict(SRC), null);
});

test('the query is not cleared after the input can be typed into', () => {
  assert.equal(resetVerdict(SRC), null);
});

test('the two verdicts convict the shapes they are for', () => {
  const timer = `React.useEffect(() => { if (open) { setQ('');
    const t = setTimeout(() => inputRef.current && inputRef.current.focus(), 0); } }, [open]);`;
  assert.equal(focusVerdict(timer), 'a focus() call is outside a layout effect');
  assert.match(resetVerdict(timer), /passive effect/);

  const timerInLayout = `React.useLayoutEffect(() => { setQ('');
    setTimeout(() => inputRef.current.focus(), 0); }, [open]);`;
  assert.equal(focusVerdict(timerInLayout), 'a focus() call is deferred by setTimeout');

  const frame = `React.useLayoutEffect(() => { requestAnimationFrame(() => el.focus()); }, [open]);`;
  assert.equal(focusVerdict(frame), 'a focus() call is deferred by requestAnimationFrame');

  const passive = `React.useEffect(() => { inputRef.current.focus(); }, [open]);`;
  assert.equal(focusVerdict(passive), 'a focus() call is outside a layout effect');

  const good = `React.useLayoutEffect(() => { if (!open) return; setQ(''); setCursor(0);
    if (inputRef.current) inputRef.current.focus(); }, [open]);`;
  assert.equal(focusVerdict(good), null);
  assert.equal(resetVerdict(good), null);

  assert.equal(focusVerdict('const x = 1;'), 'the palette never focuses its input');
  // a bracket inside a string does not close the call early
  const stringy = `React.useLayoutEffect(() => { log(')'); el.focus(); }, []);`;
  assert.equal(focusVerdict(stringy), null);
});
