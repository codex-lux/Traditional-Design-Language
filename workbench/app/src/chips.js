/* THE CHIPS, ONE TABLE EACH (Phase 17, WP-17.1, docs/ui-redesign-2026-10-29.md).

   Every number in the corpus says where it came from, every kit slot how it is bound, every
   variant where it stands on its style's ladder, and every finding how much it matters. Those
   were drawn by private maps inside `SlotRow.jsx` and `VariantPill.jsx`, in ink only. The
   redesign gives each a FORM as well as an ink, and this file holds the forms:

     SOURCE    measured · editorial · derived · invented · code   a parameter's kind
     BINDING   specified · extends · forbidden · open             a slot's binding
     VARIANT   canonical · permitted · atypical · forbidden       a variant's rank
     SEVERITY  fatal · serious · minor · advisory · info          a finding's weight

   THE WORD IS ALWAYS IN A TEXT DUTY, NEVER IN THE CHIP'S PIGMENT, and that was measured before
   it was written: --paper reads 3.78 : 1 on --green-deep and 3.50 on --brick, so a word set in a
   filled green or brick chip fails 4.5. Where the board draws a FILL in a strong pigment
   (canonical, permitted, forbidden; every severity), the pigment is a SWATCH beside the word and
   the word is --text-body. Where the fill is pale (measured, editorial, derived, a specified
   binding), the chip's ground is that pale fill and the word is --coal, which reads 11.8 : 1 or
   better on every one of them. So every chip reads on the dark instrument and on vellum alike.
   `src/chips.test.mjs` computes those ratios from the stylesheet.

   Pure: no React, no DOM. */

/* A chip's look: `fill` its ground (null: the ground the chip stands on), `ink` its word,
   `border` its border, `swatch` the pigment drawn beside the word, `struck` a line through the
   word, `hatch` a duty-token field drawn behind it, `weight` the word's weight. */
const chip = (o) => Object.freeze({ fill: null, ink: 'var(--text-body)', border: null, swatch: null,
  struck: false, hatch: null, weight: null, ...o });

export const SOURCE = Object.freeze({
  measured: chip({ fill: 'var(--green-pale)', ink: 'var(--coal)', border: 'var(--green-deep)' }),
  editorial: chip({ fill: 'var(--sepia-pale)', ink: 'var(--coal)', border: 'var(--sepia)' }),
  // "pale green-grey" on the board. The palette's own green-grey is --blue-pale, whose duty is
  // water, so derived takes the mat with a green-deep edge rather than borrow water's pigment.
  derived: chip({ fill: 'var(--paper-mat)', ink: 'var(--coal)', border: 'var(--green-deep)' }),
  // the one that shouts: brick edged and brick-washed, its word set heavy
  invented: chip({ fill: 'var(--paper)', ink: 'var(--coal)', border: 'var(--brick)', swatch: 'var(--brick)', weight: 700 }),
  code: chip({ ink: 'var(--text-body)', border: 'var(--text-secondary)' }),
});

export const BINDING = Object.freeze({
  specified: chip({ fill: 'var(--paper)', ink: 'var(--coal)', border: 'var(--hair)' }),
  extends: chip({ ink: 'var(--text-body)', border: 'var(--text-body)' }),
  forbidden: chip({ ink: 'var(--text-body)', border: 'var(--brick)', swatch: 'var(--brick)', struck: true }),
  // open: nothing, which is the binding's own meaning -- the style declines to constrain the slot
  open: chip({ ink: 'var(--text-secondary)' }),
});

export const VARIANT = Object.freeze({
  canonical: chip({ swatch: 'var(--green-deep)', border: 'var(--green-deep)' }),
  permitted: chip({ swatch: 'var(--green)', border: 'var(--green)' }),
  atypical: chip({ ink: 'var(--text-secondary)', border: 'var(--text-secondary)' }),
  forbidden: chip({ swatch: 'var(--brick)', border: 'var(--brick)', struck: true, hatch: 'var(--mark-forbidden)' }),
});

/* Severity is a ladder of inks, never a traffic light (the board). The verdicts are filled
   swatches; advisory and info are a graphite outline and no fill, because neither is a verdict. */
export const SEVERITY = Object.freeze({
  fatal: chip({ swatch: 'var(--sev-fatal)' }),
  serious: chip({ swatch: 'var(--sev-serious)' }),
  minor: chip({ swatch: 'var(--sev-minor)' }),
  advisory: chip({ border: 'var(--sev-advisory)', ink: 'var(--text-secondary)' }),
  info: chip({ border: 'var(--sev-info)', ink: 'var(--text-secondary)' }),
});

export const LADDERS = Object.freeze({ source: SOURCE, binding: BINDING, variant: VARIANT, severity: SEVERITY });

/* The look for `value` on `ladder`, or null for a value the ladder does not hold -- which the
   caller draws as the bare word, never as some other rung. */
export function chipOf(ladder, value) {
  const l = LADDERS[ladder];
  return l && Object.prototype.hasOwnProperty.call(l, value) ? l[value] : null;
}

/* The inline style of the chip's box and of its swatch, from the look. */
export function chipStyle(look) {
  if (!look) return null;
  return {
    box: {
      display: 'inline-flex', alignItems: 'center', gap: 5, font: 'var(--type-data-s)',
      padding: look.border || look.fill ? '0 6px' : 0, whiteSpace: 'nowrap',
      color: look.ink, background: look.fill || 'transparent',
      backgroundImage: look.hatch || 'none',
      border: look.border ? `1px solid ${look.border}` : 'none',
      fontWeight: look.weight || undefined,
    },
    word: look.struck ? { textDecoration: 'line-through', textDecorationThickness: '1px' } : {},
    swatch: look.swatch ? { width: 8, height: 8, flex: 'none', borderRadius: '50%', background: look.swatch } : null,
  };
}
