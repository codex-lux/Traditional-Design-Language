import React from "react";

/* P4 — rank them, never crown one. Three rules this component exists to enforce:
   1. trades_away sits adjacent to the score at all times, never behind a disclosure.
   2. score and rightness are DIFFERENT AXES. The native diagram often scores worst; the
      'why' line reads at the same weight as the number so nobody conflates them.
   3. THE NUMBER SHOWS ITS WORKING. It used to be a demerit total — lower is better, no
      ceiling, and the line under it printed the WEIGHTS as a legend ("100/fatal · 8/serious
      · 1/minor − fidelity (7)") which reads as a count of fatal findings and explains
      nothing about the figure above it. It is now a composite out of 100, higher is better,
      and every axis is shown with its own share, its weight and the denominator that share
      was taken over. An axis that could not be evaluated says so and has its weight dropped;
      a fatal finding forfeits the score outright and the reason is printed in its place. */
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-3)'
};
const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)'
};
const h = React.createElement;

/* `why_this_diagram` is a LIST of reasons and was being handed to React whole. React
   concatenates an array of strings with nothing between them, so the native case read
   "native to tidewater-georgianfour-over-four is a canonical massing for the style", and
   the borrowed case interpolated the array into a template literal, which joins on commas
   AND repeats the "NOT native to this style" the surrounding span had just said. Both
   were in the shipped workbench. Joined properly here, and the redundant clause dropped
   where the caller has already made that point in its own colour. */
function whyText(why, dropNativity) {
  return (Array.isArray(why) ? why : [why]).filter(Boolean).map(String)
    /* strip only the clause the caller already printed, never the sentence it opens —
       "the composer is borrowing a diagram" is the part worth reading */
    .map((w) => (dropNativity ? w.replace(/^NOT native to this style\s*[—-]\s*/i, '') : w))
    .filter((w) => w.trim())
    .join('; ');
}

/* The headline and its whole arithmetic. Rendered from compose.py's `score_axes`, which
   carries one row per axis: its weight out of 100, the share of its own denominator that
   came back clean, and what that denominator was. The bar behind each row is the share, so
   the shape of a candidate is readable before any of the numbers are. */
function ScoreBlock({ candidate: c }) {
  const axes = c.score_axes || [];
  const forfeit = c.score == null;
  return h(React.Fragment, null,
    h("div", { style: { display: 'flex', alignItems: 'baseline', gap: 9, marginTop: 12 } },
      h("span", { style: { font: 'var(--fw-reg) 26px/1 var(--mono)',
                           color: forfeit ? 'var(--sev-fatal)' : 'var(--ink)' } },
        forfeit ? '—' : c.score.toFixed(1)),
      h("span", { style: { ...EYE } }, forfeit ? "score forfeit" : "score")),
    !forfeit && h("div", { style: { ...EYE, color: 'var(--ink-4)', marginTop: 3 } },
      "out of 100 · higher is better"),
    /* A forfeited score is never a blank. The corpus states its refusals. */
    c.score_forfeit && h("p", {
      style: { font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--sev-fatal)',
               margin: '6px 0 0' }
    }, c.score_forfeit),
    axes.length > 0 && h("div", { style: { marginTop: 10 } },
      h("div", { style: EYE }, "how it scores"),
      axes.map(function (a) {
        const pct = a.share == null ? null : Math.round(a.share * 100);
        const title = [a.what, a.denominator && ('over ' + a.denominator),
                       a.unjudged ? (a.unjudged + ' could not be judged and are not counted as passed') : null,
                       a.note].filter(Boolean).join(' — ');
        return h("div", {
          key: a.axis, title,
          style: { position: 'relative', display: 'grid',
                   gridTemplateColumns: '1fr auto auto', columnGap: 8, alignItems: 'baseline',
                   padding: '2px 4px', marginTop: 1,
                   /* the share, drawn behind the row rather than beside it — four columns
                      of these have no width to spare for a separate bar */
                   backgroundImage: pct == null ? 'none'
                     : `linear-gradient(to right, var(--paper-deep) ${pct}%, transparent ${pct}%)` }
        },
          h("span", { style: { font: 'var(--type-data-s)', color: 'var(--ink-2)',
                               whiteSpace: 'nowrap', overflow: 'hidden',
                               textOverflow: 'ellipsis' } },
            a.axis,
            /* the mark, not the number — the count would wrap every row it appears on and
               make the eight axes unreadable as a block. It is said once, in full, below. */
            a.unjudged ? h("span", { style: { color: 'var(--ink-4)' } }, " °") : null),
          h("span", { style: { font: 'var(--type-data-s)',
                               color: pct == null ? 'var(--ink-4)' : 'var(--ink-3)' } },
            pct == null ? 'not evaluated' : pct + '%'),
          h("span", { style: { font: 'var(--type-data-s)', color: 'var(--ink-4)' } },
            (a.points == null ? '—' : a.points) + '/' + a.weight));
      })),
    /* Unjudged is not passed, and it is never left to a tooltip: the axes carrying checks
       the corpus could not evaluate are named here in full, under the mark they carry. */
    axes.some(function (a) { return a.unjudged; }) && h("p", {
      style: { font: 'var(--fw-reg) 12px/1.5 var(--body)', color: 'var(--ink-3)', margin: '7px 0 0' }
    }, "° ", axes.filter(function (a) { return a.unjudged; })
             .map(function (a) { return `${a.unjudged} ${a.axis}`; }).join(", "),
       " could not be evaluated on this plan. They are outside the fraction, not counted as passed."),
    c.score_weight_unevaluated > 0 && h("p", {
      style: { font: 'var(--fw-reg) 12px/1.5 var(--body)', color: 'var(--ink-3)', margin: '6px 0 0' }
    }, `Scored over ${c.score_weight_evaluated} of 100 points of evidence — `
     + `${c.score_weight_unevaluated} could not be evaluated on this plan, and are dropped `
     + `rather than passed.`));
}

function CandidateColumn({
  candidate,
  rank,
  selected,
  onSelect,
  children,
  style
}) {
  const c = candidate;
  const native = !!c.native;
  return /*#__PURE__*/React.createElement("section", {
    onClick: onSelect ? function () {
      onSelect(c);
    } : undefined,
    style: {
      flex: 1,
      minWidth: 0,
      border: '1px solid ' + (selected ? 'var(--gilt-deep)' : 'var(--rule)'),
      background: selected ? 'var(--paper-deep)' : 'var(--paper)',
      padding: '14px 15px 16px',
      cursor: onSelect ? 'pointer' : 'default',
      transition: 'var(--t-hover)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 9
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)'
    }
  }, rank), /*#__PURE__*/React.createElement("h3", {
    style: {
      font: 'var(--fw-reg) var(--fs-d4)/1.16 var(--display)',
      fontVariationSettings: '"opsz" 30',
      letterSpacing: 'var(--tr-display)',
      color: 'var(--ink)',
      margin: 0,
      flex: 1
    }
  }, c.parti_name)), /*#__PURE__*/React.createElement(ScoreBlock, {
    candidate: c
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      marginTop: 10,
      flexWrap: 'wrap'
    }
  }, ['fatal', 'serious', 'minor'].map(function (s) {
    const n = c.counts && c.counts[s] != null ? c.counts[s] : 0;
    return /*#__PURE__*/React.createElement("span", {
      key: s,
      style: {
        font: 'var(--type-data-s)',
        color: n === 0 ? 'var(--ink-4)' : SEV[s]
      }
    }, s, " ", n);
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 13,
      paddingTop: 12,
      borderTop: '1px solid var(--rule-soft)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: EYE
  }, "why"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.55 var(--body)',
      margin: '5px 0 0',
      color: native ? 'var(--green-deep)' : 'var(--ink-2)'
    }
  }, native ? whyText(c.why) : /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--gilt-deep)'
    }
  }, "NOT native to this style"), whyText(c.why, true) ? ' \u2014 ' + whyText(c.why, true) : ''))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...EYE,
      color: 'var(--gilt-deep)'
    }
  }, "trades away"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 13px/1.6 var(--body)',
      color: 'var(--ink)',
      margin: '5px 0 0',
      textWrap: 'pretty'
    }
  }, c.trades_away)), /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: '14px 0 0',
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      columnGap: 12,
      rowGap: 4
    }
  }, [['area', c.area], ['footprint', c.footprint], ['bays', c.bays], ['massing', c.massing]].filter(function (r) {
    return r[1];
  }).map(function (r) {
    return /*#__PURE__*/React.createElement(React.Fragment, {
      key: r[0]
    }, /*#__PURE__*/React.createElement("dt", {
      style: {
        ...EYE
      }
    }, r[0]), /*#__PURE__*/React.createElement("dd", {
      style: {
        font: 'var(--type-data-s)',
        color: 'var(--ink-2)',
        margin: 0
      }
    }, r[1]));
  })), c.warnings && c.warnings.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 13,
      paddingTop: 12,
      borderTop: '1px solid var(--rule-soft)'
    }
  }, c.warnings.map(function (w, i) {
    return /*#__PURE__*/React.createElement("p", {
      key: i,
      style: {
        display: 'flex',
        gap: 8,
        font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
        color: 'var(--ink-2)',
        margin: i ? '7px 0 0' : 0
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: 'var(--fw-semi) 12.5px/1.55 var(--mono)',
        color: 'var(--sev-serious)'
      }
    }, "!"), w);
  })), children);
}
export default CandidateColumn;
export { CandidateColumn };
