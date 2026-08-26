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

// The rail is addressed by its accessible name from here on, and every click into it is
// scoped to it: since WP-5.6 the Overview offers doors carrying the same labels, so an
// unscoped getByRole would match two elements and Playwright would refuse both.
await page.waitForSelector('nav[aria-label="surfaces"]', { timeout: 15000 });
const rail = page.locator('nav[aria-label="surfaces"]');
const railText = await rail.innerText();
check('left rail shows live style count', railText.includes(String(overview.counts.styles)));
check('all twelve surfaces in the rail', /Overview/.test(railText) && /Drawing Set/.test(railText)
  && /Details & Export/.test(railText) && /Transcription/.test(railText));
// The work-package numerals are gone: they read as an ordering while meaning build order,
// went 2,3,4,9,10,5… and two surfaces both wore ⑧.
check('no work-package numerals in the rail', !/[②③④⑤⑥⑦⑧⑨⑩⑪]/.test(railText));

// ⓪ Overview: the landing, and every claim on it comes from /api/overview
check('a cold load lands on the Overview', new URL(page.url()).hash === '' || /#\/$/.test(page.url()));
const ovText = await page.locator('main').innerText();
check('the corpus describes itself in its own words',
  ovText.includes(overview.what_this_is.slice(0, 60)));
check('the inventory is the corpus inventory',
  ovText.includes(String(overview.counts.faults)) && ovText.includes(String(overview.counts.rooms)));
check('the ontology version is stated', ovText.includes(overview.ontology_version));
check('the search invitation is on the landing',
  await page.locator('main').getByRole('button', { name: /Search the corpus/ }).count() > 0);
await page.screenshot({ path: SHOTS + 'overview.png', fullPage: false });

// ⑦ Plan Workbench: load an example, wait for evaluation
// The walk used to land here on page load, so this surface was already mounted by the
// time it was addressed. It is reached by a click now, and only the surface in view is
// constructed — so wait for its own furniture before reaching for it.
await rail.getByRole('button', { name: /Plan Workbench/ }).click();
const example = page.getByRole('button', { name: 'tidewater-georgian-careful' });
await example.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
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

// style switch: same plan, different rules.
// Driven through the combobox that replaced the 164-option <select> in WP-5.6 — typing a
// few letters, which is the whole reason it replaced it.
const pickStyle = async (name) => {
  const box = page.locator('main').getByRole('combobox', { name: /different style/i });
  await box.click();
  await box.fill(name);
  await page.waitForTimeout(400);
  await page.locator('[role="option"]').first().click();
};
await pickStyle('craftsman');
await page.waitForTimeout(2500);
const after = await page.locator('main').innerText();
check('style switch re-scores', (after.match(/serious\s+(\d+)/) || [])[1] !== undefined);
check('no 164-option select survives on the bench', await page.locator('main select').count() === 0);
await page.screenshot({ path: SHOTS + 'workbench-craftsman.png' });
await pickStyle('tidewater-georgian');
await page.waitForTimeout(1500);

// ② Phylogeny
await rail.getByRole('button', { name: /The Phylogeny/ }).click();
await page.waitForSelector('text=compressed', { timeout: 15000 });
const phylo = await page.locator('main').innerText();
check('phylogeny names the missing trunks', /missing peer trunks/i.test(phylo));
await page.screenshot({ path: SHOTS + 'phylogeny.png' });

// ④ Kit
await rail.getByRole('button', { name: /The Kit/ }).click();
// Wait for the CLAIM being asserted, not for a heading that renders before it. "cascade" is
// the section header and is on screen the moment the surface mounts; the note comes from
// /api/kit/{style}/cascade a round trip later. Locally that gap is invisible and this passed
// every run; on a CI runner it lost the race and failed the one assertion below. A wait that
// does not wait for the thing under test is a flake with a plausible-looking line number.
await page.waitForSelector('text=thin kit is correct', { timeout: 20000 });
const kit = await page.locator('main').innerText();
check('kit shows thin-kit-is-correct note', /thin kit is correct/i.test(kit));
await page.screenshot({ path: SHOTS + 'kit.png' });

// ③ Style Record
await rail.getByRole('button', { name: /Style Record/ }).click();
await page.waitForSelector('text=diagnostic tells', { timeout: 15000 });
const record = await page.locator('main').innerText();
check('style record: tells get the room', /diagnostic tells/i.test(record));
check('style record: judgment rows offered back', /refuses to invent/i.test(record));
await page.screenshot({ path: SHOTS + 'style-record.png' });

// ⑩ Proportions
await rail.getByRole('button', { name: /Proportions/ }).click();
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
await rail.getByRole('button', { name: /Fault Corpus/ }).click();
await page.waitForSelector('text=solecisms', { timeout: 15000 });
await page.waitForSelector('text=dishonest', { timeout: 15000 }).catch(() => {});
const faults = await page.locator('main').innerText();
check('fault corpus voice line present', /explaining an economy/i.test(faults));
check('fix tiers named plainly', /dishonest/i.test(faults));
await page.screenshot({ path: SHOTS + 'faults.png' });

// ⑤ Brief Intake
await rail.getByRole('button', { name: /Brief Intake/ }).click();
await page.waitForSelector('text=feasibility', { timeout: 15000 });
const brief = await page.locator('main').innerText();
check('silences are named as decisions', /becomes a composer decision/i.test(brief));
// WP-2.3 landed; the panel now says WHERE the conflict set is named (the bench, on a plan)
// rather than that it does not exist. The assertion moved with the claim.
check('conflict set located, not promised', /conflict set · on the bench, not here/i.test(brief));
check('feasibility still advisory, never a proof', /never a proof/i.test(brief));
await page.screenshot({ path: SHOTS + 'brief.png' });

// ⑥ Candidate Set (empty state without a run)
await rail.getByRole('button', { name: /Candidate Set/ }).click();
await page.waitForTimeout(500);
await page.screenshot({ path: SHOTS + 'candidates.png' });

// (8) Drawing Set - the elevation with its disclosure
// Scoped to the rail: since WP-5.6 the Overview offers doors carrying the same labels, so an
// unscoped getByRole matches two elements and Playwright refuses both.
await rail.getByRole('button', { name: /Drawing Set/ }).click();
// The disclosure is asserted by its CLAIM, not by a number. It used to wait on the literal
// "83 of" — which was tidewater-georgian's own fault-coverage count (wp-3.2's report says so
// in as many words) printed unqualified beneath a Craftsman or Charleston elevation, and
// corpus-wide it was 175 rather than 177 besides. Pinning it here is what kept it shipping.
await page.waitForSelector('text=photograph-measurable', { timeout: 40000 });
const ds = await page.locator('main').innerText();
check('drawing set: WP-3.2 disclosure on-sheet',
  /photograph-measurable fault corpus/i.test(ds) && /no model at this layer yet/i.test(ds));
check('drawing set: the disclosure states the unjudged rule, not a borrowed count',
  /absent from the measurements rather than reported as zero/i.test(ds));
check('drawing set: no per-style fault count is printed as if it were universal',
  !/\b\d+ of the \d+ applicable/i.test(ds));
await page.screenshot({ path: SHOTS + 'drawing-elevation.png' });
// A sheet kind is one of a set, so it is a radio now, not a button — the chips that pick
// between alternatives say so to a screen reader since WP-5.6.
await page.getByRole('radio', { name: 'bearing lines' }).click();
await page.waitForTimeout(3000);
await page.screenshot({ path: SHOTS + 'drawing-bearing.png' });

// (8b) Details & Export - forthcoming, never hidden
await rail.getByRole('button', { name: /Details & Export/ }).click();
await page.waitForSelector('text=forthcoming', { timeout: 15000 });
const ex = await page.locator('main').innerText();
check('export: DXF/IFC live (WP-5.1)', /plan dxf/.test(ex) && /ifc model/.test(ex));
check('export: unbuilt work named with its WP', /WP-5\.3 is not built/.test(ex));
check('export: no costing engine implied', /No costing engine exists/i.test(ex));
check('export: conflict count is the recorded 262', /262 recorded pack conflicts/.test(ex));
await page.screenshot({ path: SHOTS + 'export.png' });

// (11) Transcription - a drawing goes in, a record comes out, gaps named
await rail.getByRole('button', { name: /Transcription/ }).click();
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
const aiRail = await page.locator('aside').last().innerText();
check('rail present on every surface', /the rail/i.test(aiRail));

// ── WP-5.6: navigation, addressing and search ──────────────────────────────────
// A place is a URL. Everything below is the one claim, tested from both ends.

// A citation pasted cold resolves, and canonicalises to the place it names — so the URL
// you copy back out is the place, not the redirect that reached it.
await page.goto(BASE + '/#/cite/fault:porch-too-shallow-to-inhabit', { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
check('a #/cite/ link resolves cold', /#\/faults\/porch-too-shallow-to-inhabit/.test(page.url()));
check('and it landed on the fault', /four-foot porch/i.test(await page.locator('main').innerText()));

// A deep link restores on refresh — the thing no amount of useState could do.
await page.goto(BASE + '/#/kit/craftsman', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
check('a refresh keeps the place', /#\/kit\/craftsman/.test(page.url()));
check('and the place is loaded', /craftsman/i.test(await page.locator('main').innerText()));

// Filters live in the URL, survive leaving and returning, and can be cleared in one act.
await page.goto(BASE + '/#/faults', { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
await page.keyboard.press('/');                      // focuses this surface's filter bar
await page.keyboard.type('porch');
await page.waitForTimeout(500);
check('/ reaches the filter bar and it narrows', /q=porch/.test(page.url()));
const faultsFiltered = await page.locator('main').innerText();
check('the list says how much it is hiding',
  new RegExp(`${overview.counts.faults} solecisms · [1-9]\\d? shown`, 'i').test(faultsFiltered));
await page.locator('nav[aria-label="surfaces"]').getByRole('button', { name: /The Kit/ }).click();
await page.waitForTimeout(700);
await page.goBack();
await page.waitForTimeout(900);
check('filters survive leaving and coming back', /q=porch/.test(page.url()));
await page.getByRole('button', { name: /narrowing · clear/ }).click();
await page.waitForTimeout(500);
check('one act clears every filter', !/q=porch/.test(page.url()));

// The palette: opened by key, dispatches by citation, reachable by a word a newcomer
// would actually type.
await page.keyboard.press('Control+k');
await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
check('⌘K opens the palette', await page.locator('[role="dialog"]').count() > 0);
await page.keyboard.type('mistakes');
await page.waitForTimeout(500);
check('a newcomer word finds the fault corpus',
  /Fault Corpus/i.test(await page.locator('[role="option"]').first().innerText()));
await page.keyboard.press('Escape');
await page.waitForTimeout(200);
await page.keyboard.press('Control+k');
await page.waitForTimeout(300);
await page.keyboard.type('tidewater georgian');      // words in either order
await page.waitForTimeout(500);
const hit = await page.locator('[role="option"]').first().innerText();
check('half-remembered word order still finds it', /Tidewater/i.test(hit));
check('the citation is printed beside the result', /style:tidewater-georgian/.test(hit));
await page.screenshot({ path: SHOTS + 'palette.png' });
await page.keyboard.press('Enter');
await page.waitForTimeout(900);
check('the palette navigates to the cited place', /#\/style\/tidewater-georgian/.test(page.url()));

// ── The phylogeny's map reading ────────────────────────────────────────────────
await page.goto(BASE + '/#/phylogeny/tidewater-georgian?view=map', { waitUntil: 'networkidle' });
await page.waitForTimeout(2000);
const mapSvg = page.locator('main svg[role="img"]');
const mapLabel = await mapSvg.getAttribute('aria-label');
check('the map reading is addressable', /view=map/.test(page.url()));
check('hearths and arcs are drawn', /hearths carrying \d+ styles/.test(mapLabel || ''));
const mapText = await page.locator('main').innerText();
// The whole point of the precision tiers: a country is not a hearth, and the drawing
// says so rather than planting a firm dot in the middle of a nation.
check('placement precision is counted, not implied', /\d+ country/i.test(mapText)
  && /no hearth to place it at/i.test(mapText));
check('the gazetteer is disclaimed as interface, not source',
  /in prose, not coordinates/i.test(mapText) && /none of them is a source/i.test(mapText));
// OQ 65: a country-wide mark must be distinguishable from a failure to place. Every one
// of them is now country-wide by the corpus's own account — a family, a tradition, or a
// record whose hearth says it has none — and the drawing says which.
check('coarse marks are attributed to the record, not to the drawing',
  /because the corpus says so rather than because this drawing failed/i.test(mapText));
// Every taxon must be either placed or named as unplaced — never dropped.
{
  const phyl = await (await fetch(BASE + '/api/phylogeny')).json();
  const placedM = /(\d+) hearths carrying (\d+) styles/.exec(mapLabel || '');
  const unlocated = /(\d+) styles? name no region the gazetteer knows/.exec(mapText);
  const accounted = Number(placedM[2]) + (unlocated ? Number(unlocated[1]) : 0);
  check('every taxon is placed or listed as unplaced, none dropped',
    accounted === phyl.taxa.length);
}
check('edges inside one hearth are counted, not faked',
  /share a hearth/i.test(mapText) || !/not drawn/i.test(mapText));
await page.screenshot({ path: SHOTS + 'phylogeny-map.png' });

// and the two readings are one graph: switching back keeps the taxon
await page.locator('main').getByRole('radio', { name: 'tree' }).click();
await page.waitForTimeout(900);
check('switching back to the tree keeps the taxon and drops the param',
  /#\/phylogeny\/tidewater-georgian$/.test(page.url()));

// The keys card teaches the grammar the rail and the URL share.
await page.goto(BASE + '/#/faults', { waitUntil: 'networkidle' });
await page.waitForTimeout(600);
await page.keyboard.press('?');
await page.waitForTimeout(400);
const card = await page.locator('[role="dialog"]').innerText();
// ── the adversarial audit's fixes, pinned so they cannot come back ──────────────
// Every one of these passed the suite while being broken; that is why they are here.

// B2: `style` is both a filter axis and a router selection key. It used to read from the
// query, where the router never puts it, so the picker snapped back and the style-specific
// exception set was never fetched.
await page.goto(BASE + '/#/faults?style=craftsman');
await page.waitForTimeout(1600);
const styleFilter = await page.locator('main input[role="combobox"]').first().inputValue();
check('a selection-key filter axis actually holds', /craftsman/i.test(styleFilter));
check('and it counts as narrowing', /1 narrowing/i.test(await page.locator('main').innerText()));

// W3: 138 of 665 palette entries dispatched a selection key no surface read, so the search
// silently did nothing. A record with no detail view is acknowledged rather than dropped.
await page.goto(BASE + '/#/cite/room:parlor');
await page.waitForTimeout(1600);
check('a searched record with no detail view is acknowledged',
  /searched/i.test(await page.locator('main').innerText()));

// W5: every surface guarded its sync with `if (selection?.x)`, so going back to a bare
// surface left the previous record on screen — the URL and the panel disagreeing.
await page.goto(BASE + '/#/kit/craftsman');
await page.waitForTimeout(1400);
await page.goto(BASE + '/#/kit');
await page.waitForTimeout(1400);
check('a bare surface URL does not still show the last record',
  !/craftsman/i.test((await page.locator('main').innerText()).slice(0, 400)));

// W6: setPointerCapture on the <svg> retargeted the click, so no mark on the map could be
// selected — while panning still worked, which is why it looked fine.
await page.goto(BASE + '/#/phylogeny?view=map');
await page.waitForTimeout(2000);
await page.locator('main svg g[style*="pointer"]').first().click({ force: true });
await page.waitForTimeout(900);
check('a hearth on the map can be clicked',
  /VARIANT|STYLE|FAMILY|TRADITION|searched/i.test(await page.locator('main').innerText()));

check('? explains the keys and the addressing', /kind:id/.test(card) && /⌘K/.test(card));
await page.keyboard.press('Escape');

await browser.close();
if (failures.length) { console.error('\nFAILED:', failures); process.exit(1); }
console.log('\nE2E WALK GREEN');
