# The instrument panel and the cockpit

What is on the panel and where, what that was drawn from, and where to change it.

## Where the arrangement comes from

The panel follows the handbook's own figure of it and the description that goes with it (POH Figure 7-2,
p.7-6 and 7-7; text p.7-8 and 7-9). The handbook gives what is where; it gives no dimensions, so sizes and
exact places are estimated.

| Where | What | Parts |
|---|---|---|
| In front of the pilot | The attitude indicator over the directional indicator, with the control column under them; the airspeed indicator and the turn coordinator on their left, the altimeter and the rate-of-climb indicator on their right; the tachometer under the turn coordinator | `PANEL.ASI`, `AI`, `ALT`, `TC`, `DG`, `VSI`, `TACH` |
| Between the flight group and the radios | Two omni course indicators and, under them, the ADF bearing indicator | `PANEL.VOR1`, `VOR2`, `ADF` |
| Near the left edge | Clock, suction gage, the fuel quantity indicators (left and right), oil temperature and oil pressure, the ammeter, the low-voltage light | `PANEL.CLOCK`, `SUCTION`, `FUEL_L`, `FUEL_R`, `OIL_T`, `OIL_P`, `AMMETER`, `PANEL.low_volt` |
| About the centreline | The avionics stack: audio control panel, marker beacon lights, two NAV/COM sets, ADF receiver, transponder | `PANEL.radio_*` |
| On the right | Space for additional instruments (blanked), the flight hour recorder, the limitations placard | `PANEL.instrument_space_1..3`, `PANEL.hourmeter`, `PANEL.placard_speed` |
| Subpanel, left | Primer, master switch, ignition switch, avionics power switch, circuit breakers, electrical switches | `PANEL.primer`, `master_alt`, `master_bat`, `ignition_switch`, `switch_*`, `breaker_*` |
| Subpanel, middle | Carburetor heat, throttle, mixture; the light rheostats and the alternate static source valve under them | `PANEL.carb_heat`, `throttle`, `mixture`, `PANEL.light_rheostats`, `PITOT_STATIC.alternate_static_valve` |
| Subpanel, right | Wing flap switch lever with its position scale, lighter, cabin heat and cabin air, map compartment | `PANEL.flap_switch`, `flap_slot`, `flap_ind`, `PANEL.lighter`, `cabin_heat`, `cabin_air`, `map_compartment` |
| Below the subpanel | Parking brake handle in front of the pilot; the pedestal with the trim wheel and the microphone | `INTERIOR.parking_brake`, `INTERIOR.pedestal`, `trim_wheel` |
| On the glareshield | Magnetic compass | `PANEL.magnetic_compass` |

Three things changed place to match the handbook: the tachometer (it stood to the right of the radios), the
circuit breakers (they were on the right of the subpanel; the handbook puts them on the left), and the
control wheels (their shafts came through the subpanel; they come through the panel under the gyros, 13 cm
higher). The halves of the master switch were the wrong way round: the left half is ALT, the right half BAT
(POH p.7-25).

## How an instrument is built

The panel is a plate with an opening for each instrument. Round a round instrument stands a moulded rim
(`PANEL.<name>.bezel`); the dial lies 8.5 mm behind the face of the panel at the bottom of the recess
(`.face`, or `.ball` / `.card` with a `.mask` for the two gyros); the pointers turn 3 mm in front of the
dial, under a hub cap; the glass sits in the rim. So a pointer moves over its dial as the eye moves, and
the rim shades the dial.

The fuel quantity and oil indicators are small rectangular ones, two to a frame, and the ammeter is one of
the same kind: the pointer is pivoted below the middle of the face, under a cover, and sweeps a scale across
the top. Their scales, like those of
the round dials, are drawn from `data/instruments.json` (limits and arcs from POH Section 2).

The radios are plain sets of their kind for the period, with small readouts, legends and knobs; they copy
no maker's set, and the avionics of an aircraft vary. The omni course indicators and the ADF bearing
indicator are plain faces too: the viewer's simulation has no radio aids, so their pointers do not move.

## Where to change it

| To change | Edit | Then |
|---|---|---|
| Where an instrument stands, or its size | `INSTRUMENTS`, `RECT_GAUGES`, `BLANKS` and the row and column constants at the top of `blender/c172/cockpit.py` | `npm run build:model8` |
| The order of the avionics stack | `STACK` in `cockpit.py` | as above |
| The face of a radio, its knobs | `panel_misc_atlas` and `RADIO_KNOBS` in `blender/c172/dials.py` (the knobs stand where the table says, and the face is drawn round them) | as above |
| A dial | `data/instruments.json` (scale, arcs, limits), `dials_atlas` in `dials.py` (lettering) | as above |
| A switch, a breaker, a knob of the subpanel | `build_panel` in `cockpit.py` | as above |
| The control wheel | `build_controls` in `cockpit.py` | as above |

What lies behind the panel follows by itself: the cases and works of the flight instruments, the radio
units, the control column, the bus bar and the lines and wires read where their instrument, switch or
shaft stands. `npm run validate:geometry8` then says whether a line or a wire now cuts through something.

## What this is not

- Not a survey of an aircraft's panel. The handbook's figure shows a panel with optional equipment; what an
  aircraft carries, and exactly where, is for its equipment list and a look at it.
- The lettering gives the plain names of the controls; the typeface and wording of the placards of an
  aircraft are not reproduced. No registration is shown.
- The wood grain of the subpanel, the ivory rocker switches, the moulded rims and the form of the control
  wheel are those of the late 1970s; their exact form is representative.
