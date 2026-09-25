/* The citation grammar: kind:id(#fragment)?  —  one router for the whole product.
   Rail chips, finding rule refs and cross-surface links all come through here, so a
   citation anywhere navigates the canvas the same way.

   The id character class must stay identical to REF_RE in workbench/server/citations.py.
   It was not: the server allowed dots (its comment says why — constraint ids are
   style-id.cNN) and this half did not, so all 660 constraint ids validated on the server,
   streamed as citations, and then parsed to null here. Every `constraint:` chip the rail
   ever drew navigated nowhere, silently. WP-5.6 widened this class to match — and an
   adversarial audit then found a THIRD copy, in rail.py's CITE_RE, which extracts
   `[[cite:...]]` from model output and also lacked the dot. So the widening changed nothing
   observable: a constraint citation was never extracted, never validated, and reached the
   reader as literal bracket syntax. All three now agree, and
   workbench/server/tests/test_grammar_agreement.py reads this file to keep them agreeing —
   which is why the classes below are named constants rather than a regex literal.

   ID_CHARS and FRAG_CHARS are the same two classes citations.py exports under those names. */

export const ID_CHARS = 'A-Za-z0-9_.-';
export const FRAG_CHARS = 'A-Za-z0-9_-';
const REF_RE = new RegExp(`^([a-z]+):([${ID_CHARS}]+)(?:#([${FRAG_CHARS}]+))?$`);

export function parseCite(ref) {
  const m = REF_RE.exec(ref || '');
  if (!m) return null;
  return { kind: m[1], id: m[2], fragment: m[3] || null };
}

/* The dossier's sections, in the corpus's own consulting order (PRD phase 14, §D.1). The URL
   id is the first column; the label a reader sees is the `section-<id>` glossary record's
   term and is written nowhere in the app.

   A pinned VOCABULARY, not a pattern — the grammar above is untouched by it. It lets a
   `style:` fragment name a section as well as a slot, which is unambiguous only because no
   slot id is a section id: 97 slots, 0 collisions, measured 24 Sep 2026 against ontology
   0.7.0. §D.1 allows exactly one other spelling, the server's tuple of the same name in
   workbench/server/citations.py, which test_grammar_agreement.py holds to this line by
   READING it — so it stays on one line, in this exact form. */
export const DOSSIER_SECTIONS = Object.freeze(['identify', 'members', 'lineage', 'kit', 'proportions', 'plans', 'rules', 'faults', 'evidence']);

/* `identify` is the section the bare citation already names. It is read as an alias for the
   bare form and never written: a place with it selected and a place with no section are one
   place, and one place has one citation. */
const IDENTIFY = 'identify';
const KIT = 'kit';

/* The style a constraint belongs to: the text before the LAST dot of its id, or null for an id
   with no dot or an empty style. 660 of 660 constraint ids in the corpus are
   `<style id>.<suffix>` with the id of the very node whose `constraints` carry them, and no style
   id contains a dot (both measured 24 Sep 2026; e2e/router-unit.mjs re-derives the first over the
   whole corpus on every run). THE ONE SPELLING: `routeCite` routes a constraint by it and
   `names/names.js` names one by it (WP-14.12 moved names.js's temporary copy here). */
export function constraintStyleOf(id) {
  if (typeof id !== 'string') return null;
  const at = id.lastIndexOf('.');
  return at > 0 ? id.slice(0, at) : null;
}

/* Returns {surface, selection} — App owns applying it. */
export function routeCite(ref) {
  const c = parseCite(ref);
  if (!c) return null;
  switch (c.kind) {
    // the full record beats the graph panel now that surface ③ exists;
    // the phylogeny stays one rail-click away and links back
    case 'style': {
      // A fragment that is a section opens it. `#identify` is an alias and carries NO section
      // key, so it cannot round-trip into a URL that mints it. Any OTHER fragment is a slot: the
      // server's validator admits a `style:` fragment only when it is a slot id or a section id
      // (§E.6), and no slot id is a section id, so what is left is a slot — and it opens in the
      // style's kit, as `kit:<id>#<slot>` does (WP-14.12; until then it was dropped). A fragment
      // the corpus does not hold still opens the kit, which says it holds no such slot.
      if (!c.fragment || c.fragment === IDENTIFY) return { surface: 'style', selection: { style: c.id } };
      if (DOSSIER_SECTIONS.includes(c.fragment)) {
        return { surface: 'style', selection: { style: c.id, section: c.fragment } };
      }
      return { surface: 'style', selection: { style: c.id, section: KIT, slot: c.fragment } };
    }
    /* The kit is the dossier's KIT SECTION since WP-14.12 (PRD §E.3): `kit:<id>` opens it and
       `kit:<id>#<slot>` opens that slot in it. `slot:<id>` names a slot with no style, which is
       the slot panel — one slot across every style that specifies it — rather than, as it was,
       Tidewater Georgian's kit, a style the citation never named. */
    case 'kit': return { surface: 'style',
      selection: c.fragment ? { style: c.id, section: KIT, slot: c.fragment } : { style: c.id, section: KIT } };
    case 'slot': return { surface: 'style', selection: { section: KIT, slot: c.id } };
    case 'fault': return { surface: 'faults', selection: { fault: c.id } };
    case 'pack': return { surface: 'proportions', selection: { pack: c.id } };
    case 'candidate': return { surface: 'candidates', selection: { candidate: Number(c.id) } };
    case 'finding': return { surface: 'workbench', selection: { finding: c.id } };
    case 'plan': return { surface: 'workbench', selection: { room: c.id } };
    /* A constraint is a rule a STYLE states, so it opens where that style states it: the
       dossier's rules section, with the constraint selected. Until WP-14.5 it routed to the
       Plan Workbench, which reads no `constraint` from its selection and never has — every
       constraint citation landed on the bench with nothing highlighted.

       The style is `constraintStyleOf`'s, above. An id with no dot names no style, and landing
       it on an arbitrary one would be worse than not moving, so it is null. */
    case 'constraint': {
      const style = constraintStyleOf(c.id);
      if (!style) return null;
      return { surface: 'style', selection: { style, section: 'rules', constraint: c.id } };
    }
    case 'term': return { surface: 'glossary', selection: { term: c.id } };
    case 'room': return { surface: 'workbench', selection: { roomType: c.id } };
    case 'massing': return { surface: 'phylogeny', selection: { massing: c.id } };
    case 'parti': return { surface: 'candidates', selection: { parti: c.id } };
    case 'grouping': return { surface: 'workbench', selection: { grouping: c.id } };
    case 'brief': return { surface: 'brief', selection: {} };
    case 'asset': return { surface: 'faults', selection: { asset: c.id } };
    default: return null;
  }
}

/* The inverse: what citation names this place? Lives beside routeCite so the two
   directions cannot drift — the URL scheme (router.js) is a serialization of exactly
   these pairs, and e2e/router-unit.mjs pins routeCite → citeFor as an identity for
   every kind but one.

   That one is `brief`: routeCite discards the id (there is a single brief), so no
   citation can be recovered from the surface. It returns null rather than inventing one.
   Where a surface holds several citable keys at once the most specific wins.

   Aliases are the other direction's business and are asserted as aliases, never in that
   identity list: `style:<id>#identify` reads as `style:<id>`, and this function never mints
   it. */
export function citeFor(surface, selection) {
  const s = selection || {};
  switch (surface) {
    case 'style':
      // The most specific first: a selected constraint names the place better than the
      // section it sits in.
      if (s.constraint) return 'constraint:' + s.constraint;
      /* The kit section is cited by the kit's own kinds (§E.3's second branch, WP-14.12): a
         style's kit is `kit:<id>`, one slot in it `kit:<id>#<slot>`, and a slot with no style —
         the slot panel — `slot:<id>`. `style:<id>#kit` and `style:<id>#<slot>` are aliases that
         route here and are never minted. */
      if (s.section === KIT) {
        if (s.style) return 'kit:' + s.style + (s.slot ? '#' + s.slot : '');
        return s.slot ? 'slot:' + s.slot : null;
      }
      if (!s.style) return null;
      /* A section is written only when it is one — `identify` is the bare form, and a section
         id the vocabulary does not hold (a hand-typed `#/style/x/nonsense`) is not a place a
         citation can name: `style:x#nonsense` is a ref the server's validator refuses, and
         routeCite would read it back as the bare style anyway. */
      if (s.section && s.section !== IDENTIFY && DOSSIER_SECTIONS.includes(s.section)) {
        return 'style:' + s.style + '#' + s.section;
      }
      return 'style:' + s.style;
    case 'glossary': return s.term ? 'term:' + s.term : null;
    case 'faults':
      if (s.fault) return 'fault:' + s.fault;
      return s.asset ? 'asset:' + s.asset : null;
    case 'proportions': return s.pack ? 'pack:' + s.pack : null;
    case 'candidates':
      if (s.parti) return 'parti:' + s.parti;
      return s.candidate != null ? 'candidate:' + s.candidate : null;
    case 'phylogeny':
      // A style on the phylogeny is not `style:` — that citation routes to the full
      // record by a decision recorded above. Only the massing has an exact inverse here.
      return s.massing ? 'massing:' + s.massing : null;
    case 'workbench':
      if (s.finding) return 'finding:' + s.finding;
      // No citation routes a constraint here any more (WP-14.5); an address written before it,
      // `#/workbench?constraint=<id>`, still parses to the bench, and the citation that names
      // what it selected is the constraint's own — which now opens where the rule is stated.
      if (s.constraint) return 'constraint:' + s.constraint;
      if (s.room) return 'plan:' + s.room;
      if (s.roomType) return 'room:' + s.roomType;
      return s.grouping ? 'grouping:' + s.grouping : null;
    default: return null;
  }
}
