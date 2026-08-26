import React from "react";

/* Trust is built by watching it check, not by its confidence. A compact trace of the MCP
   tools consulted, with the records each one read.

   The mockup also used this in a Console surface's corpus-health strip. That surface was never
   built -- the rail runs from the Phylogeny -- and the corpus inventory it would have carried is
   already in the left rail's footer, fed live from /api/overview. Ruled 26 Aug 2026: strike the
   reference rather than build a twelfth surface to justify a sentence. Said here rather than
   deleted silently, because a component header that cites a screen nobody can open is how a spec
   and a product start disagreeing without either being wrong. */
function ToolTrace({
  calls,
  onCite,
  running,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--rule-soft)',
      background: 'var(--paper-mat)',
      padding: '8px 10px',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-4)',
      marginBottom: 6
    }
  }, "consulted", running && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--gilt-deep)',
      marginLeft: 8
    }
  }, "reading further\u2026")), calls.map(function (c, i) {
    return /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: 'flex',
        gap: 8,
        alignItems: 'baseline',
        padding: '2px 0'
      }
    }, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        width: 4,
        height: 4,
        flex: 'none',
        marginTop: 6,
        background: c.pending ? 'var(--ink-4)' : 'var(--green-deep)'
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-2)',
        flex: 'none'
      }
    }, c.tool), /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-4)',
        flex: 1,
        minWidth: 0,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }
    }, c.detail), c.cite && onCite && /*#__PURE__*/React.createElement("button", {
      type: "button",
      onClick: function () {
        onCite(c.cite);
      },
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--gilt-deep)',
        flex: 'none'
      }
    }, "open"));
  }));
}
export default ToolTrace;
export { ToolTrace };
