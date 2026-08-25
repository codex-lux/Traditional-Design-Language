import React from "react";

/* P1 — the most important mark in the system. Three states, and 'unjudged' is a FORM, not a
   colour: a colour would be read as a verdict. Same size and optical weight as the other two. */
function JudgmentMark({
  state,
  size = 13,
  label,
  reason,
  style
}) {
  const base = {
    width: size,
    height: size,
    flex: 'none',
    display: 'block'
  };
  const skin = state === 'pass' ? {
    background: 'var(--judge-pass)'
  } : state === 'fail' ? {
    background: 'var(--judge-fail)'
  } : {
    border: '1px solid var(--judge-unjudged)',
    backgroundImage: 'var(--hatch-unjudged)'
  };
  const words = {
    pass: 'evaluated \u2014 passed',
    fail: 'evaluated \u2014 failed',
    unjudged: 'could not evaluate'
  };
  const mark = /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      ...base,
      ...skin
    }
  });
  if (!label) return /*#__PURE__*/React.createElement("span", {
    title: reason || words[state],
    style: {
      display: 'inline-flex',
      ...style
    }
  }, mark);
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'flex-start',
      gap: 8,
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      height: 20
    }
  }, mark), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-med) 13px/1.5 var(--body)',
      color: state === 'unjudged' ? 'var(--ink-2)' : 'var(--ink)'
    }
  }, label), reason && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
      color: 'var(--ink-3)',
      maxWidth: 'var(--measure-note)'
    }
  }, reason)));
}
export default JudgmentMark;
export { JudgmentMark };
