# The pilot's seat

The first-person camera of the Phase 8 viewer. The camera is the eye of the pilot in the left seat. The head
turns and the body leans within limits, and a hand works a control on the model itself, but only a control
that is within arm's reach.

**What it is not.** The limits of the head and the reach of the arm are estimates for a seated adult in a
shoulder harness. Nothing here was measured on an aircraft or on a pilot. No body, arm or hand is drawn, and
the reach is a distance from the shoulder, not the motion of an arm round the control wheel. Use it to show
where things are and how they are worked, not to judge whether a particular pilot can reach a particular
control.

## Using it

Choose **Cockpit** in the top bar, or **Camera → Pilot**. In flight, press **C** or choose **Pilot's eye**:
the same seat, in the aircraft the flight model flies. Beginning a flight from the Cockpit mode begins it in
the seat.

| To do this | Pointer | Keys | Buttons (left drawer, *Pilot's seat*) |
|---|---|---|---|
| Turn the head | drag the picture; the view goes the way the pointer goes | I J K L | the eight views |
| Look ahead again | | R | Ahead |
| A named view | | 1 to 8 | Ahead, Panel, Left, Right, Pedestal, Fuel selector, Overhead, Behind |
| Lean | | W A S D | Forward, Back, Left, Right, Sit up |
| Zoom | mouse wheel over anything that is not a control | | |
| Flip a switch | click it | | |
| Move a push-pull control, the trim wheel or the control wheel | drag it | | |
| Move a control one step | mouse wheel over it | | |
| See what a part is | click it (the eye looks through the glass of a window or an instrument) | | |

A control under the pointer is tinted and named, with its state: blue when it is within reach, amber when a
lean toward it would bring it within reach, red when no lean of this seat reaches it. A control that is out
of reach does not move. **Show what the hand reaches** tints every control at once.

On a touch screen a finger turns the head and works the controls in the same way; the buttons of the drawer
lean and choose the views.

## The head and the body

Model coordinates: metres, nose +Z, the pilot's left +X, up +Y. Positive yaw is to the left.

| Quantity | Value | Source |
|---|---|---|
| Eye, head level and straight | (0.28, 1.63, −0.05) | Estimated: where an adult's eye is on the seat as the model draws it, 0.77 m above the cushion pressed down by 3 cm and 0.2 m ahead of the seat back at shoulder height. The handbook's station 37 (Figure 6-3) is the centre of gravity of the front seat occupant, not the eye. |
| Head turn (yaw) | 135° either way | Estimated: about 80° of neck, the rest eyes and shoulders. Not straight behind. |
| Head nod (pitch) | 70° down to 55° up | Estimated. |
| Lean forward | 0 to 0.20 m | Estimated: the seat back behind, the harness and the control wheel ahead. |
| Lean sideways | 0.14 m to the right, none to the left | Estimated. On the left the door post is a hand's width from the head. |
| Neck, from the eyes | 0.10 m below, 0.085 m behind | Estimated. The eyes swing about the neck as the head turns. |
| Shoulders, from the eyes | 0.25 m below, 0.19 m either side, 0.045 m behind | Estimated. They follow 70 % of a lean and do not turn with the head. |
| Hips to eyes | 0.75 m | Estimated. A lean swings the head about the hips, so it comes down a little. |
| Reach of the arm | 0.72 m from the shoulder | Estimated. |
| Field of view | 68° top to bottom; 28° to 75° with the mouse wheel | A choice of the viewer, not a property of the eye. |

The head turns in the cabin's own axes. On the ground the cabin stands 4.7° nose up, so "straight ahead" is
along the fuselage and the horizon lies a little below it. At rest the gaze is 11° below straight ahead: over
the glareshield, with the top of the panel in view.

**The eye stays inside the cabin.** Wherever these limits let the eye go, the nearest surface of the model
is at least 6 cm away, twice the near plane of the camera, so the picture never cuts through a wall, the
windshield, the headliner or the seat. The browser test checks this against the model.

## The controls

Each control is a part of the model. What it does is in `js/cockpit_controls.js`; in flight it acts on the
flight, on the apron it moves the model and the systems simulation.

| Control (part) | How it is worked | From the seat |
|---|---|---|
| Throttle, mixture (`PANEL.throttle`, `PANEL.mixture`) | Drag: up the picture is pushed in. Throttle in is open; mixture out is lean, to idle cut-off. | within reach |
| Carburetor heat (`PANEL.carb_heat`) | Click, or drag out: on. | within reach |
| Ignition (`PANEL.ignition_switch`) | Click the right half: one position toward BOTH. Click the left half: one position toward OFF. Held on the right half at BOTH: START, until let go. | within reach |
| Master switch, two halves (`PANEL.master_bat`, `PANEL.master_alt`) | Click. | within reach |
| Avionics, beacon, navigation lights, strobes, landing light, pitot heat (`PANEL.switch_*`) | Click. | within reach |
| Primer (`PANEL.primer`) | Click: one stroke. | within reach |
| Flap lever (`PANEL.flap_switch`) | Click the upper half: 10° up. Click the lower half: 10° down. In flight the flaps follow at the speed of their motor, and need electrical power. | just within reach |
| Elevator trim wheel (`INTERIOR.trim_wheel`) | Drag: the rim rolled down is nose up. | within reach |
| Control wheel (`INTERIOR.yoke_L`) | Hold and drag: across turns it, down the picture pulls it back. In flight it centres when let go; on the apron it stays where it is put. | within reach |
| Parking brake (`INTERIOR.parking_brake`) | Click. | within reach |
| Fuel selector (`FUEL.selector_handle`) | Click the right half: clockwise. Click the left half: the other way. LEFT, BOTH, RIGHT, OFF round the dial. | with a slight lean: on the floor between the seats |
| Cabin heat (`PANEL.cabin_heat`) | Click. The knob moves; the simulation has no cabin air. | with a lean |
| Cabin air (`PANEL.cabin_air`) | Click. The knob moves; the simulation has no cabin air. | with a lean |
| Left door, inside handle (`INTERIOR.door_inner_handle_L`) | Click: the door opens or closes. Only while the aircraft stands still. | within reach, on the arm rest behind the left elbow |
| Right door, inside handle (`INTERIOR.door_inner_handle_R`) | Click. | within reach, across the cabin |

In the model the nearest control is the control wheel, about 0.42 m from the shoulder; the flap lever is
at 0.70 m, just within the arm. Three controls take a lean: the fuel selector on the floor (by a hair), cabin
heat and cabin air, the farthest at about 0.81 m. No control of this table is out of reach of the left seat, as
it should be in an aircraft that one pilot flies. The red tint is there for a seat or an arm that differs from
these estimates.

The mouse wheel over a control moves it one step: the throttle and mixture by 4 %, the trim by a hundredth of
its travel, the flap lever, the key and the fuel selector by one position.

## A pilot who was measured

The eye, the reach of the arm and the shoulders can be replaced by measurements of a pilot sitting in the
aircraft: the eye from the face of the instrument panel, from the cabin centreline and from the floor; the
arm from the shoulder joint to the fist. See [10_flight_survey.md](10_flight_survey.md). The drawer then says
what was measured. None is today.

## What is not modelled

- The pilot's body. No arm is drawn, nothing stops the hand, and the hand does not have to let go of one
  control to take another.
- The feet. The rudder pedals and the toe brakes are worked by the keys (Z, X, B) or by the rudder
  assistant, as in the outside view.
- The right seat. There is one eye point, the pilot's.
- Seat adjustment, the door window, the sun visors, the ventilators, the radios, the light rheostats and the
  circuit breakers. They can be clicked for their description; they do not move.
- The alternate static source valve. It lies behind the panel in the model and cannot be seen from the seat;
  it is worked from the left drawer.

## Files and tests

| File | What it holds |
|---|---|
| `js/seat.js` | The limits, where the eyes and the shoulders are, and what a hand reaches. Plain numbers. |
| `js/cockpit_controls.js` | What each control does when it is pressed, clicked, dragged or wheeled. Plain logic. |
| `js/cockpit.js` | The camera at the eye, the pointer on the controls, the tint and the name under the pointer. |
| `js/app.js`, `js/flightmode.js` | What the controls act on: the model on the apron, the flight in the air. |
| `js/survey.js` | A survey of the pilot in the seat, replacing the estimates ([10_flight_survey.md](10_flight_survey.md)). |
| `tests/cockpit.test.mjs` | 11 tests: limits, eye, lean, reach; every control worked through all its positions. |
| `tests/e2e.mjs` | In a browser, on the model: the eye at its place, the limits, the cabin clear of the eye, the reach of each control, and the controls worked with the pointer. |
