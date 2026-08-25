/* The Workbench shell. Six of the ten surfaces are live; the rest are listed in the
   rail as forthcoming rather than hidden. The AI rail is persistent across all of them.
   A citation anywhere routes through citations.js and navigates this shell. */
import React from 'react';
import { api } from './api/client.js';
import { routeCite } from './citations.js';
import { planDoc } from './state/planDoc.js';
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

export default function App() {
  const [surface, setSurface] = React.useState('workbench');
  const [selection, setSelection] = React.useState({});
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

  function cite(ref) {
    const target = routeCite(ref);
    if (!target) return;
    setSelection(target.selection || {});
    setSurface(target.surface);
  }

  const shared = { onCite: cite, selection, setSelection, go: setSurface, lastEval, setLastEval };
  const surfaces = {
    workbench: <PlanWorkbench {...shared} />,
    candidates: <CandidateSet {...shared} />,
    faults: <FaultCorpus {...shared} />,
    kit: <KitSurface {...shared} />,
    phylogeny: <Phylogeny {...shared} />,
    brief: <BriefIntake {...shared} />,
    style: <StyleRecord {...shared} />,
    proportions: <Proportions {...shared} />,
    drawings: <DrawingSet {...shared} />,
    export: <ExportDetails {...shared} />,
  };

  const unjudged = lastEval?.check?.constraint_summary?.unjudged;

  if (locked === null) return null;                 // one frame, before we know which
  if (locked) return <Gate onUnlocked={boot} />;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Masthead plan={plan} judgment={unjudged} />
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <LeftRail current={surface} onGo={setSurface} counts={overview?.counts} />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, minHeight: 0 }}>
          {surfaces[surface] || surfaces.workbench}
        </main>
        <RailHost onCite={cite} surface={surface} plan={plan} lastEval={lastEval}
          railAvailable={health ? !!health.rail : null} />
      </div>
    </div>
  );
}
