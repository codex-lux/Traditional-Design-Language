/* A SURFACE THAT COULD NOT LOAD IS SAID, NOT A BLANK APP (the second audit of Phase 17).

   Three surfaces load when first visited (`App.jsx`'s `React.lazy`). A chunk that fails to arrive --
   a tab left open across a deploy asking for a file the new build no longer has, or a dropped
   connection -- rejects, and with no boundary anywhere in the tree React unmounted the whole app.
   This boundary catches what a surface throws while it renders, says so under its record, carries
   the error's own message, and leaves the shell standing. It is keyed by the surface in `App.jsx`,
   so moving to another page starts it clean. */
import React from 'react';
import { Term } from './Term.jsx';

export class SurfaceBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;
    return (
      <div role="alert" data-surface-failed="" style={{ padding: '22px 26px', maxWidth: '72ch',
        borderLeft: '2px solid var(--refusal)', margin: '18px 22px' }}>
        <p style={{ font: 'var(--type-name)', color: 'var(--refusal-text)', margin: 0 }}>
          <Term id="page-not-loaded" />
        </p>
        <p style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)', margin: '6px 0 0', overflowWrap: 'anywhere' }}>
          {String(error && error.message ? error.message : error)}
        </p>
      </div>
    );
  }
}
