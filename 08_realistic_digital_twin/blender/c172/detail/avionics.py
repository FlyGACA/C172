"""Avionics installation: the radios behind their faces, the avionics bus, the antenna cables, the
speaker wire, the emergency locator transmitter.

What the handbook says: avionics equipment is stacked approximately on the centreline of the panel
(p.7-9); an avionics power switch feeds it (p.7-23 to 7-27, Figure 7-7); an audio control panel
connects the receivers to the airplane speaker or to a headset and the microphone to the chosen
transmitter (p.7-35 to 7-37). Section 7 does not describe the antennas, their cables or where the
units are mounted, and the equipment fitted differs from one aircraft to another.

What this pack builds:
  the unit behind each face of the radio stack (a chassis in its tray, with its connector);
  the avionics bus beside the stack, its feed from the avionics power switch and a lead to each unit;
  a coaxial cable from the communication transceiver to the antenna on the cabin roof, from the
  navigation receiver to the antenna on the fin, from the ADF receiver to the sense antenna and from
  the transponder to its antenna under the fuselage; the wire from the audio control panel to the
  speaker in the cabin ceiling;
  an emergency locator transmitter in the tailcone with the cable to its antenna.

What is from where:
  poh        that there is an avionics bus fed through the avionics power switch, an audio control
             panel and a speaker
  estimated  everything else: the depth of the units, where the bus and the transmitter are mounted,
             every route. The cables leave the stack to the right, run along the right side of the
             cabin above the upper engine mount stringer, up the right forward door post between the
             wiring and the fuel pipe, and aft above the headliner; the transponder cable runs under
             the floor in a lane of its own (lanes.py).
Not modelled: the wiring from the bus bar to the switches and circuit breakers, the wires to the
microphone and phone jacks and to the keying switch, the marker beacon antenna and the ADF loop
antenna with their cables.
"""
import bpy
from mathutils import Vector

from ..units import IN, fs, wl
from .. import airframe as A
from . import lanes
from . import structure_fuselage as SF
from . import structure_tail as ST
from .structure_fuselage import SKIN
from .common import pipe, disc, rod, part, new_bm, box, X, Y, Z

SYS = "AVIONICS"
ASSEMBLY = "avionics"
COAX = 0.0025                     # radius of a coaxial antenna cable as drawn
WIRE = 0.0018
PITCH = 0.008                     # distance between two cables that run side by side
DEPTH = {"COMNAV1": 0.24, "COMNAV2": 0.24, "ADF": 0.20, "XPDR": 0.20, "AUDIO": 0.12, "MARKER": 0.10}       # of each unit behind its face
NAMES = {
    "COMNAV1": ("NAV/COM 1", "جهاز الملاحة والاتصال 1"), "COMNAV2": ("NAV/COM 2", "جهاز الملاحة والاتصال 2"), "ADF": ("ADF receiver", "مستقبل ADF"),
    "XPDR": ("Transponder", "المرسل المجيب"), "AUDIO": ("Audio control panel", "لوحة التحكم الصوتي"), "MARKER": ("Marker beacon receiver", "مستقبل منارات العلامات"),
}


def bounds(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [min(c[i] for c in corners) for i in range(3)], [max(c[i] for c in corners) for i in range(3)]


def add(ctx, name, bm, group, en, ar, mat, status="estimated", smooth=True, **tags):
    tags.setdefault("assembly", ASSEMBLY)
    return part(ctx, name, bm, group, tags.pop("system", SYS), en, ar, mat, status=status, smooth=smooth, **tags)


def build(ctx):
    scene = bpy.data.objects
    backs = build_units(ctx, scene)
    build_bus(ctx, scene, backs)
    build_roof_cables(ctx, scene, backs)
    build_transponder_cable(ctx, scene, backs)
    build_elt(ctx, scene)
    for name in ("ELECTRICAL.comm_antenna", "ELECTRICAL.adf_sense_wire", "ELECTRICAL.elt_antenna", "EMPENNAGE.nav_antenna", "AIRFRAME.transponder_antenna", "PANEL.switch_avionics_master") + tuple(
            f"PANEL.radio_{region}" for region in DEPTH):
        if name in scene:
            scene[name]["assembly"] = ",".join([a for a in str(scene[name].get("assembly", "")).split(",") if a] + [ASSEMBLY])


def build_units(ctx, scene):
    """The unit behind each face. Returns, for each, the middle of its back and its extent."""
    backs = {}
    for region, depth in DEPTH.items():
        face = scene[f"PANEL.radio_{region}"]
        low, high = bounds(face)
        y1 = low[1]                                    # back of the face plate
        y0 = y1 - depth
        x0, x1, z0, z1 = low[0] + 0.006, high[0] - 0.006, low[2] + 0.003, high[2] - 0.008
        centre = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        bm = new_bm()
        box(bm, (x1 - x0, depth, z1 - z0), center=centre)
        box(bm, (0.034, 0.008, min(0.016, z1 - z0 - 0.004)), center=(centre.x - 0.03, y0 - 0.004, centre.z))          # the connector
        en, ar = NAMES[region]
        add(ctx, f"PANEL.radio_{region}.chassis", bm, "PANEL", f"{en}: the unit behind its face, in its mounting tray", f"{ar}: الوحدة خلف واجهتها، في حاملها", "panel_grey", smooth=False,
            parent=face, note="Avionics equipment is stacked on the centreline of the panel (POH p.7-9); the depth of the unit is representative and the equipment fitted varies by aircraft")
        backs[region] = dict(point=Vector((centre.x, y0, centre.z)), x=(x0, x1), z=(z0, z1))
    return backs


def build_bus(ctx, scene, backs):
    """Avionics bus beside the stack: fed from the avionics power switch, with a lead to each unit."""
    x_bus, y_bus = backs["ADF"]["x"][1] + 0.024, bounds(scene["PANEL.radio_ADF"])[0][1] - 0.027       # beside the stack, just behind the panel
    low, high = min(b["z"][0] for b in backs.values()), max(b["z"][1] for b in backs.values())
    bm = new_bm()
    box(bm, (0.004, 0.012, high - low - 0.02), center=(x_bus, y_bus, (low + high) / 2))
    for region, back in backs.items():
        z = sum(back["z"]) / 2
        rod(bm, (x_bus, y_bus, z), (back["x"][1], y_bus, z), 0.0015, segs=5)
    add(ctx, "ELECTRICAL.avionics_bus", bm, "SYSTEMS", "Avionics bus, with a lead to each unit of the radio stack", "قضيب توزيع الأفيونكس، مع وصلة إلى كل وحدة في مجموعة الراديو", "copper",
        status="poh", ref="p.7-23 to 7-27 (Fig 7-7)", smooth=False, system="ELECTRICAL", note="The avionics power switch connects the avionics bus to the primary bus (POH Figure 7-7); where the bus is mounted is representative")
    switch = scene["PANEL.switch_avionics_master"].matrix_world.translation.copy()
    bm = new_bm()
    pipe(bm, [Vector((switch.x, switch.y - 0.035, switch.z)), Vector((switch.x - 0.03, y_bus, switch.z + 0.055)), Vector((x_bus + 0.03, y_bus, low + 0.012)), Vector((x_bus + 0.002, y_bus, low + 0.012))],
         WIRE, bend=0.02)
    add(ctx, "ELECTRICAL.wire_avionics_feed", bm, "SYSTEMS", "Avionics feed wire: from the avionics power switch to the avionics bus", "سلك تغذية الأفيونكس: من مفتاح طاقة الأفيونكس إلى قضيب الأفيونكس", "hose_red",
         status="poh", ref="p.7-23 to 7-27 (Fig 7-7)", system="ELECTRICAL", joins="ELECTRICAL.avionics_bus", note="Route representative")


def build_roof_cables(ctx, scene, backs):
    """The cables that leave the stack to the right and go up the right forward door post: the speaker
    wire and the communication, ADF and navigation antenna cables. They keep the same order all the way
    (the first to leave the bundle lies on top, ahead and inboard), so that none crosses another:
    behind the panel each has its own depth and height; along the right side, between the skin and the
    lining, they lie one above the other below the wing wiring; in the post each has its own lane between
    the wiring and the fuel pipe; above the headliner they lie side by side inboard of the tail wiring."""
    ceiling = lambda station: A.headliner_z(station) + 0.010
    corridor_y = backs["COMNAV1"]["point"].y - 0.017
    members = [   # key, unit, x of its start behind the stack, radius, lane in the post (in from the centre line of the post)
        ("speaker", "AUDIO", -0.105, WIRE, -0.12),
        ("com", "COMNAV1", -0.02, COAX, 0.07),
        ("adf", "ADF", -0.05, COAX, 0.28),
        ("nav", "COMNAV2", -0.08, COAX, 0.49),
    ]
    paths = {}
    for index, (key, unit, start_x, radius, lane) in enumerate(members):
        z = 1.556 - index * 0.0076
        water = (z - 0.375) / IN
        y = corridor_y - index * PITCH
        roof_x = -0.400 - index * PITCH
        back = backs[unit]["point"]
        corners = [Vector((start_x, back.y, back.z))]
        if key == "speaker":                                                   # the audio panel is a short unit: its wire leaves beside the stack
            corners += [Vector((start_x, back.y - 0.022, back.z)), Vector((-0.16, back.y - 0.022, z)), Vector((-0.16, y, z))]
        else:
            corners += [Vector((start_x, y, back.z)), Vector((start_x, y, z))]
        corners += [SF.side_point(station, water, -1, SKIN + 0.008) for station in ((y / IN) + 40.0, 14.0, 20.0, 27.0)]
        corners += [SF.post_point("fwd", -1, w, shift=lane) for w in (water, 52.0, 58.0, 62.0, 65.0)]
        top = corners[-1]
        corners += [Vector((roof_x, top.y, top.z + 0.003)), Vector((roof_x, fs(41.5), ceiling(41.5)))]
        paths[key] = (corners, radius, roof_x)

    def finish(key, corners, name, en, ar, mat, **tags):
        path, radius, _x = paths[key]
        bm = new_bm()
        pipe(bm, path + corners, radius, bend=0.02)
        tags.setdefault("inside", "fuselage")
        return add(ctx, name, bm, "SYSTEMS", en, ar, mat, note="Not described in the POH; route representative", **tags)

    # ---- speaker wire: to the speaker in the cabin ceiling
    speaker = scene["ELECTRICAL.speaker"].matrix_world.translation.copy()
    x = paths["speaker"][2]
    level = ceiling((speaker.y / IN) + 40.0)
    finish("speaker", [Vector((x, speaker.y, level)), Vector((-0.04, speaker.y, level)), Vector((-0.03, speaker.y, speaker.z + 0.006))],
           "ELECTRICAL.wire_speaker", "Speaker wire: from the audio control panel to the airplane speaker", "سلك مكبر الصوت: من لوحة التحكم الصوتي إلى مكبر صوت الطائرة", "wire_yellow",
           system="ELECTRICAL", joins="ELECTRICAL.speaker")
    # ---- communication antenna cable: up to the antenna on the cabin roof, ahead of the rear carry-through spar
    antenna = scene["ELECTRICAL.comm_antenna"].matrix_world.translation.copy()
    x = paths["com"][2]
    y_turn = antenna.y - 0.062
    finish("com", [Vector((x, fs(60.0), ceiling(60.0))), Vector((x, y_turn, ceiling(67.5))), Vector((-0.012, y_turn, ceiling(67.5))), Vector((-0.012, antenna.y - 0.018, antenna.z - 0.012)),
                   Vector((-0.003, antenna.y - 0.004, antenna.z - 0.004))],
           "AVIONICS.coax_com", "Communication antenna cable: from the NAV/COM transceiver to the antenna on the cabin roof", "كابل هوائي الاتصال: من جهاز الملاحة والاتصال إلى الهوائي على سقف المقصورة",
           "hose_black", joins="ELECTRICAL.comm_antenna")
    # ---- ADF sense antenna cable: to the lead-in of the sense wire on the roof
    sense = scene["ELECTRICAL.adf_sense_wire"].matrix_world.translation.copy()
    x = paths["adf"][2]
    y_turn = sense.y - 0.02
    finish("adf", [Vector((x, fs(60.0), ceiling(60.0))), Vector((x, fs(71.3), ceiling(71.3))), Vector((x, y_turn, ceiling(83.0))), Vector((-0.012, y_turn, ceiling(83.0))),
                   Vector((-0.004, sense.y - 0.004, sense.z - 0.046))],              # ends under the roof skin, below the lead-in of the wire
           "AVIONICS.coax_adf", "ADF sense antenna cable: from the ADF receiver to the lead-in of the sense wire on the roof", "كابل هوائي الاستشعار لجهاز ADF: من المستقبل إلى مدخل سلك الاستشعار على السقف",
           "hose_black", joins="ELECTRICAL.adf_sense_wire")
    # ---- navigation antenna cable: beside the tail wiring (further inside) down the pillar behind the rear side window and along the tailcone
    x = paths["nav"][2]
    more = 0.014
    corners = [Vector((x, fs(60.0), ceiling(60.0))), Vector((x, fs(71.3), ceiling(71.3))), Vector((x, fs(86.0), ceiling(86.0))), SF.side_point(93.0, 63.5, -1, SKIN + 0.008 + more),
               SF.side_point(95.6, 60.3, -1, SKIN + 0.008 + more), SF.side_point(98.4, 56.2, -1, SKIN + 0.012 + more), SF.side_point(102.9, 50.0, -1, SKIN + 0.024 + more),
               SF.side_point(106.0, 46.3, -1, SKIN + 0.024 + more)]
    corners += [SF.section_point(station, 3.1416 - 0.14, SKIN + 0.04 + more) for station in (120.0, 150.0, 180.0, 205.0)]
    foot = Vector((-ST.FIN_COAX_X, fs(212.5), A.fus_top_z(212.5) - SKIN - 0.024))          # below and beside the foot of the fin wiring
    finish("nav", corners + [foot], "AVIONICS.coax_nav", "Navigation antenna cable: from the NAV/COM receiver along the cabin roof and the tailcone to the vertical stabiliser",
           "كابل هوائي الملاحة: من جهاز الملاحة والاتصال بمحاذاة سقف المقصورة ومخروط الذيل إلى المثبت الرأسي", "hose_black", joins="EMPENNAGE.nav_antenna_cable")
    # ---- and its last part, up the fin beside the wiring, through an opening of its own in each rib, to the foot of the antenna
    spar = A.FIN_SPAR
    low, high = bounds(scene["EMPENNAGE.nav_antenna"])
    base = Vector((-0.012, low[1] - 0.006, (low[2] + high[2]) / 2))
    up = [Vector((-ST.FIN_COAX_X, fs(ST.fin_wire_station(water)), wl(water))) for water in (spar[0][1] + 3.0, 83.2)]
    bm = new_bm()
    pipe(bm, [foot] + up + [Vector((-ST.FIN_COAX_X, base.y - 0.04, base.z)), base], COAX, bend=0.02)
    add(ctx, "EMPENNAGE.nav_antenna_cable", bm, "EMPENNAGE", "Navigation antenna cable in the vertical stabiliser", "كابل هوائي الملاحة داخل المثبت الرأسي", "hose_black",
        joins="EMPENNAGE.nav_antenna,AVIONICS.coax_nav", note="Runs up the fin beside the wiring, through an opening in each rib; route representative")


def build_transponder_cable(ctx, scene, backs):
    """Transponder antenna cable: down behind the panel, through the floor, aft under the floor in its own lane."""
    back = backs["XPDR"]["point"]
    antenna = scene["AIRFRAME.transponder_antenna"].matrix_world.translation.copy()
    x, level, first, last = lanes.ALONG["coax_xpdr"]
    y_down = fs(first) - 0.02
    corners = [Vector((back.x + 0.03, back.y, back.z)), Vector((back.x + 0.03, back.y - 0.012, back.z)), Vector((back.x + 0.03, back.y - 0.012, 1.44)), Vector((x, y_down, 1.30)),
               Vector((x, y_down, level + 0.004)), Vector(lanes.point("coax_xpdr", first + 3.0)), Vector(lanes.point("coax_xpdr", last - 1.0)), Vector((antenna.x, antenna.y, level)),
               Vector((antenna.x, antenna.y, A.fus_surface_z((antenna.y / IN) + 40.0, abs(antenna.x)) + SKIN + 0.002))]
    bm = new_bm()
    pipe(bm, corners, COAX, bend=0.02)
    add(ctx, "AVIONICS.coax_transponder", bm, "SYSTEMS", "Transponder antenna cable: from the transponder to the antenna under the fuselage", "كابل هوائي المرسل المجيب: من الجهاز إلى الهوائي تحت جسم الطائرة",
        "hose_black", inside="fuselage", joins="AIRFRAME.transponder_antenna", note="Not described in the POH; route representative")


def build_elt(ctx, scene):
    """Emergency locator transmitter on the right side of the tailcone, behind the rear cabin wall, and the cable to its antenna."""
    centre = Vector((-0.255, fs(118.6), 1.14))
    bm = new_bm()
    box(bm, (0.085, 0.20, 0.075), center=centre)
    box(bm, (0.11, 0.24, 0.004), center=centre - Z * 0.0395)                   # its tray
    rod(bm, centre + Vector((0.02, 0.10, 0.02)), centre + Vector((0.02, 0.112, 0.02)), 0.005, segs=8)
    add(ctx, "AVIONICS.elt", bm, "SYSTEMS", "Emergency locator transmitter (ELT), in the tailcone behind the rear cabin wall", "جهاز تحديد الموقع في حالات الطوارئ (ELT)، في مخروط الذيل خلف الجدار الخلفي للمقصورة",
        "knob_red", smooth=False, optional=True, inside="fuselage", note="Described in the supplements of the handbook when fitted; where it is mounted is representative")
    antenna = scene["ELECTRICAL.elt_antenna"].matrix_world.translation.copy()
    bm = new_bm()
    pipe(bm, [centre + Vector((0.02, 0.112, 0.02)), Vector((-0.20, fs(126.5), 1.33)), Vector((0.04, fs(143.0), 1.50)), Vector((antenna.x, antenna.y - 0.035, antenna.z - 0.045)),
              Vector((antenna.x, antenna.y - 0.003, antenna.z - 0.016))], COAX, bend=0.03)
    add(ctx, "AVIONICS.coax_elt", bm, "SYSTEMS", "ELT antenna cable", "كابل هوائي جهاز ELT", "hose_black", optional=True, inside="fuselage", joins="ELECTRICAL.elt_antenna",
        note="Not described in the POH; route representative")
