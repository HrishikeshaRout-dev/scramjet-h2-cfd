# Design Parameters and Initial Operating Assumptions

Geometry dimensions are millimeters unless stated otherwise. The values below are transcribed from the current source in `geometry/scramjet_geometry.py`; that script is authoritative if this table and the implementation ever differ.

## Geometry

| Parameter | Variable | Current value |
|---|---|---:|
| Duct height | H | 30.0 mm |
| Geometric contraction ratio | CR_geo | 3.0 |
| Body-leading-edge-to-cowl-line height | Hgap = CR_geo H | 90.0 mm |
| Compression angle parameter | delta1 | 12.0 deg |
| Compression-contour starting-angle factor | k0 | 0.3 |
| Turn-back radius | R_t | 300.0 mm |
| Isolator length | L_iso | 150.0 mm |
| Cavities per wall | n_cav | 3 |
| Cavity pitch | pitch | 50.0 mm |
| Cavity/ramp angle | theta | 30.0 deg |
| Cavity radius/depth parameter | cav_r | 8.0 mm |
| Forward lip radius | r_fore | 5.0 mm |
| Aft lip radius | r_aft | 12.0 mm |
| Injector placement fractions | hole_f0, hole_f1 | 0.15, 0.70 |
| Slots per cavity ramp per wall | n_holes | 6 |
| Injector slot width parameter | hole_w | 0.375 mm |
| Injector channel length | hole_len | 1.5 mm |
| Injection angle | hole_ang | 30.0 deg |
| Tail length | L_tail | 100.0 mm |
| Body-wall nozzle half-angle | noz_deg | 6.0 deg |
| Cowl-wall nozzle half-angle | cowl_noz_deg | 6.0 deg |
| Nozzle length | L_noz | 120.0 mm |
| Cowl thickness parameter | cowl_t | 16.0 mm |
| Cowl wedge angle | cowl_wedge_deg | 10.0 deg |
| Concept span | SPAN_WIDTH | 90.0 mm |

The compression offset is `Delta = Hgap - H = 60 mm`. The compression-contour angle varies from approximately 3.6 to 12 degrees. The nozzle diverges symmetrically: each flow-side wall opens by `L_noz tan(6 deg)`, approximately 12.6 mm, giving an exit height of approximately 55.2 mm. The cowl's external underside remains level; its remaining thickness at the nozzle exit is approximately 3.4 mm.

There are 36 injector openings total: six on each of three cavity ramps on each of the two walls. The CFD mesh builder consumes these openings from the geometry script as explicit boundary segments.

## Hydrogen injection

- Fuel: H2
- Stagnation temperature T0,H2: 300 K (user confirmed)
- Stagnation pressure p0,H2: 350 kPa (initial design assumption)
- R_H2 used in preliminary ideal-gas estimates: 4124 J/(kg K)
- gamma_H2 used in preliminary estimates: 1.4
- Target equivalence ratio: approximately 0.3 (design target, not a verified current mesh result)

The earlier choked-flow estimate of 215.5 kg/(m2 s) and equivalence ratio 0.308 was based on the previous injector dimensions and must not be applied to the current 0.375 mm slot geometry without recalculating the effective slot area and boundary-condition mass flow. The OpenFOAM fuel-inlet boundary conditions remain preliminary and should be reconciled with the selected stagnation state and the actual integrated injector area before quantitative runs.

## Flight reference

Nominal Mach 6 at 25 km: T_inf approximately 221.65 K, p_inf approximately 2.511 kPa, U_inf approximately 1791 m/s. A combustor-entry reference of 65 kPa and 620 K was discussed; these are targets/reference values, not simulation results.

## Modeling notes

- 2D slots are continuous in the out-of-plane direction; 3D is needed for finite-span injector effects.
- The current slot width parameter is 0.375 mm. Local mesh refinement and mesh-independence testing are essential.
- Regenerate the CAD references and Gmsh mesh whenever the geometry source changes.
- Validate geometry, mesh, air-only flow, fuel mass flow, and chemistry before interpreting reacting-flow results.
- The repository's current case scripts target OpenCFD OpenFOAM v1912. They have not been ported or validated for OpenFOAM Foundation v9.
