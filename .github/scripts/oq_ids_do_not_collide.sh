#!/usr/bin/env bash
# THE ONLY PLACE A CROSS-BRANCH ID COLLISION IS DETECTABLE BEFORE IT COSTS A RENUMBER.
# Four collisions in four days, every one found at the merge and paid for afterwards with
# a sweep of ~1,500 references. `pull_request` gives us both refs, so the SECOND pull
# request to issue an id can be failed before it lands rather than renumbered after.
#
# The register being a directory is most of the fix, but not all of it: two sessions
# issuing id 99 with DIFFERENT slugs create two different PATHS, so git merges both
# without a conflict and the register carries two entries numbered 99. check_ids.py
# catches that within one tree; this catches it across two.
#
# A FILE RATHER THAN AN INLINE `run:` BLOCK SINCE WP-11.12, because the corpus job it used
# to live in is a five-way matrix now and this answers the same for every shard. Lifted
# verbatim; the only edit is taking the base ref as $1 instead of interpolating it.
set -euo pipefail
BASE_REF="${1:?usage: oq_ids_do_not_collide.sh <base-ref>}"

git fetch --no-tags --depth=1 origin "$BASE_REF"
BASE="origin/$BASE_REF"
files () { git ls-tree -r --name-only "$1" -- docs/open-questions/ 2>/dev/null | sort; }
ids () { files "$1" | sed -n 's#.*/\([0-9][0-9][0-9]\)-.*\.md#\1#p' | sort -u; }
# THE SET TO WALK IS THE INTERSECTION, NOT THE DIFFERENCE. The first version of this
# step walked ids this branch ADDED (base \ head reversed) and then asked for the
# BASE's file for that id -- non-empty only when the id is already in base, which is
# exactly what `added` excludes. Unsatisfiable on every iteration; the gate could not
# fire, and said "no collision" for the one case it exists to catch. A collision is
# an id BOTH sides carry under DIFFERENT filenames, so the population is `comm -12`.
# This also holds on a `pull_request` checkout, which is the MERGE commit: HEAD then
# carries both files, the id is in both sets, and the filename lists differ.
both=$(comm -12 <(ids "$BASE") <(ids HEAD))
collide=""
for id in $both; do
  b=$(files "$BASE" | grep -E "/${id}-" || true)
  h=$(files HEAD   | grep -E "/${id}-" || true)
  if [ "$b" != "$h" ]; then collide="$collide $id"; fi
done
if [ -n "$collide" ]; then
  echo "::error::open-question id(s)$collide exist on $BASE_REF under a"
  echo "different filename. Another session issued them first. Reissue this branch's"
  echo "under a NAMED id (docs/open-questions/oq-<slug>.md) and add a row to"
  echo "docs/open-questions/README.md's conversion table. PLAN-OF-ACTION.md §1: ids"
  echo "are never reused, and the side that merged first keeps its numbers."
  exit 1
fi
# The named namespace needs no comparison of its own: filename IS the id, so two
# sessions raising `oq-<slug>.md` have derived the same slug from the same subject
# and the conflict git refuses to auto-merge is the one you want. That is the whole
# point of freezing the numbers -- see docs/open-questions/oq-two-id-namespaces.md.
echo "No open-question id on this branch collides with $BASE_REF."
