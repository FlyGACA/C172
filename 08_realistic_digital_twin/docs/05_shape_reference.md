# Shape reference — where the outline of the airframe comes from

The model has been corrected twice. The first Phase 8 model was built from three POH dimensions and
from proportions judged by eye, and it did not read as a Cessna 172. A first correction took the side
outline from one photograph. This second correction lays the model under the manufacturer's own
drawings, which settle what a single photograph could not: the stations of the doors and windows, the
plan view, and how the aircraft sits on its wheels.

**Status of the result: `estimated`.** The outline follows manufacturer drawings of the type, read at
handbook scale; it is not a survey of the FlyGACA aircraft and not a loft drawing. The dimensions that
the POH prints are reproduced exactly and are checked on every build (see [Checks](#checks)).

## Sources

| Source | Used for |
|---|---|
| POH of the Model 172N (1978 handbook), Figure 1-1 "Three View", p. 1-2 | every printed dimension: span 36 ft with strobe lights, length 26 ft 11 in, maximum height 8 ft 9½ in, tail span 11 ft 4 in, track 8 ft 4½ in, wheel base 65 in, propeller clearance 11¾ in, wing area 174 sq ft |
| Same handbook, Figure 6-4 "Internal Cabin Dimensions", p. 6-8 | sizes of the cabin and baggage door openings, cabin stations (rear doorpost bulkhead 65.3, aft cabin wall 108, end of the aft baggage area 142), widths inside the cabin |
| Handbook of the later Model 172S, Figure 1-1 "Three View — normal ground attitude" | the outline itself. The 172S keeps the 172N's fuselage aft of the firewall, its wing and its tail; its three-view is computer-drawn and sharp. Side view: stations and heights of everything, and the attitude on the wheels. Top view: planform of the wing and tail, widths of the fuselage. Front view: track, strut, cabin width only |
| Equipment list of the 172S handbook (arms in inches aft of the firewall) | stations: main wheels 57.8–58.2, nose wheel −6.8, propeller −38.2 (172S nose), door windows 48.5 |
| Type data | chords 64 in at the root and 44.5 in at the tip rib, dihedral 1° 44′, incidence +1.5° / −1.5°, leading edge of the mean chord at station 25.90 |
| Photograph of a 172 in flight, side-on ("photo-profile", first correction) | the nose of the 172N (cowl, chin, spinner), which differs from the 172S, and the wheel fairings |

The drawings are used for measurement only and are not part of this repository.

## Method

`blender/threeview.py` draws the built model from the side, from above and from ahead as line drawings
at a known scale (6 pixels per inch) and writes, for each picture, the pixel that corresponds to
station 0, the centreline and the ground. A handbook drawing is scaled by a dimension printed on it
and laid under that picture:

| Drawing | Scale from | Check |
|---|---|---|
| 172S side view | 27 ft 2 in overall length (0.2098 in per pixel) | wheel base measures 65.8 in (printed: 65.0) |
| 172S top and front view | 36 ft 1 in span (0.2587 in per pixel) | tail span 136.0 in (printed: 11 ft 4 in); track 100.5 in (172N POH: 8 ft 4½ in); root chord 63.6 in, tip rib chord 44.5 in (published: 64 and 44.5) |
| 172N three-view (hand-drawn, small) | 36 ft span | used for the printed dimensions and as a second opinion on the planform |

The model was then changed until its lines lay on the drawing's lines. After the correction they agree
to about an inch along the fuselage, the cabin openings, the wing and the tail; the remaining
differences are the parts that really differ between the two model years (cowl, spinner, wheel fairings).

## What the drawings showed

**The aircraft sits nose-up, and higher on its main gear.** The first correction levelled the model on
the wheels of an aircraft *in flight* and then moved the ground until the propeller cleared it by the
published 11¾ in. Both steps were wrong. In the 172S "normal ground attitude" the belly line of the
model fits only after the aircraft is turned 1.66° nose-up and raised 2.5 in at the main wheels; the
propeller then clears the ground by about 17 in, not 11¾.

The two published figures are not contradicted by this. The POH gives the maximum height "with nose
gear depressed", and the propeller clearance belongs to the same condition: if the model is pushed
nose-down about its main wheels until the propeller clears the ground by 11¾ in, the nose wheel has to
go down 3.6 in — a bottomed strut and a soft tyre — and the top of the beacon rises from 7 ft 10 in to
8 ft 8½ in, an inch below the published 8 ft 9½ in. `validate_geometry.py` and the unit tests keep
this relation.

**The doors and windows were 11–14 in too far forward.** A photograph taken 19° off the beam shows
the near side of the cabin displaced forward, and the first correction read stations from it. The door
now stands between the front door post (behind the wing strut) and the rear door post; the sill of
its window drops toward the rear; the baggage door is where the handbook has it.

**The windshield runs up to the wing.** There is no wing leading edge across the cabin: the
windshield ends at the roof just behind the leading edge, the cabin top between the wings belongs to
the fuselage, and each wing ends at the cabin side.

**The wing tapers on both edges.** Constant chord to BL 100, where the strut meets the wing; from
there 27 % of the taper is on the leading edge (5.2 in at the tip rib). The first correction had all
of it on the trailing edge. Aileron and flap: the fixed skin ends at 79 % chord over the flap, and the
aileron shows a constant 9.8 in of chord.

**The tailcone is slimmer in side view and the rudder wider.** The top of the tailcone falls to
WL 40.6 at the last frame, which carries the rudder at FS 231.5; the dorsal fin is correspondingly
taller. The rudder hinge line is raked 32°, so the rudder is 20 in wide at its foot and 8 in at the top.

| | Before (photo-profile) | Now | From |
|---|---|---|---|
| Attitude at rest | level on the build frame | 1.66° nose-up, 2.5 in higher at the main wheels | 172S side view |
| Propeller clearance at rest | 11¾ in | 16.9 in (11¾ in with the nose gear depressed) | 172S side view, POH Fig 1-1 |
| Track | 8 ft 3½ in | 8 ft 4½ in | POH Fig 1-1 |
| Span over the strobe lights | 36 ft 1 in | 36 ft | POH Fig 1-1 |
| Cabin door | FS 17.5–55 | FS 30.9–67.9 at the sill, 38.4–70.4 at the top | 172S side view, POH Fig 6-4 |
| Windshield foot / top | FS 3 / FS 25 under the wing | FS 10.3 / FS 33 at the roof | 172S side view |
| Rear window | to FS 128 | slopes from the wing trailing edge (FS 93.8) to FS 115.5 | 172S side view |
| Baggage door | none | left side, FS 92–110, 22 in high | POH Fig 6-4, 172S side view |
| Wing root leading edge | FS 24, chord line 67.5 in above the build ground | FS 30.0, WL 70.0 | 172S side view |
| Wing planform | all taper on the trailing edge, 41 in tip chord | 27 % on the leading edge, 44.5 in at the tip rib | 172S top view, type data |
| Wing strut | FS 20.5 → 44, to BL 96 | FS 28.2 → 38.2, to BL 100.5 | 172S side and front view |
| Fuselage width | 19.3 in at the firewall, 21.3 in at the doors | 20.3 in and 21.6 in; straight taper aft of FS 94 | 172S top view |
| Top of the tailcone at FS 200 | WL 48.5 | WL 44.6 | 172S side view |
| End of the fuselage | FS 247 | FS 231.5 | 172S side view |
| Rudder hinge line | 25° rake | 32° rake | 172S side view |
| Horizontal tail | chords 50 / 29.5 in | chords 49.5 / 27.6 in, hinge line straight across | 172S top view |
| Main gear leg | straight out from FS 57 | from the gear bulkhead (FS 65) forward to the wheel at FS 58 | 172S side and front view |
| Flap travel | 30° | 40° | POH (performance tables, p. 7-10) |

## Three frames of reference

The tables in `blender/c172` are written in the **build frame**: FS along the model, WL upward
(`units.py`). Two other frames matter, and both are tilted against it:

* **On the ground** the aircraft is 1.66° nose-up relative to the build frame (`GROUND_PITCH_DEG`).
  `build.py` turns the finished model into this attitude and puts the tyres on z = 0, so the saved
  scene and the exported models stand as the aircraft stands. `units.to_ground()` and
  `units.from_ground()` convert.
* **Handbook stations** follow the fuselage reference line, to which the published wing incidence
  refers. It is pitched about 3° nose-down in the build frame (`FRL_PITCH_DEG`): the door posts and
  the firewall, upright in the handbook's cabin drawing, lean back by that much here, and the wing
  root sits at 4.5° in the build frame. `units.cessna_fs()` converts a handbook station at a given
  height. This angle is the least certain number in this note: the wing-root line of the side view
  gives 3.0°, the wheels of the front view 1.7°. The 1978 POH marks 5° between the level reference
  and the ground line on its side view; the model has 4.7° (1.66° + 3.0°).
* **The seats** stand at the stations of the handbook's loading figure (Figure 6-3, p.6-7): the centre of
  gravity of the pilot and the front passenger at station 37 with the seat set for an average occupant
  (the rails allow 34 to 46), that of the rear passengers at station 73, and baggage area 1 behind the
  rear seat back, from station 82. Where an occupant's centre of gravity lies on a seat is an estimate
  (about 6 in ahead of the seat back), so the seats may be an inch or two out.

## What is still uncertain

* The nose of the 172N. Cowl, chin and spinner come from the photo-profile; the 172S drawing cannot
  check them.
* Cross-sections. A three-view gives widths and heights, not the shape between them. The front view of
  the 172S drawing is not consistent with its side view in height (it places the wing about 8 in
  lower), so only widths were taken from it; the height of the cabin agrees with POH Fig 6-4 (48 in
  inside at the front seats).
* The wheel fairings, and everything that changed between model years.
* The engine thrust line is level in the build frame; the drawing suggests it lies along the
  fuselage reference line (3° lower at the firewall end).

## Checks

`blender/validate_geometry.py` (run in CI on the rebuilt model) measures the built scene and fails if
any of these differs from the published figure:

| Dimension | Published | Tolerance |
|---|---|---|
| Wing span over the strobe lights | 36 ft (POH Fig 1-1) | 2 cm |
| Wing span over the tips | 35 ft 10 in (type data) | 2 cm |
| Length, spinner tip to rudder, on the wheels | 26 ft 11 in | 3 cm |
| Wheel base | 65 in | 1 cm |
| Track | 8 ft 4½ in | 1 cm |
| Span of the horizontal tail | 11 ft 4 in | 2 cm |
| Height with the nose pushed down to 11¾ in of propeller clearance | 8 ft 9½ in | 3 cm |
| Tyres | on the ground (z = 0) | — |

It also checks that struts, fairings, doors, gear, fin, stabiliser, wings and cowl meet their
neighbours, and that no part of the engine, the panel or the cabin interior sticks out through the
skin (255 parts are tested against the sections the skin is built from).

## How to replace this with measurements

Everything above is a stand-in for a survey of the real aircraft. The measurement workflow in
[04_aircraft_measurements.md](04_aircraft_measurements.md) already carries verified records into the
model with their provenance. The readings that would improve the shape most, in order:

1. cabin width at the door sill, at the window sill and at the roof, at the front and rear door posts;
2. cowl width and depth at the firewall and at the nose cap, and the length of the spinner;
3. a square-on side photograph and a head-on photograph of the aircraft itself, taken from at
   least 30 m with a long lens, with a levelled reference of known length in the frame;
4. the height of the propeller hub and of the top of the fin above the ramp, with the aircraft at rest;
5. the stations of the strut fittings, the main gear legs and the door posts.
