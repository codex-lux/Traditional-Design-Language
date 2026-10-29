import React from "react";
import { LadderChip } from "./Chip.jsx";

/* 97 of these per kit, most of them 'open'. Collapsed it is one 26px line: slot, binding,
   source, and the fault count filed against it. Open it carries the rule sentence, the
   authoring note, the variants ladder, the parameters with their kind, and the pack
   precedence. Prose stays beside the test: the rule sentence is never replaced by the number. */
/* The binding, the variant ranks and the parameter kinds are drawn as chips since Phase 17, one
   form per rung from `chips.js` (`components/Chip.jsx`); this file keeps no map of its own. */
const FAULT_LINK = {
  display: 'block',
  font: 'var(--fw-reg) 13px/1.5 var(--display)',
  marginTop: 4,
  textAlign: 'left'
};
const FAULT_TEXT = {
  ...FAULT_LINK,
  color: 'var(--text-secondary)'
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)'
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
      borderBottom: '1px solid var(--border-soft)',
      background: open ? 'var(--surface-panel)' : hover ? 'var(--surface-raised)' : 'transparent',
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
      color: 'var(--text-secondary)',
      width: 132,
      flex: 'none',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, slot.group), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data)',
      color: bind === 'open' ? 'var(--text-secondary)' : 'var(--text-body)',
      flex: 1,
      minWidth: 0,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, slot.id), /*#__PURE__*/React.createElement(LadderChip, {
    ladder: "binding",
    value: bind,
    style: {
      width: 74,
      flex: 'none',
      justifyContent: 'flex-start'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--text-secondary)',
      width: 190,
      flex: 'none',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, slot.source ? /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-secondary)'
    }
  }, "\u2191", slot.source.distance, "\xA0"), slot.source.id) : '\u2014'), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      width: 52,
      flex: 'none',
      textAlign: 'right',
      color: slot.faults ? 'var(--sev-serious)' : 'var(--text-secondary)'
    }
  }, slot.faults ? slot.faults.length + ' fault' + (slot.faults.length === 1 ? '' : 's') : '\u2014')), open && /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '4px 10px 16px 152px'
    }
  }, slot.rule && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13.5px/1.6 var(--body)',
      color: 'var(--text-body)',
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
        color: 'var(--text-secondary)',
        padding: '2px 18px 2px 0'
      }
    }, p.name), /*#__PURE__*/React.createElement("td", {
      style: {
        font: 'var(--type-data)',
        color: 'var(--text-body)',
        padding: '2px 12px 2px 0'
      }
    }, p.value), /*#__PURE__*/React.createElement("td", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)',
        padding: '2px 12px 2px 0'
      }
    }, p.unit), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: '2px 0'
      }
    }, /*#__PURE__*/React.createElement(LadderChip, {
      ladder: "source",
      value: p.kind
    })));
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
    return /*#__PURE__*/React.createElement(LadderChip, {
      key: v.name,
      title: v.note,
      ladder: "variant",
      value: v.status
    }, v.name);
  })), slot.variants.filter(function (v) {
    return v.note;
  }).map(function (v) {
    return /*#__PURE__*/React.createElement("p", {
      key: v.name,
      style: {
        font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
        color: 'var(--text-secondary)',
        margin: '7px 0 0',
        maxWidth: 'var(--measure-prose)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-body)',
        marginRight: 7
      }
    }, v.name), v.note);
  })), slot.note && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.6 var(--body)',
      color: 'var(--text-secondary)',
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
        color: 'var(--text-secondary)',
        marginTop: 4
      }
    }, p);
  })), slot.faults && slot.faults.length > 0 && /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, "faults filed here"), slot.faults.map(function (fl) {
    // A fault name navigates to its record, so it is a link and takes `.tdl-link` whole; with no
    // handler it is plain text in the working grey (WP-14.33's audit).
    return /*#__PURE__*/React.createElement(onFault ? "button" : "span", {
      key: fl.id,
      type: onFault ? "button" : undefined,
      onClick: onFault ? function () {
        onFault(fl.id);
      } : undefined,
      className: onFault ? "tdl-link" : undefined,
      style: onFault ? FAULT_LINK : FAULT_TEXT
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
