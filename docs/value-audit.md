# C172N value audit — `shared/js/sim.js` against the 1979 POH

source-verified: 2026-11-20

> Fly GACA is an independent educational platform, not affiliated with, endorsed by, or operated by GACA or the Government of Saudi Arabia. GACA (gaca.gov.sa) is always the authoritative source.
>
> فلاي قاكا منظومة تعليمية مستقلة، غير تابعة لهيئة الطيران المدني (GACA) وغير مرتبطة بها ولا معتمدة منها. هيئة الطيران المدني هي المصدر الرسمي.

Training and reference only. Not for flight, navigation or maintenance decisions.

## Scope and method

Every POH-tagged number in `shared/js/sim.js` was read against the source the repository itself
commits:

- `07_kinematic_twin/data/poh_references.json` and `08_realistic_digital_twin/data/poh_references.json`
  (the value list with page numbers, read on 2026-11-06);
- `04b_poh_reference/poh_1979_reference_data.json` (the source record and the public-scan caution);
- the handbook itself, Cessna Model 172N Pilot's Operating Handbook, 1 July 1978, 1979 model, for the
  pages marked *page image* below (read 2026-11-20).

Page numbers are POH section-page numbers (section-page), not PDF page numbers. "Verified" means the
value and its page agree with the source. "Illustrative" means the number is a modelling constant that
the code already labels as not from the handbook.

## The table

| Value (`sim.js` key) | Source | Page | Status |
| --- | --- | --- | --- |
| VNE 160 KIAS (`vne`) | POH, 1 Jul 1978 | 2-4 Fig 2-1 | Verified (KCAS 158) |
| VNO 128 KIAS (`vno`) | POH, 1 Jul 1978 | 2-4 Fig 2-1 | Verified (KCAS 126) |
| VFE 85 KIAS (`vfe`) | POH, 1 Jul 1978 | 2-4 Fig 2-1 | Verified for the printed 10–40° row |
| VFE 110 KIAS at 10° (not previously carried) | POH, 1 Jul 1978 | 2-4 Fig 2-1 | Verified (page image); overlaps the 85 row at 10° — see open item 1 |
| VA 97 KIAS (`va2300`) | POH, 1 Jul 1978 | 2-4 Fig 2-1 | Verified at 2300 lb (KCAS 96); utility 97 KIAS at 2000 lb |
| White arc 41–85 KIAS (`asiWhite`) | POH, 1 Jul 1978 | 2-5 Fig 2-2 | Verified |
| Green arc 47–128 KIAS (`asiGreen`) | POH, 1 Jul 1978 | 2-5 Fig 2-2 | Verified |
| Yellow arc 128–160 KIAS (`asiYellow`) | POH, 1 Jul 1978 | 2-5 Fig 2-2 | Verified |
| Max engine speed 2700 rpm (`maxRpm`) | POH, 1 Jul 1978 | 2-5 | Verified |
| Static RPM 2280–2400 (`staticRpm`) | POH, 1 Jul 1978 | 2-5 note | Verified (full throttle, carb heat off, full rich) |
| Tachometer green, sea level 2100–2450 (`tachGreenSL`) | POH, 1 Jul 1978 | 2-6 Fig 2-3 | Verified (SL row; 5000 ft 2100–2575, 10000 ft 2100–2700) |
| Oil temperature max 245 °F (`oilTempMaxF`) | POH, 1 Jul 1978 | 2-5 | Verified |
| Oil temperature green 100–245 °F (`oilTempGreen`) | POH, 1 Jul 1978 | 2-6 Fig 2-3 | Verified |
| Oil pressure min 25 psi (`oilPressMin`) | POH, 1 Jul 1978 | 2-5 | Verified |
| Oil pressure max 100 psi (`oilPressMax`) | POH, 1 Jul 1978 | 2-5 | Verified |
| Oil pressure green 60–90 psi (`oilPressGreen`) | POH, 1 Jul 1978 | 2-6 Fig 2-3 | Verified |
| Suction green 4.5–5.4 inHg (`suctionGreen`) | POH, 1 Jul 1978 | 2-6 Fig 2-3; 7-34 | Verified |
| Magneto check 1700 rpm (`magCheckRpm`) | POH, 1 Jul 1978 | 4-7, 4-13 | Verified |
| Magneto drop max 125 rpm (`magDropMax`) | POH, 1 Jul 1978 | 4-7, 4-13 | Verified at 1700 rpm |
| Magneto differential max 50 rpm (`magDiffMax`) | POH, 1 Jul 1978 | 4-7, 4-13 | Verified at 1700 rpm |
| Carb heat drop 100–225 rpm (`carbHeatFullThrottleDrop`) | POH, 1 Jul 1978 | 7-19 | Verified (full heat, full throttle) |
| Lean peak drop 25–50 rpm (`leanPeakDrop`) | POH, 1 Jul 1978 | 4-16 | Verified |
| Fuel 21.5 gal per tank (`fuelPerTankTotal`) | POH, 1 Jul 1978 | 1-4, 7-21 | Verified; comment corrected (the old `p.2-6` applies to the unusable marking) |
| Usable 20 gal per tank (`fuelPerTankUsable`) | POH, 1 Jul 1978 | 1-4, 7-21 | Verified |
| Unusable 1.5 gal per standard tank (`fuelUnusablePerTank`) | POH, 1 Jul 1978 | 2-6 Fig 2-3 | Verified |
| System 28 V (`systemVolts`) | POH, 1 Jul 1978 | 7-23, 7-25 | Verified |
| Battery 24 V (`batteryVolts`) | POH, 1 Jul 1978 | 7-23, 7-25 | Verified |
| Alternator 60 A (`alternatorAmps`) | POH, 1 Jul 1978 | 7-25 | Verified |
| Alternate-static table 40→39 … 140→141 (`ALT_STATIC_TABLE`) | POH, 1 Jul 1978 | 5-9 Fig 5-1 sheet 2 | Verified (flaps up; heater, vents and windows closed) |
| 2700 rpm in `equilibriumRpm` | POH, 1 Jul 1978 | 2-5 | Verified constant |
| Initial fuel 21.5 gal each side | POH, 1 Jul 1978 | 1-4, 7-21 | Verified |
| `P0_INHG` 29.92, `A0_KT`, ISA exponents | ICAO standard atmosphere | — | Standard, not POH |
| `ENGINE_MODEL.*` (propeller, mixture, single-magneto, carb-heat factors) | — | — | Illustrative; labelled not from the POH in code |
| 13 Ah battery; alternator output vs RPM; oil temperature and pressure models; gyro spin times; windmilling RPM | — | — | Illustrative |

## R01 — best glide

| Value | Source | Page | Status |
| --- | --- | --- | --- |
| Best glide 65 KIAS (`GLIDE.kias`) | POH, 1 Jul 1978 | 3-11 Fig 3-1; 3-3 table | Verified twice in the text layer |
| Maximum glide ratio 9.1 (`GLIDE.ratio`) | POH, 1 Jul 1978 | 3-11 Fig 3-1 | Verified against the repository's citation; the figure image was not re-read this cycle |
| Conditions: flaps up, propeller windmilling | POH, 1 Jul 1978 | 3-11 Fig 3-1 | Recorded in `GLIDE.conditions`; weight not recorded in the extract — Needs source |

The matching handbook is available (the 1979-model POH cited by the repository and its committed
extracts), so the value is documented with its conditions rather than nulled. The missing condition is
the figure's weight: it is not in the text layer or the extract, so it is not asserted.

## Findings and what changed

1. **VFE was incomplete.** `sim.js` carried only 85 KIAS, which is the printed 10–40° row. The handbook
   also prints 110 KIAS for the 10° row on the same page. Both rows are now evidence records; `POH.vfe`
   stays 85 (the conservative 10–40° value), and the gate withholds the 10° case as ambiguous instead of
   choosing. No published number changed.
2. **One page citation was split.** The 21.5/20 gal totals are on p.1-4 and p.7-21; p.2-6 carries the
   1.5 gal unusable marking. The `sim.js` comment now cites each page for what it contains.
3. **Every other POH-tagged scalar matches** the committed extract and the handbook page.
4. **Illustrative constants are now listed apart** so a reader does not mistake a modelling constant for
   a handbook limit.
5. **The values are wired through the gate.** `POH` in `sim.js` is built with `useValue()` from
   `shared/js/evidence.js`; a missing document, edition, page, model or condition stops the module rather
   than showing an uncited number. The six acceptance tests are in `test/evidence.test.mjs`.

## Open items (Needs source)

1. **VFE at exactly 10° flaps.** The page prints 110 KIAS (10° row) and 85 KIAS (10–40° row). The gate
   returns `ambiguous_conditions` at 10° until a human decides which row governs the detent. Owner: a POH
   review; source: p.2-4 Fig 2-1.
2. **Weight for the maximum-glide figure.** p.3-11 Fig 3-1 does not state its weight in the text layer or
   the committed extract. Owner: read the figure image; do not assume 2300 lb.
3. **Copy reviewed.** The committed extract is a public scan, not a serial-number-specific approved flight
   manual (`04b_poh_reference/poh_1979_reference_data.json`, `cautions`). A serial-specific AFM still
   governs any real aircraft.
