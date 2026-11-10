# Flight model

The viewer can fly the aircraft. A small flight model moves it, its control surfaces and its instruments;
its numbers come from the Pilot's Operating Handbook (Cessna Model 172N, 1978) wherever the handbook has
them, and every number says where it comes from.

**What it is.** Rigid-body equations of motion in six degrees of freedom with a coefficient model of the
wing, the tail, the propeller and the landing gear: about 600 lines of JavaScript in `shared/js/flight.js`,
written to be read.

**What it is not.** It has no certified fidelity. It reproduces the handbook's published performance within
the tolerances stated below, and behaves plausibly between those points. It does not model spins, icing,
turbulence, structural limits or damage. **It must not be used to plan or judge a real flight.**

## Flying it

Open the viewer and choose **Flight**. The aircraft stands on a runway with the engine running and the
parking brake set. Release the brake (P), open the throttle (Page Up) and raise the nose at about 55 KIAS.

| Control | Keys | On a touch screen |
|---|---|---|
| Wheel (ailerons, elevator) | arrows; the down arrow pulls the wheel back | the square at the lower right |
| Rudder | Z, X | — (the assistant) |
| Throttle | Page Up, Page Down | PWR + / PWR − |
| Flaps | F (down), V (up) | FLAP ▼ / FLAP ▲ |
| Trim | ] (nose up), [ (nose down) | TRIM ▲ / TRIM ▼ |
| Brakes | B or space; P sets the parking brake | BRAKES |
| Camera | C: outside or the pilot's eye | Camera |

- **Begin** on the runway, in cruise (3000 ft, 100 KIAS) or on approach (600 ft, 70 KIAS, flaps 20°, 1¼ NM out).
- **Assistance.** *Rudder* keeps the aircraft straight on the ground, keeps the nose into the wind in the air
  and holds what the propeller asks of hand and foot. Switch it off to see the left-turning tendency: the nose
  swings left and the left wing drops when power is added at low speed. *Wings level* holds the wings level
  when the wheel is let go.
- **Conditions.** Weight (1600 to 2300 lb), centre of gravity between its limits, wind and temperature are
  applied when a flight begins.
- Mixture, carburetor heat, magnetos, fuel selector, electrics and the fault panel act as in the systems
  simulation: an engine that stops no longer pulls.
- A touchdown at more than 900 ft/min, or in an attitude the landing gear cannot take, ends the flight.

The table of numbers is in the viewer too: **Flight → The numbers of the model and their sources**.

## How it is built

- **Lift.** A straight lift curve that bends over during the last 3° and falls after the stall. Its top is the
  maximum lift coefficient the handbook's stall speeds give, for each flap setting and each end of the centre
  of gravity range.
- **Drag.** A parabolic polar; flap drag; a rise close to and beyond the stall; less induced drag near the
  ground; the drag of a windmilling or stopped propeller when the engine is not running.
- **Pitch.** Stability from the distance between the centre of gravity and the neutral point; damping; an
  elevator that loses effect at large angles, in the wake of the wing and gains it in the slipstream; trim that
  moves where the elevator floats; a nose-up moment with power; the moment of the flaps; and the break of the
  stall: a stalled wing sends less downwash to the tail, so the nose drops even with the wheel held back.
- **Roll and yaw.** Dihedral effect, weathercock stability, damping, adverse yaw, the roll of the propeller
  torque and the yaw of its slipstream. The airframe is rigged to fly straight hands off at 100 KCAS in
  level flight; at other speeds and powers it asks for a little aileron and rudder, as an aircraft does.
- **Propeller and engine.** Power and thrust coefficients of the fixed-pitch propeller against advance ratio.
  The engine speed is where the propeller absorbs what the engine gives; full-throttle torque follows the
  pressure and the temperature of the air; a throttled engine gives a power that does not depend on its speed.
- **Landing gear.** Three wheels on springs and dampers with rolling, braking and side friction; the nose
  wheel steers with the pedals.
- **Integration.** Semi-implicit Euler at 120 steps a second, attitude as a quaternion; steady wind.

## Where the numbers come from

Each entry of `FM` in `flight.js` carries a value, a source, a note and, unless it is an estimate, a handbook
page. The sources are:

| Source | Meaning |
|---|---|
| **POH** | read from the handbook |
| **POH-derived** | worked out from handbook numbers by the rule stated in the note |
| **estimated** | a representative value for an aircraft of this type; not from the handbook, not measured |

The derivations, in the order they depend on each other:

1. **Maximum lift coefficients** from the stall speeds of Figure 5-3 at 2300 lb.
2. **Propeller power coefficient**: standing still from the static RPM (p.2-5), in flight from the RPM, power
   and speed of the cruise table (Figure 5-7).
3. **Drag polar** from two lines of the cruise table, assuming a propeller efficiency of 0.78 in cruise. That
   efficiency is an estimate, and the parasite drag and the induced drag factor depend on it.
4. **Propeller thrust coefficient** from the takeoff ground roll (Figure 5-4), the rate of climb at sea level
   (Figure 5-6) and the cruise efficiency assumed above.
5. **Engine torque with altitude and temperature** from the rate of climb table (Figures 5-5 and 5-6).
6. **Windmilling propeller drag** from the maximum glide (Figure 3-1).
7. **Braking friction** from the landing ground roll (Figure 5-10).

Stability and control numbers (how quickly it rolls, how much rudder the climb needs, how the trim speed
changes with flaps and power) are estimates: the handbook does not publish them. They were chosen so that
the behaviour the handbook describes in words is there: the stall warning 5 to 10 knots before the stall,
conventional stall characteristics, the pitch-up of a go-around with full flaps.

## The model against the handbook

Computed by `scripts/flight_doc.mjs` from the code; `tests/flight.test.mjs` fails if a figure leaves its
tolerance. The takeoffs, landings and stalls are flown by the scripted pilot (`shared/js/pilot.js`) with the
handbook's technique.

<!-- validation:begin (generated by scripts/flight_doc.mjs) -->
### Stall speeds, power off, 2300 lb (p.5-11 Fig 5-3)

| Flaps | Centre of gravity | Handbook KCAS | Model KCAS |
|---|---|---|---|
| 0° | most rearward | 50 | 50.0 |
| 10° | most rearward | 47 | 47.0 |
| 40° | most rearward | 44 | 44.0 |
| 0° | most forward | 53 | 53.0 |
| 10° | most forward | 51 | 51.0 |
| 40° | most forward | 47 | 47.0 |

Flown by the scripted pilot (throttle closed, altitude held, centre of gravity in the middle): flaps 0°: horn at 57.4 KCAS, stall at 49.7 KCAS (0.93 g), recovery lost 88 ft; flaps 40°: horn at 50.5 KCAS, stall at 43.8 KCAS (0.94 g), recovery lost 86 ft. The handbook: horn 5 to 10 knots before the stall (p.7-34); a recovery may lose as much as 180 ft.

### Static RPM (p.2-5)

Handbook: 2280 to 2400 RPM at full throttle. Model: 2340 RPM, with 540 lb of thrust.

### Rate of climb, flaps up, full throttle, standard temperature (p.5-15 Fig 5-6)

| Altitude ft | Climb KIAS | Handbook ft/min | Model ft/min | Difference |
|---|---|---|---|---|
| 0 | 73 | 770 | 781 | +11 |
| 1000 | 73 | 725 | 730 | +5 |
| 2000 | 72 | 675 | 678 | +3 |
| 3000 | 72 | 630 | 628 | −2 |
| 4000 | 71 | 580 | 578 | −2 |
| 5000 | 71 | 535 | 530 | −5 |
| 6000 | 70 | 485 | 482 | −3 |
| 7000 | 69 | 440 | 436 | −4 |
| 8000 | 69 | 390 | 390 | 0 |
| 9000 | 68 | 345 | 346 | +1 |
| 10000 | 68 | 295 | 302 | +7 |
| 11000 | 67 | 250 | 259 | +9 |
| 12000 | 67 | 200 | 216 | +16 |

At −20, 0, 20 and 40 °C (p.5-14 Fig 5-5, 25 values from sea level to 12,000 ft): the largest difference is 38 ft/min.

### Cruise, standard temperature (p.5-16 Fig 5-7)

| Altitude ft | Lines within full throttle | Largest difference | Fastest handbook line | Model at full throttle |
|---|---|---|---|---|
| 2000 | 5 of 5 | 0.5 kt, 0.3 points of power | 116 KTAS at 2500 RPM, 75 % | within reach |
| 4000 | 6 of 6 | 0.6 kt, 0.7 points of power | 118 KTAS at 2550 RPM, 75 % | within reach |
| 6000 | 6 of 6 | 1.0 kt, 0.7 points of power | 120 KTAS at 2600 RPM, 75 % | within reach |
| 8000 | 4 of 6 | 0.8 kt, 0.6 points of power | 122 KTAS at 2650 RPM, 75 % | 118 KTAS at 2580 RPM, 70 % |
| 10000 | 4 of 6 | 1.5 kt, 0.5 points of power | 122 KTAS at 2650 RPM, 71 % | 115 KTAS at 2530 RPM, 63 % |
| 12000 | 3 of 5 | 2.7 kt, 1.3 points of power | 118 KTAS at 2600 RPM, 64 % | 111 KTAS at 2480 RPM, 57 % |

### Maximum glide (p.3-11 Fig 3-1)

Handbook: about 9.1 to 1 at 65 KIAS, propeller windmilling. Model: 9.10 to 1, sinking 799 ft/min.

### Short-field takeoff (p.5-12, 5-13 Fig 5-4)

| Field ft | °C | Weight lb | Handbook ground roll / over 50 ft | Model | Difference |
|---|---|---|---|---|---|
| 0 | 0 | 2300 | 720 / 1300 ft | 714 / 1392 ft | −1 % / +7 % |
| 0 | 20 | 2300 | 835 / 1490 ft | 802 / 1553 ft | −4 % / +4 % |
| 0 | 40 | 2300 | 960 / 1700 ft | 895 / 1725 ft | −7 % / +1 % |
| 2000 | 20 | 2300 | 1000 / 1790 ft | 966 / 1863 ft | −3 % / +4 % |
| 4000 | 20 | 2300 | 1210 / 2175 ft | 1169 / 2266 ft | −3 % / +4 % |
| 8000 | 20 | 2300 | 1805 / 3375 ft | 2040 / 3576 ft | +13 % / +6 % |
| 0 | 20 | 2100 | 680 / 1220 ft | 690 / 1290 ft | +1 % / +6 % |
| 0 | 20 | 1900 | 540 / 985 ft | 574 / 1093 ft | +6 % / +11 % |

### Short-field landing (p.5-21 Fig 5-10)

| Field ft | °C | Handbook ground roll / over 50 ft | Model | Difference |
|---|---|---|---|---|
| 0 | 0 | 495 / 1205 ft | 491 / 1263 ft | −1 % / +5 % |
| 0 | 20 | 530 / 1265 ft | 526 / 1318 ft | −1 % / +4 % |
| 0 | 40 | 565 / 1330 ft | 560 / 1372 ft | −1 % / +3 % |
| 4000 | 20 | 615 / 1410 ft | 604 / 1441 ft | −2 % / +2 % |
| 8000 | 20 | 710 / 1580 ft | 698 / 1589 ft | −2 % / +1 % |
<!-- validation:end -->

### Tolerances the tests hold

| Figure | Tolerance |
|---|---|
| Stall speeds, every flap setting, centre of gravity limit and bank angle of Figure 5-3 | 1 KCAS |
| Static RPM | inside the handbook's range |
| Rate of climb, standard temperature, sea level to 12,000 ft | 25 ft/min |
| Rate of climb at −20, 0, 20 and 40 °C | 45 ft/min |
| Cruise, every line full throttle reaches | 3 KTAS, 2.5 points of power |
| Maximum glide | 0.1 |
| Takeoff at sea level, 2300 lb | ground roll 8 %, over 50 ft 9 % |
| Takeoff to 8000 ft, and at 2100 and 1900 lb | 14 % |
| Landing, sea level to 8000 ft | ground roll 5 %, over 50 ft 7 % |
| Stall warning | 5 to 10 knots before the stall |
| Recovery from a stall | less than the handbook's 180 ft |

## Where it departs from the handbook

- **Cruise at and above 8000 ft.** The handbook's rate of climb table and its cruise table do not agree on
  the power the engine has left at altitude. The model is fitted to the climb table, so its full throttle is
  4 to 7 knots short of the fastest cruise lines at 8000 to 12,000 ft. Every other cruise line is within 3 knots.
- **Takeoff at 8000 ft** is about 13 % longer on the ground than the handbook's figure, and at 1900 lb about
  11 % longer over 50 ft.
- **A closed throttle** leaves almost no thrust and no drag from the propeller, so a glide at idle is
  better than the handbook's glide with the propeller windmilling on a stopped engine.
- **Stability and control** are estimates (see above), and so is everything beyond the stall. The model
  shows a stall and its recovery; it does not show a spin, which the handbook forbids in the normal category.
- **Not modelled:** ground effect on lift, turbulence and gusts, icing of the airframe, structural limits,
  tyre and brake wear, a tail or wing tip touching the ground, the alternate static source's effect on the
  altimeter. The airspeed indicator shows the indicated airspeed of the handbook's calibration table
  (Figure 5-1).

## With the systems simulation

`shared/js/flightdeck.js` flies the flight model and the systems simulation of Phase 7 together. The engine
of the systems simulation, with its mixture, magnetos, carburetor ice and fuel supply, turns the propeller of
the flight model; the motion of the flight model is what the instruments indicate, through the pitot-static
lines, the vacuum gyros and the electrical system with their faults. Scenarios that do not fly are unchanged.

## Files and tests

| File | What it is |
|---|---|
| `shared/js/flight.js` | the flight model and its numbers (`FM`) |
| `shared/js/flight_notes_ar.js` | the notes of the numbers in Arabic |
| `shared/js/poh_tables.js` | the handbook's performance figures, as numbers with their pages |
| `shared/js/pilot.js` | the scripted pilot; the handbook's takeoff, landing and stall as procedures |
| `shared/js/flightdeck.js` | the flight model with the systems simulation |
| `js/flightmode.js` | the flight mode of the viewer: world, camera, keys, on-screen wheel |
| `tests/flight.test.mjs` | the model against the handbook (`npm test`) |
| `tests/e2e.mjs` | the flight mode in a browser (`npm run test:e2e8`) |
| `scripts/flight_doc.mjs` | writes the generated tables of this document (`npm run flight:doc`) |

## Every number and its source

<!-- coefficients:begin (generated by scripts/flight_doc.mjs) -->
83 numbers: 12 read from the handbook, 16 derived from handbook numbers, 55 estimated. Values are in SI units unless the note says otherwise.

| Number | Value | Source | What it is, and the rule | POH page |
|---|---|---|---|---|
| `wingArea` | 16.165 | POH-derived | maximum weight 2300 lb divided by the wing loading 13.2 lb/sq ft = 174 sq ft | p.1-5 |
| `wingSpan` | 10.973 | POH | wing span 36 ft (with strobe lights) | p.1-2 Fig 1-1 |
| `propDiameter` | 1.905 | POH | propeller diameter 75 in (maximum) | p.1-3, 2-5 |
| `ratedPower` | 119310 | POH | 160 BHP at 2700 RPM | p.1-3, 2-5 |
| `ratedRpm` | 2700 | POH | maximum engine speed 2700 RPM | p.2-5 |
| `maxWeightLb` | 2300 | POH | maximum takeoff and landing weight, normal category | p.1-5, 2-6 |
| `wheelBase` | 1.651 | POH | wheel base 65 in | p.1-2 Fig 1-1 |
| `wheelTrack` | 2.5527 | POH | main wheel track 8 ft 4½ in | p.1-2 Fig 1-1 |
| `Ixx` | 1285.3 | estimated | roll inertia at maximum weight; a textbook value for the type |  |
| `Iyy` | 1824.9 | estimated | pitch inertia at maximum weight; a textbook value for the type |  |
| `Izz` | 2666.9 | estimated | yaw inertia at maximum weight; a textbook value for the type |  |
| `cgHeight` | 1.15 | estimated | height of the centre of gravity above the ground at rest (m) |  |
| `wingAboveCg` | 1.1 | estimated | height of the wing above the centre of gravity (m): for the ground effect |  |
| `groundPitchDeg` | 4.7 | POH-derived | attitude of the fuselage reference line at rest, from the three-view | p.1-2 Fig 1-1 |
| `mainGearStation` | 58 | estimated | fuselage station of the main wheel axle (in), from the three-view |  |
| `cgStationFwd` | 38.5 | POH | forward centre of gravity limit at 2300 lb: 38.5 in aft of datum | p.2-7, p.6-12 Fig 6-8 |
| `cgStationFwdLight` | 35 | POH | forward centre of gravity limit at 1950 lb or less: 35.0 in aft of datum, with a straight line to the limit at 2300 lb | p.2-7, p.6-12 Fig 6-8 |
| `cgStationAft` | 47.3 | POH | aft centre of gravity limit at all weights: 47.3 in aft of datum | p.2-7, p.6-12 Fig 6-8 |
| `macLeadingEdge` | 25.9 | estimated | station of the leading edge of the mean aerodynamic chord (in); a value for the type |  |
| `CLalpha` | 4.6 | estimated | lift curve slope per radian, from the aspect ratio 7.4 |  |
| `CL0` | 0.2 | estimated | lift coefficient with the fuselage reference line along the flight path, flaps up |  |
| `flapAngles` | 0, 10, 20, 30, 40 | POH | flap settings 0 to 40 degrees | p.7-10 |
| `dCL0Flap` | 0, 0.25, 0.45, 0.6, 0.7 | estimated | lift added by the flaps at a given angle of attack |  |
| `CLmaxAft` | 1.562, 1.768, 1.851, 1.934, 2.017 | POH-derived | from the stall speeds 50, 47 and 44 KCAS at 2300 lb, most rearward centre of gravity, flaps up, 10 and 40 degrees; 20 and 30 degrees interpolated | p.5-11 Fig 5-3 |
| `CLmaxFwd` | 1.39, 1.501, 1.59, 1.679, 1.768 | POH-derived | from the stall speeds 53, 51 and 47 KCAS at 2300 lb, most forward centre of gravity; 20 and 30 degrees interpolated | p.5-11 Fig 5-3 |
| `stallWarningMargin` | 0.8 | POH-derived | the stall warning horn sounds 5 to 10 knots above the stall: at about 0.80 of the maximum lift coefficient | p.7-34 |
| `stallBreakDeg` | 3 | estimated | the lift curve bends over this many degrees before the stall |  |
| `CD0` | 0.0303 | POH-derived | with the induced drag factor: from two lines of the cruise table at 8000 ft (75 % and 47 % power), taking the propeller efficiency as 0.78 | p.5-16 Fig 5-7 |
| `K` | 0.0536 | POH-derived | induced drag factor (Oswald efficiency 0.80), from the same two lines | p.5-16 Fig 5-7 |
| `CDnearStall` | 1 | estimated | extra drag close to the stall: above 0.8 of the maximum lift coefficient, per square of the excess fraction |  |
| `propEfficiencyCruise` | 0.78 | estimated | propeller efficiency in cruise, the assumption behind CD0 and K |  |
| `dCDFlap` | 0, 0.01, 0.026, 0.044, 0.062 | estimated | drag added by the flaps |  |
| `CDwindmill` | 0.0251 | POH-derived | drag of the windmilling propeller: what the drag polar lacks to give the maximum glide of 9.1 to 1 at 65 KIAS | p.3-11 Fig 3-1 |
| `CDstopped` | 0.008 | estimated | drag of a stopped propeller |  |
| `kStallDrag` | 6 | estimated | drag rise beyond the stall, per radian squared |  |
| `neutralPoint` | 0.46 | estimated | neutral point as a fraction of the mean aerodynamic chord |  |
| `Cm0` | 0.03 | estimated | pitching moment at zero angle of attack: sets the trim speed with the elevator and trim neutral |  |
| `Cmq` | -14 | estimated | pitch damping |  |
| `Cmde` | -1.28 | estimated | elevator power per radian, before the two factors below |  |
| `tailWake` | 0.8 | estimated | what is left of the elevator and rudder power in the wake of the wing and fuselage, propeller windmilling |  |
| `kSlipstream` | 1.5 | estimated | gain of elevator and rudder power in the slipstream, per unit of thrust coefficient |  |
| `elevatorUpDeg` | 28 | estimated | elevator travel up; a value for the type |  |
| `elevatorDownDeg` | 23 | estimated | elevator travel down; a value for the type |  |
| `elevatorSaturationDeg` | 21 | estimated | the elevator loses effect at large angles: full travel up is worth about 18 degrees |  |
| `trimAuthorityDeg` | 10 | estimated | what full trim is worth in degrees of elevator |  |
| `dCmFlap` | 0, -0.028, -0.049, -0.062, -0.069 | estimated | pitching moment of the flaps at the middle of the centre of gravity range: with the lift they add, lowering them at a fixed trim and throttle slows the aircraft from 80 KIAS to about 73, 68, 64 and 61 KIAS |  |
| `kCmThrust` | 0.3 | estimated | nose-up moment with power, per unit of thrust coefficient |  |
| `kDownwash` | 0.18 | estimated | nose-down break of the stall: a stalled wing sends less downwash to the tail; per unit of lift coefficient lost |  |
| `CYbeta` | -0.31 | estimated | side force due to sideslip |  |
| `Clbeta` | -0.105 | estimated | dihedral effect |  |
| `Clp` | -0.47 | estimated | roll damping |  |
| `Clr0` | 0.03 | estimated | roll due to yaw rate at zero lift |  |
| `ClrCL` | 0.12 | estimated | roll due to yaw rate, per unit lift coefficient: with the dihedral effect it leaves the aircraft slow to leave level flight in cruise and slowly spiralling at low speed |  |
| `ClAileron` | 0.054 | estimated | rolling moment of full aileron |  |
| `CnAileron0` | -0.001 | estimated | adverse yaw of full aileron at zero lift |  |
| `CnAileronCL` | -0.002 | estimated | adverse yaw of full aileron, per unit lift coefficient |  |
| `Cnbeta` | 0.065 | estimated | weathercock stability |  |
| `Cnr` | -0.099 | estimated | yaw damping |  |
| `CnpCL` | -0.1 | estimated | yaw due to roll rate (adverse), per unit lift coefficient |  |
| `CnRudder` | 0.0215 | estimated | yawing moment of full rudder, before the wake and slipstream factors |  |
| `CYRudder` | -0.052 | estimated | side force of full rudder |  |
| `ClRudder` | -0.004 | estimated | rolling moment of full rudder |  |
| `kCnThrust` | -0.035 | estimated | left-turning tendency with power and low airspeed, per unit of thrust coefficient |  |
| `tailArm` | 0.4 | estimated | distance of the fin behind the centre of gravity as a fraction of the wing span |  |
| `slipstreamShare` | 0.5 | estimated | share of the left-turning tendency that is a side force of the slipstream on the fin; the rest is the propeller disc itself |  |
| `rigKcas` | 100 | estimated | the airframe is rigged to fly straight, hands off, in level flight at this speed at 3000 ft: there the roll of the propeller torque and the yaw of the slipstream are balanced |  |
| `Cp0` | 0.0567 | POH-derived | power coefficient of the propeller standing still: full throttle gives 2280 to 2400 RPM static (2340 taken) | p.2-5 |
| `CpJ0` | 0.976 | POH-derived | advance ratio at which the propeller would absorb no power, with the exponent below: from the cruise table (2100 to 2650 RPM, 2000 to 8000 ft) | p.5-16 Fig 5-7 |
| `CpExp` | 5.36 | POH-derived | exponent of the fall of the power coefficient with advance ratio, from the cruise table | p.5-16 Fig 5-7 |
| `Ct0` | 0.0978 | POH-derived | thrust coefficient standing still (about 540 lb of static thrust): from the takeoff ground roll | p.5-12 Fig 5-4 |
| `Ct1` | -0.02516 | POH-derived | fall of the thrust coefficient with the advance ratio; with Ct3 it gives the rate of climb at sea level and the assumed efficiency of 0.78 in cruise | p.5-14 Fig 5-5, p.5-16 Fig 5-7 |
| `Ct3` | -0.08136 | POH-derived | fall of the thrust coefficient with the cube of the advance ratio (see Ct1) | p.5-14 Fig 5-5, p.5-16 Fig 5-7 |
| `torqueLapse` | 0.165 | POH-derived | full-throttle torque goes as (pressure ratio over the root of the temperature ratio) to the power 1.165: fits the rate of climb with altitude and with temperature. The fastest lines of the cruise table at and above 8000 ft then ask 5 to 8 % more power than the model has (4 to 7 knots) | p.5-14, 5-15, 5-16 |
| `windmillJ` | 0.95 | estimated | advance ratio of the windmilling propeller |  |
| `kMain` | 60000 | estimated | stiffness of a main gear leg (N/m) |  |
| `cMain` | 4500 | estimated | damping of a main gear leg (N s/m) |  |
| `kNose` | 32000 | estimated | stiffness of the nose strut (N/m) |  |
| `cNose` | 3000 | estimated | damping of the nose strut (N s/m) |  |
| `muRolling` | 0.02 | estimated | rolling friction on a paved, level, dry runway |  |
| `muBraking` | 0.43 | POH-derived | braking friction with maximum braking: from the landing ground roll | p.5-21 Fig 5-10 |
| `muSide` | 0.65 | estimated | side friction of the tyres |  |
| `noseSteerDeg` | 10 | POH | the rudder pedals turn the nose wheel about 10 degrees each side of centre | p.7-9 |
| `flapRateDegS` | 5 | estimated | speed of the electric flaps (degrees per second): about eight seconds from up to full down |  |
<!-- coefficients:end -->
