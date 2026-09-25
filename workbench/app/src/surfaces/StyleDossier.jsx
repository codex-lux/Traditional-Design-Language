/* The Style Dossier — everything about one style in one citable place (WP-14.12, PRD §D, §E.2).

   It replaces `StyleRecord.jsx`, which was one long page, and the Kit surface, which was a second
   page about the same style reached by a different address. The style surface is two places on
   one path and `dossier/sections.js::placeOf` says which a selection names: a style present opens
   the DOSSIER, and anything else is the STYLES INDEX, which never shows a record. A third, the
   slot panel for a slot with no style, left for the Elements index at WP-14.23 (tranche 2 §B.2),
   and its old address is rewritten there by the router.

   THE DOSSIER. A head -- rank, what it is filed under, its years, its name with its id as a margin
   note, its tradition's swatch, a StylePicker, "Design a house in this style" and, since WP-14.26,
   "compare with…", which opens this style beside another on the Compare page -- then a strip of
   the sections the dossier payload lists, in `DOSSIER_SECTIONS` order and labelled by their
   `section-*` glossary records, then ONLY THE SECTION IN VIEW. A section whose count is zero is not
   listed and is not drawn: the URL may ask for it and is told, by name, that this record has none.
   Every count on the page is the payload's. Every hop writes the URL -- a section is an anchor, the
   picker selects, a slot opens its own address -- so any state of this page is a link.

   When a dossier the API resolved is on screen, `prefs.setStyleInHand` records it, and that is the
   ONLY thing this file does with the style in hand: it is written here and offered elsewhere, and
   never read back into what this page shows. `dossier.test.mjs` holds the source to that.

   Beside the sections, in the Kit's old pullable pane (`PANES.kit`, "the style's record"), the
   relations panel: what it is filed under, what is filed under it, its neighbours, and the plan on
   the bench. On the kit section that pane is the kit's own, holding its cascade ladder, as it did
   when the Kit was a surface: a slot table beside two panes has no width left to be read. */
import React from 'react';
import { api } from '../api/client.js';
import { prefs } from '../state/prefs.js';
import { formatHash } from '../router.js';
import { nav } from '../state/nav.js';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { DOSSIER_SECTIONS } from '../citations.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { PullPane } from '../components/PullPane.jsx';
import { RelationsPanel } from '../components/RelationsPanel.jsx';
import { TRADITION_HUES } from '../styles/taxa.js';
import { StylesIndex } from './StylesIndex.jsx';
import {
  placeOf, listedSections, sectionInView, summaryCards, sectionAddress, IDENTIFY,
} from '../dossier/sections.js';
import { SectionWord } from '../dossier/parts.jsx';
import { Identify } from '../dossier/Identify.jsx';
import { Members } from '../dossier/Members.jsx';
import { Lineage } from '../dossier/Lineage.jsx';
import { KitSection } from '../dossier/KitSection.jsx';
import { ProportionsSection } from '../dossier/ProportionsSection.jsx';
import { PlanTypes } from '../dossier/PlanTypes.jsx';
import { Rules } from '../dossier/Rules.jsx';
import { Faults } from '../dossier/Faults.jsx';
import { Evidence } from '../dossier/Evidence.jsx';

/* "compare with…" (WP-14.26): the `compare-with` record's word and a picker for the second style,
   which opens the two side by side at `#/compare/<this>/<that>`. The picker's label is the same
   record's word, read as text because an input's label cannot hold a `Term`. */
function CompareWith({ styleId }) {
  const v = termView(useGlossary(), { id: 'compare-with' });
  return (
    <span data-compare-with={styleId} style={{ display: 'inline-flex', gap: 7, alignItems: 'center' }}>
      <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}><Term id="compare-with" /></span>
      <StylePicker value="" width={190} label={v.state === 'ready' ? v.word : undefined}
        onChange={(other) => { if (other && other !== styleId) nav.go('compare', { style: styleId, compare: other }); }} />
    </span>
  );
}

const ALL_SECTIONS = 'summary,description,characteristics,lineage,proportion,massing,constraints,exemplars,sources';
const BUILT = { style: 1, variant: 1 };
const quietText = { font: 'var(--type-body)', color: 'var(--ink-2)' };

export function StyleDossier({ onCite, selection, setSelection }) {
  const place = placeOf(selection);
  if (place === 'index') return <StylesIndex />;
  return <Dossier styleId={selection.style} selection={selection} setSelection={setSelection} onCite={onCite} />;
}

function Dossier({ styleId, selection, setSelection, onCite }) {
  const [dossier, setDossier] = React.useState(null);
  const [rec, setRec] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [taxa, setTaxa] = React.useState(null);

  React.useEffect(() => {
    let live = true;
    setDossier(null); setRec(null); setError(null);
    Promise.all([api.styleDossier(styleId), api.style(styleId, ALL_SECTIONS)])
      .then(([d, r]) => { if (live) { setDossier(d); setRec(r); } })
      .catch((e) => { if (live) setError(e); });
    return () => { live = false; };
  }, [styleId]);

  React.useEffect(() => {
    api.phylogeny().then((p) => setTaxa(p.taxa || [])).catch(() => setTaxa(null));
  }, []);

  // A dossier the API RESOLVED, for the id this page names -- never a request still in flight.
  React.useEffect(() => {
    if (dossier && dossier.id === styleId) prefs.setStyleInHand(styleId);
  }, [dossier, styleId]);

  if (error) {
    return (
      <div data-dossier-missing={styleId} style={{ padding: 24 }}>
        <p style={quietText}>
          {error.status === 404
            ? <>The corpus holds no style <code>{styleId}</code>.</>
            : <>The dossier for <code>{styleId}</code> could not be read.</>}
        </p>
        <p style={quietText}><a href={formatHash('style', {}, {})}><Term id="surface-style" /></a></p>
      </div>
    );
  }
  if (!dossier || !rec) {
    return <div style={{ padding: 24, font: 'var(--type-body)', color: 'var(--ink-2)' }}>reading the record…</div>;
  }

  const listed = listedSections(dossier);
  const view = sectionInView(selection.section, listed);
  const s = rec.summary || {};
  const chain = dossier.chain || [];
  const parent = chain.length ? chain[chain.length - 1] : null;
  const tradition = dossier.rank === 'tradition'
    ? { id: dossier.id, name: dossier.name }
    : (chain[0] && chain[0].rank === 'tradition' ? chain[0] : null);
  const hue = tradition ? TRADITION_HUES[tradition.id] : null;
  const pick = (v) => setSelection && setSelection({ style: v, slot: null, constraint: null });
  const isKit = view.id === 'kit';

  return (
    <div data-dossier={styleId} style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <header data-dossier-head={styleId} style={{ flex: 'none', padding: '14px 26px 10px', borderBottom: '1px solid var(--rule)' }}>
        <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'baseline' }}>
          {dossier.rank && <span data-rank={dossier.rank}><Term field="style.rank" value={dossier.rank} /></span>}
          {parent && (
            <span data-filed-under-head={parent.id}>
              · <Term id="member-of" /> <RecordLink cite={'style:' + parent.id}>{parent.name || parent.id}</RecordLink>
            </span>
          )}
          {s.years && <span>· {s.years}</span>}
        </div>
        <h2 style={{ font: 'var(--fw-reg) var(--fs-d1, 34px)/1.08 var(--display)', letterSpacing: 'var(--tr-display)',
          margin: '6px 0 6px' }}>
          {dossier.name || styleId}<span className="tdl-record-note" data-dossier-id="">{styleId}</span>
        </h2>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
          {tradition && (
            <span data-tradition={tradition.id} style={{ display: 'inline-flex', gap: 7, alignItems: 'center', font: 'var(--type-data-s)' }}>
              {hue && <span aria-hidden="true" style={{ width: 10, height: 10, background: hue, flex: 'none' }} />}
              <RecordLink cite={'style:' + tradition.id}>{tradition.name || tradition.id}</RecordLink>
            </span>
          )}
          <StylePicker value={styleId} width={230} label="Which style's dossier to read" onChange={pick} />
          {BUILT[dossier.rank] && (
            <a data-design-house={styleId} href={formatHash('brief', { style: styleId }, {})}
              style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', whiteSpace: 'nowrap' }}>
              Design a house in this style →
            </a>
          )}
          <a href={formatHash('phylogeny', { style: styleId }, {})}
            style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', whiteSpace: 'nowrap' }}>
            place in the phylogeny →
          </a>
          <CompareWith styleId={styleId} />
        </div>
      </header>

      <nav aria-label="dossier sections" data-section-strip={styleId}
        style={{ flex: 'none', display: 'flex', gap: 2, padding: '0 20px', borderBottom: '1px solid var(--rule)',
          overflowX: 'auto', background: 'var(--paper)' }}>
        {listed.map((sec) => {
          const on = sec.id === view.id;
          return (
            <a key={sec.id} href={sectionAddress(styleId, sec.id)} aria-current={on ? 'page' : undefined}
              data-section={sec.id} data-count={sec.count == null ? undefined : sec.count}
              style={{ display: 'inline-flex', gap: 6, alignItems: 'baseline', padding: '8px 10px 7px', whiteSpace: 'nowrap',
                textDecoration: 'none', color: on ? 'var(--ink)' : 'var(--ink-2)',
                borderBottom: on ? '2px solid var(--gilt-deep)' : '2px solid transparent',
                font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 13px/1.3 var(--body)' }}>
              <SectionWord id={sec.id} />
              {sec.count != null && <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>{sec.count}</span>}
            </a>
          );
        })}
      </nav>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div data-section-in-view={view.id}
          style={isKit
            ? { flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, minWidth: 0 }
            : { flex: 1, overflow: 'auto', minHeight: 0, minWidth: 0, padding: '20px 26px 40px' }}>
          {view.refused && (
            <p data-section-refused={view.refused} style={{ ...quietText, margin: '0 0 16px' }}>
              This record has no{' '}
              {DOSSIER_SECTIONS.includes(view.refused) ? <strong><SectionWord id={view.refused} /></strong> : <code>{view.refused}</code>}
              {' '}section.
            </p>
          )}
          {view.id === IDENTIFY && <Identify rec={rec} styleId={styleId} cards={summaryCards(listed)} />}
          {view.id === 'members' && <Members dossier={dossier} />}
          {view.id === 'lineage' && <Lineage rec={rec} styleId={styleId} onCite={onCite} />}
          {view.id === 'kit' && <KitSection styleId={styleId} selection={selection} setSelection={setSelection} onCite={onCite} />}
          {view.id === 'proportions' && <ProportionsSection rec={rec} styleId={styleId} />}
          {view.id === 'plans' && <PlanTypes dossier={dossier} />}
          {view.id === 'rules' && <Rules rec={rec} styleId={styleId} selected={selection.constraint || null} />}
          {view.id === 'faults' && <Faults dossier={dossier} styleId={styleId} />}
          {view.id === 'evidence' && <Evidence rec={rec} styleId={styleId} />}
        </div>
        {!isKit && (
          <PullPane pane="kit" side="right"
            style={{ borderLeft: '1px solid var(--rule)', overflow: 'auto', background: 'var(--paper)' }}>
            <RelationsPanel dossier={dossier} styleId={styleId} taxa={taxa} />
          </PullPane>
        )}
      </div>
    </div>
  );
}
