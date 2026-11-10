# Shape reference — where the outline of the airframe comes from

The first Phase 8 model was built from the POH three-view dimensions (span, length, height) and
from proportions judged by eye. It had the right span and length, but it did not read as a
Cessna 172: it stood far too high on its landing gear, the tail was too far aft and the wrong
shape, the windows were too tall and the nose was short. This note records how the outline was
corrected, what it was corrected against, and how far that reference can be trusted.

**Status of the result: `estimated`.** The outline now follows a real Cessna 172, but it was taken
from photographs of *a* 172, not surveyed on the FlyGACA aircraft and not copied from manufacturer
drawings. Dimensions that the POH or the type data publish are reproduced exactly and are checked
on every build (see [Checks](#checks)).

## Method: a side elevation from one photograph ("photo-profile")

A photograph taken almost exactly from the side, from far away, is close to a side elevation.
The reference is a Cessna 172 photographed in flight against a sunset, which gives a clean
silhouette (photograph by Marko Pavlichenko on Unsplash, photo `Zy7hXqw2he8`). The photograph is
used for measurement only and is not part of this repository.

1. **Viewing direction.** Fitting the model to the silhouette puts the camera 19° aft of the
   right beam and 4.5° below the aircraft. Lengths along the fuselage are therefore foreshortened
   by cos 19° (5 %), which the scale below absorbs.
2. **Scale.** The overall length in the photograph is set to the POH length, 26 ft 11 in (323 in).
   That gives 8.30 px/in along the fuselage and 8.83 px/in vertically.
3. **Cross-checks.** With that scale the wheel base measures 65.9 in (published: 65 in) and the
   tyres 17.0 in and 13.5 in (6.00-6 and 5.00-5). The scale was not adjusted to make them fit.
4. **Level.** Water lines are measured from the static ground line. In flight the wheels hang
   lower than at rest, so the line under the wheels was raised by 2.8 in — the amount that
   reproduces the published 11¾ in propeller ground clearance.
5. **Readings.** The outline was read at stations along the fuselage (FS, inches aft of the
   firewall) as water lines (WL, inches above the ground). Reading accuracy is about ±0.5 in,
   and ±1 in where the outline is soft (blurred propeller, wing root).

| Line | Readings (FS → WL, inches) |
|---|---|
| Propeller axis | WL 49.25; spinner tip at FS −44.5 |
| Top of the cowl | −33.5 → 51.8, −30 → 53.5, −20 → 55.8, −10 → 57.0, 0 → 57.8 |
| Underside of the cowl | −33 → 42.8, −30 → 37, −27 → 32, −23 → 27, −19 → 23.8, −10 → 21.2, 0 → 19.8 |
| Belly | 10 → 19, 20 → 18, 30 → 17.2, 40–50 → 16.7, 80 → 18.2, 100 → 19.2, 133 → 21.5, 150 → 22.2, 185 → 24.8, 200 → 26, 220 → 27.2, 240 → 29.5, 250 → 32 |
| Top of the tailcone and dorsal fin | 129 → 52.2, 150 → 53.2, 165 → 54.8, 180 → 55.7, 190 → 56.4, 200 → 57.2, 210 → 59, 215 → 61 |
| Fin leading edge (45° sweep) | 220 → 64.3, 230 → 73.8, 240 → 83.5, 251 → 95 |
| Fin top | 254 → 96.5, falling to the rear corner at WL 92.3 |
| Rudder trailing edge | from the rear top corner to FS 258.5 at WL 43.5 (23° rake), then vertical to WL 35 |
| Horizontal tail | chord plane at WL 37; elevator tip trailing edge near FS 245 |
| Side windows | sill WL 48–49.5, top WL 59.5–61.5; front door post about 47° from the horizontal |

The rear top corner of the rudder is placed at FS 278.5 so that spinner tip to rudder is exactly the
POH length; the reading (279.2) agrees within its accuracy.

### What the side view cannot give

Widths and cross-sections are not visible in a side elevation. They come from three other
photographs, read by eye, and are the least certain part of the shape:

- a 1970s Cessna 172 on a ramp, seen from low at the front right (Chris Leipelt, `7lLa10H0oY8`):
  nose cap with a cooling inlet either side of the spinner, a single round landing light on the
  centreline below it and the rectangular carburettor air inlet below that; the windshield
  wrapping round to a thin door post, with the cabin air inlets in the wing-root leading edges;
  wheel fairings; exhaust tailpipe under the right side of the cowl;
- a Cessna 172 from directly below on final approach (Cody F, `O0Tr0mrzXLA`): straight wing
  leading edge with the taper in the trailing edge of the outer panel; flat belly with tight
  lower corners; plan of the horizontal tail; straight taper of the tailcone;
- a later Cessna 172 head-on (Mark Ulm / ALPEN AIR, `ze18FDQru4Y`), used only for the general
  proportion of cabin width to height.

Two more caveats. The viewing direction is 19° off the beam, so parts far from the centreline are
displaced in the photograph: a point one metre nearer the camera appears 13 in further forward.
Stations of such parts cannot be read off the photograph. The wing strut was placed the other way
round, by rendering the model from the direction of the photograph until its strut covered the
strut in the photograph: foot at FS 20.5 on the fuselage frame under the lower front corner of the
door, upper end at FS 44, about 30 % of the chord. And the reference aircraft are not the 1979
model: details that changed between model years (nose cap, lights, fairings) follow the ramp
photograph and the POH text, not the silhouette.

## What changed in the model

| | First Phase 8 model | Now | From |
|---|---|---|---|
| Propeller ground clearance | 17.6 in | 11¾ in | published three-view note |
| Belly above the ground at FS 45 | 31.5 in | 16.7 in | photo-profile |
| Top of the cowl at the firewall | 68.5 in | 57.8 in | photo-profile |
| Wing chord line above the ground | 82.3 in | 67.5 in | photo-profile |
| Spinner tip | FS −40 | FS −44.5 | photo-profile |
| Tailcone | to FS 283, straight | ends at the rudder post, FS 247 | photo-profile |
| Fin and rudder | top at the POH maximum height (105.5 in), vertical rudder trailing edge, no distinct dorsal fin | 45° swept fin on a long dorsal fin, raked rudder, top 96.5 in above the ground at rest | photo-profile |
| Horizontal tail | trailing edge at FS 282 | trailing edge at FS 253, 29 in further forward | photo-profile |
| Side windows | about 22 in tall | 13 in tall, sill at propeller-axis height | photo-profile |
| Windshield | cut into the top of the cabin only | wraps round the sides to the door posts | ramp photograph |
| Cabin section | oval | slab sides, flat belly, tight lower corners | photograph from below |
| Wheel fairings | half domes | teardrop shells open underneath | ramp photograph |
| Landing light | rectangular, off centre | single round lamp on the centreline of the nose cap | POH p. 7-27, ramp photograph |
| Wing struts | foot at FS 22 where the door now is | foot on the fuselage frame under the corner of the door (FS 20.5), top at FS 44 | photo-profile |

Two things in the build were also wrong independently of the reference. Section tables were
interpolated with an ease-in/ease-out curve, which flattens the outline at every row and gave the
tailcone and the fin a series of small kinks; they are now interpolated with a shape-preserving
cubic (`profiles.interp_pchip`). And the fuselage skin was smoothed as a closed body, which
rounded off its front end and opened a gap behind the cowl; both ends are now kept square.

## Fit

The model is rendered as a silhouette from the direction of the photograph (orthographic) and
laid over the photograph's silhouette; the score is the area both share divided by the area
either covers. Wheel fairings and propeller are left out, as on the reference aircraft, and the
two patches where the blurred propeller was removed from the photograph are not counted.

| | Overlap |
|---|---|
| First Phase 8 model | 0.78 |
| Corrected model | 0.90 |

The fuselage, cowl and tail outlines now coincide to within about an inch. What remains is the
difference between an aircraft in flight and one at rest: the wings are bent upward and the
wheels hang lower in the photograph.

## Checks

`blender/validate_geometry.py` (run in CI on the rebuilt model) now measures the built scene and
fails if any of these differs from the published figure:

| Dimension | Published | Tolerance |
|---|---|---|
| Wing span over the tips, lights excluded | 35 ft 10 in | 2 cm |
| Length, spinner tip to rudder | 26 ft 11 in (POH Fig 1-1) | 3 cm |
| Wheel base | 65 in | 1 cm |
| Track | 8 ft 3½ in | 1 cm |
| Propeller ground clearance | 11¾ in | 1.5 cm |
| Span of the horizontal tail | 11 ft 4 in | 2 cm |
| Tyres | on the ground (z = 0) | — |

It also checks that struts, fairings, gear, fin, stabiliser and cowl meet their neighbours, and
that no part of the engine, the panel or the cabin interior sticks out through the skin (253
parts are tested against the sections the skin is built from).

Three notes on these figures. The POH gives the height as a maximum, with the nose gear
depressed; at rest the top of the beacon is 96.5 in above the ground in the photo-profile, which
is what the model reproduces. Wheel base and propeller clearance are quoted from published
three-views and are marked `type_data` in `units.py` until they are confirmed against Figure 1-1
of the aircraft's own POH. And the repository's own data disagree about the span: `units.py`
carries 35 ft 10 in, `data/poh_references.json` records 36 ft from Figure 1-1. The model measures
35 ft 10 in over the wing tips and 36 ft 1 in over the navigation lights, so the two may be the
span without and with the tip lights; this needs a look at the figure itself.

## How to replace this with measurements

Everything above is a stand-in for a survey of the real aircraft. The measurement workflow in
[04_aircraft_measurements.md](04_aircraft_measurements.md) already carries verified records into
the model with their provenance. The readings that would improve the shape most, in order:

1. cabin width at the door sill, at the window sill and at the roof, at the front and rear door posts;
2. cowl width and depth at the firewall and at the nose cap;
3. a square-on side photograph and a head-on photograph of the aircraft itself, taken from at
   least 30 m with a long lens, with a levelled reference of known length in the frame;
4. the stations of the strut fittings, the main gear legs and the door posts.
