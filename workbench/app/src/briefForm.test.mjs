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
  BRIEF_DEFAULTS, briefFrom, budgetTiers, offSchemaTier, exampleId, briefReady, composeRequest,
  partiOptions, nativityOfParti,
} from './journey/briefForm.js';
import { journeyState } from './journey/journey.js';
import { formatHash, parseHash } from './router.js';

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

/* A BRIEF MAY NAME A PARTI, AND THE BRIEF THE FORM POSTS CARRIES IT (WP-14.25, PRD §C.5).

   The composer guarantees a named parti a place among the candidates; the guarantee reaches a
   reader only if the form's posted brief keeps the name. `composeRequest` is that brief -- lifted
   out of Brief Intake's JSX, where it was an inline expression nothing tested. The schema is read
   as the premise: `parti` is admitted, and its own pattern refuses an empty id, which is why an
   unstated parti must be ABSENT from the post rather than an empty string. */
const PARTI = 'centre-passage-double-pile';

test('the schema admits a parti, and refuses an empty one -- the premise of the two tests below', () => {
  assert.ok(SCHEMA.properties.parti, 'brief.schema.json 0.2.0 carries `parti`');
  const pattern = new RegExp(SCHEMA.properties.parti.pattern);
  assert.ok(pattern.test(PARTI));
  assert.ok(!pattern.test(''), 'an empty parti is not an id the schema admits');
  assert.equal(BRIEF_DEFAULTS.parti, '', 'the form names no parti by default: the composer chooses');
});

test('the brief the form posts keeps the parti the reader named', () => {
  const req = composeRequest({ ...BRIEF_DEFAULTS, style: 'tidewater-georgian', parti: PARTI });
  assert.equal(req.brief.parti, PARTI, 'the posted brief lost the parti the reader named');
  assert.equal(req.brief.style, 'tidewater-georgian');
  // a draft laid over the defaults keeps it too, as the session hands the form back its brief
  assert.equal(briefFrom({ style: 'x', parti: PARTI }).parti, PARTI);
});

test('an unstated parti is absent from the post, never an empty string the schema would refuse', () => {
  const req = composeRequest({ ...BRIEF_DEFAULTS, style: 'x' });
  assert.ok(!Object.prototype.hasOwnProperty.call(req.brief, 'parti'), JSON.stringify(req.brief));
  // and the other blanks the form has always dropped, dropped the same way
  const b = composeRequest({ ...BRIEF_DEFAULTS, style: 'x', household: '', bedrooms: null,
    must_have: [], context: {} }).brief;
  for (const k of ['household', 'bedrooms', 'must_have', 'context', 'name']) {
    assert.ok(!Object.prototype.hasOwnProperty.call(b, k), `${k} was posted blank`);
  }
  // an empty brief is posted as an empty brief, which the server refuses by name -- never thrown here
  assert.deepEqual(composeRequest({}).brief, {});
  assert.deepEqual(composeRequest(null).brief, {});
});

test('the candidate count travels beside the brief, and a count that is not one or more is left out', () => {
  const four = composeRequest({ ...BRIEF_DEFAULTS, style: 'x', candidates: 4 });
  assert.equal(four.candidates, 4);
  for (const bad of [0, '', null, -2, 'many']) {
    const r = composeRequest({ ...BRIEF_DEFAULTS, style: 'x', candidates: bad });
    assert.equal(r.candidates, null, `candidates ${JSON.stringify(bad)}`);
    assert.ok(!Object.prototype.hasOwnProperty.call(r.brief, 'candidates'), `candidates ${JSON.stringify(bad)} posted`);
  }
});

/* THE SELECT IS GROUPED BY THE NATIVITY THE SERVER STATED, AND BORROWED ONLY ON REQUEST. The
   payloads are `/api/partis`'s own shape since WP-14.19: `OWN` asked with a style, `WIDE` asked
   with `include_borrowed`, which returns every row, native and lineage included. */
const OWN = { count: 2, partis: [
  { id: PARTI, name: 'Centre-passage double pile', nativity: 'native' },
  { id: 'five-part-palladian', name: 'Five-part Palladian', nativity: 'lineage' },
] };
const WIDE = { count: 3, partis: [...OWN.partis,
  { id: 'octagon-radial', name: 'Octagon', nativity: 'borrowed' }] };

test("the select groups the style's partis by served nativity, each group worded by its record", () => {
  const o = partiOptions(OWN, null, '');
  assert.deepEqual(o.groups.map((g) => [g.nativity, g.termId, g.rows.map((r) => r.id)]), [
    ['native', 'parti-native', [PARTI]],
    ['lineage', 'parti-lineage', ['five-part-palladian']],
  ]);
  assert.equal(o.offList, null);
  // a lineage parti is under lineage and nowhere else -- the form used to call every row native
  assert.equal(nativityOfParti(o, 'five-part-palladian'), 'lineage');
  assert.equal(nativityOfParti(o, PARTI), 'native');
});

test('borrowed partis are offered only from the list asked for them, and never twice', () => {
  // without the borrowed list, a borrowed parti the brief names is shown as itself, not dropped
  const narrow = partiOptions(OWN, null, 'octagon-radial');
  assert.ok(!narrow.groups.some((g) => g.nativity === 'borrowed'));
  assert.equal(narrow.offList, 'octagon-radial', 'a named parti the list does not hold was dropped');
  assert.equal(nativityOfParti(narrow, 'octagon-radial'), null, 'no nativity is guessed for it');
  // with it, the borrowed rows join under their own word, and the native and lineage rows the wide
  // list repeats are not offered a second time
  const wide = partiOptions(OWN, WIDE, 'octagon-radial');
  assert.deepEqual(wide.groups.map((g) => g.nativity), ['native', 'lineage', 'borrowed']);
  assert.deepEqual(wide.groups.flatMap((g) => g.rows.map((r) => r.id)),
    [PARTI, 'five-part-palladian', 'octagon-radial']);
  assert.equal(wide.offList, null);
  // the borrowed list contributes ONLY what the server calls borrowed: a row it labels otherwise is
  // not promoted by arriving on the wider list
  const other = { partis: [{ id: 'x', name: 'X', nativity: 'native' }] };
  assert.equal(partiOptions(null, other, '').groups.length, 0);
});

test('Brief Intake reads the parti off the address, posts composeRequest, and keeps borrowed behind a choice', () => {
  const src = live('./surfaces/BriefIntake.jsx');
  assert.match(src, /place\.selection\.parti/, '`?parti=` seeds the brief');
  assert.match(src, /composeRequest\(brief\)/, "the posted brief is composeRequest's");
  assert.doesNotMatch(src, /JSON\.parse\(JSON\.stringify\(brief/, 'no second spelling of the posted brief');
  assert.match(src, /include_borrowed: true/, "borrowed partis are asked for with the route's own flag");
  assert.match(src, /usePartis\(includeBorrowed \? brief\.style : null, true\)/,
    'the borrowed list is asked for only where the reader included it');
  // the three readers WP-14.19 named read the served nativity now
  assert.doesNotMatch(src, /partis\?\.partis \|\| \[\]/, 'the whole list read as native');
  assert.doesNotMatch(src, /native to \$\{/, 'a count calling every listed parti native to the style');
  assert.doesNotMatch(src, /egyptian-revival|new-urbanist-traditional|tuscan-vernacular/,
    'the advisory naming three styles by hand, all three of which have plan types now');
  // loading is not a judgment
  assert.doesNotMatch(src, /reading the corpus/, 'the loading state is a JudgmentMark again');
  assert.match(src, /data-plan-types=[\s\S]{0,120}aria-busy=\{own\.state === 'loading'/);
});

test('a plan type on the dossier starts the brief that names it, at the address Brief Intake reads', () => {
  /* WP-14.25. The link is written by the router's own writer and read back by its own reader, so
     the parti arrives in `place.selection.parti`, which is what the form seeds from. Its word is a
     glossary record's, which must exist; the dossier section writes no word of its own. */
  const href = formatHash('brief', { style: 'tidewater-georgian', parti: 'centre-passage-double-pile' });
  const back = parseHash(href);
  assert.equal(back.surface, 'brief');
  assert.deepEqual(back.selection, { style: 'tidewater-georgian', parti: 'centre-passage-double-pile' });
  const src = live('./dossier/PlanTypes.jsx');
  assert.match(src, /formatHash\('brief', \{ style: styleId, parti: partiId \}\)/);
  assert.match(src, /<StartBrief styleId=\{dossier\.id\} partiId=\{p\.id\} \/>/);
  assert.match(src, /START_BRIEF_TERM = 'start-a-brief-from-a-plan-type'/);
  const rec = JSON.parse(readFileSync(new URL('glossary/start-a-brief-from-a-plan-type.json', ROOT), 'utf8'));
  assert.equal(rec.id, 'start-a-brief-from-a-plan-type');
  assert.equal(rec.kind, 'editorial');
  // the row's nativity is the served one, worded by its own record, and never decided here
  assert.match(src, /NATIVITY_TERMS\[p\.nativity\]/);
  assert.doesNotMatch(src, /start a brief/i, 'the link word is written in the app rather than read from its record');
});
