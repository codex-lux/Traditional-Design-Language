// The shell's two faces are served by this app and by nobody else.
//
// Deployment-readiness review, 27 Nov 2026 (DR-10). `index.html` asked fonts.googleapis.com for
// EB Garamond and Courier Prime, so every visitor's address went to Google before the sign-in
// page had drawn, and a machine with no route to Google drew the shell in a fallback face with
// a different line box (the walk read differently with and without a network for that reason).
//
// These read source files only. They import nothing from node_modules, which this suite may not
// (`no_bare_imports.test.mjs`).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const read = (...p) => readFileSync(join(here, ...p), 'utf8');

test('the shell asks no outside host for anything', () => {
  const html = read('..', 'index.html');
  assert.match(html, /<script type="module" src="\/src\/main\.jsx">/, 'the reader is not reading the shell');
  const outside = [...html.matchAll(/(?:href|src)\s*=\s*"((?:https?:)?\/\/[^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(outside, [], `index.html loads from outside the app: ${outside.join(', ')}`);
});

test('every weight and style the old stylesheet link asked for is imported from the package', () => {
  const css = read('theme', 'faces.css');
  // What the Google link named: EB Garamond 400, 500, 600 and italic 400, 500; Courier Prime
  // 400, 700 and italic 400. A face missing here is drawn as a synthesised bold or slant.
  const want = [
    'eb-garamond/400.css', 'eb-garamond/500.css', 'eb-garamond/600.css',
    'eb-garamond/400-italic.css', 'eb-garamond/500-italic.css',
    'courier-prime/400.css', 'courier-prime/700.css', 'courier-prime/400-italic.css',
  ];
  for (const f of want) {
    assert.ok(css.includes(`@import '@fontsource/${f}';`), `faces.css does not import ${f}`);
  }
  const main = read('main.jsx');
  assert.match(main, /import '\.\/theme\/faces\.css';/, 'main.jsx does not load faces.css');
});

test('the packages the faces come from are dependencies, so `npm ci` installs them for the build', () => {
  const pkg = JSON.parse(read('..', 'package.json'));
  for (const name of ['@fontsource/eb-garamond', '@fontsource/courier-prime']) {
    const v = pkg.dependencies?.[name];
    assert.ok(v, `${name} is not in dependencies`);
    assert.doesNotMatch(v, /^[\^~*]|latest/, `${name} is not pinned to one version: ${v}`);
  }
});
