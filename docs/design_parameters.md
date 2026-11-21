# Design Parameters and Initial Operating Assumptions

Geometry dimensions are millimeters unless stated otherwise. Verify each parameter against the original geometry source before treating this as an authoritative implementation.

## Geometry

| Parameter | Variable | Value |
|---|---|---:|
| Duct height | H | 20.0 mm |
| Contraction ratio | CR | 8.0 |
| Compression angle parameter | delta1 | 15.0 deg |
| Geometry parameter | k0 | 0.3 |
| Turn-back radius | R_t | 100.0 mm |
| Isolator length | L_iso | 150.0 mm |
| Cavities per wall | n_cav | 3 |
| Cavity pitch | pitch | 50.0 mm |
| Cavity/ramp angle | theta | 30.0 deg |
| Cavity radius/depth parameter | cav_r | 6.0 mm |
| Forward lip radius | r_fore | 3.0 mm |
| Aft lip radius | r_aft | 8.0 mm |
| Injector placement fractions | hole_f0, hole_f1 | 0.15, 0.70 |
| Slots per ramp | n_holes | 6 |
| Slot width | hole_w | 0.013 mm |
| Slot/channel length | hole_len | 0.3 mm |
| Injection angle | hole_ang | 30.0 deg |
| Tail length | L_tail | 100.0 mm |
| Nozzle angle | noz_deg | 0.0 deg |
| Nozzle length | L_noz | 0.0 mm |

Retained relationships: Hcap = CR*H = 160 mm; Delta = (Hcap-H)/2 = 70 mm. Compression-wall angle varies approximately from 4.5 to 15 degrees. A 100 mm radius turn-back transitions to the 20 mm straight duct. Three cavities per wall and six slots per cavity ramp per wall were specified (36 slots total across both walls).

## Hydrogen injection

- Fuel: H2
- Stagnation temperature T0,H2: 300 K (user confirmed)
- Stagnation pressure p0,H2: 350 kPa (initial design assumption)
- R_H2 used in preliminary ideal-gas estimate: 4124 J/(kg K)
- gamma_H2 used in preliminary estimate: 1.4
- Target equivalence ratio: approximately 0.3

The idealized choked-flow estimate gave approximately 215.5 kg/(m2 s) hydrogen mass flux and equivalence ratio 0.308 for 36 continuous 2D slots. This is a preliminary estimate, not a CFD result or guaranteed injected mass flow.

## Flight reference

Nominal Mach 6 at 25 km: T_inf approximately 221.65 K, p_inf approximately 2.511 kPa, U_inf approximately 1791 m/s. A combustor-entry reference of 65 kPa and 620 K was discussed; these are targets/reference values, not simulation results.

## Modeling notes

- 2D slots are continuous in the out-of-plane direction; 3D is needed for finite-span injector effects.
- A 13 micrometer slot is very small relative to a 20 mm duct; local mesh refinement and mesh-independence testing are essential.
- Validate geometry, mesh, and air-only flow before fuel transport and chemistry.
- Use OpenFOAM Foundation v9 syntax and tutorials specifically.
