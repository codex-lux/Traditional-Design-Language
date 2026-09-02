/* The app's unit suite must import nothing from node_modules, and this is what says so.

   `build/check_all.py` runs `node --test workbench/app/src/*.test.mjs` with NO npm install
   — its own comment reads "the app suite needs no npm install; it imports no packages" —
   and the corpus CI job depends on that being true. It was a comment and nothing else.

   WP-5.7's audit pass broke it: `coastlines.test.mjs` imported `coastTiers.js`, which had
   `import React from 'react'` at the top for the one hook it held. The whole suite passed
   locally, where node_modules happens to exist, and failed the corpus job in CI with
   `Cannot find package 'react'` — a green local run and a red remote one, from an
   invariant that lived only in prose. The hook moved to `useCoastline.js`; this walks the
   graph so the next one is caught before it is pushed.

   It resolves the graph itself rather than asking node, because the failure IS a
   resolution failure: importing the offending module to inspect it is the very thing that
   throws. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));

/* A specifier is RELATIVE (./x, ../x), ABSOLUTE, or BARE (react, node:fs). Bare ones that
   are not `node:` come from node_modules and are what this forbids. */
const isBare = (spec) => !spec.startsWith('.') && !spec.startsWith('/') && !spec.startsWith('node:');

/* Static `import ... from 'x'` and `export ... from 'x'` only. A dynamic import() is
   deliberately NOT followed: `coastTiers.js` uses one to code-split the heavy coastline
   tiers, and that edge is never taken by a test — it would be resolved at call time, and
   no test calls it. Following it would forbid the very lazy-loading the map depends on. */
const SPEC = /^\s*(?:import|export)[\s\S]{0,400}?from\s+['"]([^'"]+)['"]/gm;
const SIDE_EFFECT = /^\s*import\s+['"]([^'"]+)['"]/gm;

function specifiers(source) {
  const out = [];
  for (const re of [SPEC, SIDE_EFFECT]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(source)) !== null) out.push(m[1]);
  }
  return out;
}

function walk(entry) {
  const seen = new Set();
  const offenders = [];
  const queue = [entry];
  while (queue.length) {
    const file = queue.pop();
    if (seen.has(file)) continue;
    seen.add(file);
    let source;
    try { source = readFileSync(file, 'utf8'); } catch { continue; }
    for (const spec of specifiers(source)) {
      if (isBare(spec)) { offenders.push(`${relative(HERE, file)} imports '${spec}'`); continue; }
      if (spec.startsWith('.')) queue.push(resolve(dirname(file), spec));
    }
  }
  return { offenders, seen };
}

test('nothing the app suite imports reaches node_modules', () => {
  const suites = readdirSync(HERE).filter((f) => f.endsWith('.test.mjs'));
  assert.ok(suites.length >= 4, `only ${suites.length} suites found — the glob is wrong`);
  const offenders = [];
  let reached = 0;
  for (const s of suites) {
    const r = walk(resolve(HERE, s));
    offenders.push(...r.offenders);
    reached += r.seen.size;
  }
  // The walk has to actually reach something, or it forbids nothing. More files than
  // suites: a suite may read its subject with node:fs and import nothing relative
  // (sse_handlers.test.mjs reads .jsx the corpus job cannot build), so the floor is the
  // suites plus the modules the OTHERS reach, not two per suite.
  assert.ok(reached > suites.length,
    `the import walk reached only ${reached} files from ${suites.length} suites`);
  assert.deepEqual(offenders, [],
    'build/check_all.py runs this suite with no npm install, so a package import here is a '
    + 'green local run and a red CI one:\n  ' + offenders.join('\n  '));
});

test('the walk can see a bare import when there is one', () => {
  // Proves the detector rather than trusting it: a suite that DOES import a package must
  // be caught. MapView.jsx imports React and is not in the test graph, so it is a real
  // file with a real bare import to point the walker at.
  const r = walk(resolve(HERE, 'surfaces/phylo/useCoastline.js'));
  assert.ok(r.offenders.some((o) => /'react'/.test(o)),
    `the walker missed React in useCoastline.js — it found ${JSON.stringify(r.offenders)}`);
});
