"""How far away the automatic camera stands (pure Python, tested outside Blender).

Blender's field of view and orthographic scale apply to the longer side of the picture. A subject
has to fit the shorter side as well, so both are worked out for that side."""
import math


def short_side_half_angle(fov_deg, aspect):
    """Half the field of view across the shorter side of a picture whose field of view across the
    longer side is fov_deg; aspect is width / height."""
    return math.atan(math.tan(math.radians(fov_deg) / 2) * min(aspect, 1 / aspect))


def perspective_distance(radius, fov_deg, aspect, margin=1.0):
    """Distance at which a sphere of `radius` (times margin) just fits the picture."""
    return radius * margin / math.sin(short_side_half_angle(fov_deg, aspect))


def orthographic_scale(radius, aspect, margin=1.0):
    """Orthographic scale (the extent of the longer side) at which a sphere of `radius` (times margin) just fits the picture."""
    return 2 * radius * margin * max(aspect, 1 / aspect)
