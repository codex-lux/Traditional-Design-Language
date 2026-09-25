/* The Workbench shell. All eleven surfaces are live (⑪ Transcription joined in
   WP-5.5). The AI rail is persistent across all of them. A citation anywhere routes
   through citations.js and navigates this shell — and since WP-5.6 that navigation is
   written to the URL (router.js, state/nav.js), so a place can be refreshed, gone back
   from, and handed to somebody else.

   WP-5.7 made the shell's proportions the reader's. Both rails fold and both pull
   (state/layout.js, components/Splitter.jsx), and a surface can take the whole window —
   `layout.full`, which the atlas asks for and escape gives back. What the layout store
   holds is a preference about this browser, so it lives in localStorage; it deliberately
   stays out of the URL, because a citation that carried the sender's rail width would be
   handing the reader the sender's monitor.

   WP-14.13 made every page say where it is, what it is and what comes next. The rail, the
   crumb strip and the tab title are `nav/navModel.js`'s and `nav/crumbs.js`'s, fed from here
   with what only the shell holds — the place, the glossary, the names, the style list, the
   style in hand, the journey and the counts — and each page is headed by its own glossary
   record (`PageHead`). The URL decides what is read; per-browser memory only offers. */
import React from 'react';
import { api, setUnauthorizedHandler } from './api/client.js';
import { planDoc } from './state/planDoc.js';
import { nav } from './state/nav.js';
import { useGlobalKeys, requestFilterFocus } from './keys.js';
import { CommandPalette } from './palette/CommandPalette.jsx';
import { ShortcutCard } from './palette/ShortcutCard.jsx';
import { Masthead, LeftRail, PaneStub, CrumbStrip } from './Chrome.jsx';
import { Splitter } from './components/Splitter.jsx';
import { JourneyBar, showJourneyBar } from './components/JourneyBar.jsx';
import { layout, PANES, surfaceWidth, MAIN_FLOOR_PX } from './state/layout.js';
import { Gate } from './Gate.jsx';
import { RailHost, assistantName } from './rail/RailHost.jsx';
import { PageHead } from './components/PageHead.jsx';
import { ColdLinkBanner } from './components/ColdLinkBanner.jsx';
import { useGlossary } from './api/useGlossary.js';
import { useNames } from './names/useNames.js';
import { useStyles } from './api/useStyles.js';
import { prefs } from './state/prefs.js';
import { session } from './state/session.js';
import { journeyState, evalPlanOf } from './journey/journey.js';
import { navModel, headTermFor, inHandFrom, normalizePlace, stylePlaceKind } from './nav/navModel.js';
import { crumbsFor, titleFor } from './nav/crumbs.js';
import { PlanWorkbench } from './surfaces/PlanWorkbench.jsx';
import { CandidateSet } from './surfaces/CandidateSet.jsx';
import { FaultCorpus } from './surfaces/FaultCorpus.jsx';
import { Phylogeny } from './surfaces/Phylogeny.jsx';
import { BriefIntake } from './surfaces/BriefIntake.jsx';
import { StyleDossier } from './surfaces/StyleDossier.jsx';
import { Proportions } from './surfaces/Proportions.jsx';
import { DrawingSet } from './surfaces/DrawingSet.jsx';
import { ExportDetails } from './surfaces/ExportDetails.jsx';
import { Transcription } from './surfaces/Transcription.jsx';
import { Overview } from './surfaces/Overview.jsx';
import { Glossary } from './surfaces/Glossary.jsx';
import { Elements } from './surfaces/Elements.jsx';
import { RoomPage, MassingPage, GroupingPage, PartiPage } from './surfaces/RecordPage.jsx';
import { Compare } from './surfaces/Compare.jsx';

const SURFACES = {
  overview: Overview,
  workbench: PlanWorkbench,
  candidates: CandidateSet,
  faults: FaultCorpus,
  phylogeny: Phylogeny,
  brief: BriefIntake,
  style: StyleDossier,
  proportions: Proportions,
  drawings: DrawingSet,
  export: ExportDetails,
  transcription: Transcription,
  glossary: Glossary,
  // the Elements index and the four plan-type record pages (WP-14.23, tranche 2 §B)
  elements: Elements,
  room: RoomPage,
  massing: MassingPage,
  grouping: GroupingPage,
  parti: PartiPage,
  // two styles side by side (WP-14.26, tranche 2 §B.1)
  compare: Compare,
};

export default function App() {
  const place = React.useSyncExternalStore(nav.subscribe, nav.get);
  const { surface, selection } = place;
  const [overview, setOverview] = React.useState(null);
  const [health, setHealth] = React.useState(null);
  const [lastEval, setLastEval] = React.useState(null);
  // null while unknown — rendering the shell before we know would flash it at a locked
  // visitor, and rendering the gate before we know would flash it at an open server.
  const [locked, setLocked] = React.useState(null);
  /* A server that does not answer is SAID, not drawn as a blank page (WP-14.13). `locked`
     stays null until /api/health answers, and it used to stay null for ever when it could
     not, which rendered nothing at all — to a stranger handed the URL during a slow boot, a
     broken product. */
  const [bootFailed, setBootFailed] = React.useState(false);
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);

  const boot = React.useCallback(() => {
    setBootFailed(false);
    // /api/health is never gated, so it answers either way and tells us which way.
    api.health().then((h) => {
      setHealth(h);
      if (!h.auth?.required) { setLocked(false); }
      /* SIGNED OUT, NOTHING GATED IS ASKED (WP-14.20). A password is set and /api/health says
         this request carries no session -- the gate's own answer, `auth.authorised` -- so the
         Gate shows and no gated route is called to find that out. Until WP-14.20 the only way to
         learn it was to probe `/api/overview` and take the 401, which put one gated request on
         every signed-out visit (the walk's Gate block counts them, and must count none). A
         server that does not state `session` is the one case left to the probe below, because
         there a real request is still the only way to find out. */
      else if (h.session === false) { setLocked(true); return undefined; }
      return api.overview()
        .then((o) => { setOverview(o); setLocked(false); })
        .catch((e) => {
          if (e.status === 401) setLocked(true);
          else if (h.auth?.required) setBootFailed(true);   // still unknown which way: say so
        });
    }).catch(() => { setHealth({ ok: false }); setBootFailed(true); });
  }, []);

  React.useEffect(boot, [boot]);

  // Any 401 after boot means the session went away — a redeploy, or an expiry. Show the
  // gate again rather than letting every surface render an error.
  React.useEffect(() => {
    setUnauthorizedHandler(() => setLocked(true));
    return () => setUnauthorizedHandler(null);
  }, []);

  const [palette, setPalette] = React.useState(false);
  const [helpCard, setHelpCard] = React.useState(false);
  const panes = React.useSyncExternalStore(layout.subscribe, layout.get);
  /* Full screen belongs to ONE surface. `layout.full` holds which, and this render treats
     it as off anywhere else — because ⌘K still works in full screen, and a palette jump
     from the atlas to the Kit used to carry the chrome-less shell along with it, onto a
     surface with no control to leave by. The effect below clears the state so the browser's
     own full screen goes with it rather than lingering. */
  const full = panes.full === surface ? panes.full : null;

  /* A width stored on a wide monitor must not strand the nav off the side of a laptop,
     and the two rails together must never eat the canvas between them. The store holds
     the absolute bounds; only the window knows the situational one. */
  React.useEffect(() => {
    const fit = () => layout.clampAll(window.innerWidth);
    fit();
    window.addEventListener('resize', fit);
    return () => window.removeEventListener('resize', fit);
  }, []);

  /* Leaving the browser's own full screen — by F11, by the escape key the browser eats
     before we see it, by anything — must also leave ours, or the reader is left in a
     chrome-less shell they did not ask for. */
  React.useEffect(() => {
    if (typeof document === 'undefined') return undefined;
    const sync = () => { if (!document.fullscreenElement && layout.get().full) layout.setFull(null); };
    document.addEventListener('fullscreenchange', sync);
    return () => document.removeEventListener('fullscreenchange', sync);
  }, []);

  /* Declared above the key map that calls it: leaving our full screen must also leave
     the browser's, and the two have to be the same act or the reader ends up in one
     without the other. */
  const exitFull = React.useCallback(() => {
    layout.setFull(null);
    if (typeof document !== 'undefined' && document.fullscreenElement && document.exitFullscreen) {
      document.exitFullscreen().catch(() => {});
    }
  }, []);

  React.useEffect(() => {
    if (layout.get().full && layout.get().full !== surface) exitFull();
  }, [surface, exitFull]);

  useGlobalKeys({
    onPalette: () => { setHelpCard(false); setPalette((p) => !p); },
    onHelp: () => { setPalette(false); setHelpCard(true); },
    onSlash: () => { requestFilterFocus(); },
    onEscape: () => {
      if (palette) setPalette(false);
      else if (helpCard) setHelpCard(false);
      else if (layout.get().full) exitFull();
    },
    /* Two keys, added deliberately — see keys.js. The reason is the one the rails
       themselves are the answer to: 580px of permanent furniture is worth a key.

       Inert where there is nothing to fold. In full screen both rails are already gone and
       no modal is dismissed by them, so the keys used to flip state invisibly — and leaving
       full screen then revealed a rail the reader did not remember folding. A key that
       silently changes something you cannot see is worse than a key that does nothing. */
    onFoldNav: () => { if (!layout.get().full && !palette && !helpCard) layout.toggle('nav'); },
    onFoldRail: () => { if (!layout.get().full && !palette && !helpCard) layout.toggle('rail'); },
  });

  const cite = React.useCallback((ref) => nav.cite(ref), []);
  const select = React.useCallback((patch) => nav.select(patch), []);
  const go = React.useCallback((s, sel) => nav.go(s, sel), []);

  const shared = { onCite: cite, selection, setSelection: select, go, lastEval, setLastEval,
    onSearch: () => setPalette(true), full, onFull: layout.setFull, onExitFull: exitFull };
  // Only the surface in view is constructed. It used to be all eleven, every render,
  // each with its own mount effects waiting to fire.
  const Active = SURFACES[surface] || SURFACES.workbench;

  /* ── Where you are (WP-14.13). ─────────────────────────────────────────────────────── */
  /* Nothing gated is asked while the lock is unknown or shut (PRD §C.3): the Gate is the one
     place a signed-out browser may read, and it reads one record. `locked === false` is the
     only state in which these three may fetch, and they fetch when it arrives. */
  const unlocked = locked === false;
  const glossary = useGlossary(unlocked);
  const lookup = glossary.lookup;
  const names = useNames(unlocked);
  const { styles } = useStyles(unlocked);
  const memory = React.useSyncExternalStore(prefs.subscribe, prefs.get);
  const sessionNow = React.useSyncExternalStore(session.subscribe, session.get);

  /* An evaluation belongs to the plan it was of. `lastEval` outlived a plan change, so a newly
     loaded plan's name could sit beside the previous plan's counts in the masthead. It is
     cleared when the plan's id changes — UNLESS it is already this plan's: the bench loads a
     revised record and sets its evaluation in one tick, and a blanket clear running after
     both would throw away the verdict it had just been handed. Which plan an evaluation was of
     is `evalPlanOf`'s answer, the journey's own reader, so an evaluation whose check errored --
     which names its plan only at the top of the route's response -- is kept for its plan here
     exactly as the journey reads it (WP-14.20). */
  const planId = plan ? plan.id : null;
  const lastPlanId = React.useRef(planId);
  React.useEffect(() => {
    if (lastPlanId.current === planId) return;
    lastPlanId.current = planId;
    setLastEval((ev) => (ev && evalPlanOf(ev) === planId ? ev : null));
  }, [planId]);

  /* The style dossier's head, for a style's place: its chain names the crumbs and its sections
     are the in-hand item's children. Read through the GET cache, which the dossier surface
     shares, so a place costs one request however many readers it has. */
  const here = normalizePlace(place);
  const dossierStyle = here.surface === 'style' && stylePlaceKind(here.selection) === 'dossier'
    ? here.selection.style : null;
  const [dossier, setDossier] = React.useState(null);
  React.useEffect(() => {
    if (!dossierStyle) return undefined;
    let live = true;
    api.styleDossier(dossierStyle)
      .then((d) => { if (live) setDossier(d && typeof d === 'object' ? d : null); })
      .catch(() => { if (live) setDossier(null); });
    return () => { live = false; };
  }, [dossierStyle]);
  const dossierHere = dossier && dossier.id === dossierStyle ? dossier : null;

  const styleName = React.useCallback((id) => {
    const n = names.nameFor(`style:${id}`);
    if (n.resolved) return n.name;
    const s = styles.find((x) => x.id === id);
    return s ? s.name : null;
  }, [names, styles]);
  const inHand = inHandFrom(memory.styleInHand, lookup, styleName);
  const journey = journeyState({ session: sessionNow, plan, lastEval });
  const model = navModel({
    lookup, counts: overview?.counts, glossaryCount: lookup ? lookup.count : null,
    inHand, dossier: dossierHere, journey, place,
  });
  const crumbs = crumbsFor(place, { lookup, dossier: dossierHere, names: names.index, styles, journey });
  const title = titleFor(crumbs, lookup);
  React.useEffect(() => {
    if (title && typeof document !== 'undefined') document.title = title;
  }, [title]);

  /* Whether the page in view reflows or keeps a floor, from `state/layout.js`'s table (WP-14.30,
     tranche 2 PRD §E). This used to be a hard-coded pair, the front door and the Glossary, each
     releasing a 1380 px floor on `#root` that every other page kept; the floor is gone. A
     'reflow' page is marked `data-reflow` and takes the window. A 'floor' page is marked
     `data-floor`, and the stylesheet holds `<main>`'s content to `--main-floor` and lets `<main>`
     scroll sideways inside itself, so the masthead and its Keys button stay on screen. An id the
     table does not hold is judged as the surface that actually renders, which is the bench.
     A LAYOUT effect, because a plain one paints a floored page for one frame without its floor. */
  React.useLayoutEffect(() => {
    const root = typeof document !== 'undefined' ? document.getElementById('root') : null;
    if (!root) return;
    const floored = surfaceWidth(SURFACES[surface] ? surface : 'workbench') === 'floor';
    root.toggleAttribute('data-reflow', !floored);
    root.toggleAttribute('data-floor', floored);
    root.style.setProperty('--main-floor', `${MAIN_FLOOR_PX}px`);
  }, [surface]);

  /* The first place this page loaded, and whether it was a cold deep link. Visiting the front
     door is having seen it. */
  const firstPlace = React.useRef(place);
  React.useEffect(() => { if (surface === 'overview') prefs.markSeen('front-door'); }, [surface]);
  const coldLink = firstPlace.current.surface !== 'overview' && !memory.seen['front-door'];

  const railName = assistantName(glossary);

  if (locked === null) {                            // one frame, before we know which
    if (!bootFailed) return null;
    return (
      <div role="status" data-boot-status=""
        style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: 10, font: 'var(--fw-reg) 15px/1.5 var(--body)', color: 'var(--ink)',
          background: 'var(--paper)' }}>
        Cannot reach the server
        <span aria-hidden="true" style={{ color: 'var(--ink-3)' }}>·</span>
        <button type="button" onClick={boot}
          style={{ font: 'inherit', color: 'var(--link)', borderBottom: '1px solid var(--link-underline)' }}>
          Retry
        </button>
      </div>
    );
  }
  if (locked) return <Gate onUnlocked={boot} auth={health?.auth} />;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Full screen takes the masthead and both rails, not just the rails: on the
          laptop this was reported from, the masthead plus the browser's own bookmark bar
          was more of the window than the atlas's legend. It is a state of the shell
          rather than a mode of the surface, so every surface can ask for it and none of
          them has to reimplement getting out. */}
      {!full && (
        <Masthead plan={plan} planStep={journey.steps.find((s) => s.id === 'plan')}
          onSearch={() => setPalette(true)}
          onKeys={() => { setPalette(false); setHelpCard(true); }} />
      )}
      {!full && coldLink && (
        <ColdLinkBanner crumbs={crumbs} onDismiss={() => prefs.markSeen('front-door')} />
      )}
      {!full && <CrumbStrip crumbs={crumbs} />}
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {!full && <LeftRail model={model} busy={glossary.status === 'loading'} />}
        {!full && layout.isOpen('nav') && <Splitter pane="nav" grows="left" />}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, minHeight: 0 }}>
          {!full && <PageHead termId={headTermFor(place)} />}
          {showJourneyBar(surface, full) && <JourneyBar surface={surface} lastEval={lastEval} />}
          <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, minHeight: 0 }}>
            <Active {...shared} />
          </main>
        </div>
        {!full && layout.isOpen('rail') && <Splitter pane="rail" grows="right" />}
        {!full && (layout.isOpen('rail')
          ? (
            <RailHost onCite={cite} surface={surface} plan={plan} lastEval={lastEval}
              railAvailable={health ? !!health.rail : null}
              toolCount={health?.mcp?.tools} />
          )
          : <PaneStub pane="rail" label={PANES.rail.label} spine={railName} side="right" />)}
      </div>
      <CommandPalette open={palette} onClose={() => setPalette(false)}
        onAction={(run) => { if (run === 'help') setHelpCard(true); }} />
      <ShortcutCard open={helpCard} onClose={() => setHelpCard(false)} />
    </div>
  );
}
