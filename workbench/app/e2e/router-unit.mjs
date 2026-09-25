/* The URL and the citation grammar are one addressing scheme written two ways. This
   pins that: every citation kind survives a round trip through a URL, and every URL
   parses back to the place it names.

   Pure functions, no DOM, no server:  node e2e/router-unit.mjs

   The modules are ESM with no JSX, so node runs them directly. Nothing here may import
   a .jsx file — if a future edit makes router.js or citations.js pull in a component,
   this test stops running and that is the point at which to split the module, not to
   delete the test.

   Two sections reach past the modules, and both say so where they do (WP-14.5): the
   constraint sweep READS styles/ from the checkout, because "a constraint opens its own
   style" is a claim about the corpus and not about the code; and section 7 imports
   state/nav.js behind a stand-in `location`, because withContext being right says nothing
   about whether nav.cite calls it. Still no DOM and no server. */

import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { parseCite, routeCite, citeFor, DOSSIER_SECTIONS } from '../src/citations.js';
import {
  parseHash, formatHash, SURFACE_PATHS, SELECTION_KEYS, DEFAULT_SURFACE,
  CONTEXT_KEYS, withContext, hrefFor, LEGACY_PATHS, isLegacyHash, canonicalHash,
} from '../src/router.js';

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
   navigated nowhere. Regression pin for that fix (WP-5.6).

   WP-14.5 re-cut the ROUTE half of this pin, not the parse half. It used to assert the
   constraint landed on the Plan Workbench, which reads no `constraint` from its selection —
   so the pin held a citation to a place that showed nothing about it. The property now is
   that a constraint opens where its style states it: that style's rules section, with the
   constraint selected, and citeFor naming it again from there. */
ok(() => {
  const c = parseCite('constraint:tidewater-georgian.c01');
  assert.deepEqual(c, { kind: 'constraint', id: 'tidewater-georgian.c01', fragment: null });
  assert.deepEqual(routeCite('constraint:tidewater-georgian.c01'),
    { surface: 'style',
      selection: { style: 'tidewater-georgian', section: 'rules', constraint: 'tidewater-georgian.c01' } });
  assert.equal(citeFor('style', routeCite('constraint:tidewater-georgian.c01').selection),
    'constraint:tidewater-georgian.c01');
});

/* The style is the text before the LAST dot, and an id with no dot names no style. The corpus
   holds no dotted style id, so the last-dot half is pinned on a synthetic id — it is the
   stated rule (§E.3), and a first-dot reading would pass every real id while being wrong. */
ok(() => {
  assert.equal(routeCite('constraint:a.b.c07').selection.style, 'a.b');
  assert.equal(routeCite('constraint:nodot'), null, 'a constraint with no style must go nowhere');
  assert.equal(routeCite('constraint:.c01'), null, 'an empty style is no style');
});

/* The address itself: a real constraint, written as the dossier writes it, parses to the
   rules section with the constraint selected and inverts to the citation. */
ok(() => {
  const hash = '#/style/tidewater-georgian/rules?constraint=tidewater-georgian.c01';
  const p = parseHash(hash);
  assert.deepEqual(p, {
    surface: 'style',
    selection: { style: 'tidewater-georgian', section: 'rules', constraint: 'tidewater-georgian.c01' },
    params: {},
  });
  assert.equal(citeFor(p.surface, p.selection), 'constraint:tidewater-georgian.c01');
  assert.equal(formatHash(p.surface, p.selection, p.params), hash, 'the dossier address is not canonical');
  assert.equal(hrefFor('constraint:tidewater-georgian.c01'), hash);
});

/* "The constraint's own style" is a claim about the CORPUS, so it is re-derived from the
   corpus on every run rather than trusted: every constraint a style node states must route to
   THAT node. Read from styles/ as the server's `_constraint_ids` reads it (each node's
   `constraints[].id`). A constraint filed under one style with another style's prefix would
   route silently to the wrong dossier, and nothing else would notice. */
ok(() => {
  const dir = new URL('../../../styles/', import.meta.url);
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  let n = 0;
  const wrong = [];
  files.forEach((f) => {
    const node = JSON.parse(readFileSync(new URL(f, dir), 'utf8'));
    (node.constraints || []).forEach((con) => {
      if (!con || !con.id) return;
      n += 1;
      const t = routeCite('constraint:' + con.id);
      if (!t || t.surface !== 'style' || t.selection.style !== node.id || t.selection.section !== 'rules'
          || t.selection.constraint !== con.id || citeFor(t.surface, t.selection) !== 'constraint:' + con.id) {
        wrong.push(`${con.id} (stated by ${node.id}) → ${JSON.stringify(t)}`);
      }
    });
  });
  // The premise, or a styles/ that moved would make this pass over nothing.
  assert.ok(files.length > 0 && n > 0, `read ${files.length} style files and ${n} constraints — the sweep saw nothing`);
  assert.deepEqual(wrong, [], `${wrong.length} of ${n} constraints do not route to their own style`);
});

/* ── 2. routeCite → citeFor is an identity for every kind but `brief` ──────────── */

const KINDS = [
  'style:craftsman',
  'style:craftsman#lineage',
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
  'term:judgment-unjudged',
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

/* ── 2b. Aliases: read, never written, and never in the identity list ──────────── */

/* `style:<id>#identify` is the bare style under another name. It routes with NO section key,
   so it cannot be written back into an address; the address it opens is the bare dossier; and
   the citation recovered from it is the bare one. An address that does carry `/identify` — a
   hand-typed one — is read as the same place: citeFor never mints `style:x#identify`. That
   last assertion is the one a writer that minted the alias would fail, which is why it reads
   the parsed URL rather than routeCite's output (routeCite has already dropped the section). */
ok(() => {
  assert.deepEqual(routeCite('style:craftsman#identify'), { surface: 'style', selection: { style: 'craftsman' } });
  assert.equal(citeFor('style', routeCite('style:craftsman#identify').selection), 'style:craftsman');
  assert.equal(hrefFor('style:craftsman#identify'), '#/style/craftsman', 'a writer emitted the identify form');
  const typed = parseHash('#/style/craftsman/identify');
  assert.deepEqual(typed.selection, { style: 'craftsman', section: 'identify' });
  assert.equal(citeFor(typed.surface, typed.selection), 'style:craftsman', 'citeFor minted style:x#identify');
  assert.equal(citeFor('style', { style: 'craftsman', section: 'identify' }), 'style:craftsman');
  assert.ok(!KINDS.some((k) => k.endsWith('#identify')), 'an alias was put in the identity list');
});

/* A fragment that is not a section is a SLOT, and it opens in the style's kit (WP-14.12, §E.3):
   the server's validator admits a `style:` fragment only as a slot id or a section id (§E.6), and
   no slot id is a section id. Until the kit moved into the dossier the fragment was dropped here
   and the reader landed on the style's top with nothing about the slot on screen. It is an ALIAS
   of `kit:<id>#<slot>` — read, never minted, and never in the identity list. The same holds for
   `style:<id>#kit`, an alias of `kit:<id>` (it was an identity at WP-14.5, before the kit moved).

   An address holding an unknown section is not cited by it — `style:x#nonsense` is a ref the
   server's validator refuses, so citeFor names the style and nothing it cannot stand behind. An
   absent or empty section is the bare place. */
ok(() => {
  assert.deepEqual(routeCite('style:craftsman#cornice'),
    { surface: 'style', selection: { style: 'craftsman', section: 'kit', slot: 'cornice' } });
  assert.equal(citeFor('style', routeCite('style:craftsman#cornice').selection), 'kit:craftsman#cornice',
    'a slot fragment is cited by the kit it opens');
  assert.equal(hrefFor('style:craftsman#cornice'), '#/style/craftsman/kit/cornice');
  assert.deepEqual(routeCite('style:craftsman#kit'), { surface: 'style', selection: { style: 'craftsman', section: 'kit' } });
  assert.equal(citeFor('style', routeCite('style:craftsman#kit').selection), 'kit:craftsman');
  assert.ok(!KINDS.some((k) => /^style:[^#]+#(kit|cornice)$/.test(k)), 'an alias was put in the identity list');
  assert.equal(citeFor('style', { style: 'craftsman', section: 'nosuch' }), 'style:craftsman');
  assert.equal(citeFor('style', { style: 'craftsman' }), 'style:craftsman');
  assert.equal(citeFor('style', { style: 'craftsman', section: '' }), 'style:craftsman');
});

/* The glossary: a term citation lands on the term; the bare glossary is a place no citation
   names, so citeFor says null rather than inventing one. */
ok(() => {
  assert.deepEqual(routeCite('term:judgment-unjudged'), { surface: 'glossary', selection: { term: 'judgment-unjudged' } });
  assert.deepEqual(parseHash('#/glossary'), { surface: 'glossary', selection: {}, params: {} });
  assert.deepEqual(parseHash('#/glossary/judgment-unjudged').selection, { term: 'judgment-unjudged' });
  assert.equal(citeFor('glossary', {}), null);
  assert.equal(hrefFor('term:judgment-unjudged'), '#/glossary/judgment-unjudged');
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

/* ── 3b. Every dossier section round-trips through a URL ───────────────────────── */

/* The vocabulary's properties, not its words: the words are spelled in citations.js and, by
   §D.1, once more on the server, and a third copy here would be one more thing to drift.
   Frozen, no duplicate, `identify` first (the alias is defined against it), and every id a
   fragment the grammar can carry and a path segment that needs no escaping — a section no
   citation could name, or one whose address is written percent-encoded, is not a place. */
ok(() => {
  assert.ok(Object.isFrozen(DOSSIER_SECTIONS), 'DOSSIER_SECTIONS can be widened at run time');
  assert.equal(new Set(DOSSIER_SECTIONS).size, DOSSIER_SECTIONS.length, 'a section id is listed twice');
  assert.equal(DOSSIER_SECTIONS[0], 'identify');
  DOSSIER_SECTIONS.forEach((s) => {
    assert.equal(parseCite('style:craftsman#' + s)?.fragment, s, `'${s}' is not a fragment the grammar can carry`);
    assert.equal(encodeURIComponent(s), s, `'${s}' would be written escaped in the address`);
  });
});

/* Each section, as the dossier's address and back. `identify` survives the URL as a selection
   and is cited as the bare style — the reader treats the two forms alike; `kit` is cited by the
   kit's own kind, `kit:<id>` (§E.3, final since WP-14.12), and routes back to the same selection;
   every other section is its own citation, which routes back to the same selection and draws the
   same address. */
DOSSIER_SECTIONS.forEach((section) => ok(() => {
  const sel = { style: 'craftsman', section };
  const hash = formatHash('style', sel, {});
  const back = parseHash(hash);
  assert.deepEqual(back, { surface: 'style', selection: sel, params: {} }, `${section}: ${hash} lost its section`);
  const ref = citeFor(back.surface, back.selection);
  if (section === 'identify') {
    assert.equal(ref, 'style:craftsman', 'the identify section minted its own citation');
    return;
  }
  assert.equal(hash, '#/style/craftsman/' + section);
  assert.equal(ref, section === 'kit' ? 'kit:craftsman' : 'style:craftsman#' + section);
  assert.deepEqual(routeCite(ref), { surface: 'style', selection: sel });
  assert.equal(hrefFor(ref), hash);
  assert.equal(citeFor(parseHash('#/cite/' + ref).surface, parseHash('#/cite/' + ref).selection), ref);
}));

/* A slot rides after the section, in the path, and the `-` placeholder holds an absent style —
   the two shapes §E.2 names, and each is a citation now (WP-14.12): one slot in a style's kit is
   `kit:<id>#<slot>`, and one slot across styles — the slot panel — is `slot:<id>`. */
ok(() => {
  assert.deepEqual(parseHash('#/style/tidewater-georgian/kit/cornice').selection,
    { style: 'tidewater-georgian', section: 'kit', slot: 'cornice' });
  assert.equal(formatHash('style', { style: 'tidewater-georgian', section: 'kit', slot: 'cornice' }, {}),
    '#/style/tidewater-georgian/kit/cornice');
  assert.equal(citeFor('style', parseHash('#/style/tidewater-georgian/kit/cornice').selection),
    'kit:tidewater-georgian#cornice');
  assert.equal(hrefFor('kit:tidewater-georgian#cornice'), '#/style/tidewater-georgian/kit/cornice');
  assert.deepEqual(parseHash('#/style/-/kit/cornice').selection, { section: 'kit', slot: 'cornice' });
  assert.equal(formatHash('style', { section: 'kit', slot: 'cornice' }, {}), '#/style/-/kit/cornice');
  assert.equal(citeFor('style', { section: 'kit', slot: 'cornice' }), 'slot:cornice');
  assert.equal(hrefFor('slot:cornice'), '#/style/-/kit/cornice');
  // The kit section with neither a style nor a slot names nothing a citation can: the index.
  assert.equal(citeFor('style', { section: 'kit' }), null);
  assert.deepEqual(parseHash('#/style').selection, {});
  assert.deepEqual(parseHash('#/style/-').selection, {});
});

/* ── 4. The URL shapes themselves ──────────────────────────────────────────────── */

/* THE KIT IS NOT A SURFACE, AND ITS OLD ADDRESS IS AN ALIAS (WP-14.12, PRD §E.1). Every row of
   §E.1's legacy table, read positionally with the same `-` placeholder; `section: 'kit'` set only
   where a style or a slot is named, so a bare `#/kit` — which used to show Tidewater's kit, a
   style the URL never said — is the Styles index. Each row is asserted three ways: what it parses
   to, the canonical address `formatHash` and `canonicalHash` write for it, and that the canonical
   address is not itself legacy (a rewrite that produced another legacy hash would loop). */
ok(() => {
  assert.equal(SURFACE_PATHS.kit, undefined, 'the kit is still a surface of its own');
  assert.ok(Object.isFrozen(LEGACY_PATHS) && Object.isFrozen(LEGACY_PATHS.kit), 'the legacy table can be widened at run time');
  assert.ok(!Object.keys(LEGACY_PATHS).some((k) => SURFACE_PATHS[k]), 'a legacy path is also a live surface');
  Object.values(LEGACY_PATHS).forEach((l) => assert.ok(SURFACE_PATHS[l.to], `a legacy path points at '${l.to}', which has no route`));
  const TABLE = [
    ['#/kit/craftsman/cornice', { style: 'craftsman', section: 'kit', slot: 'cornice' }, '#/style/craftsman/kit/cornice'],
    ['#/kit/craftsman', { style: 'craftsman', section: 'kit' }, '#/style/craftsman/kit'],
    ['#/kit/-/cornice', { section: 'kit', slot: 'cornice' }, '#/style/-/kit/cornice'],
    ['#/kit', {}, '#/style'],
    ['#/kit/', {}, '#/style'],
    ['#/kit/tidewater-georgian/cornice?group=openings&q=cornice',
      { style: 'tidewater-georgian', section: 'kit', slot: 'cornice' },
      '#/style/tidewater-georgian/kit/cornice?group=openings&q=cornice'],
  ];
  TABLE.forEach(([legacy, selection, canonical]) => {
    const p = parseHash(legacy);
    assert.equal(p.surface, 'style', `${legacy} did not read as the dossier`);
    assert.deepEqual(p.selection, selection, `${legacy} read as ${JSON.stringify(p.selection)}`);
    assert.ok(isLegacyHash(legacy), `${legacy} is not recognised as legacy`);
    assert.equal(canonicalHash(legacy), canonical, `${legacy} canonicalises to ${canonicalHash(legacy)}`);
    assert.equal(formatHash(p.surface, p.selection, p.params), canonical);
    assert.ok(!isLegacyHash(canonical), `${canonical} is itself legacy — the rewrite would loop`);
    assert.equal(canonicalHash(canonical), null, 'a canonical address was rewritten again');
  });
  // The filters rode along into params, not the selection.
  assert.deepEqual(parseHash('#/kit/tidewater-georgian/cornice?group=openings').params, { group: 'openings' });
});

/* A caller that still says `kit` writes the canonical address, not the Overview's: a retired
   surface id is an alias in the writer too. And nothing that is not legacy is taken for it. */
ok(() => {
  assert.equal(formatHash('kit', { style: 'tidewater-georgian', slot: 'cornice' }, {}), '#/style/tidewater-georgian/kit/cornice');
  assert.equal(formatHash('kit', { slot: 'cornice' }, {}), '#/style/-/kit/cornice');
  assert.equal(formatHash('kit', {}, {}), '#/style');
  assert.equal(formatHash('kit', { style: 'craftsman' }, { q: 'porch' }), '#/style/craftsman/kit?q=porch');
  ['#/style/craftsman/kit', '#/kitchen', '#/cite/kit:craftsman', '#/', '', '#/style', '#/faults/kit']
    .forEach((h) => {
      assert.ok(!isLegacyHash(h), `${h} was taken for a legacy address`);
      assert.equal(canonicalHash(h), null);
    });
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

/* WP-12.4: the Round's axes ride in the query and round-trip, so a copied link reproduces the
   view, the overlays and the cut. None of them is a SELECTION key — `router.js` puts any query
   key that is neither a selection key nor one of the surface's path keys into `params`, so this
   needed no table change, and adding them to SELECTION_KEYS would quietly change what a
   citation means. */
ok(() => {
  const p = parseHash('#/drawings?cut=x:20.4&explode=levels&ov=grid,datums&view=axon-sw');
  assert.deepEqual(p.selection, {});
  assert.deepEqual(p.params, { view: 'axon-sw', ov: 'grid,datums', explode: 'levels', cut: 'x:20.4' });
  // Asserted as a ROUND TRIP rather than as a byte string: `formatHash` percent-encodes the
  // ':' in a cut and the ',' in an overlay list, and `parseHash` decodes them again. Pinning
  // the encoded literal would pin the encoder rather than the property a copied link needs.
  const params = { view: 'axon-sw', ov: 'grid,datums', explode: 'levels', cut: 'x:20.4' };
  assert.deepEqual(parseHash(formatHash('drawings', {}, params)).params, params);
  assert.deepEqual(parseHash(formatHash('drawings', {}, params)).surface, 'drawings');
});

/* A plan view carries its level, and the level survives as a STRING — NUMERIC_KEYS holds only
   `candidate`, so a surface comparing `level === 0` against '0' silently never matches. */
ok(() => {
  const p = parseHash('#/drawings?level=1&view=plan-l1');
  assert.deepEqual(p.params, { view: 'plan-l1', level: '1' });
  assert.equal(typeof p.params.level, 'string');
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

/* The context table names only surfaces that have a route and only keys the URL can carry: a
   key withContext added that is not a selection key would be written nowhere by formatHash —
   carried in memory and lost from the link. Frozen, so no reader can widen it for everyone. */
ok(() => {
  assert.ok(Object.isFrozen(CONTEXT_KEYS), 'CONTEXT_KEYS can be widened at run time');
  Object.entries(CONTEXT_KEYS).forEach(([surface, keys]) => {
    assert.ok(SURFACE_PATHS[surface], `CONTEXT_KEYS names '${surface}', which has no route`);
    assert.ok(Object.isFrozen(keys), `CONTEXT_KEYS.${surface} can be widened at run time`);
    keys.forEach((k) => assert.ok(SELECTION_KEYS.includes(k),
      `CONTEXT_KEYS.${surface} carries '${k}', which the URL would drop`));
  });
});

/* ── 6. Context carry ──────────────────────────────────────────────────────────── */

/* What a reader holds where a link is drawn. Deliberately a selection carrying keys no surface
   may receive beside the one some may, so that "keeps only the allowed keys" has something to
   refuse. */
const CTX = {
  style: 'craftsman', fault: 'porch-too-shallow-to-inhabit', slot: 'cornice', pack: 'brick-course',
  section: 'kit', term: 'judgment-unjudged', constraint: 'craftsman.c01', candidate: 2,
};

/* Every surface, from an empty selection, gains exactly the keys the table lists for it, each
   with the context's value, and nothing else; a surface with no entry gains nothing. */
Object.keys(SURFACE_PATHS).forEach((surface) => ok(() => {
  const got = withContext({ surface, selection: {} }, CTX);
  const want = Object.fromEntries((CONTEXT_KEYS[surface] || []).map((k) => [k, CTX[k]]));
  assert.deepEqual(got, { surface, selection: want }, `withContext carried the wrong keys onto '${surface}'`);
}));

/* The same, by citation, as a reader follows them: the three targets §E.5 names take the
   style, and places that could hold a style and do not honour a carried one take nothing —
   the kit and the phylogeny carry `style` in their own paths, and a carried value there would
   silently change which record the reader is shown. */
ok(() => {
  assert.deepEqual(withContext(routeCite('pack:trim-classical'), CTX),
    { surface: 'proportions', selection: { pack: 'trim-classical', style: 'craftsman' } });
  assert.deepEqual(withContext(routeCite('fault:porch-too-shallow-to-inhabit'), CTX),
    { surface: 'faults', selection: { fault: 'porch-too-shallow-to-inhabit', style: 'craftsman' } });
  assert.deepEqual(withContext(routeCite('brief:x'), CTX), { surface: 'brief', selection: { style: 'craftsman' } });
  ['slot:cornice', 'kit:tidewater-georgian#cornice', 'massing:center-passage-single-pile',
    'style:tidewater-georgian#lineage', 'constraint:tidewater-georgian.c01', 'term:judgment-unjudged',
    'candidate:3', 'plan:parlour'].forEach((ref) => {
    assert.deepEqual(withContext(routeCite(ref), CTX), routeCite(ref), `${ref} received context it does not honour`);
  });
});

/* The target always wins: a citation that names a style means that style. */
ok(() => {
  const t = { surface: 'faults', selection: { fault: 'porch-too-shallow-to-inhabit', style: 'gothic-revival' } };
  assert.equal(withContext(t, CTX).selection.style, 'gothic-revival');
});

/* Only a non-empty string travels; no context is no change; and a citation that resolves
   nowhere still goes nowhere — a context must not turn a dead link into a live one. */
ok(() => {
  const t = routeCite('pack:trim-classical');
  [{}, { style: '' }, { style: null }, { style: 7 }, { style: ['craftsman'] }].forEach((ctx) => {
    assert.deepEqual(withContext(t, ctx).selection, { pack: 'trim-classical' }, `carried ${JSON.stringify(ctx)}`);
  });
  assert.deepEqual(withContext(t, undefined), t);
  assert.deepEqual(withContext(t, null), t);
  assert.equal(withContext(null, CTX), null);
  assert.equal(withContext(routeCite('nosuchkind:x'), CTX), null);
  assert.equal(hrefFor('nosuchkind:x', CTX), null);
});

/* It never mutates what it was handed — routeCite's result is a fresh object today, and a
   caller holding a target it did not build must not find a style written into it. */
ok(() => {
  const t = { surface: 'proportions', selection: { pack: 'trim-classical' } };
  const before = JSON.stringify(t);
  withContext(t, CTX);
  assert.equal(JSON.stringify(t), before, 'withContext wrote into the target it was handed');
});

/* The carried key survives the address, and is context rather than citation: the page it opens
   is still cited as the pack alone. */
ok(() => {
  const hash = hrefFor('pack:trim-classical', CTX);
  assert.equal(hash, '#/proportions/trim-classical?style=craftsman');
  const p = parseHash(hash);
  assert.deepEqual(p, { surface: 'proportions', selection: { pack: 'trim-classical', style: 'craftsman' }, params: {} });
  assert.equal(citeFor(p.surface, p.selection), 'pack:trim-classical');
  assert.equal(hrefFor('fault:porch-too-shallow-to-inhabit', CTX), '#/faults/porch-too-shallow-to-inhabit?style=craftsman');
  assert.equal(hrefFor('brief:x', CTX), '#/brief?style=craftsman');
  assert.equal(hrefFor('slot:cornice', CTX), '#/style/-/kit/cornice');
});

/* ── 7. The two writers: nav.cite carries context, nav.go does not ─────────────── */

/* withContext being right says nothing about whether nav.cite calls it — each half driven and
   the join asserted by nothing is how a guard goes blind. So the join is driven, against a
   stand-in address bar: nav.js reaches `location`, `history` and `window` only behind `typeof`
   guards and follows a citation with `location.hash = …`, so an object with a `hash` field is
   the whole of what it needs. No DOM. */
/* WP-14.12 adds `history` and `window` stand-ins, and starts the address bar on a LEGACY hash:
   nav.js canonicalizes on a cold load (behind `typeof window`) and on every hashchange, and the
   one way to know it rewrites `#/kit/...` is to load it on one and read the address bar after.
   `replaceState` writes the address without firing a hashchange, as a browser's does. */
const hashListeners = [];
globalThis.location = { hash: '#/kit/craftsman/cornice?q=porch' };
globalThis.history = { replaceState: (_s, _t, url) => { globalThis.location.hash = url; } };
globalThis.window = { addEventListener: (type, fn) => { if (type === 'hashchange') hashListeners.push(fn); } };
const { nav } = await import('../src/state/nav.js');

ok(() => {
  assert.equal(location.hash, '#/style/craftsman/kit/cornice?q=porch',
    'a cold load on a legacy #/kit address was not rewritten to the dossier');
  assert.deepEqual(nav.get(), { surface: 'style',
    selection: { style: 'craftsman', section: 'kit', slot: 'cornice' }, params: { q: 'porch' } });
  // and on a hashchange, as a reader typing or following an old link produces
  assert.equal(hashListeners.length, 1, 'nav.js does not listen for the address changing');
  location.hash = '#/kit';
  hashListeners.forEach((fn) => fn());
  assert.equal(location.hash, '#/style', 'a bare #/kit was not rewritten to the Styles index');
  assert.deepEqual(nav.get().selection, {});
  location.hash = '#/kit/-/cornice';
  hashListeners.forEach((fn) => fn());
  assert.equal(location.hash, '#/style/-/kit/cornice');
  // a canonical address is left exactly as it was
  location.hash = '#/style/craftsman/lineage';
  hashListeners.forEach((fn) => fn());
  assert.equal(location.hash, '#/style/craftsman/lineage');
});

ok(() => {
  nav.cite('pack:trim-classical', CTX);
  assert.equal(location.hash, '#/proportions/trim-classical?style=craftsman', 'nav.cite dropped or widened the context');
  nav.cite('slot:cornice', CTX);
  assert.equal(location.hash, '#/style/-/kit/cornice', 'nav.cite carried context onto a surface that does not honour it');
  nav.cite('fault:porch-too-shallow-to-inhabit');
  assert.equal(location.hash, '#/faults/porch-too-shallow-to-inhabit', 'nav.cite with no context is not the call it was');
  nav.cite('nosuchkind:x', CTX);
  assert.equal(location.hash, '#/faults/porch-too-shallow-to-inhabit', 'an unresolvable citation moved the reader');
  nav.go('proportions', { pack: 'trim-classical' }, CTX);
  assert.equal(location.hash, '#/proportions/trim-classical', 'nav.go carried context across a surface boundary');
});

/* An anchor drawn with hrefFor and a click through nav.cite land in one place, for every kind. */
KINDS.concat(['brief:x']).forEach((ref) => ok(() => {
  nav.cite(ref, CTX);
  assert.equal(location.hash, hrefFor(ref, CTX), `${ref}: the anchor and the click disagree`);
}));

delete globalThis.location;
delete globalThis.history;
delete globalThis.window;

console.log(`router-unit: ${checks} checks passed`);
