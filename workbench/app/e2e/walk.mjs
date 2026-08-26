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
await rail.getByRole('button', { name: /The Phylogeny/ }).click();
await page.waitForSelector('text=compressed', { timeout: 15000 });
const phylo = await page.locator('main').innerText();
check('phylogeny names the missing trunks', /missing peer trunks/i.test(phylo));
await page.screenshot({ path: SHOTS + 'phylogeny.png' });

// ④ Kit
await rail.getByRole('button', { name: /The Kit/ }).click();
await page.waitForSelector('text=cascade', { timeout: 15000 });
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
await rail.getByRole('button', { name: /Drawing Set/ }).click();
await page.waitForSelector('text=83 of', { timeout: 40000 });
const ds = await page.locator('main').innerText();
check('drawing set: WP-3.2 disclosure on-sheet', /83 of the 177 applicable/i.test(ds));
await page.screenshot({ path: SHOTS + 'drawing-elevation.png' });
await page.getByRole('button', { name: 'bearing lines' }).click();
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
  && /the record names no hearth/i.test(mapText));
check('the gazetteer is disclaimed as interface, not source',
  /regions in prose, not coordinates/i.test(mapText) && /none of them is a source/i.test(mapText));
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
check('? explains the keys and the addressing', /kind:id/.test(card) && /⌘K/.test(card));
await page.keyboard.press('Escape');

await browser.close();
if (failures.length) { console.error('\nFAILED:', failures); process.exit(1); }
console.log('\nE2E WALK GREEN');
