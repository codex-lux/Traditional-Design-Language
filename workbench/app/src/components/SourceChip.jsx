import React from "react";

/* P2 — attaches to every number in the product. 'invented' (25 of 1,556) is the only kind
   that shouts, and it must keep shouting so the number stays small. */
const KIND = {
  measured: {
    c: 'var(--kind-measured)',
    t: 'taken from a source or a real building'
  },
  editorial: {
    c: 'var(--kind-editorial)',
    t: 'an honest judgment call, marked as one'
  },
  derived: {
    c: 'var(--kind-derived)',
    t: 'computed from another value'
  },
  invented: {
    c: 'var(--kind-invented)',
    t: 'no precedent exists',
    field: 'var(--kind-invented-field)'
  },
  code: {
    c: 'var(--kind-code)',
    t: 'a building-code minimum, advisory IRC model text'
  }
};
function SourceChip({
  kind,
  value,
  unit,
  label = true,
  style
}) {
  const k = KIND[kind] || KIND.measured;
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'baseline',
      gap: 7,
      ...style
    }
  }, value != null && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data)',
      color: 'var(--ink)'
    }
  }, value, unit && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--ink-3)',
      marginLeft: 3
    }
  }, unit)), label && /*#__PURE__*/React.createElement("span", {
    title: k.t,
    style: {
      font: 'var(--type-data-s)',
      color: k.c,
      border: '1px solid currentColor',
      background: k.field || 'transparent',
      padding: '1px 5px',
      whiteSpace: 'nowrap'
    }
  }, kind));
}
export default SourceChip;
export { SourceChip };
