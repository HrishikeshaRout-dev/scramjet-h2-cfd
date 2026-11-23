# Hydrogen-Fueled Scramjet CFD

Parametric geometry and staged OpenFOAM setup for a one-sided,
wing-integrated scramjet concept.

## Current status

- `geometry/scramjet_geometry.py` is the current profile. It places body-wall
  compression ahead of the cowl lip, followed by an isolator, three cavity
  stations, and a symmetrically diverging nozzle (6 degrees on each wall).
- `mesh/build_gmsh_mesh.py` creates the internal 2D flowpath mesh, extruded
  1 mm in span and treated as `empty`. It does not resolve external inlet
  compression.
- The geometry-current case templates are in `cases/wing_integrated/`.
  Existing cases directly under `cases/` and their saved run data are retained
  unchanged as legacy cases.
- The meshes are design-study inputs, not evidence that the scramjet concept
  is physically validated. Reacting cases still use perfect-gas
  thermodynamics and preliminary fuel-flow assumptions.

## Prepare a case

Generate the mesh matching the case profile (see [case instructions](cases/README.md)).
For example, from PowerShell:

```powershell
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_air.msh --profile air
```

Then in WSL:

```bash
cd /mnt/c/Users/rout/Downloads/scramjet-h2-cfd/cases/wing_integrated/2D_air_flow
bash Allmesh
bash Allrun --dry-run
```

Run a transient only after the dry run and physical-model inputs have been
reviewed. The available WSL installation is OpenCFD OpenFOAM v1912; the case
dictionaries have not been ported or validated for OpenFOAM Foundation v9.

See [design parameters](docs/design_parameters.md), [geometry notes](geometry/README.md),
[mesh instructions](mesh/README.md), and [case notes](cases/README.md).
ParaView is for inspecting meshes and simulation results; it does not run the
solver.
