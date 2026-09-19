/* The plan record is a document the browser owns (the server is stateless for plans).
   A tiny external store: subscribe/getSnapshot for useSyncExternalStore, an undo
   stack, and localStorage persistence so a refresh loses nothing. */

const KEY = 'tdl-workbench-plan';
let plan = null;
let undoStack = [];
let redoStack = [];
const listeners = new Set();

try {
  const saved = localStorage.getItem(KEY);
  if (saved) plan = JSON.parse(saved);
} catch { /* private windows etc. — start empty */ }

/* WHAT IS PERSISTED IS THE RECORD, NEVER THE LOOP'S ACCOUNT OF ITSELF (WP-13.9's audit).

   `revision_report` is the revision panel, and since the bench's solve began running its
   corrective rounds it rides on the document -- which `emit()` stringifies SYNCHRONOUSLY on
   the main thread on every mutation, and a mutation is every step of a wall drag. Measured on
   `tidewater-georgian-careful` after the bench's default two rounds: the declared record is
   13,892 bytes and the report is 146,733 more, so the drag was about to pay a 162 KB
   stringify and a synchronous `setItem` per frame -- on the one interaction the engine choice
   exists to protect, whose own comment says it "cannot afford the wait".

   It is dropped from the PERSISTED copy only. In memory the document keeps it, so the panel,
   undo and redo behave exactly as WP-9.3 specified; what a refresh loses is the account of a
   solve that a refresh has already thrown away the placement for. */
function persisted(p) {
  if (!p || !p.revision_report) return p;
  const { revision_report: _drop, ...rest } = p;
  return rest;
}

function emit() {
  try { localStorage.setItem(KEY, JSON.stringify(persisted(plan))); } catch { /* best effort */ }
  listeners.forEach((fn) => fn());
}

export const planDoc = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return plan; },

  /* Replace the whole document (load an example, open a candidate). */
  load(next) {
    // CAPPED LIKE `update` IS, and it was not (WP-13.9's audit). `update` has capped at 100
    // since it was written; `load` was the once-an-hour act of opening a record and had no
    // cap -- and then the bench's solve began loading the loop's revised record on every
    // explicit solve, so the stack grew one full record per re-solve press, unbounded, each
    // one carrying a revision report.
    if (plan) undoStack.push(plan);
    if (undoStack.length > 100) undoStack.shift();
    redoStack = [];
    plan = next;
    emit();
  },

  /* Apply a mutation via a pure function of the previous record. */
  update(fn) {
    if (!plan) return;
    undoStack.push(plan);
    if (undoStack.length > 100) undoStack.shift();
    redoStack = [];
    plan = fn(JSON.parse(JSON.stringify(plan)));
    emit();
  },

  undo() {
    if (!undoStack.length) return;
    redoStack.push(plan);
    plan = undoStack.pop();
    emit();
  },

  redo() {
    if (!redoStack.length) return;
    undoStack.push(plan);
    plan = redoStack.pop();
    emit();
  },

  canUndo: () => undoStack.length > 0,
  canRedo: () => redoStack.length > 0,
};

/* Common mutations, kept here so surfaces stay declarative. Every one of these edits
   the DECLARED record — geometry is a render of the record and is never edited. */

export const mutations = {
  setStyle: (styleId) => (p) => ({ ...p, style: styleId }),

  resizeRoom: (levelIdx, roomId, patch) => (p) => {
    const lv = levelIdx >= 0 ? p.levels[levelIdx] : null;
    if (!lv) return p;   // an unknown level index must not corrupt the record
    lv.rooms = lv.rooms.map((r) => (r.id === roomId ? { ...r, ...patch } : r));
    return p;
  },

  /* Assert a fact the record lacked — e.g. not-visible-from. The finding clears only
     if the validator actually clears it; the assertion stays visible and revocable. */
  assertRelation: (a, b, relation) => (p) => {
    p.adjacencies = (p.adjacencies || []).concat([{ a, b, relation }]);
    return p;
  },

  revokeRelation: (idx) => (p) => {
    p.adjacencies = (p.adjacencies || []).filter((_, i) => i !== idx);
    return p;
  },
};
