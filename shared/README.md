# Shared viewer modules

`shared/js` is the canonical implementation of the systems simulation, guided scenarios, and
SVG gauges used by both the Phase 7 and Phase 8 viewers. Each phase retains a small compatibility
module at its historical path so existing imports, bookmarks, and tests continue to work.

Changes to simulation behaviour or lesson scenarios belong here and must pass both phase test
suites with `npm test`.
