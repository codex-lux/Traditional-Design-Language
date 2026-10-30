/* WHAT THE SIDEBAR DRAWS, OUT OF THE SITE MAP (Phase 17, WP-17.2).

   `navModel` is still the one account of the places (ids, records, counts); this file decides
   only which of them the redrawn sidebar shows, and in what shape (docs/ui-redesign-2026-10-29.md,
   "The shell"):

     home       the front door, drawn as the wordmark, which is the way home
     house      the house on the bench: its five steps as stations, each with the journey's mark,
                state words and whether it is blocked (`journey/bar.js` decides that, not here),
                tracing a drawing joining at the plan as it always has
     library    five rows: Styles, then the library's own four. Styles' own places (the style in
                hand, the family tree, a dossier's sections) are its sub-rows, and are shown only
                while the reader is in that section, so the sidebar is short where it is a map and
                long only where the reader already is
     compact    on a library page the five stations shrink to five marks in a row; the house is
                still there, and still a link

   `drawnItems(view)` is every place the sidebar draws as a link, in order, which is what the
   browser walk holds the rendered anchors to. A blocked step is drawn as words and is not a link
   (the journey bar's rule since WP-14.10), so it is not among them. Pure: no React. */
import { stations } from '../journey/spine.js';

const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const STYLES_SURFACES = new Set(['style', 'phylogeny', 'compare']);
const HOUSE_SURFACES = new Set(['brief', 'candidates', 'workbench', 'transcription', 'drawings', 'export']);

export function sidebarView(model, { bar = null, resume = null, surface = null } = {}) {
  const groups = isObj(model) && Array.isArray(model.groups) ? model.groups : [];
  const group = (id) => groups.find((g) => g.id === id) || null;
  const start = group('start'), styles = group('styles'), house = group('a-house'), library = group('library');
  const home = start && start.items.find((i) => i.id === 'overview') || null;

  const marked = stations(bar, resume);
  const byHref = new Map(marked.map((s) => [s.href, s]));
  const houseItems = (house ? house.items : []).map((it) => {
    const st = byHref.get(it.href) || null;
    return {
      ...it,
      station: st,
      mark: st ? st.mark : null,
      blocked: Boolean(st && !st.link),
      // the alternate (tracing a drawing) joins at the plan and is never blocked
      children: it.children || [],
    };
  });

  const stylesItem = styles ? styles.items.find((i) => i.id === 'style') : null;
  const stylesOpen = STYLES_SURFACES.has(surface)
    || Boolean(styles && styles.items.some((i) => i.current || (i.children || []).some((c) => c.current)));
  const stylesRow = stylesItem ? {
    ...stylesItem,
    // the style in hand, the family tree, and whatever children each carries
    children: stylesOpen ? styles.items.filter((i) => i.id !== 'style') : [],
  } : null;

  return {
    home,
    house: { group: house, items: houseItems },
    library: { group: library, rows: [stylesRow, ...(library ? library.items : [])].filter(Boolean) },
    compact: surface !== null && surface !== 'overview' && !HOUSE_SURFACES.has(surface),
    stylesOpen,
  };
}

/* Every place drawn as a link, in the order the sidebar draws it. */
export function drawnItems(view) {
  const out = [];
  const walk = (items, skipBlocked) => items.forEach((it) => {
    if (!(skipBlocked && it.blocked)) out.push(it);
    walk(it.children || [], false);
  });
  if (view && view.home) out.push(view.home);
  if (view) walk(view.house.items, true);
  if (view) walk(view.library.rows, false);
  return out;
}
