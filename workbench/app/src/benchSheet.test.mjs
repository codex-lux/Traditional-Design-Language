/* The bench plate, held to what it is served (WP-14.6's second audit).

   An independent audit measured the bench against `mcp_server/core.py::placement_summary` on all
   sixteen shipped plans and found the plate drawing less than it was served, or more than was there:

   - E1: the terrace door named undrawable on good-02 and good-04, over the hole the plate cut for
     it -- the placement never served `appendages`, which the sheet has read since WP-11.10;
   - E2: the tagged Tidewater's UPPER plate laid floor over a wing and a hyphen with no upper storey;
   - E3: the furniture key cleared the 4.5 in derived partitions while the plate drew the SERVED
     bands, so 11 of the 146 keys fitted over the sixteen plans stood on a drawn wall body, all
     eleven on the Tidewater plan;
   - E4: WP-14.6 deleted the caption's bay-module sentence instead of printing the served one, so on
     15 of 16 plans the plate drew a 10 ft grid with nothing on it saying the module is a default;
   - E5: no chimney breast drawn at all, under a strip saying one of three fires was not drawn.

   Everything the plate draws for these is computed in `sheet/derive.js` and `sheet/marks.js` now and
   the JSX copies it, so each is held here by what those leaves return, on the shapes of the records
   the audit measured; and the last block holds the JSX to drawing what they return and nothing of its
   own. It cannot render the JSX -- this suite runs with no `node_modules` -- so that half reads the
   source, and says so. The pure-leaf half is the one a reader should trust first. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import { appendageRects, doors, drawnBreasts, elementBounds, keyObstacles, levelAppendages,
         levelBlocks, massingBlocks, plateNote, refusedBreasts, servedLine, wallOf, windows } from './sheet/derive.js';
import { furnitureKeyPlan } from './sheet/furnitureKey.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..', '..');

/* ------------------------------------------------------------------ the records the audit measured */

// tidewater-georgian-careful's three massing elements as placed on the search (the census's engine):
// the main block, the service hyphen, the west dependency
const TIDEWATER_BLOCKS = [
  { id: 'main', x_ft: 0, y_ft: 0, width_ft: 45, depth_ft: 37.24 },
  { id: 'service-hyphen', x_ft: -7, y_ft: 9.62, width_ft: 7, depth_ft: 18 },
  { id: 'service', x_ft: -34, y_ft: 5.28, width_ft: 27, depth_ft: 26.68 },
];
const room = (id, x, y, w, h, extra = {}) => ({ id, name: id, x, y, w, h, windows: [], doors: [],
  exterior_walls: [], fixture_layout: [], furniture_layout: [], ...extra });
const GROUND = [room('passage', 17.5, 0, 10, 37.24), room('backhall', -7, 9.62, 7, 18),
  room('kitchen', -34, 5.28, 20, 26.68), room('breakfast', -14, 5.28, 7, 26.68)];
const UPPER = [room('landing', 17.5, 20, 10, 17.24), room('primary', 0, 0, 17.5, 20)];

/* ------------------------------------------------------------------ E1: the appendages */

test('E1: a level\'s appendages are the placed ones on that level, in the form the door lookup reads', () => {
  const placement = { appendages: { placed: [
    { room: 'terrace', level: 0, wall: 'W', rect: { x_ft: -10, y_ft: 11.96, width_ft: 10, depth_ft: 24 } },
    { room: 'deck', level: 1, wall: 'N', rect: { x_ft: 0, y_ft: 40, width_ft: 8, depth_ft: 6 } }] } };
  assert.deepEqual(levelAppendages(placement, 0).map((a) => a.room), ['terrace'],
    'the ground plate takes the ground-floor terrace and not the upper deck');
  assert.deepEqual(appendageRects(levelAppendages(placement, 0)), [{ id: 'terrace', x: -10, y: 11.96, w: 10, h: 24 }]);
  assert.deepEqual(levelAppendages({}, 0), [], 'a placement serving none gives none, not an error');
  // good-02: the family room's door onto the terrace, as the record seats it
  const family = room('family', 0, 20, 16, 16, { exterior_walls: ['W'],
    doors: [{ to: 'terrace', width_ft: 6, type: 'double', wall: 'W', position_ft: 27.98 }] });
  const without = doors([family], 50, 40, 0.6, appendageRects(levelAppendages({}, 0)));
  assert.deepEqual(without.undrawable.map((u) => u.reason), ['the other room is not placed on this level'],
    'the premise: with nothing served the bench names the seated door undrawable, which is the defect');
  const withIt = doors([family], 50, 40, 0.6, appendageRects(levelAppendages(placement, 0)));
  assert.equal(withIt.undrawable.length, 0);
  assert.equal(withIt.interior.length, 1);
  assert.equal(withIt.interior[0].exteriorWall, 'W', 'and it stands in the exterior wall, not a partition');
});

/* ------------------------------------------------------------------ E2: the floor on each level */

test('E2: a level\'s floor is drawn for the elements holding its rooms, as render_plan._blocks_here draws its walls', () => {
  const fp = { width_ft: 45, depth_ft: 37.24, blocks: TIDEWATER_BLOCKS };
  const blocks = massingBlocks(fp, 45, 37.24);
  assert.equal(blocks.length, 3);
  const ids = (list) => list.map((b) => TIDEWATER_BLOCKS.find((t) => t.x_ft === b.x && t.y_ft === b.y).id);
  assert.deepEqual(ids(levelBlocks(blocks, GROUND, elementBounds(GROUND, fp))), ['main', 'service-hyphen', 'service']);
  assert.deepEqual(ids(levelBlocks(blocks, UPPER, elementBounds(UPPER, fp))), ['main'],
    'the upper plate draws floor for the main block alone: the wing and the hyphen have no upper storey');
  // several rooms in one element give that element once
  assert.equal(levelBlocks(blocks, [...UPPER, room('cl', 30, 0, 5, 5)], elementBounds([...UPPER, room('cl', 30, 0, 5, 5)], fp)).length, 1);
});

test('E2: one element is drawn whatever its rooms; a level with rooms none of which resolves draws them all; a level with none draws nothing', () => {
  const one = massingBlocks({ width_ft: 40, depth_ft: 30 }, 40, 30);
  assert.deepEqual(one, [{ x: 0, y: 0, w: 40, h: 30 }], 'a record stating no blocks is its footprint');
  assert.deepEqual(levelBlocks(one, [room('a', 0, 0, 10, 10)], {}), one);
  const three = massingBlocks({ blocks: TIDEWATER_BLOCKS }, 45, 37.24);
  const stray = [room('stray', 100, 100, 5, 5)];
  assert.deepEqual(levelBlocks(three, stray, elementBounds(stray, { blocks: TIDEWATER_BLOCKS })), three,
    'rooms in no element: every element, the direction `_blocks_here` keeps its `or blocks` for');
  assert.deepEqual(levelBlocks(one, [], {}), [], 'a level nothing placed (bad-03\'s third storey) has no floor');
  assert.deepEqual(levelBlocks(three, [], {}), []);
});

/* ------------------------------------------------------------------ E3 and E5: the key */

const KEYED = room('library', 0, 0, 14, 12, { furniture_layout: [
  { item: 'writing table', x_ft: 9, y_ft: 8, width_ft: 4, depth_ft: 3, marks: [{ rect: [9, 8, 4, 3] }] }] });
const NO_DOORS = { interior: [], exterior: [] };
const overlaps = (a, b) => Math.min(a[2], b[2]) - Math.max(a[0], b[0]) > 1e-6 && Math.min(a[3], b[3]) - Math.max(a[1], b[1]) > 1e-6;
function keyBox(opts) {
  const kp = furnitureKeyPlan([KEYED], opts).byRoom.get('library');
  assert.ok(kp && kp.fit, 'the premise: the room keys its item in a corner');
  const f = kp.fit;
  return [KEYED.x + f.x0, KEYED.y + KEYED.h - f.y1, KEYED.x + f.x1, KEYED.y + KEYED.h - f.y0];
}

test('E3: the key clears the wall bodies the plate DRAWS -- the served bands -- and not only the derived partitions', () => {
  // an 11 in bearing band on the library's west wall, as the plate serves a masonry bearing line,
  // against the 4.5 in partition `derive.partitions` would put there
  const band = { wall: 'bearing', kind: 'masonry', x_ft: -0.4583, y_ft: 0, width_ft: 0.9167, depth_ft: 12 };
  const served = { level: 0, bands: [band] };
  const parts = [{ x: -0.1875, y: 0, w: 0.375, h: 12 }];
  const drawn = [band.x_ft, band.y_ft, band.x_ft + band.width_ft, band.y_ft + band.depth_ft];
  const inputs = keyObstacles({ drs: NO_DOORS, served, parts, stair: null, levelIndex: 0, breasts: [] });
  assert.deepEqual(inputs.partitions, [{ x: -0.4583, y: 0, w: 0.9167, h: 12 }], 'the served band is the key\'s wall');
  assert.ok(!overlaps(keyBox(inputs), drawn), `the key ${keyBox(inputs)} stands on the drawn band ${drawn}`);
  // the control, which is the defect: the derived partition alone, and the key stands on the band
  const old = keyObstacles({ drs: NO_DOORS, served: null, parts, stair: null, levelIndex: 0, breasts: [] });
  assert.deepEqual(old.partitions, parts, 'with no walls served the derived partitions stand');
  assert.ok(overlaps(keyBox(old), drawn), 'the premise: on the derived partition alone this key stands on the band');
});

test('E5: the key keeps clear of a drawn chimney breast, as the Python key does', () => {
  // a breast on the library's west wall, standing where the key would take its corner
  const breast = { level: 0, room: 'library', index: 0, wall: 'W', drawn: true, x_ft: 0, y_ft: 7, width_ft: 1.8, depth_ft: 4.75 };
  const box = [0, 7, 1.8, 11.75];
  const inputs = keyObstacles({ drs: NO_DOORS, served: null, parts: [], stair: null, levelIndex: 0, breasts: [breast] });
  assert.ok(inputs.stairRects.some((s) => s.x === 0 && s.y === 7 && s.w === 1.8 && s.h === 4.75), 'the breast is an obstacle');
  assert.ok(!overlaps(keyBox(inputs), box), 'the key stands on the breast');
  const blind = keyObstacles({ drs: NO_DOORS, served: null, parts: [], stair: null, levelIndex: 0, breasts: [] });
  assert.ok(overlaps(keyBox(blind), box), 'the premise: a key that knows no breast takes that corner');
});

test('E3: the swing squares are the leaves as drawn, lifted out of the JSX unchanged', () => {
  const drs = {
    interior: [{ x: 10, y: 5, w: 3, horiz: true, swingUp: true }, { x: 4, y: 8, w: 2.5, horiz: false, swingRight: false }],
    exterior: [{ wall: 'S', x: 20, y: 0, w: 3.5 }, { wall: 'E', x: 40, y: 12, w: 3 }],
  };
  const { swings } = keyObstacles({ drs, served: null, parts: [], stair: null, levelIndex: 0, breasts: [] });
  assert.deepEqual(swings, [
    { x: 8.5, y: 5, w: 3, h: 3 }, { x: 1.5, y: 6.75, w: 2.5, h: 2.5 },
    { x: 18.25, y: 0, w: 3.5, h: 3.5 }, { x: 37, y: 10.5, w: 3, h: 3 }]);
});

/* ------------------------------------------------------------------ E5: the breasts */

const HEARTHS = { breasts: [
  { level: 0, room: 'drawing', index: 0, wall: 'W', drawn: false, x_ft: 7, y_ft: 16.17, width_ft: 1.911, depth_ft: 4.9 },
  { level: 0, room: 'dining', index: 0, wall: 'W', drawn: true, x_ft: 0, y_ft: 28.551, width_ft: 1.807, depth_ft: 4.758 },
  { level: 0, room: 'library', index: 0, wall: 'E', drawn: true, x_ft: 43.269, y_ft: 28.605, width_ft: 1.731, depth_ft: 4.65 },
  { level: 1, room: 'chamber', index: 0, wall: 'E', drawn: true, x_ft: 43, y_ft: 2, width_ft: 1.7, depth_ft: 4.6 },
  // a row with a rectangle and NO verdict. Its first version carried no rectangle, so the coordinate
  // filter refused it and a `drawn !== false` reading stayed green -- found by mutation
  { level: 0, room: 'parlor', index: 0, wall: 'S', x_ft: 20, y_ft: 0, width_ft: 4.6, depth_ft: 1.7 }] };

test('E5: the plate draws the breasts the placement\'s verdict lets it draw, on their own level, and no other', () => {
  // a row with no verdict is unjudged and is not drawn: it is the plate's own unjudged branch, not copied
  const unjudged = HEARTHS.breasts.find((b) => b.room === 'parlor');
  assert.ok(!('drawn' in unjudged) && unjudged.x_ft != null && unjudged.width_ft > 0,
    'the premise: the unjudged row has a rectangle, so only its missing verdict can keep it off the plate');
  assert.ok(!drawnBreasts({ hearths: HEARTHS }, 0).some((b) => b.room === 'parlor'),
    'a breast with no verdict is drawn as though the placement had judged it');
  assert.deepEqual(drawnBreasts({ hearths: HEARTHS }, 0).map((b) => b.room), ['dining', 'library'],
    'the Tidewater ground floor: two of three stated fires drawn, the drawing room\'s refused');
  assert.deepEqual(drawnBreasts({ hearths: HEARTHS }, 1).map((b) => b.room), ['chamber'],
    'the upper plate draws the upper chamber\'s breast and none of the ground floor\'s');
  assert.deepEqual(refusedBreasts({ hearths: HEARTHS }, 0).map((b) => b.room), ['drawing']);
  assert.deepEqual(drawnBreasts({}, 0), []);
});

/* ------------------------------------------------------------------ E4 and the note */

const BAY_LINE = "BAY GRID AT THE PLACER'S DEFAULT 10 FT — NO PARTI STATES A MODULE, AND THE BEARING WALLS ARE READ OFF IT";
const FIRES_LINE = '1 OF 3 STATED FIRE(S) NOT DRAWN — DRAWING: NO EXTERIOR WALL CARRIES THE FLUE ON THIS PLACEMENT';

function note(over = {}) {
  const fp = over.footprint || { width_ft: 50, depth_ft: 30.75, bay_module_ft: 10 };
  const wins = Object.assign([], { offFootprint: 0, crowded: 0, refused: 0 }, over.wins || {});
  return plateNote({
    wall: wallOf(fp), footprint: fp, placement: over.placement || {}, levelIndex: over.levelIndex ?? 0,
    rooms: over.rooms || [room('a', 0, 0, 10, 10)], served: 'served' in over ? over.served : { bands: [] },
    relax: null, rxMarks: { drawn: [], unlocated: [] }, spanCap: over.spanCap ?? null,
    drs: { undrawable: [], inferredWidths: 0, inferredPositions: 0 }, wins, diverged: [],
    keyMargin: over.keyMargin || [], bays: 'bays' in over ? over.bays : [10, 20, 30, 40],
  });
}
const text = (lines) => lines.map((l) => l.text).join('');

test('E4: the plate prints whose bay module the grid is, in the words the server serves', () => {
  const placement = { disclosures: [{ id: 'relaxations', text: '8 CUT(S)' }, { id: 'bay-module', tone: 'copper', text: BAY_LINE }] };
  const lines = note({ placement });
  const bay = lines.find((l) => l.id === 'bay-module');
  assert.ok(bay, 'the caption says nothing of a grid it draws at the placer\'s default');
  assert.equal(bay.text, `${BAY_LINE}. `, 'the served line, verbatim: not composed a second time');
  assert.ok(text(lines).includes(BAY_LINE));
  // and where no line is served -- a parti states the module -- the plate composes none of its own
  const own = note({ placement: { disclosures: [] } });
  assert.ok(!own.some((l) => l.id === 'bay-module'));
  assert.ok(!/default|placer/i.test(text(own)), 'the plate spelled the bay-module line itself');
  assert.equal(servedLine(placement, 'bay-module'), BAY_LINE);
  assert.equal(servedLine({}, 'bay-module'), null);
});

test('E4: the ids the plate reads are the ids build/disclosures.py writes', () => {
  // a join between two files in two languages that nothing else holds: rename either side and the
  // plate prints nothing, green
  const py = readFileSync(join(ROOT, 'build', 'disclosures.py'), 'utf8');
  for (const id of ['bay-module', 'fires']) {
    assert.match(py, new RegExp(`"id":\\s*"${id}"`), `build/disclosures.py writes no "${id}" line`);
  }
});

test('E5: a stated fire the placement refused is said on the plate of its own level, in the served words', () => {
  const placement = { hearths: HEARTHS, disclosures: [{ id: 'fires', text: FIRES_LINE }] };
  const fires = note({ placement }).find((l) => l.id === 'fires');
  assert.ok(fires, 'the plate says nothing of a stated fire the placement refused');
  assert.equal(fires.text, `${FIRES_LINE}. `);
  assert.ok(!note({ placement, levelIndex: 1 }).some((l) => l.id === 'fires'), 'no fire is refused upstairs');
  // a server that spells no line is not a reason to fall silent
  const bare = note({ placement: { hearths: HEARTHS } }).find((l) => l.id === 'fires');
  assert.ok(bare && /1 stated fire\(s\) on this level refused/.test(bare.text), bare && bare.text);
});

test('the plate says a level is not placed rather than that the server sent nothing', () => {
  // bad-03's third storey: declared, placed by neither engine, and chosen from the level chips
  const ml = { levels_placed: [0, 1], levels_not_placed: [2], note: 'COULD NOT EVALUATE: this record declares a level the placer does not place.' };
  const placement = { walls: [{ level: 0, bands: [] }, { level: 1, bands: [] }], geometry_report: { multi_level: ml } };
  const lines = note({ placement, levelIndex: 2, rooms: [], served: null });
  const unplaced = lines.find((l) => l.id === 'level-not-placed');
  assert.ok(unplaced, `the plate does not say the level is unplaced: ${text(lines)}`);
  assert.equal(unplaced.text, `${ml.note} `);
  assert.ok(!/server sent no wall bodies/.test(text(lines)), 'the server sent wall bodies for every level it placed');
  // a placed level whose walls the server left out is said to be that, not "this placement"
  const placed = note({ placement, levelIndex: 3, served: null });
  assert.match(text(placed), /sent no wall bodies for this level/);
  // an older server that sends no walls at all keeps the sentence it always had
  assert.match(text(note({ placement: {}, served: null })), /sent no wall bodies with this placement/);
});

test('the plate counts the windows the placement refused to seat', () => {
  const refused = note({ wins: { refused: 2 } }).find((l) => l.id === 'windows-refused');
  assert.ok(refused, 'the plate says nothing of two windows the placement refused to seat');
  assert.equal(refused.text, '2 declared window(s) the placement refused to seat — declared, not drawn. ');
  assert.ok(!note().some((l) => l.id === 'windows-refused'), 'and says nothing where none was refused');
});

/* A PARTIAL REFUSAL IS THE PLACER'S, AND ITS REASON IS THE RECORD'S (WP-16.8, the audit of Phase 16,
   auditor C). Since WP-16.6 the placer refuses a unit for the pier floor (R5) or the axis below (R6)
   as well as for want of run; the bench counted every partly seated window as "crowded" and printed
   "had no clear run left on their wall" over 18 units on 10 of the 16 shipped plans, 17 of them
   refused for a ruled reason. Driven: one window of two units, one seated, refused under rule `pier`. */
test('a partly seated window refused for the pier floor is not called crowded, and the reason is the served one', () => {
  const room = { id: 'living', x: 0, y: 0, w: 20, h: 14, exterior_walls: ['S'],
                 windows: [{ wall: 'S', count: 2, width_ft: 3, positions_ft: [6.0],
                             unplaced: { rule: 'pier', reason: '1 of 2 unit(s) would leave a wall below 1 x the wider window beside the window next to it' } }] };
  const got = windows([room], 20, 14);
  assert.equal(got.crowded, 0, 'a ruled refusal counted as no run left on the wall');
  assert.equal(got.refused, 1);
  // the control: the same unit missing from a window the placer did not refuse is this file's own
  // inference on a declared record, and keeps the crowded count
  const declared = windows([{ ...room, windows: [{ wall: 'S', count: 2, width_ft: 3, positions_ft: [6.0] }] }], 20, 14);
  assert.equal(declared.crowded, 1);
  const served = '3 OF 35 DECLARED WINDOW UNIT(S) NOT DRAWN — 3 TOO NEAR THE NEXT WINDOW FOR A WALL OF 1 × THE WIDER';
  const lines = note({ wins: got, placement: { disclosures: [{ id: 'windows', text: served }] } });
  const said = lines.find((l) => l.id === 'windows-refused');
  assert.ok(said && /^1 declared window\(s\) the placement refused/.test(said.text), `the refusal was not counted: ${text(lines)}`);
  assert.ok(!/no clear run left/.test(text(lines)), 'the pier refusal was called a full wall');
});

/* EACH PLATE COUNTS ITS OWN LEVEL, AND THE COUNTS ARE DISJOINT (the audit of WP-16.8's own diff, 3 Oct
   2026, auditor B). WP-16.8 printed the server's plan-wide window sentence on every plate that refused a
   unit, so a two-storey house said the whole figure twice and a plate counted its off-footprint units
   twice: once in its own line and again in the served sentence's "ON NO SUCH WALL" bucket -- bad-02's one
   plate read 3 + 4 missing of 6 declared. Driven: two plates, a plan-wide sentence served, and each plate
   says its own counts, never the house's sentence, and the counts sum to the house's. */
test('each plate counts its own level\'s refused windows and never prints the house\'s sentence', () => {
  const served = '4 OF 9 DECLARED WINDOW UNIT(S) NOT DRAWN — 1 ON NO SUCH WALL, 3 TOO NEAR THE NEXT WINDOW';
  const placement = { disclosures: [{ id: 'windows', text: served }] };
  const ground = note({ wins: { offFootprint: 1, crowded: 0, refused: 2 }, placement });
  const upper = note({ wins: { offFootprint: 0, crowded: 0, refused: 1 }, placement, levelIndex: 1 });
  for (const [lines, off, ref] of [[ground, 1, 2], [upper, 0, 1]]) {
    assert.ok(!text(lines).includes('NOT DRAWN —'), `a plate printed the house's sentence: ${text(lines)}`);
    const r = lines.find((l) => l.id === 'windows-refused');
    assert.ok(r && r.text.startsWith(`${ref} declared window(s) the placement refused`), text(lines));
    const o = lines.find((l) => l.id === 'windows-off-footprint');
    assert.equal(Boolean(o), off > 0, text(lines));
  }
});

test('"the grid remains" is said only where a grid is drawn', () => {
  assert.ok(note().some((l) => l.id === 'grid'));
  const none = note({ footprint: { width_ft: 50, depth_ft: 30 }, bays: [] });
  assert.ok(none.some((l) => l.id === 'no-bay-module'), 'the premise: no module, no grid, and the plate says so');
  assert.ok(!none.some((l) => l.id === 'grid'), 'beside "no bay grid is drawn" it was a sentence about nothing');
});

/* The span line moved into plateNote with the rest, and tests/test_span_findings.py holds the Python
   plate's printed sentence; this holds the bench's three states (WP-11.12, OQ 98's reporting half):
   a count is a FLOOR and says so, the zero says so too, and a catalogue that could not be read is
   unjudged rather than clear. */
test('the span count is said as a floor, the zero as well, and an unread catalogue as unjudged', () => {
  const span = (spanCap) => note({ spanCap }).find((l) => l.id === 'span');
  const over = span({ over_capacity: 4, worst_span_ft: 45 });
  assert.ok(over, 'the plate says nothing of four spans over capacity');
  assert.match(over.text, /^4 clear span\(s\) over the framing capacity, worst 45 ft — at least that many/);
  assert.match(over.text, /however short the wall runs/, 'the count is printed without the understatement');
  const zero = span({ over_capacity: 0, worst_span_ft: 18 });
  assert.ok(zero && /^0 clear span\(s\).*at least none found/.test(zero.text), 'the zero is a claim the understatement can make falsely');
  const unread = span({ over_capacity: null });
  assert.ok(unread && /^Clear span not evaluated/.test(unread.text), 'an unread catalogue reads as a clear house');
  assert.equal(span(null), undefined, 'no span record, no span line');
});

test('a furniture key refused to the margin keeps its room on the note', () => {
  const lines = note({ keyMargin: [{ id: 'cl3', name: 'CLOSET', lines: ['1 HANGING ROD, SINGLE, WITH SHELF OVER'] }] });
  const m = lines.find((l) => l.id === 'key-margin');
  assert.equal(m.room, 'cl3');
  assert.equal(m.text, 'Furniture key, CLOSET — no corner of the room holds it: 1 HANGING ROD, SINGLE, WITH SHELF OVER. ');
});

/* ------------------------------------------------------------------ the JSX draws what the leaves return

   These read SOURCE, because this suite cannot render JSX, and each says what it holds. A rewording of
   the JSX may need them re-cut; what they exist to catch is the plate computing a second answer of its
   own beside the leaf's, which a behavioural test of the leaf cannot see. */

function stripComments(src) {
  let out = '', i = 0;
  const n = src.length;
  while (i < n) {
    if (src.startsWith('/*', i)) { const j = src.indexOf('*/', i + 2); i = j < 0 ? n : j + 2; }
    else if (src.startsWith('//', i) && src[i - 1] !== ':') { const j = src.indexOf('\n', i); i = j < 0 ? n : j; }
    else { out += src[i]; i += 1; }
  }
  return out;
}
const live = (rel) => stripComments(readFileSync(join(HERE, rel), 'utf8'));

test('the plate takes its appendages, floors, breasts and key from the leaves', () => {
  const src = live('sheet/Sheet.jsx');
  assert.ok(src.length > 20000, 'the premise: this is reading the sheet');
  assert.match(src, /const appendages = levelAppendages\(placement, levelIndex\)/, 'E1: the served appendages');
  assert.match(src, /doors\(rooms, W, H, 0\.6, appendageRects\(appendages\), elBounds\)/, 'E1: handed to the door lookup');
  assert.match(src, /const floors = levelBlocks\(blocks, rooms, elBounds\)/, 'E2: this level\'s floors');
  assert.match(src, /\{floors\.map\(\(b, i\) => \(\s*<rect key=\{'fl' \+ i\} data-floor/, 'E2: the floor fields are those');
  assert.doesNotMatch(src, /\{blocks\.map\(\(b, i\) => \(\s*<rect key=\{'fl'/, 'E2: a floor for every element on every level again');
  assert.match(src, /const breasts = drawnBreasts\(placement, levelIndex\)/, 'E5: the breasts the verdict allows');
  const drawsBreasts = src.indexOf('{breasts.map((b) => {');
  assert.ok(drawsBreasts > 0, 'E5: the plate draws no breast');
  const block = src.slice(drawsBreasts, drawsBreasts + 1600);
  assert.match(block, /style=\{POCHE\.masonry\}/, 'E5: a breast is brick, drawn in the masonry poche');
  assert.match(block, /breastOpening\(b, /, 'E5: with its opening, from marks.breastOpening');
  // at the CALL: the first version of this line matched `keyPlanFor`'s own parameter list, so a call
  // handing it `null` for the bands stayed green -- found by mutation, not by reading
  assert.match(src, /const keyPlan = keyPlanFor\(rooms, wall, drs, parts, stair, levelIndex, served, breasts\)/,
    'E3/E5: the key is handed the served bands and the breasts');
  assert.match(src, /return furnitureKeyPlan\(rooms, \{\s*\.\.\.keyObstacles\(\{ drs, served, parts, stair, levelIndex, breasts \}\),/,
    'E3/E5: and takes them from keyObstacles');
  assert.match(src, /\)\) : rooms\.length > 0 && \(\s*<g data-walls="derived">/, 'no wall ring on a level nothing placed');
});

test('every door the plate draws is drawn from the descriptors and leaves marks.js computes', () => {
  const src = live('sheet/Sheet.jsx');
  assert.match(src, /<DoorMark key=\{'ed' \+ i\} d=\{exteriorDoorMark\(d, wall\.exterior_ft\)\} \/>/);
  assert.match(src, /<DoorMark key=\{'d' \+ i\} d=\{interiorDoorMark\(d, wall\.exterior_ft\)\} \/>/);
  assert.match(src, /<Leaf s=\{leafOf\(d\)\} \/>/, 'the single leaf is marks.leafOf\'s');
  assert.match(src, /const \[a, b\] = pairOf\(d\);/, 'the pair is marks.pairOf\'s');
  assert.match(src, /A \$\{s\.len\} \$\{s\.len\} 0 0 \$\{s\.sweep\} \$\{s\.far\[0\]\} \$\{s\.far\[1\]\}/,
    'the arc is drawn with the leaf\'s own radius, sweep and far jamb');
  assert.doesNotMatch(src, /sweepFlag\(/, 'the plate derives a sweep of its own');
  const bench = readFileSync(join(ROOT, 'tests', 'js', 'bench_marks.mjs'), 'utf8');
  assert.match(bench, /doors\(rooms, W, H, 0\.6, appendageRects\(levelAppendages\(c\.placement, c\.level\)\), el\)/,
    'the census reads the bench with the appendages the sheet passes');
  assert.match(bench, /exteriorDoorMark\(d, wall\.exterior_ft\)/, 'and draws its doors from the sheet\'s descriptor');
});

test('the plate note says what plateNote says, after the sketch and the engine, and nothing of its own', () => {
  const src = live('sheet/Sheet.jsx');
  const open = src.indexOf('<div data-plate-note=""');
  assert.ok(open > 0, 'the premise: the plate publishes its note');
  const body = src.slice(src.indexOf('>', open) + 1, src.indexOf('</div>', open));
  // the note's children, at the top level: expressions only, and exactly these three
  const groups = [];
  let depth = 0, start = -1;
  for (let i = 0; i < body.length; i += 1) {
    const c = body[i];
    if (c === '{') { if (depth === 0) start = i; depth += 1; }
    else if (c === '}') {
      depth -= 1;
      // a JSX comment `{/* ... */}` is left as `{}` once its comment is stripped: it says nothing
      if (depth === 0 && body.slice(start + 1, i).trim()) groups.push(body.slice(start, i + 1));
    } else if (depth === 0 && !/\s/.test(c)) assert.fail(`the note prints text of its own: "${body.slice(i, i + 60)}"`);
  }
  assert.equal(groups.length, 3, `the note has ${groups.length} parts: ${groups.map((g) => g.slice(0, 30)).join(' | ')}`);
  assert.match(groups[0], /^\{sketch\b/);
  assert.equal(groups[1], '{engineLine}');
  assert.match(groups[2], /^\{note\.map\(/);
  assert.match(groups[2], />\{n\.text\}<\/span>/, 'each line is its text and nothing else');
  assert.match(src, /const note = plateNote\(\{/, 'and the lines are plateNote\'s');
});

test('the stair\'s arrow and riser count are lettering and do not take the room\'s click', () => {
  const src = live('sheet/Sheet.jsx');
  assert.match(src, /<g data-stair-arrow=\{[^}]*\} pointerEvents="none">/, 'the arrow eats the click meant for the stair hall');
  assert.match(src, /<text[^>]*pointerEvents="none"[^>]*>\s*UP \{stair\.risers\}R/, 'the riser count eats it too');
});
