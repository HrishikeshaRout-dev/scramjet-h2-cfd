import numpy as np

d2r = np.radians

# ============ WING-INTEGRATED, ONE-SIDED SCRAMJET CONCEPT (mm, deg) ============
# Undergraduate concept study. Not CFD-validated. Reference flight: Mach 6 at 25 km.
# The body wall does the compression; the cowl lip sits at the compression contour end.
# The nozzle diverges symmetrically: the aft-body ramp and the cowl flow-side wall open at the same
# half-angle, while the cowl's outer underside stays level. Planar, one-sided layout, not axisymmetric.
H = 30.0
CR_geo = 3.0
SPAN_WIDTH = 90.0
delta1 = 12.0
k0 = 0.3
R_t = 300.0
L_iso = 150.0
n_cav = 3
pitch = 50.0
theta = 30.0
cav_r = 8.0
r_fore = 5.0
r_aft = 12.0
hole_f0, hole_f1 = 0.15, 0.70
n_holes = 6
hole_w = 0.375
hole_len = 1.5
hole_ang = 30.0
L_tail = 100.0
noz_deg = 6.0  # nozzle half-angle, applied to both the body wall and the cowl wall
L_noz = 120.0
cowl_noz_deg = noz_deg  # symmetric divergence
cowl_wedge_deg = 10.0
cowl_t = cav_r + 8.0
le_deg = 5.0
le_r = 0.5

Hgap = CR_geo * H
Delta = Hgap - H
y0 = -H / 2 - Delta

# Body-wall compression contour; the cowl lip is at the contour end.
xi = np.linspace(0, 1, 801)
g = np.tan(d2r(k0 * delta1 + (delta1 - k0 * delta1) * xi))
Ig = np.trapezoid(g, xi)
Lc = (Delta - R_t * (1 - np.cos(d2r(delta1)))) / Ig
x = xi * Lc
y = Lc * np.concatenate([[0], np.cumsum(0.5 * (g[1:] + g[:-1]) * np.diff(xi))])
body = [(a, y0 + b) for a, b in zip(x, y)]
i_lip = len(body) - 1
x_lip = body[i_lip][0]
Pc = np.array(body[-1])
cen = Pc + R_t * np.array([np.sin(d2r(delta1)), -np.cos(d2r(delta1))])
for a in np.linspace(90 + delta1, 90, 25)[1:]:
    body.append(tuple(cen + R_t * np.array([np.cos(d2r(a)), np.sin(d2r(a))])))
x_t = body[-1][0]
CR_int = (H / 2 - body[i_lip][1]) / H

# Semicircular cavities with tangent ramps and injector passages.
inj_inlet = []


def cavity(x0):
    r, th = cav_r, d2r(theta)
    cx = x0 + r
    dx = np.sqrt(r * r + 2 * r * r_fore)
    xf = cx - dx
    pts = [(xf, 0.0)]
    psi = np.degrees(np.arctan2(r_fore, dx))
    for a in np.linspace(90, psi, 12)[1:]:
        pts.append((xf + r_fore * np.cos(d2r(a)), -r_fore + r_fore * np.sin(d2r(a))))
    phi0 = 180 + np.degrees(np.arctan2(r_fore, dx))
    for p in np.linspace(phi0, 270 + theta, 40)[1:]:
        pts.append((cx + r * np.cos(d2r(p)), r * np.sin(d2r(p))))
    A = np.array([cx + r * np.sin(th), -r * np.cos(th)])
    L = r * (1 + 1 / np.sin(th))
    B = np.array([x0 + L, 0.0])
    u = (B - A) / np.linalg.norm(B - A)
    m = np.array([-u[1], u[0]])
    al = d2r(hole_ang)
    dv = np.cos(al) * u + np.sin(al) * m
    h = hole_w / (2 * np.sin(al))
    ramp_len = np.linalg.norm(B - A)
    Tl = r_aft * np.tan(th / 2)
    assert Tl < (1 - hole_f1) * ramp_len - 0.5, "aft fillet too large for hole row"
    for f in np.linspace(hole_f0, hole_f1, n_holes):
        P = A + f * (B - A)
        I1, I2 = P - h * u, P + h * u
        o1 = (I1 - P) - np.dot(I1 - P, dv) * dv
        Pb = P - hole_len * dv
        B1, B2 = Pb + o1, Pb - o1
        pts += [tuple(I1), tuple(B1), tuple(B2), tuple(I2)]
        inj_inlet.append((tuple(B1), tuple(B2)))
    cf2 = np.array([B[0] + Tl, -r_aft])
    for a in np.linspace(90 + theta, 90, 12):
        pts.append((cf2[0] + r_aft * np.cos(d2r(a)), cf2[1] + r_aft * np.sin(d2r(a))))
    return pts, L + Tl


x_first = x_t + L_iso
cav = []
for i in range(n_cav):
    p, L_cav = cavity(x_first + i * pitch)
    cav += [(a, -H / 2 + z) for a, z in p]
x_comb_end = x_first + (n_cav - 1) * pitch + L_cav + L_tail
x_exit = x_comb_end + L_noz
dy = L_noz * np.tan(d2r(noz_deg))
dyc = L_noz * np.tan(d2r(cowl_noz_deg))
assert cowl_t > dyc + 1.0, "cowl too thin for this divergence"
body += cav + [(x_comb_end, -H / 2)]
if L_noz > 0:
    body.append((x_exit, -H / 2 - dy))
y_exit_body = body[-1][1]

# Internal cowl with mirrored cavity features; its wall diverges in the nozzle like the body wall.
cowl = [(x_lip, H / 2), (x_t, H / 2)] + [(a, -b) for a, b in cav] + [
    (x_comb_end, H / 2),
    (x_exit, H / 2 + dyc),
]
inj_body = [((a[0], -H / 2 + a[1]), (b[0], -H / 2 + b[1])) for a, b in inj_inlet]
inj_cowl = [((a[0], -a[1]), (b[0], -b[1])) for a, b in inj_body]

# Solid outlines: wing/body on the upper side after the coordinate flip.
ybot = y0 - 10.0
a0 = d2r(k0 * delta1)
le = d2r(le_deg)
psi = a0 + le
x_w_le = 10.0 / np.tan(le)
P0 = np.array(body[0])
if le_r > 0:
    t = le_r / np.tan(psi / 2)
    d = le_r / np.sin(psi / 2)
    b = (a0 - le) / 2
    C = P0 + d * np.array([np.cos(b), np.sin(b)])
    Tb = P0 + t * np.array([np.cos(a0), np.sin(a0)])
    nose = [
        tuple(C + le_r * np.array([np.cos(a), np.sin(a)]))
        for a in np.linspace(-le - np.pi / 2, a0 + np.pi / 2 - 2 * np.pi, 30)
    ]
    body_solid = nose + [p for p in body if p[0] > Tb[0]] + [(x_exit, ybot), (x_w_le, ybot)]
else:
    body_solid = body + [(x_exit, ybot), (x_w_le, ybot)]
x_w = x_lip + cowl_t / np.tan(d2r(cowl_wedge_deg))
cowl_solid = cowl + [(x_exit, H / 2 + cowl_t), (x_w, H / 2 + cowl_t)]
flow = cowl + list(reversed(body[i_lip:]))

# Flip so the body wall (wing underside) is on top in the 2D view.
fl = lambda pts: [(a, -b) for a, b in pts]
parts = {"BODY_WALL": fl(body_solid), "COWL": fl(cowl_solid), "FLOWPATH": fl(flow)}
body_line = fl(body)
cowl_line = fl(cowl)
inj_body = [(fl([a, b])[0], fl([a, b])[1]) for a, b in inj_body]
inj_cowl = [(fl([a, b])[0], fl([a, b])[1]) for a, b in inj_cowl]
inj_all = inj_body + inj_cowl

# Mesh-generator compatibility: flow-boundary paths begin at the cowl lip,
# excluding the external body compression surface from the internal CFD domain.
lower = cowl_line
upper = body_line[i_lip:]
inj_lower = inj_cowl
inj_upper = inj_body

print(f"Body LE-to-cowl-line height={Hgap:.1f}, throat={H:.1f}, span={SPAN_WIDTH:.1f}")
print(
    f"Compression contour length={Lc:.1f}, cowl lip at x={x_lip:.1f}, "
    f"lip-plane height={H / 2 - body[i_lip][1]:.1f}, "
    f"internal contraction at lip={CR_int:.3f}:1"
)
print(
    f"Inlet end x={x_t:.1f}, isolator={L_iso:.1f}, combustor start x={x_first:.1f}, "
    f"cavity L/D={L_cav / cav_r:.2f}, nozzle exit height={H + dy + dyc:.1f}, "
    f"overall length={x_exit:.1f}"
)

if __name__ == "__main__":
    import ezdxf

    doc = ezdxf.new("R2010")
    doc.units = 4
    msp = doc.modelspace()
    for (name, poly), col in zip(parts.items(), (7, 5, 3)):
        doc.layers.add(name, color=col)
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": name})
    doc.layers.add("INJ_INLET", color=1)
    for a, b in inj_all:
        msp.add_line(a, b, dxfattribs={"layer": "INJ_INLET"})
    doc.saveas("scramjet_wing_v6_2d.dxf")

    pts, lines, pid = [], [], []
    items = [(k, [p + [p[0]]]) for k, p in enumerate(parts.values())] + [
        (3, [[a, b] for a, b in inj_all])
    ]
    for k, segs in items:
        for segment in segs:
            i0 = len(pts)
            pts += [(a / 1000, b / 1000, 0.0) for a, b in segment]
            lines.append(list(range(i0, i0 + len(segment))))
            pid.append(k)
    with open("scramjet_wing_v6_2d.vtk", "w") as fh:
        fh.write(
            "# vtk DataFile Version 3.0\n"
            "wing scramjet 2D (m); part_id 0=body 1=cowl 2=flowpath 3=injector inlets\n"
            "ASCII\nDATASET POLYDATA\n"
        )
        fh.write(
            f"POINTS {len(pts)} float\n"
            + "\n".join(f"{p[0]:.7f} {p[1]:.7f} 0" for p in pts)
            + "\n"
        )
        fh.write(f"LINES {len(lines)} {sum(len(line) + 1 for line in lines)}\n")
        for line in lines:
            fh.write(f"{len(line)} " + " ".join(map(str, line)) + "\n")
        fh.write(
            f"CELL_DATA {len(lines)}\nSCALARS part_id int 1\nLOOKUP_TABLE default\n"
            + "\n".join(map(str, pid))
            + "\n"
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(4, 1, figsize=(13, 17))
    for axis in ax:
        for (_, poly), color in zip(parts.items(), ("k", "tab:blue", "tab:green")):
            points = np.array(poly + [poly[0]])
            axis.plot(points[:, 0], points[:, 1], color, lw=1)
        for start, end in inj_all:
            axis.plot(*zip(start, end), "r", lw=2.5)
        axis.set_aspect("equal")
        axis.grid(alpha=0.3)
    ax[0].set_title("Full geometry (mm): body wall / wing underside on top, flow left to right")
    ax[1].set_xlim(-5, 45)
    ax[1].set_ylim(-y0 - 8, -y0 + 8)
    ax[1].set_title("Wing leading edge")
    ax[2].set_xlim(x_lip - 120, x_t + 80)
    ax[2].set_ylim(-H, H)
    ax[2].set_title("Cowl lip and end of compression")
    ax[3].set_xlim(x_first - 20, x_comb_end + 5)
    ax[3].set_ylim(-H, H)
    ax[3].set_title("Cavity section")
    plt.tight_layout()
    plt.savefig("scramjet_wing_v6_2d_preview.png", dpi=110)
