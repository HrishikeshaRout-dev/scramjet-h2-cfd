#!/usr/bin/env python3
"""Export an extruded 3D concept from the one-sided wing-integrated profile."""

from pathlib import Path
import sys
from math import hypot

import cadquery as cq

GEOMETRY_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GEOMETRY_DIR))
import scramjet_geometry as profile

STEP_OUTPUT = GEOMETRY_DIR / "scramjet_planar_reference.step"
PREVIEW_OUTPUT = GEOMETRY_DIR / "scramjet_planar_reference.png"
CONCEPT_WIDTH = profile.SPAN_WIDTH


def extrude_profile(points: list[tuple[float, float]], name: str) -> cq.Shape:
    cleaned = []
    for x, y in points:
        if not cleaned or hypot(x - cleaned[-1][0], y - cleaned[-1][1]) > 1e-7:
            cleaned.append((x, y))
    if hypot(cleaned[-1][0] - cleaned[0][0], cleaned[-1][1] - cleaned[0][1]) <= 1e-7:
        cleaned.pop()
    shape = (
        cq.Workplane("XY")
        .polyline(cleaned)
        .close()
        .extrude(CONCEPT_WIDTH)
        .translate((0, 0, -CONCEPT_WIDTH / 2))
        .val()
    )
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise RuntimeError(f"{name} did not produce one valid solid")
    return shape


def make_assembly() -> cq.Assembly:
    components = (
        ("Wing_body", profile.parts["BODY_WALL"], cq.Color(0.66, 0.7, 0.76)),
        ("Cowl", profile.parts["COWL"], cq.Color(0.38, 0.52, 0.7)),
        ("Internal_flowpath", profile.parts["FLOWPATH"], cq.Color(0.3, 0.75, 0.9, 0.28)),
    )
    assembly = cq.Assembly(name="Planar scramjet preliminary reference concept")
    for name, section, color in components:
        solid = extrude_profile(section, name)
        assembly.add(solid, name=name, color=color)
        print(
            f"{name}: valid={solid.isValid()}, volume={solid.Volume():.3f} "
            f"mm^3"
        )
    return assembly


def export_side_view() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    figure, axis = plt.subplots(figsize=(16, 5))
    axis.add_patch(
        Polygon(profile.parts["FLOWPATH"], closed=True, facecolor="#9edaf0", alpha=0.75)
    )
    axis.add_patch(
        Polygon(profile.parts["BODY_WALL"], closed=True, facecolor="#aab3bf", edgecolor="#283747")
    )
    axis.add_patch(
        Polygon(profile.parts["COWL"], closed=True, facecolor="#657e9a", edgecolor="#283747")
    )
    for start, end in profile.inj_all:
        axis.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color="#d33d32",
            linewidth=1.6,
        )

    axis.annotate("body compression / leading edge", (profile.x_lip * 0.35, 18), fontsize=10)
    axis.annotate("cowl lip", (profile.x_lip + 3, 5), fontsize=10)
    axis.annotate("isolator", (profile.x_first - 70, 0), fontsize=10)
    axis.annotate("cavity combustor / injectors", (profile.x_first + 30, -10), fontsize=10)
    axis.annotate("aft-body nozzle", (profile.x_comb_end + 35, 22), fontsize=10)
    axis.set_aspect("equal", adjustable="datalim")
    axis.set_xlabel("Axial direction (mm)")
    axis.set_ylabel("Profile height (mm)")
    axis.set_title("WING-INTEGRATED ONE-SIDED SCRAMJET — PRELIMINARY / NOT VALIDATED")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    figure.savefig(PREVIEW_OUTPUT, dpi=170)
    plt.close(figure)
    print(f"Concept side-view written to {PREVIEW_OUTPUT}")


def main() -> None:
    assembly = make_assembly()
    assembly.save(str(STEP_OUTPUT), exportType="STEP")
    if not STEP_OUTPUT.is_file() or STEP_OUTPUT.stat().st_size == 0:
        raise RuntimeError(f"STEP export did not create {STEP_OUTPUT}")
    print(f"STEP concept written to {STEP_OUTPUT} ({STEP_OUTPUT.stat().st_size} bytes)")
    export_side_view()


if __name__ == "__main__":
    main()
