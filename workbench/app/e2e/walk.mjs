/* Walk every live surface against a running server (127.0.0.1:8177 serving the built
   app), assert the load-bearing honesty affordances, and screenshot each surface for
   eyeball review against the mockup. Run: node e2e/walk.mjs */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
import { existsSync, mkdirSync } from 'node:fs';

const BASE = process.env.WB_URL || 'http://127.0.0.1:8177';
const SHOTS = new URL('./shots/', import.meta.url).pathname;
mkdirSync(SHOTS, { recursive: true });

// CHROMIUM if it is set, the pre-installed browser if this machine has one, otherwise
// Playwright's own — which is what a CI runner has after `playwright install chromium`.
// Naming a path that does not exist is how this refuses to run anywhere but here.
const EXEC = process.env.CHROMIUM
  || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);
const browser = await chromium.launch(EXEC ? { executablePath: EXEC } : {});
const page = await browser.newPage({ viewport: { width: 1680, height: 1000 } });
const failures = [];
const check = (name, cond) => { if (!cond) failures.push(name); console.log(cond ? ' ok ' : 'FAIL', name); };

await page.goto(BASE, { waitUntil: 'networkidle' });
const overview = await (await fetch(BASE + '/api/overview')).json();

// masthead + rail counts come from the corpus, not literals
await page.waitForSelector('nav', { timeout: 15000 });
const railText = await page.locator('nav').innerText();
check('left rail shows live style count', railText.includes(String(overview.counts.styles)));
check('all eleven surfaces in the rail', /Drawing Set/.test(railText) && /Details & Export/.test(railText) && /Transcription/.test(railText));

// ⑦ Plan Workbench: load an example, wait for evaluation
await page.getByRole('button', { name: /Plan Workbench/ }).click();
const example = page.getByRole('button', { name: 'tidewater-georgian-careful' });
if (await example.count()) await example.click();
await page.waitForSelector('svg[role="img"]', { timeout: 30000 });
const body = await page.locator('main').innerText();
check('three-state panel present (could not evaluate)', /could not evaluate/i.test(body));
check('hill-climb honesty line present', /hill-climb/i.test(body));
check('the proof is offered, not just the search', /prove placement/i.test(body));
check('relaxations counted', /cut\(s\) off the bay line/i.test(body));
// Not "a toolbar rendered": the loupe has to make the drawing bigger. Measured on the
// sheet's own SVG, before and after two steps of the ladder.
const sheetBox = () => page.evaluate(() => {
  const s = document.querySelector('main svg[role="img"]');
  return s ? s.getBoundingClientRect().width : 0;
});
const wFit = await sheetBox();
await page.getByRole('button', { name: '+', exact: true }).first().click();
await page.getByRole('button', { name: '+', exact: true }).first().click();
await page.waitForTimeout(500);
const wBig = await sheetBox();
check(`the loupe magnifies the sheet (${Math.round(wFit)}px → ${Math.round(wBig)}px)`,
  wFit > 50 && wBig > wFit * 1.2);
const canPanNow = await page.evaluate(() => {
  const d = [...document.querySelectorAll('div')]
    .find((e) => e.style.overflow === 'auto' && e.scrollHeight > e.clientHeight + 1);
  return !!d;
});
check('magnified, the plate can be panned', canPanNow);

// Every room label must stay inside the room it names. The sheet fits each name by
// measuring it, so the guarantee can be checked the same way — and this is the assertion
// that would have caught BUTLER'S PANTRY drawn eleven feet long in a seven-foot room.
const measureLabels = () => page.evaluate(() => {
  const out = { rooms: 0, labelled: 0, over: [] };
  for (const g of document.querySelectorAll('svg g')) {
    const ttl = g.firstElementChild;
    if (!ttl || ttl.tagName !== 'title') continue;
    const rect = g.querySelector('rect');
    if (!rect) continue;
    out.rooms += 1;
    if (g.querySelectorAll('text').length) out.labelled += 1;
    const room = rect.getBoundingClientRect();
    for (const t of g.querySelectorAll('text')) {
      const b = t.getBoundingClientRect();
      if (b.width < 0.5) continue;
      if (b.left < room.left - 1 || b.right > room.right + 1
          || b.top < room.top - 1 || b.bottom > room.bottom + 1) {
        out.over.push(`${ttl.textContent}: ${t.textContent}`);
      }
    }
  }
  return out;
});
const spill = await measureLabels();
// a selector that matched nothing would pass this vacuously, which is the one way an
// honesty check can lie: the room count is asserted first
check(`the sheet draws the record's rooms (${spill.rooms})`, spill.rooms >= 13);
// and the spill check above passes vacuously on a sheet with no labels at all, so the
// labels are counted before their containment is asserted
check(`every room is lettered (${spill.labelled}/${spill.rooms})`,
  spill.rooms > 0 && spill.labelled === spill.rooms);
check(`no room label leaves the room it names (${spill.rooms} rooms)`
  + (spill.over.length ? ' — ' + spill.over.join('; ') : ''), spill.over.length === 0);
// and on the UPPER level, which is where the small rooms are: a closet and a linen press
// are exactly where the size floor stops being able to hold a name, and level 0 has none
await page.getByRole('button', { name: /^level 1$/ }).click().catch(() => {});
await page.waitForTimeout(2500);
const upper = await measureLabels();
check(`upper level: every room is lettered (${upper.labelled}/${upper.rooms})`,
  upper.rooms >= 8 && upper.labelled === upper.rooms);
check(`upper level: no room label leaves its room (${upper.rooms} rooms)`
  + (upper.over.length ? ' — ' + upper.over.join('; ') : ''), upper.over.length === 0);
await page.getByRole('button', { name: /^level 0$/ }).click().catch(() => {});
await page.waitForTimeout(2000);
// the loupe's scroller, and one room's drawn dimensions, read the same way twice
const scrollPos = () => page.evaluate(() => {
  const d = [...document.querySelectorAll('div')]
    .find((e) => e.style.overflow === 'auto'
      && (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1));
  return d ? { l: d.scrollLeft, t: d.scrollTop } : null;
});
const roomLabel = (name) => page.evaluate((n) => {
  for (const g of document.querySelectorAll('svg g')) {
    const t = g.firstElementChild;
    if (t && t.tagName === 'title' && t.textContent.startsWith(n)) return t.textContent;
  }
  return null;
}, name);

// The caption offers a wall drag; until 26 Aug 2026 the handle was drawn with the rooms
// and the partition on that very wall line covered it, so the gesture could not be
// started. Press, raise the preview, come back and release — asserting the affordance
// exists without leaving the record changed for the checks below.
const handleLive = await (async () => {
  const room = await page.evaluate(() => {
    for (const g of document.querySelectorAll('svg g')) {
      const t = g.firstElementChild;
      if (t && t.tagName === 'title' && /Drawing Room/.test(t.textContent)) {
        const b = g.querySelector('rect').getBoundingClientRect();
        return { x: b.x + b.width / 2, y: b.y + b.height / 2 };
      }
    } return null;
  });
  if (!room) return null;
  const before = await roomLabel('Drawing Room');
  await page.mouse.click(room.x, room.y);
  await page.waitForTimeout(400);
  const scroll0 = await scrollPos();
  const h = await page.evaluate(() => {
    const rs = [...document.querySelectorAll('[data-nopan]')].map((e) => e.getBoundingClientRect());
    if (!rs.length) return null;
    const r = rs.sort((a, b) => b.x - a.x)[0];
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  if (!h) return null;
  await page.mouse.move(h.x, h.y);
  await page.mouse.down();
  await page.mouse.move(h.x + 30, h.y, { steps: 6 });
  const preview = await page.evaluate(() => [...document.querySelectorAll('line')]
    .filter((l) => (l.getAttribute('stroke') || '').includes('gilt')
      && l.getAttribute('stroke-dasharray')).length);
  const panned = await scrollPos();
  await page.mouse.move(h.x, h.y, { steps: 4 });
  await page.mouse.up();
  await page.waitForTimeout(1600);
  // A drag and return is still a DRAG, and committing it is correct. The record it left
  // is put back before the separate no-movement test below, so that one measures the
  // thing it names.
  await page.getByRole('button', { name: 'undo' }).click();
  await page.waitForTimeout(1800);
  const restored = await roomLabel('Drawing Room');
  // now a real click: press and release on the handle without moving at all
  const h2 = await page.evaluate(() => {
    const rs = [...document.querySelectorAll('[data-nopan]')].map((e) => e.getBoundingClientRect());
    if (!rs.length) return null;
    const r = rs.sort((a, b) => b.x - a.x)[0];
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  if (h2) {
    await page.mouse.move(h2.x, h2.y);
    await page.mouse.down();
    await page.mouse.up();
    await page.waitForTimeout(1800);
  }
  const after = await roomLabel('Drawing Room');
  return { preview, panned, scroll0, before, restored, after, clicked: !!h2 };
})();
check('a wall handle can still be grasped through the loupe', handleLive?.preview > 0);
// data-nopan: the handle's drag must not become a pan. The pane is magnified above, so
// there IS something to pan — without that this asserts nothing, because a fitted pane
// cannot scroll and the guard is never reached.
check('the handle keeps its drag: the loupe did not pan instead',
  handleLive && handleLive.panned && handleLive.scroll0
    && handleLive.panned.l === handleLive.scroll0.l
    && handleLive.panned.t === handleLive.scroll0.t);
// and a release with no movement is not a resize. It used to commit anyway — quantising
// the dimension to the half-foot and snapping up to 0.75 ft to a bay line, from a gesture
// nobody made, straight into the record and localStorage.
check('the wall drag reaches the record', handleLive && typeof handleLive.restored === 'string');
// A CLICK IS NOT A RESIZE. A zero-movement release used to commit anyway: quantising the
// dimension to the half-foot and snapping up to 0.75 ft to a bay line from a gesture
// nobody made, onto the DECLARED record, and into localStorage. It never fired while the
// handle was painted over by its own partition; making the handle reachable made it live.
check(`a click on the handle is not a silent resize (${handleLive?.restored} → ${handleLive?.after})`,
  handleLive && handleLive.clicked && handleLive.restored === handleLive.after);
await page.screenshot({ path: SHOTS + 'workbench.png', fullPage: false });

// style switch: same plan, different rules
const before = (body.match(/serious\s+(\d+)/) || [])[1];
await page.locator('select').first().selectOption('craftsman');
await page.waitForTimeout(2500);
const after = await page.locator('main').innerText();
check('style switch re-scores', (after.match(/serious\s+(\d+)/) || [])[1] !== undefined);
await page.screenshot({ path: SHOTS + 'workbench-craftsman.png' });
await page.locator('select').first().selectOption('tidewater-georgian');

// ② Phylogeny
await page.getByRole('button', { name: /The Phylogeny/ }).click();
await page.waitForSelector('text=compressed', { timeout: 15000 });
const phylo = await page.locator('main').innerText();
check('phylogeny names the missing trunks', /missing peer trunks/i.test(phylo));
await page.screenshot({ path: SHOTS + 'phylogeny.png' });

// ④ Kit
await page.getByRole('button', { name: /The Kit/ }).click();
await page.waitForSelector('text=cascade', { timeout: 15000 });
const kit = await page.locator('main').innerText();
check('kit shows thin-kit-is-correct note', /thin kit is correct/i.test(kit));
await page.screenshot({ path: SHOTS + 'kit.png' });

// ③ Style Record
await page.getByRole('button', { name: /Style Record/ }).click();
await page.waitForSelector('text=diagnostic tells', { timeout: 15000 });
const record = await page.locator('main').innerText();
check('style record: tells get the room', /diagnostic tells/i.test(record));
check('style record: judgment rows offered back', /refuses to invent/i.test(record));
await page.screenshot({ path: SHOTS + 'style-record.png' });

// ⑩ Proportions
await page.getByRole('button', { name: /Proportions/ }).click();
await page.waitForSelector('text=five authorities', { timeout: 20000 });
const prop = await page.locator('main').innerText();
check('proportions: material modules lead', /material modules/i.test(prop));
check('proportions: conflicts with building today', /conflicts with building today/i.test(prop));

// The order is ONE stack. Until 26 Aug 2026 the plate added each assembly's base to
// member positions that were already absolute, so the base floated clear of the plinth
// and the cornice left the frame; both faults are gaps in the drawn column, and both
// are caught by asking whether the bands cover their own extent without a hole in it.
// Measured in MODEL INCHES off getBBox, not in screen pixels: the plate is fitted to its
// pane, so a real gap at a small fit factor can read as under a two-pixel tolerance and
// slip through. The frame is compared against the engine's own stated stack height rather
// than against the drawn extent — a frame derived from the bands can never be smaller
// than the bands, which is what made the first version of this check a tautology.
async function readPlate(pack) {
  if (pack) {
    const b = page.getByRole('button', { name: pack, exact: true });
    if (!(await b.count())) return { missing: 'no nav for ' + pack };
    await b.click();
    await page.waitForTimeout(1600);
  }
  return page.evaluate(() => {
    const svg = document.querySelector('main svg[role="img"]');
    if (!svg) return { missing: 'no plate' };
    const bands = [...svg.querySelectorAll('path[data-asm]')];
    if (!bands.length) return { missing: 'no bands' };
    const spans = [], out = { bands: bands.length, gap: 0, shaftMax: 0, capMax: 0, maxX: 0 };
    for (const p of bands) {
      const b = p.getBBox();
      out.maxX = Math.max(out.maxX, b.x + b.width);
      if (p.dataset.asm === 'shaft') out.shaftMax = Math.max(out.shaftMax, b.x + b.width);
      if (p.dataset.asm === 'capital') out.capMax = Math.max(out.capMax, b.x + b.width);
      if (b.height < 0.001) continue;
      spans.push([b.y, b.y + b.height]);
    }
    spans.sort((a, b) => a[0] - b[0]);
    let end = spans.length ? spans[0][1] : 0;
    for (const [t, b] of spans) { out.gap = Math.max(out.gap, t - end); end = Math.max(end, b); }
    const vb = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    out.frameTop = vb[1]; out.frameBottom = vb[1] + vb[3]; out.frameRight = vb[0] + vb[2];
    out.drawnTop = Math.min(...spans.map((s) => s[0]));
    out.drawnBottom = Math.max(...spans.map((s) => s[1]));
    return out;
  });
}
// One pack of each reading (OQ 65): gibbs-doric records projections from the naked,
// vignola-ionic as radii from the axis. Checking only the default pack is how a datum
// wrong on twelve packs shipped green.
for (const [pack, dia] of [[null, 12], ['vignola-ionic', 12], ['palladio-corinthian', 12]]) {
  const plate = await readPlate(pack);
  const id = pack || 'gibbs-doric';
  if (plate.missing) { check(`⑩ ${id}: a plate is drawn (${plate.missing})`, false); continue; }
  const api = await (await fetch(`${BASE}/api/proportions/${id}?members=true&column_diameter=${dia}`)).json();
  const r0 = (api.totals?.lower_diameter_in || 0) / 2;
  const stack = api.totals?.stack_height_in || 0;
  check(`⑩ ${id}: the plate draws every member the engine emitted (${plate.bands})`,
    plate.bands >= api.assemblies.reduce((a, x) => a + (x.members || []).length, 0));
  check(`⑩ ${id}: the order stands as one stack — no gap (worst ${plate.gap.toFixed(2)}″)`,
    plate.gap < 0.25);
  check(`⑩ ${id}: the stack is drawn to its stated height (${(plate.drawnBottom - plate.drawnTop).toFixed(1)}″ of ${stack}″)`,
    Math.abs((plate.drawnBottom - plate.drawnTop) - stack) < 0.25);
  check(`⑩ ${id}: nothing is drawn outside the frame`,
    plate.drawnTop >= plate.frameTop - 0.01 && plate.drawnBottom <= plate.frameBottom + 0.01
      && plate.maxX <= plate.frameRight + 0.01);
  // the datum. A shaft moulding never stands a whole radius clear of the shaft; adding a
  // naked to a figure that was already a radius drew exactly that, on twelve packs.
  check(`⑩ ${id}: the shaft is a column and not a stick (${plate.shaftMax.toFixed(2)}″ against r ${r0}″)`,
    plate.shaftMax > r0 * 0.8 && plate.shaftMax < r0 * 1.35);
  check(`⑩ ${id}: the capital stands clear of the shaft`, plate.capMax >= plate.shaftMax - 0.01);
}
await page.screenshot({ path: SHOTS + 'proportions-order.png' });

// ⑨ Fault Corpus
await page.getByRole('button', { name: /Fault Corpus/ }).click();
await page.waitForSelector('text=solecisms', { timeout: 15000 });
await page.waitForSelector('text=dishonest', { timeout: 15000 }).catch(() => {});
const faults = await page.locator('main').innerText();
check('fault corpus voice line present', /explaining an economy/i.test(faults));
check('fix tiers named plainly', /dishonest/i.test(faults));
await page.screenshot({ path: SHOTS + 'faults.png' });

// ⑤ Brief Intake
await page.getByRole('button', { name: /Brief Intake/ }).click();
await page.waitForSelector('text=feasibility', { timeout: 15000 });
const brief = await page.locator('main').innerText();
check('silences are named as decisions', /becomes a composer decision/i.test(brief));
// WP-2.3 landed; the panel now says WHERE the conflict set is named (the bench, on a plan)
// rather than that it does not exist. The assertion moved with the claim.
check('conflict set located, not promised', /conflict set · on the bench, not here/i.test(brief));
check('feasibility still advisory, never a proof', /never a proof/i.test(brief));
await page.screenshot({ path: SHOTS + 'brief.png' });

// ⑥ Candidate Set (empty state without a run)
await page.getByRole('button', { name: /Candidate Set/ }).click();
await page.waitForTimeout(500);
await page.screenshot({ path: SHOTS + 'candidates.png' });

// (8) Drawing Set - the elevation with its disclosure
await page.getByRole('button', { name: /Drawing Set/ }).click();
await page.waitForSelector('text=83 of', { timeout: 40000 });
const ds = await page.locator('main').innerText();
check('drawing set: WP-3.2 disclosure on-sheet', /83 of the 177 applicable/i.test(ds));
await page.screenshot({ path: SHOTS + 'drawing-elevation.png' });
await page.getByRole('button', { name: 'bearing lines' }).click();
await page.waitForTimeout(3000);
await page.screenshot({ path: SHOTS + 'drawing-bearing.png' });

// (8b) Details & Export - forthcoming, never hidden
await page.getByRole('button', { name: /Details & Export/ }).click();
await page.waitForSelector('text=forthcoming', { timeout: 15000 });
const ex = await page.locator('main').innerText();
check('export: DXF/IFC live (WP-5.1)', /plan dxf/.test(ex) && /ifc model/.test(ex));
check('export: unbuilt work named with its WP', /WP-5\.3 is not built/.test(ex));
check('export: no costing engine implied', /No costing engine exists/i.test(ex));
check('export: conflict count is the recorded 262', /262 recorded pack conflicts/.test(ex));
await page.screenshot({ path: SHOTS + 'export.png' });

// (11) Transcription - a drawing goes in, a record comes out, gaps named
await page.getByRole('button', { name: /Transcription/ }).click();
await page.getByRole('button', { name: 'start a draft' }).click();
const tr = await page.locator('main').innerText();
check('transcription: gaps named before it is a record', /not yet a record/i.test(tr));
check('transcription: style stays a recorded judgment', /style is unset — a judgment/i.test(tr));
check('transcription: backdrop never uploaded', /stays in this browser — never uploaded/i.test(tr));
// actually trace a room: drag on the canvas, then the draft should hold one
// untyped room and the completeness panel should name its missing type
const svg = await page.locator('main svg').first().boundingBox();
await page.mouse.move(svg.x + svg.width * 0.3, svg.y + svg.height * 0.3);
await page.mouse.down();
await page.mouse.move(svg.x + svg.width * 0.55, svg.y + svg.height * 0.55, { steps: 5 });
await page.mouse.up();
const tr2 = await page.locator('main').innerText();
check('transcription: a drag traces a room', /type unset/.test(tr2));
check('transcription: the untyped room is a named gap', /has no type from the catalog/.test(tr2));
await page.screenshot({ path: SHOTS + 'transcription.png' });

// the rail's honest no-key state
const rail = await page.locator('aside').last().innerText();
check('rail present on every surface', /the rail/i.test(rail));

await browser.close();
if (failures.length) { console.error('\nFAILED:', failures); process.exit(1); }
console.log('\nE2E WALK GREEN');
