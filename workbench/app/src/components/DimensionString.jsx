import React from "react";

/* Architectural dimensioning: ticks, not arrowheads; feet-and-inches, never decimal feet.
   Lives on the vellum sheet, so it draws in bistre. */
function feetInches(ft) {
  if (typeof ft === 'string') return ft;
  const whole = Math.floor(ft + 1e-9);
  const inches = Math.round((ft - whole) * 12);
  if (inches === 12) return whole + 1 + '\'-0"';
  return whole + '\'-' + inches + '"';
}
function DimensionString({
  segments,
  total,
  orientation = 'horizontal',
  length,
  showTotal,
  style
}) {
  const vertical = orientation === 'vertical';
  const segs = segments || (total != null ? [{
    ft: total
  }] : []);
  const sum = segs.reduce(function (a, s) {
    return a + (typeof s.ft === 'number' ? s.ft : 0);
  }, 0);
  const px = length != null ? length : sum * 13;
  const tickStyle = {
    position: 'absolute',
    background: 'var(--draw-dim)',
    width: 1,
    height: 'var(--tick-len)',
    top: vertical ? undefined : -3,
    left: vertical ? -3 : undefined,
    transform: 'rotate(60deg)'
  };
  let run = 0;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      width: vertical ? 26 : px,
      height: vertical ? px : 26,
      font: 'var(--dim-text)',
      color: 'var(--draw-dim)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      left: vertical ? 13 : 0,
      top: vertical ? 0 : 13,
      width: vertical ? 0 : px,
      height: vertical ? px : 0,
      borderTop: vertical ? 'none' : 'var(--lw-dim) solid var(--draw-dim)',
      borderLeft: vertical ? 'var(--lw-dim) solid var(--draw-dim)' : 'none'
    }
  }), segs.map(function (s, i) {
    const w = (typeof s.ft === 'number' ? s.ft : 0) / (sum || 1) * px;
    const at = run;
    run += w;
    return /*#__PURE__*/React.createElement(React.Fragment, {
      key: i
    }, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        ...tickStyle,
        left: vertical ? -3 : at + 13,
        top: vertical ? at + 13 : 6
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        position: 'absolute',
        whiteSpace: 'nowrap',
        color: 'var(--text-on-paper-2)',
        left: vertical ? 0 : at + w / 2,
        top: vertical ? at + w / 2 : 0,
        transform: vertical ? 'translateY(-50%) rotate(-90deg)' : 'translateX(-50%)'
      }
    }, s.label || feetInches(s.ft)), i === segs.length - 1 && /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        ...tickStyle,
        left: vertical ? -3 : at + w + 13,
        top: vertical ? at + w + 13 : 6
      }
    }));
  }), showTotal && /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      color: 'var(--text-on-paper)',
      whiteSpace: 'nowrap',
      left: vertical ? 0 : px + 10,
      top: vertical ? px + 10 : 0
    }
  }, feetInches(sum)));
}
export default DimensionString;
export { DimensionString };
