/* Surface ④ — the Kit, live. 95 slots in 8 groups resolved through the cascade, with
   the source column showing which ancestor supplied each value. The cascade is a
   first-class object with its own display; a thin kit is correct, not incomplete. */
import React from 'react';
import { api } from '../api/client.js';
import { SlotRow } from '../components/SlotRow.jsx';
import { ProvenanceTrace } from '../components/ProvenanceTrace.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

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
    packs: row.packs ? row.packs.map((p) => ({ id: p.pack, role: p.note ? 'governs' : '',
      prec: p.precedence })) : null,
    faults: row.faults || null,
    judgment: row.judgment, invented: row.invented, code_conflict: row.code_conflict,
  };
}

export function KitSurface({ onCite, selection }) {
  const [styleId, setStyleId] = React.useState(selection?.style || 'tidewater-georgian');
  const [styleOptions, setStyleOptions] = React.useState([]);
  const [kit, setKit] = React.useState(null);
  const [cascade, setCascade] = React.useState(null);
  const [styleInfo, setStyleInfo] = React.useState(null);
  const [group, setGroup] = React.useState(null);
  const [specifiedOnly, setSpecifiedOnly] = React.useState(true);
  const [openSlot, setOpenSlot] = React.useState(selection?.slot || null);
  const [detail, setDetail] = React.useState({});   // slot id → full record (+faults)
  const [source, setSource] = React.useState(null);
  const [groups, setGroups] = React.useState([]);

  React.useEffect(() => {
    api.overview().then((o) => setGroups(o.slot_groups || []));
    api.styles({ limit: 200 }).then((r) => setStyleOptions((r.results || []).map((s) => s.id).sort()));
  }, []);

  React.useEffect(() => {
    if (selection?.style) setStyleId(selection.style);
    if (selection?.slot) setOpenSlot(selection.slot);
  }, [selection?.style, selection?.slot]);

  React.useEffect(() => {
    setKit(null); setCascade(null);
    api.kit(styleId, { only_specified: specifiedOnly }).then(setKit).catch(() => setKit(null));
    api.cascade(styleId).then(setCascade).catch(() => setCascade(null));
    api.style(styleId, 'summary,massing,proportion').then(setStyleInfo).catch(() => setStyleInfo(null));
  }, [styleId, specifiedOnly]);

  React.useEffect(() => {
    if (!openSlot || detail[openSlot]) return;
    Promise.all([
      fetch(`/api/kit/${styleId}/slot/${openSlot}`).then((r) => (r.ok ? r.json() : null)),
      api.faults({ slot: openSlot, style: styleId, limit: 8 }).catch(() => null),
    ]).then(([d, fl]) => {
      if (d) setDetail((prev) => ({ ...prev, [openSlot]: { ...d, faults: (fl?.faults || []).map((f) => f.id) } }));
    });
  }, [openSlot, styleId]);

  const distances = {};
  (cascade?.cascade || []).forEach((r) => { distances[r.id] = r.distance; });
  const rows = (kit?.slots || [])
    .filter((s) => !group || s.group === group)
    .map((s) => adaptRow(detail[s.slot] ? { ...s, ...detail[s.slot] } : s, distances));

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
      <FilterStrip right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Chip on={specifiedOnly} onClick={() => setSpecifiedOnly(!specifiedOnly)}>specified only</Chip>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
            {kit ? `${kit.slots_returned} of 95 slots ${specifiedOnly ? 'bound' : 'shown'}` : '…'}
          </span>
        </span>
      }>
        <Eyebrow as="span">style</Eyebrow>
        <select value={styleId} onChange={(e) => setStyleId(e.target.value)}
          style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', background: 'var(--paper-mat)',
            border: '1px solid var(--rule)', padding: '2px 6px', maxWidth: 210 }}>
          {styleOptions.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span">slot group</Eyebrow>
        {groups.map((g) => (
          <Chip key={g.id} on={group === g.id}
            onClick={() => setGroup(group === g.id ? null : g.id)}>{g.id} {g.count}</Chip>
        ))}
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
                    status={m.affinity} title={m.note} />
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
