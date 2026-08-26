/* The instrument's fixed frame: masthead, the 236px left rail, the vocabulary filter
   strip. Ported from the mockup; the counts stop being literals and come from
   /api/overview. All eleven surfaces are live (⑪ Transcription joined in WP-5.5) — the
   forthcoming-not-hidden treatment lives on the Export surface's cards, where the
   unbuilt work packages are named. */
import React from 'react';
import { Eyebrow } from './components/Eyebrow.jsx';
import { Icon } from './components/Icon.jsx';

/* The rail, grouped by what you are trying to do rather than by the order the surfaces
   were built in.

   The circled numerals are gone. They were work-package numbers — ②③④⑨⑩ then ⑤⑥⑦⑧⑧⑪ —
   so they read as an ordering while meaning build history, sent the eye down a sequence
   that goes 2,3,4,9,10 and then back to 5, and two surfaces both wore ⑧. The docs keep
   the WP numbering, which is where it belongs.

   `output` and `ingest` are split out of what used to be one long `compose` list of six.
   Composing a house and exporting a drawing are different errands, and the Drawing Set
   sitting under "compose" was the reason Export and Drawings kept being confused. */
export function surfaces(counts) {
  const c = counts || {};
  const packs = c.proportion_packs
    ? Object.values(c.proportion_packs).reduce((a, b) => a + b, 0) : null;
  return [
    { group: 'start', items: [
      { id: 'overview', label: 'Overview', meta: 'what this holds' },
    ] },
    { group: 'read the corpus', items: [
      { id: 'phylogeny', label: 'The Phylogeny', meta: c.styles ? `${c.styles} taxa` : '' },
      { id: 'style', label: 'Style Record', meta: '9 sections' },
      { id: 'kit', label: 'The Kit', meta: c.element_slots ? `${c.element_slots} slots` : '' },
      { id: 'proportions', label: 'Proportions', meta: packs ? `${packs} packs` : '' },
      { id: 'faults', label: 'Fault Corpus', meta: c.faults ? `${c.faults} solecisms` : '' },
    ] },
    { group: 'compose', items: [
      { id: 'brief', label: 'Brief Intake', meta: 'state the brief' },
      { id: 'candidates', label: 'Candidate Set', meta: 'and its criticism' },
      { id: 'workbench', label: 'Plan Workbench', meta: 'place and solve' },
    ] },
    { group: 'take it out', items: [
      { id: 'drawings', label: 'Drawing Set', meta: '5 sheets' },
      // The four format names fit the Overview, not a 236px rail — spelled out here they
      // pushed "Details & Export" onto three lines, broken at the ampersand.
      { id: 'export', label: 'Details & Export', meta: '4 formats' },
    ] },
    { group: 'bring it in', items: [
      { id: 'transcription', label: 'Transcription', meta: 'drawing in' },
    ] },
  ];
}

export function Masthead({ plan, judgment, onSearch }) {
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
      {/* The shortcut is the fast way in; this is the way anyone finds it at all. It is
          drawn as a field rather than a button because that is what it opens. */}
      {onSearch && (
        <button type="button" onClick={onSearch} aria-label="Search the corpus"
          title="Search styles, slots, faults, packs and rooms — ⌘K"
          style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 210,
            padding: '3px 9px', border: '1px solid var(--rule)', background: 'var(--paper-mat)',
            color: 'var(--ink-3)', transition: 'var(--t-hover)' }}>
          <span style={{ font: 'var(--fw-reg) 12.5px/1.4 var(--body)' }}>Search the corpus</span>
          <span style={{ flex: 1 }} />
          <span style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
            color: 'var(--ink-4)' }}>⌘K</span>
        </button>
      )}
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
  return (
    <nav aria-label="surfaces"
      style={{ width: 'var(--rail-left)', flex: 'none', borderRight: '1px solid var(--rule)',
        background: 'var(--paper)', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div style={{ flex: 1, overflow: 'auto', padding: '14px 0 18px' }}>
        {surfaces(counts).map((g) => (
          <div key={g.group} style={{ marginBottom: 18 }}>
            <Eyebrow style={{ padding: '0 14px 8px' }}>{g.group}</Eyebrow>
            {g.items.map((it) => {
              const on = current === it.id;
              return (
                <button key={it.id} type="button" onClick={() => onGo(it.id)}
                  aria-current={on ? 'page' : undefined}
                  style={{ display: 'flex', alignItems: 'baseline', gap: 9, width: '100%', textAlign: 'left',
                    padding: '4px 14px', minHeight: 28, cursor: 'pointer',
                    background: on ? 'var(--paper-deep)' : 'transparent',
                    borderLeft: on ? '2px solid var(--gilt-deep)' : '2px solid transparent',
                    transition: 'var(--t-hover)' }}>
                  <span style={{ font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 13px/1.4 var(--body)',
                    color: on ? 'var(--ink)' : 'var(--ink-2)', flex: 1, whiteSpace: 'nowrap' }}>
                    {it.label}
                  </span>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', flex: 'none',
                    whiteSpace: 'nowrap' }}>{it.meta}</span>
                </button>
              );
            })}
          </div>
        ))}
      </div>
      {/* The corpus inventory used to live here, on every surface, in a rail that is for
          navigating. It is orientation — read once — so it moved to the Overview, and the
          rail got its foot back. */}
    </nav>
  );
}

/* The strip. `filters` is the {activeCount, clear} a surface gets from useSurfaceFilters;
   passing it puts a standing "N narrowing · clear" at the right-hand end. Every surface
   that filters gets the same one, in the same place, saying the same thing — there was
   one clear-all in the whole product before, hand-built on the Plan Workbench, and no
   surface at all said how many filters were on. */
export function FilterStrip({ children, right, filters }) {
  const n = filters ? filters.activeCount : 0;
  return (
    <div style={{ height: 'var(--substrip-h)', flex: 'none', display: 'flex', alignItems: 'center',
      gap: 14, padding: '0 14px', borderBottom: '1px solid var(--rule)', background: 'var(--paper)',
      overflowX: 'auto', overflowY: 'hidden', scrollbarWidth: 'thin' }}>
      {children}
      <div style={{ flex: 1, minWidth: 14 }} />
      {right}
      {n > 0 && (
        <button type="button" onClick={filters.clear}
          title="Show everything again"
          style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', whiteSpace: 'nowrap',
            flex: 'none', borderBottom: '1px solid var(--link-underline)' }}>
          {n} narrowing · clear
        </button>
      )}
    </div>
  );
}

/* A filter. On or off, and it says so to a screen reader as well as to an eye.

   Chip used to be three things — a toggle, a radio, and a plain action like "download
   SVG" or "undo" — drawn identically, so a button that DID something looked exactly like
   a button that HID something. Actions moved to ActionChip; this one is now only ever a
   filter, and carries aria-pressed to prove it. */
export function Chip({ on, onClick, children, tone, title, radio }) {
  const aria = radio ? { role: 'radio', 'aria-checked': !!on } : { 'aria-pressed': !!on };
  return (
    <button type="button" onClick={onClick} title={title} {...aria}
      style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
        border: '1px solid ' + (on ? (tone || 'var(--gilt-deep)') : 'var(--rule)'),
        color: on ? (tone || 'var(--gilt-deep)') : 'var(--ink-3)',
        background: on ? 'var(--paper-deep)' : 'transparent', transition: 'var(--t-hover)' }}>{children}</button>
  );
}

/* An act, not a state. Drawn with no border and a gilt hand so it cannot be mistaken for
   something that is switched on. */
export function ActionChip({ onClick, children, title, disabled, affix = '→' }) {
  return (
    <button type="button" onClick={onClick} title={title} disabled={disabled}
      style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
        display: 'inline-flex', alignItems: 'center', gap: 5, border: '1px solid transparent',
        color: disabled ? 'var(--text-disabled)' : 'var(--gilt-deep)',
        cursor: disabled ? 'default' : 'pointer', transition: 'var(--t-hover)' }}>
      {children}
      {affix && <span aria-hidden="true" style={{ color: 'var(--ink-4)' }}>{affix}</span>}
    </button>
  );
}

/* Chips that are alternatives rather than independent switches — one level, one sort
   order, one view. The group is what tells a screen reader they are alternatives. */
export function ChipGroup({ label, children }) {
  return (
    <span role="radiogroup" aria-label={label}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      {children}
    </span>
  );
}

/* A cluster of filters that stays folded until wanted, showing what is on inside it while
   closed. This is the whole answer to a strip with eight axes on it: the two you steer by
   stay out, the rest fold into a word — and the word says whether anything inside is
   narrowing what you see, so folding never hides an active filter. */
export function FilterGroup({ label, summary, children, defaultOpen = false, active = 0 }) {
  const [open, setOpen] = React.useState(defaultOpen);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8, flex: 'none' }}>
      <button type="button" onClick={() => setOpen(!open)} aria-expanded={open}
        title={open ? `Fold ${label} away` : `Show the ${label} filters`}
        style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
          display: 'inline-flex', alignItems: 'center', gap: 6,
          border: '1px solid ' + (active ? 'var(--gilt-deep)' : 'var(--rule)'),
          color: active ? 'var(--gilt-deep)' : 'var(--ink-3)',
          background: open ? 'var(--paper-deep)' : 'transparent', transition: 'var(--t-hover)' }}>
        <span aria-hidden="true" style={{ color: 'var(--ink-4)' }}>{open ? '−' : '+'}</span>
        {label}
        {!open && summary && (
          <span style={{ color: active ? 'var(--gilt-deep)' : 'var(--ink-4)' }}>· {summary}</span>
        )}
      </button>
      {open && children}
    </span>
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
