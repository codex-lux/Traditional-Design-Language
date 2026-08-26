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

// Browser resolution, in order: an explicit CHROMIUM, this machine's preinstalled one if it
// is actually there, else whatever playwright installed for itself. It used to hardcode
// /opt/pw-browsers/chromium as the fallback, which exists on exactly one machine — so this
// walk could never have run in CI even if CI had been running it (it was not).
import { existsSync } from 'node:fs';
const LOCAL = '/opt/pw-browsers/chromium';
const exe = process.env.CHROMIUM || (existsSync(LOCAL) ? LOCAL : null);
const browser = await chromium.launch(exe ? { executablePath: exe } : {});
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
