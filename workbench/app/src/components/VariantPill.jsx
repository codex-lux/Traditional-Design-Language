import React from "react";

/* A four-rank ladder, not a binary. 'forbidden' is positive knowledge — 851 forbidden
   variants and 228 forbidden bindings — and gets the loudest form in the system: a
   cross-hatched field with a ruled-through label. */
const LADDERS = {
  variant: {
    canonical: 'var(--var-canonical)',
    permitted: 'var(--var-permitted)',
    atypical: 'var(--var-atypical)',
    forbidden: 'var(--var-forbidden)'
  },
  binding: {
    specified: 'var(--bind-specified)',
    extends: 'var(--bind-extends)',
    forbidden: 'var(--bind-forbidden)',
    open: 'var(--bind-open)'
  },
  affinity: {
    canonical: 'var(--aff-canonical)',
    common: 'var(--aff-common)',
    possible: 'var(--aff-possible)',
    atypical: 'var(--aff-atypical)',
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
  const colour = (LADDERS[ladder] || LADDERS.variant)[status] || 'var(--ink-3)';
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
      backgroundImage: forbidden ? 'var(--hatch-forbidden)' : 'none',
      textDecoration: forbidden ? 'line-through' : 'none',
      textDecorationThickness: '1px'
    }
  }, name || status), name && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: colour,
      opacity: .75
    }
  }, status), note && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
      color: 'var(--ink-3)',
      maxWidth: 'var(--measure-note)'
    }
  }, note));
}
export default VariantPill;
export { VariantPill };
