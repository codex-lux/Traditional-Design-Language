/* Where you land. The calm room before the dense ones.

   The workbench opened directly onto the Plan Workbench — the single most instrument-like
   surface in the product, eight filter axes and a solver — which is a reasonable place to
   RESUME and a poor place to ARRIVE. Somebody seeing this for the first time met a
   half-built plan and eleven unexplained words down the left-hand side.

   Everything here is already served by /api/overview. Not one number, claim or sentence
   on this page is written in the app: `what_this_is` is the corpus's own description of
   itself, the counts are the counts, and the traditions are the five trunks it holds. A
   landing page that describes a corpus in words the corpus does not use is a landing page
   that goes stale silently, and this one is the first thing anybody reads.

   Returning readers are served by the URL rather than by this page: every place is now
   addressable, so a refresh, a bookmark or a back button puts you where you were. */
import React from 'react';
import { api } from '../api/client.js';
import { nav } from '../state/nav.js';
import { planDoc } from '../state/planDoc.js';
import { Eyebrow } from '../components/Eyebrow.jsx';

/* The three things anybody is here to do. The rail groups by the same three, so the
   vocabulary is learned once. */
const DOORS = [
  {
    group: 'Read the corpus',
    blurb: 'What the tradition holds, and where each figure came from.',
    items: [
      ['phylogeny', 'The Phylogeny', 'every style, and what descends from what'],
      ['style', 'Style Record', 'one style in full — tells, constraints, sources'],
      ['kit', 'The Kit', 'what a style specifies, slot by slot'],
      ['proportions', 'Proportions', 'the systems that dimension it'],
      ['faults', 'Fault Corpus', 'the named errors, and why each reads as wrong'],
    ],
  },
  {
    group: 'Compose a house',
    blurb: 'A brief in, candidates out, one plan on the bench. In that order.',
    items: [
      ['brief', 'Brief Intake', 'state what the house is for'],
      ['candidates', 'Candidate Set', 'what the composer proposed, and its criticism'],
      ['workbench', 'Plan Workbench', 'place rooms, solve, read the findings'],
    ],
  },
  {
    group: 'Take it out, or bring it in',
    blurb: 'The record is the object; these are its renderings.',
    items: [
      ['drawings', 'Drawing Set', 'plan, elevation, section, bearing, roof'],
      ['export', 'Details & Export', 'JSON · SVG · DXF · IFC'],
      ['transcription', 'Transcription', 'a drawing in, a plan record out'],
    ],
  },
];

const NUM = (n) => (n == null ? '—' : String(n));

export function Overview({ onSearch }) {
  const [o, setO] = React.useState(null);
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);

  React.useEffect(() => { api.overview().then(setO).catch(() => setO(null)); }, []);

  const c = (o && o.counts) || {};
  const packs = c.proportion_packs
    ? Object.values(c.proportion_packs).reduce((a, b) => a + b, 0) : null;

  const inventory = [
    ['styles', c.styles], ['lineage edges', c.lineage_edges], ['element slots', c.element_slots],
    ['proportion packs', packs], ['massings', c.massings], ['rooms', c.rooms],
    ['room groupings', c.room_groupings], ['faults', c.faults], ['image records', c.image_records],
  ];

  const countFor = {
    phylogeny: c.styles && `${c.styles} taxa`,
    kit: c.element_slots && `${c.element_slots} slots`,
    faults: c.faults && `${c.faults} named`,
    proportions: packs && `${packs} packs`,
  };

  return (
    <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
      <div style={{ maxWidth: 940, margin: '0 auto', padding: '42px 34px 60px' }}>

        <Eyebrow tone="secondary">the corpus</Eyebrow>
        <h1 style={{ font: 'var(--fw-reg) var(--fs-d1)/1.08 var(--display)',
          fontVariationSettings: '"opsz" 72', letterSpacing: 'var(--tr-display)',
          color: 'var(--ink)', margin: '10px 0 0' }}>
          Traditional Design Language
        </h1>

        {/* The corpus describing itself. Not a word of this is written in the app. */}
        <p style={{ font: 'var(--fw-reg) 15.5px/1.65 var(--body)', color: 'var(--ink-2)',
          margin: '16px 0 0', maxWidth: '66ch' }}>
          {o ? o.what_this_is : ' '}
        </p>

        {/* The one invitation. A newcomer's first useful act is to look something up. */}
        <button type="button" onClick={onSearch}
          style={{ display: 'flex', alignItems: 'center', gap: 14, width: '100%', maxWidth: 560,
            margin: '26px 0 0', padding: '12px 15px', textAlign: 'left',
            border: '1px solid var(--rule)', background: 'var(--paper-mat)',
            transition: 'var(--t-hover)' }}>
          <span style={{ font: 'var(--fw-reg) 15px/1.4 var(--body)', color: 'var(--ink-2)' }}>
            Search the corpus
          </span>
          <span style={{ flex: 1 }} />
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
            {o ? `${NUM(c.styles)} styles · ${NUM(c.element_slots)} slots · ${NUM(c.faults)} faults` : ''}
          </span>
          <span style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)', color: 'var(--ink-3)' }}>⌘K</span>
        </button>

        {/* What is on the bench, if anything. The one piece of state a returning reader
            most wants, and the reason not to make them go looking for it. */}
        {plan && (
          <button type="button" onClick={() => nav.go('workbench')}
            style={{ display: 'block', width: '100%', maxWidth: 560, textAlign: 'left',
              margin: '12px 0 0', padding: '11px 15px', border: '1px solid var(--rule)',
              borderLeft: '2px solid var(--gilt-deep)', background: 'var(--paper)',
              transition: 'var(--t-hover)' }}>
            <Eyebrow tone="accent" as="span">on the bench</Eyebrow>
            <div style={{ font: 'var(--fw-reg) 14.5px/1.35 var(--body)', color: 'var(--ink)',
              marginTop: 5 }}>
              {plan.id}
              {plan.style && (
                <span style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
                  color: 'var(--ink-4)' }}> · {plan.style}</span>
              )}
            </div>
          </button>
        )}

        {/* The doors. */}
        <div style={{ marginTop: 40, display: 'grid', gap: 30,
          gridTemplateColumns: 'repeat(auto-fit, minmax(268px, 1fr))' }}>
          {DOORS.map((d) => (
            <section key={d.group}>
              <h2 style={{ font: 'var(--fw-reg) var(--fs-d4)/1.2 var(--display)',
                letterSpacing: 'var(--tr-display)', color: 'var(--ink)', margin: 0 }}>{d.group}</h2>
              <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-4)',
                margin: '5px 0 12px', maxWidth: '38ch' }}>{d.blurb}</p>
              {d.items.map(([id, label, what]) => (
                <button key={id} type="button" onClick={() => nav.go(id)}
                  style={{ display: 'block', width: '100%', textAlign: 'left', padding: '6px 9px',
                    marginLeft: -9, borderLeft: '2px solid transparent', transition: 'var(--t-hover)' }}>
                  <span style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <span style={{ font: 'var(--fw-reg) 14px/1.3 var(--body)', color: 'var(--ink)' }}>
                      {label}
                    </span>
                    {countFor[id] && (
                      <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
                        {countFor[id]}
                      </span>
                    )}
                  </span>
                  <span style={{ display: 'block', font: 'var(--fw-reg) 12px/1.45 var(--body)',
                    color: 'var(--ink-3)', marginTop: 2 }}>{what}</span>
                </button>
              ))}
            </section>
          ))}
        </div>

        {/* The inventory, moved off the rail — it is orientation, read once, not
            navigation, read constantly. It was taking 140px of the rail on every surface. */}
        <div style={{ marginTop: 44, paddingTop: 18, borderTop: '1px solid var(--rule)' }}>
          <Eyebrow style={{ marginBottom: 11 }}>
            what it holds{o ? ` · ontology ${o.ontology_version}` : ''}
          </Eyebrow>
          <div style={{ display: 'grid', gap: '3px 30px',
            gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))' }}>
            {inventory.map(([label, n]) => (
              <div key={label} style={{ display: 'flex', justifyContent: 'space-between', gap: 10,
                borderBottom: '1px solid var(--rule-soft)', padding: '3px 0' }}>
                <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>{label}</span>
                <span style={{ font: 'var(--type-data)', color: 'var(--ink-2)' }}>{NUM(n)}</span>
              </div>
            ))}
          </div>

          {/* The five trunks, named. The absence of the others is stated on the Phylogeny
              itself; this only says what is here. */}
          {o && o.traditions && (
            <div style={{ marginTop: 22 }}>
              <Eyebrow style={{ marginBottom: 9 }}>{o.traditions.length} traditions</Eyebrow>
              {o.traditions.map((t) => (
                <button key={t.id} type="button" onClick={() => nav.cite('style:' + t.id)}
                  style={{ display: 'block', width: '100%', textAlign: 'left', padding: '5px 0',
                    borderBottom: '1px solid var(--rule-soft)' }}>
                  <span style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                    <span style={{ font: 'var(--fw-reg) 13.5px/1.35 var(--body)', color: 'var(--ink)' }}>
                      {t.name}
                    </span>
                    <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{t.years}</span>
                  </span>
                  <span style={{ display: 'block', font: 'var(--fw-reg) 12px/1.5 var(--body)',
                    color: 'var(--ink-3)', marginTop: 2, maxWidth: '80ch' }}>{t.short}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
