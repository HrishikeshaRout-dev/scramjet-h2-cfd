#!/usr/bin/env python3
import runpy
import sys
import numpy as np
import gmsh

GEOMETRY_FILE = sys.argv[1] if len(sys.argv) > 1 else "../geometry/scramjet_geometry.py"
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "scramjet2D.msh"
SPAN = 1.0e-3
LC_WALL = 2.5e-4
LC_FUEL = 2.6e-6
FUEL_ELEMENTS = 6
TOL = 1.0e-10

def path_array(value, name):
    points = np.asarray(value, dtype=float)
    if points.ndim != 2 or points.shape[1] < 2:
        raise ValueError(name + " must be an N x 2 coordinate array")
    points = points[:, :2]
    keep = np.ones(len(points), dtype=bool)
    keep[1:] = np.linalg.norm(np.diff(points, axis=0), axis=1) > TOL
    points = points[keep]
    if len(points) < 2:
        raise ValueError(name + " contains fewer than two distinct points")
    return points

def segment_array(value, name):
    segments = np.asarray(value, dtype=float)
    if segments.size == 0:
        return np.empty((0, 2, 2))
    if segments.shape[-2:] != (2, 2):
        raise ValueError(name + " must contain endpoint pairs with shape (..., 2, 2)")
    return segments.reshape((-1, 2, 2))

def point_key(point):
    return tuple(np.round(np.asarray(point, dtype=float)[:2], 11))

def segment_key(segment):
    a, b = point_key(segment[0]), point_key(segment[1])
    return tuple(sorted((a, b)))

def bbox_close(a, b):
    return all(abs(a[i] - b[i]) <= 2.0e-7 for i in range(4))

geometry = runpy.run_path(GEOMETRY_FILE)
required = ("lower", "upper", "inj_lower", "inj_upper")
missing = [name for name in required if name not in geometry]
if missing:
    raise KeyError("Geometry script is missing: " + ", ".join(missing))

lower = path_array(geometry["lower"], "lower")
upper = path_array(geometry["upper"], "upper")
fuel_segments = np.vstack((
    segment_array(geometry["inj_lower"], "inj_lower"),
    segment_array(geometry["inj_upper"], "inj_upper")
))
if len(fuel_segments) != 36:
    raise ValueError("Expected 36 injector openings; found " + str(len(fuel_segments)))
if abs(lower[0, 0] - upper[0, 0]) > 1.0e-7:
    raise ValueError("Lower and upper inlet endpoints do not share the same x-coordinate")
if abs(lower[-1, 0] - upper[-1, 0]) > 1.0e-7:
    raise ValueError("Lower and upper outlet endpoints do not share the same x-coordinate")

lower_keys = [segment_key((lower[i], lower[i + 1])) for i in range(len(lower) - 1)]
upper_keys = [segment_key((upper[i], upper[i + 1])) for i in range(len(upper) - 1)]
fuel_keys = [segment_key(segment) for segment in fuel_segments]
if len(set(fuel_keys)) != len(fuel_keys):
    raise ValueError("Duplicate injector opening segments were found")
if not set(fuel_keys).issubset(set(lower_keys + upper_keys)):
    raise ValueError("At least one injector opening is not an explicit edge in lower or upper")

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.option.setNumber("Mesh.Binary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 1)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)
gmsh.model.add("scramjet2D")

point_tags = {}
curve_data = {}
lower_curves = []
upper_curves = []
lower_path_curves = []
upper_path_curves = []
fuel_curves = []
all_curves = []

def add_point(point):
    key = point_key(point)
    if key not in point_tags:
        point_tags[key] = gmsh.model.geo.addPoint(
            float(point[0]) * 1.0e-3,
            float(point[1]) * 1.0e-3,
            0.0,
            LC_WALL
        )
    return point_tags[key]

def add_path(points, wall_name):
    curves = []
    for i in range(len(points) - 1):
        a = points[i]
        b = points[i + 1]
        tag = gmsh.model.geo.addLine(add_point(a), add_point(b))
        key = segment_key((a, b))
        curve_data[tag] = (key, wall_name, np.array([a, b], dtype=float))
        curves.append(tag)
        all_curves.append(tag)
        if wall_name == "lower":
            lower_path_curves.append(tag)
        else:
            upper_path_curves.append(tag)
        if key in fuel_keys:
            fuel_curves.append(tag)
        elif wall_name == "lower":
            lower_curves.append(tag)
        else:
            upper_curves.append(tag)
    return curves

add_path(lower, "lower")
add_path(upper, "upper")
inlet_curve = gmsh.model.geo.addLine(add_point(upper[0]), add_point(lower[0]))
outlet_curve = gmsh.model.geo.addLine(add_point(lower[-1]), add_point(upper[-1]))
curve_data[inlet_curve] = (None, "airInlet", np.array([upper[0], lower[0]]))
curve_data[outlet_curve] = (None, "outlet", np.array([lower[-1], upper[-1]]))
all_curves.extend((inlet_curve, outlet_curve))

if len(fuel_curves) != 36:
    raise ValueError("Mapped " + str(len(fuel_curves)) + " fuel openings instead of 36")

loop = gmsh.model.geo.addCurveLoop(
    lower_path_curves + [outlet_curve] + [-tag for tag in reversed(upper_path_curves)] + [inlet_curve]
)
surface = gmsh.model.geo.addPlaneSurface([loop])
gmsh.model.geo.synchronize()

for tag in fuel_curves:
    gmsh.model.mesh.setTransfiniteCurve(tag, FUEL_ELEMENTS)
    gmsh.model.mesh.setSize(gmsh.model.getBoundary([(1, tag)], oriented=False, recursive=True), LC_FUEL)

distance = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(distance, "CurvesList", fuel_curves)
gmsh.model.mesh.field.setNumber(distance, "Sampling", 100)
threshold = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(threshold, "InField", distance)
gmsh.model.mesh.field.setNumber(threshold, "SizeMin", LC_FUEL)
gmsh.model.mesh.field.setNumber(threshold, "SizeMax", LC_WALL)
gmsh.model.mesh.field.setNumber(threshold, "DistMin", 5.0e-5)
gmsh.model.mesh.field.setNumber(threshold, "DistMax", 2.0e-3)
gmsh.model.mesh.field.setAsBackgroundMesh(threshold)

extruded = gmsh.model.geo.extrude(
    [(2, surface)],
    0.0,
    0.0,
    SPAN,
    numElements=[1],
    heights=[1.0],
    recombine=True
)
gmsh.model.geo.synchronize()
volumes = [tag for dim, tag in extruded if dim == 3]
if len(volumes) != 1:
    raise RuntimeError("Expected one extruded fluid volume; found " + str(len(volumes)))
volume = volumes[0]

boundary_surfaces = [
    tag for dim, tag in gmsh.model.getBoundary(
        [(3, volume)], combined=False, oriented=False, recursive=False
    ) if dim == 2
]
surface_groups = {
    "airInlet": [],
    "fuelInlets": [],
    "lowerWall": [],
    "upperWall": [],
    "outlet": [],
    "frontAndBack": []
}
curve_groups = {
    "airInlet": [inlet_curve],
    "fuelInlets": fuel_curves,
    "lowerWall": lower_curves,
    "upperWall": upper_curves,
    "outlet": [outlet_curve]
}

curve_boxes = {}
for curve in all_curves:
    box = gmsh.model.getBoundingBox(1, curve)
    curve_boxes[curve] = box

for surf in boundary_surfaces:
    box = gmsh.model.getBoundingBox(2, surf)
    zmin, zmax = box[2], box[5]
    if abs(zmax - zmin) < 2.0e-7 and (
        abs(zmin) < 2.0e-7 or abs(zmin - SPAN) < 2.0e-7
    ):
        surface_groups["frontAndBack"].append(surf)
        continue
    matches = [
        curve for curve, curve_box in curve_boxes.items()
        if bbox_close(box, curve_box)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "Could not uniquely map extruded boundary surface " + str(surf) +
            " to one original boundary curve; matches=" + str(matches)
        )
    curve = matches[0]
    for name, tags in curve_groups.items():
        if curve in tags:
            surface_groups[name].append(surf)
            break

for name, tags in surface_groups.items():
    if not tags:
        raise RuntimeError("Physical surface group is empty: " + name)
    group = gmsh.model.addPhysicalGroup(2, tags)
    gmsh.model.setPhysicalName(2, group, name)

fluid_group = gmsh.model.addPhysicalGroup(3, [volume])
gmsh.model.setPhysicalName(3, fluid_group, "fluidRegion")

gmsh.model.mesh.generate(3)
gmsh.write(OUTPUT_FILE)

print("Wrote:", OUTPUT_FILE)
print("Injector openings:", len(fuel_curves))
print("Boundary surface counts:", {name: len(tags) for name, tags in surface_groups.items()})
print("Run gmshToFoam and checkMesh to validate the OpenFOAM mesh")

gmsh.finalize()
