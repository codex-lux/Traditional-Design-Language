/* Surface ④ — the Kit, live. Every element slot in 8 groups resolved through the cascade,
   with the source column showing which ancestor supplied each value. The cascade is a
   first-class object with its own display; a thin kit is correct, not incomplete. */
import React from 'react';
import { api } from '../api/client.js';
import { SlotRow } from '../components/SlotRow.jsx';
import { ProvenanceTrace } from '../components/ProvenanceTrace.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip, ChipGroup, FilterGroup } from '../Chrome.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';

const DEFAULT_STYLE = 'tidewater-georgian';

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

export function KitSurface({ onCite, selection, setSelection }) {
  const [styleId, setStyleId] = React.useState(selection?.style || DEFAULT_STYLE);
  const [kit, setKit] = React.useState(null);
  const [cascade, setCascade] = React.useState(null);
  const [styleInfo, setStyleInfo] = React.useState(null);
  const [openSlot, setOpenSlot] = React.useState(selection?.slot || null);
  const [detail, setDetail] = React.useState({});   // slot id → full record (+faults)
  const [source, setSource] = React.useState(null);
  const [groups, setGroups] = React.useState([]);
  const [counts, setCounts] = React.useState(null);

  const filters = useSurfaceFilters(KIT_SPEC);
  const { group, q } = filters.values;
  // The URL says `all`; the fetch wants its opposite. Stated this way round because
  // "show me everything" is the deliberate act and belongs in the link.
  const specifiedOnly = !filters.values.all;

  React.useEffect(() => {
    api.overview().then((o) => { setGroups(o.slot_groups || []); setCounts(o.counts || null); });
  }, []);

  React.useEffect(() => {
/* The URL owns this, so an ABSENT selection must reset to the default rather than leave the
   last one showing. Guarding the sync with `if (selection?.x)` meant pressing Back to a bare
   #/kit left the panel displaying the record you had just left — the address bar and the
   screen disagreeing, which is the one thing the router exists to prevent. Found by an
   adversarial audit. */
    setStyleId(selection?.style || DEFAULT_STYLE);
    setOpenSlot(selection?.slot || null);
  }, [selection?.style, selection?.slot]);

  React.useEffect(() => {
    setKit(null); setCascade(null);
    api.kit(styleId, { only_specified: specifiedOnly }).then(setKit).catch(() => setKit(null));
    api.cascade(styleId).then(setCascade).catch(() => setCascade(null));
    api.style(styleId, 'summary,massing,proportion').then(setStyleInfo).catch(() => setStyleInfo(null));
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

  const cascadeRows = (cascade?.cascade || []).map((r) => ({
    distance: r.distance, id: r.id,
    bindings: r.specified + r.extends + r.forbidden,
    detail: [
      r.specified ? `${r.specified} specified` : null,
      r.extends ? `${r.extends} extends` : null,
      r.forbidden ? `${r.forbidden} forbidden` : null,
    ].filter(Boolean).join(', ') || (r.has_kit ? 'nothing of its own' : 'no kit'),
  }));

  const summary = styleInfo?.summary || {};
  const openCount = (kit?.slots || []).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip filters={filters} right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Chip on={specifiedOnly} onClick={() => filters.set('all', specifiedOnly)}>specified only</Chip>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
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
        <Eyebrow as="span">style</Eyebrow>
        <StylePicker value={styleId} onChange={(v) => {
          setStyleId(v);
          setSelection && setSelection({ style: v, slot: undefined });
        }} label="Which style's kit to resolve" width={210} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
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
        <div style={{ width: 340, flex: 'none', borderRight: '1px solid var(--rule)', overflow: 'auto',
          minHeight: 0, padding: '14px 12px 22px' }}>
          <h2 style={{ font: 'var(--fw-reg) var(--fs-d3)/1.1 var(--display)', fontVariationSettings: '"opsz" 48',
            letterSpacing: 'var(--tr-display)', margin: '0 0 3px' }}>{summary.name || styleId}</h2>
          <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginBottom: 16 }}>
            {styleId}{summary.rank ? ` · ${summary.rank}` : ''}
            {cascade ? ` · ${cascade.levels} levels of cascade` : ''}
          </div>

          {cascadeRows.length > 0 && (
            <ProvenanceTrace cascade={cascadeRows} sourceId={source} collapseFrom={7}
              onSelect={(s) => { setSource(s); onCite && onCite('style:' + s); }} />
          )}

          {(styleInfo?.proportion_packs || []).length > 0 && (
            <div style={{ marginTop: 20 }}>
              <Eyebrow style={{ marginBottom: 8 }}>
                proportion packs · {styleInfo.proportion_packs.length} bound
              </Eyebrow>
              {styleInfo.proportion_packs.map((p) => (
                <div key={p.pack + (p.role || '')} title={p.note}
                  style={{ display: 'flex', gap: 8, alignItems: 'baseline', padding: '3px 0' }}>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink)', width: 128, flex: 'none' }}>{p.pack}</span>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', width: 82, flex: 'none' }}>{p.role}</span>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', flex: 1 }}>{p.authority || ''}</span>
                </div>
              ))}
            </div>
          )}

          {(styleInfo?.massing_affinities || []).length > 0 && (
            <div style={{ marginTop: 20 }}>
              <Eyebrow style={{ marginBottom: 8 }}>massing affinities</Eyebrow>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
                {styleInfo.massing_affinities.map((m) => (
                  <VariantPill key={m.massing} ladder="affinity" name={'massing:' + m.massing}
                    status={m.affinity} note={m.note} />
                ))}
              </div>
              <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '9px 0 0' }}>
                Massing is not style. The
                <span style={{ fontFamily: 'var(--mono)', color: 'var(--ink-2)' }}> massing:</span> prefix
                keeps the two namespaces apart.
              </p>
            </div>
          )}
        </div>

        <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
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
              onToggle={() => setOpenSlot(openSlot === s.id ? null : s.id)}
              onSource={(x) => setSource(x)}
              onFault={(x) => onCite && onCite('fault:' + x)} />
          ))}
          <p style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-3)',
            padding: '14px 12px 26px', margin: 0, maxWidth: '72ch' }}>
            {openCount} slot{openCount === 1 ? '' : 's'} shown. A thin kit is correct, not incomplete:
            a style states only what the cascade does not already give it.
          </p>
        </div>
      </div>
    </div>
  );
}
