/* The URL and the citation grammar are one addressing scheme written two ways. This
   pins that: every citation kind survives a round trip through a URL, and every URL
   parses back to the place it names.

   Pure functions, no DOM, no server:  node e2e/router-unit.mjs

   The modules are ESM with no JSX, so node runs them directly. Nothing here may import
   a .jsx file — if a future edit makes router.js or citations.js pull in a component,
   this test stops running and that is the point at which to split the module, not to
   delete the test. */

import assert from 'node:assert/strict';
import { parseCite, routeCite, citeFor } from '../src/citations.js';
import { parseHash, formatHash, SURFACE_PATHS, SELECTION_KEYS, DEFAULT_SURFACE } from '../src/router.js';

let checks = 0;
const ok = (fn) => { fn(); checks += 1; };

/* ── 1. The grammar itself ─────────────────────────────────────────────────────── */

ok(() => {
  assert.deepEqual(parseCite('style:craftsman'), { kind: 'style', id: 'craftsman', fragment: null });
  assert.deepEqual(parseCite('kit:tidewater-georgian#door_main_entry'),
    { kind: 'kit', id: 'tidewater-georgian', fragment: 'door_main_entry' });
  assert.equal(parseCite('not a ref'), null);
  assert.equal(parseCite(''), null);
  assert.equal(parseCite(null), null);
});

/* Dots in ids. The server's REF_RE has always allowed them because constraint ids are
   style-id.cNN; this half did not, so all 660 constraint citations parsed to null and
   navigated nowhere. Regression pin for that fix (WP-5.6). */
ok(() => {
  const c = parseCite('constraint:tidewater-georgian.c01');
  assert.deepEqual(c, { kind: 'constraint', id: 'tidewater-georgian.c01', fragment: null });
  assert.deepEqual(routeCite('constraint:tidewater-georgian.c01'),
    { surface: 'workbench', selection: { constraint: 'tidewater-georgian.c01' } });
});

/* ── 2. routeCite → citeFor is an identity for every kind but `brief` ──────────── */

const KINDS = [
  'style:craftsman',
  'kit:tidewater-georgian',
  'kit:tidewater-georgian#cornice',
  'slot:cornice',
  'fault:porch-too-shallow-to-inhabit',
  'pack:brick-course',
  'candidate:3',
  'finding:f12',
  'plan:parlour',
  'constraint:tidewater-georgian.c01',
  'room:dining-room',
  'massing:center-passage-single-pile',
  'parti:center-passage',
  'grouping:service-wing',
  'asset:habs-va-123',
];

KINDS.forEach((ref) => ok(() => {
  const target = routeCite(ref);
  assert.ok(target, `routeCite could not read ${ref}`);
  assert.equal(citeFor(target.surface, target.selection), ref,
    `${ref} did not survive routeCite → citeFor`);
}));

/* The documented exception, asserted rather than assumed: routeCite discards the brief's
   id, so no citation can be recovered from the surface, and citeFor says so with null
   instead of inventing one. */
ok(() => {
  const target = routeCite('brief:anything');
  assert.deepEqual(target, { surface: 'brief', selection: {} });
  assert.equal(citeFor('brief', {}), null);
});

ok(() => {
  assert.equal(routeCite('nosuchkind:x'), null);
  assert.equal(citeFor('nosuchsurface', { style: 'x' }), null);
  assert.equal(citeFor('style', {}), null);
});

/* ── 3. Every citation survives a round trip through a URL ─────────────────────── */

/* A URL cannot write down "present, but null", and nothing downstream reads one: every
   surface tests `selection?.slot` for truth. routeCite emits `slot: null` for a kit
   citation with no fragment, so the comparison is against the defined keys only. This
   is the one place the two representations are not literally equal, and it is stated
   here rather than hidden in a loose assertion. */
const defined = (o) => Object.fromEntries(Object.entries(o || {}).filter(([, v]) => v != null));

KINDS.forEach((ref) => ok(() => {
  const target = routeCite(ref);
  const hash = formatHash(target.surface, target.selection, {});
  const back = parseHash(hash);
  assert.equal(back.surface, target.surface, `${ref} → ${hash} landed on the wrong surface`);
  assert.deepEqual(back.selection, defined(target.selection), `${ref} → ${hash} lost part of its selection`);
  assert.equal(citeFor(back.surface, back.selection), ref, `${ref} did not survive the URL`);
}));

/* And the #/cite/ form, which is what a machine writes and a human clicks. */
KINDS.forEach((ref) => ok(() => {
  const back = parseHash('#/cite/' + ref);
  assert.equal(citeFor(back.surface, back.selection), ref, `#/cite/${ref} did not resolve to itself`);
}));

/* ── 4. The URL shapes themselves ──────────────────────────────────────────────── */

ok(() => {
  assert.deepEqual(parseHash('#/kit/tidewater-georgian/cornice'),
    { surface: 'kit', selection: { style: 'tidewater-georgian', slot: 'cornice' }, params: {} });
  assert.equal(formatHash('kit', { style: 'tidewater-georgian', slot: 'cornice' }, {}),
    '#/kit/tidewater-georgian/cornice');
});

/* A slot with no style: the placeholder holds the empty leading position rather than
   letting the slot slide into it. */
ok(() => {
  assert.equal(formatHash('kit', { slot: 'cornice' }, {}), '#/kit/-/cornice');
  assert.deepEqual(parseHash('#/kit/-/cornice').selection, { slot: 'cornice' });
});

/* Filters ride in the query and stay out of the selection. */
ok(() => {
  const p = parseHash('#/faults/porch-too-shallow-to-inhabit?sev=serious&driver=budget');
  assert.deepEqual(p.selection, { fault: 'porch-too-shallow-to-inhabit' });
  assert.deepEqual(p.params, { sev: 'serious', driver: 'budget' });
  assert.equal(formatHash('faults', { fault: 'x' }, { sev: 'serious' }), '#/faults/x?sev=serious');
});

/* Params are written in a stable order, so the same place is always the same link. */
ok(() => {
  assert.equal(formatHash('phylogeny', {}, { view: 'map', rank: 'family' }),
    formatHash('phylogeny', {}, { rank: 'family', view: 'map' }));
});

/* Empty, false and null params clear rather than serialize. */
ok(() => {
  assert.equal(formatHash('phylogeny', {}, { view: null, rank: '', ghost: false }), '#/phylogeny');
});

/* A selection key with no place in the surface's path still travels. */
ok(() => {
  const hash = formatHash('workbench', { room: 'parlour' }, {});
  assert.deepEqual(parseHash(hash).selection, { room: 'parlour' });
});

/* candidate is a number on both sides of the wire. */
ok(() => {
  assert.deepEqual(parseHash('#/candidates/3').selection, { candidate: 3 });
  assert.equal(typeof parseHash('#/candidates/3').selection.candidate, 'number');
  assert.deepEqual(parseHash('#/candidates/not-a-number').selection, {});
});

/* Nothing unreadable ever renders a blank screen. */
ok(() => {
  ['', '#', '#/', '#/nosuchsurface', '#/cite/garbage', '#/cite/', '#/?x=1'].forEach((h) => {
    const p = parseHash(h);
    assert.ok(SURFACE_PATHS[p.surface], `${JSON.stringify(h)} resolved to no surface`);
  });
  assert.equal(parseHash('#/nosuchsurface').surface, DEFAULT_SURFACE);
});

/* Ids with characters that need escaping survive both ways. */
ok(() => {
  const hash = formatHash('faults', { fault: 'a b/c' }, {});
  assert.deepEqual(parseHash(hash).selection, { fault: 'a b/c' });
});

/* ── 5. The tables agree with each other ───────────────────────────────────────── */

/* Every surface has a distinct path, or two surfaces would answer the same URL. */
ok(() => {
  const paths = Object.values(SURFACE_PATHS).map((s) => s.path);
  assert.equal(new Set(paths).size, paths.length, 'two surfaces claim the same path');
});

/* Every key a path carries is a selection key — a filter in the path could not be
   cleared, and a selection key missing from the list would be silently dropped. */
ok(() => {
  Object.entries(SURFACE_PATHS).forEach(([id, spec]) => {
    spec.keys.forEach((k) => {
      assert.ok(SELECTION_KEYS.includes(k), `${id} carries '${k}' in its path but it is not a selection key`);
    });
  });
});

/* Every selection routeCite can produce is one the URL knows how to carry. */
ok(() => {
  KINDS.concat(['brief:x']).forEach((ref) => {
    const t = routeCite(ref);
    Object.keys(t.selection || {}).forEach((k) => {
      assert.ok(SELECTION_KEYS.includes(k),
        `routeCite('${ref}') produces '${k}', which the URL would drop`);
    });
  });
});

console.log(`router-unit: ${checks} checks passed`);
