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
     the map           the sidebar since Phase 17 (the two-spine map on this page is retired),
                       rows — the rail's own table, so the navigation is learned once
     the example       `guided-example`: its definition, its citations as links, and where it
                       stops, in its own words (`oq/the-worked-house-has-no-plan-that-places`)
     what it holds     `/api/overview`'s counts, named by the records for each rank and kind,
                       and the ontology version, under `front-door-holds`'s heading
     what it is not    `about-tdl`'s `is_not`, under `front-door-is-not`'s heading

   THE TWO LOWER SECTIONS HAD NO HEADING (WP-14.17): a column of figures under a version string and
   a list of refusals, each a region a screen reader could not name and a sighted reader had to
   infer. Each carries an `h2` now, and its word is a record like every other word here.

   The page is written by `frontdoor/frontDoor.js`, which is pure and tested, and this file draws
   it. `src/frontDoor.test.mjs` reads this file for count literals, app-written prose, a style id
   and readable `--ink-4`, and `src/copy_ratchet.test.mjs` holds the tree's count literals.

   REDRAWN IN PHASE 17 (WP-17.3, ruled 29 Oct 2026): the page was a text page about a drawing
   instrument, and it said the navigation three times. It leads now with the thesis (`about-tdl`'s
   definition at display size), one primary act and one secondary, and a real plate -- the plan
   sheet of the first shipped house the product may draw (`GET /api/front-door/hero`), never
   assumed to be the Tidewater record, which is refused. Below it the five stations of the
   journey (`stationTiles`) and the library as five cards (`libraryCards`, the sidebar's own rows),
   then the worked example, what the corpus holds and what it is not. The readers' paragraphs and
   the two-spine map are gone: the readers are `about-tdl`'s still, and the sidebar is the map.

   IT FITS A LAPTOP: no fixed width over a column's share, every row wraps. `state/layout.js`'s
   table makes this page 'reflow' and the shell marks `#root[data-reflow]` from it (WP-14.30; the
   1380 px floor that attribute once released is gone). This page does not set that attribute
   itself, because the shell owns `#root`. */
import React from 'react';
import { api } from '../api/client.js';
import { useGlossary } from '../api/useGlossary.js';
import { useNames } from '../names/useNames.js';
import { nav } from '../state/nav.js';
import { planDoc } from '../state/planDoc.js';
import { session } from '../state/session.js';
import { prefs } from '../state/prefs.js';
import { navModel, inHandFrom } from '../nav/navModel.js';
import { journeyState, JOURNEY_WORDS } from '../journey/journey.js';
import {
  aboutView, guidedView, rankRows, total, entranceItems, resumeView, stationTiles, libraryCards,
} from '../frontdoor/frontDoor.js';
import { isMissing } from '../glossary/lookup.js';
import { Term, noEntry } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Vellum } from '../components/Vellum.jsx';
import { Plate } from '../components/Plate.jsx';
import { MarkGlyph } from '../components/MarkGlyph.jsx';
import { GLYPHS } from '../frontdoor/glyphs.js';
import { sidebarView } from '../nav/sidebar.js';
import { barView } from '../journey/bar.js';

const prose = { font: 'var(--type-prose)', color: 'var(--text-body)', margin: 0 };
const small = { font: 'var(--fw-reg) var(--fs-body-s)/var(--lh-body) var(--serif)', color: 'var(--text-body)' };
const note = { font: 'var(--type-data-s)', color: 'var(--text-secondary)' };
const rule = { borderTop: '1px solid var(--border-soft)' };
/* Its anchors take the `a` rule whole: an inline underline here beat `a:hover` (WP-14.33's audit). */

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

/* The hero: the plate the server drew, whole, so its disclosures stay with it. While it is on
   its way the loading mark says so; where nothing is drawable the plate says that as a refusal. */
function Hero() {
  const [hero, setHero] = React.useState(null);
  const [failed, setFailed] = React.useState(false);
  React.useEffect(() => {
    // the server never holds the request on its sweep: it says `pending`, and the page asks again
    let live = true, timer = null, tries = 0;
    const ask = () => api.frontDoorHero().then((h) => {
      if (!live) return;
      // ten minutes before the page gives up: a cold sweep to good-03 was measured at 118 s, and one
      // over every good record can run past the four minutes this allowed first (the second audit)
      if (h && h.pending) { if (++tries < 150) timer = setTimeout(ask, 4000); else setFailed(true); return; }
      if (h && h.failed) { setFailed(true); return; }   // the sweep raised: unjudged, never refused
      setHero(h);
    }, () => { if (live) setFailed(true); });
    ask();
    return () => { live = false; if (timer) clearTimeout(timer); };
  }, []);
  const svg = hero && hero.drawing && typeof hero.drawing.svg === 'string' ? hero.drawing.svg : null;
  const engine = hero && hero.drawing && hero.drawing.solver ? hero.drawing.solver.engine : null;
  return (
    <Plate data-hero={hero ? (hero.refused ? 'refused' : hero.plan_id || '') : (failed ? 'failed' : 'loading')}
      caption={hero && !hero.refused ? <><Term id="front-door-hero" />{JOURNEY_WORDS.separator}{hero.name}{engine ? JOURNEY_WORDS.separator + engine : ''}</> : null}>
      {svg && <div className="plate-fit" style={{ maxHeight: 460, overflow: 'hidden' }} dangerouslySetInnerHTML={{ __html: svg }} />}
      {!svg && !hero && !failed && (
        <div aria-busy="true" style={{ padding: 40 }}><MarkGlyph token="--mark-loading"><Term id="front-door-hero" /></MarkGlyph></div>
      )}
      {/* A REFUSAL AND A FAILURE ARE TWO THINGS: where no shipped record may be drawn the plate says
          refused, with the count it swept; where the request itself failed nothing was judged, and
          it says unjudged -- never "refused" for a plate nobody was refused. */}
      {hero && hero.refused && (
        <div data-hero-refused="" style={{ padding: 28, borderLeft: '4px solid var(--refusal)', color: 'var(--refusal-text)' }}>
          <Term id="judgment-refused" />{JOURNEY_WORDS.separator}{hero.tried}
        </div>
      )}
      {failed && (
        <div data-hero-failed="" style={{ padding: 28, display: 'flex', gap: 8, alignItems: 'center' }}>
          <MarkGlyph token="--mark-unjudged" size={12} /><Term id="judgment-unjudged" />
        </div>
      )}
    </Plate>
  );
}

/* One station: a vellum tile done, a dark tile with a gilt border in hand, a dashed outline not yet.
   A blocked step is a tile and not a link, as in the sidebar. */
const TILE = {
  // the done tile is vellum: it carries data-ground="vellum", so the panel duty here is paper
  '--mark-journey-done': { background: 'var(--surface-panel)', border: '1px solid var(--surface-panel)' },
  '--mark-journey-current': { background: 'var(--heavy-2)', border: '1.5px solid var(--gilt)' },
  '--mark-journey-not-yet': { background: 'transparent', border: '1px dashed var(--border-paper)' },
  '--mark-refused': { background: 'transparent', border: '2px solid var(--refusal)' },
};
function Station({ t }) {
  const done = t.mark === '--mark-journey-done';
  const body = (
    <span data-ground={done ? 'vellum' : undefined} style={{ display: 'flex', flexDirection: 'column', gap: 4,
      padding: '10px 12px 11px', minHeight: 74, ...TILE[t.mark] }}>
      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <MarkGlyph token={t.mark} size={12} />
        <span style={{ ...note }}>{t.n}</span>
        <span style={{ font: 'var(--fw-med) 15px/1.3 var(--body)', color: 'var(--text-body)' }}>
          <Word label={t.label} missing={t.missing} />
        </span>
      </span>
      {t.words && <span style={{ font: 'italic var(--fw-reg) 13px/1.35 var(--body)',
        color: t.state === 'refused' ? 'var(--refusal-text)' : 'var(--text-secondary)' }}>{t.words}</span>}
    </span>
  );
  return (
    <li data-station={t.id} data-station-mark={t.mark} style={{ listStyle: 'none', minWidth: 0, zIndex: 1 }}>
      {t.href ? <a href={t.href} data-station-link={t.id} style={{ display: 'block', borderBottom: 'none' }}>{body}</a> : body}
    </li>
  );
}

function LibraryCard({ c, entrance, children }) {
  const paths = GLYPHS[c.id] || [];
  return (
    <Vellum as="section" data-library-card={c.id} style={{ padding: '14px 16px 15px', minWidth: 0,
      display: 'flex', flexDirection: 'column', gap: 8 }}>
      <span style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
        {paths.length > 0 && (
          <svg aria-hidden="true" width="40" height="40" viewBox="0 0 40 40" style={{ flex: 'none' }}>
            {paths.map((d, i) => <path key={i} d={d} fill="none" stroke="var(--heavy)"
              strokeWidth="var(--lw-fine)" vectorEffect="non-scaling-stroke" />)}
          </svg>
        )}
        {c.figure != null && <span data-card-figure="" style={{ font: 'var(--type-data)', color: 'var(--text-body)' }}>{c.figure}</span>}
      </span>
      <a href={c.href} data-entrance-link={entrance || undefined}
        style={{ font: 'var(--fw-reg) var(--fs-d4)/1.25 var(--display)', alignSelf: 'flex-start' }}>
        <Word label={c.label} missing={c.missing} />
      </a>
      {c.what && <p style={{ ...small, margin: 0 }}>{c.what}</p>}
      {children}
    </Vellum>
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
  const bar = barView(journey, { surface: 'overview', jobId: sess ? sess.jobId : null });
  const tiles = model ? stationTiles(bar, journey.resume, model) : [];
  const cards = model ? libraryCards(sidebarView(model, { bar, resume: journey.resume, surface: 'overview' }), lookup) : [];

  return (
    <div data-front-door="" data-ground="instrument" style={{ flex: 1, overflow: 'auto', minHeight: 0, minWidth: 0,
      background: 'var(--surface-app)' }}>
      <div style={{ maxWidth: 1240, margin: '0 auto', padding: '40px clamp(16px, 3vw, 40px) 64px' }}>

        {/* THE THESIS, the act, and a real plate beside them. */}
        <div style={{ display: 'grid', gap: '28px 44px', alignItems: 'center',
          gridTemplateColumns: 'repeat(auto-fit, minmax(22rem, 1fr))' }}>
          <header data-about="" aria-busy={about.state === 'loading' ? 'true' : undefined} style={{ minWidth: 0 }}>
            {about.state === 'missing' && <p data-missing="" style={note}>{noEntry(about.missing)}</p>}
            {about.state === 'ready' && (
              <>
                <Eyebrow as="div" tone="accent">{about.term}</Eyebrow>
                <h1 data-about-definition="" style={{ font: 'var(--fw-reg) clamp(24px, 2.3vw, var(--fs-d2))/1.22 var(--display)',
                  letterSpacing: 'var(--tr-display)', color: 'var(--text-body)', margin: '12px 0 0', maxWidth: '26em' }}>
                  {about.definition}
                </h1>
              </>
            )}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 26, alignItems: 'center' }}>
              <a href={resume ? resume.href : (doors.brief ? doors.brief.href : '#/brief')} data-front-act="continue"
                data-resume={resume ? resume.id : undefined}
                style={{ padding: '9px 18px', background: 'var(--gilt)', color: 'var(--text-on-gilt)', borderBottom: 'none',
                  font: 'var(--fw-med) 15px/1.3 var(--body)' }}>
                <Term id="front-door-continue" />
              </a>
              <a href={doors.brief ? doors.brief.href : '#/brief'} data-front-act="new-brief" data-entrance-link="brief"
                style={{ padding: '8px 16px', border: '1px solid var(--border-paper)', borderBottom: '1px solid var(--border-paper)',
                  font: 'var(--fw-reg) 15px/1.3 var(--body)' }}>
                <Term id="front-door-new-brief" />
              </a>
            </div>
            {resume && resume.plan && plan && (
              <p style={{ ...small, color: 'var(--text-secondary)', margin: '12px 0 0' }}>
                <Term id="on-the-bench" />
                <span style={{ marginLeft: 7, color: 'var(--text-body)' }}>{plan.name || plan.id}</span>
                {resume.origin && (
                  <span data-resume-origin="" style={{ ...note, marginLeft: 7, display: 'inline-block' }}>
                    {JOURNEY_WORDS.separator}{resume.origin}
                  </span>
                )}
              </p>
            )}
          </header>
          <Hero />
        </div>

        {/* THE JOURNEY, as five stations on a rule. */}
        <section data-stations="" style={{ marginTop: 44 }}>
          <Eyebrow as="h2" style={{ margin: 0 }}><Term id="nav-group-a-house" /></Eyebrow>
          <ol style={{ position: 'relative', display: 'grid', gap: 12, margin: '14px 0 0', padding: 0,
            gridTemplateColumns: 'repeat(auto-fit, minmax(10rem, 1fr))' }}>
            <span aria-hidden="true" style={{ position: 'absolute', left: 0, right: 0, top: '50%',
              borderTop: '1px solid var(--border-paper)' }} />
            {tiles.map((t) => <Station key={t.id} t={t} />)}
          </ol>
        </section>

        {/* THE LIBRARY, as five cards with a drawn figure and the API's count. */}
        <section data-library="" style={{ marginTop: 40 }}>
          <Eyebrow as="h2" style={{ margin: 0 }}><Term id="nav-group-library" /></Eyebrow>
          <div style={{ display: 'grid', gap: 14, marginTop: 14, gridTemplateColumns: 'repeat(auto-fit, minmax(13rem, 1fr))' }}>
            {cards.map((c) => (
              <LibraryCard key={c.id} c={c} entrance={c.id === 'style' ? 'style' : null}>
                {c.id === 'style' && doors.inHand && (
                  <p style={{ ...small, margin: 0 }}>
                    <a href={doors.inHand.href} data-entrance-link="in-hand">
                      <Word label={doors.inHand.label} missing={doors.inHand.missing} />
                    </a>
                  </p>
                )}
              </LibraryCard>
            ))}
          </div>
        </section>

        {/* The one invitation that is not a place: look something up. */}
        <button type="button" onClick={onSearch}
          style={{ display: 'flex', alignItems: 'center', gap: 14, width: '100%', maxWidth: 560,
            margin: '28px 0 0', padding: '11px 15px', textAlign: 'left',
            border: '1px solid var(--border-paper)', background: 'var(--surface-well)',
            transition: 'var(--t-hover)' }}>
          <span style={{ font: 'var(--fw-reg) 15px/1.4 var(--body)', color: 'var(--text-secondary)' }}>
            Search the corpus
          </span>
          <span style={{ flex: 1 }} />
          <span style={{ ...note, fontFamily: 'var(--mono)' }}>⌘K</span>
        </button>

        {/* THE WORKED EXAMPLE, WHAT IT HOLDS, and WHAT IT IS NOT: the closing furniture. */}
        <div style={{ marginTop: 40, display: 'grid', gap: '26px 40px',
          gridTemplateColumns: 'repeat(auto-fit, minmax(17rem, 1fr))', alignItems: 'start' }}>
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
                    borderLeft: '2px solid var(--border-hairline)' }}>{guided.more}</p>
                )}
              </>
            )}
          </section>

          <section data-inventory="" style={{ ...rule, paddingTop: 10, minWidth: 0 }}>
            <Eyebrow as="h2" data-heading="front-door-holds" style={{ margin: 0 }}>
              <Term id="front-door-holds" />
            </Eyebrow>
            <div data-ontology-version={o ? o.ontology_version : undefined}
              style={{ ...note, margin: '4px 0 0' }}>
              {o ? `ontology ${o.ontology_version}` : ' '}
            </div>
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
            <section data-is-not-section="" style={{ ...rule, paddingTop: 10, minWidth: 0 }}>
              <Eyebrow as="h2" data-heading="front-door-is-not" style={{ margin: 0 }}>
                <Term id="front-door-is-not" />
              </Eyebrow>
              <ul data-is-not="" style={{ listStyle: 'none', padding: '4px 0 0', margin: 0, minWidth: 0 }}>
                {about.isNot.map((line) => (
                  <li key={line} style={{ ...small, color: 'var(--text-secondary)', padding: '4px 0' }}>{line}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

const invRow = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12,
  borderBottom: '1px solid var(--border-soft)', padding: '3px 0',
  font: 'var(--fw-reg) var(--fs-body-s)/1.4 var(--serif)', color: 'var(--text-body)',
};
const figure = { margin: 0, font: 'var(--type-data)', color: 'var(--text-body)' };
