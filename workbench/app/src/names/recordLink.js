/* WHAT A LINK TO A RECORD SAYS AND WHERE IT GOES, WITHOUT REACT (WP-14.8, PRD §I.3).

   `components/RecordLink.jsx` draws a citation as a link: the record's NAME first, in the
   serif, and its id beside it as a Courier margin note — because `trim-classical` is what the
   machine calls a pack and not what a practitioner does. This is the part of it that decides,
   as two pure functions, so every case is driven under `node --test`:

     linkView(cite, ctx, index)  → { href, name, note, resolved }
     isPlainPrimaryClick(ev)     → whether a click is the app's to handle

   THE ADDRESS IS THE ROUTER'S (`hrefFor`, which is `routeCite` then `withContext` then
   `formatHash`) and the NAME is the search index's (`nameFor`): no pattern, no table and no
   guess here. A citation `routeCite` cannot read has no address, and the link is then plain
   text carrying `data-unresolved` rather than an anchor to nowhere — a dead link that looks
   live is worse than a word that says it is not a link. A citation the index does not name
   shows ITSELF, never a name made up from its id (`names.js` says why). */
import { hrefFor } from '../router.js';
import { nameFor } from './names.js';

export function linkView(cite, ctx, index) {
  const href = typeof cite === 'string' ? hrefFor(cite, ctx) : null;
  const n = nameFor(cite, index || []);
  return {
    href,
    name: n.name,
    // The id as a margin note — only where there is a name for it to annotate. A citation shown
    // as itself needs no second copy of itself beside it.
    note: n.resolved && n.note && n.note !== n.name ? n.note : null,
    resolved: n.resolved,
  };
}

/* A plain primary click navigates inside the app (nav.cite, so the context carry and the
   history entry are the router's). A modified or non-primary click — open in a new tab, a
   middle click, a shift-click — is the browser's, and the anchor's real href is what makes
   that work, which is why the link is an anchor at all. */
export function isPlainPrimaryClick(ev) {
  return Boolean(ev) && ev.button === 0 && !ev.defaultPrevented
    && !ev.metaKey && !ev.ctrlKey && !ev.shiftKey && !ev.altKey;
}
