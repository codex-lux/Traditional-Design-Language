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
   handing the reader the sender's monitor. */
import React from 'react';
import { api, setUnauthorizedHandler } from './api/client.js';
import { planDoc } from './state/planDoc.js';
import { nav } from './state/nav.js';
import { useGlobalKeys, requestFilterFocus } from './keys.js';
import { CommandPalette } from './palette/CommandPalette.jsx';
import { ShortcutCard } from './palette/ShortcutCard.jsx';
import { Masthead, LeftRail, PaneStub } from './Chrome.jsx';
import { Splitter } from './components/Splitter.jsx';
import { layout } from './state/layout.js';
import { Gate } from './Gate.jsx';
import { RailHost } from './rail/RailHost.jsx';
import { PlanWorkbench } from './surfaces/PlanWorkbench.jsx';
import { CandidateSet } from './surfaces/CandidateSet.jsx';
import { FaultCorpus } from './surfaces/FaultCorpus.jsx';
import { KitSurface } from './surfaces/KitSurface.jsx';
import { Phylogeny } from './surfaces/Phylogeny.jsx';
import { BriefIntake } from './surfaces/BriefIntake.jsx';
import { StyleRecord } from './surfaces/StyleRecord.jsx';
import { Proportions } from './surfaces/Proportions.jsx';
import { DrawingSet } from './surfaces/DrawingSet.jsx';
import { ExportDetails } from './surfaces/ExportDetails.jsx';
import { Transcription } from './surfaces/Transcription.jsx';
import { Overview } from './surfaces/Overview.jsx';

const SURFACES = {
  overview: Overview,
  workbench: PlanWorkbench,
  candidates: CandidateSet,
  faults: FaultCorpus,
  kit: KitSurface,
  phylogeny: Phylogeny,
  brief: BriefIntake,
  style: StyleRecord,
  proportions: Proportions,
  drawings: DrawingSet,
  export: ExportDetails,
  transcription: Transcription,
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
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);

  const boot = React.useCallback(() => {
    // /api/health is never gated, so it answers either way and tells us which way.
    api.health().then((h) => {
      setHealth(h);
      if (!h.auth?.required) { setLocked(false); }
      // A password is set, but this browser may already hold a session. One real
      // request is the only way to find out.
      return api.overview()
        .then((o) => { setOverview(o); setLocked(false); })
        .catch((e) => { if (e.status === 401) setLocked(true); });
    }).catch(() => setHealth({ ok: false }));
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
       themselves are the answer to: 580px of permanent furniture is worth a key. */
    onFoldNav: () => layout.toggle('nav'),
    onFoldRail: () => layout.toggle('rail'),
  });

  const cite = React.useCallback((ref) => nav.cite(ref), []);
  const select = React.useCallback((patch) => nav.select(patch), []);
  const go = React.useCallback((s, sel) => nav.go(s, sel), []);

  const shared = { onCite: cite, selection, setSelection: select, go, lastEval, setLastEval,
    onSearch: () => setPalette(true), full, onFull: layout.setFull, onExitFull: exitFull };
  // Only the surface in view is constructed. It used to be all eleven, every render,
  // each with its own mount effects waiting to fire.
  const Active = SURFACES[surface] || SURFACES.workbench;

  const unjudged = lastEval?.check?.constraint_summary?.unjudged;

  if (locked === null) return null;                 // one frame, before we know which
  if (locked) return <Gate onUnlocked={boot} auth={health?.auth} />;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Full screen takes the masthead and both rails, not just the rails: on the
          laptop this was reported from, the masthead plus the browser's own bookmark bar
          was more of the window than the atlas's legend. It is a state of the shell
          rather than a mode of the surface, so every surface can ask for it and none of
          them has to reimplement getting out. */}
      {!full && <Masthead plan={plan} judgment={unjudged} onSearch={() => setPalette(true)} />}
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {!full && <LeftRail current={surface} onGo={go} counts={overview?.counts} />}
        {!full && layout.isOpen('nav') && <Splitter pane="nav" grows="left" />}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, minHeight: 0 }}>
          <Active {...shared} />
        </main>
        {!full && layout.isOpen('rail') && <Splitter pane="rail" grows="right" />}
        {!full && (layout.isOpen('rail')
          ? (
            <RailHost onCite={cite} surface={surface} plan={plan} lastEval={lastEval}
              railAvailable={health ? !!health.rail : null}
              toolCount={health?.mcp?.tools} />
          )
          : <PaneStub pane="rail" label="the rail" side="right" />)}
      </div>
      <CommandPalette open={palette} onClose={() => setPalette(false)}
        onAction={(run) => { if (run === 'help') setHelpCard(true); }} />
      <ShortcutCard open={helpCard} onClose={() => setHelpCard(false)} />
    </div>
  );
}
