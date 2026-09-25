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
import { composeHandlers } from './journey/sessionWrites.js';

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

/* WP-14.10 (PRD §J.1): THE TWO COMPOSE CALL SITES HAND jobEvents ONE HANDLER SET, and that set
   is DRIVEN here rather than read. Until this package each site wrote its own object literal, and
   the Candidate Set's reattach stream handed `error` to `() => {}` -- so a job the server had
   given up on read "composing" on that surface for ever, while Brief Intake's own stream, which
   did look, was closed the moment the reader left Brief Intake. The earlier form of this test
   read each literal's KEYS and was satisfied by exactly that: `error` was registered. A key that
   is present and does nothing is the defect, so the check is now what each handler DOES. */

// every jobEvents(...) call and the text of its second argument, brackets balanced
function handlerArgs(file) {
  const src = read(file);
  const out = [];
  const re = /jobEvents\(([^,]+),\s*/g;
  let m;
  while ((m = re.exec(src))) {
    let depth = 1; let i = re.lastIndex;
    while (depth && i < src.length) {
      if ('({['.includes(src[i])) depth++;
      else if (')}]'.includes(src[i])) depth--;
      i++;
    }
    out.push({ file, arg: src.slice(re.lastIndex, i - 1).trim() });
  }
  return out;
}

// a store with the two methods the handlers use, recording what it was told, in order
function recorder() {
  const told = [];
  return { told, set: (patch) => told.push(['set', patch]), pushProgress: (ev) => told.push(['push', ev]) };
}

test('the compose handler set registers every compose event the server can put, revised included', () => {
  const keys = new Set(Object.keys(composeHandlers(recorder(), 'job-1')));
  for (const ev of serverEvents('compose')) assert.ok(keys.has(ev), `composeHandlers does not register '${ev}'`);
});

test('every compose call site hands jobEvents that one handler set, and no literal of its own', () => {
  const files = ['workbench/app/src/surfaces/CandidateSet.jsx', 'workbench/app/src/surfaces/BriefIntake.jsx'];
  const sites = files.flatMap(handlerArgs);
  // the denominator first: a pattern matching nothing would make every assertion below vacuous
  for (const f of files) assert.ok(sites.some((s) => s.file === f), `${f} has no jobEvents call to judge`);
  for (const s of sites) {
    // the argument IS the call, so nothing can be spread over it or written in beside it
    assert.match(s.arg, /^composeHandlers\(session,\s*[A-Za-z_.]+\s*[,)]/,
      `${s.file} hands jobEvents something other than composeHandlers(session, <job id>): ${s.arg.slice(0, 80)}`);
    assert.ok(s.arg.endsWith(')'), `${s.file}: the handler argument must be the call and nothing after it`);
  }
});

test("the Candidate Set's error handler writes jobError, with the job's own reason", () => {
  // the premise: the Candidate Set's handler is the factory's, with nothing of its own after it
  const cs = handlerArgs('workbench/app/src/surfaces/CandidateSet.jsx');
  assert.equal(cs.length, 1, 'the Candidate Set has one compose stream, its reattach');
  assert.match(cs[0].arg, /^composeHandlers\(session,\s*jobId\)$/);

  const store = recorder();
  composeHandlers(store, 'job-7').error({ error: 'the composer raised: no parti fits' });
  assert.deepEqual(store.told, [['set', { jobError: { state: 'failed',
    reason: 'the composer raised: no parti fits', jobId: 'job-7' } }]]);

  // the stream dropping is recorded too, in the words jobEvents gives it -- not swallowed
  const dropped = recorder();
  composeHandlers(dropped, 'job-7').error({ error: 'stream closed' });
  assert.equal(dropped.told[0][1].jobError.reason, 'stream closed');

  // and an event carrying no text is still a failure, its reason null rather than invented
  const bare = recorder();
  composeHandlers(bare, 'job-7').error(undefined);
  assert.deepEqual(bare.told, [['set', { jobError: { state: 'failed', reason: null, jobId: 'job-7' } }]]);
});

test('done clears a recorded failure; stage, candidate and revised reach the progress, revised marked', () => {
  const store = recorder();
  const h = composeHandlers(store, 'job-2');
  h.stage({ stage: 'partis' });
  h.candidate({ n: 1, parti: 'x' });
  h.revised({ n: 1, parti: 'x' });
  h.done({ candidates: [] });
  assert.deepEqual(store.told, [
    ['push', { stage: 'partis' }],
    ['push', { n: 1, parti: 'x' }],
    ['push', { n: 1, parti: 'x', revised: true }],
    ['set', { result: { candidates: [] }, jobError: null }],
  ]);
});

test("a site's own reaction runs AFTER the session is told, and cannot stand in for it", () => {
  const store = recorder();
  const order = [];
  const h = composeHandlers({ ...store, set: (p) => { order.push('session'); store.set(p); } }, 'job-3', {
    error: () => order.push('site'), done: () => order.push('site'),
  });
  h.error({ error: 'boom' });
  h.done({ candidates: [] });
  assert.deepEqual(order, ['session', 'site', 'session', 'site']);
  assert.equal(store.told[0][1].jobError.reason, 'boom');
});

/* The Candidate Set's reattach stream is CLOSED when the surface goes away (WP-14.10). Its handle
   used to be discarded -- `jobEvents(...)` called for its side effect -- so every visit to the
   Candidate Set during a compose opened an EventSource nothing could close, against a browser's
   six per origin; Brief Intake had learned that and closes its own. A React effect cannot be
   driven here, so this reads the one effect that opens the stream: the handle must be kept, and
   the cleanup the effect returns must release it. It is a reading of source and says so; the
   property it guards is structural to the effect, and nothing below React reaches it. */
test("the Candidate Set keeps its stream's handle and releases it when it goes away", () => {
  const src = read('workbench/app/src/surfaces/CandidateSet.jsx');
  const at = src.indexOf('jobEvents(');
  assert.ok(at > 0, 'the Candidate Set opens a compose stream');
  const effect = src.slice(src.lastIndexOf('React.useEffect(', at), src.indexOf('}, [s.jobId]);', at));
  const kept = effect.match(/\b(\w+) = jobEvents\(/);
  assert.ok(kept, 'the handle jobEvents returns is kept');
  assert.match(effect, new RegExp(`return \\(\\) => \\{[^}]*\\b${kept[1]}\\(\\)`),
    `the effect's cleanup calls ${kept[1]}(), closing the stream`);
});

test('the revise call site registers every revise event, round included', () => {
  const sites = callSites('workbench/app/src/surfaces/PlanWorkbench.jsx');
  assert.equal(sites.length, 1);
  for (const ev of serverEvents('revise')) assert.ok(sites[0].keys.has(ev), `PlanWorkbench does not register '${ev}'`);
});
