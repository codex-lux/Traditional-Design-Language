import React from "react";

/* The workhorse. 142 findings must fit on one screen collapsed, and any one of them must
   open to full prose: statement / why / fix, always in that order. Note that a fix often
   ends 'or record the relation as X if the separation is real' — that is a real
   interaction, so onAssert is a first-class prop, not an extra. */
const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)',
  advisory: 'var(--sev-advisory)',
  info: 'var(--sev-info)'
};
const FIELD = {
  fatal: 'var(--sev-fatal-field)',
  serious: 'var(--sev-serious-field)',
  minor: 'var(--sev-minor-field)'
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
function FindingRow({
  finding,
  expanded,
  onToggle,
  onAssert,
  onLocate,
  onCite,
  selected,
  dense,
  style
}) {
  const [hover, setHover] = React.useState(false);
  const [openInner, setOpenInner] = React.useState(false);
  const open = expanded != null ? expanded : openInner;
  const sev = finding.severity;
  const colour = SEV[sev] || 'var(--ink-3)';
  const toggle = function () {
    onToggle ? onToggle(finding) : setOpenInner(!open);
  };
  return /*#__PURE__*/React.createElement("div", {
    onMouseEnter: function () {
      setHover(true);
    },
    onMouseLeave: function () {
      setHover(false);
    },
    style: {
      borderBottom: '1px solid var(--rule-soft)',
      borderLeft: '2px solid ' + colour,
      background: selected ? 'var(--paper-deep)' : open ? 'var(--paper)' : hover ? 'var(--paper-deep)' : FIELD[sev] || 'transparent',
      transition: 'var(--t-finding)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: toggle,
    "aria-expanded": open,
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10,
      width: '100%',
      textAlign: 'left',
      minHeight: dense ? 'var(--row-h)' : 'var(--row-h-l)',
      padding: dense ? '4px 8px' : '7px 10px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: colour,
      width: 52,
      flex: 'none'
    }
  }, sev), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-3)',
      width: 76,
      flex: 'none'
    }
  }, finding.layer), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-reg) 12.5px/1.45 var(--body)',
      color: 'var(--ink)',
      flex: 1,
      textWrap: 'pretty'
    }
  }, finding.statement), finding.at && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)',
      flex: 'none'
    }
  }, finding.at)), open && /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '2px 10px 12px 150px',
      maxWidth: 'calc(var(--measure-prose) + 150px)'
    }
  }, finding.why && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      color: 'var(--ink-2)',
      margin: '0 0 8px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8
    }
  }, "why"), finding.why), finding.fix && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      color: 'var(--ink-2)',
      margin: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8,
      color: 'var(--green-deep)'
    }
  }, "fix"), finding.fix), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 14,
      marginTop: 10,
      alignItems: 'center'
    }
  }, finding.rule_ref && /*#__PURE__*/React.createElement(onCite ? "button" : "span", {
    type: onCite ? "button" : undefined,
    onClick: onCite ? function () { onCite(finding.rule_ref); } : undefined,
    style: {
      font: 'var(--type-data-s)',
      color: onCite ? 'var(--gilt-deep)' : 'var(--ink-4)',
      borderBottom: onCite ? '1px solid var(--link-underline)' : 'none'
    }
  }, finding.rule_ref), onLocate && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onLocate(finding);
    },
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--gilt-deep)'
    }
  }, "show on drawing"), onAssert && finding.assertable && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onAssert(finding);
    },
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--green-deep)'
    }
  }, "assert ", finding.assertable, " and re-score"))));
}
export default FindingRow;
export { FindingRow };
