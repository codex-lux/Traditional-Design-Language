import React from "react";

/* 97 of these per kit, most of them 'open'. Collapsed it is one 26px line: slot, binding,
   source, and the fault count filed against it. Open it carries the rule sentence, the
   authoring note, the variants ladder, the parameters with their kind, and the pack
   precedence. Prose stays beside the test: the rule sentence is never replaced by the number. */
const BIND = {
  specified: 'var(--bind-specified)',
  extends: 'var(--bind-extends)',
  forbidden: 'var(--bind-forbidden)',
  open: 'var(--bind-open)'
};
const VAR = {
  canonical: 'var(--var-canonical)',
  permitted: 'var(--var-permitted)',
  atypical: 'var(--var-atypical)',
  forbidden: 'var(--var-forbidden)'
};
const KIND = {
  measured: 'var(--kind-measured)',
  editorial: 'var(--kind-editorial)',
  derived: 'var(--kind-derived)',
  invented: 'var(--kind-invented)',
  code: 'var(--kind-code)'
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
function SlotRow({
  slot,
  expanded,
  onToggle,
  onSource,
  onFault,
  style
}) {
  const [openInner, setOpenInner] = React.useState(false);
  const [hover, setHover] = React.useState(false);
  const open = expanded != null ? expanded : openInner;
  const bind = slot.binding;
  return /*#__PURE__*/React.createElement("div", {
    onMouseEnter: function () {
      setHover(true);
    },
    onMouseLeave: function () {
      setHover(false);
    },
    style: {
      borderBottom: '1px solid var(--rule-soft)',
      background: open ? 'var(--paper)' : hover ? 'var(--paper-deep)' : 'transparent',
      transition: 'var(--t-hover)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onToggle ? onToggle(slot) : setOpenInner(!open);
    },
    "aria-expanded": open,
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10,
      width: '100%',
      textAlign: 'left',
      height: 'var(--row-h)',
      padding: '0 8px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)',
      width: 132,
      flex: 'none',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, slot.group), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data)',
      color: bind === 'open' ? 'var(--ink-4)' : 'var(--ink)',
      flex: 1,
      minWidth: 0,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, slot.id), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: BIND[bind] || 'var(--ink-3)',
      width: 74,
      flex: 'none',
      textDecoration: bind === 'forbidden' ? 'line-through' : 'none'
    }
  }, bind), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-2)',
      width: 190,
      flex: 'none',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, slot.source ? /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--ink-4)'
    }
  }, "\u2191", slot.source.distance, "\xA0"), slot.source.id) : '\u2014'), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      width: 52,
      flex: 'none',
      textAlign: 'right',
      color: slot.faults ? 'var(--sev-serious)' : 'var(--ink-4)'
    }
  }, slot.faults ? slot.faults.length + ' fault' + (slot.faults.length === 1 ? '' : 's') : '\u2014')), open && /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '4px 10px 16px 152px'
    }
  }, slot.rule && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13.5px/1.6 var(--body)',
      color: 'var(--ink)',
      maxWidth: 'var(--measure-prose)',
      margin: '0 0 12px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8
    }
  }, "rule"), slot.rule), slot.parameters && slot.parameters.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "parameters"), /*#__PURE__*/React.createElement("table", {
    style: {
      marginTop: 6
    }
  }, /*#__PURE__*/React.createElement("tbody", null, slot.parameters.map(function (p) {
    return /*#__PURE__*/React.createElement("tr", {
      key: p.name
    }, /*#__PURE__*/React.createElement("td", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-2)',
        padding: '2px 18px 2px 0'
      }
    }, p.name), /*#__PURE__*/React.createElement("td", {
      style: {
        font: 'var(--type-data)',
        color: 'var(--ink)',
        padding: '2px 12px 2px 0'
      }
    }, p.value), /*#__PURE__*/React.createElement("td", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-3)',
        padding: '2px 12px 2px 0'
      }
    }, p.unit), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: '2px 0'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: KIND[p.kind] || 'var(--ink-3)',
        border: '1px solid currentColor',
        padding: '0 5px',
        background: p.kind === 'invented' ? 'var(--kind-invented-field)' : 'transparent'
      }
    }, p.kind)));
  })))), slot.variants && slot.variants.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "variants"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 8,
      marginTop: 6
    }
  }, slot.variants.map(function (v) {
    return /*#__PURE__*/React.createElement("span", {
      key: v.name,
      title: v.note,
      style: {
        font: 'var(--type-data-s)',
        color: VAR[v.status] || 'var(--ink-3)',
        border: '1px solid currentColor',
        padding: '1px 6px',
        background: v.status === 'forbidden' ? 'var(--bind-forbidden-field)' : 'transparent',
        backgroundImage: v.status === 'forbidden' ? 'var(--hatch-forbidden)' : 'none',
        textDecoration: v.status === 'forbidden' ? 'line-through' : 'none'
      }
    }, v.name);
  })), slot.variants.filter(function (v) {
    return v.note;
  }).map(function (v) {
    return /*#__PURE__*/React.createElement("p", {
      key: v.name,
      style: {
        font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
        color: 'var(--ink-3)',
        margin: '7px 0 0',
        maxWidth: 'var(--measure-prose)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: VAR[v.status],
        marginRight: 7
      }
    }, v.name), v.note);
  })), slot.note && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.6 var(--body)',
      color: 'var(--ink-2)',
      maxWidth: 'var(--measure-prose)',
      margin: '0 0 12px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8
    }
  }, "note"), slot.note), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 22,
      flexWrap: 'wrap'
    }
  }, slot.packs && slot.packs.length > 0 && /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, "pack precedence"), slot.packs.map(function (p) {
    return /*#__PURE__*/React.createElement("span", {
      key: p,
      style: {
        display: 'block',
        font: 'var(--type-data-s)',
        color: 'var(--ink-2)',
        marginTop: 4
      }
    }, p);
  })), slot.faults && slot.faults.length > 0 && /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, "faults filed here"), slot.faults.map(function (fl) {
    return /*#__PURE__*/React.createElement("button", {
      key: fl.id,
      type: "button",
      onClick: onFault ? function () {
        onFault(fl.id);
      } : undefined,
      style: {
        display: 'block',
        font: 'var(--fw-reg) 13px/1.5 var(--display)',
        color: 'var(--gilt-deep)',
        marginTop: 4,
        textAlign: 'left'
      }
    }, fl.name);
  })), slot.source && onSource && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onSource(slot.source.id);
    },
    style: {
      ...EYE,
      color: 'var(--gilt-deep)',
      alignSelf: 'flex-end'
    }
  }, "trace to origin"))));
}
export default SlotRow;
export { SlotRow };
