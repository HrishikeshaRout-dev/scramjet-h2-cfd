# OpenFOAM cases

Use the fresh cases under `cases/wing_integrated/` for the one-sided
wing-integrated profile in `geometry/scramjet_geometry.py`. The older cases
directly under `cases/` contain meshes and saved results from an earlier
geometry; they are preserved and must not be used as if they matched this
profile.

The current mesh begins at the cowl lip and ends at the nozzle exit. It
resolves the internal duct only, not the upstream external compression flow.
Its 1 mm spanwise extrusion is a numerical thickness for a 2D `empty` case,
not the concept's 90 mm module width. Boundary patches are `airInlet`,
`fuelInlets` (detailed meshes only), `lowerWall` (cowl), `upperWall`
(body), `outlet`, and `frontAndBack` (`empty`). The symmetric 6-degree
nozzle changes the outlet geometry but does not change these patch names, so
the existing field dictionaries remain geometrically addressable.

## Generate the meshes

Run these commands from the repository root in PowerShell. Generate the mesh
needed by the case you intend to use, using the updated geometry source:

```powershell
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_air.msh --profile air
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_detailed.msh
py -3.13 .\mesh\build_gmsh_mesh.py .\geometry\scramjet_geometry.py .\mesh\scramjet2D_wing_combustor.msh --profile combustor
```

In WSL, run `Allmesh` in the matching case, then use `Allrun --dry-run`
before any solver run:

| Case | Mesh profile | Solver |
|---|---|---|
| `wing_integrated/2D_air_flow/` | `air` | `rhoCentralFoam` |
| `wing_integrated/2D_air_thermally_perfect/` | `air` | `rhoCentralFoam` |
| `wing_integrated/2D_cold_flow/` | `detailed` | `rhoCentralFoam` |
| `wing_integrated/2D_hydrogen_combustion/` | `detailed` | `rhoReactingFoam` |
| `wing_integrated/2D_hydrogen_quasi_steady/` | `combustor` | `rhoReactingFoam` |

Earlier mesh counts, `checkMesh` results, and dry-run results documented for
the previous geometry do not automatically validate the symmetric-nozzle
revision. Regenerate the meshes in fresh case directories, run
`checkMesh -allTopology -allGeometry`, and then run `Allrun --dry-run` for
each case before attempting a transient simulation. The `Allmesh` script
refuses to overwrite an existing `constant/polyMesh`; create a fresh case
directory rather than replacing a mesh beneath saved results.

The quasi-steady case starts with air composition (O2 0.2329, N2 0.7671,
H2 0). The reacting dictionaries still use perfect-gas thermodynamics and
preliminary fuel-flow assumptions. Reconcile the imposed fuel mass flow and
thermodynamic state with the current injector geometry, and validate the EOS,
chemistry, timestep, and mesh sensitivity before interpreting a simulation
physically.

The repository's current case scripts target OpenCFD OpenFOAM v1912. They have
not been ported or validated for OpenFOAM Foundation v9.
