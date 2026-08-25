import React from "react";

/* P5 + P8. The prose-capable card. Three things it must never lose:
   1. The style exception renders ABOVE the general rule when a style is in view.
   2. Two severity axes — how it reads, how it lives — are two axes, not one badge.
   3. All three fix tiers appear, named right / cheap / dishonest, because the cheap one
      is what actually gets built and naming the dishonest one is how the corpus stays honest. */
const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)'
};
const FIX = {
  right: 'var(--fix-right)',
  cheap: 'var(--fix-cheap)',
  dishonest: 'var(--fix-dishonest)'
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
const META = {
  font: 'var(--type-data-s)',
  color: 'var(--ink-3)'
};
function Axis({
  label,
  value,
  colour
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      flexDirection: 'column',
      gap: 3,
      minWidth: 92
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data)',
      color: colour || 'var(--ink-2)'
    }
  }, value));
}
function FaultCard({
  fault,
  styleInView,
  onSlot,
  style
}) {
  const exception = styleInView && fault.exceptions ? fault.exceptions.filter(function (e) {
    return e.style === styleInView;
  })[0] : null;
  return /*#__PURE__*/React.createElement("article", {
    style: {
      border: '1px solid var(--rule)',
      borderLeft: '2px solid ' + (SEV[fault.severity] || 'var(--ink-3)'),
      background: 'var(--paper)',
      padding: '18px 20px 20px',
      ...style
    }
  }, /*#__PURE__*/React.createElement("header", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: 'var(--fw-reg) var(--fs-d3)/1.15 var(--display)',
      fontVariationSettings: '"opsz" 40',
      letterSpacing: 'var(--tr-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, fault.name), fault.aka && fault.aka.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--fw-reg) italic 13px/1.5 var(--body)',
      color: 'var(--gilt-deep)',
      fontStyle: 'italic',
      marginTop: 4
    }
  }, fault.aka.map(function (a) {
    return '\u201c' + a + '\u201d';
  }).join(', ')), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 20,
      flexWrap: 'wrap',
      margin: '14px 0 0',
      paddingBottom: 14,
      borderBottom: '1px solid var(--rule-soft)'
    }
  }, /*#__PURE__*/React.createElement(Axis, {
    label: "how it reads",
    value: fault.severity,
    colour: SEV[fault.severity]
  }), /*#__PURE__*/React.createElement(Axis, {
    label: "how it lives",
    value: fault.frequency
  }), /*#__PURE__*/React.createElement(Axis, {
    label: "category",
    value: fault.category
  }), /*#__PURE__*/React.createElement(Axis, {
    label: "cause driver",
    value: fault.cause && fault.cause.driver
  }), fault.slots && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      flexDirection: 'column',
      gap: 3
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, "filed against"), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      gap: 8
    }
  }, fault.slots.map(function (s) {
    return onSlot ? /*#__PURE__*/React.createElement("button", {
      key: s,
      type: "button",
      onClick: function () {
        onSlot(s);
      },
      style: {
        font: 'var(--type-data)',
        color: 'var(--gilt-deep)'
      }
    }, s) : /*#__PURE__*/React.createElement("span", {
      key: s,
      style: {
        font: 'var(--type-data)',
        color: 'var(--ink-2)'
      }
    }, s);
  }))))), exception && /*#__PURE__*/React.createElement("section", {
    style: {
      margin: '16px 0 0',
      padding: '12px 14px',
      border: '1px solid var(--rule)',
      background: 'var(--paper-deep)',
      borderLeft: '2px solid var(--gilt-deep)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...EYE,
      color: 'var(--gilt-deep)'
    }
  }, "exception for ", exception.style), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13.5px/1.55 var(--body)',
      color: 'var(--ink)',
      margin: '7px 0 0'
    }
  }, exception.statement), exception.bounds && /*#__PURE__*/React.createElement("div", {
    style: {
      ...META,
      marginTop: 7
    }
  }, exception.bounds)), /*#__PURE__*/React.createElement("section", {
    style: {
      marginTop: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "symptom"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--type-prose)',
      color: 'var(--ink)',
      maxWidth: 'var(--measure-prose)',
      margin: '7px 0 0',
      textWrap: 'pretty'
    }
  }, fault.symptom)), fault.cause && /*#__PURE__*/React.createElement("section", {
    style: {
      marginTop: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "cause \u2014 driver: ", fault.cause.driver), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13.5px/1.6 var(--body)',
      color: 'var(--ink-2)',
      maxWidth: 'var(--measure-prose)',
      margin: '7px 0 0'
    }
  }, fault.cause.explanation), fault.cause.cost_saved && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-med) 13.5px/1.55 var(--body)',
      color: 'var(--gilt-deep)',
      margin: '9px 0 0'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8
    }
  }, "cost saved"), fault.cause.cost_saved)), fault.rule_violated && fault.rule_violated.length > 0 && /*#__PURE__*/React.createElement("section", {
    style: {
      marginTop: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "rule violated"), fault.rule_violated.map(function (r, i) {
    return /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: 'flex',
        gap: 10,
        alignItems: 'baseline',
        marginTop: 7
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        ...META,
        width: 168,
        flex: 'none'
      }
    }, r.kind, " \xB7 ", r.ref), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--fw-reg) 13px/1.55 var(--body)',
        color: 'var(--ink-2)',
        maxWidth: 'var(--measure-note)'
      }
    }, r.statement));
  })), fault.fix && /*#__PURE__*/React.createElement("section", {
    style: {
      marginTop: 18,
      borderTop: '1px solid var(--rule-soft)',
      paddingTop: 14
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "fix \u2014 three tiers, named plainly"), ['right', 'cheap', 'dishonest'].map(function (tier) {
    if (!fault.fix[tier]) return null;
    return /*#__PURE__*/React.createElement("div", {
      key: tier,
      style: {
        display: 'flex',
        gap: 12,
        alignItems: 'baseline',
        marginTop: 9
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: FIX[tier],
        border: '1px solid currentColor',
        padding: '1px 6px',
        width: 78,
        flex: 'none',
        textAlign: 'center'
      }
    }, tier), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--fw-reg) 13.5px/1.6 var(--body)',
        color: 'var(--ink-2)',
        maxWidth: 'var(--measure-prose)'
      }
    }, fault.fix[tier]));
  })), fault.test && /*#__PURE__*/React.createElement("section", {
    style: {
      marginTop: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "test \u2014 beside the statement, never instead of it"), /*#__PURE__*/React.createElement("pre", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-2)',
      background: 'var(--paper-mat)',
      border: '1px solid var(--rule-soft)',
      padding: '8px 10px',
      marginTop: 7,
      whiteSpace: 'pre-wrap'
    }
  }, fault.test)));
}
export default FaultCard;
export { FaultCard };
