# oq/the-atlas-pane-is-a-different-shape-in-ci-than-in-a-local-walk — one viewport, one build, two panes

*Status: OPEN · Raised in: the CI fixes of PR #42 (16 October 2026)*

**OPEN — the browser walk's atlas block counted 29 rings at the home view in CI and 33 on the
machine this was worked on, with the same viewport (1680 x 1000) and the same build. The atlas draws
the rings whose bounding box meets its viewBox and the viewBox takes the pane's own shape, so the two
machines were handed panes of different shape. Why is not established.**

## What was measured

`workbench/app/e2e/walk.mjs` asserted `30 <= rings <= 120` at the home view. CI's run on `20b7971`
read 29 and failed it; the walk here read 33 in each of three runs, two without the page's real
webfonts and one with them injected. The webfonts were the first suspect, because they changed the
plate-label check on the same run, and they do not move this count.

The band was a property of the layout and not of the data, which is shown directly. Visiting the
same address at five window sizes (1680 x 1000, 1280 x 700, 1000 x 900, 1680 x 600, 900 x 1000)
gives 10, 16, 4, 12 and 7 rings at the home view, every one outside the band. The count that does
not depend on the pane is the number of rings of the coarse tier whose recorded box meets the
viewBox the page itself carries, and the plate drew exactly that on all five. The walk asserts that
equality now. It is held by two cull defects driven through a build served from a second directory
(dropping the north clause drew more rings than met the view at all five sizes, and shaving the east
edge drew fewer), both red.

## What is not known

- What differs between the two machines' panes: the Chromium build (CI installs Playwright's own and
  this container carries `chromium-1194`), the fonts the chrome falls back to for the glyphs the page
  loads from Google, the scrollbar gutter, or state the earlier steps of the walk leave in the layout
  store. Nothing here can reproduce CI's 29.
- Whether the exact check holds in CI. It is shape-independent by construction and was verified at
  five shapes here; the CI run that follows this commit is its first read there.

## What it would take

One CI run with the atlas block printing the pane's width and height and the viewBox it read. If the
two panes differ by the chrome's height the cause is the shell's layout and the count was only ever a
symptom; if the viewBox attribute and the drawn rings disagree in CI, that is a real defect in the
cull and the exact check will say so by name.
