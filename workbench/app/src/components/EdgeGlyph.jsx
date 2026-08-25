import React from "react";

/* The single most important modelling decision in the project, made visible. descends_from
   and regional_of carry the kit cascade and are structurally heavier; references,
   reacts_against and revives are claims and carry nothing. Weight, not just hue. */
const CARRIES = {
  descends_from: 1,
  regional_of: 1
};
const VERB = {
  descends_from: 'descends from',
  regional_of: 'regional of',
  references: 'references',
  reacts_against: 'reacts against',
  revives: 'revives',
  member_of: 'member of'
};
function EdgeGlyph({
  type,
  from,
  to,
  note,
  width = 96,
  style
}) {
  const carries = !!CARRIES[type];
  const browsing = type === 'member_of';
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      minWidth: 0,
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: width,
      flex: 'none',
      height: 0,
      borderTop: carries ? 'var(--edge-carries-w) solid var(--edge-carries)' : 'var(--edge-claims-w) ' + (browsing ? 'dotted' : 'dashed') + ' var(--edge-claims)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: carries ? 'var(--ink)' : 'var(--ink-3)'
    }
  }, type), (from || to) && /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
      color: 'var(--ink-2)',
      marginLeft: 8
    }
  }, from, " ", VERB[type] || type, " ", to), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)'
    }
  }, browsing ? 'browsing only \u2014 carries no inheritance' : carries ? 'carries the kit cascade' : 'carries nothing'), note && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
      color: 'var(--ink-3)',
      maxWidth: 'var(--measure-note)',
      marginTop: 3
    }
  }, note)));
}
export default EdgeGlyph;
export { EdgeGlyph };
