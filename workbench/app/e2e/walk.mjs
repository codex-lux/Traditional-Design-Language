/* Walk every live surface against a running server (127.0.0.1:8177 serving the built
   app), assert the load-bearing honesty affordances, and screenshot each surface for
   eyeball review against the mockup. Run: node e2e/walk.mjs */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
import { existsSync, mkdirSync } from 'node:fs';
// The pane table, so this file is not a second authority over numbers the store owns —
// which is the sin `--rail-left` was deleted for.
import { PANES } from '../src/state/layout.js';

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

/* A 429 must announce itself, not surface as a selector timeout thirty seconds later.

   The server allows 60 composing/checking calls an hour PER IDENTITY (HEAVY_CALLS_PER_HOUR
   in workbench/server/limits.py), and this walk spends several of them — so running it
   repeatedly against one server, which is exactly what iterating on it looks like,
   eventually exhausts the budget. What that looked like was `waitForSelector('svg[role=
   "img"]')` timing out on the Plan Workbench: a failure that reads as a broken sheet and is
   a spent quota. The limiter already says so honestly in its response body; nothing was
   listening. Restarting the server resets the window. */
let limited = null;
page.on('response', (r) => {
  if (r.status() === 429 && !limited) {
    limited = r.url();
    console.log('\nRATE LIMITED by the workbench server at ' + limited);
    console.log('  This walk is not failing on the code. The server allows 60 heavy calls');
    console.log('  an hour per identity and this run has spent them — restart the server');
    console.log('  (or wait for the window) and run again.\n');
  }
});

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
// …and the caption names the engine that ACTUALLY DREW THIS SHEET. Until WP-6.3 flipped
// the default it said flatly that every edit re-scores on the hill-climb and that nothing
// drawn asserts feasibility was proved — true then, false the moment `auto` became the
// default, and false in the direction that matters: a reader could not tell a proof from a
// search. Checked against the API's own report rather than against a phrase.
{
  const solved = await fetch(BASE + '/api/plans/examples/tidewater-georgian-careful')
    .then((r) => r.json())
    .then((p) => fetch(BASE + '/api/plan/evaluate', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plan: p.plan || p, place: true }),
    }))
    .then((r) => r.json())
    .catch(() => null);
  const eng = solved?.placement?.geometry_report?.solver?.engine;
  if (!eng) {
    check('the caption names the engine that drew the sheet — COULD NOT EVALUATE '
      + '(the API did not report one)', false);
  } else {
    const saysProved = /was\s+proved,\s+not\s+searched/i.test(body);
    const saysSearched = /came from the\s+fast search/i.test(body);
    check(`the caption names the engine that drew the sheet (${eng})`,
      eng === 'cp-sat' ? (saysProved && !saysSearched) : (saysSearched && !saysProved));
    // …and the PLATE says it too, not only the page prose beside it. WP-6.3 put the
    // disclosure one level out, which is the one place it cannot travel: a printed or
    // exported plate leaves the prose behind and a reader cannot tell a proof from a
    // search. Measured on the plate's own caption element.
    const plate = await page.evaluate(() => {
      const n = document.querySelector('[data-plate-note]');
      return n ? n.textContent.replace(/\s+/g, ' ').trim() : '';
    });
    check(`the plate's own caption names the engine (${eng})`,
      eng === 'cp-sat'
        ? /placement proved \(cp-sat\)/i.test(plate)
        : /placement searched, not proved/i.test(plate));
  }
}
check('relaxations counted', /cut\(s\) off the bay line/i.test(body));
// WP-9.3: the analyst and the loop reach the bench. The solver fold renders its children
// only when open (FilterGroup, defaultOpen false) — the /prove placement/ check above passes
// on the page PROSE — so open it and count the chips as the denominator before clicking.
{
  await page.getByRole('button', { name: /^solver/ }).click();
  const chips = page.locator('button', { hasText: /^(critique|revise \(search\)|revise \(proof\))/ });
  const nChips = await chips.count();
  check('the analyst and both revise acts are offered once the solver fold is open (3 chips)', nChips === 3);
  if (nChips === 3) {
    await page.getByRole('button', { name: /^critique/ }).click();
    await page.waitForSelector('[data-panel="critique"]', { timeout: 90000 }).catch(() => {});
    const sums = await page.evaluate(() => {
      const p = document.querySelector('[data-panel="critique"]');
      if (!p) return null;
      return { text: p.textContent, classified: +p.getAttribute('data-classified'),
        findings: +p.getAttribute('data-findings') };
    });
    check('the critique names every class', !!sums && /by class/i.test(sums.text));
    // classified (from /api/plan/critique) against the non-info findings shown (from
    // /api/plan/evaluate): two routes, one placement through the solve cache — a real
    // cross-check, and zero findings would pass nothing
    check(`the class counts sum to the findings the sheet shows (${sums?.classified} of ${sums?.findings})`,
      !!sums && sums.findings > 0 && sums.classified === sums.findings);
    // ... and the rows CARRY their class, not only the strip its counts (WP-9.4: nothing
    // asserted the tags, so dropping them from the row left every check green)
    const tagged = await page.locator('[data-class-tag]').count();
    check(`every classified finding row carries its class tag (${tagged} of ${sums?.classified})`,
      !!sums && tagged === sums.classified);
    const drawn = await page.locator('[data-layer="drawn"]').count();
    if (!drawn) {
      check('every drawn finding carries the engine that placed it — COULD NOT EVALUATE '
        + '(no drawn finding on this sheet)', false);
    } else {
      const tagged = await page.locator('[data-layer="drawn"] [data-engine-tag]').count();
      check(`every drawn finding carries the engine that placed it (${tagged} of ${drawn})`, tagged === drawn);
    }
    // the fast loop: rounds 6, budget 60 s on the chip, so the poll and the promise agree
    await page.getByRole('button', { name: /^revise \(search\)/ }).click();
    let panel = '';
    for (let i = 0; i < 90; i++) {
      await page.waitForTimeout(1000);
      panel = await page.locator('[data-panel="revision"]').innerText().catch(() => '');
      if (/stopped:|converged/i.test(panel)) break;
    }
    check('the revision panel names why the loop stopped', /stopped:|converged/i.test(panel));
    check('the revision panel names its round count', /\d+ rounds?\b/i.test(panel));
    check('the panel says the sheet is a fresh solve of the revised record', /fresh solve/i.test(panel));
    // one undo step: the loop loaded the revised record through planDoc.load
    await page.getByRole('button', { name: 'undo' }).click();
    await page.waitForTimeout(400);
    const still = await page.locator('[data-panel="revision"]').count();
    check('undo takes the revision away — the loop loaded one undo step', still === 0);
    await page.waitForTimeout(2500);   // the debounce re-evaluates the restored record
    // the critique was of the evaluation BEFORE the revise; two evaluations have landed
    // since, so the panel must say so and its tags must be gone -- the one moment the
    // staleness path fires, and the walk used to step over it (WP-9.4)
    const stale = await page.locator('[data-panel="critique"]').innerText().catch(() => '');
    check('a critique of an earlier evaluation says so after the record changed', /earlier evaluation/i.test(stale));
    const tagsAfter = await page.locator('[data-class-tag]').count();
    check('and no finding row still wears a class from the earlier evaluation', tagsAfter === 0);
  }
}
// WP-5.7: every surface's index panel pulls, not just the shell's rails. The findings
// column was 430px written into the JSX and chosen against one window.
{
  const sep = page.locator('[role="separator"][aria-label="resize the findings"]');
  check('the findings column has a pullable margin', await sep.count() === 1);
  const box = await sep.boundingBox();
  await page.mouse.move(box.x + 5, box.y + 200);
  await page.mouse.down();
  await page.mouse.move(box.x + 95, box.y + 200, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(250);
  const moved = (await sep.boundingBox()).x - box.x;
  check(`pulling the findings column widens it (${Math.round(moved)}px)`, moved > 60);
  /* And it must NOT fold: a Plan Workbench with its findings folded away is not a
     decluttered workbench, it is a broken one.

     MEASURED BY WIDTH, because that is the only thing that differs. `PullPane` never reads
     `collapsed`, so a folded pane renders a byte-identical DOM — the separator is still
     there and "could not evaluate" is still there — and the original version of this check,
     which asserted exactly those two things, stayed green with BOTH foldable guards deleted.
     Folded leaves the width where it was; clamped puts it at the pane's floor. */
  const findingsW = () => page.evaluate(() => {
    const s = document.querySelector('[role="separator"][aria-label="resize the findings"]');
    return s.parentElement.previousElementSibling.getBoundingClientRect().width;
  });
  const wide = await findingsW();
  const grab = await sep.boundingBox();               // re-measured: the pane just moved
  await page.mouse.move(grab.x + grab.width / 2, grab.y + 200);
  await page.mouse.down();
  await page.mouse.move(grab.x - 500, grab.y + 200, { steps: 14 });
  await page.mouse.up();
  await page.waitForTimeout(250);
  const narrow = await findingsW();
  check(`a surface's own index clamps at its floor rather than folding `
    + `(${Math.round(wide)} → ${Math.round(narrow)}, floor ${PANES.workbench.min})`,
    Math.abs(narrow - PANES.workbench.min) < 3);
  await sep.dblclick();
  await page.waitForTimeout(250);
  check('and double-click puts it back',
    Math.abs(await findingsW() - PANES.workbench.def) < 3);
}
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
  // A ROOM IS `[data-room]`, NOT "a group whose first child is a title and which holds a
  // rect". That heuristic was the population this check measured until WP-11.3, and it was
  // never a description of a room -- it was a description of the markup a room HAPPENED to
  // have. The moment furniture arrived, drawn as <g data-furniture><title/><rect/></g>, the
  // room count went 13 -> 44 and the check failed for counting chairs as rooms. Fifth
  // instance in this file of a guard selecting on incidental shape rather than on identity,
  // and the third repaired in this package.
  for (const g of document.querySelectorAll('svg g[data-room]')) {
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

// WP-6.1 — the sheet's openings say what they are, and the sheet owns up to what it
// could not draw. Every assertion here is against something the page computed from the
// record, never against a number written down twice.
const openings = await page.evaluate(() => {
  const marks = [...document.querySelectorAll('[data-door-type]')];
  const note = document.querySelector('[data-plate-note]');
  const title = document.querySelector('[data-plate-title]');
  return {
    total: marks.length,
    types: [...new Set(marks.map((m) => m.getAttribute('data-door-type')))].sort(),
    rooms: [...document.querySelectorAll('[data-room]')].map((g) => g.getAttribute('data-room')),
    note: note ? note.textContent.replace(/\s+/g, ' ').trim() : '',
    legend: !!document.querySelector('[data-legend="relaxation"]'),
    titleText: title ? title.textContent : '',
    diverged: document.querySelectorAll('[data-diverged]').length,
  };
});
// vacuity first, as everywhere else in this walk: a selector that matches nothing must
// not be able to pass the assertions that follow
check(`the sheet draws door marks (${openings.total})`, openings.total >= 10);
// the 5 ft pair between drawing room and dining room, and the 6 ft cased opening into the
// stair hall, were BOTH drawn as one giant hinged leaf until this package, because no
// renderer read `type` at all
check(`door marks carry their type (${openings.types.join(', ')})`,
  openings.types.includes('double') && (openings.types.includes('open')
    || openings.types.includes('cased-opening')));
// the undrawable disclosure: it must name pairs, and every room it names must be a room
// this sheet actually drew — a caption naming phantoms would be a new kind of lie
const undrawn = openings.note.match(/(\d+) declared door\(s\) without a drawable opening[^:]*:([^.]*)\./i);
check('the sheet states the doors it could not draw', !!undrawn);
if (undrawn) {
  const named = undrawn[2].split(',').map((s) => s.trim()).filter(Boolean);
  const ids = new Set([...openings.rooms, 'exterior']);
  // ONE end must be a room this sheet drew, not both: "the other room is not placed on
  // this level" is itself one of the reasons a door cannot be drawn, and the Tidewater
  // record's breakfast-room door to the terrace is exactly that case. Requiring both ends
  // would make the sheet unable to name the very doors it most needs to name.
  const phantom = named.filter((p) => !p.split('–').some((r) => ids.has(r.trim())));
  check(`the undrawable list names ${undrawn[1]} door(s), each touching a room on this sheet`
    + (phantom.length ? ' — phantom: ' + phantom.join('; ') : ''),
    Number(undrawn[1]) === named.length && phantom.length === 0);
}
// the △ is defined on the sheet that uses it, not only in the running prose of a caption
check('the relaxation mark carries a legend', openings.legend || !/cut\(s\) off the bay line/i.test(openings.note));
// …and it sits on a wall. A CP mark carries no from/to extent, and the sheet used to drop
// it at the MIDDLE OF THE PLAN: on this very placement that put a tick and a triangle
// inside the drawing room, on a line with no wall near it, which is what was reported as
// arrows that "seem to point to anything and everything". Measured, not asserted from the
// record: each △'s own drawn centre against each drawn room rectangle.
const rx = await page.evaluate(() => {
  const tris = [...document.querySelectorAll('svg path')].filter((p) => {
    const t = p.parentElement && p.parentElement.querySelector('title');
    return t && /off the bay line/.test(t.textContent);
  });
  const rooms = [...document.querySelectorAll('[data-room]')]
    .map((g) => ({ id: g.getAttribute('data-room'), b: g.querySelector('rect').getBoundingClientRect() }));
  const adrift = [];
  for (const p of tris) {
    const b = p.getBoundingClientRect();
    const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
    for (const r of rooms) {
      if (cx <= r.b.left || cx >= r.b.right || cy <= r.b.top || cy >= r.b.bottom) continue;
      // inside this room: how far from the nearest wall of it, in screen px
      const d = Math.min(cx - r.b.left, r.b.right - cx, cy - r.b.top, r.b.bottom - cy);
      if (d > 12) adrift.push(`${r.id} (${Math.round(d)}px in)`);
    }
  }
  return { tris: tris.length, adrift };
});
check(`every △ is drawn on a wall, none adrift in a room (${rx.tris} mark(s))`
  + (rx.adrift.length ? ' — ' + rx.adrift.join(', ') : ''),
  rx.tris > 0 && rx.adrift.length === 0);
// a room drawn at a size its record does not declare says so, in the caption and on itself
const divergedClaim = openings.note.match(/(\d+) room\(s\) are drawn at a size the record does not declare/i);
check('rooms drawn off their declaration are marked and counted',
  !divergedClaim || Number(divergedClaim[1]) === openings.diverged);
// and the plate title survives its own line-wrapping: stripped of the interpuncts and the
// zero-width spaces that let it fold, it must still be the whole name. Folded badly, this
// title read 'WATER GEORGIAN, FIVE CAREFULLY PLANNED' — a different house.
const flat = openings.titleText.replace(/[·​]/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
check(`the plate title is whole ("${flat.slice(0, 48)}")`,
  flat.includes('tidewater') && flat.includes('georgian'));

// WP-6.2 — the stair and the fixtures, both drawn ONLY from the record. There has never
// been a line of stair-drawing code in this system, and a stair hall was an empty rectangle
// with lettering in it. Either the flights are on the sheet, or the sheet says why not:
// what must never happen is an empty stair hall presented as a finished drawing.
const built = await page.evaluate(() => ({
  stair: document.querySelectorAll('[data-stair]').length,
  refused: !!document.querySelector('[data-stair="refused"]'),
  // WP-11.3: BY WHAT IT IS, not by the dash it happens to be drawn with. This counted
  // `svg rect` whose stroke-dasharray ATTRIBUTE started "1.4" -- a selector that the pen
  // ladder would have emptied the moment the dash moved into `style`, and that furniture
  // drawn with any similar dash would have silently inflated. It asserts `> 0`, so either
  // failure reads as a pass. Fourth instance of the class in this file.
  fixtures: document.querySelectorAll('[data-fixture]').length,
  furniture: document.querySelectorAll('[data-furniture]').length,
  furnitureSymbols: new Set([...document.querySelectorAll('[data-furniture]')]
    .map((g) => g.getAttribute('data-furniture'))).size,
  // WP-11.4. The stoop and the gable-end stacks. Counted by what they ARE and measured
  // against the PLATE, because the failure this catches is not a missing mark: it is a mark
  // drawn outside the viewBox, where nothing errors and nothing is seen.
  stacks: [...document.querySelectorAll('[data-stack]')].map((r) => ({
    x: +r.getAttribute('x'), w: +r.getAttribute('width'), wall: r.getAttribute('data-stack'),
  })),
  stoops: [...document.querySelectorAll('[data-threshold] rect')].map((r) => ({
    x: +r.getAttribute('x'), y: +r.getAttribute('y'),
    w: +r.getAttribute('width'), h: +r.getAttribute('height'),
  })),
  vb: (document.querySelector('svg[role="img"]') || document.querySelector('svg'))
    ?.getAttribute('viewBox'),
}));
check(`the stair is drawn or its absence is stated (${built.stair} mark(s), refused=${built.refused})`,
  built.stair > 0);
check(`wet-room fixtures are drawn from the record (${built.fixtures})`, built.fixtures > 0);
// WP-11.3 — the dry rooms are furnished, from the record's own marks and from nothing else.
// The count and the SYMBOL VARIETY are both asserted: a sheet that drew every item as the
// default outline would satisfy a bare count while saying nothing, which is the vacuous-pass
// shape this file has been caught by four times.
check(`dry-room furniture is drawn from the record (${built.furniture} items, `
      + `${built.furnitureSymbols} distinct symbols)`,
  built.furniture > 10 && built.furnitureSymbols > 2);
// WP-11.4 — the stoop and the stacks, from plan.threshold and plan.hearths. Both stand
// OUTSIDE the block, so the plate has to have grown for them; a stack drawn at x = -3.1 on a
// viewBox starting at -11 is invisible and raises nothing, which is why the extent is
// asserted here and not only the count.
{
  const vb = (built.vb || '').split(/\s+/).map(Number);
  const inside = built.stacks.length > 0 && built.stacks.every(
    (s) => s.x >= vb[0] && s.x + s.w <= vb[0] + vb[2]);
  check(`the gable-end stacks are drawn and lie on the plate (${built.stacks.length}, `
        + `walls ${built.stacks.map((s) => s.wall).join('/')}, viewBox ${built.vb})`,
    built.stacks.length === 2 && inside);
  // COUNTED AS A PROPERTY AND NOT AS A NUMBER. The first version asserted exactly one, and
  // the walk answered TWO: on CP-SAT the placement puts the KITCHEN's exterior door on the
  // entrance front as well, so the count is the engine's and not the record's. What must hold
  // on any engine is that every mark of the flight lies on the plate.
  const onPlate = built.stoops.length > 0 && built.stoops.every(
    (r) => r.x >= vb[0] && r.x + r.w <= vb[0] + vb[2]
        && r.y >= vb[1] && r.y + r.h <= vb[1] + vb[3]);
  check(`the entrance stoop is drawn from the record and lies on the plate `
        + `(${built.stoops.length} mark(s))`, onPlate);
}

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
  //
  // SCROLLED INTO VIEW BEFORE IT IS MEASURED, AND THE REASON IS A MEASUREMENT (7 Sep 2026).
  // `page.mouse.click` takes VIEWPORT coordinates, and this read the rect where it happened to
  // sit. WP-11.1 put a "what this placement gave up" panel above the sheet -- on this record it
  // carries two lines and a paragraph -- and the Drawing Room went to **y = 1020.98 in a
  // viewport 1000 tall**. Twenty-one pixels below the fold: the click landed outside the window,
  // nothing was selected, `[data-nopan]` stayed at 0, and this block returned null, so all four
  // checks below reported `undefined` and named nothing.
  //
  // That is the SECOND time these same four have gone red as a block for a reason that was not
  // the wall handle -- CLAUDE.md records the first, where an annotation swallowed the click and
  // it was misdiagnosed as CP latency for a week. The checks are about whether a handle can be
  // grasped and what the drag does, not about where the page happens to have scrolled to, so
  // scrolling the room into view restores what they were written to ask. Anything added above
  // the sheet from now on moves the plate and not this test.
  const room = await page.evaluate(() => {
    for (const g of document.querySelectorAll('svg g')) {
      const t = g.firstElementChild;
      if (t && t.tagName === 'title' && /Drawing Room/.test(t.textContent)) {
        g.scrollIntoView({ block: 'center' });          // synchronous: the rect below is post-scroll
        const b = g.querySelector('rect').getBoundingClientRect();
        return { x: b.x + b.width / 2, y: b.y + b.height / 2,
                 onScreen: b.y >= 0 && b.y + b.height <= window.innerHeight };
      }
    } return null;
  });
  if (!room) return { reason: 'the sheet drew no Drawing Room to click' };
  const before = await roomLabel('Drawing Room');
  await page.mouse.click(room.x, room.y);
  await page.waitForTimeout(400);
  // Captured whatever happens next, so a failure below can NAME its cause instead of four
  // `undefined`s. A room that did not select raises no handle, and that is a different defect
  // from a handle that cannot be grasped.
  const handles = await page.evaluate(() => document.querySelectorAll('[data-nopan]').length);
  const scroll0 = await scrollPos();
  const h = await page.evaluate(() => {
    const rs = [...document.querySelectorAll('[data-nopan]')].map((e) => e.getBoundingClientRect());
    if (!rs.length) return null;
    const r = rs.sort((a, b) => b.x - a.x)[0];
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  if (!h) return { handles, room, reason: 'clicking the room raised no wall handle' };
  await page.mouse.move(h.x, h.y);
  await page.mouse.down();
  await page.mouse.move(h.x + 30, h.y, { steps: 6 });
  // COMPUTED STYLE, NOT THE ATTRIBUTE. The sheet's stroke widths moved onto the pen ladder
  // (`sheet/pen.js`), and `var(--lw-cut)` does not resolve inside an SVG presentation
  // attribute -- so every mark states its weight and its ink in `style=` now and
  // `getAttribute('stroke')` returns null on all of them. Reading the attribute here would
  // have made this check count zero previews on a working drag: a guard that reads a
  // selector rather than a property is this repository's most-repeated way of going blind,
  // and the pen check thirty lines below carries the same lesson in its own comment.
  const preview = await page.evaluate(() => {
    const toRGB = (hex) => {
      const h = hex.replace('#', '');
      const n = parseInt(h.length === 3 ? h.split('').map(c => c + c).join('') : h, 16);
      return `rgb(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255})`;
    };
    const gilt = toRGB(getComputedStyle(document.documentElement)
      .getPropertyValue('--gilt-deep').trim());
    return [...document.querySelectorAll('line')]
      .filter((l) => getComputedStyle(l).stroke === gilt
        && l.getAttribute('stroke-dasharray')).length;
  });
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
  return { preview, panned, scroll0, before, restored, after, clicked: !!h2, handles, room };
})();
// THE STEP BEFORE THE HANDLE, so this block can no longer fail four times saying `undefined`.
// It reports what actually broke: the room was not drawn, or the click did not select it.
check(`clicking a room raises its wall handles (${handleLive?.handles ?? 'n/a'}${
  handleLive?.reason ? ' — ' + handleLive.reason : ''})`, (handleLive?.handles ?? 0) > 0);
check('the room the drag needs is on screen to be clicked',
  handleLive?.room ? handleLive.room.onScreen === true : false);
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
{
  /* The sheet's own declared ground must survive being embedded. It did not: the fit was
     injected as a SECOND `style` attribute before the element's own, so the parser kept
     the injected one and silently dropped `style="background:…"` that every Python
     renderer writes. Invisible only because what showed through happened to be a
     near-identical vellum, and one theme change from dark ink on a dark ground. */
  const g = await page.evaluate(() => {
    const svg = document.querySelector('.plate-fit > svg');
    if (!svg) return null;
    const head = svg.outerHTML.slice(0, svg.outerHTML.indexOf('>') + 1);
    return { dup: (head.match(/style=/g) || []).length,
             bg: getComputedStyle(svg).backgroundColor,
             fits: svg.getBoundingClientRect().width
               <= svg.parentElement.getBoundingClientRect().width + 1 };
  });
  check('drawing set: the sheet carries one style attribute, not two', g && g.dup === 1);
  check(`drawing set: its declared ground actually applies (${g && g.bg})`,
    g && g.bg !== 'rgba(0, 0, 0, 0)');
  check('drawing set: and the sheet still fits its column', g && g.fits);
}
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

// ── WP-5.7: the shell's proportions, and an atlas that sharpens ────────────────
// The report that started it: "the map is VERY crude and doesn't take well to zooming in
// since the resolution does not scale up as you zoom in." Two separate causes, both
// pinned here, plus the three affordances asked for in the same breath.
await page.goto(BASE + '/#/phylogeny/tidewater-georgian?view=map', { waitUntil: 'networkidle' });
await page.waitForTimeout(1800);

/* (1) The pen was scaled with the drawing: `vector-effect` does not inherit, so it was on
   the <g> and reached none of the paths, and a 0.7-unit coastline was 0.7 DEGREES of ink.

   THIS READS COMPUTED STYLE, AND THE FIRST VERSION DID NOT — which made it inert against
   the exact defect it names. It filtered on `el.getAttribute('stroke-width')`, but
   `stroke-width` IS inherited: the coastline paths and the graticule lines take theirs
   from their <g> and carry no attribute of their own, so both were dropped from the
   population before the vector-effect test ever ran. Reverting the fix left it reporting
   zero. Only the resolved value distinguishes the two shapes, because "does not inherit"
   is a statement about resolution. Verified against a reconstruction of both. */
async function penCheck(where) {
  const r = await page.evaluate(() => {
    const svgs = [...document.querySelectorAll('main svg')];
    let stroked = 0;
    const bad = [];
    svgs.forEach((svg) => {
      // a scalable drawing is one whose user units are not pixels
      if (!svg.getAttribute('viewBox')) return;
      svg.querySelectorAll('path,line,circle,rect,polyline,polygon,ellipse,polygon').forEach((el) => {
        const c = getComputedStyle(el);
        if (!c.stroke || c.stroke === 'none' || !(parseFloat(c.strokeWidth) > 0)) return;
        // a mark inside a <pattern> is deliberately in model units — the hatch spacing is
        // a measurement, not a pen — and is the one exemption.
        if (el.closest('pattern')) return;
        stroked += 1;
        if (c.vectorEffect !== 'non-scaling-stroke') bad.push(el.tagName + ':' + (el.getAttribute('class') || ''));
      });
    });
    return { stroked, bad: bad.slice(0, 6), n: bad.length };
  });
  // Assert the DENOMINATOR too: a guard whose population is empty passes on anything.
  check(`${where}: the guard actually inspects marks (${r.stroked} stroked)`, r.stroked > 0);
  check(`${where}: no stroked mark scales its own pen with the view${r.n ? ' — ' + r.bad.join(', ') : ''}`,
    r.n === 0);
}
await penCheck('the atlas');

// (2) The outline itself gains detail. Zoom in and the tier the map is drawing must
// change — and it must SAY which one, so a coarse coastline is never passed off as a
// fine one.
const atHome = await page.locator('main').innerText();
check('the atlas names the outline it is drawing and how much it can show',
  /Coastline · land-110m\.json/.test(atHome) && /simplified at 0\.35°/.test(atHome));
{
  const svg = await page.locator('main svg[role="img"]').boundingBox();
  for (let i = 0; i < 14; i += 1) {
    await page.mouse.move(svg.x + svg.width * 0.78, svg.y + svg.height * 0.35);
    await page.mouse.wheel(0, -200);
    await page.waitForTimeout(60);
  }
  await page.waitForTimeout(2500);       // the fine tier is a fetched chunk
  const zoomed = await page.locator('main').innerText();
  check('zooming in fetches an outline that can carry the scale',
    /land-10m\.json/.test(zoomed) && /simplified at 0\.012°/.test(zoomed));
  // and the grid does not vanish at the zooms that were just made reachable
  const grid = await page.locator('main svg[role="img"] line').count();
  check(`the graticule follows the scale rather than disappearing (${grid} lines)`,
    grid >= 5 && grid <= 40);
}
{
  /* THE PLATE AND THE VIEWBOX ARE THE SAME RECTANGLE. They were not: the svg had no
     `preserveAspectRatio`, so `meet` painted 27.8 degrees of latitude above and below the
     box while the new cull and the new graticule were both cut TO the box — South America
     vanished from the home view because its bounding box misses the viewBox and not the
     paper, and the grid ended short of the edge of the plate. One mismatch, three defects.
     Asserting the two rectangles agree is what stops all three coming back. */
  await page.locator('main').getByRole('button', { name: 'reset the view' }).click();
  await page.waitForTimeout(700);
  const m = await page.evaluate(() => {
    const svg = document.querySelector('main svg[role="img"]');
    const r = svg.getBoundingClientRect();
    const vb = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    const g = [...svg.querySelectorAll('g')].find((x) => x.getAttribute('fill') === 'var(--paper-deep)');
    const par = [...svg.querySelectorAll('line')].filter((l) => l.getAttribute('y1') === l.getAttribute('y2'));
    return { pane: r.width / r.height, box: vb[2] / vb[3], vbW: vb[2],
             land: g ? g.children.length : 0,
             gratSpan: par.length ? Math.abs(+par[0].getAttribute('x2') - +par[0].getAttribute('x1')) : 0,
             southern: g ? [...g.children].some((pa) => { const b = pa.getBBox(); return b.y + b.height > 20 && b.width > 20; }) : false };
  });
  check(`the viewBox has the pane's own shape, so nothing is letterboxed `
    + `(${m.pane.toFixed(3)} vs ${m.box.toFixed(3)})`, Math.abs(m.pane - m.box) < 0.01);
  check(`the graticule spans the whole plate (${m.gratSpan} of ${m.vbW})`,
    Math.abs(m.gratSpan - m.vbW) < 0.01);
  /* Bounded on BOTH sides. Too few means the cull is dropping land the plate paints —
     the regression this block exists for. Too many means the tier choice has swung the
     other way and a hemisphere view is mounting the 10m outline it fetched earlier, which
     is 827 rings and one 25,000-point path for a drawing nobody can tell apart at 0.134
     degrees per pixel. Both were live at some point in this package. */
  check(`land that the plate paints is drawn, and no more (${m.land} rings at the home view)`,
    m.land >= 30 && m.land <= 120 && m.southern);
}

// (3) Full screen: the atlas takes the window, and escape gives the instrument back.
// The rail's presence is asserted BEFORE it is asserted absent — the two fold checks below
// are both `=== 0`, and would pass together if the rail simply stopped rendering here.
check('the rail is on this surface to begin with',
  await page.locator('aside[aria-label*="the rail"]').count() === 1);
await page.getByRole('button', { name: /full screen/i }).click();
await page.waitForTimeout(500);
check('full screen takes the masthead and both rails',
  await page.locator('nav[aria-label="surfaces"]').count() === 0
  && await page.locator('aside[aria-label*="the rail"]').count() === 0);
{
  /* IN THE VIEWPORT, not merely in the DOM. `innerText` includes text inside a scrolled
     `overflow-y: auto` container, so the original textual check passed on exactly the
     shipped defect it was written for — the exit control sitting 1,256px below the
     bottom of the legend's scroller. A way out that can be scrolled away is not a way out,
     and a check that reads innerText cannot tell the difference. */
  const exit = page.getByRole('button', { name: /leave full screen/i }).first();
  check('and says how to leave', await exit.count() === 1);
  const box = await exit.boundingBox();
  const vp = page.viewportSize();
  check(`and the way out is on screen (${box ? Math.round(box.y) : '?'} of ${vp.height})`,
    !!box && box.y >= 0 && box.y + box.height <= vp.height && box.x >= 0);
}
await page.screenshot({ path: SHOTS + 'phylogeny-map-full.png' });
/* Switching the READING while full used to strand the reader: the exit chip lived only in
   MapView, so pressing `tree` unmounted the one visible way out while the chrome stayed
   hidden. The strip survives both readings, so the control belongs to the strip. */
await page.locator('main').getByRole('radio', { name: 'tree' }).click();
await page.waitForTimeout(700);
check('switching the reading in full screen keeps a visible way out',
  await page.locator('nav[aria-label="surfaces"]').count() === 0
  && await page.getByRole('button', { name: /leave full screen/i }).first().isVisible());
await page.locator('main').getByRole('radio', { name: 'map' }).click();
await page.waitForTimeout(700);
await page.keyboard.press('Escape');
await page.waitForTimeout(500);
check('escape gives the instrument back',
  await page.locator('nav[aria-label="surfaces"]').count() === 1);
// ⌘K still works in full screen, and a jump out of the atlas used to carry the
// chrome-less shell onto a surface with no control to leave it by.
await page.getByRole('button', { name: /full screen/i }).click();
await page.waitForTimeout(400);
await page.goto(BASE + '/#/kit', { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
check('leaving the atlas leaves full screen with it, not a shell with no way out',
  await page.locator('nav[aria-label="surfaces"]').count() === 1);
await page.goto(BASE + '/#/phylogeny/tidewater-georgian?view=map', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);

// (4) Both rails fold, from the keyboard, and a fold leaves a way back rather than a hole.
await page.keyboard.press('[');
await page.keyboard.press(']');
await page.waitForTimeout(300);
check('[ and ] fold the surface list and the rail away',
  await page.locator('nav[aria-label="surfaces"]').count() === 0
  && await page.locator('aside[aria-label*="the rail"]').count() === 0);
check('a folded pane leaves a spine to bring it back, not a trapdoor',
  await page.getByRole('button', { name: /show the surface list/i }).count() === 1
  && await page.getByRole('button', { name: /show the rail/i }).count() === 1);
await page.screenshot({ path: SHOTS + 'phylogeny-map-folded.png' });
await page.getByRole('button', { name: /show the surface list/i }).click();
await page.getByRole('button', { name: /show the rail/i }).click();
await page.waitForTimeout(300);
check('and the spine brings it back', await page.locator('nav[aria-label="surfaces"]').count() === 1);

// (5) The margins pull. A width the reader chose has to survive a reload, or it is a
// gesture rather than a setting.
{
  const navW = () => page.locator('nav[aria-label="surfaces"]').evaluate((e) => e.getBoundingClientRect().width);
  const before = await navW();
  const sep = page.locator('[role="separator"][aria-label*="surface list"]');
  check('the margin between the panes is a real separator', await sep.count() === 1);
  /* AND IT ANSWERS KEYS. The original check counted the element and stopped there — and
     `onKeyDown` was written, documented in the component header, in docs/workbench.md and
     in the package report, and never attached to the element. A focusable role="separator"
     that announces aria-valuenow and then swallows every key is worse for a keyboard user
     than one that is not focusable at all, and this is the check that was meant to catch
     it. Drive the keys and measure the pane. */
  await sep.focus();
  check('and it takes focus', await sep.evaluate((e) => e === document.activeElement));
  const kb0 = await navW();
  for (let i = 0; i < 4; i += 1) await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(200);
  const kb1 = await navW();
  check(`arrow keys resize the pane (${Math.round(kb0)} → ${Math.round(kb1)})`, kb1 > kb0 + 20);
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('ArrowLeft');
  await page.waitForTimeout(200);
  const kb2 = await navW();
  check(`and go back the other way (${Math.round(kb1)} → ${Math.round(kb2)})`, kb2 < kb1);
  await page.keyboard.down('Shift');
  await page.keyboard.press('ArrowRight');
  await page.keyboard.up('Shift');
  await page.waitForTimeout(200);
  check('shift strides further than an arrow nudges',
    (await navW()) - kb2 > (kb1 - kb0) / 4 + 8);
  await page.keyboard.press('Home');
  await page.waitForTimeout(200);
  check(`Home returns it to its shipped width (${PANES.nav.def})`,
    Math.abs((await navW()) - PANES.nav.def) < 3);
  const box = await sep.boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + 200);
  await page.mouse.down();
  await page.mouse.move(box.x + 110, box.y + 200, { steps: 12 });
  await page.mouse.up();
  await page.waitForTimeout(300);
  const after = await page.locator('nav[aria-label="surfaces"]').evaluate((e) => e.getBoundingClientRect().width);
  check('pulling the margin widens the pane', after > before + 60);
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  const kept = await page.locator('nav[aria-label="surfaces"]').evaluate((e) => e.getBoundingClientRect().width);
  check('and the width the reader chose survives a reload', Math.abs(kept - after) < 3);
  // put it back, so the screenshots the rest of this walk takes are the shipped layout
  await page.locator('[role="separator"][aria-label*="surface list"]').dblclick();
  await page.waitForTimeout(300);
  check('double-clicking the margin returns the pane to its shipped width',
    Math.abs(await navW() - PANES.nav.def) < 3);
}

await browser.close();
if (limited) {
  console.error('\nCOULD NOT EVALUATE: the server rate-limited this run (429 at ' + limited
    + '). Restart it and run again — an unjudged walk is not a green one.');
  process.exit(3);
}
if (failures.length) { console.error('\nFAILED:', failures); process.exit(1); }
console.log('\nE2E WALK GREEN');
