/* EVERY REQUEST GOES THROUGH THE CLIENT (WP-14.20).

   `api/client.js` is where a request learns the app's conventions: a 401 raises the Gate
   (`noteUnauthorized`), a path parameter is encoded (`seg`), an error carries its status and body,
   and a corpus read is cached for the page's life. A surface that calls `fetch` itself gets none of
   that, and each time one did it cost something a reader saw: the Drawing Set threw on an expired
   session instead of showing the Gate (WP-12.0), Details & Export swallowed a 422 with no
   else-branch (WP-13.4), and the Kit's slot read put a style id from the URL into its path
   unencoded (WP-14.20). Those were found one surface at a time; this walks every source file.

   THE ALLOW-LIST IS NAMED AND EACH ENTRY SAYS WHY. Every legitimate network call in the app was
   looked for before this was written -- the Gate's sign-in (`api.login`), the Gate's one open read
   (`api.glossaryTerm('about-tdl')`), the rail's streamed turn (`railTurn`), a job's event stream
   (`jobEvents`) -- and every one already lives in the client, so the list has one entry. The
   coastline tiers and the Round's 3D chunk are `import()`s of the app's own modules, not requests
   for data, and are not what this is about. `e2e/` is the browser walk, a harness in Node that
   asks the API directly to hold the page against it; it is not the app and is not walked.

   What is looked for: a call of `fetch`, a `new EventSource` and an `XMLHttpRequest` -- the three
   ways a browser script asks a server for something -- in code, with comments stripped, because
   the files that explain why they do NOT fetch say "fetch" in prose. Tests are excluded: a test in
   `src/` runs under Node and reads files, and asks no server. No `node_modules` import. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';

const SRC = new URL('./', import.meta.url);

export const ALLOWED = Object.freeze({
  'api/client.js': 'the one client: getJSON and postJSON carry the 401 handler, the encoding and '
    + 'the error shape; railTurn streams a POST, which EventSource cannot; jobEvents holds the one '
    + 'EventSource and closes it',
});

const NETWORK = /\bfetch\s*\(|\bnew\s+EventSource\s*\(|\bXMLHttpRequest\b/;

function sources() {
  const out = [];
  const walk = (dir) => {
    for (const f of readdirSync(dir).sort()) {
      const u = new URL(f, dir);
      if (statSync(u).isDirectory()) walk(new URL(f + '/', dir));
      else if (/\.(m?js|jsx)$/.test(f) && !/\.test\.mjs$/.test(f)) out.push(u);
    }
  };
  walk(SRC);
  return out;
}

/* Block comments whole (JSX's braced block comments included), and a line comment from a `//`
   that starts a line or follows whitespace -- so `'http://'` inside a string survives. Prose that
   says "fetch" is not a fetch. */
export function code(text) {
  return text.replace(/\/\*[\s\S]*?\*\//g, ' ')
    .split('\n').map((l) => l.replace(/(^|\s)\/\/.*$/, '$1')).join('\n');
}

const rel = (u) => u.pathname.slice(SRC.pathname.length);

test('no source outside the client asks the server for anything by hand', () => {
  const files = sources();
  assert.ok(files.length > 50, `the walk reached the app's sources (${files.length} files)`);
  const offenders = files.filter((u) => !(rel(u) in ALLOWED))
    .filter((u) => NETWORK.test(code(readFileSync(u, 'utf8'))))
    .map((u) => {
      const lines = code(readFileSync(u, 'utf8')).split('\n');
      const i = lines.findIndex((l) => NETWORK.test(l));
      return `${rel(u)}:${i + 1}: ${lines[i].trim()}`;
    });
  assert.deepEqual(offenders, [],
    'these call the network themselves; add a function to api/client.js and call that');
});

test('every allow-listed file exists and really does call the network, so the list cannot rot', () => {
  const names = sources().map(rel);
  for (const [f, why] of Object.entries(ALLOWED)) {
    assert.ok(names.includes(f), `${f} is allow-listed and is not a source file`);
    assert.ok(why.length > 20, `${f}: an allow-list entry says why`);
    assert.ok(NETWORK.test(code(readFileSync(new URL(f, SRC), 'utf8'))),
      `${f} is allow-listed and calls nothing: the entry is stale`);
  }
});

test('the reader of code tells a call from a sentence about one', () => {
  /* The premise the walk rests on, driven: stripping must remove prose and keep code. A stripper
     that removed everything would make the walk pass vacuously. */
  assert.ok(NETWORK.test(code("const r = await fetch('/api/x');")));
  assert.ok(NETWORK.test(code('const es = new EventSource(`/api/jobs/${id}/events`);')));
  assert.ok(NETWORK.test(code("fetch('http://example.test/api')")), 'a URL in a string is not a comment');
  assert.ok(!NETWORK.test(code('/* a raw fetch( here swallowed a 422 */')));
  assert.ok(!NETWORK.test(code("// the fetch(url) the client makes\nconst a = 1;")));
  assert.ok(!NETWORK.test(code("{/* fetch('/api') */}")));
  assert.ok(!NETWORK.test(code('api.fetchOnce(); refetch();')), 'a name containing fetch is not fetch(');
});
