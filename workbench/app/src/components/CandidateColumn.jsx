import React from "react";

/* P4 — rank them, never crown one. Two rules this component exists to enforce:
   1. trades_away sits adjacent to the score at all times, never behind a disclosure.
   2. score and rightness are DIFFERENT AXES. The native diagram often scores worst; the
      'why' line reads at the same weight as the number so nobody conflates them. */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)'
};
function CandidateColumn({
  candidate,
  rank,
  selected,
  onSelect,
  children,
  style
}) {
  const c = candidate;
  const native = !!c.native;
  return /*#__PURE__*/React.createElement("section", {
    onClick: onSelect ? function () {
      onSelect(c);
    } : undefined,
    style: {
      flex: 1,
      minWidth: 0,
      border: '1px solid ' + (selected ? 'var(--gilt-deep)' : 'var(--rule)'),
      background: selected ? 'var(--paper-deep)' : 'var(--paper)',
      padding: '14px 15px 16px',
      cursor: onSelect ? 'pointer' : 'default',
      transition: 'var(--t-hover)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 9
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)'
    }
  }, rank), /*#__PURE__*/React.createElement("h3", {
    style: {
      font: 'var(--fw-reg) var(--fs-d4)/1.16 var(--display)',
      fontVariationSettings: '"opsz" 30',
      letterSpacing: 'var(--tr-display)',
      color: 'var(--ink)',
      margin: 0,
      flex: 1
    }
  }, c.parti_name)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10,
      marginTop: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-reg) 26px/1 var(--mono)',
      color: 'var(--ink)'
    }
  }, c.score), /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE
    }
  }, "score")), c.score_arithmetic && /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)',
      marginTop: 4
    }
  }, c.score_arithmetic), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      marginTop: 10,
      flexWrap: 'wrap'
    }
  }, ['fatal', 'serious', 'minor'].map(function (s) {
    const n = c.counts && c.counts[s] != null ? c.counts[s] : 0;
    return /*#__PURE__*/React.createElement("span", {
      key: s,
      style: {
        font: 'var(--type-data-s)',
        color: n === 0 ? 'var(--ink-4)' : SEV[s]
      }
    }, s, " ", n);
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 13,
      paddingTop: 12,
      borderTop: '1px solid var(--rule-soft)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "why"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      margin: '5px 0 0',
      color: native ? 'var(--green-deep)' : 'var(--ink-2)'
    }
  }, native ? c.why : /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--gilt-deep)'
    }
  }, "NOT native to this style"), c.why ? ' \u2014 ' + c.why : ''))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...EYE,
      color: 'var(--gilt-deep)'
    }
  }, "trades away"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.6 var(--body)',
      color: 'var(--ink)',
      margin: '5px 0 0',
      textWrap: 'pretty'
    }
  }, c.trades_away)), /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: '14px 0 0',
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      columnGap: 12,
      rowGap: 4
    }
  }, [['area', c.area], ['footprint', c.footprint], ['bays', c.bays], ['massing', c.massing]].filter(function (r) {
    return r[1];
  }).map(function (r) {
    return /*#__PURE__*/React.createElement(React.Fragment, {
      key: r[0]
    }, /*#__PURE__*/React.createElement("dt", {
      style: {
        ...EYE
      }
    }, r[0]), /*#__PURE__*/React.createElement("dd", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-2)',
        margin: 0
      }
    }, r[1]));
  })), c.warnings && c.warnings.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 13,
      paddingTop: 12,
      borderTop: '1px solid var(--rule-soft)'
    }
  }, c.warnings.map(function (w, i) {
    return /*#__PURE__*/React.createElement("p", {
      key: i,
      style: {
        display: 'flex',
        gap: 8,
        font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
        color: 'var(--ink-2)',
        margin: i ? '7px 0 0' : 0
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--fw-semi) 12.5px/1.55 var(--mono)',
        color: 'var(--sev-serious)'
      }
    }, "!"), w);
  })), children);
}
export default CandidateColumn;
export { CandidateColumn };
