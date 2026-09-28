/* The Transcription canvas's geometry, with no React in it (WP-14.4).

   The canvas draws a person's own tracing: every traced room at the draft's own feet, a 5 ft
   reference grid, and the scanned backdrop at the width the person states and the height its own
   aspect gives. None of it is a reading of a researched record -- the draft is the person's -- so
   the one fidelity question is that the canvas draws exactly what the draft holds, in the model
   frame every other plate uses (x east, y north, screen y flipped). That was true and nothing held
   it; these are the numbers `surfaces/Transcription.jsx` draws, lifted so `node --test` and the
   census (row TR1) can. */

/* The canvas extent in feet: every traced room with a margin, the backdrop, and a floor. */
export function canvasSize(rooms, backdrop) {
  const W = Math.max(44, ...rooms.map((r) => r.x + r.w + 4), backdrop?.wFt + 2 || 0);
  const H = Math.max(32, ...rooms.map((r) => r.y + r.h + 4), backdrop?.hFt + 2 || 0);
  return { W, H };
}

/* A traced room's rectangle on the canvas: its own feet, y flipped. */
export function roomRect(r) {
  return { x: r.x, y: -r.y - r.h, width: r.w, height: r.h };
}

/* The backdrop's box: the stated width, and the height the image's own aspect gives
   (`hFt` is always `wFt * ratio`), standing on the canvas origin. */
export function backdropBox(b) {
  return { x: 0, y: -b.hFt, width: b.wFt, height: b.hFt };
}

/* The reference grid: a line every 5 ft, every 10 ft heavier. */
export function gridSteps(W, H) {
  const v = [], h = [];
  for (let g = 0; g <= W; g += 5) v.push({ at: g, heavy: g % 10 === 0 });
  for (let g = 0; g <= H; g += 5) h.push({ at: g, heavy: g % 10 === 0 });
  return { v, h };
}
