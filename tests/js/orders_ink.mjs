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
      id, innerHTML: '', textContent: '', value: '', style: {}, dataset: {}, scrollTop: 0,
      addEventListener() {}, querySelectorAll() { return []; },
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
                   S.ped = __c.ped; S.ghost = null; S.selAsm = null; draw();`, ctx);
  out[c.key] = { svg: el('canvas').innerHTML, info: el('info').innerHTML, meta: el('meta').innerHTML };
}
// the controls a reader can reach, as built at load: which packs any button pair can select
vm.runInContext('buildControls();', ctx);
out.__reachable = vm.runInContext(
  'DATA.authorities.flatMap(a => DATA.orders.filter(o => has(a.id, o)).map(o => packId(a.id, o)))', ctx);
process.stdout.write(JSON.stringify(out));
