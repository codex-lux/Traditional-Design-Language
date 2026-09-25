/* THE GLOSSARY: EVERY WORD THE WORKBENCH USES, AND ONE PAGE PER WORD (WP-14.8, PRD §E.2, §E.4).

   #/glossary          the index — every record, grouped by family in the schema's order
   #/glossary/<term>   one record, whole: what it means, what it rests on, what it is not

   Ruled 24 Sep 2026: definitions live in `glossary/` records the corpus checks
   (`build/check_glossary.py`), and the app writes none. So there is no sentence on this page
   the app wrote about a word: every term, sense, definition, analogy, longer note, source and
   quotation is the record's, fetched from `GET /api/glossary` by `api/useGlossary.js` — never
   imported into the bundle, which `build/check_frontend.py` checks. What the app does write is
   the furniture: the few labels that say which part of a record is which.

   THE FAMILY HEADINGS ARE THE SCHEMA'S OWN VALUES (`product`, `param-kind`, …), printed as they
   are. A family is not itself a glossary record, and a table of friendlier family names here
   would be exactly the app-written "kind heading" PRD §J.4 forbids; the report names the gap.

   A BARE `#/glossary` SHOWS THE INDEX, never a remembered or default term — the URL decides what
   is read (PRD §F.4). `?q=` narrows by the words a reader would type and `?family=` to one family,
   both in the URL through `useSurfaceFilters`, so a narrowed glossary is a link.

   The page reflows below the shell's 1380 px floor: the shell marks `#root` with `data-reflow`
   on this surface and the front door (PRD §I.12, WP-14.13), which `theme/tokens.css` releases,
   and the entries are laid out on a grid that folds to one column. The page head is the
   shell's too — it heads every surface from `nav/navModel.js`'s `headTermFor` — so neither is
   mounted here: `e2e/walk.mjs` asserts there is exactly one head, and two would fail it. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { formatHash } from '../router.js';
import { glossaryListing } from '../glossary/listing.js';
import { termView, provenanceOf, wordOf, wordForCite } from '../glossary/termView.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Chip } from '../Chrome.jsx';

const FILTERS = { q: { type: 'text' }, family: {} };

function Status({ glossary }) {
  if (glossary.status === 'failed') {
    return (
      <p role="status" className="tdl-glossary-status" data-glossary-failed="">
        The glossary could not be read
        {glossary.error && glossary.error.message ? ` — ${glossary.error.message}` : ''}.
      </p>
    );
  }
  return <p role="status" className="tdl-glossary-status" aria-busy="true">Reading the glossary…</p>;
}

function GlossaryIndex({ lookup }) {
  const { values, set, toggle } = useSurfaceFilters(FILTERS);
  const groups = glossaryListing(lookup, { q: values.q, family: values.family });
  const shown = groups.reduce((n, g) => n + g.terms.length, 0);
  const families = lookup.families().filter((f) => lookup.family(f).length > 0);
  return (
    <div className="tdl-glossary-index" data-glossary-index="">
      <div className="tdl-glossary-filters">
        <FilterInput value={values.q || ''} onChange={(v) => set('q', v)}
          label="Filter the glossary by word, sense or id" count={shown} />
        <span className="tdl-glossary-families" role="group" aria-label="family">
          {families.map((f) => (
            <Chip key={f} on={values.family === f} onClick={() => toggle('family', f)}>{f}</Chip>
          ))}
        </span>
      </div>
      {groups.map((g) => (
        <section key={g.family} className="tdl-glossary-family" data-family={g.family}
          aria-labelledby={`tdl-glossary-family-${g.family}`}>
          <h2 id={`tdl-glossary-family-${g.family}`} className="tdl-glossary-family-name">{g.family}</h2>
          <dl className="tdl-glossary-list">
            {g.terms.map((rec) => (
              <div key={rec.id} className="tdl-glossary-entry" data-glossary-term={rec.id}>
                <dt>
                  <a href={formatHash('glossary', { term: rec.id })}>{rec.term}</a>
                  {rec.sense && <span className="tdl-glossary-sense">{rec.sense}</span>}
                </dt>
                <dd>{rec.definition}</dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
      {!groups.length && <p role="status" className="tdl-glossary-status">No word matches.</p>}
    </div>
  );
}

function Field({ label, children }) {
  return (
    <section className="tdl-glossary-field">
      <Eyebrow as="h2">{label}</Eyebrow>
      {children}
    </section>
  );
}

function TermPage({ id, glossary }) {
  const lookup = glossary.lookup;
  const view = termView(glossary, { id });
  // The way back is named by the Glossary's own record, like every other word on this page.
  const back = (
    <p className="tdl-glossary-back">
      <a href={formatHash('glossary', {})}>{wordOf(lookup, 'surface-glossary')}</a>
    </p>
  );
  if (view.state !== 'ready') {
    return (
      <article className="tdl-glossary-page" data-glossary-page={id} data-missing="">
        {back}
        <h1 className="tdl-glossary-word">{view.text}</h1>
      </article>
    );
  }
  const rec = view.record;
  const prov = provenanceOf(rec);
  const aka = Array.isArray(rec.aka) ? rec.aka : [];
  const see = Array.isArray(rec.see) ? rec.see : [];
  const binds = Array.isArray(rec.binds) ? rec.binds : [];
  const surface = rec.surface && typeof rec.surface === 'object' ? rec.surface : null;
  const read = surface && Array.isArray(surface.read) ? surface.read : [];
  return (
    <article className="tdl-glossary-page" data-glossary-page={rec.id}>
      {back}
      <p className="tdl-glossary-kicker">{rec.family}<code>{rec.id}</code></p>
      <h1 className="tdl-glossary-word">{rec.term}</h1>
      {rec.sense && <p className="tdl-glossary-sense tdl-glossary-sense-lede">{rec.sense}</p>}
      <p className="tdl-glossary-def" data-definition="">{rec.definition}</p>
      {rec.analogy && <p className="tdl-glossary-analogy">{rec.analogy}</p>}
      {rec.more && <p className="tdl-glossary-more">{rec.more}</p>}

      {aka.length > 0 && (
        <Field label="Also called"><p>{aka.join(' · ')}</p></Field>
      )}
      {view.confusables.length > 0 && (
        <Field label="Not to be confused with">
          <ul className="tdl-glossary-links">
            {view.confusables.map((c) => (
              <li key={c.id || c.missing}>
                {c.missing
                  ? <span data-missing="">{c.text}</span>
                  : <><Term id={c.id} />{c.sense && <span className="tdl-glossary-sense">{c.sense}</span>}</>}
              </li>
            ))}
          </ul>
        </Field>
      )}
      {Array.isArray(rec.readers) && rec.readers.length > 0 && (
        <Field label="Who it is for">
          <dl className="tdl-glossary-readers">
            {rec.readers.map((r) => (
              <div key={r.who}><dt>{r.who}</dt><dd>{r.line}</dd></div>
            ))}
          </dl>
        </Field>
      )}
      {Array.isArray(rec.is_not) && rec.is_not.length > 0 && (
        <Field label="What it is not">
          <ul>{rec.is_not.map((s) => <li key={s}>{s}</li>)}</ul>
        </Field>
      )}
      {surface && (
        <Field label="The page">
          {surface.what && <p>{surface.what}</p>}
          {read.length > 0 && <ul>{read.map((s) => <li key={s}>{s}</li>)}</ul>}
          {surface.try && <p><RecordLink cite={surface.try}>{wordForCite(lookup, surface.try)}</RecordLink></p>}
        </Field>
      )}
      {see.length > 0 && (
        <Field label="See">
          <ul className="tdl-glossary-links">
            {see.map((c) => (
              <li key={c}><RecordLink cite={c}>{wordForCite(lookup, c)}</RecordLink></li>
            ))}
          </ul>
        </Field>
      )}
      {binds.length > 0 && (
        <Field label="Names the value">
          <ul>{binds.map((b) => <li key={`${b.field}=${b.value}`}><code>{b.field} = {b.value}</code></li>)}</ul>
        </Field>
      )}
      <Field label="Rests on">
        <p className="tdl-glossary-prov" data-kind={prov.kind || undefined}>{prov.kind}</p>
        {Array.isArray(rec.sources) && rec.sources.length > 0 && (
          <ul>{rec.sources.map((s) => <li key={s}>{s}</li>)}</ul>
        )}
        {prov.kind === 'editorial' && prov.items.length > 0 && (
          <ul className="tdl-glossary-reads">{prov.items.map((f) => <li key={f}><code>{f}</code></li>)}</ul>
        )}
        {typeof rec.basis === 'string' && rec.basis && <p className="tdl-glossary-basis">{rec.basis}</p>}
      </Field>
    </article>
  );
}

export function Glossary({ selection }) {
  const glossary = useGlossary();
  const termId = selection && typeof selection.term === 'string' ? selection.term : null;
  return (
    <div className="tdl-glossary-scroll">
      <div className="tdl-glossary" data-glossary="">
        {glossary.status !== 'ready'
          ? <Status glossary={glossary} />
          : (termId
            ? <TermPage id={termId} glossary={glossary} />
            : <GlossaryIndex lookup={glossary.lookup} />)}
      </div>
    </div>
  );
}
