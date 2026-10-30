import React from "react";

/* P2 — the cascade is a first-class object, not a breadcrumb and not a tooltip. Tidewater
   Georgian resolves through 20 levels; appalachian-log-house reaches 23, and monterey-revival 53. Craftsman resolves
   78 of its 97 slots from ancestors before a line of its own was written, and that fact
   should be visible. Two forms: compact (one line, for a slot row) and full (the ladder). */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)'
};
/* A LEVEL'S OWN BINDINGS AS A BAR (Phase 17, WP-17.10): specified, extends and forbidden, each its
   binding ink, the length against the busiest level in the cascade, so a thin kit reads thin. */
function LevelBar({ counts, max }) {
  const w = 64, seg = [['specified', 'var(--bind-specified)'], ['extends', 'var(--bind-extends)'],
    ['forbidden', 'var(--bind-forbidden)']];
  let x = 0;
  return /*#__PURE__*/React.createElement("svg", {
    "aria-hidden": "true", width: w, height: 8, style: { flex: 'none', alignSelf: 'center' }
  }, seg.map(function ([k, ink]) {
    const len = (counts[k] || 0) / max * w;
    const r = /*#__PURE__*/React.createElement("rect", { key: k, x: x, y: 1, width: len, height: 6, style: { fill: ink } });
    x += len;
    return r;
  }));
}

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
        color: 'var(--text-secondary)'
      }
    }, "\u2191", hit.distance), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: hit.distance === 0 ? 'var(--text-body)' : 'var(--text-secondary)'
      }
    }, hit.id));
  }
  const shown = all ? cascade : cascade.slice(0, collapseFrom);
  const maxB = Math.max(1, ...cascade.map(function (l) { return l.bindings || 0; }));
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
      color: 'var(--text-secondary)'
    }
  }, cascade.length, " levels")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 8
    }
  }, shown.map(function (l) {
    const isSource = l.id === sourceId;
    return /*#__PURE__*/React.createElement(React.Fragment, { key: l.id }, /*#__PURE__*/React.createElement("button", {
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
        minHeight: 'var(--row-h)',
        padding: '0 6px',
        cursor: onSelect ? 'pointer' : 'default',
        background: isSource ? 'var(--surface-raised)' : 'transparent',
        borderLeft: isSource ? '2px solid var(--text-accent)' : '2px solid transparent',
        transition: 'var(--t-hover)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)',
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
        color: isSource ? 'var(--text-accent)' : l.distance === 0 ? 'var(--text-body)' : 'var(--text-secondary)'
      }
    }, l.id), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)',
        flex: 'none'
      }
    }, l.bindings), l.counts && /*#__PURE__*/React.createElement(LevelBar, {
      counts: l.counts,
      max: maxB
    }), l.detail && /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)',
        flex: 'none',
        maxWidth: 176,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        textAlign: 'right'
      }
    }, l.detail)), l.bans && l.bans.length > 0 && /*#__PURE__*/React.createElement("div", {
      "data-cascade-bans": l.id,
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--text-secondary)',
        padding: '0 6px 4px 38px',
        overflowWrap: 'anywhere'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: { color: 'var(--refusal-text)', marginRight: 6 }
    }, "\u2715"), l.bans.map(function (b) {
      return b.variant ? b.slot + ' \u00b7 ' + b.variant : b.slot;
    }).join(', ')));
  })), hidden > 0 && /*#__PURE__*/React.createElement("button", {
    type: "button",
    // a control that navigates takes the link ink through the class (WP-14.33); Phase 17 moved
    // it off the gilt, which removes its row from inks.test's gilt remainder
    className: "tdl-link",
    onClick: function () {
      setAll(true);
    },
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      marginTop: 8
    }
  }, "show ", hidden, " further levels"));
}
export default ProvenanceTrace;
export { ProvenanceTrace };
