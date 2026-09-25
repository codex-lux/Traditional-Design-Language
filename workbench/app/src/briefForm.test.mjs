/* STEP ONE OF THE HOUSE JOURNEY, WHICH USED TO BREAK (WP-14.10, PRD §E, §F.4, §G.1).

   Brief Intake offered four budget tiers written into its JSX -- `entry`, `move-up`, `custom`,
   `estate` -- against a brief schema admitting `value`, `mid`, `custom`, `unlimited`. Three of
   the four a reader could pick were off the schema's list, and picking one refused the WHOLE
   brief at compose. The tiers are the schema's now, read through `journey/briefForm.js`, and this
   file holds both halves: the reader of the schema is driven on the schema itself, and the form's
   source is held to having no list of its own. The walk (`e2e/walk.mjs`) reads the rendered
   options against `GET /api/schema/brief`.

   And the form had a default style, `tidewater-georgian`, so a reader arriving with none was
   given one. PRD §F.4: the URL decides what is read, and memory only offers. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  BRIEF_DEFAULTS, briefFrom, budgetTiers, offSchemaTier, exampleId, briefReady,
} from './journey/briefForm.js';
import { journeyState } from './journey/journey.js';

const ROOT = new URL('../../../', import.meta.url);
const SCHEMA = JSON.parse(readFileSync(new URL('schema/brief.schema.json', ROOT), 'utf8'));
const ENUM = SCHEMA.properties.context.properties.budget_tier.enum;
// the words the form used to offer that the schema never admitted
const RETIRED = ['entry', 'move-up', 'estate'];

// Comments are not code. A tier named in a comment explaining this very defect is not an option.
const live = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8')
  .replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[\s;,{}()])\/\/[^\n]*/g, '$1');

test('the tiers are the schema\'s enum, in its order, read from the payload the server serves', () => {
  // the premise: the schema really does carry the enum this form must offer
  assert.ok(Array.isArray(ENUM) && ENUM.length > 0, 'brief.schema.json states budget_tier as an enum');
  // `GET /api/schema/brief` answers `{schema, examples, hint}` (core.brief_schema)
  assert.deepEqual(budgetTiers({ schema: SCHEMA, examples: [], hint: '' }), ENUM);
  for (const w of RETIRED) assert.ok(!ENUM.includes(w), `${w} is not a tier the schema admits`);
  // a payload with no such enum is said to have none -- never answered from a list of our own
  for (const p of [null, {}, { schema: {} }, { schema: { properties: { context: { properties: {} } } } },
    { schema: { properties: { context: { properties: { budget_tier: { enum: [] } } } } } }]) {
    assert.equal(budgetTiers(p), null, JSON.stringify(p));
  }
});

test('Brief Intake offers the schema\'s tiers and writes no tier of its own', () => {
  const src = live('./surfaces/BriefIntake.jsx');
  assert.match(src, /import \{[^}]*\bbudgetTiers\b[^}]*\} from '\.\.\/journey\/briefForm\.js'/);
  assert.match(src, /\(tiers \|\| \[\]\)\.map\(/, 'the options are mapped from the tiers the schema gave');
  // no tier, admitted or retired, written into the form as a string of its own
  for (const w of [...ENUM, ...RETIRED]) {
    assert.doesNotMatch(src, new RegExp(`['"\`]${w.replace('-', '\\-')}['"\`]`),
      `BriefIntake.jsx writes the tier '${w}' itself`);
  }
});

test('a tier an older draft carries that the schema does not admit is named, not dropped or hidden', () => {
  assert.equal(offSchemaTier(ENUM, 'entry'), 'entry');
  assert.equal(offSchemaTier(ENUM, ENUM[0]), null);
  assert.equal(offSchemaTier(ENUM, null), null);
  assert.equal(offSchemaTier(null, 'entry'), null, 'with the tiers unknown, nothing is judged off them');
});

test('the form gives a reader no style: it arrives from the address, the picker or the draft', () => {
  assert.equal(BRIEF_DEFAULTS.style, '');
  const src = live('./surfaces/BriefIntake.jsx');
  assert.doesNotMatch(src, /tidewater-georgian/, 'no style id written into the form');
  assert.match(src, /<StylePicker\b[^>]*value=\{brief\.style\}/, 'chosen with the StylePicker every surface uses');
  assert.doesNotMatch(src, /<select[^>]*value=\{brief\.style\}/, 'not a select of 164 ids');
  // `?style=` and `?example=` are read off the address, where the router keeps them
  assert.match(src, /place\.selection\.style/);
  assert.match(src, /place\.params\.example/);
  assert.match(src, /api\.exampleBrief\(urlExample\)/);
});

test('Compose is a real button, disabled until the brief states what its schema requires', () => {
  const src = live('./surfaces/BriefIntake.jsx');
  assert.match(src, /<button type="button" data-compose=""[^>]*onClick=\{compose\}[^>]*disabled=\{composing \|\| !ready\}/);
  assert.doesNotMatch(src, /<Chip\b[^>]*onClick=\{[^}]*compose\b/, 'not a Chip, which is a filter');
  assert.match(src, /const ready = briefReady\(brief\)/);
});

test('ready is the journey\'s own brief test, not a second spelling of it', () => {
  const stated = (b) => journeyState({ session: { brief: b } }).steps[0].state === 'stated';
  for (const b of [{}, { style: 'x' }, { target_area_sf: 3 }, { style: 'x', target_area_sf: 3 },
    { style: '  ', target_area_sf: 3 }, { style: 'x', target_area_sf: 0 }, { style: 'x', target_area_sf: '9' },
    BRIEF_DEFAULTS, null]) {
    assert.equal(briefReady(b), stated(b), JSON.stringify(b));
  }
  assert.equal(briefReady({ ...BRIEF_DEFAULTS, style: 'craftsman' }), true);
  assert.equal(briefReady(BRIEF_DEFAULTS), false, 'the defaults alone are not a brief');
});

test('a saved draft or a loaded example is laid over the defaults without crashing the form', () => {
  const b = briefFrom({ style: 'craftsman', context: 'garbage', must_have: 'library' });
  assert.equal(b.style, 'craftsman');
  assert.deepEqual(b.context, {});
  assert.deepEqual(b.must_have, []);
  assert.equal(b.target_area_sf, BRIEF_DEFAULTS.target_area_sf);
  const ex = briefFrom({ id: 'family-georgian', name: 'Family house', context: { budget_tier: 'custom' } });
  assert.deepEqual([ex.id, ex.name, ex.context.budget_tier, ex.style], ['family-georgian', 'Family house', 'custom', '']);
  // the defaults are not shared with the brief a reader then edits
  briefFrom(null).must_have.push('library');
  assert.deepEqual([...BRIEF_DEFAULTS.must_have], []);
});

test('a shipped example is addressed by the name the route takes', () => {
  assert.equal(exampleId('family-georgian.json'), 'family-georgian');
  assert.equal(exampleId('bungalow-small'), 'bungalow-small');
  assert.equal(exampleId('../briefs/family-georgian.json'), 'family-georgian');
  assert.equal(exampleId(''), null);
  assert.equal(exampleId(null), null);
});
