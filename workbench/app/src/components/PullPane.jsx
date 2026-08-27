/* A surface's index panel, with a pullable margin.

   Every surface in the workbench has the same shape: a list or a form down one side, a
   drawing or a table beside it, and a hairline between them that used to be a number
   written into the JSX — 330 on the Fault Corpus, 340 on the Kit, 430 on the Plan
   Workbench, 250 on Proportions, 360 on Transcription. Those numbers were chosen against
   one window, and the pane they set is exactly the pane a reader wants narrower while
   reading a plan and wider while reading a fault.

   This is the shell's splitter applied to them, and it exists as a component rather than
   as five copies because the ORDER matters and is easy to get backwards: the handle
   belongs on the pane's inner edge, so it goes after a left-hand pane and before a
   right-hand one, and `grows` has to agree with which side it is on.

   These panes PULL but do not FOLD, which is a deliberate difference from the two shell
   rails. Folding was asked for on the rails, where the pane is chrome you may not want at
   all; a surface's index is the surface's own subject — a Fault Corpus with the fault list
   folded away is not a decluttered Fault Corpus, it is a broken one. `PANES` says so with
   `foldable: false`, and `layout.dragTo` clamps at the floor for them rather than folding.
*/
import React from 'react';
import { layout } from '../state/layout.js';
import { Splitter } from './Splitter.jsx';

export function PullPane({ pane, side = 'left', style, children }) {
  const width = React.useSyncExternalStore(layout.subscribe, () => layout.width(pane));
  return (
    <>
      {side === 'right' && <Splitter pane={pane} grows="right" />}
      <div style={{ width, flex: 'none', minHeight: 0, ...style }}>{children}</div>
      {side === 'left' && <Splitter pane={pane} grows="left" />}
    </>
  );
}
