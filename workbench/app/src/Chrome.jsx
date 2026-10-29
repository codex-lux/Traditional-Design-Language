/* The instrument's frame: masthead, the trail, the left rail, the vocabulary filter strip.

   It is no longer FIXED, which is the change WP-5.7 made here. The left rail was 236px
   and the AI rail 344px at every window size and on every errand, which is 580px of
   permanent furniture — a third of a laptop screen — held whether you were navigating or
   reading a map. Both fold now, both pull, and `state/layout.js` owns the numbers.

   AND IT SAYS WHERE YOU ARE (WP-14.13). No page did: the tab title never changed, the masthead's
   persistent content was the bench plan's unlabelled ids, and the rail was a card catalogue of
   eleven surfaces in the order they were built, each labelled in words this file wrote and the
   palette and the Overview wrote differently. The rail is `nav/navModel.js`'s now — two spines
   (a style, a house) and a library, every label a glossary record's `term`, every figure beside
   one the API's — and the crumb strip is `nav/crumbs.js`'s. This file draws them and decides
   nothing about either. */
import React from 'react';
import { Eyebrow } from './components/Eyebrow.jsx';
import { Term, useTermDescription } from './components/Term.jsx';
import { noEntry } from './glossary/termView.js';
import { crumbLabel } from './nav/crumbs.js';
import { JOURNEY_WORDS, JOURNEY_TERMS } from './journey/journey.js';
import { layout } from './state/layout.js';
import { MarkGlyph } from './components/MarkGlyph.jsx';

/* A count and its word, apart from the other two: a count the check did not state is "not
   counted", never a zero (journey/journey.js's rule, in its words). */
function Count({ n, termId }) {
  return (
    <span style={{ whiteSpace: 'nowrap' }}>
      {n == null ? null : <span data-count={termId}>{n} </span>}
      <Term id={termId} />
      {n == null ? ` ${JOURNEY_WORDS.counts.notCounted}` : null}
    </span>
  );
}

/* What is on the bench, said as a place and three counts — never the plan's id and style as
   bare text, and never the counts of a plan that is not this one (the journey reads an
   evaluation only for the plan it was of). */
function OnTheBench({ plan, planStep }) {
  const counts = planStep && planStep.counts;
  const state = planStep ? planStep.state : null;
  const name = plan && typeof plan.name === 'string' && plan.name.trim() ? plan.name : (plan ? plan.id : null);
  const sep = <span aria-hidden="true" style={{ color: 'var(--text-secondary)' }}>{JOURNEY_WORDS.separator}</span>;
  return (
    <div data-bench="" style={{ display: 'flex', flexDirection: 'column', gap: 3, minWidth: 0 }}>
      {name && (
        <a href="#/workbench" data-bench-link=""
          style={{ font: 'var(--fw-med) 16px/1.3 var(--body)', color: 'var(--text-body)', borderBottom: 'none',
            overflowWrap: 'anywhere' }}>
          <span className="tdl-sr-only">On the bench: </span>{name}
        </a>
      )}
      {/* the counts, in mono: figures, not prose. Each count and the refusal word stand beside
          their mark's own form (WP-14.29), and the words are the counts' own Terms. */}
      <span style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: '2px 8px',
        font: 'var(--type-data-s)', color: 'var(--text-secondary)' }}>
        {state === 'refused' && (
          <span data-bench-refused="" style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
            <MarkGlyph token="--mark-refused" size={10} />
            <Term id={JOURNEY_TERMS.refused} />
          </span>
        )}
        {counts ? (
          <span data-bench-counts="" style={{ display: 'inline-flex', flexWrap: 'wrap', alignItems: 'baseline', gap: 5 }}>
            <Count n={counts.fatal} termId={JOURNEY_TERMS.fatal} />{sep}
            <Count n={counts.serious} termId={JOURNEY_TERMS.serious} />{sep}
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              <MarkGlyph token="--mark-unjudged" size={10} />
              <Count n={counts.unjudged} termId={JOURNEY_TERMS.unjudged} />
            </span>
          </span>
        ) : (state === 'unevaluated' ? <span data-bench-counts="">{JOURNEY_WORDS.plan.unevaluated}</span> : null)}
      </span>
    </div>
  );
}

/* The invitation to search. Its label is the one phrase the shell writes for an act (the front
   door's own test rules the same phrase there), and it is the `search-the-corpus` record's term,
   which `src/readerCopy.test.mjs` holds it to. What the search DOES -- which it used to explain in
   an eight-word tooltip written here -- is that record's definition, carried as the title and
   the described-by text (WP-14.31). */
function SearchInvitation({ onSearch }) {
  const d = useTermDescription('search-the-corpus');
  return (
    <>
      <button type="button" onClick={onSearch} aria-label="Search the corpus"
        aria-describedby={d.describedBy} title={d.title}
        style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0, width: '100%',
          padding: '3px 9px', border: '1px solid var(--border-hairline)', background: 'var(--surface-well)',
          color: 'var(--text-secondary)', transition: 'var(--t-hover)' }}>
        <span style={{ font: 'var(--fw-reg) 12.5px/1.4 var(--body)' }}>Search the corpus</span>
        <span style={{ flex: 1 }} />
        <span style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
          color: 'var(--text-secondary)' }}>⌘K</span>
      </button>
      {d.element}
    </>
  );
}

/* THE TOP BAR (Phase 17, WP-17.2; the masthead and the crumb strip until then). Forty-eight
   pixels of coal: the trail as an eyebrow, the address in the corpus's own grammar in mono beside
   it, and the one button that opens the assistant, which is folded until it is asked for. The
   wordmark, the bench, search and the keys moved into the sidebar; while the sidebar is folded the
   search and the keys stand here, so neither is ever off the screen. */
export function TopBar({ crumbs, address, onAsk, onSearch, onKeys, navOpen }) {
  const ask = useTermDescription('ask-the-corpus');
  return (
    <header data-topbar="" style={{ height: 'var(--topbar-h)', flex: 'none', display: 'flex', alignItems: 'center',
      gap: 16, padding: '0 16px', borderBottom: '1px solid var(--border-hairline)', background: 'var(--surface-chrome)' }}>
      {!navOpen && <Wordmark compact />}
      <CrumbStrip crumbs={crumbs} />
      {address && (
        <code data-address="" style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)', whiteSpace: 'nowrap',
          overflow: 'hidden', textOverflow: 'ellipsis', minWidth: 0, flexShrink: 1 }}>{address}</code>
      )}
      <div style={{ flex: 1 }} />
      {!navOpen && onSearch && <SearchInvitation onSearch={onSearch} />}
      {!navOpen && onKeys && <KeysButton onKeys={onKeys} />}
      {onAsk && (
        <button type="button" onClick={onAsk} data-ask="" aria-describedby={ask.describedBy} title={ask.title}
          style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '4px 12px',
            border: '1px solid var(--gilt)', color: 'var(--text-body)', whiteSpace: 'nowrap',
            font: 'var(--fw-med) 13px/1.3 var(--body)', transition: 'var(--t-hover)' }}>
          <Term id="ask-the-corpus" />
        </button>
      )}
      {ask.element}
    </header>
  );
}

/* The wordmark is the way home: once the rail folds, it was the only thing left on screen that
   looked like it named the product, and it went nowhere. In the sidebar it is also the site
   map's front-door item, so it carries that item's `data-nav`. */
function Wordmark({ compact, item }) {
  return (
    <a href="#/" data-home="" data-nav={item ? item.id : undefined}
      aria-current={item && item.current ? 'page' : undefined}
      style={{ font: `var(--fw-med) ${compact ? 11.5 : 12.5}px/1.55 var(--serif)`, letterSpacing: '.26em',
        textTransform: 'uppercase', color: 'var(--text-body)', borderBottom: 'none', display: 'block',
        whiteSpace: compact ? 'nowrap' : 'normal' }}>
      <span>Traditional&#183;<wbr />Design&#183;<wbr />Language</span>
    </a>
  );
}

function KeysButton({ onKeys }) {
  return (
    <button type="button" onClick={onKeys} data-keys="" aria-haspopup="dialog"
      style={{ display: 'inline-flex', alignItems: 'baseline', gap: 6, padding: '3px 9px',
        border: '1px solid var(--border-paper)', font: 'var(--type-data-s)', color: 'var(--text-secondary)',
        whiteSpace: 'nowrap', transition: 'var(--t-hover)' }}>
      Keys <kbd style={{ fontFamily: 'var(--mono)' }}>?</kbd>
    </button>
  );
}

/* Where you are, as a trail. Full width, between the masthead and the three panes, so it reads
   as the address of everything below it rather than of one pane. A group crumb is a heading and
   not a place, so it is not a link; the last crumb is the page and says so to a screen reader.
   The front door is the root and has no trail. */
export function CrumbStrip({ crumbs }) {
  if (!Array.isArray(crumbs) || !crumbs.length) return null;
  return (
    <nav aria-label="crumbs" style={{ minWidth: 0, overflow: 'hidden' }}>
      <ol style={{ display: 'flex', alignItems: 'baseline', gap: '0 8px', listStyle: 'none', margin: 0,
        padding: 0, whiteSpace: 'nowrap', font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
        textTransform: 'uppercase' }}>
        {crumbs.map((c, i) => {
          const last = i === crumbs.length - 1;
          const text = crumbLabel(c);
          return (
            <li key={`${i}:${c.cite || c.termId || text}`}
              style={{ display: 'inline-flex', alignItems: 'baseline', gap: 8,
                color: last ? 'var(--text-accent)' : 'var(--text-secondary)' }}>
              {i > 0 && <span aria-hidden="true" style={{ color: 'var(--text-secondary)' }}>›</span>}
              {last
                ? <span aria-current="page" data-missing={c.missing ? '' : undefined}>{text}</span>
                : (c.href
                  ? <a href={c.href} data-cite={c.cite || undefined} style={{ color: 'inherit' }}>{text}</a>
                  : <span data-group={c.group ? '' : undefined}>{text}</span>)}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

/* A folded pane, drawn as a spine rather than removed.

   Hiding a rail completely and hanging its opener off a floating button somewhere else
   is how a fold becomes a trapdoor: the reader loses the pane and has to find out where
   it went. A 26px spine costs almost nothing, keeps the shell's proportions legible, and
   puts the way back exactly where the thing was. */
export function PaneStub({ pane, label, spine, side, width = 26 }) {
  const edge = side === 'left'
    ? { borderRight: '1px solid var(--border-hairline)' }
    : { borderLeft: '1px solid var(--border-hairline)' };
  return (
    <div data-pane-stub={pane} style={{ width, flex: 'none', background: 'var(--surface-chrome)', ...edge,
      display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: 0 }}>
      <button type="button" onClick={() => layout.setCollapsed(pane, false)}
        aria-expanded={false} aria-label={`show ${label}`} title={`show ${label}`}
        style={{ width, height: 30, flex: 'none', color: 'var(--text-secondary)',
          font: 'var(--type-data-s)', fontFamily: 'var(--mono)', cursor: 'pointer',
          transition: 'var(--t-hover)' }}>
        {side === 'left' ? '›' : '‹'}
      </button>
      {/* The name of what is folded, turned up the spine — the fold is legible without
          hovering anything. It is the SHORT name: `label` is the accessible one and has
          to say what pressing the chevron does ("show the surface list"), while the spine
          has 26px and says what is folded ("surfaces"). They were one string, and the
          screen-reader name was the one that suffered. */}
      <span aria-hidden="true"
        style={{ writingMode: 'vertical-rl', font: 'var(--type-eyebrow)',
          letterSpacing: 'var(--tr-eyebrow)', textTransform: 'uppercase',
          color: 'var(--text-secondary)', marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden' }}>
        {spine || label}
      </span>
    </div>
  );
}

/* The control that folds a pane away, drawn small and quiet at the pane's own edge. */
export function FoldControl({ pane, label, side }) {
  return (
    <button type="button" onClick={() => layout.setCollapsed(pane, true)}
      aria-expanded aria-label={`hide ${label}`} title={`hide ${label}`}
      style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)', color: 'var(--text-secondary)',
        padding: '0 6px', cursor: 'pointer', flex: 'none', transition: 'var(--t-hover)' }}>
      {side === 'left' ? '‹' : '›'}
    </button>
  );
}

/* One place in the rail: an ANCHOR to its address, because a place is a link a reader can open
   in a new tab or copy — the rail was eleven buttons, and a button cannot be either. Its label
   and its description are its glossary record's (`useTermDescription`, since a Term may not sit
   inside an anchor); a record the glossary lacks is named as missing, visibly. A step number is
   the journey's order; a figure is the API's; a journey word goes on its own line, because a
   house step's state is a phrase and not a count. The label WRAPS and is never cut: the style in
   hand is named "<name> · the guided example", and at the rail's shipped width an ellipsis
   left the reader "the guided exa…". Its id is the margin note under it (navModel's `note`).
   */
function RailLink({ it, depth, width, desc }) {
  const on = !!it.current;
  const label = it.label != null ? it.label : (it.missing ? noEntry(it.missing) : '…');
  const figure = typeof it.meta === 'number';
  const words = typeof it.meta === 'string' ? it.meta : null;
  return (
    <>
      <a data-nav={it.id} href={it.href} aria-current={on ? 'page' : undefined}
        aria-describedby={desc ? desc.describedBy : undefined} title={desc ? desc.title : undefined}
        style={{ display: 'flex', flexDirection: 'column', width: '100%', boxSizing: 'border-box',
          padding: `4px 14px 4px ${14 + depth * 14}px`, minHeight: 28, borderBottom: 'none',
          textDecoration: 'none', cursor: 'pointer',
          background: on ? 'var(--surface-raised)' : 'transparent',
          borderLeft: on ? '2px solid var(--text-accent)' : '2px solid transparent',
          transition: 'var(--t-hover)' }}>
        <span style={{ display: 'flex', alignItems: 'baseline', gap: 9, width: '100%' }}>
          {it.step != null && (
            <span data-step-n="" style={{ font: 'var(--type-data-s)', fontFamily: 'var(--mono)',
              color: on ? 'var(--text-body)' : 'var(--text-secondary)', flex: 'none' }}>{it.step}</span>
          )}
          <span data-missing={it.label == null && it.missing ? '' : undefined}
            style={{ font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 13px/1.4 var(--body)',
              color: on ? 'var(--text-body)' : 'var(--text-secondary)', flex: 1, minWidth: 0,
              overflowWrap: 'anywhere' }}>
            {label}
          </span>
          {/* The figure is the first thing to go when the rail is pulled narrow: it is
              orientation, and the label is the control. */}
          {figure && width >= 200 && (
            <span data-meta="" style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)', flex: 'none',
              whiteSpace: 'nowrap' }}>{it.meta}</span>
          )}
        </span>
        {words && width >= 200 && (
          <span data-meta="" style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)',
            paddingLeft: it.step != null ? 17 : 0, whiteSpace: 'nowrap', overflow: 'hidden',
            textOverflow: 'ellipsis' }}>{words}</span>
        )}
        {it.note && width >= 200 && (
          <span data-note="" style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{it.note}</span>
        )}
      </a>
      {desc ? desc.element : null}
    </>
  );
}

function DescribedRailLink(props) {
  const desc = useTermDescription(props.it.termId);
  return <RailLink {...props} desc={desc} />;
}

function RailItem({ it, depth, width }) {
  return (
    <li style={{ listStyle: 'none' }}>
      {it.termId
        ? <DescribedRailLink it={it} depth={depth} width={width} />
        : <RailLink it={it} depth={depth} width={width} desc={null} />}
      {it.children && it.children.length > 0 && (
        <ul style={{ margin: 0, padding: 0 }}>
          {it.children.map((c) => <RailItem key={c.id} it={c} depth={depth + 1} width={width} />)}
        </ul>
      )}
    </li>
  );
}

/* THE SIDEBAR (Phase 17, WP-17.2; the left rail until then). Coal, 236 px by default and still
   the reader's to pull or fold. From the top: the wordmark, which is the front door; the house on
   the bench -- its name, its counts, and its five steps as stations (`JourneySpine`); the library,
   five rows, with Styles' own places under it only while the reader is among them
   (`nav/sidebar.js`); and search and the keys at the foot. Every label is a glossary record's and
   every figure the API's, as the rail's were. */
export function LeftRail({ model, view, busy, plan, planStep, spine, onSearch, onKeys }) {
  const open = React.useSyncExternalStore(layout.subscribe, () => layout.isOpen('nav'));
  const width = React.useSyncExternalStore(layout.subscribe, () => layout.width('nav'));
  const uid = React.useId().replace(/[^A-Za-z0-9_-]/g, '');
  if (!open) return <PaneStub pane="nav" label="the surface list" spine="surfaces" side="left" />;
  const house = view && view.house ? view.house.group : null;
  const library = view && view.library ? view.library.group : null;
  const head = (g) => (g ? (g.label != null ? g.label : (g.missing ? noEntry(g.missing) : '…')) : '…');
  return (
    <nav aria-label="surfaces" aria-busy={busy ? 'true' : undefined}
      style={{ width, flex: 'none', borderRight: '1px solid var(--border-hairline)',
        background: 'var(--surface-chrome)', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 0 18px' }}>
        <div style={{ padding: '0 16px 18px' }}>
          <Wordmark item={view ? view.home : null} />
        </div>
        <section data-nav-group="a-house" aria-labelledby={`rail-${uid}-house`}
          style={{ padding: '0 16px 18px', borderBottom: '1px solid var(--border-hairline)', marginBottom: 16 }}>
          <Eyebrow id={`rail-${uid}-house`} tone="accent" style={{ marginBottom: 8 }}>
            {plan ? <Term id="on-the-bench" /> : head(house)}
          </Eyebrow>
          {plan && (
            <div style={{ marginBottom: 12 }}>
              <OnTheBench plan={plan} planStep={planStep} />
            </div>
          )}
          {spine}
        </section>
        <section data-nav-group="library" aria-labelledby={`rail-${uid}-library`} style={{ marginBottom: 12 }}>
          <Eyebrow id={`rail-${uid}-library`} style={{ padding: '0 16px 8px' }}>{head(library)}</Eyebrow>
          <ul style={{ margin: 0, padding: 0 }}>
            {(view ? view.library.rows : []).map((it) => <RailItem key={it.id} it={it} depth={0} width={width} />)}
          </ul>
        </section>
      </div>
      <div style={{ flex: 'none', display: 'flex', flexDirection: 'column', gap: 8, padding: '10px 12px',
        borderTop: '1px solid var(--border-hairline)' }}>
        {onSearch && <SearchInvitation onSearch={onSearch} />}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {onKeys ? <KeysButton onKeys={onKeys} /> : <span />}
          <FoldControl pane="nav" label="the surface list" side="left" />
        </div>
      </div>
    </nav>
  );
}

/* The strip. `filters` is the {activeCount, clear} a surface gets from useSurfaceFilters;
   passing it puts a standing "N narrowing · clear" at the right-hand end. Every surface
   that filters gets the same one, in the same place, saying the same thing — there was
   one clear-all in the whole product before, hand-built on the Plan Workbench, and no
   surface at all said how many filters were on.

   `wrap` IS FOR A PAGE THAT REFLOWS (WP-14.30, tranche 2 PRD §E). The strip is one line, 34 px
   tall, and scrolls sideways when it is full. On a reflow surface that is the one thing the
   ruling forbids: at 1280 × 800 the Phylogeny's strip held 1176 px of controls in a 1018 px
   column and scrolled 158 px. With `wrap` the strip keeps its one-line height as a floor and
   takes a second line when it needs one; nothing in it is dropped. It is opt-in because three
   of this strip's callers are the floored surfaces that draw, where a second line would take
   height from the sheet. The walk's width block says which page needs it. */
export function FilterStrip({ children, right, filters, wrap, below }) {
  const n = filters ? filters.activeCount : 0;
  const line = wrap
    ? { minHeight: 'var(--substrip-h)', flexWrap: 'wrap', rowGap: 4, padding: '4px 14px' }
    : { height: 'var(--substrip-h)', padding: '0 14px', overflowX: 'auto', overflowY: 'hidden',
      scrollbarWidth: 'thin' };
  return (
    <div data-filter-strip={wrap ? 'wrap' : 'line'}
      style={{ ...line, flex: 'none', display: 'flex', alignItems: 'center', columnGap: 14,
        borderBottom: '1px solid var(--border-hairline)', background: 'var(--surface-panel)' }}>
      {children}
      <div style={{ flex: 1, minWidth: 14 }} />
      {/* Before `right`, not after it. The clear-all is the escape hatch from a strip that
          is already too full, so it must not be the control that a full strip pushes off
          the edge — which is exactly what happened on the Fault Corpus at 1680px. */}
      {/* STICKY, not merely early. Putting it before `right` stopped a full strip from
          PUSHING it off the edge, which is what the note above records — but the strip is
          `overflowX: auto`, so everything in it including this scrolls, and a reader who
          has over-filtered into an empty list had to scroll a 34px-tall bar sideways to
          find the way out. The same defect as the map legend scrolling its own
          leave-full-screen control away, and the same rule: a way out that can be scrolled
          away is not a way out. */}
      {n > 0 && (
        <button type="button" onClick={filters.clear} className="tdl-link"
          title="Show everything again"
          style={{ font: 'var(--type-data-s)', whiteSpace: 'nowrap', flex: 'none',
            position: 'sticky', right: 0, background: 'var(--surface-panel)',
            paddingLeft: 8, zIndex: 2 }}>
          {n} narrowing · clear
        </button>
      )}
      {right}
      {/* A row of its own beneath the rest, for a wrapping strip that has something to say about
          what was just picked (the Candidate Set's act). After `right` in the document as it is
          beneath it on the page, so the reading order and the tab order are the visual one. */}
      {wrap && below}
    </div>
  );
}

/* A filter. On or off, and it says so to a screen reader as well as to an eye.

   Chip used to be three things — a toggle, a radio, and a plain action like "download
   SVG" or "undo" — drawn identically, so a button that DID something looked exactly like
   a button that HID something. Actions moved to ActionChip; this one is now only ever a
   filter, and carries aria-pressed to prove it. */
export function Chip({ on, onClick, children, tone, title, radio }) {
  /* `aria-pressed` only where there is a state to press. Stamping it unconditionally put
     aria-pressed="false" on roughly fifteen plain acts that had not been migrated to
     ActionChip yet — "discard draft", "compose 4 candidates", a delete-window ×  — announcing
     each as an unpressed toggle, which is worse than the no-ARIA-at-all they had before.
     A chip with no `on` prop is an act; it gets plain button semantics. Found by an
     adversarial audit. */
  const aria = radio ? { role: 'radio', 'aria-checked': !!on }
    : (on === undefined ? {} : { 'aria-pressed': !!on });
  return (
    <button type="button" onClick={onClick} title={title} {...aria}
      style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
        border: '1px solid ' + (on ? (tone || 'var(--gilt-deep)') : 'var(--border-hairline)'),
        color: on ? (tone || 'var(--gilt-deep)') : 'var(--text-secondary)',
        background: on ? 'var(--surface-raised)' : 'transparent', transition: 'var(--t-hover)' }}>{children}</button>
  );
}

/* An act, not a state. Drawn with no border and a gilt hand so it cannot be mistaken for
   something that is switched on. */
export function ActionChip({ onClick, children, title, disabled, affix = '→' }) {
  return (
    <button type="button" onClick={onClick} title={title} disabled={disabled}
      style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
        display: 'inline-flex', alignItems: 'center', gap: 5, border: '1px solid transparent',
        color: disabled ? 'var(--text-disabled)' : 'var(--gilt-deep)',
        cursor: disabled ? 'default' : 'pointer', transition: 'var(--t-hover)' }}>
      {children}
      {affix && <span aria-hidden="true" style={{ color: disabled ? 'var(--text-disabled)' : 'var(--text-secondary)' }}>{affix}</span>}
    </button>
  );
}

/* Chips that are alternatives rather than independent switches — one level, one sort
   order, one view. The group is what tells a screen reader they are alternatives. */
export function ChipGroup({ label, children }) {
  return (
    <span role="radiogroup" aria-label={label}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      {children}
    </span>
  );
}

/* A cluster of filters that stays folded until wanted, showing what is on inside it while
   closed. This is the whole answer to a strip with eight axes on it: the two you steer by
   stay out, the rest fold into a word — and the word says whether anything inside is
   narrowing what you see, so folding never hides an active filter. */
export function FilterGroup({ label, summary, children, defaultOpen = false, active = 0 }) {
  const [open, setOpen] = React.useState(defaultOpen);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8, flex: 'none' }}>
      <button type="button" onClick={() => setOpen(!open)} aria-expanded={open}
        title={open ? `Fold ${label} away` : `Show the ${label} filters`}
        style={{ font: 'var(--type-data-s)', padding: '2px 7px', whiteSpace: 'nowrap',
          display: 'inline-flex', alignItems: 'center', gap: 6,
          border: '1px solid ' + (active ? 'var(--gilt-deep)' : 'var(--border-hairline)'),
          color: active ? 'var(--gilt-deep)' : 'var(--text-secondary)',
          background: open ? 'var(--surface-raised)' : 'transparent', transition: 'var(--t-hover)' }}>
        <span aria-hidden="true" style={{ color: 'var(--text-secondary)' }}>{open ? '−' : '+'}</span>
        {label}
        {!open && summary && (
          <span style={{ color: active ? 'var(--gilt-deep)' : 'var(--text-secondary)' }}>· {summary}</span>
        )}
      </button>
      {open && children}
    </span>
  );
}
