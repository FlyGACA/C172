# Under the skin: structure, systems, mechanisms and fasteners

The basic Phase 8 model is what you see from outside and from the seats. This document describes
what has been added underneath, so that any part can be shown on its own or in place: a rib, a
pulley, the fuel selector valve, a rocker arm, the capsule of the airspeed indicator, a row of
rivets, a single bolt.

- **Which parts exist, and their ids:** [`06_parts_index.md`](06_parts_index.md) (1,084 parts, English and Arabic names).
- **Pictures of every assembly:** [`../../09_book_figures/atlas/`](../../09_book_figures/atlas/README.md).
- **How to draw or export a part:** [`../../09_book_figures/README.md`](../../09_book_figures/README.md#any-part-on-its-own).

## Detail levels

Every part carries a level.

| Level | What | Parts | Where it is |
|---|---|---|---|
| 0 | Basic model: skins, glass, gear, cockpit, engine as seen with the cowl off | 340 | every web model, the `.blend` |
| 1 | Under the skin: structure, control runs, system components, wiring, the insides of the engine and of the instruments | 503 | the **high** web model, the `.blend` |
| 2 | Fasteners (rivet rows, screws, bolts) and the hardware kit | 241 | the `.blend` only; left out of renders until a figure asks for them |

The medium and low web models stay basic, so that tablets and phones do not download what they will
not show. A figure recipe sets `"detail": 2` to see the fasteners; the part tool shows whatever part
it is asked for.

## What was built, and from what

The handbook says what the aircraft is made of and shows how its systems are joined. It does not
give positions. So each part records two things: `status`, which says how we know the part exists,
and `note`, which says what is representative about it.

| Pack (`blender/c172/detail/`) | Parts | From the handbook | Representative |
|---|---|---|---|
| `structure_wing` | 102 | Front and rear spar, ribs, stringers, the fittings each spar carries; the rear spar is a partial-span spar (p.7-3) | Rib stations, gauges, lightening holes, number of stringers |
| `structure_fuselage` | 43 | Semimonocoque: bulkheads, stringers, skin; carry-through spars; gear bulkhead and forgings; strut bulkhead and attaching plates; four engine mount stringers; door posts (p.7-3). Stations 65.3, 108 and 142 (Fig 6-4) | Other frame stations, sections, the keel beams |
| `structure_tail` | 56 | Fin spar, ribs, dorsal; rudder ribs and balance weight; stabiliser spars and ribs; elevator torque tube, balance weights (p.7-3) | Stations and sections |
| `controls` | 101 | Every member of Figure 7-1: control column, chains, cables, bellcranks, push-pull rods, rudder bars, trim wheel chain and actuator | Every position; pulley and turnbuckle positions |
| `flap_drive` | 25 | Electric motor, transmission, drive pulleys, cables, push-pull rods, tracks (p.7-10, Fig 7-3) | Positions; the form of the tracks |
| `fuel` | 27 | Two tanks, two outlets each, selector valve, strainer, primer, vent crossover, quantity transmitters, sump drains (p.7-20 to 7-23, Fig 7-6) | The tank outline (the bay holds about 21.5 US gal, the standard tank), every pipe route |
| `pneumatic` | 13 | Pitot and static lines, alternate static valve, vacuum relief valve, filter, hoses, suction gage line, stall warning tube and horn (p.7-31 to 7-34, Fig 7-9) | Routes and forms |
| `brakes` | 8 | Master cylinder on each of the pilot's pedals, a line to each brake, parking brake (p.7-23) | Forms, routes, parking brake linkage |
| `electrical` | 18 | Contactors, alternator control unit, bus bar (Fig 7-7) | Mounting positions, every cable and harness route |
| `engine_detail` | 64, and 8 of level 2 | Oil system: suction strainer screen, engine-driven pump, bypass valve, hose to the cooler on the lower right side of the firewall and back, pressure relief valve, breather (p.7-18). Carburetor: up-draft, float type, fixed jet, accelerator pump, mixture control, carburetor heat from the muffler shroud (p.7-19). Engine controls (p.7-16) | What every engine of this kind has (tappets, push rods, rocker arms, valve springs, piston pins and rings, timing gears at 2 : 1) is `type_data`; every form, size and position is representative, not Lycoming data |
| `instruments` | 46 | What works each instrument: pitot and static pressure (p.7-31), suction for the two gyro indicators (p.7-32); a direct oil line to the oil pressure gage, an electrical sensor for the oil temperature gage, an engine-driven mechanical tachometer (p.7-17) | Everything inside the cases: see below |
| `fasteners` | 233 | Nothing: the handbook does not show fasteners | Rows follow the modelled structure at a representative pitch |

Also part of the basic model since this work: a headliner at the level of the wing-root underside
(the carry-through spars lie above it), a raised baggage floor behind the rear seat, and openings
in the under-floor bulkheads, keel beams, wing ribs, the aileron spar and the last tailcone frame
wherever a cable or pipe passes.

### Inside the instruments

Each of the six flight instruments and the tachometer has a case (a square front against the back
of the panel, a round barrel behind it) and, inside it, the mechanism of an instrument of its kind:

| Assembly | Inside |
|---|---|
| `@airspeed_indicator` | capsule with the pitot inlet, static port into the case, link, rocking shaft, sector gear, pinion and hairspring |
| `@altimeter` | three aneroid capsules, the same linkage, the gear train to the three pointers, the barometric setting knob with its pinion and ring gear |
| `@vertical_speed_indicator` | capsule on the static line, calibrated leak into the case, linkage |
| `@attitude_indicator` | rotor with an upright axis, inner and outer gimbal, horizon bar, air nozzle, suction port |
| `@directional_gyro` | rotor with a level axis, two gimbals, the gears from the outer gimbal to the heading card, setting knob, air nozzle, suction port |
| `@turn_coordinator` | electric rotor, gimbal tilted 30 degrees, centring spring, damper |
| `@tachometer` | drive cable from the engine, rotating magnet, drag cup, hairspring |

These show **how an instrument of each kind works**. They are drawn to fit the case and to mesh
(the sector reaches the pinion, the knob's pinion reaches its ring gear), but they are not the
mechanism of the make installed in the aircraft, and every such part says so in its `note`.
The cases are the assembly `@instrument_cases`; a figure draws a case as a phantom round its
mechanism with `--ghost PANEL.ASI.case`. The pitot, static and vacuum lines end at the ports on
the backs of the cases (`PORTS` in `detail/instruments.py` is the one table both packs read).

**None of this is a maintenance reference.** For anything that matters on the aircraft, use the
manufacturer's maintenance manual and illustrated parts catalogue.

## Where the runs lie

`detail/lanes.py` is one table of where cables, pipes and wires run: under the cabin floor (which
lateral position and height each run has, and between which stations), across the cabin, and along
each wing. The packs that lay a run read its lane from that table, and the structure packs cut an
opening where a lane passes a bulkhead, a keel beam or a rib. To add a run, add its lane first.

Where there is no lane, each pack lays its runs so that they pass each other:

- **Door posts.** A door post is a channel: its web on the skin, its flanges standing inward as far
  as the cabin lining. The runs lie in it side by side, each on the side from which it enters and
  leaves: in the forward post the wiring (ahead), the pitot line (centre, left post only) and the
  fuel pipe from the forward tank outlet (behind); in the rear post the fuel pipe from the aft
  outlet (ahead) and the aileron cable (behind).
- **Behind the instrument panel.** The static lines cross in one layer 30 mm behind the instrument
  ports and the vacuum hoses turn 30 mm further forward.
- **Engine compartment.** Cables, hoses and pipes pass inboard or outboard of the engine mount
  tubes, not between them: the alternator cable and the primer lines along the left side of the
  cowl, the oil gage line and the breather near the centreline.

**Nothing runs through anything else.** The validator checks every pipe, hose, cable and wire (51
runs) against every other part: a run may touch the parts it joins (those of its own assembly, a
panel instrument or control, or a part named in its `joins` tag) and may pass through the skins,
linings and walls that have an opening for it in the aircraft (firewall, cabin lining, door-post
flanges); anything else it cuts through fails the build.

## Assemblies

A part can belong to one or more assemblies, which gather the parts of a system wherever they are:
`aileron_control` has parts in the cabin, in both wings and on the ailerons. Select an assembly with
`@name` in a figure recipe or in the part tool. The index lists the 26 of them, from
`@aileron_control` to `@vertical_speed_indicator`.

## Checks

`validate_geometry.py` (run by `npm run validate:geometry8` and in CI) checks, for every part of
every level:

- mesh health: no zero-area faces, no non-finite vertices;
- parts in the fuselage stay inside the fuselage and cowl skin (551 of them), parts in a wing stay
  inside the wing skin (155; 3 mm tolerance; a rivet head is allowed to stand proud);
- no pipe, hose, cable or wire cuts through another part (see "Where the runs lie");
- the published dimensions, the stance and the attachments of the basic model, as before.

`quality_gate.py` checks that the parts list has bilingual names and a valid status for every part,
that a part documented from the handbook carries its page, that the list agrees with the high web
model, and that the parts index is up to date.

## Adding a pack

1. Create `blender/c172/detail/<name>.py` with a `build(ctx)` function (and `LEVEL = 2` for
   fasteners). List its name in `detail/__init__.py`.
2. Make each part with `common.part(ctx, name, mesh, group, system, label_en, label_ar, material,
   status=..., ref=..., note=..., assembly=...)`. Name a part after where it is: `WING_L.*` parts are
   checked against the wing skin, parts of the tail are `EMPENNAGE.*`, everything else is checked
   against the fuselage.
3. Use the builders in `common.py` (sheet-metal plates with holes, flanges, swept sections, cables
   led round pulleys, pipes, bellcranks, bolts) rather than raw meshes, and `lanes.py` for routes.
   A new kind of run is checked once its name matches a pattern in `RUNS` (`validate_geometry.py`);
   name what it is joined to with `joins="PART.name,OTHER.*"` if that is not in its own assembly.
4. `npm run build:model8 && npm run validate:geometry8 && npm run parts:index && npm run quality`.
