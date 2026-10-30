/* THE SIDEBAR'S SHAPE AND THE STATIONS' MARKS (Phase 17, WP-17.2).

   `nav/sidebar.js` decides which of the site map's places the sidebar draws, and
   `journey/spine.js` which journey mark each station carries. Both are pure, and the browser walk
   holds the rendered anchors to `drawnItems`, so what is held here is the decisions themselves. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { navModel } from './nav/navModel.js';
import { sidebarView, drawnItems } from './nav/sidebar.js';
import { barView } from './journey/bar.js';
import { journeyState } from './journey/journey.js';
import { stations, stationMark, STATION_MARKS } from './journey/spine.js';

const viewAt = (surface, { session = {}, plan = null } = {}) => {
  const place = { surface, selection: {} };
  const js = journeyState({ session, plan });
  const model = navModel({ lookup: null, counts: { styles: 164 }, place, journey: js });
  return sidebarView(model, { bar: barView(js, { surface }), resume: js.resume, surface });
};

test('the front door is the wordmark, the house comes first, and the library is five rows', () => {
  const v = viewAt('overview');
  assert.equal(v.home.id, 'overview');
  assert.deepEqual(v.house.items.map((i) => i.id), ['brief', 'candidates', 'workbench', 'drawings', 'export']);
  assert.deepEqual(v.library.rows.map((r) => r.id), ['style', 'proportions', 'faults', 'elements', 'glossary']);
  assert.equal(v.compact, false, 'the front door shows the whole spine');
});

test('Styles\' own places are its sub-rows only while the reader is among them', () => {
  assert.deepEqual(viewAt('overview').library.rows[0].children, []);
  const open = viewAt('phylogeny').library.rows[0].children.map((c) => c.id);
  assert.ok(open.includes('phylogeny'), 'the family tree is under Styles on its own page');
  for (const s of ['style', 'phylogeny', 'compare']) assert.equal(viewAt(s).stylesOpen, true, s);
  for (const s of ['faults', 'brief', 'glossary']) assert.equal(viewAt(s).stylesOpen, false, s);
});

test('a library page draws the house compact, and a house page draws it whole', () => {
  // every library page, not two of them (Phase 17's audit: style and proportions moved into the
  // house's set stayed green)
  for (const s of ['faults', 'glossary', 'proportions', 'elements', 'style', 'compare', 'phylogeny']) {
    assert.equal(viewAt(s).compact, true, s);
  }
  for (const s of ['brief', 'candidates', 'workbench', 'drawings', 'export', 'transcription']) {
    assert.equal(viewAt(s).compact, false, s);
  }
});

test('a blocked step is drawn as words and is not among the links; the open ones are', () => {
  const v = viewAt('overview');
  const ids = drawnItems(v).map((i) => i.id);
  // with no plan on the bench, the drawings and the export cannot be made: barView blocks both
  assert.ok(!ids.includes('drawings') && !ids.includes('export'), ids.join(','));
  assert.ok(ids.includes('brief') && ids.includes('workbench') && ids.includes('transcription'));
  assert.equal(ids[0], 'overview', 'the wordmark first');
  assert.ok(ids.indexOf('export') < 0 && ids.indexOf('style') > ids.indexOf('workbench'), 'house, then library');
});

test('a station is done by its own state, in hand where its surface is the page, and refused where the plan is', () => {
  const brief = { id: 'brief', state: 'stated', current: false };
  assert.equal(stationMark(brief), STATION_MARKS.done);
  assert.equal(stationMark({ ...brief, state: 'todo' }), STATION_MARKS.notYet);
  assert.equal(stationMark({ ...brief, current: true }), STATION_MARKS.current);
  assert.equal(stationMark({ id: 'plan', state: 'refused', current: true }), STATION_MARKS.refused,
    'a refused plan says so even where it is the page');
  assert.equal(stationMark({ id: 'drawings', state: 'ready' }), STATION_MARKS.notYet,
    'a drawing has no state that records its making, so it is never drawn done');
});

test('where no step is the page, the station in hand is the one the journey resumes at', () => {
  const items = [{ id: 'brief', state: 'stated' }, { id: 'candidates', state: 'ready' }, { id: 'plan', state: 'evaluated' }];
  const marks = stations({ items }, { id: 'plan' }).map((i) => i.mark);
  assert.deepEqual(marks, [STATION_MARKS.done, STATION_MARKS.done, STATION_MARKS.current]);
  // and a step that IS the page wins over the resume
  const here = stations({ items: [{ ...items[0], current: true }, items[1], items[2]] }, { id: 'plan' }).map((i) => i.mark);
  assert.deepEqual(here, [STATION_MARKS.current, STATION_MARKS.done, STATION_MARKS.done]);
});
