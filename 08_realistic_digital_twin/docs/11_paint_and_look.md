# Paint, markings, shade and the look of the viewer

How the model gets its paint scheme, its markings, the shade in its cabin and the picture the viewer
draws, and where to change each. The scheme and the markings are the model's own: they copy no
manufacturer's scheme, and no registration is painted on the model.

## The paint scheme

The scheme is a drawing of the aircraft **seen from the side**: a navy band that grows from a point at the
nose bowl, runs level along the cabin and the tailcone, and sweeps up across the fin and the rudder, with a
gold line under it and a thin navy line over it. It is defined by a handful of numbers at the top of the
scheme section of `blender/c172/textures.py`:

| Name | Meaning | Value |
|---|---|---|
| `BAND_Z` | height of the middle of the band along the cabin | 1.375 m (build frame) |
| `BAND_HALF` | half the height of the band | 0.065 m |
| `NOSE_Z` | where the band ends at the nose bowl | 1.585 m |
| `TAIL_FROM`, `TAIL_SLOPE`, `TAIL_BEND` | where the band leaves the tailcone, how steeply it climbs the fin, over what length it turns | station 186, 0.42, 12 in |
| `WHITE`, `NAVY`, `GOLD` | the three colours | at the top of the file |

To lay that drawing on a skin, the painter has to know which point of the aircraft each texel of the
skin's texture covers. That is read off the finished surface: `blender/posmaps.py` builds the airframe in
Blender and draws the triangles of the fuselage, the cowl, the fin, the rudder and the cabin liner into
their textures, carrying their positions (`assets/posmaps/*.npy`, not kept in the repository). The texture
generator then paints each texel from where it lies. A stripe is therefore the same line in space on the
cowl, the fuselage, a door, the fin and the rudder, and crosses their joints unbroken. A plate that lies in
a painted skin (the ventilating air door on the right of the forward fuselage) takes the paint of that skin
from the same map (`posmap.wear_skin`), so the stripes run across it too.

The paint of the fuselage is 4096 px in the high level and 2048 px in the others, that of the cowl 2048 px
and 1024 px (it is a quarter as long, so its texels are as fine); the relief and roughness maps are half
the size of the paint.

```bash
npm run build:model8      # position maps, textures, then the model (about 3 minutes)
npm run posmaps8          # the position maps alone
npm run textures8         # the textures alone (needs the position maps)
```

## Markings

A marking painted into a skin's texture is only as sharp as that texture, and is stretched wherever the
skin is unrolled unevenly. The markings are therefore separate small sheets with their own texels, pressed
onto the skin where they belong (`blender/c172/decals.py`, atlas `assets/textures/decals.png`):

| Part | What it is |
|---|---|
| `AIRFRAME.marking_wordmark_L/R`, `EMPENNAGE.marking_wordmark_L/R` | the operator's wordmark on the rear fuselage and on the fin |
| `WING_L/R.marking_fuel` | the fuel grade and quantity beside each filler: 100LL (POH p.1-3), 21.5 US gal in each standard tank (POH p.1-4) |
| `WING_L/R.marking_no_step` | NO STEP on each flap |

The wording, typeface and form of the placards of an aircraft are not reproduced. To change the wordmark,
edit `DECAL_LAYOUT` in `blender/c172/atlas.py` and rebuild. Each marking is a part like any other: it can be
selected, hidden and exported on its own. A marking that does not lie wholly on its skin stops the build.

The names of the switches and controls are lettered in white on the panel, the pedestal and the fuel
selector in the same way (`PANEL.lettering`, `INTERIOR.pedestal_lettering`, `FUEL.selector_lettering`;
atlas `panel_placards.png`). They are the plain names of the controls, for finding them in a lesson.

## The propeller

The blades stand in the spinner, clear of the nose bowl (propeller plane at station −38.6, 4 in ahead of the
spinner's base). The face the pilot sees is flat black, the forward face black with a sheen, and each tip
carries a yellow band 8 cm wide. Planform, twist and section are illustrative.

## Shade baked into the model

A web viewer lights every surface as if nothing stood round it, so a cabin looks flat. The build gives
each vertex of the basic model a value for how open it is to its surroundings (`blender/c172/ao.py`): 1 in
the open, lower in corners, under the panel, between the seats, under the wing root. It travels in the
GLB as the vertex colour and darkens the surface there. The seams of the pleated seat inserts are shaded
the same way.

- Only what one looks at from outside and from the seats is shaded (airframe, wings, tail, gear, cowl,
  cabin, panel). The systems and what lies under the skin are not: they are shown through a ghosted skin
  or with the cowl off, and must not be dark from what hid them.
- The editable `.blend` and the Cycles renders do not use it: they work the light out properly.

## The picture

| What | Where | Levels |
|---|---|---|
| Sky drawn by a shader (gradient, sun, drifting clouds); it also lights the model and is what the paint reflects | `js/sky.js` | all |
| Concrete apron painted on a canvas: slabs, joints, stains, tyre marks; lead-in line and stop bar at the nose wheel | `js/sky.js` | all |
| Sun with soft shadows; clear coat on the painted skin | `js/viewer.js` | all |
| Bloom on the highlights, a little contrast and a vignette | `js/viewer.js` | high, medium |
| Screen-space ambient occlusion; window glass that lets the picture behind show through | `js/viewer.js` | high |
| From the pilot's seat the glass and the bright metal mirror the cabin, not the open sky | `js/viewer.js`, `js/cockpit.js` | all |

`?test=1` leaves the effects off (the browser tests run on a software renderer); `?fx=1` forces them on,
`?fx=0` off. A telephone gets the low level, a tablet the medium one, a desktop the high one (the medium
one if it has little memory or few processor cores); `?q=` chooses.

## What this is not

- Not a record of any aircraft's paint, markings or upholstery. The interior is a late-1970s pattern in
  tan: vinyl bolsters round pleated cloth, a two-tone liner, cut-pile carpet.
- The baked shade is an approximation of soft light, not a measurement, and it does not change when a
  door opens or a part is taken away.
