/* The Workbench shell. All eleven surfaces are live (⑪ Transcription joined in
   WP-5.5). The AI rail is persistent across all of them. A citation anywhere routes
   through citations.js and navigates this shell — and since WP-5.6 that navigation is
   written to the URL (router.js, state/nav.js), so a place can be refreshed, gone back
   from, and handed to somebody else. */
import React from 'react';
import { api, setUnauthorizedHandler } from './api/client.js';
import { planDoc } from './state/planDoc.js';
import { nav } from './state/nav.js';
import { useGlobalKeys, requestFilterFocus } from './keys.js';
import { CommandPalette } from './palette/CommandPalette.jsx';
import { ShortcutCard } from './palette/ShortcutCard.jsx';
import { Masthead, LeftRail } from './Chrome.jsx';
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

  useGlobalKeys({
    onPalette: () => { setHelpCard(false); setPalette((p) => !p); },
    onHelp: () => { setPalette(false); setHelpCard(true); },
    onSlash: () => { requestFilterFocus(); },
    onEscape: () => {
      if (palette) setPalette(false);
      else if (helpCard) setHelpCard(false);
    },
  });

  const cite = React.useCallback((ref) => nav.cite(ref), []);
  const select = React.useCallback((patch) => nav.select(patch), []);
  const go = React.useCallback((s, sel) => nav.go(s, sel), []);

  const shared = { onCite: cite, selection, setSelection: select, go, lastEval, setLastEval,
    onSearch: () => setPalette(true) };
  // Only the surface in view is constructed. It used to be all eleven, every render,
  // each with its own mount effects waiting to fire.
  const Active = SURFACES[surface] || SURFACES.workbench;

  const unjudged = lastEval?.check?.constraint_summary?.unjudged;

  if (locked === null) return null;                 // one frame, before we know which
  if (locked) return <Gate onUnlocked={boot} auth={health?.auth} />;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Masthead plan={plan} judgment={unjudged} onSearch={() => setPalette(true)} />
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <LeftRail current={surface} onGo={go} counts={overview?.counts} />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, minHeight: 0 }}>
          <Active {...shared} />
        </main>
        <RailHost onCite={cite} surface={surface} plan={plan} lastEval={lastEval}
          railAvailable={health ? !!health.rail : null} />
      </div>
      <CommandPalette open={palette} onClose={() => setPalette(false)}
        onAction={(run) => { if (run === 'help') setHelpCard(true); }} />
      <ShortcutCard open={helpCard} onClose={() => setHelpCard(false)} />
    </div>
  );
}
