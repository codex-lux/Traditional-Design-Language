/* WHERE YOU ARE, AS A TRAIL AND AS A TAB TITLE (WP-14.13, PRD §F.3).

   No page in the workbench said where it was: `document.title` was fixed at one string for
   every place, so every tab and every bookmark read the same, and a colleague handed a link
   landed on a page with nothing to say how it related to anything. `crumbsFor(place, …)` is the
   trail — the group, then each place above this one, then this one — and `titleFor(crumbs,
   lookup)` is the same trail read backwards for a tab, because a tab shows its first words and
   the first words should be the page.

   THE STYLE CHAIN FOLLOWS `member_of`, NEVER LINEAGE. A style is FILED under one family and a
   family under one tradition; it DESCENDS from, references and is regional to many others. The
   trail is the filing — *Styles › North American › American Colonial › Georgian Colonial
   American › Tidewater Georgian › Kit › Main cornice* — because that is the one path upward
   that is a path; lineage is a graph and has the Lineage section to itself. The chain comes from
   the served dossier (`dossier.chain`, root first) where that dossier is this style's, and
   otherwise from the style list the app already holds (`chainOf`, the same walk over the same
   field), so the trail is complete on the first render and not only after the dossier arrives.
   `src/crumbs.test.mjs` holds the two to each other and to `styles/*.json` for every style.

   EVERY WORD IS A RECORD'S. Group and surface crumbs are glossary records' `term`s; a style, a
   slot, a pack, a fault is named by `names/names.js` over the search index, which never invents a
   name (an unnamed record reads as its citation, visibly a machine id); a glossary term is its
   own record's word. A record the glossary does not hold is `label: null, missing: <id>`, and a
   renderer prints `noEntry(id)`.

   THE URL DECIDES WHAT IS READ. The trail is built from the place alone: a bare `#/faults` is
   *Library › Faults*, whichever fault the surface falls back to drawing, because a trail that
   named a fallback record would present a default as the thing the reader asked for.

   Pure: no React, no DOM. */
import { formatHash } from '../router.js';
import { nameFor } from '../names/names.js';
import { noEntry } from '../glossary/termView.js';
import { normalizePlace, sectionOf, stylePlaceKind, wordFor, NAV } from './navModel.js';

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);
const str = (v) => (typeof v === 'string' && v.trim() ? v.trim() : null);

/* The group each surface's crumb trail begins with — read off NAV, so a surface moved between
   groups moves its trail with it. */
function groupOfSurface(surface) {
  for (const g of NAV) {
    for (const it of g.items) {
      if (it.surface === surface) return g;
      for (const c of it.children || []) if (c.surface === surface) return g;
    }
  }
  return null;
}

/* The `member_of` chain of a style, root first and excluding the style itself, over a map of
   nodes each carrying `member_of` (the record's field) or `in` (the same fact as `/api/styles`
   serves it). A cycle or a missing ancestor ends the walk rather than looping or inventing one. */
export function chainOf(styleId, nodes) {
  const byId = nodes instanceof Map ? nodes : new Map(
    (Array.isArray(nodes) ? nodes : []).filter((n) => isObj(n) && str(n.id)).map((n) => [n.id, n]),
  );
  const parentOf = (n) => str(n.member_of) || str(n.in);
  const start = byId.get(styleId);
  if (!start) return null;
  const out = [];
  const seen = new Set([styleId]);
  let cur = parentOf(start);
  while (cur && !seen.has(cur) && byId.has(cur)) {
    seen.add(cur);
    const n = byId.get(cur);
    out.push({ id: cur, name: str(n.name), rank: str(n.rank) });
    cur = parentOf(n);
  }
  return out.reverse();
}

function namer(names) {
  if (typeof names === 'function') return (cite) => names(cite);
  return (cite) => nameFor(cite, names);
}

const termCrumb = (lookup, termId, href, isGroup) => {
  const { label, missing } = wordFor(lookup, termId);
  return { label, href: href || null, termId, missing, group: Boolean(isGroup), cite: null };
};

const recordCrumb = (name, href, cite) => ({
  label: name, href: href || null, termId: null, missing: null, group: false, cite,
});

/* → [{ label, href, termId, missing, group, cite }]. The last crumb is the place: `href` null. */
export function crumbsFor(place, { lookup, dossier, names, styles, journey } = {}) {
  void journey; // accepted per §F.3; a house step's crumb is its surface's record, not its state
  const { surface, selection: sel } = normalizePlace(place);
  if (surface === 'overview') return [];
  const nameOf = namer(names);
  const recordName = (cite) => {
    const n = nameOf(cite);
    return n && str(n.name) ? n.name : cite;
  };
  const g = groupOfSurface(surface);
  if (!g) return [];
  const out = [termCrumb(lookup, g.termId, null, true)];
  const here = (termId) => termCrumb(lookup, termId, formatHash(surface, {}, {}));

  if (surface === 'style') {
    const kind = stylePlaceKind(sel);
    if (kind !== 'dossier') {
      out.push(termCrumb(lookup, 'surface-style', formatHash('style', {}, {})));
      if (kind === 'slot') {
        out.push(termCrumb(lookup, 'section-kit', null));
        out.push(recordCrumb(recordName(`slot:${sel.slot}`), null, `slot:${sel.slot}`));
      }
    } else {
      const id = sel.style;
      const mine = isObj(dossier) && dossier.id === id ? dossier : null;
      const chain = mine && Array.isArray(mine.chain) ? mine.chain : chainOf(id, styles) || [];
      for (const c of chain) {
        if (!isObj(c) || !str(c.id)) continue;
        out.push(recordCrumb(str(c.name) || recordName(`style:${c.id}`),
          formatHash('style', { style: c.id }, {}), `style:${c.id}`));
      }
      const name = (mine && str(mine.name)) || recordName(`style:${id}`);
      out.push(recordCrumb(name, formatHash('style', { style: id }, {}), `style:${id}`));
      const section = sectionOf(sel);
      if (section !== 'identify') {
        out.push(termCrumb(lookup, `section-${section}`, formatHash('style', { style: id, section }, {})));
        if (section === 'kit' && str(sel.slot)) {
          out.push(recordCrumb(recordName(`slot:${sel.slot}`), null, `slot:${sel.slot}`));
        }
      }
    }
  } else if (surface === 'phylogeny') {
    out.push(here('surface-phylogeny'));
    if (str(sel.style)) {
      out.push(recordCrumb(recordName(`style:${sel.style}`), null, `style:${sel.style}`));
    }
  } else if (surface === 'proportions') {
    out.push(here('surface-proportions'));
    if (str(sel.pack)) out.push(recordCrumb(recordName(`pack:${sel.pack}`), null, `pack:${sel.pack}`));
  } else if (surface === 'faults') {
    out.push(here('surface-faults'));
    if (str(sel.fault)) out.push(recordCrumb(recordName(`fault:${sel.fault}`), null, `fault:${sel.fault}`));
  } else if (surface === 'glossary') {
    out.push(here('surface-glossary'));
    if (str(sel.term)) {
      const c = termCrumb(lookup, sel.term, null);
      out.push({ ...c, cite: `term:${sel.term}` });
    }
  } else {
    // a house step, or Trace a drawing: its surface's own record
    out.push(here(`surface-${surface}`));
  }

  const last = out[out.length - 1];
  out[out.length - 1] = { ...last, href: null };
  return out;
}

/* A crumb's words, or `noEntry(id)` where the glossary holds no record for it. */
export function crumbLabel(c) {
  if (!isObj(c)) return '';
  if (str(c.label)) return c.label;
  return c.missing ? noEntry(c.missing) : '';
}

/* The tab title: the place first, then each crumb above it, then the product's name — or the
   product's name alone on the front door. Null while the glossary has not answered, so the
   caller leaves the page's own title in place rather than writing a title of missing words. */
export function titleFor(crumbs, lookup) {
  if (!lookup || typeof lookup.term !== 'function') return null;
  const about = wordFor(lookup, 'about-tdl');
  const product = about.label || noEntry('about-tdl');
  const parts = (Array.isArray(crumbs) ? crumbs : []).filter((c) => isObj(c) && !c.group)
    .map(crumbLabel).filter(Boolean).reverse();
  return parts.length ? `${parts.join(' · ')} — ${product}` : product;
}
