import React from "react";

/* A four-rank ladder, not a binary. 'forbidden' is positive knowledge — 851 forbidden
   variants and 228 forbidden bindings — and gets the loudest form in the system: a
   cross-hatched field with a ruled-through label.

   THE LADDER IS READ AS WORDS AS WELL AS INKS (WP-14.31). Its two lowest rungs were set in the
   faint inks their duty tokens resolve to (`--var-atypical` and `--aff-atypical` are `--ink-3`,
   `--bind-open` is `--ink-4`), which read 3.15 : 1 and 2.26 : 1 on paper, below what a word needs.
   They take `--ink-2` now, so atypical shares permitted's (or possible's) ink; the pill prints its
   status word, which is what tells the two apart, and it is no longer faded by an opacity. */
const LADDERS = {
  variant: {
    canonical: 'var(--var-canonical)',
    permitted: 'var(--var-permitted)',
    atypical: 'var(--ink-2)',
    forbidden: 'var(--var-forbidden)'
  },
  binding: {
    specified: 'var(--bind-specified)',
    extends: 'var(--bind-extends)',
    forbidden: 'var(--bind-forbidden)',
    open: 'var(--ink-2)'
  },
  affinity: {
    canonical: 'var(--aff-canonical)',
    common: 'var(--aff-common)',
    possible: 'var(--aff-possible)',
    atypical: 'var(--ink-2)',
    forbidden: 'var(--aff-forbidden)'
  }
};
function VariantPill({
  status,
  ladder = 'variant',
  name,
  note,
  style
}) {
  const colour = (LADDERS[ladder] || LADDERS.variant)[status] || 'var(--ink-2)';
  const forbidden = status === 'forbidden';
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'baseline',
      gap: 8,
      minWidth: 0,
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: colour,
      border: '1px solid currentColor',
      padding: '1px 6px',
      whiteSpace: 'nowrap',
      background: forbidden ? 'var(--bind-forbidden-field)' : 'transparent',
      backgroundImage: forbidden ? 'var(--mark-forbidden)' : 'none',
      textDecoration: forbidden ? 'line-through' : 'none',
      textDecorationThickness: '1px'
    }
  }, name || status), name && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: colour
    }
  }, status), note && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
      color: 'var(--ink-2)',
      maxWidth: 'var(--measure-note)'
    }
  }, note));
}
export default VariantPill;
export { VariantPill };
