/* Screenshots of the shell at three laptop-to-desktop widths, with nothing stored (WP-14.13).

   Run against a server serving the built app:  WB_URL=http://127.0.0.1:8179 node e2e/shots-shell.mjs <outdir>

   Each shot is taken in a FRESH browser context, so localStorage is empty and the page is the
   one a first-time reader gets: at 1280 and 1440 the assistant starts folded (PRD §I.11), at
   1680 it is open. Not a check — the walk is the check; this is for looking at. */
import { createRequire } from 'node:module';
import { existsSync, mkdirSync } from 'node:fs';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const BASE = process.env.WB_URL || 'http://127.0.0.1:8179';
const OUT = process.argv[2] || new URL('./shots/', import.meta.url).pathname;
mkdirSync(OUT, { recursive: true });
const EXEC = process.env.CHROMIUM
  || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);
const browser = await chromium.launch(EXEC ? { executablePath: EXEC } : {});

const PLACES = [
  ['front-door', '#/'],
  ['kit-cornice', '#/style/tidewater-georgian/kit/cornice'],
  ['trim-classical', '#/proportions/trim-classical'],
  ['workbench', '#/workbench'],
];
const SIZES = [[1280, 800], [1440, 900], [1680, 1050]];

for (const [w, h] of SIZES) {
  for (const [name, hash] of PLACES) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h } });
    const page = await ctx.newPage();
    await page.goto(BASE + '/' + hash, { waitUntil: 'networkidle' });
    await page.waitForSelector('nav[aria-label="surfaces"]', { timeout: 20000 }).catch(() => {});
    if (name === 'workbench') {
      // a plan on the bench, so the masthead has something to say
      const ex = page.getByRole('button', { name: 'tidewater-georgian-careful' });
      await ex.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
      if (await ex.count()) await ex.click();
      await page.waitForSelector('[data-bench-counts]', { timeout: 90000 }).catch(() => {});
    }
    await page.waitForTimeout(1500);
    const file = `${OUT}/${name}-${w}.png`;
    await page.screenshot({ path: file });
    const title = await page.title();
    const rail = await page.locator('aside[aria-label*="the rail"]').count();
    console.log(`${w}x${h} ${hash} -> ${file} | title "${title}" | assistant ${rail ? 'open' : 'folded'}`);
    await ctx.close();
  }
}
await browser.close();
