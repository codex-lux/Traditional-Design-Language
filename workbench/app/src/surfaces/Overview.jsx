/* THE FRONT DOOR (WP-14.14). Where somebody arrives with no idea what this is.

   Phase 14's first finding was that nothing said. The landing's one paragraph was
   `core.overview().what_this_is`, which is the MCP server's orientation string, written to an AI
   agent and still SERVED by `/api/overview` for it — but it never said that a house can be
   composed, checked and drawn here, and it is no longer this page's paragraph. The rest was
   `DOORS`: eleven buttons in three groups, each with a label and a description typed into this
   file, under a comment claiming "not one number, claim or sentence on this page is written in
   the app". Both are retired.

   EVERY WORD ON THIS PAGE IS A GLOSSARY RECORD'S, AND EVERY FIGURE IS THE API'S:

     what this is      `about-tdl`'s term and definition — the one sentence the Gate also shows
     who it is for     `about-tdl`'s readers, VISION IX's practitioners; the record leaves the
                       homeowner out on purpose, and so does this page
     two entrances     the site map's own items for Find a style and the first house step, each
                       with its surface record's `what`; the style in hand OFFERED as a link
                       beside the first (memory only offers — PRD §F.4) and, where a house is
                       under way, the journey's own resume beside the second
     the map           `components/TwoSpineMap.jsx`, which is `nav/navModel.js` drawn as ruled
                       rows — the rail's own table, so the navigation is learned once
     the example       `guided-example`: its definition, its citations as links, and where it
                       stops, in its own words (`oq/the-worked-house-has-no-plan-that-places`)
     what it holds     `/api/overview`'s counts, named by the records for each rank and kind,
                       and the ontology version
     what it is not    `about-tdl`'s `is_not`

   The page is written by `frontdoor/frontDoor.js`, which is pure and tested, and this file draws
   it. `src/frontDoor.test.mjs` reads this file for count literals, app-written prose, a style id
   and readable `--ink-4`, and `src/copy_ratchet.test.mjs` holds the tree's count literals.

   IT FITS A LAPTOP: no fixed width over a column's share, every row wraps. The shell releases the
   1380 px floor for this page (`#root[data-reflow]`, PRD §I.12, WP-14.13); this page does not set
   that attribute itself, because the shell owns `#root`. */
import React from 'react';
import { api } from '../api/client.js';
import { useGlossary } from '../api/useGlossary.js';
import { useNames } from '../names/useNames.js';
import { nav } from '../state/nav.js';
import { planDoc } from '../state/planDoc.js';
import { session } from '../state/session.js';
import { prefs } from '../state/prefs.js';
import { navModel, inHandFrom } from '../nav/navModel.js';
import { journeyState } from '../journey/journey.js';
import {
  aboutView, guidedView, rankRows, total, entranceItems, resumeView,
} from '../frontdoor/frontDoor.js';
import { isMissing } from '../glossary/lookup.js';
import { Term, noEntry } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { TwoSpineMap } from '../components/TwoSpineMap.jsx';

const prose = { font: 'var(--type-prose)', color: 'var(--ink)', margin: 0 };
const small = { font: 'var(--fw-reg) var(--fs-body-s)/var(--lh-body) var(--serif)', color: 'var(--ink)' };
const note = { font: 'var(--type-data-s)', color: 'var(--ink-2)' };
const rule = { borderTop: '1px solid var(--rule-soft)' };
const link = { color: 'var(--ink)', textDecoration: 'none', borderBottom: '1px solid var(--link-underline)' };

/* A place's word, or `noEntry(id)` where the record is missing; nothing while it loads. */
function Word({ label, missing }) {
  if (label) return label;
  if (missing) return <span data-missing="" style={note}>{noEntry(missing)}</span>;
  return null;
}

/* A surface record's `what`, the one line its own page head leads with. */
function whatOf(rec) {
  if (!rec) return null;
  if (isMissing(rec)) return <span data-missing="" style={note}>{noEntry(rec.missing)}</span>;
  return rec.surface && typeof rec.surface.what === 'string' ? rec.surface.what : null;
}

function Entrance({ group, item, what, children }) {
  return (
    <section data-entrance={item ? item.id : ''} style={{
      border: '1px solid var(--rule)', background: 'var(--paper-lit)', padding: '14px 16px 15px',
      minWidth: 0,
    }}>
      <Eyebrow as="div">{group}</Eyebrow>
      {item && (
        <a href={item.href} data-entrance-link={item.id} style={{
          ...link, display: 'inline-block', marginTop: 8,
          font: 'var(--fw-reg) var(--fs-d4)/1.25 var(--display)',
        }}>
          {item.step != null && <span style={{ ...note, marginRight: 8 }}>{item.step}</span>}
          <Word label={item.label} missing={item.missing} />
          {item.meta != null && <span style={{ ...note, marginLeft: 9 }}>{String(item.meta)}</span>}
        </a>
      )}
      {what && <p style={{ ...small, margin: '7px 0 0' }}>{what}</p>}
      {children}
    </section>
  );
}

export function Overview({ onSearch, lastEval }) {
  const glossary = useGlossary();
  const lookup = glossary.lookup;
  const names = useNames();
  const place = React.useSyncExternalStore(nav.subscribe, nav.get);
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const sess = React.useSyncExternalStore(session.subscribe, session.get);
  const held = React.useSyncExternalStore(prefs.subscribe, prefs.get).styleInHand;

  const [o, setO] = React.useState(null);
  React.useEffect(() => { api.overview().then(setO, () => setO(null)); }, []);
  // The front door has been visited: the cold-link banner (WP-14.13) reads this and never shows.
  React.useEffect(() => { prefs.markSeen('front-door'); }, []);

  const about = aboutView(lookup);
  const guided = guidedView(lookup);

  // The example brief's own name: `brief:` is a kind the search index does not name, so the link
  // is worded by the record it cites, read from the route that serves it — or left as the cite.
  const [briefName, setBriefName] = React.useState(null);
  const briefId = guided.state === 'ready' ? guided.briefId : null;
  React.useEffect(() => {
    if (!briefId) return undefined;
    let live = true;
    api.exampleBrief(briefId).then((b) => {
      if (live) setBriefName(b && typeof b.name === 'string' && b.name.trim() ? b.name.trim() : null);
    }, () => {});
    return () => { live = false; };
  }, [briefId]);

  const counts = o && o.counts ? o.counts : null;
  const nameOf = (id) => {
    const n = names.nameFor('style:' + id);
    return n.resolved ? n.name : null;
  };
  const journey = journeyState({ session: sess, plan, lastEval });
  const model = lookup
    ? navModel({ lookup, counts, glossaryCount: lookup.count, inHand: inHandFrom(held, lookup, nameOf),
      journey, place })
    : null;
  const doors = entranceItems(model);
  const resume = resumeView(journey, model);

  return (
    <div data-front-door="" style={{ flex: 1, overflow: 'auto', minHeight: 0, minWidth: 0 }}>
      <div style={{ maxWidth: 1060, margin: '0 auto', padding: '34px clamp(16px, 3vw, 34px) 56px' }}>

        {/* WHAT THIS IS — the one sentence the Gate shows too. */}
        <header data-about="" aria-busy={about.state === 'loading' ? 'true' : undefined}>
          {about.state === 'missing' && <p data-missing="" style={note}>{noEntry(about.missing)}</p>}
          {about.state === 'ready' && (
            <>
              <h1 style={{ font: 'var(--fw-reg) var(--fs-d1)/1.08 var(--display)',
                fontVariationSettings: '"opsz" 72', letterSpacing: 'var(--tr-display)',
                color: 'var(--ink)', margin: 0 }}>
                {about.term}
              </h1>
              <p data-about-definition="" style={{ ...prose, font: 'var(--fw-reg) var(--fs-lede)/1.5 var(--serif)',
                margin: '12px 0 0', maxWidth: '64ch' }}>
                {about.definition}
              </p>

              {/* WHO IT IS FOR — VISION IX's practitioners, as the record gives them. */}
              <ul data-readers="" style={{ listStyle: 'none', padding: 0, margin: '22px 0 0', display: 'grid',
                gap: '12px 26px', gridTemplateColumns: 'repeat(auto-fit, minmax(15rem, 1fr))' }}>
                {about.readers.map((r) => (
                  <li key={r.who} data-reader="" style={{ ...rule, paddingTop: 9, minWidth: 0 }}>
                    <div style={{ font: 'var(--type-name)', fontSize: 'var(--fs-body)', color: 'var(--ink)' }}>{r.who}</div>
                    <p style={{ ...small, margin: '4px 0 0' }}>{r.line}</p>
                  </li>
                ))}
              </ul>
            </>
          )}
        </header>

        {/* TWO ENTRANCES — read a style, or write a house. The site map's own items. */}
        <div data-entrances="" style={{ marginTop: 28, display: 'grid', gap: 16,
          gridTemplateColumns: 'repeat(auto-fit, minmax(17rem, 1fr))' }}>
          <Entrance group={<Term id="nav-group-styles" />} item={doors.style}
            what={lookup ? whatOf(lookup.term('surface-style')) : null}>
            {doors.inHand && (
              <p style={{ ...small, margin: '10px 0 0' }}>
                <a href={doors.inHand.href} data-entrance-link="in-hand" style={link}>
                  <Word label={doors.inHand.label} missing={doors.inHand.missing} />
                </a>
                {doors.inHand.note && <span className="tdl-record-note">{doors.inHand.note}</span>}
              </p>
            )}
          </Entrance>
          <Entrance group={<Term id="nav-group-a-house" />} item={doors.brief}
            what={lookup ? whatOf(lookup.term('surface-brief')) : null}>
            {resume && (
              <p data-resume={resume.id} style={{ ...small, margin: '10px 0 0' }}>
                {resume.plan && plan && (
                  <span style={{ marginRight: 8 }}>
                    <Term id="on-the-bench" />
                    <span style={{ marginLeft: 7 }}>{plan.name || plan.id}</span>
                  </span>
                )}
                <a href={resume.href} style={link}>
                  <span style={{ ...note, marginRight: 6 }}>{resume.n}</span>
                  <Word label={resume.label} missing={resume.missing} />
                </a>
                {resume.words && <span style={{ ...note, marginLeft: 8 }}>{resume.words}</span>}
              </p>
            )}
          </Entrance>
        </div>

        {/* The one invitation that is not a place: look something up. */}
        <button type="button" onClick={onSearch}
          style={{ display: 'flex', alignItems: 'center', gap: 14, width: '100%', maxWidth: 560,
            margin: '16px 0 0', padding: '11px 15px', textAlign: 'left',
            border: '1px solid var(--rule)', background: 'var(--paper-mat)',
            transition: 'var(--t-hover)' }}>
          <span style={{ font: 'var(--fw-reg) 15px/1.4 var(--body)', color: 'var(--ink-2)' }}>
            Search the corpus
          </span>
          <span style={{ flex: 1 }} />
          <span style={{ ...note, fontFamily: 'var(--mono)' }}>⌘K</span>
        </button>

        {/* THE MAP, and THE WORKED EXAMPLE beside it. */}
        <div style={{ marginTop: 34, display: 'grid', gap: '26px 40px',
          gridTemplateColumns: 'repeat(auto-fit, minmax(20rem, 1fr))', alignItems: 'start' }}>
          <div style={{ minWidth: 0 }}>{model && <TwoSpineMap model={model} />}</div>

          <section data-guided-example="" style={{ ...rule, paddingTop: 10, minWidth: 0 }}>
            {guided.state === 'missing' && <p data-missing="" style={note}>{noEntry(guided.missing)}</p>}
            {guided.state === 'ready' && (
              <>
                <Eyebrow as="h2" style={{ margin: 0 }}>{guided.word}</Eyebrow>
                <p data-guided-definition="" style={{ ...prose, margin: '8px 0 0' }}>{guided.definition}</p>
                {guided.cites.length > 0 && (
                  <ul style={{ listStyle: 'none', padding: 0, margin: '10px 0 0' }}>
                    {guided.cites.map((c) => (
                      <li key={c} style={{ ...small, padding: '3px 0' }}>
                        <RecordLink cite={c}>{c === guided.briefCite && briefName ? briefName : undefined}</RecordLink>
                      </li>
                    ))}
                  </ul>
                )}
                {/* WHERE IT STOPS, in the record's words and no others. */}
                {guided.more && (
                  <p data-guided-stop="" style={{ ...small, margin: '10px 0 0', paddingLeft: 10,
                    borderLeft: '2px solid var(--rule)' }}>{guided.more}</p>
                )}
              </>
            )}
          </section>
        </div>

        {/* WHAT IT HOLDS, and WHAT IT IS NOT. */}
        <div style={{ marginTop: 34, display: 'grid', gap: '26px 40px',
          gridTemplateColumns: 'repeat(auto-fit, minmax(17rem, 1fr))', alignItems: 'start' }}>
          <section data-inventory="" style={{ ...rule, paddingTop: 10, minWidth: 0 }}>
            <Eyebrow as="div" data-ontology-version={o ? o.ontology_version : undefined}>
              {o ? `ontology ${o.ontology_version}` : ' '}
            </Eyebrow>
            {counts && (
              <dl style={{ margin: '8px 0 0' }}>
                {rankRows(counts, lookup).map((r) => (
                  <div key={r.key} data-rank={r.key} style={invRow}>
                    <dt>{r.termId ? <Term field="style.rank" value={r.key} />
                      : <span data-missing="" style={note}>{noEntry(r.missing || r.key)}</span>}</dt>
                    <dd data-figure="" style={figure}>{r.figure}</dd>
                  </div>
                ))}
                <div data-holds="slot" style={invRow}>
                  <dt><Term id="slot" /></dt><dd data-figure="" style={figure}>{counts.element_slots}</dd>
                </div>
                <div data-holds="proportion-pack" style={invRow}>
                  <dt><Term id="proportion-pack" /></dt>
                  <dd data-figure="" style={figure}>{total(counts.proportion_packs)}</dd>
                </div>
                <div data-holds="fault" style={invRow}>
                  <dt><Term id="fault" /></dt><dd data-figure="" style={figure}>{counts.faults}</dd>
                </div>
                <div data-holds="massing" style={invRow}>
                  <dt><Term id="massing" /></dt><dd data-figure="" style={figure}>{counts.massings}</dd>
                </div>
                <div data-holds="grouping" style={invRow}>
                  <dt><Term id="grouping" /></dt><dd data-figure="" style={figure}>{counts.room_groupings}</dd>
                </div>
              </dl>
            )}
          </section>

          {about.state === 'ready' && about.isNot.length > 0 && (
            <ul data-is-not="" style={{ ...rule, listStyle: 'none', padding: '10px 0 0', margin: 0, minWidth: 0 }}>
              {about.isNot.map((line) => (
                <li key={line} style={{ ...small, color: 'var(--ink-2)', padding: '4px 0' }}>{line}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

const invRow = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12,
  borderBottom: '1px solid var(--rule-soft)', padding: '3px 0',
  font: 'var(--fw-reg) var(--fs-body-s)/1.4 var(--serif)', color: 'var(--ink)',
};
const figure = { margin: 0, font: 'var(--type-data)', color: 'var(--ink)' };
