import React from "react";
import { useGlossary } from '../api/useGlossary.js';
import { describeTerm } from '../glossary/termView.js';

/* The workhorse. 142 findings must fit on one screen collapsed, and any one of them must
   open to full prose: statement / why / fix, always in that order. Note that a fix often
   ends 'or record the relation as X if the separation is real' — that is a real
   interaction, so onAssert is a first-class prop, not an extra. */
const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)',
  advisory: 'var(--sev-advisory)',
  // info is set in --ink-2, not --sev-info (--ink-3): the word is read, and --ink-3 reads 3.15 : 1
  info: 'var(--text-secondary)'
};
const FIELD = {
  fatal: 'var(--sev-fatal-field)',
  serious: 'var(--sev-serious-field)',
  minor: 'var(--sev-minor-field)'
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--text-secondary)'
};
/* The rule a finding cites: a link that takes `.tdl-link` whole where it navigates, the working
   grey where it cannot (WP-14.33's audit). */
const RULE_LINK = {
  font: 'var(--type-data-s)'
};
const RULE_TEXT = {
  font: 'var(--type-data-s)',
  color: 'var(--text-secondary)'
};

function FindingRow({
  finding,
  expanded,
  onToggle,
  onAssert,
  onLocate,
  onCite,
  selected,
  dense,
  style,
  // WP-9.3: two tags the analyst adds beside the layer -- which engine placed the house a
  // drawn finding was read from, and what the finding MEANS to a generator. Both are
  // strings made by revision.js; this row only shows them.
  engineTag,
  classTag
}) {
  const [hover, setHover] = React.useState(false);
  /* What the engine tag and the class tag MEAN is each a glossary record's (WP-14.31); the two
     tooltips were written here, one of them carrying the work package that added the tag. */
  const glossary = useGlossary();
  const [openInner, setOpenInner] = React.useState(false);
  const open = expanded != null ? expanded : openInner;
  const sev = finding.severity;
  const colour = SEV[sev] || 'var(--text-secondary)';
  const toggle = function () {
    onToggle ? onToggle(finding) : setOpenInner(!open);
  };
  return /*#__PURE__*/React.createElement("div", {
    onMouseEnter: function () {
      setHover(true);
    },
    onMouseLeave: function () {
      setHover(false);
    },
    "data-layer": finding.layer,
    style: {
      borderBottom: '1px solid var(--border-soft)',
      borderLeft: '2px solid ' + colour,
      background: selected ? 'var(--surface-raised)' : open ? 'var(--surface-panel)' : hover ? 'var(--surface-raised)' : FIELD[sev] || 'transparent',
      transition: 'var(--t-finding)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: toggle,
    "aria-expanded": open,
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: 10,
      width: '100%',
      textAlign: 'left',
      minHeight: dense ? 'var(--row-h)' : 'var(--row-h-l)',
      padding: dense ? '5px 10px' : '8px 12px'
    }
  },
  /* THE STATEMENT HAS THE ROW (WP-18.5, 27 Nov 2026). A row was four columns, two of them fixed
     Courier: the severity, then the layer at 76 px under a group heading that had just said the
     layer, then the statement in what was left of a 430 px pane, then a room's id. The severity,
     the layer and the room are one narrow side column now, stacked, and the statement takes the
     rest with its two tags run on after it. Nothing a row said is gone.
     A FIRST CUT PUT THE LAYER, THE TAGS AND THE ROOM ON A LINE UNDER THE STATEMENT, and measured
     it: the statement went 212 to 325 px wide and a row went 66 to 86 px tall, so a screen held
     a quarter fewer findings. This file's first sentence is that the findings must fit. */
  /*#__PURE__*/React.createElement("span", {
    "data-finding-side": "",
    style: {
      display: 'flex',
      flexDirection: 'column',
      width: '5.4rem',
      flex: 'none',
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    "data-finding-severity": sev,
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: colour
    }
  }, sev), /*#__PURE__*/React.createElement("span", {
    "data-finding-layer": "",
    style: {
      font: 'italic var(--fw-reg) 13.5px/1.35 var(--body)',
      color: 'var(--text-secondary)'
    }
  }, finding.layer), finding.at && /*#__PURE__*/React.createElement("span", {
    "data-finding-at": "",
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--text-secondary)',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    },
    title: finding.at
  }, finding.at)), /*#__PURE__*/React.createElement("span", {
    "data-finding-statement": "",
    style: {
      flex: 1,
      minWidth: 0,
      font: 'var(--fw-reg) 15.5px/1.45 var(--body)',
      color: 'var(--text-body)',
      textWrap: 'pretty'
    }
  }, finding.statement, engineTag && /*#__PURE__*/React.createElement("span", {
    "data-engine-tag": "",
    title: describeTerm(glossary, 'finding-engine').title,
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--text-secondary)',
      marginLeft: 9,
      whiteSpace: 'nowrap'
    }
  }, engineTag), classTag && /*#__PURE__*/React.createElement("span", {
    "data-class-tag": "",
    title: describeTerm(glossary, 'finding-class').title,
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--text-accent)',
      marginLeft: 9,
      whiteSpace: 'nowrap'
    }
  }, classTag))), open && /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '2px 12px 14px calc(5.4rem + 22px)',
      maxWidth: 'calc(var(--measure-prose) + 5rem)'
    }
  }, finding.why && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 15px/1.55 var(--body)',
      color: 'var(--text-secondary)',
      margin: '0 0 8px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8
    }
  }, "why"), finding.why), finding.fix && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 15px/1.55 var(--body)',
      color: 'var(--text-secondary)',
      margin: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...EYE,
      marginRight: 8,
      color: 'var(--sev-cleared)'
    }
  }, "fix"), finding.fix), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 14,
      marginTop: 10,
      alignItems: 'center'
    }
  }, finding.rule_ref && /*#__PURE__*/React.createElement(onCite ? "button" : "span", {
    type: onCite ? "button" : undefined,
    onClick: onCite ? function () { onCite(finding.rule_ref); } : undefined,
    className: onCite ? "tdl-link" : undefined,
    style: onCite ? RULE_LINK : RULE_TEXT
  }, finding.rule_ref), onLocate && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onLocate(finding);
    },
    className: "tdl-link",
    style: {
      font: 'var(--fw-reg) 14.5px/1.4 var(--body)'
    }
  }, "show on drawing"), onAssert && finding.assertable && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onAssert(finding);
    },
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--sev-cleared)'
    }
  }, "assert ", finding.assertable, " and re-score"))));
}
export default FindingRow;
export { FindingRow };
