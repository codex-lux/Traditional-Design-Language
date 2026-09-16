/* THE ONE READER OF A REFUSED PLACEMENT, in the app (WP-13.4).

   Lucas ruled on 15 Sep 2026 that a placement which breaks a hard fact of the type is
   REFUSED, not drawn: the bench shows the conflict set, and the brief or the parti is what
   changes. That REVERSES the 25 Aug ruling ("the partner hears the refusal and still sees a
   drawing") for every user-facing surface -- the RECORD keeps the search's least-bad
   placement, because it is the conflict set's own explanation and the wall drag's sketch, and
   no surface draws it.

   THE VERDICT IS THE SERVER'S AND IS READ, NEVER DERIVED. `build/typefacts.py::refusal` is the
   one spelling; `geometry.solve` writes it to `geometry_report.refused` from `_disclose`, which
   both record writers call. This file turns that body -- however it arrived -- into the one
   object the surfaces render, and it re-derives NOTHING. In particular it does not look at
   `geometry_report.type_facts` and count downgrades for itself: a second reader of that block
   would be a second answer to "may this be drawn", which is the defect this repository keeps
   meeting (the citation grammar's three spellings, `required_wall_ft`'s three, the proof
   verdict's three at WP-13.2).

   UNJUDGED IS NOT REFUSED, AND UNJUDGED IS NOT DRAWABLE EITHER -- THREE STATES, NAMED.
   `refusalState` answers `refused`, `drawable` or `unstated`. A house that states no hearth is
   not refused for it: only a fact whose status is `downgraded`, or an INFEASIBLE proof, refuses,
   and that arithmetic is done on the server. `unstated` is the state this file exists to keep
   apart from the other two -- a record whose `geometry_report` carries no `refused` KEY has not
   been judged by a server that answers this contract, and reading that silence as "drawable"
   would be the fake-pass collapse while reading it as "refused" would black out every surface
   against every older server. A surface draws on `unstated` because there is no verdict to
   honour and it may not invent one; `e2e/walk.mjs` reports COULD NOT EVALUATE there rather than
   a pass, which is the half that keeps the silence visible.

   `refusal` IS NOT THE KEY, AND THE COLLISION IS LIVE. `workbench/server/app.py` maps a body
   carrying `refusal` to **501 Not Implemented** -- that key means "this server has no ezdxf /
   ifcopenshell", a missing capability and not a refused house. Nothing here reads it as a
   placement refusal; `isMissingLibrary` is the separate reader, so an export on a machine with
   no CAD library keeps saying what it has always said instead of being reported as a conflict
   set with no conflicts in it.

   A REFUSAL IS CONTENT. It names what could not hold and why, in the corpus's own words
   (`geometry.conflict_lines`), never a bare "error" -- so `conflictLines` returns the server's
   sentences and `unstatedConflicts` COUNTS the entries no sentence covers rather than
   stringifying an object into prose the corpus did not write. `namesSomething` is what a panel
   checks before claiming to be a conflict set: a refusal that names nothing is a bare error
   wearing the word, and the panel says so in as many words.

   No React, no DOM: a leaf, like `engineClaim.js` beside it and `derive.js` and `overlayRules.js`
   under it, so every branch is driven by `refusal.test.mjs` under `node --test` with a hand-built
   body -- which is also how this file was written before the server slice landed. */

/* The two kinds `typefacts.refusal` mints. An object whose `kind` is neither is NOT read as a
   refusal: it is a body this app cannot understand, which is `unstated` and not `refused`. */
export const REFUSAL_KINDS = Object.freeze(['infeasible', 'type-fact-downgraded']);

export const REFUSAL_STATES = Object.freeze(['refused', 'drawable', 'unstated']);

const str = (v) => (typeof v === 'string' && v.trim() ? v.trim() : null);
const strings = (v) => (Array.isArray(v)
  ? v.filter((x) => typeof x === 'string' && x.trim()).map((x) => x.trim())
  : []);

/* Normalise any of the bodies the contract names into the one object the surfaces render:

     a 422 `detail`                  -> {error, refused_placement, unsolved}
     `/api/plan/evaluate`'s 200      -> body.placement_refused
     a composed candidate            -> candidate.refused
     a placed record                 -> placement.geometry_report.refused
                                        placement.sketch.refused   (the wall drag)

   The wrapper form is unwrapped once, so a caller may hand this the whole 422 detail without
   knowing which layer of it carries the verdict. Returns null for anything that is not a
   refusal this app can read -- including an object with an unrecognised `kind`, which is the
   `unstated` case and must not be drawn as a conflict set with nothing in it. */
export function readRefusal(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return null;
  const raw = (body.refused_placement && typeof body.refused_placement === 'object'
    && !Array.isArray(body.refused_placement))
    ? body.refused_placement : body;
  const kind = str(raw.kind);
  if (!kind || !REFUSAL_KINDS.includes(kind)) return null;
  return {
    kind,
    facts: strings(raw.facts),
    conflicts: Array.isArray(raw.conflicts) ? raw.conflicts : [],
    lines: strings(raw.lines),
    engine: str(raw.engine),
    status: str(raw.status),
    // the one sentence the route puts beside the refusal; on the evaluate path it rides on the
    // 200 body rather than on the refusal, so a caller may pass either and get the same object
    error: str(body.error) || str(raw.error),
  };
}

/* The sentences a conflict-set panel prints, in the corpus's own words.

   `lines` is `geometry.conflict_lines`' output and is what a reader is owed. Where the server
   stated none, a conflict entry that is ITSELF a string is the corpus's own words too (the
   `geometry_report.infeasible.conflicts` the Plan Workbench has rendered as list items since
   WP-2.3), so it is passed through; anything else is COUNTED by `unstatedConflicts` and never
   stringified, because `String({})` is prose nobody wrote. */
export function conflictLines(r) {
  if (!r) return [];
  if (r.lines.length) return r.lines;
  return r.conflicts.filter((c) => typeof c === 'string' && c.trim()).map((c) => c.trim());
}

/* How many conflict entries no printed sentence covers. A panel showing four sentences for six
   conflicts and saying nothing about the other two would be understating a refusal, which is the
   OQ 52 family wearing its safe-looking sign. */
export function unstatedConflicts(r) {
  if (!r) return 0;
  return Math.max(0, r.conflicts.length - conflictLines(r).length);
}

/* Whether this refusal names anything at all. A refusal naming no fact, no conflict and no
   sentence is a bare error with the word "refused" on it, and the panel has to say that rather
   than drawing an empty rectangle a reader will read as "nothing much". */
export function namesSomething(r) {
  return Boolean(r) && (r.facts.length > 0 || r.conflicts.length > 0 || r.lines.length > 0);
}

/* One line for a strip or a caption: what kind of refusal, and how much it named. */
export function refusalHeadline(r) {
  if (!r) return null;
  const n = conflictLines(r).length + unstatedConflicts(r);
  const what = r.kind === 'infeasible'
    ? 'infeasible as declared — proven'
    : `${r.facts.length} hard fact${r.facts.length === 1 ? '' : 's'} of the type downgraded`;
  return n ? `${what} (${n} conflict${n === 1 ? '' : 's'})` : what;
}

/* THE THREE STATES, off a placed record or a drawing result.

   `refused`  — the server judged and said no; nothing may be drawn or exported from it.
   `drawable` — the server judged and found no refusal.
   `unstated` — no verdict on this record: either it carries no `geometry_report` at all, or the
                block carries no `refused` KEY, or the body under that key is one this app cannot
                read. Not a pass and not a refusal. */
export function refusalState(placed) {
  const gr = placed && typeof placed === 'object' ? placed.geometry_report : null;
  if (!gr || typeof gr !== 'object') return 'unstated';
  if (!Object.prototype.hasOwnProperty.call(gr, 'refused')) return 'unstated';
  if (gr.refused === null || gr.refused === undefined) return 'drawable';
  return readRefusal(gr.refused) ? 'refused' : 'unstated';
}

/* The refusal carried by a placed record, or null. `refusalState` is what distinguishes a null
   here that means "judged, not refused" from a null that means "nobody judged". */
export function placementRefusal(placed) {
  const gr = placed && typeof placed === 'object' ? placed.geometry_report : null;
  return gr && typeof gr === 'object' ? readRefusal(gr.refused) : null;
}

/* THE WALL DRAG'S WORKING SKETCH.

   `workbench/server/evaluate.py` asks for the hill-climb BY NAME behind a wall drag, because a
   gesture cannot wait for a proof (the 26 Aug ruling, and no settle-timer re-proof: a second
   render landing mid-gesture replaces the handle under the pointer and the drag dies). That is
   the ONE path the contract still lets return a placement on a refusal, and it returns it marked
   `placement.sketch = {working, refused, reason}`.

   A sketch may be drawn and may NOT be exported, and a surface that draws one has to say so on
   the PLATE rather than in the prose beside it -- WP-6.4's rule: a printed or exported plate
   leaves the prose behind, and a reader then cannot tell a sketch from a drawing. */
export function sketchOf(placed) {
  const s = placed && typeof placed === 'object' ? placed.sketch : null;
  if (!s || typeof s !== 'object' || Array.isArray(s)) return null;
  if (s.working !== true) return null;
  return { working: true, reason: str(s.reason), refused: readRefusal(s.refused) };
}

/* MAY THIS RECORD BE DRAWN AT ALL, in one place. `false` only where the server said so: a
   refused placement, or a sketch — which the bench draws under its own banner and no other
   surface draws at all. Everything merely `unstated` draws, because there is no verdict to
   honour and this file may not invent one. */
export function mayDraw(placed, { allowSketch = false } = {}) {
  if (refusalState(placed) === 'refused') return false;
  if (sketchOf(placed) && !allowSketch) return false;
  return true;
}

/* MAY THIS RECORD LEAVE THE SYSTEM AS A FILE. Strictly narrower than `mayDraw`: a working sketch
   is a legitimate thing to look at and is never a legitimate thing to hand a drafter. */
export function mayExport(placed) {
  return refusalState(placed) !== 'refused' && !sketchOf(placed);
}

/* THE ONE READER OF A THROWN api/client.js ERROR. `postJSON`/`getJSON` throw with `.status` and
   `.body`; five surfaces dug `e.body?.detail?.error` out by hand, which is five spellings of one
   join and how a route that starts answering differently goes unnoticed on four of them. */
export function errorText(e) {
  if (!e) return null;
  if (typeof e === 'string') return str(e);
  const b = e.body;
  if (b && typeof b === 'object') {
    const d = b.detail;
    if (d && typeof d === 'object' && str(d.error)) return str(d.error);
    if (str(d)) return str(d);
    if (str(b.error)) return str(b.error);
  }
  return str(e.message) || String(e);
}

/* The refusal inside a thrown error, or null. The contract answers a refused placement with 422
   and `detail` = `corpus._placed`'s own return, so the verdict is one unwrap down and
   `readRefusal` does that unwrapping itself. */
export function refusalFromError(e) {
  return e && typeof e === 'object' ? readRefusal(e.body && e.body.detail) : null;
}

/* A 501 carrying `refusal` is a MISSING LIBRARY on the server, not a refused house. Read apart,
   so an export on a machine without ezdxf keeps saying what it has always said. */
export function isMissingLibrary(e) {
  if (!e || typeof e !== 'object') return false;
  return e.status === 501 || Boolean(e.body && e.body.detail && e.body.detail.refusal);
}

/* The refusal an `/api/plan/evaluate` 200 carries. That route answers 200 with
   `placement_refused` and NO `placement`, because the check still ran on the declared record and
   its findings are worth having — it is the PLACEMENT that is refused, not the evaluation. */
export function evaluateRefusal(res) {
  if (!res || typeof res !== 'object') return null;
  const r = readRefusal(res.placement_refused);
  if (!r) return null;
  return { ...r, error: r.error || str(res.error) };
}
