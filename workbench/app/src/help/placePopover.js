/* WHERE A DEFINITION'S POPOVER GOES, AS ARITHMETIC (WP-14.6, PRD §I.1 and §K).

   A `Term` opens a non-modal popover beside the word it defines. Where it lands is pure geometry
   over three rectangles — the word, the popover, the visible viewport — and it is written here, with
   no DOM, so every edge case can be driven under `node --test` at the laptop size a reader actually
   has (1280 x 720) instead of being discovered in a browser. No tooltip library: PRD §J.4 refuses
   one, and the whole rule is a dozen lines.

   THE RULE. Below the word by default. Above it when the popover would run off the bottom AND there
   is more room above than below — a popover that fits nowhere goes where it fits best rather than
   flipping to a worse side. Horizontally it starts at the word's left edge and is clamped into the
   viewport less `margin`, so a word at the right edge opens leftward rather than off-screen. A
   popover wider than the viewport allows is given `maxWidth` (the viewport less both margins) and a
   popover taller than the room on its chosen side is given `maxHeight`, so it scrolls inside itself
   rather than covering the word it explains. Both are `null` when not needed. Finally the rectangle
   is clamped into the viewport, which only moves it when the WORD itself is out of view.

   Coordinates are the VISUAL viewport's (a pinch-zoomed page has `x`/`y` offsets), which is the
   caller's to supply: `window.visualViewport` gives `offsetLeft`/`offsetTop`/`width`/`height`.

   Pure, and imports nothing. */

const num = (v, d = 0) => (typeof v === 'number' && Number.isFinite(v) ? v : d);
const clamp = (v, lo, hi) => (hi < lo ? lo : Math.min(Math.max(v, lo), hi));

export function placePopover({ anchor, popover, viewport, gap = 6, margin = 8 } = {}) {
  const a = { x: num(anchor?.x), y: num(anchor?.y), w: num(anchor?.width), h: num(anchor?.height) };
  const p = { w: Math.max(0, num(popover?.width)), h: Math.max(0, num(popover?.height)) };
  const v = { x: num(viewport?.x), y: num(viewport?.y), w: num(viewport?.width), h: num(viewport?.height) };

  const availW = Math.max(0, v.w - 2 * margin);
  const maxWidth = p.w > availW ? availW : null;
  const w = Math.min(p.w, availW);
  const left = clamp(a.x, v.x + margin, v.x + v.w - margin - w);

  const belowTop = a.y + a.h + gap;
  const roomBelow = (v.y + v.h - margin) - belowTop;
  const aboveBottom = a.y - gap;
  const roomAbove = aboveBottom - (v.y + margin);

  const side = p.h <= roomBelow || roomAbove <= roomBelow ? 'below' : 'above';
  const room = Math.max(0, side === 'below' ? roomBelow : roomAbove);
  const maxHeight = p.h > room ? room : null;
  const h = Math.min(p.h, room);

  const wanted = side === 'below' ? belowTop : aboveBottom - h;
  const top = clamp(wanted, v.y + margin, v.y + v.h - margin - h);

  return { left, top, side, maxWidth, maxHeight };
}
