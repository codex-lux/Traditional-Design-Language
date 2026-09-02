# oq/a-slug-in-a-code-span-is-not-checked — the citation guard validates 16% of the namespace it guards, by TWO mechanisms, and the second one is bigger than the one this entry is named for

*Status: OPEN · Raised in: the WP-9.2 adversarial audit (1 Sep 2026)*

**`check_citations.py` validates named open-question citations, and it validates 26 of the 164 in
this tree — 15.9%.** The count moves as documents discuss the problem (the code-span bucket was
100 at `025329c` and 113 at `84314fa`), which is the finding demonstrating itself.

**Quote ONE denominator.** Earlier versions of this entry published a tree-wide walk (126 of 182)
beside the checker's own (121 of 165); the difference is almost entirely `docs/open-questions.md`,
the GENERATED index, which carries 19 mentions and which `tracked_files()` excludes by name. **The
checker's denominator is the one that answers the question**, because the question is about the
checker. Every figure below is measured with the checker's own `tracked_files()`, `CODE` and
`SLUG_CITE`. Mutation-tested both ways:

```
fake slug in plain prose          ->  DANGLING  ...:127: OQ-SLUG-THAT-NAMES-NO-ENTRY names no entry
the same fake slug in `backticks` ->  0 dangling, silently accepted
```

*(The fake slug is written in capitals above because the first draft of this entry used a real-
looking one and **`check_citations.py` convicted this file for it** — see "the entry convicted
itself" below.)*

The cause is one line, and it is deliberate:

```python
# An inline code span is a QUOTATION, not a citation. Documents that discuss this
# bug have to be able to write `OQ 82 and 84` to show what it looks like ...
line = CODE.sub(lambda c: " " * len(c.group(0)), line)
```

**That exemption was written for the NUMBERED namespace, where prose is the citation form and a
code span is the exception. For slugs the convention is inverted**: `` `oq/the-raw-kit-read` `` in
backticks *is* how this corpus cites a named question — CLAUDE.md does it, every report does it,
and this file does it in the sentence you are reading. So for slugs, citation and illustration are
typographically identical and the checker cannot tell them apart.

**120 of the 164 are hidden by this exemption**, and the count has risen with every document that
discusses it. The corpus froze its numbers at 99 and made slugs the primary mechanism
(`099-how-an-open-question-id-is-issued.md`), so the guard covers the legacy namespace and misses
most of the live one.

## There is a SECOND blind spot, it is larger, and two audit passes of this entry missed it

**An adversarial pass found this entry measuring the wrong thing, and the correction more than
doubles the hole.** `check_citations.py` does not scan the tree. It scans
`tracked_files()`, which is:

```python
subprocess.run(["git", "grep", "--untracked", "-lE", r"OQ [0-9]+", "--", "."], ...)
```

**A file that carries no NUMBERED citation is never opened at all**, so nothing in it is checked in
any context — plain prose included. Mutation-tested, appending the identical line
`See oq/totally-invented-slug for more.` in PLAIN PROSE to four files:

```
docs/reports/wp-9.2-the-parti-is-not-the-type.md               -> DANGLING (caught)
docs/open-questions/oq-the-proportion-band-forbids-the-square.md -> 0 dangling, silent
docs/open-questions/oq-the-parti-dissolved-its-own-dependencies.md -> 0 dangling, silent
docs/open-questions/oq-the-passage-is-divided-...md            -> 0 dangling, silent
```

The three silent ones carry no `OQ <n>` and so are never opened. **All three are question files
this very session authored.**

Measured with the checker's own `tracked_files()`, `CODE` and `SLUG_CITE`, over the tree excluding
the generated index:

| bucket | mentions |
|---|---|
| **VALIDATED** (plain prose, in a file the checker opens) | **26 — 15.9%** |
| hidden by the inline-code-span exemption | 120 |
| in a file the checker NEVER OPENS (no `OQ <n>` anywhere in it) | 15, of which **9 are plain prose** |
| in `SPECIMEN`, exempt by name and on purpose | 3 |
| | **164** |

**So the unguarded share is 82.3%, not the two thirds this entry's own title claimed**, and
"56 in plain prose (checked)" was false: 26 of those are checked and 30 are not.

**DO NOT TRUST THIS TABLE — RE-MEASURE IT.** Every figure here has moved in every pass that
touched this file, including the pass that wrote this sentence (121 hidden became 120 between two
edits of the paragraph above). The buckets are reproducible in about fifteen lines: import
`build/check_citations.py`, take its `tracked_files()`, `CODE` and `SLUG_CITE`, walk the tree
skipping `docs/open-questions.md`, and for each mention decide *file not in `tracked_files()`* →
never opened, else *inside a `CODE` span* → hidden, else validated. **The shape is the finding and
the numbers are its weather.**

**Eleven files are never opened and eight of them are entries in this register**:
`oq-a-licence-conditioned-on-the-wrong-axis`, `oq-a-material-neutral-assembly-decides-a-material-question`,
`oq-a-share-alike-photograph-has-no-home-in-the-asset-schema`, `oq-applies-when-means-two-things`,
`oq-regenerating-the-asset-manifest-discards-what-was-added-to-it`,
`oq-the-parti-dissolved-its-own-dependencies`,
`oq-the-passage-is-divided-and-the-corpus-has-no-word-for-it`,
`oq-the-proportion-band-forbids-the-square`, plus `build/harvest_habs.py`, `docs/assets.md` and
`tests/test_forbidden_slots.py`.

**And this mechanism GROWS while the other one is static.** The numbers froze at 99
(`099-how-an-open-question-id-is-issued.md`), so a question raised today has no reason to contain
an `OQ <n>` at all — which means **every new named entry is born outside the guard**, and the
share the checker validates falls with each one. That is the opposite of what a guard should do
as its namespace grows.

**This changes the answer, not just the number.** Shape (1) below said checking code spans "closes
the gap completely". It does not: 9 plain-prose citations in files the checker never opens stay
unread, and the count rises with every question raised. Any fix must change the FILE SELECTION as
well as the span rule — and the file selection is the cheaper half, since `tracked_files()` could
select on the slug pattern as well as `OQ <n>` in one line, with no ambiguity to resolve.

## Nothing is currently wrong, and that is the whole difficulty

Of the 120 hidden mentions, **108 resolve and 12 do not — and every one of the 12 is
deliberate.** Five were there before this audit; the rest were added by this entry and by CLAUDE.md
quoting it, which is the clearest possible statement of the problem: **a document cannot describe
the ambiguity without producing more of it**, and each correction pass has done so again.

| mention | where | what it is |
|---|---|---|
| `oq/no-such-question` ×4 | `tests/test_citations.py`, `CLAUDE.md`, this file ×2 | this checker's own test fixture, and the documents quoting it |
| `oq/span-partial-bearing-wall` ×7 | `099-…`, `oq-two-id-namespaces` ×2, `wp-8.1-the-citation-guard.md`, `CLAUDE.md`, this file ×2 | a hypothetical slug used to explain the naming scheme — `oq-two-id-namespaces` uses it precisely as its example of a slug that would duplicate OQ 98 |
| `oq/example-only` ×3 | this file only | proposed below as a safe illustration form — **and it is not one**; see the correction under (1). Line numbers are omitted from this table on purpose: they moved three times while it was being written |

So **the exemption is doing its job for three distinct illustrative slugs, and simply deleting it
would produce twelve false accusations.** This is not a dead guard to be switched on; it is a
guard whose blind spot is load-bearing.

## The question

**How does a document cite a named question distinguishably from illustrating one?** Four shapes —
**shape (0) is now built and the remaining question is narrower for it.** What is left is only the
code-span half: 120 of the 164 mentions still sit in backticks and are exempt, and the twelve that
resolve to nothing are all deliberate illustrations. The file-selection half is closed.

0. **~~Widen `tracked_files()` to select on the slug pattern too, not only `OQ <n>`.~~ BUILT,
   WP-9.6.** The `git grep` now selects on `OQ [0-9]+|oq/[a-z0-9][a-z0-9-]*`. It opens **11 more
   files** — eight of them entries in this register — taking the checker from 392 files to 403,
   and it closed the growing half: a new named question is no longer born outside the guard.
   `tests/test_citations.py::test_every_file_carrying_a_slug_citation_is_actually_OPENED_by_the_checker`
   pins it as a PROPERTY over the real tree rather than as a count, so it cannot go stale, and it
   was mutation-checked (revert the pattern → red). **It cost exactly one repair, and that repair
   is a third instance of a gotcha this corpus keeps paying for**: `build/harvest_habs.py` wrapped
   a real slug across a Python string-literal line break, and since the checker reads line by
   line it saw a truncated id. The string was rewrapped so the slug sits on one line — the
   checker was NOT taught to rejoin hyphen-ended lines, which would have made a second rule out
   of a formatting accident.
1. **Check slugs inside code spans, and give illustrations a form that is not a slug.** Rewrite the
   twelve as something the id pattern cannot match. **The first draft of this entry proposed
   `oq/<slug>` or `oq/example-only` and one of the two is wrong**: `SLUG_CITE` is
   `\boq/[a-z0-9][a-z0-9-]*`, so `oq/example-only` matches it exactly and adopting it would create
   the eleventh dangling citation this shape is meant to prevent — the entry proposing the fix
   demonstrating the bug for the second time. `oq/<slug>` is safe because `<` is outside the
   character class. Cheapest and closes the gap completely; costs one edit to a test fixture and
   four documents, and commits the corpus to never writing a plausible-looking example slug again.
2. **Check slugs inside code spans, with a declared exemption marker** — a trailing comment or an
   `<!-- illustration -->` on the line. Honest and explicit; adds a second thing to remember.
3. **Change the citation convention: cite slugs in plain prose, reserve backticks for
   illustration**, mirroring the numbered namespace exactly. Most consistent, and it means
   rewriting 100 mentions and retraining every future agent against what currently reads as
   idiomatic.
4. **Leave it, and record that named citations are checked only in prose.** Defensible only if
   somebody states it — an unstated blind spot in a guard is the WP-8.6 pattern, and this register
   already carries `oq/two-id-namespaces` about the cost of the split.

**(1) looks right and is not obviously right**, because "never write an example that looks like a
slug" is a rule nobody will remember — which is how they got written in the first place,
and how this entry's own proposed replacement broke it in the sentence proposing it. **And (1)
alone is not sufficient at all**, per (0) above.

## The entry convicted itself, which is the finding in one line

The first draft of this file wrote the mutation output with a plausible fake slug inside a
**fenced** code block. `check_citations.py` exempts only **inline** code spans — a fenced block is
scanned like prose — so the run came back `1 dangling`, naming this file, for an illustration of
the very ambiguity the file is about.

That is worth keeping rather than quietly fixing, because it sharpens the question. The corpus has
**three** contexts, not two, and only one of them is exempt:

| context | scanned? |
|---|---|
| plain prose, **in a file carrying an `OQ <n>`** | yes — and this is the numbered namespace's citation form |
| plain prose, in a file carrying none | **no** — the file is never opened; see the second blind spot above |
| ``inline `code span` `` | **no** — and this is the slug namespace's citation form |
| fenced ``` block ``` | yes, **in an opened file** |

**An earlier version of this table said "plain prose — yes" without qualification, and it was
false for three of this session's own question files.** The row is split now because the file
selection decides before the span rule ever runs. So an author illustrating a slug has at most one
place to do it safely (an inline span), and that is the same place a citation lives. Any fix in shape (1) above must say what an illustration looks
like, or the next person writing about this problem will trip the same wire.

## Provenance

Found by mutation-testing `check_citations.py` during the WP-9.2 audit rather than by reading it:
the plain-prose mutation failed as expected, the backticked one passed, and the difference is what
exposed the exemption. **Pre-existing — not introduced by WP-9.2** — though that package added six
named entries and dozens of backticked citations to a namespace it did not know was unguarded.
Nothing in the tree is dangling today; the guard simply would not notice if it were.
