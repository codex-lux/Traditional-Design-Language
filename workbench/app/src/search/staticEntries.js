/* The things the palette can reach that are not corpus records: the surfaces themselves,
   and a few acts.

   The synonyms are the point. Somebody looking for the fault corpus types "errors",
   "mistakes", "problems", "solecisms" — the corpus's own word — or "faults". A palette
   that only answers to the label on the rail is a palette that only helps people who
   already know where things are, which is the opposite of the need.

   Rail tools are deliberately not indexed here (WP-5.6 ruling): the rail is a
   conversation, not a menu, and an entry that pre-fills a prompt would suggest otherwise. */

export const SURFACE_ENTRIES = [
  {
    kind: 'surface', id: 'phylogeny', name: 'The Phylogeny', surface: 'phylogeny',
    meta: 'lineage', short: 'Every style on a time axis, with what descends from what.',
    hay: 'the phylogeny phylogeny lineage descent ancestry tree family graph taxa taxonomy '
       + 'evolution origins time axis map geography where styles came from',
  },
  {
    kind: 'surface', id: 'style', name: 'Style Record', surface: 'style',
    meta: '9 sections', short: 'One style in full: tells, constraints, sources, exemplars.',
    hay: 'style record styles record full record tells diagnostic constraints sources '
       + 'exemplars characteristics period geography',
  },
  {
    kind: 'surface', id: 'kit', name: 'The Kit', surface: 'kit',
    meta: 'slots', short: 'What a style specifies, slot by slot, and where each binding came from.',
    hay: 'the kit kit slots elements bindings cascade inheritance specified forbidden '
       + 'open extends provenance parts vocabulary',
  },
  {
    kind: 'surface', id: 'faults', name: 'Fault Corpus', surface: 'faults',
    meta: 'solecisms', short: 'The named errors — things that read as wrong to someone fluent.',
    hay: 'fault corpus faults solecisms errors mistakes problems wrong bad practice '
       + 'anti-patterns diagnosis what not to do',
  },
  {
    kind: 'surface', id: 'proportions', name: 'Proportions', surface: 'proportions',
    meta: 'packs', short: 'The proportioning systems: modules, orders, trim and opening families.',
    hay: 'proportions proportion packs modules orders classical ratios dimensions rules '
       + 'measure geometry column diameter entablature',
  },
  {
    kind: 'surface', id: 'brief', name: 'Brief Intake', surface: 'brief',
    meta: 'start here', short: 'State the brief: rooms, site, budget, what the house is for.',
    hay: 'brief intake new start begin requirements program rooms wanted site budget '
       + 'client wishes commission',
  },
  {
    kind: 'surface', id: 'candidates', name: 'Candidate Set', surface: 'candidates',
    meta: 'compose', short: 'What the composer proposed for the brief, ranked and criticised.',
    hay: 'candidate set candidates options proposals compose composed results ranked '
       + 'alternatives schemes',
  },
  {
    kind: 'surface', id: 'workbench', name: 'Plan Workbench', surface: 'workbench',
    meta: 'the bench', short: 'The plan itself: place rooms, solve, and read the critique.',
    hay: 'plan workbench bench plan drawing rooms layout solve placement geometry '
       + 'critique findings edit the plan floor plan',
  },
  {
    kind: 'surface', id: 'drawings', name: 'Drawing Set', surface: 'drawings',
    meta: '5 sheets', short: 'Plan, elevation, section, bearing and roof, drawn from the record.',
    hay: 'drawing set drawings sheets elevation section roof bearing plate print draw',
  },
  {
    kind: 'surface', id: 'export', name: 'Details & Export', surface: 'export',
    meta: 'JSON · SVG · DXF · IFC', short: 'Take the work out: JSON, SVG, DXF, IFC.',
    hay: 'details export download save out json svg dxf ifc cad bim autocad revit '
       + 'file take out',
  },
  {
    kind: 'surface', id: 'transcription', name: 'Transcription', surface: 'transcription',
    meta: 'drawing → record', short: 'Bring a drawing in and turn it into a plan record.',
    hay: 'transcription transcribe ingest import bring in drawing to record trace '
       + 'digitise digitize scan upload dxf in',
  },
];

/* Acts, not places. Each carries a `run` name the palette resolves against handlers the
   shell passes in, so this file stays free of imports and testable on its own. */
export const ACTION_ENTRIES = [
  {
    kind: 'action', id: 'help', name: 'Keyboard shortcuts and the citation grammar',
    run: 'help', meta: '?', hay: 'help shortcuts keys keyboard hotkeys commands citation '
      + 'grammar how do i what can i type question mark',
  },
];

export const STATIC_ENTRIES = [...SURFACE_ENTRIES, ...ACTION_ENTRIES];
