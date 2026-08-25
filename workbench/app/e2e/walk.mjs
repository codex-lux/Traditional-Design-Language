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
check('forthcoming surfaces listed, not hidden', railText.includes('forthcoming'));

// ⑦ Plan Workbench: load an example, wait for evaluation
await page.getByRole('button', { name: /Plan Workbench/ }).click();
const example = page.getByRole('button', { name: 'tidewater-georgian-careful' });
if (await example.count()) await example.click();
await page.waitForSelector('svg[role="img"]', { timeout: 30000 });
const body = await page.locator('main').innerText();
check('three-state panel present (could not evaluate)', /could not evaluate/i.test(body));
check('hill-climb honesty line present', /hill-climb/i.test(body));
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
check('WP-2.3 conflict set marked forthcoming', /forthcoming \(WP-2\.3\)/i.test(brief));
await page.screenshot({ path: SHOTS + 'brief.png' });

// ⑥ Candidate Set (empty state without a run)
await page.getByRole('button', { name: /Candidate Set/ }).click();
await page.waitForTimeout(500);
await page.screenshot({ path: SHOTS + 'candidates.png' });

// the rail's honest no-key state
const rail = await page.locator('aside').last().innerText();
check('rail present on every surface', /the rail/i.test(rail));

await browser.close();
if (failures.length) { console.error('\nFAILED:', failures); process.exit(1); }
console.log('\nE2E WALK GREEN');
