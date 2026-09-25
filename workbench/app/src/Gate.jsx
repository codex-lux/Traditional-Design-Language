/* The password screen.

   Deliberately says what it is guarding and what it is not: this is one shared password
   in front of a private corpus, not an account. Saying so is the same discipline the
   rest of the interface applies to its own states — a gate that implied per-user
   identity would be claiming something it cannot do.

   AND IT SAYS WHAT THE CORPUS IS, IN ONE SENTENCE THAT IS NOT ITS OWN (WP-14.14, PRD §C.3).
   Ruled 24 Sep 2026: exactly one path is open to a visitor with no session,
   `GET /api/glossary/about-tdl`, and the Gate shows that record's definition under its
   heading. It asks for nothing else while signed out — no other glossary record, no count,
   no name — because every other corpus route answers 401 and would carry corpus text if it
   did not. If the read fails the Gate says NOTHING in its place: `frontdoor/aboutLine.js`
   answers null for every failure, and this file draws the sentence only where there is one.
   A fallback line written here would be a definition the glossary's checker never reads,
   shown to the one reader least able to tell (`src/frontDoor.test.mjs` holds this file to
   that by reading it). */
import React from 'react';
import { api } from './api/client.js';
import { Eyebrow } from './components/Eyebrow.jsx';
import { aboutLine } from './frontdoor/aboutLine.js';

export function Gate({ onUnlocked, auth }) {
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const [about, setAbout] = React.useState(null);

  React.useEffect(() => {
    let live = true;
    aboutLine(() => api.glossaryTerm('about-tdl')).then((line) => { if (live) setAbout(line); });
    return () => { live = false; };
  }, []);

  async function submit(e) {
    e.preventDefault();
    if (busy || !password) return;
    setBusy(true);
    setError(null);
    try {
      await api.login(password);
      onUnlocked();
    } catch (err) {
      const detail = err.body?.detail || {};
      setError(detail.retry_after_s
        ? `Too many attempts. Try again in about ${Math.ceil(detail.retry_after_s / 60)} minutes.`
        : (detail.error || 'That password was not accepted.'));
      setPassword('');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{
      height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--paper-deep)', padding: 24,
    }}>
      <form onSubmit={submit} style={{
        width: 'min(420px, 100%)', background: 'var(--paper)',
        border: '1px solid var(--rule)', borderRadius: 'var(--radius)',
        boxShadow: 'var(--shadow-plate)', padding: '32px 28px',
      }}>
        <Eyebrow tone="accent">Traditional Design Language</Eyebrow>
        <h1 style={{
          font: 'var(--type-title)', color: 'var(--ink)', margin: '10px 0 6px',
        }}>
          The Workbench
        </h1>
        {about && (
          <p data-about-tdl="" style={{
            font: 'var(--type-prose)', color: 'var(--ink)', margin: '0 0 12px',
          }}>{about}</p>
        )}
        <p style={{
          font: 'var(--type-aside)', color: 'var(--ink-3)', margin: '0 0 22px',
          lineHeight: 1.5,
        }}>
          {auth && auth.required && auth.password === false
            ? 'This deployment has no password set — it accepts an API token only, so '
              + 'there is nothing to type here. Set WORKBENCH_PASSWORD to allow browser access.'
            : 'A shared password, not an account — everyone who has it sees the same corpus.'}
        </p>

        <label htmlFor="wb-password" style={{ display: 'block' }}>
          <Eyebrow as="span" tone="secondary">Password</Eyebrow>
          <input
            id="wb-password"
            type="password"
            autoFocus
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: '100%', marginTop: 6, padding: '10px 12px',
              font: 'var(--type-data)', color: 'var(--ink)',
              background: 'var(--paper-mat)', border: '1px solid var(--rule)',
              borderRadius: 'var(--radius-0)',
            }}
          />
        </label>

        {error && (
          <p role="alert" style={{
            font: 'var(--type-aside)', color: 'var(--brick)', margin: '12px 0 0',
          }}>
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy || !password}
          style={{
            width: '100%', marginTop: 20, padding: '11px 14px',
            font: 'var(--type-name)', color: 'var(--paper)',
            background: busy || !password ? 'var(--ink-4)' : 'var(--ink)',
            border: 'none', borderRadius: 'var(--radius-0)',
            cursor: busy || !password ? 'default' : 'pointer',
          }}
        >
          {busy ? 'Checking…' : 'Enter'}
        </button>
      </form>
    </div>
  );
}

export default Gate;
