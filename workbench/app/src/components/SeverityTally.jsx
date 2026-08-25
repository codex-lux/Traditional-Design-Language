import React from "react";

/* The header line the corpus itself prints: fatal 4  serious 70  minor 59  advisory 1  info 13.
   Also the severity threshold control — 130 findings are solved by grouping and thresholds. */
const ORDER = ['fatal', 'serious', 'minor', 'advisory', 'info'];
const COLOUR = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)',
  advisory: 'var(--sev-advisory)',
  info: 'var(--sev-info)'
};
const FIELD = {
  fatal: 'var(--sev-fatal-field)',
  serious: 'var(--sev-serious-field)',
  minor: 'var(--sev-minor-field)',
  advisory: 'transparent',
  info: 'transparent'
};
function SeverityTally({
  counts,
  active,
  onSelect,
  size = 'default',
  style
}) {
  const small = size === 'small';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: small ? 4 : 6,
      alignItems: 'stretch',
      ...style
    }
  }, ORDER.map(function (s) {
    const n = counts && counts[s] != null ? counts[s] : 0;
    const on = active === s;
    const dim = n === 0;
    return /*#__PURE__*/React.createElement("button", {
      key: s,
      type: "button",
      onClick: onSelect ? function () {
        onSelect(on ? null : s);
      } : undefined,
      "aria-pressed": on,
      disabled: !onSelect,
      style: {
        flex: small ? 'none' : 1,
        textAlign: 'left',
        cursor: onSelect ? 'pointer' : 'default',
        borderLeft: '2px solid ' + (dim ? 'var(--rule)' : COLOUR[s]),
        background: on ? 'var(--paper-deep)' : dim ? 'transparent' : FIELD[s],
        padding: small ? '3px 7px' : '6px 9px',
        transition: 'var(--t-hover)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--fw-med) ' + (small ? '11px' : '12px') + '/1 var(--body)',
        color: dim ? 'var(--ink-4)' : COLOUR[s],
        letterSpacing: '.01em'
      }
    }, s), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: dim ? 'var(--ink-4)' : 'var(--ink-2)',
        marginLeft: small ? 6 : 0,
        display: small ? 'inline' : 'block',
        marginTop: small ? 0 : 4
      }
    }, n));
  }));
}
export default SeverityTally;
export { SeverityTally };
