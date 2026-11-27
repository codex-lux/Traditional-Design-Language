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

   REDRAWN AS THE THRESHOLD (26 Nov 2026, the two rooms). The page stands between the drafting
   room and the library and shows both: a dark band first, where the thesis is set at display size
   beside the lit plate and the house's five steps run as stations on one line; then the library
   below it on paper, five cards and the closing furniture. The thesis is `about-tdl`'s one
   sentence, set in two sizes: its first clause as the headline and the rest as the lede
   (`thesisParts`), every word the record's and in the record's order. Nothing else on the page
   changed hands -- the same records, the same routes, the same `data-` hooks.

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
  aboutView, guidedView, rankRows, total, entranceItems, resumeView, stationTiles, libraryCards, thesisParts,
} from '../frontdoor/frontDoor.js';
import { isMissing } from '../glossary/lookup.js';
import { Term, noEntry } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Plate } from '../components/Plate.jsx';
import { MarkGlyph } from '../components/MarkGlyph.jsx';
import { GLYPHS } from '../frontdoor/glyphs.js';
import { sidebarView } from '../nav/sidebar.js';
import { barView } from '../journey/bar.js';

const prose = { font: 'var(--type-prose)', color: 'var(--text-body)', margin: 0 };
const small = { font: 'var(--fw-reg) var(--fs-body-s)/var(--lh-body) var(--serif)', color: 'var(--text-body)' };
const note = { font: 'var(--type-data-s)', color: 'var(--text-secondary)' };
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
    <Plate className={svg ? 'tdl-hero-plate tdl-plate-in' : 'tdl-hero-plate'}
      data-hero={hero ? (hero.refused ? 'refused' : hero.plan_id || '') : (failed ? 'failed' : 'loading')}
      caption={hero && !hero.refused ? <><Term id="front-door-hero" />{JOURNEY_WORDS.separator}{hero.name}{engine ? JOURNEY_WORDS.separator + engine : ''}</> : null}>
      {svg && <div className="plate-fit" dangerouslySetInnerHTML={{ __html: svg }} />}
      {!svg && !hero && !failed && (
        <div aria-busy="true" style={{ padding: '18vh 40px', textAlign: 'center' }}><MarkGlyph token="--mark-loading"><Term id="front-door-hero" /></MarkGlyph></div>
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

/* One station on the line: its mark, its number and name, and the journey's words for it. A
   blocked step is drawn and is not a link, as in the sidebar. */
function Station({ t }) {
  const body = (
    <>
      <span className="tdl-station-mark"><MarkGlyph token={t.mark} size={15} /></span>
      <span className="tdl-station-name">
        <span className="tdl-station-n">{t.n}</span><Word label={t.label} missing={t.missing} />
      </span>
      {t.words && (
        <span className="tdl-station-words" data-refused={t.state === 'refused' ? '' : undefined}>{t.words}</span>
      )}
    </>
  );
  return (
    <li data-station={t.id} data-station-mark={t.mark} style={{ minWidth: 0 }}>
      {t.href
        ? <a href={t.href} data-station-link={t.id} className="tdl-station">{body}</a>
        : <span className="tdl-station">{body}</span>}
    </li>
  );
}

/* A library card: the drawn figure, the API's count, the place's name and its record's line.
   The name is the card's link and its hit area is the whole card (`tdl-stretch`); a second link
   inside the card stands above it. */
function LibraryCard({ c, entrance, children }) {
  const paths = GLYPHS[c.id] || [];
  return (
    <section data-library-card={c.id} data-lifts="" className="tdl-card tdl-library-card"
      style={{ background: 'var(--surface-lit)' }}>
      <span style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
        {paths.length > 0 && (
          <svg aria-hidden="true" width="52" height="52" viewBox="0 0 40 40" style={{ flex: 'none' }}>
            {paths.map((d, i) => <path key={i} d={d} fill="none" stroke="var(--heavy)"
              strokeWidth="var(--lw-fine)" vectorEffect="non-scaling-stroke" />)}
          </svg>
        )}
        {c.figure != null && <span data-card-figure="" className="tdl-card-figure">{c.figure}</span>}
      </span>
      <a href={c.href} data-entrance-link={entrance || undefined} className="tdl-card-title tdl-stretch"
        style={{ alignSelf: 'flex-start', marginTop: 6 }}>
        <Word label={c.label} missing={c.missing} />
      </a>
      {c.what && <p className="tdl-card-text">{c.what}</p>}
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
  const bar = barView(journey, { surface: 'overview', jobId: sess ? sess.jobId : null });
  const tiles = model ? stationTiles(bar, journey.resume, model) : [];
  const cards = model ? libraryCards(sidebarView(model, { bar, resume: journey.resume, surface: 'overview' }), lookup) : [];

  const thesis = about.state === 'ready' ? thesisParts(about.definition) : null;

  return (
    <div data-front-door="" className="tdl-scroll">
      {/* THE DRAFTING ROOM: the thesis, the act, a real plate lit beside them, and the journey. */}
      <section className="tdl-threshold" data-ground="instrument" data-threshold="">
        <div className="tdl-threshold-inner">
          <div className="tdl-threshold-grid">
            <header data-about="" className="tdl-rise" aria-busy={about.state === 'loading' ? 'true' : undefined} style={{ minWidth: 0 }}>
              {about.state === 'missing' && <p data-missing="" style={note}>{noEntry(about.missing)}</p>}
              {about.state === 'ready' && (
                <>
                  <Eyebrow as="div" tone="accent">{about.term}</Eyebrow>
                  {/* one sentence, the record's, in two sizes */}
                  <h1 data-about-definition="" className="tdl-thesis">
                    {thesis.head}
                    {thesis.rest && <span className="tdl-hero-lede" style={{ display: 'block', letterSpacing: 0 }}> {thesis.rest}</span>}
                  </h1>
                </>
              )}
              <div className="tdl-hero-acts" style={{ marginTop: 30 }}>
                <a href={resume ? resume.href : (doors.brief ? doors.brief.href : '#/brief')} data-front-act="continue"
                  data-resume={resume ? resume.id : undefined} className="tdl-act tdl-act-primary">
                  <Term id="front-door-continue" /><span className="tdl-act-arrow" aria-hidden="true">→</span>
                </a>
                <a href={doors.brief ? doors.brief.href : '#/brief'} data-front-act="new-brief" data-entrance-link="brief"
                  className="tdl-act">
                  <Term id="front-door-new-brief" />
                </a>
              </div>
              {resume && resume.plan && plan && (
                <p style={{ ...small, color: 'var(--text-secondary)', margin: '14px 0 0' }}>
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

          {/* THE JOURNEY, as five stations on one line. */}
          <section data-stations="" className="tdl-rise-3" style={{ marginTop: 'clamp(34px, 6vh, 64px)' }}>
            <Eyebrow as="h2" style={{ margin: '0 0 18px', textAlign: 'center' }}><Term id="nav-group-a-house" /></Eyebrow>
            <ol className="tdl-stations">
              {tiles.map((t) => <Station key={t.id} t={t} />)}
            </ol>
          </section>
        </div>
      </section>

      {/* THE LIBRARY, on paper: five cards with a drawn figure and the API's count. */}
      <div className="tdl-library-band">
        <section data-library="">
          <div className="tdl-section-head">
            <h2 className="tdl-section-title"><Term id="nav-group-library" /></h2>
            <button type="button" onClick={onSearch} className="tdl-quiet-link tdl-link" data-front-search="">
              Search the corpus <kbd style={{ ...note, marginLeft: 6 }}>⌘K</kbd>
            </button>
          </div>
          <div className="tdl-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(11.5rem, 1fr))' }}>
            {cards.map((c) => (
              <LibraryCard key={c.id} c={c} entrance={c.id === 'style' ? 'style' : null}>
                {c.id === 'style' && doors.inHand && (
                  <p className="tdl-card-text" style={{ position: 'relative', zIndex: 1, marginTop: 'auto' }}>
                    <a href={doors.inHand.href} data-entrance-link="in-hand">
                      <Word label={doors.inHand.label} missing={doors.inHand.missing} />
                    </a>
                  </p>
                )}
              </LibraryCard>
            ))}
          </div>
        </section>

        {/* THE WORKED EXAMPLE, WHAT IT HOLDS, and WHAT IT IS NOT: the closing furniture. */}
        <div className="tdl-colophon" style={{ marginTop: 56 }}>
          <section data-guided-example="" style={{ minWidth: 0 }}>
            {guided.state === 'missing' && <p data-missing="" style={note}>{noEntry(guided.missing)}</p>}
            {guided.state === 'ready' && (
              <>
                <div className="tdl-rule-double" />
                <Eyebrow as="h2" style={{ margin: '12px 0 0' }}>{guided.word}</Eyebrow>
                <p data-guided-definition="" style={{ ...prose, margin: '10px 0 0' }}>{guided.definition}</p>
                {guided.cites.length > 0 && (
                  <ul style={{ listStyle: 'none', padding: 0, margin: '12px 0 0' }}>
                    {guided.cites.map((c) => (
                      <li key={c} style={{ ...small, padding: '4px 0' }}>
                        <RecordLink cite={c}>{c === guided.briefCite && briefName ? briefName : undefined}</RecordLink>
                      </li>
                    ))}
                  </ul>
                )}
                {/* WHERE IT STOPS, in the record's words and no others. */}
                {guided.more && (
                  <p data-guided-stop="" style={{ ...small, color: 'var(--text-secondary)', margin: '12px 0 0', paddingLeft: 12,
                    borderLeft: '2px solid var(--border-hairline)' }}>{guided.more}</p>
                )}
              </>
            )}
          </section>

          <section data-inventory="" style={{ minWidth: 0 }}>
            <div className="tdl-rule-double" />
            <Eyebrow as="h2" data-heading="front-door-holds" style={{ margin: '12px 0 0' }}>
              <Term id="front-door-holds" />
            </Eyebrow>
            <div data-ontology-version={o ? o.ontology_version : undefined}
              style={{ ...note, margin: '4px 0 0' }}>
              {o ? `ontology ${o.ontology_version}` : ' '}
            </div>
            {counts && (
              <dl style={{ margin: '10px 0 0' }}>
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
            <section data-is-not-section="" style={{ minWidth: 0 }}>
              <div className="tdl-rule-double" />
              <Eyebrow as="h2" data-heading="front-door-is-not" style={{ margin: '12px 0 0' }}>
                <Term id="front-door-is-not" />
              </Eyebrow>
              <ul data-is-not="" style={{ listStyle: 'none', padding: '6px 0 0', margin: 0, minWidth: 0 }}>
                {about.isNot.map((line) => (
                  <li key={line} style={{ ...small, color: 'var(--text-secondary)', padding: '5px 0' }}>{line}</li>
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
  borderBottom: '1px solid var(--border-soft)', padding: '5px 0',
  font: 'var(--fw-reg) var(--fs-body)/1.4 var(--serif)', color: 'var(--text-body)',
};
const figure = { margin: 0, font: 'var(--type-data)', color: 'var(--text-body)' };
