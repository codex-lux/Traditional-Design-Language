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

function emit() {
  try { localStorage.setItem(KEY, JSON.stringify(plan)); } catch { /* best effort */ }
  listeners.forEach((fn) => fn());
}

export const planDoc = {
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  get() { return plan; },

  /* Replace the whole document (load an example, open a candidate). */
  load(next) {
    if (plan) undoStack.push(plan);
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
