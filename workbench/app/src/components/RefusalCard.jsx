import React from "react";

/* P3 — a refusal is content, not an error. Same rectangle, same weight, same padding as a
   result card. Never a toast, never a red banner, never an empty state. */
function RefusalCard({
  statement,
  reason,
  wouldChange,
  tool,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--rule)',
      borderLeft: '2px solid var(--refusal)',
      background: 'var(--paper)',
      padding: 'var(--panel-pad)',
      maxWidth: 'var(--measure-prose)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--refusal)',
      marginBottom: 9
    }
  }, "refused", tool && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--ink-4)',
      marginLeft: 8
    }
  }, tool)), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) var(--fs-body-l)/var(--lh-prose) var(--body)',
      color: 'var(--ink)',
      margin: '0 0 9px'
    }
  }, statement), reason && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      color: 'var(--ink-2)',
      margin: 0
    }
  }, reason), wouldChange && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      color: 'var(--ink-2)',
      margin: '9px 0 0'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-3)',
      marginRight: 8
    }
  }, "what would change it"), wouldChange));
}
export default RefusalCard;
export { RefusalCard };
