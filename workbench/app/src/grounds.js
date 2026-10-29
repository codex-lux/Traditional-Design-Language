/* THE TWO GROUNDS, READ ONCE (Phase 17, WP-17.0).

   The instrument is dark and the plates are vellum (ruled 29 Oct 2026). `theme/tokens.css` says
   so in two blocks, `[data-ground="instrument"]{...}` and `[data-ground="vellum"]{...}`, each
   rebinding the semantic duties and no primitive. This module is the one reader of them:

     GROUNDS               the two ground names, in the order a page nests them
     stripGrounds(css)     the stylesheet with both blocks blanked, which is the :root answer --
                           what a token means where no ground is set, and what the readers that
                           judge a token at its last declaration must read, or every duty would
                           resolve to whichever ground block happens to come last
     groundTokens(css, g)  the declarations ONE ground block makes, as {name: value}
     groundValue(css, g, name)
                           a token's value on ground `g`: the block's own if it moves the token,
                           the :root one otherwise, resolved through `var()` to a literal

   Pure: node:fs is the caller's, never this file's, so the app's test suite and the browser both
   import it. */

export const GROUNDS = Object.freeze(['instrument', 'vellum']);

const BLOCK = /\[data-ground="(instrument|vellum)"\]\s*\{([^}]*)\}/g;
const live = (css) => css.replace(/\/\*[\s\S]*?\*\//g, (c) => c.replace(/[^\n]/g, ' '));

/* The stylesheet with both ground blocks blanked to spaces (offsets kept). A rule that merely
   SELECTS a ground, such as `[data-ground]{color:...}`, has no custom property in it and is
   left alone. */
export function stripGrounds(css) {
  return live(css).replace(BLOCK, (m) => m.replace(/[^\n]/g, ' '));
}

export function groundTokens(css, ground) {
  const out = {};
  for (const m of live(css).matchAll(BLOCK)) {
    if (m[1] !== ground) continue;
    for (const d of m[2].matchAll(/(--[a-z0-9-]+)\s*:\s*([^;]+);?/gi)) out[d[1]] = d[2].trim();
  }
  return out;
}

/* Every custom property declared outside the ground blocks, last declaration winning as CSS has
   it. */
export function rootTokens(css) {
  const defs = {};
  for (const m of stripGrounds(css).matchAll(/(--[a-z0-9-]+)\s*:\s*([^;}]+)[;}]/gi)) defs[m[1]] = m[2].trim();
  return defs;
}

/* A token on a ground, resolved through `var()` until a literal. A `var()` inside a ground block
   resolves against the :root primitives, which is how CSS computes it: the block redeclares a
   duty, and the pigment it names is the page's. */
export function groundValue(css, ground, name) {
  const root = rootTokens(css);
  const g = ground ? groundTokens(css, ground) : {};
  const seen = new Set();
  let v = g[name] ?? root[name];
  while (v != null) {
    const r = /^var\((--[a-z0-9-]+)\)$/i.exec(v.trim());
    if (!r) return v.trim();
    if (seen.has(r[1])) return null;
    seen.add(r[1]);
    v = root[r[1]];
  }
  return null;
}

/* The WCAG contrast ratio of two `#rrggbb` inks. `inks.test.mjs` carries the same arithmetic for
   its own verdicts; this copy is the one a non-test module may import. */
export function contrast(a, b) {
  const lum = (h) => {
    const c = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/* WHICH GROUND EACH PAGE STANDS ON, one table, the way `state/layout.js` says which pages reflow.
   The shell (the sidebar, the top bar, the rail) is `SHELL_GROUND`; a surface's `<main>` is its
   row here. Every surface is migrated onto the instrument in its own Phase 17 package, and its
   row moves from 'vellum' to 'instrument' in that package's commit, so a surface whose layout
   has not been redrawn is never shown dark. An id the table does not hold is vellum: a page
   nobody moved is a page nobody redrew. */
export const SHELL_GROUND = 'instrument';
export const SURFACE_GROUND = Object.freeze({
  overview: 'instrument', style: 'instrument', proportions: 'instrument', faults: 'instrument',
  phylogeny: 'instrument', glossary: 'instrument', brief: 'instrument', candidates: 'instrument',
  export: 'instrument', elements: 'instrument', room: 'instrument', massing: 'instrument', grouping: 'instrument',
  parti: 'instrument', compare: 'instrument', workbench: 'instrument', drawings: 'instrument',
  transcription: 'instrument',
});
export const groundOf = (surface) => SURFACE_GROUND[surface] || 'vellum';
