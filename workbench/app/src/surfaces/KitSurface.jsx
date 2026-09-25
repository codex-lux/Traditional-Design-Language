/* The Kit — every element slot in 8 groups resolved through the cascade, with the source column
   showing which ancestor supplied each value. The cascade is a first-class object with its own
   display.

   EMBEDDED SINCE WP-14.12: it is the dossier's kit section (`#/style/<id>/kit/<slot>`), not a
   surface of its own, and `#/kit/...` is an alias the router rewrites. What that changed:

   - The style is the DOSSIER's, handed in. There is no default style: a surface that opened
     Tidewater Georgian when the URL named none was a surface whose address and whose screen could
     disagree, and a bare `#/style` is the Styles index now, which never shows a record.
   - The open slot is the URL's (`selection.slot`), so opening one writes an address that can be
     cited and handed on; a slot the URL names that this kit does not list SAYS so, rather than
     opening nothing in silence.
   - The side panel's proportion packs and massing affinities left for the dossier's Proportions
     and Plan types sections, which draw them in full; the cascade ladder stays, because the
     source column is read against it.
   - "A thin kit is correct, not incomplete" is the `thin-kit` glossary record's definition,
     rendered live, and the strip's shown and bound figures are `/api/kit`'s, published as data
     attributes so the walk holds them to that endpoint. */
import React from 'react';
import { api } from '../api/client.js';
import { SlotRow } from '../components/SlotRow.jsx';
import { ProvenanceTrace } from '../components/ProvenanceTrace.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { FilterStrip, Chip, ChipGroup, FilterGroup } from '../Chrome.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { matches } from '../search/match.js';
import { cascadeRows as ladderRows } from '../dossier/relations.js';

/* resolve_kit rows → SlotRow props. Source strings become {distance, id}; the
   "a + b (extends)" composite renders as the base ancestor plus a marker. */
function adaptRow(row, distances) {
  let source = null;
  if (row.source) {
    const base = row.source.split(' + ')[0];
    const composite = row.source.includes('(extends)');
    source = { id: composite ? base + ' +ext' : row.source, distance: distances[base] ?? '?' };
  }
  const params = row.parameters && typeof row.parameters === 'object'
    ? Object.entries(row.parameters).map(([name, p]) => ({
        name,
        value: p.value !== undefined ? String(p.value)
          : (p.range ? `${p.range[0]}–${p.range[1]}` : ''),
        unit: p.unit, kind: p.kind,
      }))
    : null;
  const variants = row.variants
    ? row.variants.map((v) => ({ name: v.name || v.id, status: v.status, note: v.note }))
    : [
        ...(row.canonical || []).map((id) => ({ name: id, status: 'canonical' })),
        ...(row.forbidden || []).map((id) => ({ name: id, status: 'forbidden' })),
      ];
  return {
    id: row.slot, group: row.group, binding: row.binding, source,
    rule: row.rule, note: row.note,
    parameters: params,
    variants: variants.length ? variants : null,
    // SlotRow renders each pack entry directly as a child — strings, not objects
    // (an object here white-screened the whole app on the default style's kit)
    packs: row.packs
      ? row.packs.map((p) => `${p.pack} · precedence ${p.precedence}`)
      : null,
    faults: row.faults || null,
    judgment: row.judgment, invented: row.invented, code_conflict: row.code_conflict,
  };
}

const KIT_SPEC = { group: {}, q: { type: 'text' }, all: { widens: true, type: 'bool' } };

export function KitSurface({ styleId, onCite, selection, setSelection }) {
  const [kit, setKit] = React.useState(null);
  const [cascade, setCascade] = React.useState(null);
  const openSlot = selection?.slot || null;
  const [detail, setDetail] = React.useState({});   // slot id → full record (+faults)
  const [source, setSource] = React.useState(null);
  const [groups, setGroups] = React.useState([]);
  const [counts, setCounts] = React.useState(null);
  const glossary = useGlossary();
  const thin = termView(glossary, { id: 'thin-kit' });

  const filters = useSurfaceFilters(KIT_SPEC);
  const { group, q } = filters.values;
  // The URL says `all`; the fetch wants its opposite. Stated this way round because
  // "show me everything" is the deliberate act and belongs in the link.
  const specifiedOnly = !filters.values.all;

  React.useEffect(() => {
    api.overview().then((o) => { setGroups(o.slot_groups || []); setCounts(o.counts || null); });
  }, []);

  /* The URL owns the open slot and the dossier owns the style, so neither is held here: an ABSENT
     slot is no slot open, never the last one. (Guarding a sync with `if (selection?.x)` once left
     the last record on screen after Back -- the address and the screen disagreeing, which is the
     one thing the router exists to prevent. Found by an adversarial audit; it cannot recur when
     there is no copy to sync.) */
  React.useEffect(() => {
    setKit(null); setCascade(null);
    api.kit(styleId, { only_specified: specifiedOnly }).then(setKit).catch(() => setKit(null));
    api.cascade(styleId).then(setCascade).catch(() => setCascade(null));
  }, [styleId, specifiedOnly]);

  React.useEffect(() => {
    const key = `${styleId}:${openSlot}`;   // keyed by style too — a style switch
    if (!openSlot || detail[key]) return;   // must never serve the old style's record
    Promise.all([
      fetch(`/api/kit/${styleId}/slot/${openSlot}`).then((r) => (r.ok ? r.json() : null)),
      api.faults({ slot: openSlot, style: styleId, limit: 8 }).catch(() => null),
    ]).then(([d, fl]) => {
      if (d) setDetail((prev) => ({ ...prev, [key]: {
        ...d,
        // SlotRow reads fl.id and fl.name per fault — keep both
        faults: (fl?.faults || []).map((f) => ({ id: f.id, name: f.name })),
      } }));
    });
  }, [openSlot, styleId]);

  const distances = {};
  (cascade?.cascade || []).forEach((r) => { distances[r.id] = r.distance; });
  const rows = (kit?.slots || [])
    .filter((s) => !group || s.group === group)
    .filter((s) => matches(s, q, ['slot', 'group', 'name', 'binding', 'source', 'value']))
    .map((s) => {
      const d = detail[`${styleId}:${s.slot}`];
      return adaptRow(d ? { ...s, ...d } : s, distances);
    });

  const cascadeRows = ladderRows(cascade);
  const inKit = !openSlot || !kit || (kit.slots || []).some((s) => s.slot === openSlot);
  const openSlotTo = (id) => setSelection && setSelection({ slot: id || null });

  return (
    <div data-dossier-section="kit" data-kit-style={styleId}
      style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip filters={filters} right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Chip on={specifiedOnly} onClick={() => filters.set('all', specifiedOnly)}>specified only</Chip>
          <span data-kit-shown={kit ? rows.length : undefined}
            data-kit-returned={kit ? kit.slots_returned : undefined}
            data-kit-total={kit ? kit.slots_total : undefined}
            style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
            {/* The slot count was the literal 95 while the ontology held 97, and main's
                fallback still carries a 97. A number typed into a view goes stale the day
                the corpus moves, so the total comes from the payload that knows it
                (`slots_total`, added on main) and failing that from /api/overview — never
                from a literal. */}
            {kit
              ? `${rows.length} of ${kit.slots_total ?? (counts ? counts.element_slots : kit.slots_returned)} `
                + `slots ${specifiedOnly ? 'bound' : 'shown'}`
              : '…'}
          </span>
        </span>
      }>
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={rows.length}
          label="Filter these slots by name, group, binding or source"
          placeholder="filter slots" width={170} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        {/* Eight groups is a lot of chips to hold open when most visits steer by one.
            Folded by default — open, they pushed the count and the specified-only toggle
            off the right-hand edge of the strip, which is how a bar of filters starts
            hiding the things it is supposed to be reporting. */}
        <FilterGroup label="slot group" active={group ? 1 : 0} summary={group || 'all 8'}>
          <ChipGroup label="slot group">
            {groups.map((g) => (
              <Chip key={g.id} radio on={group === g.id}
                onClick={() => filters.toggle('group', g.id)}>{g.id} {g.count}</Chip>
            ))}
          </ChipGroup>
        </FilterGroup>
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ width: 280, flex: 'none', borderRight: '1px solid var(--rule)', overflow: 'auto',
          padding: '14px 12px 22px' }}>
          <Eyebrow style={{ marginBottom: 8 }}>
            <Term id="cascade" />{cascade ? ` · ${cascade.levels}` : ''}
          </Eyebrow>
          {cascadeRows.length > 0 && (
            <ProvenanceTrace cascade={cascadeRows} sourceId={source} collapseFrom={7}
              onSelect={(x) => { setSource(x); onCite && onCite('style:' + x); }} />
          )}
        </div>

        <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
          {!inKit && (
            <p data-slot-absent={openSlot} style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)',
              margin: 0, padding: '10px 12px', borderBottom: '1px solid var(--rule)', background: 'var(--paper-deep)' }}>
              <RecordLink cite={'slot:' + openSlot} /> is not among the slots this kit lists
              {specifiedOnly ? ' as bound — “specified only” is on' : ''}
            </p>
          )}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, padding: '10px 10px 8px',
            borderBottom: '1px solid var(--rule)', position: 'sticky', top: 0, background: 'var(--paper)', zIndex: 1 }}>
            <Eyebrow as="span" style={{ width: 132, flex: 'none' }}>group</Eyebrow>
            <Eyebrow as="span" style={{ flex: 1 }}>slot</Eyebrow>
            <Eyebrow as="span" style={{ width: 74, flex: 'none' }}>binding</Eyebrow>
            <Eyebrow as="span" style={{ width: 190, flex: 'none' }}>source</Eyebrow>
            <Eyebrow as="span" style={{ width: 52, flex: 'none', textAlign: 'right' }}>faults</Eyebrow>
          </div>
          {rows.map((s) => (
            <SlotRow key={s.id} slot={s} expanded={openSlot === s.id}
              onToggle={() => openSlotTo(openSlot === s.id ? null : s.id)}
              onSource={(x) => setSource(x)}
              onFault={(x) => onCite && onCite('fault:' + x)} />
          ))}
          <div style={{ padding: '14px 12px 26px', maxWidth: '72ch' }}>
            <Eyebrow style={{ marginBottom: 5 }}><Term id="thin-kit" /></Eyebrow>
            {thin.state === 'ready' && (
              <p data-term-definition="thin-kit"
                style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-2)', margin: 0 }}>
                {thin.definition}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
