import React from "react";

/* P2 — the cascade is a first-class object, not a breadcrumb and not a tooltip. Tidewater
   Georgian resolves through 29 levels; appalachian-log-house reaches 34. Craftsman resolved
   91 of its 95 slots from ancestors before a line of its own was written, and that fact
   should be visible. Two forms: compact (one line, for a slot row) and full (the ladder). */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
function ProvenanceTrace({
  cascade,
  sourceId,
  mode = 'full',
  onSelect,
  collapseFrom = 6,
  style
}) {
  const [all, setAll] = React.useState(false);
  if (mode === 'compact') {
    const hit = cascade.filter(function (l) {
      return l.id === sourceId;
    })[0] || cascade[0];
    return /*#__PURE__*/React.createElement("span", {
      style: {
        display: 'inline-flex',
        alignItems: 'baseline',
        gap: 7,
        ...style
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-4)'
      }
    }, "\u2191", hit.distance), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: hit.distance === 0 ? 'var(--ink)' : 'var(--ink-2)'
      }
    }, hit.id));
  }
  const shown = all ? cascade : cascade.slice(0, collapseFrom);
  const hidden = cascade.length - shown.length;
  return /*#__PURE__*/React.createElement("div", {
    style: style
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      justifyContent: 'space-between'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: EYE
  }, "cascade\xA0\xA0(nearest first)"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)'
    }
  }, cascade.length, " levels")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 8
    }
  }, shown.map(function (l) {
    const isSource = l.id === sourceId;
    return /*#__PURE__*/React.createElement("button", {
      key: l.id,
      type: "button",
      onClick: onSelect ? function () {
        onSelect(l.id);
      } : undefined,
      style: {
        display: 'flex',
        alignItems: 'baseline',
        gap: 10,
        width: '100%',
        textAlign: 'left',
        height: 'var(--row-h)',
        padding: '0 6px',
        cursor: onSelect ? 'pointer' : 'default',
        background: isSource ? 'var(--paper-deep)' : 'transparent',
        borderLeft: isSource ? '2px solid var(--gilt-deep)' : '2px solid transparent',
        transition: 'var(--t-hover)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-4)',
        width: 22,
        flex: 'none',
        textAlign: 'right'
      }
    }, l.distance), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data)',
        flex: 1,
        minWidth: 0,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        color: isSource ? 'var(--gilt-deep)' : l.distance === 0 ? 'var(--ink)' : 'var(--ink-2)'
      }
    }, l.id), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-3)',
        flex: 'none'
      }
    }, l.bindings), l.detail && /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-4)',
        flex: 'none',
        maxWidth: 176,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        textAlign: 'right'
      }
    }, l.detail));
  })), hidden > 0 && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      setAll(true);
    },
    style: {
      ...EYE,
      color: 'var(--gilt-deep)',
      marginTop: 8
    }
  }, "show ", hidden, " further levels"));
}
export default ProvenanceTrace;
export { ProvenanceTrace };
