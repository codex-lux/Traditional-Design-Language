import React from "react";
import { ToolTrace } from "./ToolTrace.jsx";

/* The persistent rail beside the canvas — never a modal, never a separate page. Rules it
   enforces structurally rather than by instruction:
   - every claim carries a citation that navigates the canvas
   - it says which findings it could not evaluate
   - it refuses out loud, as a card
   - it never calls a plan good */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
function Citation({
  cite,
  onCite
}) {
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onCite ? function () {
      onCite(cite);
    } : undefined,
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--gilt-deep)',
      borderBottom: '1px solid var(--link-underline)'
    }
  }, cite);
}
function AiRail({
  turns,
  onCite,
  onSend,
  placeholder,
  width,
  style
}) {
  return /*#__PURE__*/React.createElement("aside", {
    style: {
      width: width || 'var(--rail-ai)',
      flex: 'none',
      display: 'flex',
      flexDirection: 'column',
      borderLeft: '1px solid var(--rule)',
      background: 'var(--paper)',
      minHeight: 0,
      ...style
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      height: 'var(--substrip-h)',
      flex: 'none',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 12px',
      borderBottom: '1px solid var(--rule)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, "the rail"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)'
    }
  }, "24 tools")), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      overflow: 'auto',
      padding: '12px',
      display: 'flex',
      flexDirection: 'column',
      gap: 14,
      minHeight: 0
    }
  }, turns.map(function (t, i) {
    if (t.role === 'user') {
      return /*#__PURE__*/React.createElement("p", {
        key: i,
        style: {
          font: 'var(--fw-reg) 13px/1.55 var(--body)',
          color: 'var(--ink)',
          margin: 0,
          paddingLeft: 10,
          borderLeft: '2px solid var(--rule)'
        }
      }, t.text);
    }
    if (t.role === 'refusal') {
      return /*#__PURE__*/React.createElement("div", {
        key: i,
        style: {
          border: '1px solid var(--rule)',
          borderLeft: '2px solid var(--refusal)',
          background: 'var(--paper-deep)',
          padding: '11px 12px'
        }
      }, /*#__PURE__*/React.createElement("div", {
        style: {
          ...EYE,
          color: 'var(--refusal)',
          marginBottom: 6
        }
      }, "refused"), /*#__PURE__*/React.createElement("p", {
        style: {
          font: 'var(--fw-reg) 13px/1.55 var(--body)',
          color: 'var(--ink)',
          margin: 0
        }
      }, t.text), t.reason && /*#__PURE__*/React.createElement("p", {
        style: {
          font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
          color: 'var(--ink-2)',
          margin: '7px 0 0'
        }
      }, t.reason));
    }
    if (t.role === 'question') {
      return /*#__PURE__*/React.createElement("div", {
        key: i,
        style: {
          border: '1px solid var(--rule)',
          background: 'var(--paper-deep)',
          padding: '11px 12px'
        }
      }, /*#__PURE__*/React.createElement("div", {
        style: {
          ...EYE,
          marginBottom: 6,
          display: 'flex',
          alignItems: 'center',
          gap: 7
        }
      }, /*#__PURE__*/React.createElement("span", {
        "aria-hidden": "true",
        style: {
          width: 10,
          height: 10,
          border: '1px solid var(--judge-unjudged)',
          backgroundImage: 'var(--hatch-unjudged)'
        }
      }), "for you to decide"), /*#__PURE__*/React.createElement("p", {
        style: {
          font: 'var(--fw-reg) 13px/1.55 var(--body)',
          color: 'var(--ink)',
          margin: 0
        }
      }, t.text), t.cite && /*#__PURE__*/React.createElement("div", {
        style: {
          marginTop: 7
        }
      }, /*#__PURE__*/React.createElement(Citation, {
        cite: t.cite,
        onCite: onCite
      })));
    }
    return /*#__PURE__*/React.createElement("div", {
      key: i
    }, t.calls && /*#__PURE__*/React.createElement(ToolTrace, {
      calls: t.calls,
      onCite: onCite,
      running: t.running,
      style: {
        marginBottom: 9
      }
    }), /*#__PURE__*/React.createElement("p", {
      style: {
        font: 'var(--fw-reg) 13px/1.6 var(--body)',
        color: 'var(--ink-2)',
        margin: 0
      }
    }, t.text), t.cites && t.cites.length > 0 && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: 10,
        marginTop: 8
      }
    }, t.cites.map(function (c) {
      return /*#__PURE__*/React.createElement(Citation, {
        key: c,
        cite: c,
        onCite: onCite
      });
    })), t.unjudged && /*#__PURE__*/React.createElement("p", {
      style: {
        display: 'flex',
        gap: 8,
        alignItems: 'flex-start',
        font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
        color: 'var(--ink-3)',
        margin: '9px 0 0'
      }
    }, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        width: 11,
        height: 11,
        flex: 'none',
        marginTop: 3,
        border: '1px solid var(--judge-unjudged)',
        backgroundImage: 'var(--hatch-unjudged)'
      }
    }), t.unjudged));
  })), /*#__PURE__*/React.createElement("form", {
    onSubmit: function (e) {
      e.preventDefault();
    },
    style: {
      flex: 'none',
      borderTop: '1px solid var(--rule)',
      padding: 10
    }
  }, /*#__PURE__*/React.createElement("input", {
    placeholder: placeholder || 'Ask the corpus\u2026',
    onKeyDown: onSend ? function (e) {
      if (e.key === 'Enter') {
        // only clear when the host accepted the message — a busy rail must not
        // silently eat what the user typed
        if (onSend(e.currentTarget.value) !== false) e.currentTarget.value = '';
      }
    } : undefined,
    style: {
      width: '100%',
      background: 'var(--paper-mat)',
      border: '1px solid var(--rule-soft)',
      color: 'var(--ink)',
      font: 'var(--fw-reg) 13px/1.5 var(--body)',
      padding: '7px 9px'
    }
  })));
}
export default AiRail;
export { AiRail };
