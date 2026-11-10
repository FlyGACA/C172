# Shared viewer modules

`shared/js` is the canonical implementation of the systems simulation, guided scenarios, and
SVG gauges used by both the Phase 7 and Phase 8 viewers. Each phase retains a small compatibility
module at its historical path so existing imports, bookmarks, and tests continue to work.

Changes to simulation behaviour or lesson scenarios belong here and must pass both phase test
suites with `npm test`.

`flight.js` is the flight model (six degrees of freedom, every coefficient labelled with its source),
`pilot.js` the scripted pilot that flies the handbook's figures in the tests and demonstrates the
lessons, and `flightdeck.js` the coupling of the flight model with the systems simulation. They are
used by the Phase 8 viewer; `08_realistic_digital_twin/tests/flight.test.mjs` states the tolerances
within which the model reproduces the Pilot's Operating Handbook.
