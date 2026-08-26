/* Walk every live surface against a running server (127.0.0.1:8177 serving the built
   app), assert the load-bearing honesty affordances, and screenshot each surface for
   eyeball review against the mockup. Run: node e2e/walk.mjs */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
import { mkdirSync } from 'node:fs';

const BASE = process.env.WB_URL || 'http://127.0.0.1:8177';
const SHOTS = new URL('./shots/', import.meta.url).pathname;
mkdirSync(SHOTS, { recursive: true });

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
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
check('the sheet can be magnified to be read', /the sheet/i.test(body) && /1:1/.test(body));

// Every room label must stay inside the room it names. The sheet fits each name by
// measuring it, so the guarantee can be checked the same way — and this is the assertion
// that would have caught BUTLER'S PANTRY drawn eleven feet long in a seven-foot room.
const spill = await page.evaluate(() => {
  const out = { rooms: 0, over: [] };
  for (const g of document.querySelectorAll('svg g')) {
    const ttl = g.firstElementChild;
    if (!ttl || ttl.tagName !== 'title') continue;
    const rect = g.querySelector('rect');
    if (!rect) continue;
    out.rooms += 1;
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
// a selector that matched nothing would pass this vacuously, which is the one way an
// honesty check can lie: the room count is asserted first
check('the sheet draws the record\'s rooms', spill.rooms >= 8);
check(`no room label leaves the room it names (${spill.rooms} rooms)`
  + (spill.over.length ? ' — ' + spill.over.join('; ') : ''), spill.over.length === 0);
// The caption offers a wall drag; until 26 Aug 2026 the handle was drawn with the rooms
// and the partition on that very wall line covered it, so the gesture could not be
// started. Press, raise the preview, come back and release — asserting the affordance
// exists without leaving the record changed for the checks below.
await page.locator('svg[role="img"] g rect').first().click({ position: { x: 4, y: 4 } }).catch(() => {});
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
  await page.mouse.click(room.x, room.y);
  await page.waitForTimeout(400);
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
  await page.mouse.move(h.x, h.y, { steps: 4 });
  await page.mouse.up();
  await page.waitForTimeout(1200);
  return preview;
})();
check('a wall handle can still be grasped through the loupe', handleLive > 0);
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
const plate = await page.evaluate(() => {
  const svg = document.querySelector('main svg[role="img"]');
  if (!svg) return { missing: true };
  const view = svg.getBoundingClientRect();
  const spans = [], out = { clipped: [], gap: 0, bands: 0 };
  for (const p of svg.querySelectorAll('path')) {
    const b = p.getBoundingClientRect();
    if (b.height < 0.05) continue;
    out.bands += 1;
    spans.push([b.top, b.bottom]);
    if (b.top < view.top - 1 || b.bottom > view.bottom + 1
        || b.left < view.left - 1 || b.right > view.right + 1) out.clipped.push(p.querySelector('title')?.textContent || '?');
  }
  spans.sort((a, b) => a[0] - b[0]);
  let end = spans.length ? spans[0][1] : 0;
  for (const [t, b] of spans) { out.gap = Math.max(out.gap, t - end); end = Math.max(end, b); }
  return out;
});
check('the order plate draws bands at all', plate.bands > 8);
check('the order stands as one stack — no gap between its assemblies', plate.gap < 2);
check('no member is drawn outside the plate' + (plate.clipped?.length ? ' — ' + plate.clipped.length : ''),
  (plate.clipped || []).length === 0);
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
