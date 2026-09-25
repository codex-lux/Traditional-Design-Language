/* A CITATION'S NAME, READ OFF THE SEARCH INDEX AND NEVER MADE UP (WP-14.6).

   The workbench writes machine ids where the corpus serves names: `trim-classical` where the record
   says *Trim — classical*, `tidewater-georgian` where it says *Tidewater Georgian*. `nameFor(cite,
   entries)` is the one reader that turns a citation into what a person calls the thing, over the
   entries `/api/search/index` already serves — every one of which carries a `cite` in the grammar
   and a `name` from its own record — so no surface has to hold a table of names of its own.

   IT NEVER INVENTS A NAME. A cite the index does not hold comes back as ITSELF with
   `resolved: false`, so the reader sees the machine id and can tell it is one. A plausible-looking
   name made from the id (`tidewater-georgian` → "Tidewater Georgian") would be right often enough to
   be trusted and wrong exactly where it matters — a deprecated id, a typo, a record another branch
   added — and would read as the corpus's word when it is the app's guess.

   THE GRAMMAR IS READ, NOT RE-SPELLED. `parseCite` in `../citations.js` is one of the three
   spellings the corpus allows (`test_grammar_agreement.py` holds them together); this file uses it
   and carries no pattern of its own, because a fourth copy is how the grammar came to disagree
   with itself about a dot.

   Four rules, in order, and each says which it used in `via`:

   1. EXACT — the index holds this cite: the entry's name, its id as the margin note.
   2. A `constraint:` cite — the index holds no constraints, and a constraint id is its style's id,
      a dot, and a suffix (660 of 660 at the PRD's measurement; `citations.py` validates the kind
      against the ids carried on the style records). The name is the STYLE's; the note is the
      constraint id, so a reader is never told a constraint is called "Tidewater Georgian".
      The style is `constraintStyleOf`'s, imported from `../citations.js` — the rule `routeCite`
      routes the same cite by. This file carried its own copy of it until WP-14.12, when the
      routing side settled; one rule, one spelling. An id with no dot names no style and is left
      bare.
   3. A `kit:` cite — the grammar's `kit` id is a style id (`citations.py` validates it against the
      style registry, and `routeCite` reads it as `{style}`), so it takes that style's name; the
      note is the id and its fragment.
   4. Any other cite with a FRAGMENT whose base (`kind:id`) the index holds — `style:craftsman#lineage`
      — takes the record's name, and the note carries the fragment. The fragment is a part of the
      record, never the record's name.

   Pure, imports nothing but the grammar and its constraint rule. `names/useNames.js` (WP-14.8) is its React hook. */
import { parseCite, constraintStyleOf } from '../citations.js';

const INDEXES = new WeakMap();

const isName = (v) => typeof v === 'string' && v.trim().length > 0;

/* entries (an array), the served payload ({entries}), or an index this file built → Map cite→entry.
   Built once per array and cached, so a page naming a hundred links reads a Map a hundred times
   rather than scanning seven hundred entries each time. */
export function nameIndex(source) {
  if (source instanceof Map) return source;
  const entries = Array.isArray(source)
    ? source
    : (source && typeof source === 'object' && Array.isArray(source.entries) ? source.entries : null);
  if (!entries) return new Map();
  const cached = INDEXES.get(entries);
  if (cached) return cached;
  const index = new Map();
  for (const e of entries) {
    if (e && typeof e === 'object' && typeof e.cite === 'string' && !index.has(e.cite)) {
      index.set(e.cite, e);
    }
  }
  INDEXES.set(entries, index);
  return index;
}

function bare(cite) {
  return { name: cite == null ? '' : String(cite), note: null, resolved: false, via: null };
}

function named(entry, note, via) {
  return { name: entry.name.trim(), note, resolved: true, via };
}

/* cite → { name, note, resolved, via }. */
export function nameFor(cite, source) {
  const c = parseCite(typeof cite === 'string' ? cite : '');
  if (!c) return bare(cite);
  const index = nameIndex(source);

  const exact = index.get(cite);
  if (exact && isName(exact.name)) {
    return named(exact, typeof exact.id === 'string' && exact.id ? exact.id : c.id, 'exact');
  }

  if (c.kind === 'constraint') {
    const styleId = constraintStyleOf(c.id);
    if (!styleId) return bare(cite);
    const style = index.get('style:' + styleId);
    return style && isName(style.name) ? named(style, c.id, 'style-of-constraint') : bare(cite);
  }

  const withFragment = c.fragment ? `${c.id}#${c.fragment}` : c.id;

  if (c.kind === 'kit') {
    const style = index.get('style:' + c.id);
    return style && isName(style.name) ? named(style, withFragment, 'style-of-kit') : bare(cite);
  }

  if (c.fragment) {
    const base = index.get(`${c.kind}:${c.id}`);
    if (base && isName(base.name)) return named(base, withFragment, 'record-of-fragment');
  }
  return bare(cite);
}
