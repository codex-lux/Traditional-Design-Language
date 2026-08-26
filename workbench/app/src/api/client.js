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

  evaluate: (plan, opts = {}) => postJSON('/api/plan/evaluate', { plan, ...opts }),
  ingestDxf: (dxf, units) => postJSON('/api/ingest/dxf', { dxf, units }),
  compose: (brief, candidates = 4) => postJSON('/api/compose', { brief, candidates }),
  job: (id) => getJSON(`/api/jobs/${seg(id)}`, { fresh: true }),
  candidatePlan: (jobId, n) => getJSON(`/api/jobs/${seg(jobId)}/candidates/${seg(n)}/plan`, { fresh: true }),
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
