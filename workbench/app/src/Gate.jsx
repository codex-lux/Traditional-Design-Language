/* The password screen.

   Deliberately says what it is guarding and what it is not: this is one shared password
   in front of a private corpus, not an account. Saying so is the same discipline the
   rest of the interface applies to its own states — a gate that implied per-user
   identity would be claiming something it cannot do. */
import React from 'react';
import { api } from './api/client.js';
import { Eyebrow } from './components/Eyebrow.jsx';

export function Gate({ onUnlocked }) {
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState(null);
  const [busy, setBusy] = React.useState(false);

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
        <p style={{
          font: 'var(--type-aside)', color: 'var(--ink-3)', margin: '0 0 22px',
          lineHeight: 1.5,
        }}>
          A shared password, not an account — everyone who has it sees the same corpus.
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
