/* Fitting a room's name inside the room.

   A plan label that runs through the wall it is naming is not a label, and the sheet
   used to set every room's name on one line at a size derived from the room's width
   alone — so BUTLER'S PANTRY, seven and a half feet wide, was drawn eleven feet long
   and crossed two partitions to get there. The rule here is the draughtsman's: break
   the name across lines before shrinking it, shrink it only as far as it stays
   readable, and never let it leave the room.

   Widths are measured against the sheet's own face rather than guessed from character
   counts — EB Garamond's capitals are narrow, and a guess wide enough to be safe for
   'W' would break lines that fit. The canvas is a measuring instrument only; nothing is
   drawn on it. Before the webfont arrives the fallback serif answers instead, so the
   first paint can be a few percent out; `useFontMetrics` re-renders once the real face
   is ready and the fit is then exact. */
import React from 'react';

const FACE = '"EB Garamond","Iowan Old Style",Georgia,serif';
const REF = 100;                 // measure at 100px and scale — one measurement per string
let ctx = null;
const cache = new Map();

/* The cache is bounded. `balance` measures every candidate joined LINE, so a name of W
   words mints O(W²) distinct keys — harmless for 'Butler's Pantry', an unbounded retained
   string for anything pathological. Oldest-out at the cap; a Map iterates in insertion
   order, which is all the eviction this needs. */
const CACHE_CAP = 600;

function advance(text) {
  // width in ems of the string set at font-size 1, letter-spacing excluded
  if (cache.has(text)) return cache.get(text);
  let w;
  if (ctx === null && typeof document !== 'undefined' && document.createElement) {
    const c = document.createElement('canvas');
    ctx = (c.getContext && c.getContext('2d')) || false;
  }
  if (ctx) {
    ctx.font = `${REF}px ${FACE}`;
    w = ctx.measureText(text).width / REF;
  } else {
    w = text.length * 0.66;      // no canvas (a test renderer): the conservative guess
  }
  if (cache.size >= CACHE_CAP) cache.delete(cache.keys().next().value);
  cache.set(text, w);
  return w;
}

/* SVG letter-spacing is added to EVERY glyph's advance, the last one included — which is
   why a centred, letterspaced string sits half a space left of where it looks like it
   should. `fitLabel`/`fitLine` return `track` already multiplied by the fitted size, so
   the caller adds `track / 2` back to x. Stated here because it is the one piece of this
   module's contract that lives at the call site. */

/* Split words into exactly n lines so the widest line is as narrow as it can be.
   Rooms are named in two or three words; the search over break points is exhaustive
   and costs nothing at this size. */
function balance(words, n, track) {
  if (n === 1) return [words.join(' ')];
  if (n > words.length) return null;
  let best = null;
  const cuts = new Array(n - 1);
  const width = (s) => advance(s) + track * s.length;
  const walk = (depth, start) => {
    if (depth === n - 1) {
      const lines = [];
      let prev = 0;
      for (const c of cuts) { lines.push(words.slice(prev, c).join(' ')); prev = c; }
      lines.push(words.slice(prev).join(' '));
      const widest = Math.max(...lines.map(width));
      if (!best || widest < best.widest) best = { lines, widest };
      return;
    }
    for (let c = start + 1; c <= words.length - (n - 1 - depth); c++) {
      cuts[depth] = c;
      walk(depth + 1, c);
    }
  };
  walk(0, 0);
  return best ? best.lines : null;
}

/* Fit `text` into a box `maxW` × `maxH` (model units).

   Returns { lines, size, track, height }. The fewest lines that hold the preferred size
   wins; failing that, whichever arrangement can be set largest. `min` is a floor, not a
   target: below it the lettering stops being a label, so the label is set at the floor
   and allowed to be the widest thing in the room rather than being silently dropped —
   a name the reader can see is cramped beats a room with no name at all. */
/* The exhaustive split is C(W-1, n-1) arrangements each costed over all W words — O(W³)
   at three lines. Nothing bounds a room's name: a record can be pasted, imported from the
   Transcription surface, or fetched, and 400 words freeze this tab for over a second on
   the main thread with no way to cancel. Past the cap the name is chunked rather than
   balanced — linear, still drawn whole, still shrunk to fit. */
const MAX_WORDS = 12;

export function fitLabel(text, maxW, maxH, opt) {
  const { preferred = 1.25, min = 0.62, track = 0.3, lead = 1.24, maxLines = 3 } = opt || {};
  let words = String(text).trim().split(/\s+/).filter(Boolean);
  if (!words.length) return null;
  if (words.length > MAX_WORDS) {
    const k = Math.ceil(words.length / maxLines);
    words = Array.from({ length: Math.ceil(words.length / k) },
      (_, i) => words.slice(i * k, i * k + k).join(' '));
  }
  const cap = Math.max(1, Math.min(maxLines, words.length));
  let best = null;
  for (let n = 1; n <= cap; n++) {
    const lines = balance(words, n, track);
    if (!lines) continue;
    const widest = Math.max(...lines.map((l) => advance(l) + track * l.length));
    const byWidth = maxW / widest;
    const byHeight = maxH / (n * lead);
    const size = Math.min(preferred, byWidth, byHeight);
    if (!best || size > best.size + 1e-6) best = { lines, size, n };
    if (size >= preferred - 1e-6) break;         // fewest lines at full size: done
  }
  if (!best) return null;
  const size = Math.max(min, best.size);
  return { lines: best.lines, size, track: track * size, lead: size * lead,
           height: best.lines.length * size * lead };
}

/* Shrink a single line (a dimension string) until it fits, never wrapping it: a
   dimension broken across two lines reads as two dimensions. */
export function fitLine(text, maxW, opt) {
  const { preferred = 0.9, min = 0.5, track = 0.12 } = opt || {};
  const unit = advance(text) + track * text.length;
  const size = Math.max(min, Math.min(preferred, maxW / unit));
  // `width` so a caller can put a mark BESIDE the fitted line instead of inside it.
  // Anything added to the string shrinks the fit until the line drops out of narrow
  // rooms, which is what happened to OQ 55's void disclosure and what
  // tests/test_drawn_labels.py has frozen the Python renderer's version of this against.
  return { text, size, track: track * size, width: unit * size };
}

/* The webfont arrives after the first paint; a measurement taken before it lands is
   taken against the fallback. One re-render when the face is ready makes every fit
   exact, and the cache is dropped so the stale widths cannot survive it. */
export function useFontMetrics() {
  const [, bump] = React.useState(0);
  React.useEffect(() => {
    if (typeof document === 'undefined' || !document.fonts) return undefined;
    let live = true;
    const settle = () => { if (live) { cache.clear(); bump((n) => n + 1); } };
    if (document.fonts.ready) document.fonts.ready.then(settle);
    document.fonts.addEventListener('loadingdone', settle);
    return () => { live = false; document.fonts.removeEventListener('loadingdone', settle); };
  }, []);
}
