# 2D wing-integrated air flow — OpenFOAM Foundation v9

This is a Foundation-v9-targeted cold-flow case using the current wing-integrated geometry. It is separate from the older OpenCFD-v1912 cases.

## Model and initial conditions

- Solver: `rhoCentralFoam`
- Flow: 2D, compressible, laminar, calorically perfect air
- Freestream initialization: Mach 6 design-point velocity, 1791 m/s
- Static inlet state: 221.65 K and 2511 Pa (25 km reference atmosphere)
- Walls: no-slip and adiabatic (zero normal temperature gradient)
- Fuel injection and chemistry: intentionally disabled for this baseline

The geometry/mesh represents the internal duct beginning at the cowl lip. It does not include the upstream external compression flow. The 1 mm extrusion is the numerical thickness for the 2D empty front/back patches, not the concept's 90 mm physical module width.

## Run in Linux / WSL

First source the OpenFOAM Foundation v9 environment. The exact path depends on the installation; common locations include `/opt/openfoam9/etc/bashrc` and `/usr/lib/openfoam/openfoam9/etc/bashrc`.

```bash
source /path/to/openfoam9/etc/bashrc
foamVersion
```

Confirm that `foamVersion` reports 9. Then from the repository root:

```bash
sudo apt update
sudo apt install -y python3-numpy python3-gmsh gmsh
python3 -c "import gmsh, numpy"
cd cases/wing_integrated/2D_air_flow_Foundation9
bash Allmesh
bash Allrun
```

If your distribution does not provide the Python gmsh module as `python3-gmsh`, install the Gmsh Python module into the Python environment used by `python3`.

The mesh script writes `mesh/scramjet2D_wing_air.msh` at the repository root. `Allmesh` imports it, converts the front/back patch to `empty`, and runs `checkMesh`. It refuses to overwrite an existing `constant/polyMesh`.

## ParaView

After the solver has written time directories, open `case.foam` in ParaView. Select the OpenFOAM reader, apply it, and choose the fields to display. Useful initial fields are `p`, `T`, `U`, and derived Mach number (where supported by the reader).

The `.foam` file is only a reader marker. It is not simulation data: run `Allmesh` and `Allrun` first.

## Validation status and next steps

These dictionaries are a first Foundation-v9 port of the existing air-only setup. They have not been executed with your local OpenFOAM installation in this environment. The first local run must be treated as a compatibility and mesh-validation test, not as a validated scramjet prediction.

Before interpreting results, inspect the `checkMesh` report, solver stability, mass conservation, pressure/temperature fields, and wall resolution. The current wall mesh spacing may need refinement for a resolved laminar boundary layer. Do not enable hydrogen chemistry until the air-only case runs reliably.
