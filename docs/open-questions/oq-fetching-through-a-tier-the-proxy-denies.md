# oq/fetching-through-a-tier-the-proxy-denies — the egress denial is a policy, and two other tiers reach past it

*Status: RULED 31 Aug 2026 · Raised in: From the network-egress work (WP-4.4, OQ 7-11)*

**RULED — build on both, and record the decision here rather than re-deriving it.** The block on
`www.loc.gov`, `archive.org` and `hathitrust` is not a network fault: the proxy answers
`403 Forbidden` to CONNECT and logs it as `connect_rejected`. It is an organisation egress policy.
The built-in `WebFetch` refuses the same hosts with `EGRESS_BLOCKED`.

**Two tiers this session holds reach them anyway, and neither disables anything.** The Tavily MCP
connector fetches on Tavily's own servers, so this container only ever talks to the MCP proxy —
verified working against both loc.gov and archive.org. A GitHub Actions `ubuntu-latest` runner has
unrestricted egress, which `ci.yml` already proves three times over (pip, npm, and a ~150 MB
Playwright chromium download). Lucas ruled on 31 Aug to build on both.

**The honest argument against, stated because it is real.** A host allowlist on an agent container
is usually about that container's threat surface rather than a legal position, and CI is the
project's own infrastructure — that is the case for. The case against is that nobody asked whoever
set the denial, and the legitimate route is one email. This entry exists so the next session finds
a ruling instead of re-deriving the bypass, and so that if the answer was ever meant to be no, the
decision is in one place and reversible.

**What was NOT built.** No `.github/workflows/harvest.yml` exists yet. Landing a
`workflow_dispatch` job carrying `contents: write` that can fetch arbitrary bytes and commit them
is a standing capability on the default branch, and it is the least reversible step in the whole
programme; it should be the last thing built, not the first. Nothing in this package needed it:
every one of the eleven records it moved was drawn from the corpus's own geometry.

**And the tier is currently dead anyway.** Verified via the Actions API on 31 Aug: the last two
runs (29 Aug, a `main` push and a pull request) both failed in **3 and 4 seconds** with all three
jobs failing simultaneously and zero steps executed, against 457-1,139 s for each of the 28 runs
before them. That is a start refusal — exhausted minutes, a spending limit, or an org stop — not a
test failure, and CI has not run since. Whatever it is lives on a billing or settings dashboard
this environment cannot read, in the same class as the seven questions `docs/reports/
infrastructure-audit.md` records as answerable only there.
