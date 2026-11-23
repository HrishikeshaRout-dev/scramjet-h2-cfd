# Mesh generation

`build_gmsh_mesh.py` reads `geometry/scramjet_geometry.py`, whose CFD boundary
aliases begin at the cowl lip and end at the nozzle exit. The generated mesh is
an internal-flow domain; upstream external compression is not included.

Generate the desired profile from the repository root in PowerShell:

```powershell
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_air.msh --profile air
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_detailed.msh
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_combustor.msh --profile combustor
```

The profiles are:

- `air`: seals all injector openings and omits the fuel patch.
- `detailed` (default): retains all 36 injector slots with local refinement.
- `combustor`: retains the 36 slots but uses a smaller refinement region.

All three use quad surface cells extruded to hexahedra. This avoids the
underdetermined corner cells found in the prior triangular-prism mesh. All
profiles passed OpenCFD OpenFOAM v1912 `checkMesh -allTopology -allGeometry`:

| Profile | Cells | Maximum non-orthogonality |
|---|---:|---:|
| `air` | 31,049 | 39.9 degrees |
| `detailed` | 496,272 | 35.9 degrees |
| `combustor` | 35,610 | 34.2 degrees |

Each generated mesh is 1 mm thick in the spanwise direction;
`frontAndBack` must be `empty` for these 2D cases.

Each current-geometry case has an `Allmesh` wrapper that imports its matching
mesh and runs the same full `checkMesh` checks. The shared importer refuses to
overwrite an existing `constant/polyMesh`, protecting saved case data. Mesh
files are generated artifacts and are ignored by Git.
