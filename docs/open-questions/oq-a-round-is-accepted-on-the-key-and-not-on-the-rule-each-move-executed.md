# oq/a-round-is-accepted-on-the-key-and-not-on-the-rule-each-move-executed — two accepted moves can leave the record breaking the first one's rule

*Status: OPEN · Raised in: the session's audit of WP-9.4 (2 Sep 2026)*

**OPEN — the loop accepts a round on `[fatal, serious, minor, faults present]`; it never
re-checks the rule each earlier move executed.**

Measured on `spec-builder-colonial` under the search engine, six rounds: `shutter-leaf-at-half-
the-opening` set `shutter_leaf_width_in` to half the declared opening, and a later round's
`narrow-the-window-and-keep-the-height` narrowed that opening to 32.8 in — leaving an 18 in
leaf against it, which is the ratio the first move was written to fix. Both rounds were
accepted: each lowered the key. The fault fires again on the next critique, and the leaf move
answers it again if a round is left (its tabu holds only refused pairs), so the loop converges
when it has rounds to spare and stops inconsistent when it does not.

The rule as ruled (1 Sep 2026) is a strict lexicographic improvement of the key, and WP-9.2's
report argues why a tie is a refusal. What is open is narrower: whether a move that executes a
fault's own fix should carry the DEPENDENT measurements with it (`narrow-the-window` rescaling
`shutter_leaf_width_in` when both are declared), or whether the loop should re-run the rule
each accepted move executed before calling the round accepted. The first is a move-level
change and belongs in `moves/registry.json`; the second changes the acceptance rule, which is
decision-level. Neither is taken here; the finding is recorded so that a report reading a
final key does not read consistency into it.
