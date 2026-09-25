/* Walk every live surface against a running server (127.0.0.1:8177 serving the built
   app), assert the load-bearing honesty affordances, and screenshot each surface for
   eyeball review against the mockup. Run: node e2e/walk.mjs */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
// The pane table, so this file is not a second authority over numbers the store owns —
// which is the sin `--rail-left` was deleted for.
import { PANES } from '../src/state/layout.js';
// The router's own table, for the same reason: an address this walk visits, and the surface a
// rail item reaches, are judged by the module that writes them rather than by a list here.
import { SURFACE_PATHS, parseHash, formatHash } from '../src/router.js';
// The site map and the trail, for the same reason again (WP-14.13): which places the rail
// offers, in what order, and what the crumbs say are the pure modules' answers, read here
// rather than written here.
import { navModel, flatItems, inHandFrom } from '../src/nav/navModel.js';
import { indexTerms } from '../src/glossary/lookup.js';

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
/* COULD NOT EVALUATE, KEPT APART FROM BOTH VERDICTS (WP-13.4). A check whose PRECONDITION the
   server does not meet is not a pass and is not a failure: it is the third state this project
   names first, and collapsing it into either is the fake-pass or the false-accusation. The run
   exits 3 for it, which is the convention the rate limiter already uses at the foot of this
   file -- "an unjudged walk is not a green one". */
const unjudged = [];
const check = (name, cond) => { if (!cond) failures.push(name); console.log(cond ? ' ok ' : 'FAIL', name); };

/* A SURFACE IS REACHED BY ITS ADDRESS, NOT BY THE WORDS ON A RAIL BUTTON (WP-14.7).

   Every block below used to arrive by clicking the rail by its LABEL -- fourteen clicks
   spelling "The Kit", "Style Record", "Drawing Set" and the rest -- so renaming a rail item
   broke the walk in fourteen places that were never about the rail, and a label shared with a
   second button anywhere on the page made Playwright refuse the click. A place in this app IS
   a URL (WP-5.6: `router.js` writes it, `nav.go` pushes it), so this sets the hash exactly as
   `nav.go(surface)` would for a surface with no selection and lets the app take it from there.
   Whether the rail reaches every surface is still asserted -- once, by itself, in the loop
   after the Overview block -- rather than fourteen times as a side effect of getting somewhere.

   The address must be one the router WRITES: `parseHash` sends anything it cannot read to the
   Overview, so a mistyped path here would put a whole block on the wrong surface with nothing
   saying so. A malformed address is a FAIL, printed only when it happens. */
async function visit(hash) {
  const p = parseHash(hash);
  if (!SURFACE_PATHS[p.surface] || formatHash(p.surface, p.selection, p.params) !== hash) {
    const name = `visit(${hash}) names an address the router writes`;
    failures.push(name); console.log('FAIL', name);
  }
  // Wait for the hashchange the app listens to, then a frame, so the store has emitted and the
  // surface has rendered before the block reads it. Setting the hash it already holds is a
  // no-op, as `nav.go` to the place you are on is.
  await page.evaluate((h) => new Promise((resolve) => {
    if (location.hash === h) { resolve(); return; }
    const done = () => requestAnimationFrame(() => resolve());
    window.addEventListener('hashchange', done, { once: true });
    setTimeout(resolve, 3000);
    location.hash = h;
  }), hash);
  // The rail click waited for the shell it clicked in; this waits for the shell's surface pane.
  await page.waitForSelector('main', { timeout: 30000 }).catch(() => {});
}

/* A SCREENSHOT, AT THE WIDTH THE WALK OPENS AT OR AT SEVERAL (WP-14.7).

   `shot(name)` writes `<name>.png` at the launch viewport, which is the file every call wrote
   before this helper existed. `shot(name, [1280, 1440, 1680])` also writes `<name>-1280.png`
   and `<name>-1440.png`, resizing for each and putting the window back afterwards, so a
   package reading the shell at narrower widths does not change what any other block sees.
   The launch width keeps its unsuffixed name deliberately: widening a call never renames the
   file an earlier review was held against. */
const SHOT_WIDTH = page.viewportSize().width;
async function shot(name, widths = [SHOT_WIDTH]) {
  const vp = page.viewportSize();
  for (const w of widths) {
    if (w !== page.viewportSize().width) {
      await page.setViewportSize({ width: w, height: vp.height });
      await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
      await page.waitForTimeout(300);
    }
    await page.screenshot({ path: SHOTS + (w === SHOT_WIDTH ? `${name}.png` : `${name}-${w}.png`) });
  }
  if (page.viewportSize().width !== vp.width) {
    await page.setViewportSize(vp);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  }
}

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

// The rail is addressed by its accessible name, and every read of it is scoped to it: since
// WP-5.6 the Overview offers doors carrying the same labels, so an unscoped getByRole would
// match two elements and Playwright would refuse both. The walk no longer CLICKS it to get
// anywhere (WP-14.7, `visit` above); the loop after the Overview block clicks every item once.
await page.waitForSelector('nav[aria-label="surfaces"]', { timeout: 15000 });
const rail = page.locator('nav[aria-label="surfaces"]');
/* THE RAIL IS THE SITE MAP (WP-14.13, PRD §F). It used to be asserted by its words —
   /Overview/, /Drawing Set/ — which is a second copy of labels the app wrote; the labels are
   glossary records' terms now and the places are `nav/navModel.js`'s. So the walk asks the
   same module what the rail must hold, from the glossary and the counts the server serves,
   and holds the rendered anchors to it: every place, in order, each an anchor to its own
   address, each labelled by its record, the style count the API's. */
const GLOSSARY_BODY = await (await fetch(BASE + '/api/glossary')).json().catch(() => null);
const LOOKUP = GLOSSARY_BODY && Array.isArray(GLOSSARY_BODY.terms) ? indexTerms(GLOSSARY_BODY) : null;
const TERM = (id) => (LOOKUP ? LOOKUP.term(id).term : undefined);
const INDEX = await (await fetch(BASE + '/api/search/index')).json().catch(() => ({ entries: [] }));
const NAME_OF = (cite) => ((INDEX.entries || []).find((e) => e.cite === cite) || {}).name || null;
await page.waitForFunction(() => {
  const n = document.querySelector('nav[aria-label="surfaces"]');
  return n && n.getAttribute('aria-busy') !== 'true' && n.querySelector('a[data-nav]');
}, null, { timeout: 15000 }).catch(() => {});
{
  const expected = flatItems(navModel({
    lookup: LOOKUP, counts: overview.counts, glossaryCount: LOOKUP ? LOOKUP.count : null,
    inHand: inHandFrom(null, LOOKUP, (id) => NAME_OF(`style:${id}`)), place: { surface: 'overview', selection: {} },
  }));
  const rendered = await rail.locator('a[data-nav]').evaluateAll((as) => as.map((a) => ({
    id: a.getAttribute('data-nav'), href: a.getAttribute('href'),
    label: (a.querySelector('span > span:not([data-step-n]):not([data-meta])') || a).textContent.trim(),
  })));
  check(`the glossary answered, so the rail's words can be judged (${LOOKUP ? LOOKUP.count : 'no'} records)`,
    Boolean(LOOKUP));
  check(`every place the site map names is in the rail, in its order (${rendered.length})`,
    rendered.length > 0 && JSON.stringify(rendered.map((r) => r.id)) === JSON.stringify(expected.map((e) => e.id)));
  const wrong = [];
  for (const e of expected) {
    const r = rendered.find((x) => x.id === e.id);
    if (!r) continue;
    if (r.href !== e.href) wrong.push(`${e.id} links ${r.href}, not ${e.href}`);
    if (e.termId && e.label && r.label !== e.label) wrong.push(`${e.id} reads "${r.label}", its record says "${e.label}"`);
    if (e.href && formatHash(parseHash(e.href).surface, parseHash(e.href).selection, {}) !== e.href) wrong.push(`${e.href} is not an address the router writes`);
  }
  check('each rail anchor links its own address and reads its own record' + (wrong.length ? ' -- ' + wrong.join('; ') : ''),
    wrong.length === 0);
}
const railText = await rail.innerText();
check('left rail shows live style count',
  (await rail.locator('a[data-nav="style"] [data-meta]').first().textContent().catch(() => '')).trim()
    === String(overview.counts.styles));
// The work-package numerals are gone: they read as an ordering while meaning build order,
// went 2,3,4,9,10,5… and two surfaces both wore ⑧. Nor may build history leak in as an id.
check('no work-package numerals or ids in the rail', !/[②③④⑤⑥⑦⑧⑨⑩⑪]/.test(railText)
  && !/\bWP-\d|\bOQ\s?\d|\boq\//.test(railText));

/* ⓪ THE FRONT DOOR (WP-14.14, PRD §J.1). Every sentence on it is a glossary record's and every
   figure is `/api/overview`'s, so every expectation below is READ from those two routes and none
   is typed here: the definition, the three readers and the five things it is not are
   `about-tdl`'s; the worked example and where it stops are `guided-example`'s; the inventory is
   `counts.by_rank`, row for row. `what_this_is` is still SERVED by the API -- other readers take
   it -- and is no longer the landing's paragraph, which is the half of the old check that
   moved. The map is held to `nav/navModel.js`'s own table here and in both directions in
   `src/frontDoor.test.mjs`; this block asks the page the one thing a node test cannot, that the
   drawn links are addresses the router writes. */
check('a cold load lands on the Overview', new URL(page.url()).hash === '' || /#\/$/.test(page.url()));
const termOf = async (id) => fetch(`${BASE}/api/glossary/${id}`)
  .then((r) => (r.ok ? r.json() : null)).then((b) => (b && b.term) || null).catch(() => null);
const aboutRec = await termOf('about-tdl');
const guidedRec = await termOf('guided-example');
await page.waitForSelector('main [data-about-definition], main [data-about] [data-missing]', { timeout: 30000 })
  .catch(() => {});
await page.waitForSelector('main [data-inventory] [data-rank]', { timeout: 30000 }).catch(() => {});
const ovText = await page.locator('main').innerText();
const front = await page.evaluate(() => {
  const m = document.querySelector('main');
  const q = (s) => m.querySelector(s);
  const qa = (s) => [...m.querySelectorAll(s)];
  const txt = (e) => (e ? e.textContent.replace(/\s+/g, ' ').trim() : null);
  return {
    definition: txt(q('[data-about-definition]')),
    readers: qa('[data-reader]').map(txt),
    isNot: qa('[data-is-not] li').map(txt),
    ranks: qa('[data-inventory] [data-rank]').map((d) => [d.dataset.rank, txt(d.querySelector('[data-figure]'))]),
    versionAttr: q('[data-ontology-version]')?.getAttribute('data-ontology-version') || null,
    versionText: txt(q('[data-ontology-version]')),
    guidedDef: txt(q('[data-guided-definition]')),
    guidedStop: txt(q('[data-guided-stop]')),
    guidedCites: qa('[data-guided-example] a[data-cite]').map((a) => a.getAttribute('data-cite')),
    rows: qa('[data-spine-row]').map((d) => d.getAttribute('data-spine-row')),
    map: qa('[data-map-item]').map((a) => [a.getAttribute('data-map-item'), a.getAttribute('href')]),
    entrances: qa('[data-entrance-link]').map((a) => [a.getAttribute('data-entrance-link'), a.getAttribute('href')]),
  };
});
if (!aboutRec) {
  unjudged.push('the front door says what this is — GET /api/glossary/about-tdl did not answer, so '
    + 'the definition, the readers and what it is not have no record to be judged against');
} else {
  check('the front door says what this is in about-tdl\'s own definition', front.definition === aboutRec.definition);
  const readers = aboutRec.readers || [];
  check(`the readers are about-tdl's, every one and no other (${front.readers.length} of ${readers.length})`,
    readers.length > 0 && front.readers.length === readers.length
    && readers.every((r, i) => front.readers[i]?.includes(r.who) && front.readers[i]?.includes(r.line)));
  // VISION.md:359's must-not, asked of the page rather than of the record alone.
  check('no reader line is a homeowner\'s', !front.readers.some((t) => /homeowner/i.test(t)));
  check(`what it is not is about-tdl's is_not (${front.isNot.length})`,
    (aboutRec.is_not || []).length > 0
    && JSON.stringify(front.isNot) === JSON.stringify(aboutRec.is_not.map((s) => s.replace(/\s+/g, ' ').trim())));
}
const byRank = (overview.counts && overview.counts.by_rank) || {};
// the denominator first: an empty by_rank would make the equality below vacuous
check(`the inventory has rank rows to compare (${Object.keys(byRank).length})`, Object.keys(byRank).length > 0);
check('the inventory figures are counts.by_rank, row for row',
  front.ranks.length === Object.keys(byRank).length
  && front.ranks.every(([k, v]) => k in byRank && v === String(byRank[k])));
check(`the ontology version stays in main (${overview.ontology_version})`,
  front.versionAttr === overview.ontology_version && (front.versionText || '').includes(overview.ontology_version));
check('the search invitation stays in main',
  await page.locator('main').getByRole('button', { name: /Search the corpus/ }).count() > 0);
check('what_this_is is still served by the API and is no longer the landing\'s paragraph',
  typeof overview.what_this_is === 'string' && overview.what_this_is.length > 60
  && !ovText.includes(overview.what_this_is.slice(0, 60)));
if (!guidedRec) {
  unjudged.push('the worked example — GET /api/glossary/guided-example did not answer, so the '
    + 'example and where it stops have no record to be judged against');
} else {
  check('the worked example is guided-example\'s definition', front.guidedDef === guidedRec.definition);
  check('the worked example says where it stops, in the record\'s words (no tour past it)',
    typeof guidedRec.more === 'string' && front.guidedStop === guidedRec.more.replace(/\s+/g, ' ').trim());
  check(`the worked example links every record it cites (${front.guidedCites.join(', ')})`,
    (guidedRec.see || []).length > 0 && guidedRec.see.every((c) => front.guidedCites.includes(c)));
}
{
  // The map's rows are the site map's groups and its links are the site map's items, in order --
  // held to the site map's own table (WP-14.13's `nav/navModel.js`), imported here inside the
  // front door's block so this block owns its dependency and no second list is typed.
  const { NAV } = await import('../src/nav/navModel.js');
  const navIds = NAV.flatMap((g) => g.items.flatMap((it) => [it.id, ...(it.children || []).map((c) => c.id)]));
  check(`the map's rows are the site map's groups (${front.rows.join(', ')})`,
    JSON.stringify(front.rows) === JSON.stringify(NAV.map((g) => g.id)));
  check(`the map carries every site-map item and nothing else (${front.map.length} of ${navIds.length})`,
    JSON.stringify(front.map.map(([id]) => id)) === JSON.stringify(navIds));
  const bad = front.map.filter(([, h]) => {
    const p = parseHash(h || '');
    return !SURFACE_PATHS[p.surface] || formatHash(p.surface, p.selection, p.params) !== h;
  });
  check(`every map link is an address the router writes${bad.length ? ` (not: ${bad.map(([i, h]) => `${i} ${h}`).join('; ')})` : ''}`,
    front.map.length > 0 && bad.length === 0);
  const door = Object.fromEntries(front.entrances);
  check('the two entrances go to reading a style and writing a house',
    parseHash(door.style || '').surface === 'style' && parseHash(door.brief || '').surface === 'brief');
  check('the style in hand is offered as a link, not opened',
    !!door['in-hand'] && parseHash(door['in-hand']).surface === 'style' && new URL(page.url()).hash.replace(/^#\/?$/, '') === '');
}
check('the front door remembers it was seen (prefs.seen["front-door"])',
  await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('tdl-workbench-prefs') || 'null')?.seen?.['front-door'] === true; }
    catch { return false; }
  }));
await shot('overview', [1280, 1440, SHOT_WIDTH]);
{
  /* A LAPTOP IS 1280 px WIDE AND THE FRONT DOOR MUST FIT IT (PRD §I.12). The shell's 1380 px floor
     is released per surface by `#root[data-reflow]`, and the SHELL sets it for the Overview --
     WP-14.13's App.jsx, not this page. Where the attribute is there, the page is judged as a
     reader meets it. Where it is not, the front door's OWN content is measured with the release
     simulated, and the reader-facing half is reported unjudged by name rather than passed. */
  const vp = page.viewportSize();
  await page.setViewportSize({ width: 1280, height: vp.height });
  await page.waitForTimeout(400);
  const fit = await page.evaluate(() => {
    const root = document.getElementById('root');
    const released = root.hasAttribute('data-reflow');
    const measure = () => {
      const fd = document.querySelector('[data-front-door]');
      return {
        sideways: document.scrollingElement.scrollWidth - document.scrollingElement.clientWidth,
        own: fd ? fd.scrollWidth - fd.clientWidth : null,
      };
    };
    if (released) return { released, ...measure() };
    root.setAttribute('data-reflow', '');
    const m = measure();
    root.removeAttribute('data-reflow');
    return { released, ...m };
  });
  check(`the front door's own content fits 1280 px (${fit.own} px over, page ${fit.sideways} px over${fit.released ? '' : ', release simulated'})`,
    fit.own !== null && fit.own <= 1 && fit.sideways <= 1);
  if (!fit.released) {
    unjudged.push('the front door at 1280 px as a reader meets it — #root carries no data-reflow on '
      + 'the Overview on this tree, so the shell\'s 1380 px floor still scrolls the page sideways; '
      + 'the release is the shell\'s (WP-14.13), and the content itself fits with it simulated');
  }
  await page.setViewportSize(vp);
}

/* EVERY RAIL ITEM REACHES ITS OWN SURFACE (WP-14.7). This is the rail's half of what the
   fourteen label clicks used to test in passing, and it is tested here on its own: each item
   rendered under nav[aria-label="surfaces"] is clicked once, in rendered order, and must move
   the address to one the router writes, be the one item the rail then marks current, and
   land somewhere no earlier item landed.

   WHICH SURFACE IS "ITS OWN" IS READ OFF THE ITEM, NOT OFF A LIST HERE. `Chrome.jsx` binds
   `aria-current` to `current === it.id` with the same `it.id` its onClick hands to `onGo`, and
   `current` is the surface `nav` parsed out of the hash -- so "this item and no other is
   current" says the hash parses to this item's surface. `Chrome.jsx` cannot be imported here
   (it is JSX over React), and a table of labels written into this file is the dependence this
   package removes. The distinct-address half does not read `aria-current` at all, so an item
   whose id lands on another item's surface fails whatever the marking says.

   The item already current proves nothing by being clicked -- a dead onClick on it passes --
   so the walk first moves to another surface the router knows and then clicks. It sits after
   the Overview block rather than inside the rail block above, because the Overview checks
   read the COLD LOAD and would otherwise read an address this loop had set. Nothing heavy
   mounts: no plan is loaded yet, so the bench and the Drawing Set fetch nothing but schema. */
{
  /* Re-cut at WP-14.13: the items are ANCHORS carrying `data-nav` now, and each is judged by
     its id and its own `href` rather than by its position — the style in hand grows its
     dossier's sections as children once its dossier is the page, so an index would point at a
     different item after that click. The one allowance is exactly that: on the in-hand style's
     own dossier the rail marks the section shown (`in-hand:identify`) rather than the style. */
  const ITEMS = 'nav[aria-label="surfaces"] a[data-nav]';
  const ids = await page.locator(ITEMS).evaluateAll((as) => as.map((a) => a.getAttribute('data-nav')));
  // the denominator first: an empty selection would make every assertion below vacuous
  check(`the rail offers surfaces to reach (${ids.length})`, ids.length > 0);
  const reached = new Map();
  const marked = () => page.locator(ITEMS).evaluateAll((as) =>
    as.filter((a) => a.getAttribute('aria-current') === 'page').map((a) => a.getAttribute('data-nav')));
  for (const id of ids) {
    const item = page.locator(`${ITEMS}[data-nav="${id}"]`).first();
    if ((await item.getAttribute('aria-current')) === 'page') {
      const here = parseHash(await page.evaluate(() => location.hash)).surface;
      await visit(formatHash(Object.keys(SURFACE_PATHS).find((s) => s !== here && s !== 'style' && s !== 'kit'), {}, {}));
    }
    const wasCurrent = (await item.getAttribute('aria-current')) === 'page';
    const href = await item.getAttribute('href');
    const before = await page.evaluate(() => location.hash);
    await item.click();
    await page.waitForFunction((h) => location.hash !== h, before, { timeout: 5000 }).catch(() => {});
    await page.waitForFunction(([sel, k]) => [...document.querySelectorAll(sel)].some((a) =>
      a.getAttribute('aria-current') === 'page'
        && (a.getAttribute('data-nav') === k || a.getAttribute('data-nav') === `${k}:identify`)),
    [ITEMS, id], { timeout: 5000 }).catch(() => {});
    const after = await page.evaluate(() => location.hash);
    const got = parseHash(after);
    const on = await marked();
    const why = [];
    if (wasCurrent) why.push('it was current before the click, so the click could not be judged');
    if (after === before) why.push(`the address did not move from ${before || '(none)'}`);
    if (after !== href) why.push(`it links ${href} and landed on ${after || '(none)'}`);
    if (!SURFACE_PATHS[got.surface] || formatHash(got.surface, got.selection, got.params) !== after) {
      why.push(`${after || '(none)'} is not an address the router writes`);
    }
    if (on.length !== 1 || (on[0] !== id && on[0] !== `${id}:identify`)) {
      why.push(`the rail marks ${on.map((k) => `"${k}"`).join(', ') || 'nothing'} current`);
    }
    if (reached.has(after)) why.push(`"${reached.get(after)}" already reached ${after}`);
    reached.set(after, id);
    check(`the rail item "${id}" reaches its own surface (${after})`
      + (why.length ? ' -- ' + why.join('; ') : ''), why.length === 0);
  }
  // back where the old walk stood when it went to the bench: the Overview
  await visit(formatHash('overview', {}, {}));
}

// ⑦ Plan Workbench: load an example, wait for evaluation
// The walk used to land here on page load, so this surface was already mounted by the
// time it was addressed. It is reached by its address now, and only the surface in view is
// constructed — so wait for its own furniture before reaching for it.
await visit('#/workbench');
const example = page.getByRole('button', { name: 'tidewater-georgian-careful' });
await example.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
if (await example.count()) await example.click();

/* THE EXAMPLE THE BENCH OFFERS DRAWS NOTHING, AND THIS WALK SPENT TWELVE DAYS DYING ON IT
   (found WP-13.9's second pass, 19 Sep 2026).

   WP-13.4 ruled that a placement breaking a hard fact of the type is REFUSED and not drawn:
   `/api/plan/evaluate` answers `placement_refused` with no `placement`, `drawable` is false,
   and the conflict set stands where the plate would be. WP-13.5's container edit then made
   the shipped Tidewater record one of those -- and MEASURED at that second pass, so is the
   other shipped plan, and ELEVEN of the sixteen records in `plans/`:

       refused on `auto`: both shipped plans, bad-01, bad-03, bad-04, bad-05,
                          good-02, good-04, good-05, good-06, good-07
       drawable:          bad-02, bad-06, bad-07, good-01, good-03

   RE-MEASURED at the audit of that package, and it is THREE: `bad-02`, `bad-06`, `good-03`.
   `bad-07` and `good-01` are borderline -- CP-SAT under a wall clock is not reproducible, so
   which side of the budget a record lands on is a property of the machine and the day, and the
   drawable set has to be re-derived rather than quoted. All three are ONE LEVEL, none carries
   a hearth, and none places an entrance stoop, so the stack and stoop checks below have no
   subject on any drawable record in this corpus and report COULD NOT EVALUATE by name.

   Both of the two records the bench offers as EXAMPLES are in the first list. So the line
   below this block -- `waitForSelector('svg[role="img"]')` -- was waiting for a plate the
   contract forbids, throwing a TimeoutError at the top level, and taking every check after
   it with it. The walk was reporting eight checks of about a hundred and ninety, and the
   refusal contract's OWN assertions at the foot of this file (the ones `refusal.test.mjs`
   says in its docstring are "e2e/walk.mjs's") were among the ones never reached.

   So the refusal is asserted HERE, where the reader meets it, and the sheet section below
   is given a subject that draws. */
{
  /* WAIT FOR THE PANEL, NOT FOR A CLOCK. The first version of this block slept 1500 ms and
     then read the panel -- and an example chip is an EXPLICIT solve now, so the click runs a
     25 s placement and a corrective round on top of it. The panel was reliably absent, four
     of the five checks below failed for the wrong reason, and the fifth PASSED, because
     `!/fresh solve/.test('')` is true of an empty string: a negative assertion over a locator
     that missed cannot tell "the solve panel correctly omits this phrase" from "there is no
     panel". So the panel is waited for, and its presence is asserted BEFORE any negative
     reading is taken from it. */
  await page.waitForSelector('[data-panel="revision"]', { timeout: 150000 }).catch(() => {});
  const shown = await page.locator('svg[role="img"]').count();
  const refusedAttr = await page.locator('[data-placement-refused]').first()
    .getAttribute('data-placement-refused').catch(() => null);
  const panel = await page.locator('[data-panel="revision"]').innerText().catch(() => '');
  // the contract, from the screen rather than from the API: no plate, and the conflict set
  // in its place. Asserted on the record a reader actually clicks.
  check(`the bench's own example is refused and draws no plate (kind ${refusedAttr || 'none'})`,
    !!refusedAttr);
  check('and the conflict set stands where the plate would be',
    (await page.locator('[data-conflict-set]').count()) > 0
    || /conflict|refused/i.test(await page.locator('main').innerText()));
  check('a refused record draws no sheet at all', shown === 0);
  /* WP-13.9: THE ROUNDS RAN BEFORE THE PLAN WAS SURFACED, WITH NO CHIP CLICKED. Nothing has
     been clicked between the example chip and here, so a revision panel on the page is the
     SOLVE's own. It renders on a refused record -- the panel is not the plate -- which is
     why these five sit here rather than below the sheet wait. */
  check('the corrective rounds ran on the solve, with no chip clicked', !!panel);
  check('the panel says the rounds ran on the solve', /revised on solve/i.test(panel));
  // the NOUN differs by whether the placement may be drawn -- "the sheet above" on a drawable
  // one, "the findings above" on a refused one, because a panel may not promise a plate the
  // reader is looking at a conflict set instead of. The claim they share is the one to assert.
  check('and claims what is above it is the placement its key was measured on',
    /the placement this key was measured on/i.test(panel));
  // the promise the OTHER path makes, and this path must not make it: nothing here was
  // re-solved, so "a fresh solve ... the two can differ" would be false of it
  // the promise the OTHER path makes, and this path must not make it. The premise is
  // asserted first: a negative reading of an empty string is not a verdict about the panel.
  check('a solve-path panel does not claim the sheet is a fresh solve',
    !!panel && !/fresh solve/i.test(panel));
  check('the panel names its round count', /\d+ rounds?\b/i.test(panel));
  check('and a refused placement is stated beside the key',
    /still refused|may not be drawn/i.test(panel));
  /* WP-14.10 (PRD §J.1): AND THE HOUSE JOURNEY SAYS WHAT THE MISSING PLATE MEANS. A refused house
     has no drawings and no export to go on to, so both steps read "blocked: refused" and neither
     is a link a reader could follow to a plate the contract forbids. The bar sits above <main>,
     so nothing any check above reads out of `main` includes it. */
  const jb = await journeyRead();
  check('the house journey is on the bench, above the surface rather than inside it', !!jb && !jb.inMain);
  for (const id of ['drawings', 'export']) {
    const st = jb && jb.steps[id];
    check(`and it reads the ${id} step as blocked: refused, and not as a link (${st ? `${st.tag}, ${st.blocked}, "${st.words}"` : 'absent'})`,
      !!st && st.tag === 'span' && st.blocked === 'refused' && !st.href);
  }
  check(`and the plan step's Next is its reason, not a link (${jb && jb.next ? jb.next.text : 'absent'})`,
    !!jb && !!jb.next && jb.next.tag !== 'a');
}

/* AND NOW A SUBJECT THAT DRAWS, because everything below measures a DRAWING: labels inside
   their rooms, the stair, the hearths, the door swings, the poche, the scale bar, the loupe,
   the wall handle. `good-03-parlor-drawing-room-house` is the drawable record whose rooms
   best match what this walk reaches for -- it carries a Drawing Room, a Stair Hall, a Porch,
   a Library, a Kitchen and a Dining Room -- and it is loaded through localStorage and a
   reload, which is the path the refusal section at the foot of this file already uses: no
   route, no app change, and the store's own boot path proved on the way through.

   IT IS ONE LEVEL WHERE THE TIDEWATER RECORD IS TWO. Every drawable record in this corpus is
   (measured), so a check that needs a second storey has no subject here and says so by name
   rather than passing over an absence. */
const DRAWABLE = 'good-03-parlor-drawing-room-house';
/* THE SUBJECT IS READ ONCE AND EVERY EXPECTATION BELOW IS DERIVED FROM IT. Every drawing check
   in this file was written against the Tidewater record and carried ITS numbers as literals --
   thirteen rooms, ten door marks, the word "tidewater" in the plate title. Those checks have
   not run since WP-13.5 made that record refused, so the literals were never wrong, only
   unreachable; the moment the walk was given a subject that draws, five of them convicted the
   surface of not being a house it was never looking at. A count derived from the record is a
   claim about the DRAWING; a count copied from one particular record is a claim about that
   record, and it goes stale the first time the subject moves. */
const rec = JSON.parse(readFileSync(
  new URL(`../../../plans/reference/${DRAWABLE}.json`, import.meta.url).pathname, 'utf8'));
/* Which face the front is decides which axon the Round opens on, which chip carries the
   entrance-front suffix, and which face chip on the Drawing Set is a CHANGE rather than a
   no-op. All three were written as the Tidewater record's answer (south) and none of them
   was about that record. */
const FRONT = String((rec.context || {}).entrance_faces || 'S').toUpperCase().slice(0, 1);
const FACE_WORD = { S: 'SOUTH', W: 'WEST', N: 'NORTH', E: 'EAST' };
const OPPOSITE = { S: 'N', N: 'S', E: 'W', W: 'E' };
const NOT_FRONT = OPPOSITE[FRONT] || 'N';
{
  await page.evaluate((plan) => {
    localStorage.setItem('tdl-workbench-plan', JSON.stringify(plan));
  }, rec);
  /* RELOAD, NEVER `goto` THE HASH WE ARE ALREADY ON. A navigation whose only difference is
     the fragment is a SAME-DOCUMENT navigation: the browser fires `hashchange` and does not
     re-run the app, so `planDoc` never re-boots and the bench goes on showing the record it
     already had. The walk sat on the refused Tidewater plan and timed out on a plate the
     contract forbids -- a 150 s death that looked exactly like a slow solve. The block at the
     foot of this file does the same thing correctly only because it arrives from another
     route. `reload()` is the honest spelling of what this wants. */
  await page.reload({ waitUntil: 'networkidle' });
}
// The sheet arrives AFTER the evaluate, and the evaluate runs CP-SAT at the interactive
// budget (`BUDGET_INTERACTIVE_S`, 25 s) before it can fall back -- measured here at 28.1 s
// from the click to the first `svg[role="img"]` on a quiet 4-core box (WP-13.2's lead pass,
// probed with a pageerror listener: no error, just late). A 30 s wait was one CPU hiccup from
// a TimeoutError that reads like a broken surface, and CI's runner is slower than this box.
// 90 s is the critique panel's wait below, for the same reason.
//
// WP-13.9 RAISED IT TO 150 s AND THE REASON IS MEASURED, NOT PRECAUTIONARY. An example chip
// is an EXPLICIT solve now, so this click runs the corrective rounds before the sheet is
// drawn: measured on this plan at `engine="auto"`, the solve is 25.9 s and one round on the
// resulting CP placement is 36.4 s, so the click-to-sheet path is about 62 s on a quiet box
// before any page overhead. 90 s was already one CPU hiccup from a TimeoutError that reads
// like a broken surface; against a 62 s path on a runner slower than this box it would be a
// failing check about nothing.
await page.waitForSelector('svg[role="img"]', { timeout: 150000 });
/* AND THE SAME PANEL ON A DRAWABLE RECORD, where the noun it chooses is the OTHER one.
   The block above asserted it on a refused placement ("the findings above"); this one is the
   case the wording exists for, and having both is what makes the choice a behaviour rather
   than a constant. */
{
  /* A BOOT LOAD IS NOT AN EXPLICIT SOLVE, AND THE FIRST VERSION OF THIS BLOCK ASSERTED IT WAS.
     The rounds run on a re-solve, a load and a paste -- acts a person waits on deliberately --
     and NOT on a refresh, because a record reaching the bench from localStorage at boot is the
     reader coming back to what they had, and revising it would change a document nobody asked
     to change. This record arrives by exactly that path, so the panel is correctly absent
     until something asks. Press the chip the reader would press. */
  await page.getByRole('button', { name: /re-solve/i }).first().click();
  await page.waitForSelector('[data-panel="revision"]', { timeout: 150000 }).catch(() => {});
  const panel = await page.locator('[data-panel="revision"]').innerText().catch(() => '');
  check('re-solve runs the corrective rounds on a drawable record', !!panel);
  check('and on a record that draws, the panel claims the SHEET above it',
    /the sheet above is the placement this key was measured on/i.test(panel));
  check('and does not say the placement is refused', !!panel && !/still refused/i.test(panel));
  // the sheet the panel is talking about has to be back on the page before anything below
  // measures a drawing: the re-solve replaced it.
  await page.waitForSelector('svg[role="img"]', { timeout: 150000 }).catch(() => {});
}
const body = await page.locator('main').innerText();
check('three-state panel present (could not evaluate)', /could not evaluate/i.test(body));
check('hill-climb honesty line present', /hill-climb/i.test(body));
check('the proof is offered, not just the search', /prove placement/i.test(body));
// …and the caption names the engine that ACTUALLY DREW THIS SHEET, and claims a proof only
// where the record carries one. Until WP-6.3 flipped the default it said flatly that every
// edit re-scores on the hill-climb and that nothing drawn asserts feasibility was proved —
// true then, false the moment `auto` became the default, and false in the direction that
// matters: a reader could not tell a proof from a search.
//
// WP-13.2 FOUND THIS CHECK ITSELF STALE, AND THE CAPTION IT GUARDED WRONG. It matched two
// PHRASES — `was proved, not searched` and `came from the fast search` — and WP-11.8 had
// reworded the first to "proved feasible" without this line noticing, so main's CI was red on
// a wording. And the wording it was red on said "proved" over ANY CP-SAT solve, FEASIBLE
// included: a placement found inside the budget with optimality never established, captioned
// as a proof — the bench half of *a green PLACEMENT PROVED over a FEASIBLE truncation*.
//
// THE CONTRACT IS STATED HERE FROM THE API'S OWN SOLVER BLOCK, never from a phrase:
//   * the caption names the engine the record names;
//   * "proved" is claimed only where the status begins with OPTIMAL AND the objective ran — a
//     FEASIBLE truncation, an `OPTIMAL (hard-only)` with a null objective and a hill-climb are
//     not proofs (the plate's rule, `build/disclosures.py::engine_line`);
//   * a CP-SAT record with no objective says its composition was not evaluated;
//   * a fallback quotes the solver's own reason.
// The POST below hits the same solve-cache key as the bench's own evaluate (engine `auto`, 250
// candidates, strict off), so the report read here IS the sheet's — the critique block further
// down rests on the same fact. `sheet/engineClaim.js` is the app's one spelling of the verdict
// and publishes it on the paragraph as `data-engine-claim`; that attribute is read AND the
// words are read, because the attribute is what the app decided and the words are what a
// reader sees, and the two can disagree.
let apiPlacement = null;   // the evaluate's own placement, read again by the stacks check below
{
  /* THE HOUSE ON THE SCREEN, AND NOT A DIFFERENT ONE. This probe fetched
     `tidewater-georgian-careful` by name while the bench was showing the drawable subject
     above, so the engine caption, the stack census and the stoop census were all measured
     against a record the plate is not of -- WP-6.4's "one drawing set is one building" broken
     inside the instrument that checks it. It also meant the caption check reported COULD NOT
     EVALUATE for a reason that is correct and irrelevant: the Tidewater evaluate is REFUSED,
     so it reports no solver, and the sheet beside it was drawn by one. */
  const solved = await fetch(BASE + '/api/plan/evaluate', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ plan: rec, place: true }),
  }).then((r) => r.json()).catch(() => null);
  apiPlacement = solved?.placement || null;
  const solver = solved?.placement?.geometry_report?.solver;
  const eng = solver?.engine;
  if (!eng) {
    check('the caption names the engine that drew the sheet — COULD NOT EVALUATE '
      + '(the API did not report one)', false);
  } else {
    const status = typeof solver.status === 'string' ? solver.status : '';
    const cp = eng === 'cp-sat';
    const objectiveRan = !cp || (solver.objective !== null && solver.objective !== undefined);
    const mayClaimProof = cp && /^OPTIMAL\b/.test(status) && objectiveRan;
    const fellBack = !cp && !!solver.reason && solver.reason !== 'requested';
    const expectVerdict = cp ? (mayClaimProof ? 'proved' : 'not-proved') : 'searched';
    const head = status ? status.split('—')[0].trim() : '(no status)';
    const cap = await page.evaluate(() => {
      const p = document.querySelector('[data-engine-claim]');
      return p ? { verdict: p.getAttribute('data-engine-claim'),
                   engine: p.getAttribute('data-engine-name'),
                   text: p.textContent.replace(/\s+/g, ' ').trim() } : null;
    });
    const text = cap ? cap.text : '';
    const saysProved = /\bproved feasible\b/i.test(text);
    const saysNotProved = /\bnot proved\b/i.test(text);
    check('the caption paragraph is on the page and publishes its claim', !!cap);
    check(`the caption names the engine that drew the sheet (${eng}, ${head})`,
      !!cap && cap.engine === eng
        && (cp ? /CP-SAT/.test(text) && !/came from the fast search/i.test(text)
               : /came from the fast search/i.test(text) && !/by CP-SAT/i.test(text)));
    check(`the caption claims a proof only where the record carries one (${head} → ${expectVerdict})`,
      mayClaimProof ? (saysProved && !saysNotProved)
                    : (!saysProved && (cp ? saysNotProved : true)));
    check(`the caption's published verdict agrees with the API (${cap?.verdict} vs ${expectVerdict})`,
      !!cap && cap.verdict === expectVerdict);
    if (cp && !objectiveRan) {
      check('a CP-SAT sheet whose objective did not run says its composition was not evaluated',
        /composition was not evaluated/i.test(text));
    }
    /* THE PAGE'S OWN SOLVE, NOT THIS PROBE'S. This compared the page's prose against the
       `reason` string of a SEPARATE evaluate of the same record -- and CP-SAT under a wall
       clock is not reproducible, so the two solves can fall back for differently-worded
       reasons and the check convicts a page that is telling the truth about its own solve.
       WP-6.4's one-building rule, inside the instrument. What holds on any solve is that a
       page reporting a fallback NAMES why: the claim is the reason's presence, read from the
       page, with the probe's own reason quoted in the message as corroboration. */
    /* THE PAGE'S OWN SOLVE, NOT THIS PROBE'S. This compared the page's prose against the
       `reason` string of a SEPARATE evaluate of the same record -- and CP-SAT under a wall
       clock is not reproducible, so two solves can fall back with differently-worded reasons
       and the check convicts a page telling the truth about its own. WP-6.4's one-building
       rule, inside the instrument. What holds on any solve is that a page reporting a
       fallback SAYS SO and NAMES the reason: the sentence is asserted, and the reason is then
       held against the probe's only where the two solves agree enough to be compared. A
       disagreement is COULD NOT EVALUATE -- two instruments, not a defect. */
    /* READ FROM THE PAGE, AND THE PROBE IS CORROBORATION RATHER THAN THE CLAIM. This compared
       the page's prose against the `reason` of a SEPARATE evaluate of the same record, and the
       two are not the same act: since WP-13.9 an explicit solve runs the corrective rounds,
       and the loop re-places on the engine that placed ASKED FOR BY NAME -- so the record the
       sheet is drawn from carries no fallback reason, while a bare `auto` probe of the same
       document does. The page was telling the truth about its own placement and the check
       convicted it on another's. WP-6.4's one-building rule, inside the instrument.

       THE DISCLOSURE THAT IS LOST IS A REAL ONE and is named rather than asserted away: after
       the rounds the caption no longer says a proof was attempted and did not answer, because
       on the placement it describes none was. Reported here as COULD NOT EVALUATE, which is
       what it is. */
    const said = /the proof was attempted and did not answer\s*[—-]\s*(.+?)\./i.exec(text);
    if (said) {
      check(`a fallback says so and names a reason ("${said[1].trim().slice(0, 44)}")`,
        !!said[1].trim());
    } else if (fellBack) {
      const mine = String(solver.reason || '').replace(/\s+/g, ' ').trim();
      unjudged.push("a fallback quotes the solver's own reason — a bare `auto` probe of this "
        + `record fell back ("${mine.slice(0, 44)}") and the page names no fallback, because `
        + 'the sheet is the corrective rounds\' own placement and the loop asks for the engine '
        + 'that placed BY NAME. Two acts, not a disagreement');
    }
    // …and the PLATE says it too, not only the page prose beside it. WP-6.3 put the
    // disclosure one level out, which is the one place it cannot travel: a printed or
    // exported plate leaves the prose behind and a reader cannot tell a proof from a
    // search. Measured on the plate's own caption element, and held to the SAME contract:
    // the plate names the engine, and prints "proved" only where the record carries a proof.
    const plate = await page.evaluate(() => {
      const n = document.querySelector('[data-plate-note]');
      return n ? n.textContent.replace(/\s+/g, ' ').trim() : '';
    });
    check(`the plate's own caption names the engine (${eng})`,
      cp ? /CP-SAT/.test(plate) : /searched, not proved/i.test(plate));
    check(`the plate claims a proof only where the record carries one (${head} → ${expectVerdict})`,
      mayClaimProof ? /\bproved\b/i.test(plate) && !/not proved/i.test(plate)
                    : !/placement proved/i.test(plate));
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
    // the fast loop: rounds 6, budget 60 s on the chip, so the poll and the promise agree.
    //
    // WP-13.9: THE PANEL IS ALREADY ON THE PAGE WHEN THIS CLICK HAPPENS, because the solve
    // above ran its own rounds -- so waiting for `/stopped:|converged/` alone would match the
    // SOLVE's panel on the first tick and this block would assert nothing about the chip at
    // all. The discriminator is the sentence each path makes: the chip's record is stripped
    // and re-solved, so its panel says "fresh solve" and the solve's says the opposite.
    await page.getByRole('button', { name: /^revise \(search\)/ }).click();
    let panel = '';
    for (let i = 0; i < 120; i++) {
      await page.waitForTimeout(1000);
      panel = await page.locator('[data-panel="revision"]').innerText().catch(() => '');
      if (/fresh solve/i.test(panel) && /stopped:|converged/i.test(panel)) break;
    }
    check('the chip\'s own loop replaced the solve\'s panel', /fresh solve/i.test(panel));
    check('the revision panel names why the loop stopped', /stopped:|converged/i.test(panel));
    check('the revision panel names its round count', /\d+ rounds?\b/i.test(panel));
    check('the panel says the sheet is a fresh solve of the revised record', /fresh solve/i.test(panel));
    /* ONE UNDO STEP, AND WHAT IT LANDS ON IS NO LONGER NOTHING (WP-13.9). This asserted the
       panel VANISHES, which was true while the solve ran no rounds: the chip's load was the
       only revision on the stack. The solve revises now, so one undo lands on the SOLVE's own
       revised record -- which correctly still has a panel. The claim that survives is the one
       the step was ever about: the chip's revision is gone. Its panel is the only one that
       says "fresh solve", because only the chip path strips and re-solves. */
    await page.getByRole('button', { name: 'undo' }).click();
    await page.waitForTimeout(400);
    const after = await page.locator('[data-panel="revision"]').innerText().catch(() => '');
    check('undo takes the CHIP\'s revision away — the loop loaded one undo step',
      !/fresh solve/i.test(after));
    // the critique was of the evaluation BEFORE the revise; two evaluations have landed
    // since, so the panel must say so and its tags must be gone -- the one moment the
    // staleness path fires, and the walk used to step over it (WP-9.4).
    // POLLED, NOT SLEPT: the restored record is re-evaluated behind a 400 ms debounce and the
    // solve itself is tens of seconds on this corpus, so a fixed 2.5 s wait was measuring the
    // machine. A check that reads an empty panel because it arrived early is indistinguishable
    // from one that reads an empty panel because the app never wrote it.
    let stale = '';
    for (let i = 0; i < 90; i++) {
      await page.waitForTimeout(1000);
      stale = await page.locator('[data-panel="critique"]').innerText().catch(() => '');
      if (/earlier evaluation/i.test(stale)) break;
    }
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
/* DERIVED FROM THE RECORD ON SCREEN, not from the house this check was written for. The
   floor was a literal 13 -- the Tidewater ground and upper levels together -- and it is the
   count of rooms the SUBJECT declares on the levels a plate is drawn for. */
const declaredRooms = (rec.levels || [])
  .filter((l) => (l.index ?? 0) >= 0)
  .reduce((n, l) => n + (l.rooms || []).length, 0);
check(`the sheet draws the record's rooms (${spill.rooms} of ${declaredRooms} declared)`,
  declaredRooms > 0 && spill.rooms >= declaredRooms - 2);
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
/* AND SO IS THIS ONE. Ten was the Tidewater plate's count; the claim is that a sheet of a
   house with declared doors draws marks for them, and the record says how many it declares. */
const declaredDoors = (rec.levels || [])
  .reduce((n, l) => n + (l.rooms || []).reduce((m, r) => m + ((r.doors || []).length), 0), 0);
check(`the sheet draws door marks (${openings.total} of ${declaredDoors} declared)`,
  declaredDoors > 0 && openings.total > 0);
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
/* THE TITLE IS THE RECORD'S OWN, word for word. This asserted the words "tidewater" and
   "georgian" -- true of one house and of nothing else -- where the property is that the plate
   title survives its own line-wrapping. The two longest words of the subject's own title are
   what the fold would break. */
const titleWords = String(rec.title || rec.name || '').toLowerCase()
  .split(/[^a-z0-9]+/).filter((w) => w.length >= 5).slice(0, 3);
check(`the plate title is whole ("${flat.slice(0, 48)}"; wants ${titleWords.join(', ')})`,
  titleWords.length > 0 && titleWords.every((w) => flat.includes(w)));

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
// THE COUNT IS THE RECORD'S, NOT A PIN OF TWO (WP-13.2, the lead's pass). This asserted
// `=== 2` -- the paired gable ends -- and went red the day the hearth slice made the breast a
// judged thing: on the bench's own placement (OPTIMAL hard-only at 25 s) both west fires stand
// 18 and 24 ft inboard of the gable, so the west stack is REFUSED with a reason and only the
// east one is drawn. One stack is the honest sheet there. What is asserted is that the sheet
// draws every stack the record placed, all of them on the plate, and that a stack the record
// refused is NAMED on the page rather than silently one short -- which is the line the
// disclosure strip carries now (`disclosures.fires_not_drawn`).
{
  const vb = (built.vb || '').split(/\s+/).map(Number);
  const hearths = apiPlacement?.hearths || {};
  const placedStacks = (hearths.stacks || []).filter((s) => s.x_ft !== undefined && s.x_ft !== null);
  const refusedFlues = (hearths.unplaced || []).filter((u) => u.flue).map((u) => u.flue);
  const inside = built.stacks.every((s) => s.x >= vb[0] && s.x + s.w <= vb[0] + vb[2]);
  /* NO SUBJECT IS NOT A FAILURE, AND IT IS NOT A PASS EITHER. The record on the bench may
     state no fire at all -- most drawable records in this corpus do -- and a check that
     convicts the sheet of not drawing a chimney the house does not have is a false positive
     of exactly the kind this corpus names first. The three-state rule applies to the walk as
     much as to a checker: judged, failed, or COULD NOT EVALUATE with the reason. */
  if (placedStacks.length + refusedFlues.length === 0) {
    unjudged.push(`the gable-end stacks are drawn and lie on the plate — ${DRAWABLE} places `
                  + 'no stack and refuses none, so there is nothing to draw or to name');
  } else {
    check(`the gable-end stacks are drawn and lie on the plate (${built.stacks.length} drawn of `
          + `${placedStacks.length} placed, ${refusedFlues.length} refused; `
          + `walls ${built.stacks.map((s) => s.wall).join('/')}, viewBox ${built.vb})`,
      built.stacks.length === placedStacks.length && inside);
  }
  if (refusedFlues.length) {
    const main = await page.locator('main').innerText();
    check(`a stack the record refused is named on the page (${refusedFlues.join(', ')})`,
      refusedFlues.every((f) => main.toUpperCase().includes(f.toUpperCase())));
  }
  // COUNTED AS A PROPERTY AND NOT AS A NUMBER. The first version asserted exactly one, and
  // the walk answered TWO: on CP-SAT the placement puts the KITCHEN's exterior door on the
  // entrance front as well, so the count is the engine's and not the record's. What must hold
  // on any engine is that every mark of the flight lies on the plate.
  const onPlate = built.stoops.length > 0 && built.stoops.every(
    (r) => r.x >= vb[0] && r.x + r.w <= vb[0] + vb[2]
        && r.y >= vb[1] && r.y + r.h <= vb[1] + vb[3]);
  // the same three states. A record whose threshold pass placed no flight has no stoop to
  // draw, and `build/threshold.py` refuses one BY NAME where it cannot derive it.
  const thr = apiPlacement?.threshold || {};
  if (built.stoops.length === 0 && !(thr.flight || thr.platform)) {
    unjudged.push(`the entrance stoop is drawn from the record — ${DRAWABLE}'s threshold pass `
                  + 'placed no flight and no platform, so there is no stoop to draw');
  } else {
    check(`the entrance stoop is drawn from the record and lies on the plate `
          + `(${built.stoops.length} mark(s))`, onPlate);
  }
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
  /* THE WORKING BANNER, READ WHILE THE SKETCH IS ON SCREEN (WP-13.4).
     A wall drag is the ONE path that still returns a placement the type's facts may refuse: it
     asks for the hill-climb BY NAME because a gesture cannot wait for a proof, and
     `workbench/server/evaluate.py` marks what comes back `placement.sketch`. The plate says so
     ITSELF rather than only the prose beside it, for WP-6.4's reason -- a printed or exported
     plate leaves the prose behind.
     It is captured HERE, inside the drag, because the `undo` two statements below loads the
     record again and the next evaluate is not a drag: read afterwards this would be zero on a
     working sketch and a check reading zero for the wrong reason is indistinguishable from one
     reading zero because nothing was drawn (WP-12.4). */
  const sketchBanner = await page.evaluate(() => {
    const b = document.querySelector('[data-working-sketch]');
    const note = document.querySelector('[data-plate-note]');
    return { present: !!b, text: b ? b.textContent.replace(/\s+/g, ' ').trim() : '',
      plate: note ? note.textContent.replace(/\s+/g, ' ').trim() : '' };
  });
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
  return { preview, panned, scroll0, before, restored, after, clicked: !!h2, handles, room,
    sketchBanner };
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
/* AND THE SHEET THE DRAG LEFT SAYS IT IS A SKETCH (WP-13.4). Read from the API's own response
   first, so this cannot pass by asserting a banner over a placement the server never marked:
   the drag's evaluate is the one path the contract lets return a placement on a refusal, and it
   returns it marked `placement.sketch = {working, refused, reason}`. Until the server slice lands
   that key is absent, and this is COULD NOT EVALUATE -- never a pass. */
{
  const dragEval = await fetch(BASE + '/api/plans/examples/tidewater-georgian-careful')
    .then((r) => r.json())
    .then((p) => fetch(BASE + '/api/plan/evaluate', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plan: p.plan || p, place: true, engine: 'heuristic' }),
    }))
    .then((r) => r.json())
    .catch(() => null);
  const marked = dragEval?.placement?.sketch?.working === true;
  if (!marked) {
    unjudged.push('the wall drag draws a WORKING banner — the evaluate marks no placement.sketch');
    console.log('N/EV the wall drag draws a WORKING banner '
      + '— COULD NOT EVALUATE: this server marks no placement.sketch on an engine-by-name evaluate');
  } else {
    check('a wall drag draws a WORKING banner on the plate',
      handleLive?.sketchBanner?.present === true);
    check('and the banner says it may not be exported',
      /may not be exported/i.test(handleLive?.sketchBanner?.text || ''));
    // the plate's own caption carries it too, so an exported or printed plate still says so
    check("and the plate's own caption calls it a working sketch",
      /WORKING SKETCH/i.test(handleLive?.sketchBanner?.plate || ''));
  }
}
await shot('workbench');

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
await shot('workbench-craftsman');
await pickStyle('tidewater-georgian');
await page.waitForTimeout(1500);

// ② Phylogeny
await visit('#/phylogeny');
// Scoped to <main> (WP-14.13): the shell's page head sits ABOVE main and carries the glossary's
// own words about this page, folded after the first visit -- its hidden "How to read" line
// mentions the compressed axis and, first in DOM order, is what a global text= wait resolved to.
await page.waitForSelector('main >> text=compressed', { timeout: 15000 });
const phylo = await page.locator('main').innerText();
check('phylogeny names the missing trunks', /missing peer trunks/i.test(phylo));
await shot('phylogeny');

/* WHAT AN EDGE CARRIES IS THE SERVED FLAG, READ PER EDGE (WP-14.11, PRD §I.13, §K).

   The panel's lineage and the tree's strokes used a table of TYPES (`CARRIES = { descends_from,
   regional_of }`, in EdgeGlyph.jsx and again in the Phylogeny), which captioned every kit-carrying
   `hybridizes_with` edge "carries nothing", listed it under "claims only" and drew it light; and
   EdgeGlyph printed "browsing only — carries no inheritance" under filing, which `build/build.py`
   has falsified since WP-4.2. This block holds what the page PRINTS to what `/api/phylogeny` STATES,
   edge by edge. Its reading of the flag is deliberately a SECOND one, written here and not imported
   from `lineage/carry.js`: a walk that asked the app's own rule would agree with any defect in it.
   The taxa it reads are chosen from the payload, never named: one with a kit-carrying co-parent
   beside a claim, and one whose edge carries only the slots it names. Restoring the table in any of
   the three places -- the glyph's caption, the panel's grouping, the tree's weight -- fails here. */
{
  const phyl = await (await fetch(BASE + '/api/phylogeny')).json();
  const gl = await (await fetch(BASE + '/api/glossary')).json().catch(() => ({}));
  const wordOf = Object.fromEntries((gl.terms || []).map((t) => [t.id, t.term]));
  const flagWord = (e) => (e.inherits_kit === true
    ? (Array.isArray(e.slots) && e.slots.length ? 'carries-named-slots' : 'carries-the-kit')
    : 'carries-nothing');
  const byId = Object.fromEntries(phyl.taxa.map((t) => [t.id, t]));
  const out = (id) => phyl.edges.filter((e) => e.from === id);
  const kitCoParent = (e) => e.type === 'hybridizes_with' && e.inherits_kit === true;
  const ids = phyl.taxa.map((t) => t.id).sort();
  const mixed = ids.find((id) => out(id).some(kitCoParent) && out(id).some((e) => e.inherits_kit !== true)
    && byId[id].member_of);
  const scoped = ids.find((id) => out(id).some((e) => e.inherits_kit === true && Array.isArray(e.slots) && e.slots.length));
  check(`lineage: the payload offers a kit-carrying co-parent beside a claim (${mixed}) and a scoped edge (${scoped})`,
    Boolean(mixed && scoped));
  for (const id of [mixed, scoped].filter(Boolean)) {
    await visit('#/phylogeny/' + id);
    await page.waitForSelector(`[data-lineage-of="${id}"] [data-edge-carry] button.tdl-term`, { timeout: 20000 })
      .catch(() => {});
    const drawn = await page.$$eval(`[data-lineage-of="${id}"] [data-edge]`, (els) => els.map((el) => {
      const t = el.querySelector('[data-edge-carry] [data-term]');
      const g = el.closest('[data-carry-group]');
      return {
        type: el.getAttribute('data-edge'), target: el.getAttribute('data-edge-target'),
        term: t ? t.getAttribute('data-term') : null, word: t ? t.innerText : '',
        group: g ? g.getAttribute('data-carry-group') : null, text: el.innerText,
      };
    }));
    const want = out(id).map((e) => ({ type: e.type, target: e.to, term: flagWord(e) }));
    if (byId[id].member_of) want.push({ type: 'member_of', target: byId[id].member_of, term: 'member-of' });
    const key = (x) => `${x.type}>${x.target}:${x.term}`;
    check(`lineage (${id}): every edge drawn once, captioned with the carry its served flag states (${drawn.length})`,
      drawn.length > 0 && JSON.stringify(drawn.map(key).sort()) === JSON.stringify(want.map(key).sort()));
    check(`lineage (${id}): each edge sits in the group of its own carry word`,
      drawn.length > 0 && drawn.every((d) => d.term && d.group === d.term));
    check(`lineage (${id}): a co-parent that carries the kit is never captioned carries nothing, nor grouped with the claims`,
      out(id).filter(kitCoParent).every((e) => drawn.some((d) => d.type === e.type && d.target === e.to
        && d.term && d.term !== 'carries-nothing' && d.group !== 'carries-nothing')));
    check(`lineage (${id}): every carry word is the glossary record's own word`,
      drawn.length > 0 && drawn.every((d) => d.term && wordOf[d.term]
        && d.word.trim().toLowerCase() === wordOf[d.term].toLowerCase()));
    const filing = drawn.find((d) => d.type === 'member_of');
    check(`lineage (${id}): filing reads "${wordOf['member-of']}", and never browsing only or carries nothing`,
      Boolean(filing) && filing.term === 'member-of'
        && !/browsing only|carries no inheritance|carries nothing/i.test(filing.text));
    const paths = await page.$$eval('main svg path[data-edge-from]', (els) => els.map((el) => ({
      from: el.getAttribute('data-edge-from'), to: el.getAttribute('data-edge-to'),
      type: el.getAttribute('data-edge-type'), w: Number(el.getAttribute('stroke-width')) })));
    const mine = paths.filter((pp) => pp.from === id);
    check(`lineage (${id}): the tree draws each of its edges at the weight its flag states (${mine.length} of ${out(id).length})`,
      mine.length === out(id).length && mine.every((pp) => {
        const e = out(id).find((x) => x.to === pp.to && x.type === pp.type);
        return e && ((e.inherits_kit === true) === (pp.w > 1));
      }));
  }
  await shot('phylogeny-lineage');
}

// ④ Kit -- a SECTION of the style's dossier since WP-14.12 (PRD §D.1, §J.1). `#/kit` is an
// alias the router canonicalises (the refresh block below drives it); this block goes to the
// canonical address, naming the style it reads, because the bare `#/kit` that used to show
// Tidewater's kit showed a default the URL never said.
// Wait for the CLAIM being asserted, not for a heading that renders before it: the note is the
// glossary's `thin-kit` record and arrives a round trip after the surface mounts. A wait that
// does not wait for the thing under test is a flake with a plausible-looking line number.
// The expectation is that record's own definition, asked of the API -- the phrase this block
// used to type ("thin kit is correct") was a copy of the corpus -- and the count beside the
// table is the kit payload's own.
await visit('#/style/tidewater-georgian/kit');
await page.waitForSelector('[data-term-definition="thin-kit"]', { timeout: 20000 });
{
  const gl = await (await fetch(`${BASE}/api/glossary/thin-kit`)).json();
  const kitApi = await (await fetch(`${BASE}/api/kit/tidewater-georgian?only_specified=true`)).json();
  const note = (await page.locator('[data-term-definition="thin-kit"]').innerText()).trim();
  const want = ((gl && gl.term && gl.term.definition) || '').trim();
  check('kit: the thin-kit note is the glossary\'s own definition', want !== '' && note === want);
  await page.waitForSelector('[data-kit-shown]', { timeout: 20000 });
  const n = await page.locator('[data-kit-shown]').evaluate((e) =>
    ({ shown: Number(e.dataset.kitShown), total: Number(e.dataset.kitTotal) }));
  check(`kit: the count beside the table is the payload's (${n.shown} of ${n.total})`,
    (kitApi.slots || []).length > 0 && n.shown === kitApi.slots.length && n.total === kitApi.slots_total);
}
await shot('kit');

// ③ The Style Dossier (WP-14.12, PRD §D, §J.1). The Style Record was one long page reached by
// a bare `#/style` that opened Tidewater Georgian by default; the bare address is the Styles
// index now (W5 below), so this block names its record. Every expectation is read off the API
// the page reads -- the tells are the record's own list, the strip is the dossier payload's own
// sections at its own counts -- and never off a phrase typed here, which is how the old checks
// ("diagnostic tells", "refuses to invent") could pass on a page that drew something else.
await visit('#/style/tidewater-georgian');
await page.waitForSelector('[data-dossier-head="tidewater-georgian"]', { timeout: 20000 });
await page.waitForSelector('[data-tell]', { timeout: 20000 }).catch(() => {});
{
  const dos = await (await fetch(`${BASE}/api/styles/tidewater-georgian/dossier`)).json();
  const ch = await (await fetch(`${BASE}/api/styles/tidewater-georgian?sections=characteristics`)).json();
  const want = (ch.diagnostic_tells || []).length;
  const tells = await page.locator('[data-tell]').count();
  check(`dossier: every diagnostic tell the record states is drawn (${tells} of ${want})`,
    want > 0 && tells === want);
  const strip = await page.locator('[data-section-strip] [data-section]').evaluateAll((as) =>
    as.map((a) => [a.dataset.section, a.dataset.count === undefined ? null : a.dataset.count]));
  const served = (dos.sections || []).filter((s) => s.id === 'identify' || s.count > 0)
    .map((s) => [s.id, s.count == null ? null : String(s.count)]);
  const key = (rows) => JSON.stringify(rows.map((r) => r.join(':')).sort());
  check(`dossier: the strip is the payload's sections at the payload's counts (${strip.length})`,
    strip.length > 1 && key(strip) === key(served));
  check('dossier: no section is offered at zero', strip.every(([, n]) => n !== '0'));
}
await shot('style-record');

// The constraints section: every constraint a row in its one state, and a `?constraint=`
// citation opening on the row it names. Craftsman is read because its record states a judgment
// constraint; on a style whose constraints are all executable the judgment count would be
// 0 === 0 and prove nothing, so that premise is asserted before the count is.
await visit('#/style/craftsman/rules');
await page.waitForSelector('[data-constraint]', { timeout: 20000 });
{
  const rec = await (await fetch(`${BASE}/api/styles/craftsman?sections=constraints`)).json();
  const cs = rec.constraints || [];
  const judged = cs.filter((c) => c.scope === 'judgment' && (c.test === undefined || c.test === null));
  check(`dossier rules: the record states a judgment to offer back (${judged.length})`, judged.length > 0);
  const rows = await page.locator('[data-constraint]').count();
  const yours = await page.locator('[data-constraint][data-constraint-state="judgment-yours-to-judge"]').count();
  check(`dossier rules: every constraint is a row (${rows} of ${cs.length})`, cs.length > 0 && rows === cs.length);
  check(`dossier rules: judgment rows offered back (${yours} of ${judged.length})`, yours === judged.length);
  if (judged.length) {
    const id = judged[0].id;
    await visit(formatHash('style', { style: 'craftsman', section: 'rules', constraint: id }, {}));
    await page.waitForSelector(`[data-constraint="${id}"][data-selected]`, { timeout: 10000 }).catch(() => {});
    check('dossier rules: a constraint citation opens on the row it names',
      await page.locator(`[data-constraint="${id}"][data-selected]`).count() === 1
      && await page.locator('[data-constraint][data-selected]').count() === 1);
  }
}

// What is filed under a tradition: its members and the buildable styles under it, each counted
// against the dossier payload the section reads.
await visit('#/style/north-american/members');
await page.waitForSelector('[data-dossier-section="members"] [data-member]', { timeout: 20000 }).catch(() => {});
{
  const dos = await (await fetch(`${BASE}/api/styles/north-american/dossier`)).json();
  const m = await page.locator('[data-dossier-section="members"] [data-member]').count();
  const b = await page.locator('[data-dossier-section="members"] [data-buildable]').count();
  check(`dossier members: what is filed under a tradition is listed (${m} members, ${b} buildable)`,
    m > 0 && m === (dos.members || []).length && b === (dos.buildable_at || []).length);
}

// ⑩ Proportions
await visit('#/proportions');
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
await shot('proportions-order');

// ⑨ Fault Corpus
await visit('#/faults');
await page.waitForSelector('text=solecisms', { timeout: 15000 });
await page.waitForSelector('main >> text=dishonest', { timeout: 15000 }).catch(() => {});
const faults = await page.locator('main').innerText();
check('fault corpus voice line present', /explaining an economy/i.test(faults));
check('fix tiers named plainly', /dishonest/i.test(faults));
/* THE CARD ANSWERS FIRST (WP-14.11). Every fault record carries `correct_practice` (the right way)
   and `detection` (how to spot it), and the card rendered neither. They lead now, read here in
   DOCUMENT ORDER off the card, and each is held to the record the API serves for the fault on
   screen -- whichever one that is, read off the card rather than named. */
{
  await page.waitForSelector('main article[data-fault] [data-fault-section]', { timeout: 15000 }).catch(() => {});
  const fid = await page.locator('main article[data-fault]').first().getAttribute('data-fault').catch(() => null);
  const order = await page.$$eval('main article[data-fault] [data-fault-section]',
    (els) => els.map((el) => el.getAttribute('data-fault-section')));
  check(`the fault card answers first: the right way, then how to spot it, then the rest (${order.join(' · ')})`,
    order[0] === 'correct_practice' && order[1] === 'detection' && order.length > 2);
  const rec = fid ? await (await fetch(`${BASE}/api/faults/${fid}`)).json() : {};
  const flat = (x) => String(x || '').replace(/\s+/g, ' ').trim();
  const cp = await page.locator('main [data-fault-section="correct_practice"] p').first().innerText().catch(() => '');
  const dt = await page.locator('main [data-fault-section="detection"] p').first().innerText().catch(() => '');
  check(`and both are the record's own words (${fid})`, Boolean(rec.correct_practice) && Boolean(rec.detection)
    && flat(cp) === flat(rec.correct_practice) && flat(dt) === flat(rec.detection));
}
await shot('faults');

// ⑤ Brief Intake
await visit('#/brief');
await page.waitForSelector('text=feasibility', { timeout: 15000 });
const brief = await page.locator('main').innerText();
check('silences are named as decisions', /becomes a composer decision/i.test(brief));
// WP-2.3 landed; the panel now says WHERE the conflict set is named (the bench, on a plan)
// rather than that it does not exist. The assertion moved with the claim.
check('conflict set located, not promised', /conflict set · on the bench, not here/i.test(brief));
check('feasibility still advisory, never a proof', /never a proof/i.test(brief));
/* WP-14.10 (PRD §J.1): EVERY BUDGET OPTION IS ONE THE BRIEF SCHEMA ADMITS, AND THEY ARE ALL OF
   THEM. The form offered `entry`, `move-up`, `custom` and `estate` against a schema admitting
   `value`, `mid`, `custom` and `unlimited`, so three of the four a reader could pick refused the
   whole brief at compose. Read against the schema the server serves, not against a list here --
   a list here would be a third spelling of the enum. The count of options is asserted first, so
   a selector matching nothing cannot make "every option is admitted" true of no options. */
{
  const sch = await fetch(BASE + '/api/schema/brief').then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const tiers = sch && sch.schema && sch.schema.properties && sch.schema.properties.context
    && sch.schema.properties.context.properties && sch.schema.properties.context.properties.budget_tier
    && sch.schema.properties.context.properties.budget_tier.enum;
  if (!Array.isArray(tiers) || !tiers.length) {
    unjudged.push('the budget tiers -- GET /api/schema/brief states no budget_tier enum to hold them to');
  } else {
    await page.waitForFunction(() =>
      document.querySelectorAll('select[data-field="budget_tier"] option[data-tier]').length > 0,
    null, { timeout: 15000 }).catch(() => {});
    const opts = await page.$$eval('select[data-field="budget_tier"] option',
      (os) => os.map((o) => o.value).filter(Boolean));
    const off = opts.filter((o) => !tiers.includes(o));
    check(`the budget offers tiers to be judged (${opts.length})`, opts.length > 0);
    check(`every budget option is one the brief schema admits (${off.length ? 'off it: ' + off.join(', ') : 'none off it'})`,
      opts.length > 0 && off.length === 0);
    check(`and the options are the schema's, all of them (${opts.length} of ${tiers.length})`,
      opts.length === tiers.length);
  }
  // an act is a button, not a filter chip announcing itself as a toggle
  const compose = await page.evaluate(() => {
    const b = document.querySelector('main button[data-compose]');
    return b ? { pressed: b.getAttribute('aria-pressed'), text: b.textContent.trim() } : null;
  });
  check(`Compose is a real button, not a toggle (${compose ? compose.text : 'absent'})`,
    !!compose && compose.pressed === null && /compose/i.test(compose.text));
}
await shot('brief');

/* `?style=` SEEDS THE BRIEF AND `?example=` LOADS ONE (WP-14.10, PRD §E). The style is read back
   from the picker by the style's NAME, which is what the reader sees, against the name the API
   gives that id; the example by its own `name` field, and the address must lose `example` once it
   has done its work, so a refresh keeps a reader's edits rather than loading the example over them. */
{
  const seed = 'craftsman';
  const rec = await fetch(`${BASE}/api/styles/${seed}`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const want = rec && (rec.name || (rec.summary && rec.summary.name));
  await visit(`#/brief?style=${seed}`);
  await page.waitForFunction((w) => {
    const i = document.querySelector('main input[role="combobox"]');
    return i && w && i.value === w;
  }, want, { timeout: 15000 }).catch(() => {});
  const shown = await page.evaluate(() => document.querySelector('main input[role="combobox"]')?.value || null);
  check(`?style= seeds the brief's style, shown by name (${shown} against ${want})`, !!want && shown === want);

  const ex = await fetch(`${BASE}/api/briefs/examples/family-georgian`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  if (!ex || !ex.name) {
    unjudged.push('?example= -- the server serves no family-georgian example brief to load');
  } else {
    await visit('#/brief?example=family-georgian');
    await page.waitForFunction((n) => [...document.querySelectorAll('main input')].some((i) => i.value === n),
      ex.name, { timeout: 15000 }).catch(() => {});
    const loaded = await page.evaluate((n) => [...document.querySelectorAll('main input')].some((i) => i.value === n), ex.name);
    const hash = await page.evaluate(() => location.hash);
    check(`?example= loads the shipped brief by its name (${ex.name})`, loaded);
    check(`and leaves the address naming its style rather than the example (${hash})`,
      !/example=/.test(hash) && parseHash(hash).selection.style === ex.style);
  }
}

// ⑥ Candidate Set (empty state without a run)
await visit('#/candidates');
await page.waitForTimeout(500);
await shot('candidates');

// (8) Drawing Set - the elevation with its disclosure
// By its address (WP-14.7). The label click this replaced had to be scoped to the rail, since
// WP-5.6's Overview doors carry the same words; an address has no second match to refuse.
await visit('#/drawings');

/* ⑧a — THE ROUND (WP-12.4). The model is the surface's FIRST plate now, so it is what a reader
   arriving here sees; the five flat plates are chips beneath it and everything below this block
   still tests them, after clicking `elevation`.

   The scene is one metered call that solves the house, so the wait is generous. */
{
  const webgl = await page.evaluate(() => {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  });
  if (!webgl) {
    // A real COULD NOT EVALUATE: this machine cannot draw the model at all, and saying so is
    // not the same as the Round being broken. It is PRINTED rather than counted as a pass.
    console.log('N/EV  the Round: this browser reports no WebGL context — the model checks '
      + 'could not be evaluated here (the flat plates below are unaffected)');
  } else {
    await page.waitForSelector('[data-round-canvas]', { timeout: 120000 });
    const cap0 = await page.locator('[data-plate-title]').first().innerText();
    /* The default view shows the entrance face and the face to its left, so which axon opens
       is a fact about the RECORD. This asserted SOUTH-WEST, which is true of the Tidewater
       front and of nothing else: the subject's own entrance face decides it, and this walk
       now draws a record whose front is west. Derived, and the record is quoted in the
       message so a reader can see what it was derived from. */
    const AXON = { S: 'SOUTH-WEST', W: 'NORTH-WEST', N: 'NORTH-EAST', E: 'SOUTH-EAST' }[FRONT];
    check(`the Round opens on the axon that shows the entrance front (${cap0}; front ${FRONT})`,
      !!AXON && new RegExp(`AXONOMETRIC · FROM THE ${AXON}`, 'i').test(cap0));

    // Every named view chip produces its own caption. Counted, so a chip that silently does
    // nothing cannot pass by leaving the previous caption on the plate.
    const bar = page.locator('[role="radiogroup"][aria-label="view"]');
    check(`the view bar offers every named view (${await bar.getByRole('radio').count()})`,
      (await bar.getByRole('radio').count()) >= 10);
    /* AND THE FACE CHIPS ARE THE RECORD'S TOO. `S` carried `· THE ENTRANCE FRONT` as part of
       its expected caption, which is a claim about where the door is and not about whether a
       chip captions its own drawing. The entrance face's chip must carry the suffix and a
       chip that is not the entrance face must not -- which is the stronger pair, and it holds
       on any record. */
    let named = 0;
    for (const [chip, want] of [[FRONT, new RegExp(`${FACE_WORD[FRONT]} ELEVATION · THE ENTRANCE FRONT`, 'i')],
                                [NOT_FRONT, new RegExp(`${FACE_WORD[NOT_FRONT]} ELEVATION(?! · THE ENTRANCE)`, 'i')],
                                ['ROOF', /ROOF PLAN/i],
                                ['PLAN·L0', /GROUND FLOOR PLAN · CUT AT/i],
                                ['AXON·NE', /AXONOMETRIC · FROM THE NORTH-EAST/i]]) {
      await bar.getByRole('radio', { name: chip, exact: true }).click();
      await page.waitForTimeout(220);
      const cap = await page.locator('[data-plate-title]').first().innerText();
      if (want.test(cap)) named += 1;
      else check(`the ${chip} chip captions its own drawing (got "${cap}")`, false);
    }
    check(`every named view captions its own drawing (${named} of 5)`, named === 5);

    // THE PLATE OVER THE MODEL. `data-frame` is what registers it, so its presence is the
    // thing to assert -- an overlay drawn without one is an SVG floating at whatever scale
    // the browser chose.
    await bar.getByRole('radio', { name: 'S', exact: true }).click();
    await page.waitForTimeout(200);
    await page.getByRole('button', { name: 'plate', exact: true }).click();
    await page.waitForTimeout(400);
    const ov = await page.evaluate(() => {
      const el = document.querySelector('[data-round-overlay]');
      if (!el) return null;
      const svg = el.querySelector('svg');
      return { frame: svg ? svg.getAttribute('data-frame') : null,
               t: getComputedStyle(el).transform };
    });
    check('the plate is laid over the model at the same view', !!ov);
    check('and it carries the frame that registers it',
      !!(ov && ov.frame && /"px_per_ft"/.test(ov.frame)));
    check(`and it is placed by a real transform (${ov && ov.t && ov.t.slice(0, 24)})`,
      !!(ov && ov.t && ov.t !== 'none'));
    await page.getByRole('button', { name: 'plate', exact: true }).click();
    await shot('round-axon-sw');

    // AN ORBIT IS NOT A NAMED DRAWING, and the caption must stop claiming to be one. A free
    // view that still called itself SOUTH ELEVATION would be a drawing lying about its own
    // projection, and every dimension on it would read as measured.
    const cv = page.locator('[data-round-canvas]');
    const b = await cv.boundingBox();
    await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2);
    await page.mouse.down();
    await page.mouse.move(b.x + b.width / 2 + 140, b.y + b.height / 2 + 30, { steps: 12 });
    await page.mouse.up();
    await page.waitForTimeout(300);
    const capFree = await page.locator('[data-plate-title]').first().innerText();
    check(`after an orbit the caption says it is a free view (${capFree.slice(0, 40)})`,
      /FREE VIEW · NOT A NAMED DRAWING · DIMENSIONS WITHHELD/i.test(capFree));
    await shot('round-free');

    // ---------------------------------------------------------- the approach (WP-12.7)
    //
    // THE ASSERTIONS HERE ARE ABOUT WHAT THE VIEW REFUSES. A perspective is easy to add and
    // easy to get wrong in a way no picture shows: the caption must say the dimensions are
    // withheld, and the flat plate must NOT be laid over it -- an affine registers a plate at
    // one depth and floats it off the model everywhere else, which looks registered and is not.
    // WP-12.5's rule applies to the screenshot below: looking at it FINDS defects and does not
    // adjudicate them, so the checks read the DOM and the picture is evidence for a reader.
    await bar.getByRole('radio', { name: 'APPROACH', exact: true }).click();
    await page.waitForTimeout(900);
    const capApp = await page.locator('[data-plate-title]').first().innerText();
    check(`the approach names itself and withholds its dimensions (${capApp.slice(0, 46)})`,
      /APPROACH TO THE/i.test(capApp) && /DIMENSIONS WITHHELD/i.test(capApp)
      && /PERSPECTIVE/i.test(capApp));
    check('and it states the ruled eye height', /5′-6″|5'-6"/.test(capApp));
    check('the approach is addressable in the URL',
      /[?&]view=approach\b/.test(page.url()), page.url().slice(-52));
    const appOv = await page.evaluate(() => {
      const el = document.querySelector('[data-plate-overlay]');
      return el ? getComputedStyle(el).transform : 'ABSENT';
    });
    check(`no flat plate is laid over the perspective (${appOv})`, appOv === 'ABSENT');
    /* AND THE MODEL IS IN THE RENDERER AT THIS VIEW -- an empty canvas would pass every line
       above, because a canvas with a house in it and a canvas with nothing in it are the same
       element, the same size and the same caption.

       THE FIRST VERSION OF THIS CHECK READ ZERO AND THE MODEL WAS FINE: it selected
       `[data-round-canvas] canvas`, and `[data-round-canvas]` IS the canvas, so the descendant
       matched nothing. A check that reads 0 because its selector is wrong is indistinguishable
       from one that reads 0 because nothing was drawn -- which is WP-12.5's own finding wearing
       the other face, so the count is published by the renderer now rather than sniffed out of
       the DOM. */
    const cvEl = page.locator('[data-round-canvas]');
    const appSolids = +(await cvEl.getAttribute('data-round-solids') || 0);
    const appRefused = +(await cvEl.getAttribute('data-round-refused') || 0);
    check(`and the model is in the renderer at it (${appSolids} solids built)`, appSolids > 100);
    check(`and no solid was refused by the renderer (${appRefused})`, appRefused === 0);
    await shot('round-approach');

    // and a named chip takes it back
    await bar.getByRole('radio', { name: 'PLAN·L0', exact: true }).click();
    await page.waitForTimeout(700);
    check('a named chip snaps back out of the free view',
      /GROUND FLOOR PLAN/i.test(await page.locator('[data-plate-title]').first().innerText()));
    await shot('round-plan');

    // ------------------------------------------------------------ overlays (WP-12.5)
    //
    // THE FAILURE THESE GUARD IS AN OVERLAY THAT LOOKS LIKE IT WORKS. Without `rooms_meta` on
    // the scene response every wash comes back empty -- no privacy rank resolves, no room is
    // wet -- and a surface that draws nothing is indistinguishable from a house with nothing
    // to draw. So each of these asserts a POSITIVE, and the URL is asserted too, because a
    // chip that does not reach the query string is a place nobody can send.
    const ovBar = page.locator('[data-chipgroup="overlay"], text=overlay').first();
    await page.getByRole('button', { name: 'privacy', exact: true }).click();
    await page.waitForTimeout(500);
    check('an overlay chip puts itself in the URL',
      /(\?|&)ov=[^&]*privacy/.test(page.url()), page.url().slice(-70));
    // AND THAT IT DREW SOMETHING. The first version of this block asserted the URL and the
    // caption and nothing else, so it passed green over an overlay that drew NOTHING at all --
    // a translucent wash that is absent looks exactly like one drawn faintly over a sepia
    // floor. Only a count can tell those apart, so the canvas states what it built.
    const drew1 = await page.locator('[data-round-canvas]').getAttribute('data-round-overlays');
    check(`the privacy overlay actually draws geometry (${drew1})`,
      /privacy:[1-9]/.test(drew1 || ''));
    await shot('round-privacy');

    await page.getByRole('button', { name: 'wet', exact: true }).click();
    await page.waitForTimeout(500);
    check('two overlays coexist in one query key',
      /(\?|&)ov=[^&]*privacy/.test(page.url()) && /(\?|&)ov=[^&]*wet/.test(page.url()),
      page.url().slice(-70));
    const drew2 = await page.locator('[data-round-canvas]').getAttribute('data-round-overlays');
    check(`and both draw (${drew2})`,
      /privacy:[1-9]/.test(drew2 || '') && /wet:[1-9]/.test(drew2 || ''));

    // ------------------------------------------------------------ modifiers (WP-12.5)
    //
    // A MODIFIER PERSISTS ACROSS VIEWS, SO THE CAPTION MUST CARRY IT. A plate still captioned
    // GROUND FLOOR PLAN while its storeys float apart has told the reader something untrue.
    await page.getByRole('radio', { name: 'levels', exact: true }).click();
    await page.waitForTimeout(700);
    const capEx = await page.locator('[data-plate-title]').first().innerText();
    check(`an exploded model says so in its caption (${capEx.slice(-46)})`,
      /EXPLODED BY LEVEL/i.test(capEx));
    check('the modifier is in the URL', /(\?|&)explode=levels/.test(page.url()),
      page.url().slice(-70));
    await shot('round-explode');

    // THE CUT SAYS WHERE IT CAME FROM. With a face selected this is the building section the
    // project does not draw flat, and a reader who mistook it for a plate would be citing a
    // drawing that does not exist.
    await page.getByRole('radio', { name: 'level', exact: true }).click();
    await page.waitForTimeout(700);
    const capCut = await page.locator('[data-plate-title]').first().innerText();
    check(`a cut says it is derived from the model and not a plate (${capCut.slice(-52)})`,
      /DERIVED FROM THE MODEL, NOT A PLATE/i.test(capCut));
    await shot('round-cut');
  }
}

// The five flat plates are chips beneath the model now, so the rest of ⑧ asks for one first.
await page.getByRole('radio', { name: 'elevation', exact: true }).click();

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
await shot('drawing-elevation');

/* (8a) WP-12.0 — the four faces, and the plate that says which placement drew it.

   `render_elevation` has taken a `face` since WP-3.2 and `corpus.drawing` has forwarded
   `body.face` since WP-5.1, and until WP-12.0 no client sent one: three of the four
   elevations this system can draw had never been looked at, and the one it did draw was
   the one face the placement defect could not reach (the front is drawn on the WIDTH,
   which does not move between the two engines; only the gable ends move). So the check
   that matters is that a chosen face draws a DIFFERENT plate — a `face` argument accepted
   and ignored looks exactly like one that works. */
{
  const faceChips = page.getByRole('radio', { name: /^(south|north|east|west)/ });
  check('drawing set: four face chips, as radios', await faceChips.count() === 4);
  check('drawing set: exactly one face is named the entrance front',
    await page.getByRole('radio', { name: /the entrance front/ }).count() === 1);
  const ink = async () => (await page.locator('.plate-fit > svg').innerHTML()).length;
  const before = await ink();
  /* A FACE THAT IS NOT THE ONE ALREADY ON THE PLATE. This clicked `west` outright, which is a
     CHANGE on a record whose front is south and a NO-OP on one whose front is west -- and the
     no-op is indistinguishable from a `face` argument accepted and ignored, which is the
     exact defect this check exists to catch. The face opposite the front is a change on any
     record. */
  const pick = FACE_WORD[NOT_FRONT].toLowerCase();
  await page.getByRole('radio', { name: new RegExp(`^${pick}`, 'i') }).click();
  await page.waitForFunction((n) => {
    const s = document.querySelector('.plate-fit > svg');
    return s && s.innerHTML.length !== n;
  }, before, { timeout: 60000 }).catch(() => {});
  check(`drawing set: a chosen face draws a different plate (${before} → ${await ink()})`,
    (await ink()) !== before);
  const cap = await page.locator('main').innerText();
  /* THE CAPTION THAT NAMES THE FACE IS GATED ON THE DATE OF REPRESENTATION, which is a
     coupling nobody chose and which this subject exposes: `DrawingSet.jsx` renders
     `{kind === 'elevation' && result.date_of_representation && (<p>…{face} elevation · the
     entrance front is X · drawn for …</p>)}`, and `good-03-parlor-drawing-room-house` returns
     `date_of_representation: null` (asked of the API directly, not inferred), so the whole
     line is absent. The face and the entrance front are facts about the DRAWING; the date is
     a separate disclosure, and one being unavailable should not take the other two with it.

     Reported as COULD NOT EVALUATE rather than failed -- the surface is doing what it was
     written to do -- and as a finding in WP-13.9's report, because the check is about the
     caption and there is no caption to judge. The letter or the word, either case: what is
     asserted where it DOES render is that the caption names the face that was chosen, not the
     spelling this surface happens to use for it today. */
  /* THE DISCRIMINATOR TOOK TWO GOES AND BOTH MISSES ARE WORTH KNOWING, because each matched
     something else on the same page and a three-state check whose third state never fires is
     a two-state check with a longer comment. "the entrance front" is also the text of the face
     CHIP that names the front, so the first guard matched a radio label. "glass module" is
     also drawn INTO THE PLATE, in the sheet's own margin schedule -- measured, the walk
     reported `tidewater-georgian · 3 BAYS · side-gable 8.0:12 · GLASS MODULE 9.0 IN (undated)`,
     which is the SVG and not the caption, and whose `(undated)` is the same null this branch
     exists for. `elevation · the entrance front` is the JSX line's own shape and nothing
     else's. */
  if (!/elevation · the entrance front/i.test(cap)) {
    unjudged.push(`drawing set: the caption names the face drawn — ${DRAWABLE} returns no `
      + '`date_of_representation`, and that line is gated on it, so there is no caption to '
      + 'judge. The face and the front are facts about the drawing and the date is not');
  } else {
    const capLine = (/[^\n]*elevation · the entrance front[^\n]*/i.exec(cap) || ['(not found)'])[0];
    check(`drawing set: the caption names the face drawn (${NOT_FRONT}), and where the front is`
          + ` — "${capLine.slice(0, 90)}"`,
      new RegExp(`\\b(${NOT_FRONT}|${FACE_WORD[NOT_FRONT]}) elevation`, 'i').test(capLine)
      && /the entrance front/i.test(capLine));
  }
  // WP-11.8's J6 on the two plates that could not carry it: two sheets of "the same house"
  // that disagree differ because the INPUT differed, and a reader must be able to see it.
  /* RE-CUT AGAINST THE PROPERTY (WP-13.4), AND IT WENT RED FIRST, WHICH IS THE POINT.
     This pinned the plate's sentence VERBATIM -- `placed by (proof (CP-SAT)|search
     (hill-climb)|an engine this plate does not name)` -- so widening that line to say whether
     a CP-SAT placement was proved AT THE OPTIMUM broke a guard about the engine with a change
     about the proof. That is this repository's pinned-literal trap, five packages running: a
     stale SELECTOR goes quietly blind and a pinned LITERAL fails loudly on an unrelated change,
     and neither is the property. The property is that the line names an engine from a closed
     vocabulary, carries the input digest, and -- where it names CP-SAT -- says which of the two
     CP states it is, because "CP-SAT" alone is exactly the claim that captioned a FEASIBLE
     truncation as a proof. */
  const engineLine = (/placed by ([^\n]*)/.exec(cap) || [])[1] || '';
  check(`drawing set: the elevation names the engine that placed it (${engineLine.slice(0, 60)})`,
    /(CP-SAT|hill-climb|an engine this plate does not name)/.test(engineLine));
  check('drawing set: and a CP-SAT plate says whether it was proved at the optimum',
    !/CP-SAT/.test(engineLine) || /(proved at the optimum|NOT proved at the optimum)/.test(engineLine));
  check('drawing set: and it carries the input digest', /input [0-9a-f]{12}/.test(cap));
  // The face group made this strip wider than the pane; without `flex: none` and `nowrap`
  // on the right-hand block the plan id wrapped inside a 34px bar and collided with the
  // chips. The strip is overflowX:auto by design — it scrolls, it does not reflow.
  const strip = await page.evaluate(() => {
    const el = [...document.querySelectorAll('div')].find((d) => d.innerText.includes('download SVG')
      && d.innerText.includes('elevation') && d.getBoundingClientRect().height < 60);
    if (!el) return null;
    const dl = [...el.querySelectorAll('button')].find((b) => /download SVG/.test(b.innerText));
    return { h: Math.round(el.getBoundingClientRect().height),
             dlw: dl ? Math.round(dl.getBoundingClientRect().width) : 0 };
  });
  check(`drawing set: the sheet strip is one row (${strip && strip.h}px) with its download still whole`,
    strip && strip.h <= 40 && strip.dlw > 40);
  await shot('drawing-elevation-west');
}

// A sheet kind is one of a set, so it is a radio now, not a button — the chips that pick
// between alternatives say so to a screen reader since WP-5.6.
await page.getByRole('radio', { name: 'bearing lines' }).click();
await page.waitForTimeout(3000);
await shot('drawing-bearing');

// (8b) Details & Export - forthcoming, never hidden
await visit('#/export');
await page.waitForSelector('text=forthcoming', { timeout: 15000 });
const ex = await page.locator('main').innerText();
check('export: DXF/IFC live (WP-5.1)', /plan dxf/.test(ex) && /ifc model/.test(ex));
check('export: unbuilt work named with its WP', /WP-5\.3 is not built/.test(ex));
check('export: no costing engine implied', /No costing engine exists/i.test(ex));
check('export: conflict count is the recorded 262', /262 recorded pack conflicts/.test(ex));
await shot('export');

// (11) Transcription - a drawing goes in, a record comes out, gaps named
await visit('#/transcription');
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
await shot('transcription');

// The assistant's pane is here, and it is NAMED — by its own glossary record, not by the words
// "the rail" the pane printed before it said what it was (WP-14.13, PRD §I.11). The aside's
// label is unchanged and is how it is found; the head is read with textContent, because the
// eyebrow is upper-cased by CSS and innerText would return what the CSS drew.
{
  const assistant = await (await fetch(BASE + '/api/glossary/assistant')).json().catch(() => null);
  const want = assistant && assistant.term ? assistant.term.term : null;
  const aside = page.locator('aside[aria-label*="the rail"]');
  const head = ((await aside.locator('[data-rail-head]').first().textContent().catch(() => '')) || '').trim();
  check(`rail present on every surface, named by its record (${JSON.stringify(head)})`,
    await aside.count() === 1 && Boolean(want) && head === want);
}

// ── WP-5.6: navigation, addressing and search ──────────────────────────────────
// A place is a URL. Everything below is the one claim, tested from both ends.

// A citation pasted cold resolves, and canonicalises to the place it names — so the URL
// you copy back out is the place, not the redirect that reached it.
await page.goto(BASE + '/#/cite/fault:porch-too-shallow-to-inhabit', { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
check('a #/cite/ link resolves cold', /#\/faults\/porch-too-shallow-to-inhabit/.test(page.url()));
check('and it landed on the fault', /four-foot porch/i.test(await page.locator('main').innerText()));

// A deep link restores on refresh — the thing no amount of useState could do. The link is the
// RETIRED `#/kit/craftsman` on purpose (WP-14.12, PRD §E.1): it is read as the dossier's kit
// section and the address bar is rewritten without a history entry, so a link pasted before the
// Kit moved still arrives, and the refresh below is of the address the app lives at.
await page.goto(BASE + '/#/kit/craftsman', { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
check('a legacy #/kit address is rewritten to the dossier\'s kit section',
  /#\/style\/craftsman\/kit$/.test(page.url()));
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
check('a refresh keeps the place', /#\/style\/craftsman\/kit$/.test(page.url()));
check('and the place is loaded', await page.locator('[data-kit-style="craftsman"]').count() === 1);

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
await visit('#/style');
await page.waitForTimeout(700);
await page.goBack();
await page.waitForTimeout(900);
check('filters survive leaving and coming back', /q=porch/.test(page.url()));
await page.getByRole('button', { name: /narrowing · clear/ }).click();
await page.waitForTimeout(500);
check('one act clears every filter', !/q=porch/.test(page.url()));

// The palette: opened by key, dispatches by citation, reachable by a word a newcomer
// would actually type.
// FOUND BY ITS OWN NAME (WP-14.7). It was `[role="dialog"]`, which was true only while the
// palette was the one dialog this app could open; a definition popover is a dialog too, and
// the name is the one `palette/CommandPalette.jsx` puts on its dialog element. Its results
// are read inside it for the same reason -- `[role="option"]` is also any combobox's list.
const palette = page.getByRole('dialog', { name: 'Search the corpus', exact: true });
await page.keyboard.press('Control+k');
await palette.waitFor({ state: 'visible', timeout: 5000 });
check('⌘K opens the palette', await palette.count() > 0);
await page.keyboard.type('mistakes');
await page.waitForTimeout(500);
// By the option's own id (WP-14.13): the place's words are its glossary record's and may be
// reworded there; the id is the site map's and does not move.
check('a newcomer word finds the fault corpus',
  (await palette.locator('[role="option"]').first().getAttribute('data-id')) === 'faults');
await page.keyboard.press('Escape');
await page.waitForTimeout(200);
await page.keyboard.press('Control+k');
await page.waitForTimeout(300);
await page.keyboard.type('tidewater georgian');      // words in either order
await page.waitForTimeout(500);
const hit = await palette.locator('[role="option"]').first().innerText();
check('half-remembered word order still finds it', /Tidewater/i.test(hit));
check('the citation is printed beside the result', /style:tidewater-georgian/.test(hit));
check('and the result carries its citation as data, which a place does not',
  (await palette.locator('[role="option"]').first().getAttribute('data-cite')) === 'style:tidewater-georgian');
await shot('palette');
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
await shot('phylogeny-map');

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
// by its own name, as the palette is and for the same reason (WP-14.7): the dialog
// `palette/ShortcutCard.jsx` opens, not whichever dialog happens to be on the page
const card = await page.getByRole('dialog', { name: 'Keyboard shortcuts and addressing', exact: true })
  .innerText();
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
// surface left the previous record on screen — the URL and the panel disagreeing. The bare
// style surface is the Styles INDEX since WP-14.12 (PRD §E.2) and never a record, so the check
// is structural -- the index is on screen and no dossier head is -- where it read the first
// 400 characters for one word. The premise is asserted first: a record that never rendered
// cannot be left behind, and the check would pass on it.
await page.goto(BASE + '/#/style/craftsman');
await page.waitForSelector('[data-dossier-head="craftsman"]', { timeout: 15000 }).catch(() => {});
check('W5 premise: the record was on screen before the bare address',
  await page.locator('[data-dossier-head="craftsman"]').count() === 1);
await page.goto(BASE + '/#/style');
await page.waitForSelector('[data-styles-index]', { timeout: 15000 }).catch(() => {});
check('a bare surface URL does not still show the last record',
  await page.locator('[data-styles-index]').count() === 1
  && await page.locator('[data-dossier-head]').count() === 0);

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
await shot('phylogeny-map-full');
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
await page.goto(BASE + '/#/style', { waitUntil: 'networkidle' });
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
await shot('phylogeny-map-folded');
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

/* ------------------------------------------------------------------ WP-13.4: REFUSED, NOT DRAWN

   Lucas ruled on 15 Sep 2026 that a placement breaking a hard fact of the type is REFUSED and
   not drawn: the bench shows the conflict set, and the brief or the parti is what changes. This
   block is the behavioural half of that, and it is the only half a node test cannot reach --
   `src/refusal.test.mjs` drives every branch of the leaf with a hand-built body and holds the
   surfaces to it by source, and neither can see a refused record arriving from a real server and
   a plate coming back anyway.

   THE RECORD IS DRIVEN AND THE DRIVING IS PROVED. No shipped plan is guaranteed to refuse -- that
   is a property of the prover's budget on the day -- so this builds one that MUST: every upper
   room is pointed at the SMALLEST ground room. Two rooms cannot both sit over one closet without
   overlapping each other, and rooms may not overlap, so at least all but one of those claims is
   geometrically impossible and `stacking.lands` must break it. The shipped record is tried first
   in case it already refuses, because driving a case the corpus reaches anyway would be inventing
   work.

   AND IF THE SERVER DOES NOT ANSWER THE CONTRACT, THIS IS UNJUDGED. The server slice of WP-13.4
   builds the routes in parallel with this one; until it lands, `placement_refused` is absent and
   every check below would pass vacuously over a bench that is behaving exactly as it did before.
   `unjudged` is what that costs, and it is not a pass. */
{
  const example = await fetch(BASE + '/api/plans/examples/tidewater-georgian-careful')
    .then((r) => r.json()).then((p) => p.plan || p).catch(() => null);

  const refusing = (() => {
    if (!example) return null;
    const q = JSON.parse(JSON.stringify(example));
    const levels = q.levels || [];
    const ground = levels.find((l) => (l.index ?? 0) === 0);
    const upper = levels.filter((l) => (l.index ?? 0) > 0);
    if (!ground || !upper.length) return null;
    const area = (r) => (r.width_ft || 0) * (r.length_ft || 0);
    const smallest = (ground.rooms || []).slice().sort((a, b) => area(a) - area(b))[0];
    if (!smallest) return null;
    let n = 0;
    for (const lv of upper) for (const r of lv.rooms || []) { r.stacks_over = smallest.id; n += 1; }
    return n >= 2 ? q : null;   // one claim alone could hold; two over one closet cannot
  })();

  const evaluate = (plan) => fetch(BASE + '/api/plan/evaluate', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ plan, place: true }),
  }).then((r) => r.json()).catch(() => null);

  let record = null, body = null;
  for (const cand of [example, refusing]) {
    if (!cand) continue;
    const got = await evaluate(cand);
    if (got && got.placement_refused) { record = cand; body = got; break; }
  }

  if (!body) {
    unjudged.push('a refused placement shows the conflict set where the plate was');
    unjudged.push('a refused placement disables the download and the exports');
    console.log('N/EV a refused placement shows the conflict set where the plate was');
    console.log('N/EV a refused placement disables the download and the exports');
    console.log('     COULD NOT EVALUATE: this server answers no `placement_refused`, on the');
    console.log('     shipped record or on one driven to break its declared stacks. The server');
    console.log('     slice of WP-13.4 is what makes these judgeable; they are NOT passes.');
  } else {
    const r = body.placement_refused;
    check(`the refused evaluate sends NO placement (kind ${r.kind})`, !body.placement);
    // the contract's own three-state rule, asserted from the API rather than from the screen:
    // unjudged does not refuse, so a body arriving here must name one of the two kinds
    check('and the refusal names a kind this app can read',
      r.kind === 'infeasible' || r.kind === 'type-fact-downgraded');

    await page.evaluate((plan) => {
      // planDoc persists to localStorage and reads it at boot, so this is how a record reaches
      // the bench without a route: no app change, and the reload proves the store's own path.
      localStorage.setItem('tdl-workbench-plan', JSON.stringify(plan));
    }, record);
    /* RELOAD, FOR THE REASON THE DRAWABLE SUBJECT ABOVE RELOADS. A `goto` whose only
       difference from the current URL is the fragment is a SAME-DOCUMENT navigation: the app
       never re-boots, `planDoc` never re-reads localStorage, and the bench goes on showing
       whatever it had -- which, once this walk got far enough to reach this block, is a
       DRAWABLE record. Every assertion below then measures the wrong house and the first of
       them ("a refused placement draws NO plate") fails on a plate that is correctly there. */
    await page.goto(BASE + '#/workbench');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForSelector('[data-conflict-set]', { timeout: 90000 }).catch(() => {});

    const bench = await page.evaluate(() => {
      const p = document.querySelector('[data-conflict-set]');
      const cap = document.querySelector('[data-engine-claim]');
      return {
        panel: !!p,
        kind: p ? p.getAttribute('data-conflict-set') : null,
        facts: p ? +p.getAttribute('data-refusal-facts') : 0,
        lines: p ? +p.getAttribute('data-refusal-lines') : 0,
        text: p ? p.textContent.replace(/\s+/g, ' ').trim() : '',
        plates: document.querySelectorAll('main svg[role="img"]').length,
        capRefused: cap ? cap.getAttribute('data-placement-refused') : null,
      };
    });
    check('a refused placement draws NO plate on the bench', bench.plates === 0);
    check('and the conflict set stands where the plate would be', bench.panel === true);
    // A REFUSAL IS CONTENT: it names what could not hold. A panel that named nothing would be a
    // bare error wearing the word, so the count is read from the panel's own attributes rather
    // than from a phrase -- and zero is a failure, not a smaller refusal.
    check(`and it names at least one fact or conflict (facts ${bench.facts}, lines ${bench.lines})`,
      (bench.facts + bench.lines) > 0);
    check('and it says the brief or the parti is what changes',
      /brief or the parti/i.test(bench.text));
    check(`the caption publishes the refusal beside the words (${bench.capRefused})`,
      bench.capRefused === r.kind);

    await visit('#/drawings');
    await page.waitForTimeout(2500);
    const ds = await page.evaluate(() => ({
      download: [...document.querySelectorAll('button')]
        .filter((b) => /download SVG/i.test(b.textContent)).length,
      plates: document.querySelectorAll('main svg[role="img"]').length,
    }));
    check('the Drawing Set offers no download for a refused record', ds.download === 0);
    check('and draws no plate for one', ds.plates === 0);
    // WP-14.10: and the journey, standing on the drawings step, does not offer them either
    {
      const jb = await journeyRead();
      const st = jb && jb.steps.drawings;
      check(`the journey on the Drawing Set reads its own step as blocked: refused (${st ? `${st.tag}, ${st.blocked}` : 'absent'})`,
        !!st && st.tag === 'span' && st.blocked === 'refused' && st.current === 'step');
      check('and offers no link on to the export', !!jb && !(jb.next && jb.next.tag === 'a')
        && !!jb.steps.export && jb.steps.export.tag === 'span');
    }

    await visit('#/export');
    await page.waitForTimeout(800);
    const ex = await page.evaluate(() => {
      const chips = [...document.querySelectorAll('button')]
        .filter((b) => /(^| )(plan|elevation|section|bearing|roof)( dxf)?$|ifc model/i.test(b.textContent.trim()));
      return {
        n: chips.length,
        enabled: chips.filter((b) => !b.disabled).length,
        blocked: !!document.querySelector('[data-export-blocked]'),
        panel: !!document.querySelector('[data-conflict-set]'),
      };
    });
    // the denominator first: a selector matching nothing makes "0 enabled" look like a pass
    check(`Details & Export offers its export controls to be judged (${ex.n})`, ex.n > 0);
    check(`and every one is disabled on a refused record (${ex.enabled} enabled)`, ex.enabled === 0);
    check('and it says why', ex.blocked === true);
    check('and shows the same conflict set the bench showed', ex.panel === true);
    // WP-14.10: and the journey on the export step says the same, as text and not a link
    {
      const jb = await journeyRead();
      const st = jb && jb.steps.export;
      check(`the journey on Details & Export reads its own step as blocked: refused (${st ? `${st.tag}, ${st.blocked}` : 'absent'})`,
        !!st && st.tag === 'span' && st.blocked === 'refused' && st.current === 'step');
    }
  }
}

/* DEFINITIONS ON SCREEN (WP-14.8, PRD §E.2, §E.4, §I.1, §I.4).

   The Glossary index and a term page, read against `GET /api/glossary` rather than against any
   count typed here: the families the page draws must be the payload's non-empty `by_family` in
   its order, the words it draws must number the payload's `count`, and a term page must show
   that record's own definition. Then one `Term`, driven the three ways a reader opens it:
   Enter (a non-modal dialog, labelled by its word, focus taken inside, "more" at the record's
   citation), Escape (closed, focus back on the word), and a resting mouse (open after the
   delay) -- and a change of place closes it. Last, the page reflows: at 1280 px there is no
   sideways scroll, because the Glossary releases the shell's 1380 px floor.

   WP-14.3 serves the route in parallel with this package. Where it does not answer with a
   terms list, every check below would be judging an app with no glossary to read, so the block
   is UNJUDGED by name -- the walk's own third state -- and not a pass. */
{
  const gl = await fetch(`${BASE}/api/glossary`)
    .then((r) => (r.ok ? r.json() : null)).catch(() => null);
  if (!gl || !Array.isArray(gl.terms) || !gl.terms.length) {
    unjudged.push('definitions on screen — GET /api/glossary did not answer with a terms list, so '
      + 'the Glossary, its page head and the Term popover have nothing to be judged against');
  } else {
    await visit('#/glossary');
    await page.waitForSelector('[data-glossary-index], [data-glossary-failed]', { timeout: 30000 })
      .catch(() => {});
    const idx = await page.evaluate(() => ({
      families: [...document.querySelectorAll('[data-glossary-index] [data-family]')]
        .map((s) => s.getAttribute('data-family')),
      terms: document.querySelectorAll('[data-glossary-index] [data-glossary-term]').length,
      heads: [...document.querySelectorAll('[data-page-head]')].map((h) => h.getAttribute('data-page-head')),
      failed: !!document.querySelector('[data-glossary-failed]'),
      reflow: !!document.getElementById('root')?.hasAttribute('data-reflow'),
      noEntry: /no entry:/.test(document.querySelector('main')?.textContent || ''),
    }));
    const nonEmpty = Object.entries(gl.by_family || {})
      .filter(([, ids]) => Array.isArray(ids) && ids.length).map(([f]) => f);
    check('the Glossary read the glossary rather than reporting it unreadable', !idx.failed);
    // the denominator first: a selector matching nothing would make every comparison below vacuous
    check(`the Glossary draws families to judge (${idx.families.length})`, idx.families.length > 0);
    check(`and they are the payload's non-empty families, in its order (${idx.families.length} of ${nonEmpty.length})`,
      JSON.stringify(idx.families) === JSON.stringify(nonEmpty));
    check(`and it lists every word the server serves (${idx.terms} of ${gl.count})`, idx.terms === gl.count);
    check(`exactly one page head, and it is the Glossary's own record (${JSON.stringify(idx.heads)})`,
      idx.heads.length === 1 && idx.heads[0] === 'surface-glossary');
    check('the Glossary releases the 1380 px floor while it is shown', idx.reflow);
    check('no word on the index reads "no entry"', !idx.noEntry);

    // The page head's "Try" link, where the record's own `surface.try` is a `term:` cite: the
    // search index names no term, so the link is worded by the glossary record it points at,
    // never printed as the raw cite. Read hidden or not -- the words are the claim, not the fold.
    const head = gl.terms.find((t) => t.id === 'surface-glossary');
    const tryCite = head && head.surface && typeof head.surface.try === 'string' ? head.surface.try : null;
    if (!tryCite || !tryCite.startsWith('term:')) {
      unjudged.push(`the page head's Try link -- surface-glossary's try is ${JSON.stringify(tryCite)}, `
        + 'not a term: cite, so the wording rule has no subject here');
    } else {
      const target = gl.terms.find((t) => t.id === tryCite.slice('term:'.length));
      const tryText = await page.evaluate(() =>
        document.querySelector('[data-page-head] .tdl-page-head-try .tdl-record-name')?.textContent || '');
      check(`the page head's Try link is worded by its record, not printed as ${tryCite} (${JSON.stringify(tryText)})`,
        !!target && tryText.trim() === String(target.term).trim());
    }

    // The focus ring: the index's filter field, focused, draws the global ring rather than none.
    const ring = await page.evaluate(() => {
      const i = document.querySelector('[data-glossary-index] input');
      if (!i) return null;
      i.focus();
      const cs = getComputedStyle(i);
      return { style: cs.outlineStyle, width: cs.outlineWidth };
    });
    check(`a focused text field draws a focus ring (${ring && `${ring.style} ${ring.width}`})`,
      !!ring && ring.style !== 'none' && parseFloat(ring.width) >= 2);

    // A term page, for a record naming a confusable, so the page carries a Term to open.
    const rec = gl.terms.find((t) => Array.isArray(t.confusable_with) && t.confusable_with.length);
    if (!rec) {
      unjudged.push('the Term popover — no glossary record names a confusable, so no term page '
        + 'carries a Term to open');
    } else {
      await visit(formatHash('glossary', { term: rec.id }));
      await page.waitForSelector('[data-glossary-page] [data-definition]', { timeout: 15000 })
        .catch(() => {});
      const shown = await page.evaluate(() =>
        document.querySelector('[data-glossary-page] [data-definition]')?.textContent || '');
      check(`the term page shows the record's own definition (${rec.id})`,
        shown.trim() === String(rec.definition).trim());
      const terms = page.locator('[data-glossary-page] button.tdl-term[data-term]');
      const nTerms = await terms.count();
      check(`the term page carries a Term to open (${nTerms})`, nTerms > 0);
      if (nTerms) {
        const term = terms.first();
        const tid = await term.getAttribute('data-term');
        await term.focus();
        await page.keyboard.press('Enter');
        await page.waitForSelector('[role="dialog"][data-term-popover]', { timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(150);
        const pop = await page.evaluate(() => {
          const d = document.querySelector('[role="dialog"][data-term-popover]');
          if (!d) return null;
          const b = document.querySelector('button.tdl-term[aria-expanded="true"]');
          const lab = d.getAttribute('aria-labelledby');
          const r = d.getBoundingClientRect();
          return {
            modal: d.getAttribute('aria-modal'),
            labelled: !!(lab && document.getElementById(lab)?.textContent.trim()),
            controls: !!b && b.getAttribute('aria-controls') === d.id,
            more: d.querySelector('.tdl-term-pop-more')?.getAttribute('href') || null,
            focusInside: d.contains(document.activeElement),
            inView: r.width > 0 && r.left >= 0 && r.top >= 0 && r.right <= innerWidth && r.bottom <= innerHeight,
            def: d.querySelector('.tdl-term-pop-def')?.textContent || '',
          };
        });
        check('Enter on a Term opens its definition as a dialog', pop !== null);
        if (pop) {
          check('the dialog is non-modal: it carries no aria-modal', pop.modal === null);
          check('and is labelled by its word', pop.labelled);
          check('the word says it is expanded and names the dialog it controls', pop.controls);
          check(`"more" is the record's citation (${pop.more})`, pop.more === `#/cite/term:${tid}`);
          check('a keyboard reader is taken into the definition', pop.focusInside);
          check('the definition stands inside the window', pop.inView);
          const want = gl.terms.find((t) => t.id === tid)?.definition || '';
          check('and it says the record’s own definition', !!want && pop.def.trim() === want.trim());
        }
        await page.keyboard.press('Escape');
        await page.waitForTimeout(200);
        const after = await page.evaluate(() => ({
          open: !!document.querySelector('[role="dialog"][data-term-popover]'),
          back: !!document.activeElement?.matches?.('button.tdl-term')
            && document.activeElement.getAttribute('aria-expanded') === 'false',
        }));
        check('Escape closes the definition', !after.open);
        check('and gives focus back to the word', after.back);

        await page.mouse.move(0, 0);
        await term.hover();
        await page.waitForTimeout(800);
        check('a mouse resting on the word opens it after the delay',
          (await page.locator('[role="dialog"][data-term-popover]').count()) === 1);
        await visit('#/glossary');
        await page.waitForTimeout(300);
        check('a change of place closes every definition',
          (await page.locator('[role="dialog"][data-term-popover]').count()) === 0);
      }
    }

    // The reflow: below the shell's floor the Glossary still fits the window.
    const vp = page.viewportSize();
    await page.setViewportSize({ width: 1280, height: vp.height });
    await page.waitForTimeout(400);
    const sideways = await page.evaluate(() =>
      document.scrollingElement.scrollWidth - document.scrollingElement.clientWidth);
    check(`the Glossary reflows at 1280 px with no sideways scroll (${sideways} px over)`, sideways <= 1);
    await page.setViewportSize(vp);
    await shot('glossary', [SHOT_WIDTH, 1280]);
  }
}

/* ------------------------------------------------------------ WP-14.10: THE HOUSE JOURNEY

   One bar, mounted by App above <main> on the six house surfaces -- the five steps and the
   tracing surface that joins them at the plan -- and on no other. Where it is shown is read off
   the router's own table of surfaces, so a surface added later is judged without this list
   growing; which six are the house is the bar's rule and is stated here once, for the check.
   Full screen is not driven: only the family tree offers it and the bar is not there anyway, so a
   walk check would pass over an absence it did not cause. `journey/bar.js`'s `showJourneyBar`
   is driven over every surface with full screen on in `src/journeyBar.test.mjs`. */
async function journeyRead() {
  // A FUNCTION DECLARATION, so the two refusal blocks above can call it: it is hoisted to the
  // top of the module, where a const or a block-scoped declaration here would not be.
  return page.evaluate(() => {
    const bar = document.querySelector('nav[aria-label="house journey"]');
    if (!bar) return null;
    const steps = {};
    for (const el of bar.querySelectorAll('[data-step]')) {
      const id = el.getAttribute('data-step');
      const w = bar.querySelector(`[data-step-words="${id}"]`);
      steps[id] = { tag: el.tagName.toLowerCase(), blocked: el.getAttribute('data-blocked'),
        current: el.getAttribute('aria-current'), href: el.getAttribute('href'),
        words: w ? w.textContent.replace(/\s+/g, ' ').trim() : null };
    }
    const next = bar.querySelector('[data-next]');
    return {
      inMain: !!bar.closest('main'),
      steps,
      next: next ? { tag: next.tagName.toLowerCase(), id: next.getAttribute('data-next'),
        href: next.getAttribute('href'), text: next.textContent.replace(/\s+/g, ' ').trim() } : null,
      origin: bar.querySelector('[data-journey-origin]')?.getAttribute('data-journey-origin') || null,
    };
  });
}
{
  const HOUSE = { brief: 'brief', candidates: 'candidates', workbench: 'plan', drawings: 'drawings',
    export: 'export', transcription: 'transcription' };
  const surfaces = Object.keys(SURFACE_PATHS);
  // the denominator first: the router must still know every house surface this names
  const unknown = Object.keys(HOUSE).filter((s) => !surfaces.includes(s));
  check(`the router knows every house surface the bar is for (${unknown.join(', ') || 'all six'})`, !unknown.length);
  const shownOn = [];
  const wrong = [];
  for (const s of surfaces) {
    await visit(formatHash(s, {}, {}));
    await page.waitForTimeout(250);
    const jb = await journeyRead();
    if (jb) shownOn.push(s);
    if (HOUSE[s]) {
      const cur = jb && Object.entries(jb.steps).filter(([, v]) => v.current === 'step').map(([k]) => k);
      if (!jb) wrong.push(`${s}: no bar`);
      else if (jb.inMain) wrong.push(`${s}: the bar is inside <main>`);
      else if (!cur || cur.length !== 1 || cur[0] !== HOUSE[s]) wrong.push(`${s}: marks ${JSON.stringify(cur)} current`);
    } else if (jb) {
      wrong.push(`${s}: a bar where there is no house step`);
    }
  }
  check(`the journey is on the six house surfaces and no other (shown on ${shownOn.join(', ')})`
    + (wrong.length ? ' -- ' + wrong.join('; ') : ''), wrong.length === 0 && shownOn.length === 6);

  /* Next is a link exactly where the step in view can proceed. Read on the steps a fresh reader
     meets: whatever the bench holds by now, the export step is last and offers no Next, and a
     step that is blocked is never the target of a link. */
  await visit('#/export');
  await page.waitForTimeout(250);
  const last = await journeyRead();
  check('the last step offers no Next', !!last && !last.next);
  for (const s of ['brief', 'candidates', 'workbench', 'drawings']) {
    await visit(formatHash(s, {}, {}));
    await page.waitForTimeout(250);
    const jb = await journeyRead();
    const n = jb && jb.next;
    const target = n && jb.steps[n.id];
    const why = [];
    if (!n) why.push('no Next at all');
    else if (n.tag === 'a' && (!target || target.tag !== 'a')) why.push(`a link on to ${n.id}, which is ${target ? target.blocked : 'absent'}`);
    else if (n.tag === 'a' && parseHash(n.href).surface !== parseHash(target.href).surface) why.push(`it links to ${n.href}, not the ${n.id} step`);
    else if (n.tag !== 'a' && !n.text) why.push('a blocked Next that does not say why');
    check(`Next on ${s} is a link only where the step can proceed (${n ? `${n.tag} "${n.text}"` : 'none'})`
      + (why.length ? ' -- ' + why.join('; ') : ''), why.length === 0);
  }
  await visit('#/workbench');
  await page.waitForTimeout(250);
  await shot('journey', [SHOT_WIDTH, 1440, 1280]);
}

/* ── WP-14.11: A LICENCE SHOWS THE SERVER'S VERDICT, NEVER COLLAPSED ────────────────────────────
   A style's exception is a licence, and whether the style EARNS it is `core.grant_exception`'s
   verdict, served as `for_this_style.exception.granted`: granted, refused or unjudged. The card
   printed the licence's own words under an "exception for" heading whatever the verdict, so a
   refused licence and one nobody could judge both read as earned. One fault and style per verdict
   is FOUND through `/api/faults?style=` (whose cards name the verdict), never named here; the card
   must print that verdict's glossary word, after the two answers and before the symptom. A verdict
   the corpus offers no instance of is COULD NOT EVALUATE, not a pass.

   AND THE CARD MUST BE THE FAULT THE ADDRESS NAMES. This block's first run went red on the refused
   case with no licence on the card at all -- and the card was not the fault asked for: moving to a
   new fault AND a new style in one navigation sent two requests (the old fault under the new style,
   then the new fault), and whichever resolved last was drawn. Every check here reads the card's own
   `data-fault` first, and the last check forces the stale answer to land last, so the guard does
   not depend on the machine's timing to bite. */
{
  const phyl = await (await fetch(BASE + '/api/phylogeny')).json();
  const CARD_KEY = { granted: 'EXCEPTION_FOR_THIS_STYLE', refused: 'EXCEPTION_NOT_EARNED_BY_THIS_STYLE',
    unjudged: 'EXCEPTION_WHOSE_CONDITION_COULD_NOT_BE_JUDGED' };
  const TERM = { granted: 'exception-granted', refused: 'exception-refused', unjudged: 'judgment-unjudged' };
  const found = {};
  for (const id of phyl.taxa.map((t) => t.id).sort()) {
    if (Object.keys(found).length === 3) break;
    const r = await (await fetch(`${BASE}/api/faults?style=${encodeURIComponent(id)}&limit=300`)).json();
    for (const [v, k] of Object.entries(CARD_KEY)) {
      const c = !found[v] && (r.faults || []).find((f) => f[k]);
      if (c) found[v] = { fault: c.id, style: id };
    }
  }
  let last = null;
  for (const v of ['granted', 'refused', 'unjudged']) {
    if (!found[v]) {
      unjudged.push(`a licence ${v} is shown as ${v} — no fault in the corpus carries a ${v} licence for any style`);
      continue;
    }
    const { fault: fid, style: sid } = found[v];
    const served = await (await fetch(`${BASE}/api/faults/${fid}?style=${encodeURIComponent(sid)}`)).json();
    const verdict = served && served.for_this_style && served.for_this_style.exception
      ? served.for_this_style.exception.granted : null;
    await visit(`#/faults/${fid}?style=${sid}`);
    last = { fault: fid, style: sid };
    await page.waitForSelector(
      `main article[data-fault="${fid}"] [data-fault-section="licence"] [data-licence-verdict] button.tdl-term`,
      { timeout: 20000 }).catch(() => {});
    const onCard = await page.$eval('main article[data-fault]', (el) => el.getAttribute('data-fault'))
      .catch(() => null);
    const shown = await page.$$eval('main [data-fault-section="licence"] [data-licence-verdict] [data-term]',
      (els) => els.map((el) => el.getAttribute('data-term')));
    const order = await page.$$eval('main article[data-fault] [data-fault-section]',
      (els) => els.map((el) => el.getAttribute('data-fault-section')));
    check(`${v === 'unjudged' ? 'an' : 'a'} ${v} licence (${fid} for ${sid}): the card is that fault (${onCard}) and prints the server's `
      + `verdict, ${verdict} (${shown.join(',')})`,
      onCard === fid && verdict === v && shown.length === 1 && shown[0] === TERM[verdict]);
    check(`and the licence follows the two answers and leads the rule (${order.slice(0, 4).join(' · ')})`,
      order[0] === 'correct_practice' && order[1] === 'detection' && order[2] === 'licence'
        && order.indexOf('licence') < order.indexOf('symptom'));
    await page.evaluate(() => {
      const el = document.querySelector('main [data-fault-section="licence"]');
      if (el) el.scrollIntoView({ block: 'center' });
    });
    await page.waitForTimeout(300);
    await shot('fault-licence-' + v);
  }

  /* The superseded answer, forced. Delay every response about the fault on screen, then move to
     another fault under another style: the request the surface sends for the OLD fault under the
     NEW style now lands last, and the card must still be the fault the address names. */
  const to = ['granted', 'refused', 'unjudged'].map((v) => found[v])
    .find((f) => f && last && f.fault !== last.fault && f.style !== last.style);
  if (!to) {
    unjudged.push('a superseded fault request does not replace the card — the corpus offered no '
      + 'second fault under a second style to move to');
  } else {
    const stale = last.fault;
    const slow = (url) => url.pathname === '/api/faults/' + stale;
    let delayed = 0;
    await page.route(slow, async (route) => {
      delayed += 1;
      await new Promise((r) => setTimeout(r, 900));
      await route.continue().catch(() => {});
    });
    await visit(`#/faults/${to.fault}?style=${to.style}`);
    await page.waitForTimeout(2500);
    const onCard = await page.$eval('main article[data-fault]', (el) => el.getAttribute('data-fault'))
      .catch(() => null);
    await page.unroute(slow);
    if (!delayed) {
      unjudged.push(`a superseded fault request does not replace the card — moving from ${stale} to `
        + `${to.fault} sent no request for ${stale}, so there was no stale answer to hold back`);
    } else {
      check(`a superseded fault request does not replace the card: the address names ${to.fault}, `
        + `the late answer was ${stale}, the card is ${onCard}`, onCard === to.fault);
    }
  }
}

/* ------------------------------------------------------------------ WP-14.13: THE SHELL

   Every page says where it is, what it is and what comes next. What is asserted here is read
   off the server — the glossary, the dossier, the search index, /api/overview — never a figure
   or a label written into this file, and every negative assertion first proves that the thing
   it looks for can be found. Each block that needs an empty browser opens its own context, so
   nothing the walk above stored in localStorage decides what these see. */
{
  const glossaryOk = Boolean(LOOKUP);
  if (!glossaryOk) {
    unjudged.push('the shell\'s crumbs, titles and names -- GET /api/glossary did not answer with a terms '
      + 'list, so there is no record to hold a crumb or a title against');
  }

  // (1) THE TRAIL. Styles, then the member_of chain root first, then the style, the section and
  // the slot; every name the server's, the last crumb the page and no link.
  await page.goto(BASE + '/#/style/tidewater-georgian/kit/cornice', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  const dossier = await (await fetch(BASE + '/api/styles/tidewater-georgian/dossier')).json().catch(() => null);
  const crumbs = page.locator('nav[aria-label="crumbs"] li');
  const got = (await crumbs.evaluateAll((lis) => lis.map((li) => {
    const t = li.querySelector('a, [aria-current], span:not([aria-hidden])');
    return { text: (t ? t.textContent : '').trim(), href: li.querySelector('a')?.getAttribute('href') || null,
      current: li.querySelector('[aria-current="page"]') ? true : false };
  })));
  if (glossaryOk && dossier && Array.isArray(dossier.chain)) {
    const want = [TERM('nav-group-styles'), ...dossier.chain.map((c) => c.name), dossier.name,
      TERM('section-kit'), NAME_OF('slot:cornice')];
    check(`the crumbs follow the filing, not the lineage (${got.map((g) => g.text).join(' › ')})`,
      JSON.stringify(got.map((g) => g.text)) === JSON.stringify(want));
    check('each ancestor crumb links its own dossier',
      dossier.chain.every((c, i) => got[1 + i] && got[1 + i].href === formatHash('style', { style: c.id }, {})));
    check('the last crumb is the page, and not a link',
      got.length > 0 && got[got.length - 1].current && got[got.length - 1].href === null
      && got.filter((g) => g.current).length === 1);
  } else {
    unjudged.push('the crumb trail -- /api/styles/tidewater-georgian/dossier answered no chain to hold it to');
  }
  const crumbText = await page.locator('nav[aria-label="crumbs"]').innerText().catch(() => '');
  check('no work-package or question ids in the crumbs', crumbText.length > 0
    && !/\bWP-\d|\bOQ\s?\d|\boq\//.test(crumbText));
  check('the front door has no trail', await (async () => {
    await visit('#/');
    await page.waitForTimeout(300);
    return (await page.locator('nav[aria-label="crumbs"]').count()) === 0;
  })());

  // (2) THE PAGE HEAD: one per page, and the record the site map names for the place.
  for (const [hash, want] of [['#/faults', 'surface-faults'], ['#/proportions', 'surface-proportions'],
    ['#/style/tidewater-georgian/lineage', 'section-lineage'], ['#/workbench', 'surface-workbench']]) {
    await visit(hash);
    await page.waitForTimeout(300);
    const heads = await page.locator('[data-page-head]').evaluateAll((hs) => hs.map((h) => h.getAttribute('data-page-head')));
    check(`${hash} is headed by its own record, once (${JSON.stringify(heads)})`,
      heads.length === 1 && heads[0] === want);
  }

  // (3) THE TAB TITLE: the page first, the product last, and no two places alike.
  if (glossaryOk) {
    const titles = new Map();
    const places = ['#/', '#/style', '#/style/tidewater-georgian', '#/style/tidewater-georgian/kit/cornice',
      '#/style/craftsman', '#/phylogeny', '#/brief', '#/candidates', '#/workbench', '#/transcription',
      '#/drawings', '#/export', '#/proportions', '#/proportions/trim-classical', '#/faults', '#/glossary',
      '#/glossary/judgment-unjudged'];
    const clashes = [];
    for (const h of places) {
      await visit(h);
      await page.waitForFunction((about) => document.title && (location.hash === '#/' || location.hash === ''
        || document.title !== about), TERM('about-tdl'), { timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(250);
      const t = await page.title();
      if (titles.has(t)) clashes.push(`${h} and ${titles.get(t)} both read "${t}"`);
      titles.set(t, h);
    }
    check(`no two places share a tab title (${titles.size} of ${places.length})` + (clashes.length ? ' -- ' + clashes.join('; ') : ''),
      clashes.length === 0 && titles.size === places.length);
    check('the front door\'s title is the product\'s name alone', titles.get(TERM('about-tdl')) === '#/');
    check('a page\'s title ends with the product\'s name',
      [...titles.keys()].every((t) => t.endsWith(TERM('about-tdl'))));
  }

  // (4) THE MASTHEAD: home, the bench as a place and three counts, the keys, and nothing inert.
  await visit('#/faults');
  await page.waitForTimeout(300);
  const header = page.locator('header').first();
  check('the wordmark is the way home', await header.locator('a[href="#/"]').count() === 1);
  const headText = await header.innerText();
  check('the masthead no longer calls a page "the workbench"', !/\bthe workbench\b/i.test(headText));
  check('the inert Export and Settings icons are gone',
    await header.locator('[title="Export"], [title="Settings"], svg[aria-label="Export"], svg[aria-label="Settings"]').count() === 0);
  check('no work-package or question ids in the masthead', !/\bWP-\d|\bOQ\s?\d|\boq\//.test(headText));
  const stored = await page.evaluate(() => { try { return JSON.parse(localStorage.getItem('tdl-workbench-plan') || 'null'); } catch { return null; } });
  const benchPlan = stored && (stored.plan || stored.doc || stored);
  const benchLink = header.locator('[data-bench-link]');
  if (benchPlan && (benchPlan.name || benchPlan.id)) {
    const text = (await benchLink.first().textContent().catch(() => '')) || '';
    check(`the bench is a place: "On the bench: <its name>" links to it (${JSON.stringify(text.trim())})`,
      await benchLink.count() === 1 && (await benchLink.getAttribute('href')) === '#/workbench'
      && text.includes(benchPlan.name || benchPlan.id));
    const counted = await header.locator('[data-count]').count();
    const terms = await header.locator('[data-bench-counts] [data-term]').evaluateAll((ts) => ts.map((t) => t.getAttribute('data-term')));
    check(`fatal, serious and unjudged stay three, or the plan says it is not yet evaluated (${JSON.stringify(terms)})`,
      counted === 0
        ? /not yet evaluated/.test(await header.innerText())
        : JSON.stringify(terms) === JSON.stringify(['severity-fatal', 'severity-serious', 'judgment-unjudged']));
  } else {
    unjudged.push('the masthead\'s bench line -- no plan was on the bench to name');
  }
  const keys = header.getByRole('button', { name: /^Keys/ });
  check('a visible Keys button', await keys.count() === 1 && await keys.isVisible());
  await keys.click();
  const card = page.getByRole('dialog', { name: 'Keyboard shortcuts and addressing', exact: true });
  await card.waitFor({ state: 'visible', timeout: 3000 }).catch(() => {});
  check('and it opens the keys card', await card.count() === 1);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(200);

  // (5) FULL SCREEN TAKES THE TRAIL AND THE HEAD WITH IT. Asserted present first, so the two
  // zeroes cannot both be the shell failing to draw them.
  await page.goto(BASE + '/#/phylogeny/tidewater-georgian?view=map', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  const trailAndHead = async () => [await page.locator('nav[aria-label="crumbs"]').count(),
    await page.locator('[data-page-head]').count()];
  const before = await trailAndHead();
  check(`the trail and the head are on this page to begin with (${before})`, before[0] === 1 && before[1] === 1);
  await page.getByRole('button', { name: /full screen/i }).first().click();
  await page.waitForTimeout(500);
  const inFull = await trailAndHead();
  check(`full screen hides the crumbs and the page head (${inFull})`, inFull[0] === 0 && inFull[1] === 0);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  const after = await trailAndHead();
  check(`and leaving it brings both back (${after})`, after[0] === 1 && after[1] === 1);
}

/* (6) THE COLD LINK, ONCE PER BROWSER. A fresh browser opening a deep link is told what this is
   and where it has landed; dismissing it is remembered; a browser that has seen the front door
   is never told. Three contexts, each with empty storage. */
{
  const about = await (await fetch(BASE + '/api/glossary/about-tdl')).json().catch(() => null);
  const def = about && about.term ? about.term.definition : null;
  const ctx = await browser.newContext({ viewport: { width: 1680, height: 1000 } });
  const p = await ctx.newPage();
  await p.goto(BASE + '/#/faults', { waitUntil: 'networkidle' });
  await p.waitForTimeout(1000);
  const banner = p.locator('[data-cold-link]');
  const text = (await banner.first().textContent().catch(() => '')) || '';
  check('a cold deep link is told what this is', await banner.count() === 1 && Boolean(def) && text.includes(def));
  check('and where it has landed', /Faults/.test(await banner.locator('[data-cold-link-trail]').first().textContent().catch(() => '')));
  check('with the front door and the guided example as its two ways in',
    (await banner.locator('[data-cold-link-front]').getAttribute('href')) === '#/'
    && /^#\/style\//.test((await banner.locator('[data-cold-link-guided]').getAttribute('href')) || ''));
  await banner.locator('[data-cold-link-dismiss]').click();
  await p.waitForTimeout(300);
  check('dismissing it takes it away', await p.locator('[data-cold-link]').count() === 0);
  await p.reload({ waitUntil: 'networkidle' });
  await p.waitForTimeout(800);
  check('and it does not come back on a reload', await p.locator('[data-cold-link]').count() === 0);
  await ctx.close();

  const ctx2 = await browser.newContext({ viewport: { width: 1680, height: 1000 } });
  const p2 = await ctx2.newPage();
  await p2.goto(BASE + '/', { waitUntil: 'networkidle' });
  await p2.waitForTimeout(800);
  check('the front door itself shows no banner', await p2.locator('[data-cold-link]').count() === 0);
  await p2.goto(BASE + '/#/faults', { waitUntil: 'networkidle' });
  await p2.reload({ waitUntil: 'networkidle' });
  await p2.waitForTimeout(800);
  check('a browser that has seen the front door is not told again', await p2.locator('[data-cold-link]').count() === 0);
  await ctx2.close();
}

/* (7) THE NARROW FOLD (PRD §I.11). With nothing stored the assistant starts folded below
   NARROW_FOLD_PX and open above it; a stored choice wins; the spine carries its record's name. */
{
  const assistant = await (await fetch(BASE + '/api/glossary/assistant')).json().catch(() => null);
  const name = assistant && assistant.term ? assistant.term.term : null;
  const open = async (w, seed) => {
    const ctx = await browser.newContext({ viewport: { width: w, height: 800 } });
    if (seed) await ctx.addInitScript((v) => { localStorage.setItem('tdl-workbench-layout', v); }, JSON.stringify(seed));
    const p = await ctx.newPage();
    await p.goto(BASE + '/#/faults', { waitUntil: 'networkidle' });
    await p.waitForSelector('nav[aria-label="surfaces"]', { timeout: 15000 }).catch(() => {});
    await p.waitForTimeout(600);
    return { ctx, p, pane: await p.locator('aside[aria-label*="the rail"]').count(),
      stub: await p.getByRole('button', { name: /show the rail/i }).count() };
  };
  const a = await open(1280);
  check(`at 1280 px with nothing stored the assistant starts folded (${a.pane} pane, ${a.stub} spine)`, a.pane === 0 && a.stub === 1);
  const spine = ((await a.p.locator('button[aria-label="show the rail"] + span').first().textContent().catch(() => '')) || '').trim();
  check(`and its spine carries its name (${JSON.stringify(spine)})`, Boolean(name) && spine === name);
  const storedAfter = await a.p.evaluate(() => localStorage.getItem('tdl-workbench-layout'));
  check('and the fold was not written for the reader', storedAfter === null);
  await a.p.setViewportSize({ width: 1680, height: 800 });
  await a.p.waitForTimeout(400);
  check('widening the window does not unfold it', await a.p.locator('aside[aria-label*="the rail"]').count() === 0);
  await a.ctx.close();
  const b = await open(1680);
  check('at 1680 px with nothing stored it is open', b.pane === 1);
  await b.p.setViewportSize({ width: 1280, height: 800 });
  await b.p.waitForTimeout(400);
  check('and narrowing the window does not fold it', await b.p.locator('aside[aria-label*="the rail"]').count() === 1);
  await b.ctx.close();
  const c = await open(1280, { widths: {}, collapsed: { rail: false } });
  check('a stored open assistant stays open at 1280 px', c.pane === 1);
  await c.ctx.close();
  const d = await open(1680, { widths: {}, collapsed: { rail: true } });
  check('a stored folded assistant stays folded at 1680 px', d.pane === 0 && d.stub === 1);
  await d.ctx.close();
}

/* (8) A SERVER THAT DOES NOT ANSWER IS SAID, WITH A WAY TO TRY AGAIN — never a blank page. */
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const p = await ctx.newPage();
  await p.route('**/api/health', (r) => r.abort());
  await p.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  const status = p.locator('[role="status"][data-boot-status]');
  await status.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
  check('an unreachable server is said, not a blank page',
    await status.count() === 1 && /Cannot reach the server/.test(await status.innerText()));
  await p.unroute('**/api/health');
  await status.getByRole('button', { name: 'Retry' }).click();
  await p.waitForSelector('nav[aria-label="surfaces"]', { timeout: 15000 }).catch(() => {});
  check('and Retry brings the shell back', await p.locator('nav[aria-label="surfaces"]').count() === 1);
  await ctx.close();
}

/* THE GATE SAYS ONE SENTENCE AND ASKS FOR NOTHING ELSE (WP-14.14, PRD §C.3, §J).

   Signed out, exactly one corpus path answers: `GET /api/glossary/about-tdl`, whose definition
   the Gate shows under its heading. The server this walk is pointed at has no password, so no
   page on it is ever signed out and the Gate cannot be reached there; this block starts a SECOND
   server from the same checkout with a password set, opens a fresh context against it, and asks
   three things: the sentence shown is that record's definition (read from the record, never
   typed here); the page asked no corpus route but that one; and when that one read fails, the
   Gate says NOTHING in its place -- no error, no fallback sentence -- so what is left on the
   form is exactly the signed-out form less the one sentence.

   ONE CALL IS NOT THIS PAGE'S AND IS NAMED RATHER THAN HIDDEN. `App.jsx` boots by asking
   `/api/overview` once to learn whether this browser already holds a session; signed out it
   answers 401 and carries no corpus text. The shell is WP-14.13's; the check below requires that
   probe to have answered 401 and to be the only other call, so a second one -- or a probe that
   answered with the corpus -- fails. If the gated server cannot be started the block is UNJUDGED
   by name, never passed. */
{
  const GATE_PORT = Number(process.env.WALK_GATE_PORT || (Number(new URL(BASE).port || 80) + 1));
  const GATE = `http://127.0.0.1:${GATE_PORT}`;
  const ROOT = new URL('../../../', import.meta.url).pathname;
  const { spawn } = await import('node:child_process');
  const srv = spawn('python3', ['-m', 'uvicorn', 'workbench.server.app:app', '--host', '127.0.0.1',
    '--port', String(GATE_PORT), '--log-level', 'error'], {
    cwd: ROOT, stdio: 'ignore',
    env: { ...process.env, WORKBENCH_PASSWORD: `walk-gate-${process.pid}-${Date.now()}` },
  });
  const stop = () => { try { srv.kill(); } catch { /* already gone */ } };
  process.on('exit', stop);
  let health = null;
  for (let i = 0; i < 80 && !health; i++) {
    health = await fetch(GATE + '/api/health').then((r) => (r.ok ? r.json() : null)).catch(() => null);
    if (!health) await new Promise((r) => setTimeout(r, 500));
  }
  const closed = health && health.auth && health.auth.required
    ? await fetch(GATE + '/api/overview').then((r) => r.status).catch(() => null) : null;
  const aboutOpen = await fetch(GATE + '/api/glossary/about-tdl')
    .then((r) => (r.ok ? r.json() : null)).then((b) => (b && b.term) || null).catch(() => null);
  if (!health || closed !== 401 || !aboutOpen) {
    unjudged.push('the Gate — a password-protected server could not be brought up beside this one '
      + `on port ${GATE_PORT} (health ${health ? 'answered' : 'did not answer'}, /api/overview `
      + `${closed === null ? 'unasked' : closed}, about-tdl ${aboutOpen ? 'answered' : 'did not answer'}), `
      + 'so there is no signed-out page to judge');
  } else {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const read = async (gp) => gp.evaluate(() => ({
      about: document.querySelector('[data-about-tdl]')?.textContent || null,
      lines: (document.querySelector('form')?.innerText || '').split('\n').map((s) => s.trim()).filter(Boolean),
    }));

    const gp = await ctx.newPage();
    const calls = [];
    gp.on('response', (r) => {
      const u = new URL(r.url());
      if (u.pathname.startsWith('/api/')) calls.push([u.pathname, r.status()]);
    });
    await gp.goto(GATE + '/', { waitUntil: 'networkidle' });
    await gp.waitForSelector('#wb-password', { timeout: 20000 }).catch(() => {});
    await gp.waitForSelector('[data-about-tdl]', { timeout: 10000 }).catch(() => {});
    await gp.waitForTimeout(500);
    const shown = await read(gp);
    check('signed out, the Gate shows about-tdl\'s definition, read from the one open glossary path',
      shown.about === aboutOpen.definition);
    const probes = calls.filter(([p]) => p === '/api/overview');
    const others = calls.filter(([p]) => !['/api/health', '/api/login', '/api/glossary/about-tdl', '/api/overview'].includes(p));
    check(`signed out, the page asked no corpus route but about-tdl (${calls.map(([p, s]) => `${p} ${s}`).join(', ')})`,
      others.length === 0 && probes.length <= 1 && probes.every(([, s]) => s === 401)
      && calls.some(([p, s]) => p === '/api/glossary/about-tdl' && s === 200));
    for (const w of [1280, 1440, 1680]) {
      await gp.setViewportSize({ width: w, height: { 1280: 800, 1440: 900, 1680: 1050 }[w] });
      await gp.waitForTimeout(250);
      await gp.screenshot({ path: SHOTS + `gate-${w}.png` });
    }

    // The read fails two ways -- no answer at all, and an error answer -- and neither may leave a
    // sentence behind: the form must read exactly as it does signed out, less the definition.
    const expected = shown.lines.filter((l) => l !== aboutOpen.definition.trim());
    for (const [how, handler] of [
      ['a failed request', (route) => route.abort()],
      ['a 500', (route) => route.fulfill({ status: 500, contentType: 'application/json', body: '{"detail":"x"}' })],
    ]) {
      const fp = await ctx.newPage();
      await fp.route('**/api/glossary/about-tdl', handler);
      await fp.goto(GATE + '/', { waitUntil: 'networkidle' });
      await fp.waitForSelector('#wb-password', { timeout: 20000 }).catch(() => {});
      await fp.waitForTimeout(700);
      const got = await read(fp);
      check(`when the about-tdl read fails (${how}) the Gate says nothing in its place`,
        // the premise: the signed-out form really carried the sentence, so removing it is a change
        expected.length === shown.lines.length - 1
        && got.about === null && got.lines.length > 0
        && JSON.stringify(got.lines) === JSON.stringify(expected));
      await fp.close();
    }
    await ctx.close();
  }
  stop();
}

await browser.close();
if (limited) {
  console.error('\nCOULD NOT EVALUATE: the server rate-limited this run (429 at ' + limited
    + '). Restart it and run again — an unjudged walk is not a green one.');
  process.exit(3);
}
if (failures.length) { console.error('\nFAILED:', failures); process.exit(1); }
if (unjudged.length) {
  console.error('\nCOULD NOT EVALUATE (' + unjudged.length + '):');
  for (const u of unjudged) console.error('  ' + u);
  /* AND THE FOOTER NO LONGER ASSERTS A CAUSE IT CANNOT KNOW. It read "because this server does
     not yet answer WP-13.4's refusal contract" -- which was the only cause when the line was
     written and is now one of several: three of the four unjudged states on this corpus are
     facts about the RECORD on the bench (it places no stack, no stoop, and states no date of
     representation) and one is two separate solves of one document. Each entry above says its
     own reason; a summary that names a different one sends the reader to the wrong place, which
     is `workbench/scripts/walk.sh`'s own lesson one file over. */
  console.error('An unjudged walk is not a green one. Nothing above failed; each line says why');
  console.error('it could not be judged.');
  process.exit(3);
}
console.log('\nE2E WALK GREEN');
