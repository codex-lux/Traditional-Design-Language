/* The things the palette can reach that are not corpus records: the places themselves, and a
   few acts.

   THE PLACES ARE THE SITE MAP'S (WP-14.13, PRD §I.12). This file used to keep a third catalogue
   of the workbench's surfaces, with names and one-line descriptions of its own that disagreed
   with the rail's and the Overview's (it called Brief Intake "start here" while the rail's START
   held only the Overview, and had no entry for the Overview at all). The entries are
   `nav/navModel.js`'s items now, in its order, the front door first, each named by its glossary
   record's `term` and described by that record's `surface.what` — so a place is called one thing
   in the rail, the crumbs, the palette and the tab. Before the glossary has answered, a place is
   shown by its record id: the palette never invents a name to fill the gap.

   THE SYNONYMS ARE THE POINT, AND THEY ARE KEPT. Somebody looking for the fault corpus types
   "errors", "mistakes", "problems", "solecisms" — the corpus's own word — or "faults". A palette
   that only answers to the label on the rail is a palette that only helps people who already know
   where things are, which is the opposite of the need. The haystacks below are the words each
   place answers to beyond its name; they are search terms, not descriptions, and nothing shows
   them. The Kit's words (`elements`, `bindings`, …) travel with the kit onto the style's place,
   where PRD §E.1 moves it.

   Rail tools are deliberately not indexed here (WP-5.6 ruling): the rail is a conversation, not
   a menu, and an entry that pre-fills a prompt would suggest otherwise. */
import { NAV, wordFor } from '../nav/navModel.js';
import { noEntry } from '../glossary/termView.js';
import { isMissing } from '../glossary/lookup.js';

/* The words each place answers to beyond its own name, by navModel item id. */
export const SURFACE_SYNONYMS = Object.freeze({
  overview: 'front door home landing welcome about introduction what is this start here begin overview',
  style: 'style record styles record full record tells diagnostic constraints sources '
    + 'exemplars characteristics period geography dossier find a style index '
    + 'the kit kit slots elements bindings cascade inheritance specified forbidden '
    + 'open extends provenance parts vocabulary',
  phylogeny: 'the phylogeny phylogeny lineage descent ancestry tree family graph taxa taxonomy '
    + 'evolution origins time axis map geography where styles came from',
  brief: 'brief intake new start begin requirements program rooms wanted site budget '
    + 'client wishes commission',
  candidates: 'candidate set candidates options proposals compose composed results ranked '
    + 'alternatives schemes',
  workbench: 'plan workbench bench plan drawing rooms layout solve placement geometry '
    + 'critique findings edit the plan floor plan',
  transcription: 'transcription transcribe ingest import bring in drawing to record trace '
    + 'digitise digitize scan upload dxf in',
  drawings: 'drawing set drawings sheets elevation section roof bearing plate print draw '
    + 'in the round model',
  export: 'details export download save out json svg dxf ifc cad bim autocad revit '
    + 'file take out',
  proportions: 'proportions proportion packs modules orders classical ratios dimensions rules '
    + 'measure geometry column diameter entablature',
  faults: 'fault corpus faults solecisms errors mistakes problems wrong bad practice '
    + 'anti-patterns diagnosis what not to do',
  glossary: 'glossary terms definitions define meaning words dictionary what does it mean',
});

function surfaceEntry(it, lookup) {
  const { label, missing } = wordFor(lookup, it.termId);
  const name = label || (missing ? noEntry(missing) : it.termId);
  const rec = lookup && typeof lookup.term === 'function' ? lookup.term(it.termId) : null;
  const what = rec && !isMissing(rec) && rec.surface && typeof rec.surface.what === 'string'
    ? rec.surface.what : undefined;
  return {
    kind: 'surface', id: it.id, surface: it.surface, termId: it.termId, name,
    short: what,
    hay: `${name} ${it.id} ${SURFACE_SYNONYMS[it.id] || ''}`.toLowerCase().trim(),
  };
}

/* The places, in the site map's order, children after their parent. `in-hand` is not a place
   of its own: it is a style, which the index already names. */
export function surfaceEntries(lookup) {
  const out = [];
  for (const g of NAV) {
    for (const it of g.items) {
      if (it.id === 'in-hand') continue;
      out.push(surfaceEntry(it, lookup));
      for (const c of it.children || []) out.push(surfaceEntry(c, lookup));
    }
  }
  return out;
}

/* Acts, not places. Each carries a `run` name the palette resolves against handlers the
   shell passes in, so this file stays testable on its own. */
export const ACTION_ENTRIES = [
  {
    kind: 'action', id: 'help', name: 'Keyboard shortcuts and the citation grammar',
    run: 'help', meta: '?', hay: 'help shortcuts keys keyboard hotkeys commands citation '
      + 'grammar how do i what can i type question mark',
  },
];

/* Everything static, named from the glossary lookup in hand (null while it loads). */
export function staticEntries(lookup) {
  return [...surfaceEntries(lookup), ...ACTION_ENTRIES];
}

/* The same, before any glossary: each place under its record id, every synonym in place. */
export const SURFACE_ENTRIES = surfaceEntries(null);
export const STATIC_ENTRIES = [...SURFACE_ENTRIES, ...ACTION_ENTRIES];
