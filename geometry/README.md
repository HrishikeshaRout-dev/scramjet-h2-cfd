The original parametric geometry source is `scramjet_geometry.py`. It defines
the one-sided, wing-integrated 2D concept: the body/wing underside supplies
external compression, the cowl lip marks the internal inlet, the duct contains
an isolator and three cavity stations, and the aft-body and cowl flow-side walls
both expand the nozzle. It also exposes the 36 injector inlet segments consumed
by `mesh/build_gmsh_mesh.py`.

`export_scramjet_planar_concept.py` writes the STEP and PNG reference outputs.
Running `scramjet_geometry.py` directly can also emit DXF and VTK polydata for
visualization; that VTK file is not a CFD volume mesh. The CFD volume mesh is
generated separately with Gmsh.

With CadQuery and Matplotlib installed, regenerate the STEP and preview from
the repository root:

```powershell
python geometry\export_scramjet_planar_concept.py
```

The exporter reads the profile directly from `scramjet_geometry.py`, so it
carries the symmetric nozzle and injector geometry into the extruded 3D
reference assembly. Regenerate these binary outputs after any geometry change;
a previously committed STEP or PNG is not automatically updated when the
Python source changes.

The current concept dimensions are a 30 mm duct, 90 mm body-leading-edge-to-
cowl-line height, 90 mm rectangular module span, 150 mm isolator, three cavity
stations, and a 120 mm nozzle with 6-degree divergence on both the body wall
and cowl wall. The cowl's external underside stays level. The generated profile
places the cowl lip at the compression-contour end and calculates the actual
internal contraction from the contour. These are undergraduate concept
dimensions, not CFD-validated or manufacturing-ready; verify shock behavior,
combustor pressure loss, nozzle expansion, fuel delivery, structures, and
thermal loads before treating them as viable.

The CFD mesh builder extrudes a 1 mm-thick slab for its quasi-2D model; that is
a numerical span, not the 90 mm concept width. Its internal inlet starts at the
cowl lip, so it does not resolve the upstream external flow. The builder
recombines the 2D surface mesh into quads before extrusion; this avoids the
two underdetermined corner cells in the earlier triangular mesh. Use the fresh
cases under `cases/wing_integrated/`; existing legacy cases and their saved
results remain untouched.
