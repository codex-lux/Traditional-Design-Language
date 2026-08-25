/* The instrument's fixed frame: masthead, the 236px left rail, the vocabulary filter
   strip. Ported from the mockup; the counts stop being literals and come from
   /api/overview, and the surfaces not yet built stay listed as forthcoming rather
   than hidden — the corpus's own honesty rule applies to the interface too. */
import React from 'react';
import { Eyebrow } from './components/Eyebrow.jsx';
import { Icon } from './components/Icon.jsx';

export function surfaces(counts) {
  const c = counts || {};
  return [
    { group: 'explore', items: [
      { id: 'phylogeny', n: '②', label: 'The Phylogeny', meta: c.styles ? `${c.styles} taxa` : '' },
      { id: 'style', n: '③', label: 'Style Record', meta: '9 sections' },
      { id: 'kit', n: '④', label: 'The Kit', meta: c.element_slots ? `${c.element_slots} slots` : '' },
      { id: 'faults', n: '⑨', label: 'Fault Corpus', meta: c.faults ? `${c.faults} solecisms` : '' },
      { id: 'proportions', n: '⑩', label: 'Proportions', meta: '36 packs' },
    ] },
    { group: 'compose', items: [
      { id: 'brief', n: '⑤', label: 'Brief Intake', meta: '' },
      { id: 'candidates', n: '⑥', label: 'Candidate Set', meta: '' },
      { id: 'workbench', n: '⑦', label: 'Plan Workbench', meta: '' },
      { id: 'drawings', n: '⑧', label: 'Drawing Set', meta: '5 sheets' },
      { id: 'export', n: '⑧', label: 'Details & Export', meta: 'JSON · SVG' },
    ] },
  ];
}

export function Masthead({ plan, judgment }) {
  return (
    <header style={{ height: 'var(--topbar-h)', flex: 'none', display: 'flex', alignItems: 'center',
      gap: 20, padding: '0 16px', borderBottom: '1px solid var(--rule)', background: 'var(--paper)' }}>
      <div style={{ font: 'var(--fw-med) 13px/1 var(--serif)', letterSpacing: '.3em',
        textTransform: 'uppercase', color: 'var(--ink)', whiteSpace: 'nowrap' }}>
        Traditional&#183;Design&#183;Language
      </div>
      <span style={{ width: 1, height: 22, background: 'var(--rule)' }} />
      <Eyebrow tone="secondary" as="span">the workbench</Eyebrow>
      <div style={{ flex: 1 }} />
      {plan && <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>{plan.id}</span>}
      {plan && <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{plan.style}</span>}
      {judgment != null && (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, font: 'var(--type-data-s)',
          color: 'var(--ink-3)' }}
          title="constraints the corpus could not evaluate on this plan — unjudged is not passed">
          <span aria-hidden="true" style={{ width: 10, height: 10, border: '1px solid var(--judge-unjudged)',
            backgroundImage: 'var(--hatch-unjudged)' }} />
          {judgment} unjudged
        </span>
      )}
      <span style={{ color: 'var(--ink-3)', display: 'inline-flex', gap: 12 }}>
        <Icon name="file-down" title="Export" /><Icon name="settings-2" title="Settings" />
      </span>
    </header>
  );
}

export function LeftRail({ current, onGo, counts }) {
  const inventory = counts ? [
    ['styles', counts.styles],
    ['lineage edges', counts.lineage_edges],
    ['element slots', counts.element_slots],
    ['massings', counts.massings],
    ['rooms', counts.rooms],
    ['faults', counts.faults],
    ['image records', counts.image_records],
  ] : [];
  return (
    <nav style={{ width: 'var(--rail-left)', flex: 'none', borderRight: '1px solid var(--rule)',
      background: 'var(--paper)', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div style={{ flex: 1, overflow: 'auto', padding: '14px 0' }}>
        {surfaces(counts).map((g) => (
          <div key={g.group} style={{ marginBottom: 18 }}>
            <Eyebrow style={{ padding: '0 14px 8px' }}>{g.group}</Eyebrow>
            {g.items.map((it) => {
              const on = current === it.id;
              return (
                <button key={it.id} type="button" disabled={it.off}
                  onClick={it.off ? undefined : () => onGo(it.id)}
                  style={{ display: 'flex', alignItems: 'baseline', gap: 9, width: '100%', textAlign: 'left',
                    padding: '4px 14px', minHeight: 28, cursor: it.off ? 'default' : 'pointer',
                    background: on ? 'var(--paper-deep)' : 'transparent',
                    borderLeft: on ? '2px solid var(--gilt-deep)' : '2px solid transparent',
                    transition: 'var(--t-hover)' }}>
                  <span style={{ font: 'var(--type-data-s)', color: it.off ? 'var(--ink-4)' : 'var(--ink-3)',
                    width: 12, flex: 'none' }}>{it.n}</span>
                  <span style={{ font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 13px/1.4 var(--body)',
                    color: it.off ? 'var(--text-disabled)' : (on ? 'var(--ink)' : 'var(--ink-2)'), flex: 1 }}>{it.label}</span>
                  <span style={{ font: 'var(--type-data-s)',
                    color: it.off ? 'var(--forthcoming)' : 'var(--ink-4)' }}>{it.meta}</span>
                </button>
              );
            })}
          </div>
        ))}
      </div>
      <div style={{ flex: 'none', borderTop: '1px solid var(--rule)', padding: '11px 14px 13px' }}>
        <Eyebrow style={{ marginBottom: 7 }}>corpus</Eyebrow>
        {inventory.map((r) => (
          <div key={r[0]} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, padding: '1px 0' }}>
            <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>{r[0]}</span>
            <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>{r[1]}</span>
          </div>
        ))}
      </div>
    </nav>
  );
}

export function FilterStrip({ children, right }) {
  return (
    <div style={{ height: 'var(--substrip-h)', flex: 'none', display: 'flex', alignItems: 'center',
      gap: 14, padding: '0 14px', borderBottom: '1px solid var(--rule)', background: 'var(--paper)',
      overflowX: 'auto', overflowY: 'hidden', scrollbarWidth: 'thin' }}>
      {children}
      <div style={{ flex: 1, minWidth: 14 }} />
      {right}
    </div>
  );
}

export function Chip({ on, onClick, children, tone, title }) {
  return (
    <button type="button" onClick={onClick} title={title}
      style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
        border: '1px solid ' + (on ? (tone || 'var(--gilt-deep)') : 'var(--rule)'),
        color: on ? (tone || 'var(--gilt-deep)') : 'var(--ink-3)',
        background: on ? 'var(--paper-deep)' : 'transparent', transition: 'var(--t-hover)' }}>{children}</button>
  );
}

export function SurfaceHead({ eyebrow, title, note, right }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 24,
      padding: '18px 22px 14px', borderBottom: '1px solid var(--rule)' }}>
      <div>
        <Eyebrow>{eyebrow}</Eyebrow>
        <h2 style={{ font: 'var(--fw-reg) var(--fs-d2)/1.1 var(--display)', fontVariationSettings: '"opsz" 72',
          letterSpacing: 'var(--tr-display)', color: 'var(--ink)', margin: '7px 0 0' }}>{title}</h2>
        {note && <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-3)',
          margin: '8px 0 0', maxWidth: '78ch' }}>{note}</p>}
      </div>
      {right}
    </div>
  );
}
