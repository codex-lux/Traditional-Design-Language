// dist/orders.html's own scripts, run in node:vm for the census (WP-14.1).
//
// The orders page draws with JavaScript that exists nowhere else: a port of the engine's stack and
// dimension(), the scaling of Python's geometry, the flute hint and the info panel. A census that
// asked Python what the page SHOULD draw would be checking Python against itself, so this runs the
// COMMITTED page's scripts, byte for byte, against a stub DOM that records what they write. No npm
// package is needed and none may be: `node` alone.
//
//   node tests/js/orders_ink.mjs <page.html>  < cases.json  > out.json
//
// cases.json is a list of {key, auth, order, diameter, ped}. Out: {key: {svg, info, meta}}, where
// `svg` is exactly what draw() assigned to #canvas.innerHTML.
import fs from 'node:fs';
import vm from 'node:vm';

const page = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length < 3) throw new Error(`expected the page's three inline scripts, found ${scripts.length}`);

const els = new Map();
function el(id) {
  if (!els.has(id)) {
    els.set(id, {
      // listeners are KEPT (WP-14.2), so reachability can click the buttons the page rendered
      id, innerHTML: '', textContent: '', value: '', style: {}, dataset: {}, scrollTop: 0, _l: {},
      addEventListener(type, fn) { this._l[type] = fn; }, querySelectorAll() { return []; },
      getBoundingClientRect() { return { top: 0, left: 0, width: 0, height: 0 }; },
    });
  }
  return els.get(id);
}
const stage = { clientHeight: 900, clientWidth: 1400 };
const document = {
  getElementById: el,
  querySelector: (sel) => (sel === 'section.stage' ? stage : el(sel)),
};
const ctx = vm.createContext({ document, addEventListener() {}, innerWidth: 1600, innerHeight: 1000,
  console, Math, JSON, Set, Map });
for (const s of scripts) vm.runInContext(s, ctx);
const snapshot = () => vm.runInContext('JSON.stringify({order:S.order, auth:S.auth, pid:S.pid})', ctx);
const LOADED = snapshot();          // the state a reader arrives in, before any case moves it

let raw = '';
process.stdin.setEncoding('utf8');
for await (const chunk of process.stdin) raw += chunk;
const out = {};
// A case may carry `patch`, JavaScript run in the page's own context before it draws: the way
// a branch the corpus never reaches (an invariant the engine could not judge) is DRIVEN rather
// than left green by absence. Patched cases run LAST, because a patch mutates the page's data.
const all = JSON.parse(raw);
for (const c of [...all.filter((x) => !x.patch), ...all.filter((x) => x.patch)]) {
  ctx.__c = c;
  if (c.patch) vm.runInContext(c.patch, ctx);
  vm.runInContext(`S.auth = __c.auth; S.order = __c.order; S.diameter = __c.diameter;
                   S.ped = __c.ped; S.pid = null; S.ghost = null; S.selAsm = null; draw();`, ctx);
  out[c.key] = { svg: el('canvas').innerHTML, info: el('info').innerHTML, meta: el('meta').innerHTML };
}
/* WHICH PACKS A READER CAN REACH, found by CLICKING (WP-14.2). This used to read the grid's own
   has() over DATA.authorities x DATA.orders -- the page's opinion of its controls, which is exactly
   what could not see two packs that no pair of buttons names. Now: from the state the page loads
   in, click every button each control actually RENDERED, through the listener the page itself
   attached, disabled ones included (the page's own guard refuses those), and record which pack
   draw() then drew -- read off the drawing's `data-pack`, not off the state. Breadth first over the
   states the clicks reach, until no click reaches a new one. */
function rendered(html) {
  return [...html.matchAll(/<button\b([^>]*)>/g)].map((m) => {
    const dataset = {};
    for (const a of m[1].matchAll(/\bdata-([a-z]+)="([^"]*)"/g)) dataset[a[1]] = a[2];
    return { dataset, disabled: /\sdisabled\b/.test(m[1]) };
  });
}
function restore(st) {
  ctx.__st = st;
  vm.runInContext('Object.assign(S, JSON.parse(__st)); S.ghost = null; buildControls(); draw();', ctx);
}
const drawnPack = () => (/data-pack="([^"]*)"/.exec(el('canvas').innerHTML) || [])[1] || null;
const reached = new Set(), seen = new Set([LOADED]), queue = [LOADED];
while (queue.length) {
  const st = queue.shift();
  restore(st);
  reached.add(drawnPack());
  for (const seg of ['orderseg', 'authseg', 'otherseg']) {
    restore(st);
    const buttons = rendered(el(seg).innerHTML);
    for (const b of buttons) {
      restore(st);
      const click = el(seg)._l.click;
      if (!click) break;
      click({ target: { closest: () => b } });
      reached.add(drawnPack());
      const next = snapshot();
      if (!seen.has(next)) { seen.add(next); queue.push(next); }
    }
  }
}
out.__reachable = [...reached].filter(Boolean).sort();
out.__states = seen.size;
process.stdout.write(JSON.stringify(out));
