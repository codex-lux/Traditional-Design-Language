/* WP-9.4. Every event name the server can put on a job's stream is registered at every
   jobEvents() call site that consumes that kind of job. jobEvents subscribes ONLY to the
   names it is handed, so a name missing at one call site is an event dropped on the floor
   with no error -- which is how the `revised` event went unheard from the day WP-9.2 added
   it until WP-9.3 noticed (and WP-9.3's fix had no guard of its own). Read with node:fs;
   no import of any .jsx, which the corpus job cannot build. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

// the names jobs.py can put, by job kind, read from the server's own DECLARATION. The first
// version regexed the string literals of each runner and could not see an event named through
// a variable (the session's audit); jobs.py now declares COMPOSE_EVENTS / REVISE_EVENTS and
// every put goes through `_put`, which refuses a name outside them -- so the tuple IS the set.
function serverEvents(kind) {
  const src = read('workbench/server/jobs.py');
  const m = src.match(new RegExp(`${kind === 'revise' ? 'REVISE' : 'COMPOSE'}_EVENTS\\s*=\\s*\\(([^)]*)\\)`));
  assert.ok(m, `jobs.py declares no ${kind} event tuple`);
  return new Set([...m[1].matchAll(/"([a-z_]+)"/g)].map((x) => x[1]));
}

// every jobEvents(...) call and the handler keys inside its braces
function callSites(file) {
  const src = read(file);
  const out = [];
  const re = /jobEvents\(([^,]+),\s*\{/g;
  let m;
  while ((m = re.exec(src))) {
    let depth = 1; let i = re.lastIndex;
    while (depth && i < src.length) { if (src[i] === '{') depth++; else if (src[i] === '}') depth--; i++; }
    const body = src.slice(re.lastIndex, i - 1);
    const keys = new Set([...body.matchAll(/(?:^|[\s,{])([a-z]+)\s*:/g)].map((k) => k[1]));
    out.push({ file, keys });
  }
  return out;
}

test('the server puts the events this suite expects, so the check is not vacuous', () => {
  assert.deepEqual([...serverEvents('compose')].sort(), ['candidate', 'done', 'error', 'revised', 'stage']);
  assert.deepEqual([...serverEvents('revise')].sort(), ['done', 'error', 'round', 'stage']);
});

test('every put in jobs.py goes through _put with a literal name inside its tuple; no bare events.put', () => {
  const src = read('workbench/server/jobs.py');
  const bare = [...src.matchAll(/events\.put\(/g)].length;
  assert.equal(bare, 1, `exactly one events.put -- inside _put -- expected, found ${bare}`);
  const all = new Set([...serverEvents('compose'), ...serverEvents('revise')]);
  const puts = [...src.matchAll(/(?<!def )_put\(job,\s*([^,]+),/g)].map((m) => m[1].trim());
  assert.ok(puts.length >= 8, `too few _put calls found (${puts.length})`);
  for (const p of puts) {
    const lit = p.match(/^"([a-z_]+)"$/);
    assert.ok(lit, `_put called with a non-literal event name: ${p}`);
    assert.ok(all.has(lit[1]), `_put puts '${lit[1]}', which no tuple declares`);
  }
});

test('every compose call site registers every compose event, revised included', () => {
  const sites = [...callSites('workbench/app/src/surfaces/CandidateSet.jsx'), ...callSites('workbench/app/src/surfaces/BriefIntake.jsx')];
  assert.ok(sites.length >= 2, 'two compose call sites are expected');
  for (const s of sites) {
    for (const ev of serverEvents('compose')) assert.ok(s.keys.has(ev), `${s.file} does not register '${ev}'`);
  }
});

test('the revise call site registers every revise event, round included', () => {
  const sites = callSites('workbench/app/src/surfaces/PlanWorkbench.jsx');
  assert.equal(sites.length, 1);
  for (const ev of serverEvents('revise')) assert.ok(sites[0].keys.has(ev), `PlanWorkbench does not register '${ev}'`);
});
