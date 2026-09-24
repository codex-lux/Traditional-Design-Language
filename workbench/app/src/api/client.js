/* Typed-by-convention fetch wrappers. Shapes mirror mcp_server/core.py returns —
   the app adapts to the corpus, never the reverse. A tiny stale-while-warm cache
   for GETs; the plan/evaluate POST is never cached (the record is the state). */

const cache = new Map();

/* A session can expire mid-visit — and does on every redeploy when WORKBENCH_SECRET is
   unset, since the signing key is then per-process. Without this every surface just threw
   and the user saw panels erroring instead of the password screen. */
let onUnauthorized = null;
export function setUnauthorizedHandler(fn) { onUnauthorized = fn; }
function noteUnauthorized(status) {
  if (status === 401 && onUnauthorized) onUnauthorized();
}

async function getJSON(url, { fresh = false } = {}) {
  if (!fresh && cache.has(url)) return cache.get(url);
  /* `fresh` skipped OUR map and then took the browser's cache instead, which is not what
     the flag promises its one caller: health is read to find out what the server is doing
     NOW. */
  const r = await fetch(url, fresh ? { cache: 'no-store' } : undefined);
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    noteUnauthorized(r.status);
    throw Object.assign(new Error(`GET ${url} → ${r.status}`), { status: r.status, body });
  }
  const j = await r.json();
  cache.set(url, j);
  return j;
}

async function postJSON(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({}));
    if (!url.endsWith('/api/login')) noteUnauthorized(r.status);
    throw Object.assign(new Error(`POST ${url} → ${r.status}`), { status: r.status, body: b });
  }
  return r.json();
}

/* Path parameters are ENCODED. Ids come from `location.hash` now, which is user-pasteable
   and therefore untrusted: an id containing `?`, `#`, `%` or a slash used to be interpolated
   raw, so `#/kit/a%3Fx%3D1` produced `/api/kit/a?x=1?only_specified=true` and silently
   dropped the flag, and `..%2F..%2Fadmin` resolved to a different endpoint entirely. Not a
   security hole — mcp_server/core.py preloads every record into dicts and looks them up with
   `.get()`, never opening a file by id, and the SPA catch-all has a realpath guard — but it
   corrupts requests, and it is one refactor away from being worse. Found by an adversarial
   audit; no real corpus id contains any of these characters, which is why nothing broke. */
const seg = (v) => encodeURIComponent(String(v == null ? '' : v));

const qs = (params) => {
  const p = Object.entries(params || {}).filter(([, v]) => v !== undefined && v !== null && v !== '');
  return p.length ? '?' + new URLSearchParams(p).toString() : '';
};

/* The record minus its revision panel, for the routes that do not read one. */
function withoutReport(plan) {
  if (!plan || !plan.revision_report) return plan;
  const { revision_report: _drop, ...rest } = plan;
  return rest;
}

export const api = {
  health: () => getJSON('/api/health', { fresh: true }),
  /* Sets an httpOnly session cookie; nothing is stored client-side. Throws with
     .status 401 on a wrong password, 429 when attempts are being throttled. */
  login: (password) => postJSON('/api/login', { password }),
  overview: () => getJSON('/api/overview'),
  /* Everything nameable, once. The GET cache above makes this fetch-once for the page's
     life, which is what the palette wants — the corpus does not change under a server. */
  searchIndex: () => getJSON('/api/search/index'),
  phylogeny: () => getJSON('/api/phylogeny'),
  styles: (params) => getJSON('/api/styles' + qs(params)),
  style: (id, sections) => getJSON(`/api/styles/${seg(id)}` + qs({ sections })),
  compareStyles: (a, b) => getJSON('/api/styles/compare' + qs({ a, b })),
  slot: (id) => getJSON(`/api/slots/${seg(id)}`),
  kit: (styleId, params) => getJSON(`/api/kit/${seg(styleId)}` + qs(params)),
  cascade: (styleId) => getJSON(`/api/kit/${seg(styleId)}/cascade`),
  proportions: (packId, params) => getJSON(`/api/proportions/${seg(packId)}` + qs(params)),
  authorities: (order, params) => getJSON(`/api/authorities/${seg(order)}` + qs(params)),
  faults: (params) => getJSON('/api/faults' + qs(params)),
  fault: (id, style) => getJSON(`/api/faults/${seg(id)}` + qs({ style })),
  vocabulary: (params) => getJSON('/api/vocabulary' + qs(params)),
  massings: (params) => getJSON('/api/massings' + qs(params)),
  rooms: (params) => getJSON('/api/rooms' + qs(params)),
  room: (id, style) => getJSON(`/api/rooms/${seg(id)}` + qs({ style })),
  groupings: (params) => getJSON('/api/groupings' + qs(params)),
  assets: (params) => getJSON('/api/assets' + qs(params)),
  partis: (params) => getJSON('/api/partis' + qs(params)),
  planSchema: () => getJSON('/api/schema/plan'),
  briefSchema: () => getJSON('/api/schema/brief'),
  examplePlan: (name) => getJSON(`/api/plans/examples/${seg(name)}`, { fresh: true }),

  // WP-12.0. The Drawing Set was the last surface calling `fetch` directly, so it was also
  // the last one outside `noteUnauthorized` -- a session that expired while a reader was on
  // it threw instead of showing the password screen. `face` is one of S/N/E/W: the server
  // has accepted it since WP-5.1 and `render_elevation` has taken it since WP-3.2, and no
  // client had ever sent one, so three of the four elevations this system can draw had
  // never been looked at.
  drawing: (kind, plan, opts = {}) => postJSON(`/api/drawings/${seg(kind)}`, { plan, ...opts }),

  /* WP-13.4. `Details & Export` was the last surface calling `fetch` by hand, and it was the
     last one outside `noteUnauthorized` AND outside every error convention this file keeps.
     Its SVG save had an `if (r.ok)` with no `else`, so a 422 downloaded nothing and said
     nothing; its CAD save parsed `j.detail || j` itself and painted the result in
     `var(--forthcoming)` — the NOT-BUILT colour — so a refused house read as a feature nobody
     had written. Both go through here now, and `sheet/refusal.js` is the one reader of what
     comes back. 501 with `refusal` still means a missing ezdxf/ifcopenshell on the server and
     nothing else: see `isMissingLibrary`. */
  exportCad: (fmt, plan, opts = {}) => postJSON(`/api/export/${seg(fmt)}`, { plan, ...opts }),

  /* The Round's one call (WP-12.3). Returns the scene record, the PLACED plan and every named
     view's plate together, because seven metered calls per record change against a budget of
     sixty an hour buys eight edits and one call buys sixty. Keep the returned `plan`: a record
     carrying `geometry` short-circuits the server's placement, 37.48 s -> 0.00 s, on every
     later export or evaluate. */
  scene: (plan, opts = {}) => postJSON('/api/scene', { plan, ...opts }),

  /* THE PANEL IS NOT AN INPUT (WP-13.9's audit). `revision_report` is authored history the
     record carries so the panel survives an undo, and since the solve began running the
     corrective rounds it is the bulk of the document: MEASURED on the revised Tidewater
     record, 162,651 bytes of which 147,583 are the report -- 91%. Nothing on this route
     reads it, and the bench re-POSTs the whole document on every debounced wall drag, so it
     went up the wire on every frame of a gesture. It is dropped HERE and not in `planDoc`,
     because the record must keep it: undo, the panel and `exportCad` all read it.
     `exportCad` deliberately does NOT strip it -- `build/export_dxf.py` turns it into the
     drawing's `revision_summary` XDATA, so a stripped record would export a plate that has
     forgotten it was revised. */
  evaluate: (plan, opts = {}) => postJSON('/api/plan/evaluate', { plan: withoutReport(plan), ...opts }),
  // WP-9.3: the analyst (synchronous) and the loop (a job; rounds arrive through jobEvents,
  // the revised record through jobPlan -- stripped of its placement, the bench re-solves)
  critique: (plan, opts = {}) => postJSON('/api/plan/critique', { plan, ...opts }),
  revise: (plan, opts = {}) => postJSON('/api/plan/revise', { plan, ...opts }),
  jobPlan: (jobId) => getJSON(`/api/jobs/${seg(jobId)}/plan`, { fresh: true }),
  ingestDxf: (dxf, units) => postJSON('/api/ingest/dxf', { dxf, units }),
  compose: (brief, candidates = 4) => postJSON('/api/compose', { brief, candidates }),
  job: (id) => getJSON(`/api/jobs/${seg(id)}`, { fresh: true }),
  candidatePlan: (jobId, n) => getJSON(`/api/jobs/${seg(jobId)}/candidates/${seg(n)}/plan`, { fresh: true }),

  /* WP-14.4 (PRD §H.3-§H.5). A style's packs by provenance, and the dossier's head and section
     counts -- corpus reads, cached like every other one, because the corpus does not change
     under a server. The example brief is fetched fresh, as `examplePlan` is: it is a document
     the reader loads to edit, and a stale copy would be a different starting point. */
  stylePacks: (id) => getJSON(`/api/styles/${seg(id)}/packs`),
  styleDossier: (id) => getJSON(`/api/styles/${seg(id)}/dossier`),
  exampleBrief: (name) => getJSON(`/api/briefs/examples/${seg(name)}`, { fresh: true }),
};

/* Subscribe to a job's SSE stream. Returns an unsubscribe function. */
export function jobEvents(jobId, handlers) {
  const es = new EventSource(`/api/jobs/${seg(jobId)}/events`);
  let finished = false;
  for (const [event, fn] of Object.entries(handlers)) {
    es.addEventListener(event, (e) => {
      if (e.data === undefined) return;  // the browser's own error event carries no data
      if (event === 'done' || event === 'error') finished = true;
      fn(JSON.parse(e.data));
    });
  }
  es.onerror = () => {
    es.close();
    if (!finished) handlers.error && handlers.error({ error: 'stream closed' });
  };
  return () => es.close();
}

/* One rail turn over fetch-streamed SSE (POST bodies rule out EventSource). */
export async function railTurn(body, onEvent) {
  const r = await fetch('/api/rail/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok || !r.body) throw new Error(`rail → ${r.status}`);
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = '';
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf('\n\n')) >= 0) {
      const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
      let event = 'message';
      const dataLines = [];
      for (const line of chunk.split('\n')) {
        if (line.startsWith('event: ')) event = line.slice(7);
        else if (line.startsWith('data: ')) dataLines.push(line.slice(6));
      }
      const data = dataLines.join('\n');   // the SSE spec joins multi-line data with \n
      if (data) onEvent(event, JSON.parse(data));
    }
  }
}
