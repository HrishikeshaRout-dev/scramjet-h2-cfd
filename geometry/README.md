The original parametric geometry source is `scramjet_geometry.py`. It defines
the one-sided, wing-integrated 2D concept: the body/wing underside supplies
external compression, a cowl lip marks the internal inlet, the duct contains
an isolator and three cavity stations, and only the aft body expands the
nozzle. It also exposes the 36 injector inlet segments consumed by
`mesh/build_gmsh_mesh.py`.

`export_scramjet_planar_concept.py` writes the current STEP and PNG reference
outputs. Running `scramjet_geometry.py` directly can also emit DXF and VTK
polydata for visualization; that VTK file is not a CFD volume mesh. The CFD
volume mesh is generated separately with Gmsh.

With CadQuery and Matplotlib installed, regenerate the current STEP and
preview using:

```powershell
python geometry\export_scramjet_planar_concept.py
```

`export_scramjet_planar_concept.py` exports `scramjet_planar_reference.step`
as an extruded wing/body, cowl, and reference flowpath, plus a 2D side-view
PNG. The current user-supplied reference dimensions are a 30 mm duct, 90 mm
body-leading-edge-to-cowl-line height, 90 mm rectangular module span, 150 mm
isolator, three cavity stations, and a 120 mm nozzle that diverges symmetrically (6 degrees on
both the body wall and the cowl wall; the cowl's outer underside stays level). The generated profile places the cowl lip at x=389.4 mm, gives a
36.6 mm lip-plane height (1.219:1 internal contraction), and reaches x=949 mm
at the nozzle exit. The external compression contour and actual internal
contraction are calculated by the geometry script. These are undergraduate concept
dimensions, not CFD-validated or manufacturing-ready; verify shock behavior,
combustor pressure loss, nozzle expansion, fuel delivery, structures, and
thermal loads before treating them as viable.

The CFD mesh builder extrudes a 1 mm-thick slab for its quasi-2D model; that
is a numerical span, not the 90 mm concept width. Its internal inlet starts at
the cowl lip, so it does not resolve the upstream external flow. The builder
recombines the 2D surface mesh into quads before extrusion; this removes the
two underdetermined corner cells in the earlier triangular mesh. Use the fresh
cases under `cases/wing_integrated/`; existing cases and their saved results
remain untouched.
