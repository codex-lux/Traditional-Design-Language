import React from "react";

/* A receipt, never a warning. Every field the brief left blank became a decision the machine
   made; this row is how the user finds out what it chose. Styled as neutral information. */
function DecisionLogEntry({
  field,
  chose,
  because,
  source,
  onOverride,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      alignItems: 'baseline',
      padding: '7px 0',
      borderBottom: '1px solid var(--rule-soft)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-3)',
      width: 132,
      flex: 'none'
    }
  }, field), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-med) 13px/1.5 var(--body)',
      color: 'var(--receipt)'
    }
  }, chose), because && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
      color: 'var(--ink-3)',
      maxWidth: 'var(--measure-note)'
    }
  }, because)), source && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)',
      flex: 'none'
    }
  }, source), onOverride && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onOverride(field);
    },
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--gilt-deep)',
      flex: 'none'
    }
  }, "state it"));
}
export default DecisionLogEntry;
export { DecisionLogEntry };
