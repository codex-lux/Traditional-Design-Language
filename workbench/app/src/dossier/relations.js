/* HOW ONE STYLE STANDS TO THE REST, DECIDED WITHOUT REACT (WP-14.12).

   The dossier's relations panel and two of its sections read other records than the style's own,
   and every reading of them is here so each can be driven under `node --test`:

     siblingsOf     the NEIGHBOURS -- the taxa filed under the same parent (`member_of`), in the
                    order a reader meets them. Filing, not lineage: `styles/taxa.js` says why the
                    two are different relations and this reads the one it reads.
     packGroups     `/api/styles/{id}/packs` (§H.3) as the five provenances it serves, never fewer:
                    a pack bound here, opted into, delivered by an ancestor, withheld by the opt-in
                    gate, or declined are five different facts, and a reader asking why a style does
                    not have a pack is answered by the last two.
     splitDelivered the delivered groups, the NEAREST ancestor apart from the farther ones. The
                    farther ones fold behind the reader's own `delivered` choice (`state/prefs.js`),
                    closed until they open it, because a style six steps down a lineage can have
                    thirty packs arriving and the nearest group is the one that explains the rest.
     cascadeRows    `/api/kit/{id}/cascade` as the ladder `ProvenanceTrace` draws -- lifted out of
                    `surfaces/KitSurface.jsx` unchanged, because the lineage section draws the
                    same ladder and two copies of one reading is how they come to disagree.
     benchOf        the plan on the bench, as it bears on this style.

   Pure; imports only the taxonomy's own readers. */
import { compareTaxa } from '../styles/taxa.js';

const list = (v) => (Array.isArray(v) ? v : []);
const named = (v) => typeof v === 'string' && v !== '';

/* The taxa filed under the same parent as `id`, `id` excluded. A root (no `member_of`) has the
   other roots for neighbours; an id the taxa do not hold has none. */
export function siblingsOf(id, taxa) {
  const all = list(taxa).filter((t) => t && named(t.id));
  const self = all.find((t) => t.id === id);
  if (!self) return [];
  const parent = named(self.member_of) ? self.member_of : null;
  return all
    .filter((t) => t.id !== id && (named(t.member_of) ? t.member_of : null) === parent)
    .sort(compareTaxa);
}

/* The packs payload -> its five lists and the total the dossier's strip counts: the sum of the
   five list lengths, delivered counted by pack and not by group (§D.2). */
export function packGroups(payload) {
  const p = payload && typeof payload === 'object' ? payload : {};
  const delivered = list(p.delivered)
    .filter((g) => g && typeof g === 'object')
    .map((g) => ({ ...g, packs: list(g.packs) }))
    .filter((g) => g.packs.length > 0);
  const out = {
    own: list(p.own),
    opted_in: list(p.opted_in),
    delivered,
    withheld: list(p.withheld),
    declined: list(p.declined),
  };
  out.total = out.own.length + out.opted_in.length
    + delivered.reduce((n, g) => n + g.packs.length, 0)
    + out.withheld.length + out.declined.length;
  return out;
}

/* delivered groups (nearest first, as served) -> { near, far }. */
export function splitDelivered(delivered) {
  const groups = list(delivered);
  return { near: groups.length ? groups[0] : null, far: groups.slice(1) };
}

/* Are the farther ancestors' packs shown? Only when the reader opened them: `prefs.fold` answers
   true, false or undefined, and undefined -- never chosen -- is folded. */
export function deliveredOpen(fold) {
  return fold === true;
}

/* The cascade payload -> ProvenanceTrace rows (from `KitSurface.jsx`, unchanged). */
export function cascadeRows(cascade) {
  return list(cascade && cascade.cascade).map((r) => ({
    distance: r.distance, id: r.id,
    bindings: r.specified + r.extends + r.forbidden,
    detail: [
      r.specified ? `${r.specified} specified` : null,
      r.extends ? `${r.extends} extends` : null,
      r.forbidden ? `${r.forbidden} forbidden` : null,
    ].filter(Boolean).join(', ') || (r.has_kit ? 'nothing of its own' : 'no kit'),
  }));
}

/* The plan on the bench -> what the panel says about it: null when there is none; otherwise its
   id, its title where it has one, its style, and whether that style is this one. */
export function benchOf(plan, styleId) {
  if (!plan || typeof plan !== 'object') return null;
  const style = named(plan.style) ? plan.style : null;
  return {
    id: named(plan.id) ? plan.id : null,
    title: named(plan.title) ? plan.title : null,
    style,
    here: style !== null && style === styleId,
  };
}
