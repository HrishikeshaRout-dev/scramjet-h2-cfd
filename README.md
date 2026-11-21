# Hydrogen-Fueled Scramjet CFD

OpenFOAM Foundation v9 project for developing and validating a hydrogen-fueled scramjet internal-flow simulation.

## Status
This is an initial documentation scaffold. The original geometry Python source, Gmsh mesh generator, OpenFOAM case dictionaries, and chemistry mechanism have not yet been committed. No CFD results are claimed.

## Workflow
1. Restore the original parametric geometry.
2. Generate and validate a 2D Gmsh mesh.
3. Run air-only compressible cold flow.
4. Add hydrogen species transport and injection.
5. Add finite-rate hydrogen-air chemistry.
6. Extend the validated setup to 3D.

## Structure
- `geometry/`: original parametric geometry source
- `mesh/`: Gmsh tools and mesh checks
- `cases/`: staged OpenFOAM cases
- `chemistry/`: hydrogen-air mechanism and data
- `postProcessing/`: analysis tools
- `docs/`: design assumptions and workflow

See [design parameters](docs/design_parameters.md). Use OpenFOAM Foundation v9-specific solver dictionaries and tutorials. The VTK geometry export is visualization data, not a CFD volume mesh. The initial 2D injector slots represent spanwise-continuous slots, not finite-span 3D injectors.
