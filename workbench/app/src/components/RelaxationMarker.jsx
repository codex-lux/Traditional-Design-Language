import React from "react";

/* P7 — a compromise is counted AND appears on the drawing, at its location. A cut off the
   bay line is a joist run that does not land on a bearing wall; eleven transfer beams is a
   number a builder prices. Absolutely positioned on the sheet. */
const KIND = {
  'off-bay': {
    mark: '\u25B3',
    words: 'cut off the bay line'
  },
  'transfer-beam': {
    mark: '\u25B2',
    words: 'upper wall line does not continue below \u2014 transfer beam'
  },
  'unsupported': {
    mark: '\u25C7',
    words: 'wall line unsupported at this level'
  }
};
function RelaxationMarker({
  kind = 'off-bay',
  index,
  note,
  x,
  y,
  onSelect,
  style
}) {
  const k = KIND[kind] || KIND['off-bay'];
  const positioned = x != null && y != null;
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onSelect ? function () {
      onSelect({
        kind: kind,
        index: index
      });
    } : undefined,
    title: note || k.words,
    style: {
      position: positioned ? 'absolute' : 'relative',
      left: x,
      top: y,
      transform: positioned ? 'translate(-50%,-50%)' : 'none',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      cursor: onSelect ? 'pointer' : 'default',
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: 15,
      height: 15,
      flex: 'none',
      display: 'grid',
      placeItems: 'center',
      color: 'var(--brick)',
      border: '1px solid var(--brick)',
      borderRadius: '50%',
      background: 'var(--paper-lit)',
      font: 'var(--fw-med) 8px/1 var(--mono)'
    }
  }, k.mark), index != null && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-med) 10px/1 var(--mono)',
      color: 'var(--brick)'
    }
  }, index));
}
export default RelaxationMarker;
export { RelaxationMarker };
