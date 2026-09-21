#!/usr/bin/env python3
"""Generate the BZM2 package pad map SVG from the public ballmap CSV.

Source of truth: references/bzm2-ballmap.csv. Nothing here is hand-placed --
side membership, ordering and grouping all come from the CSV, so the drawing
cannot drift from the data.

    python scripts/generate_padmap_svg.py          # writes the SVG + reference footprint
    python scripts/generate_padmap_svg.py --check  # fail if either committed file is stale

Geometry: the CSV fixes side membership and numbering order; the land pattern
dimensions come from the geometry block below, corroborated against the public
open-source footprint shipped by bitaxeorg. Drawn to scale. See the Assumptions
And Tolerances table in references/bzm2-pinout-reference.md before using the
figures -- they are nominal, with no published tolerance band.
"""
from __future__ import annotations

import argparse
import csv
import html
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "references" / "bzm2-ballmap.csv"
SVG_PATH = ROOT / "drawings" / "pinout" / "bzm2-padmap.svg"
MOD_PATH = ROOT / "footprints" / "BZM2.pretty" / "BZM2-FCLGA60.kicad_mod"

# Functional groups, keyed by the CSV's own fields. Order sets legend order.
GROUPS = [
    ("VDD_HASH", "#e8623c", "Core hash supply (VDD)"),
    ("VSS", "#6b7785", "Ground (VSS)"),
    ("VDDIO", "#2fb3a8", "IO rail, 1.2 V"),
    ("VDDINT", "#9a7bd0", "Stack midpoint reference - not a load rail"),
    ("PINSEL_MUX", "#3d8bd4", "PINSEL-muxed UART / reset / trip"),
    ("CLOCK", "#5fbf6a", "Reference clocks"),
    ("JTAG", "#d46fa8", "JTAG"),
    ("STRAP", "#e3b341", "Orientation strap"),
    ("RSVD", "#8a8069", "Reserved - see notes"),
]
GROUP_COLOR = {k: c for k, c, _ in GROUPS}

# Inner land field, read off the 5x4 serpentine in the public numbering:
# 41-45 ->, 50-46 <-, 51-55 ->, 60-56 <-. Rendered top row first.
INNER_ROWS = [
    [56, 57, 58, 59, 60],
    [55, 54, 53, 52, 51],
    [46, 47, 48, 49, 50],
    [45, 44, 43, 42, 41],
]


def classify(row: dict) -> str:
    """Assign a pad to a legend group using only CSV fields."""
    name, dom = row["name"], row["voltage_domain"]
    if row["pinsel0_function"] not in ("-", "") and name != "PINSEL":
        return "PINSEL_MUX"
    if name == "PINSEL":
        return "STRAP"
    if name.startswith("REFCLK"):
        return "CLOCK"
    if name in ("TDO", "TDI", "TCK", "TMS", "TRST"):
        return "JTAG"
    if name == "RSVD":
        return "RSVD"
    if name.startswith("VDDINT"):
        return "VDDINT"
    if name == "VDDIO":
        return "VDDIO"
    if name == "VSS":
        return "VSS"
    if "VDD_HASH" in dom:
        return "VDD_HASH"
    raise SystemExit(f"unclassified pad {row['pad']} ({name}) -- update classify()")


def load() -> dict[int, dict]:
    with CSV_PATH.open(encoding="utf-8") as fh:
        pads = {int(r["pad"]): r for r in csv.DictReader(fh)}
    if len(pads) != 60:
        raise SystemExit(f"expected 60 pads, CSV has {len(pads)}")
    for n, r in pads.items():
        r["group"] = classify(r)
    return pads


def validate(pads: dict[int, dict]) -> list[str]:
    """Re-derive the documented walk from the CSV rather than trusting it."""
    notes = []
    want = [("E", 1, 8), ("N", 9, 20), ("W", 21, 28), ("S", 29, 40), ("C", 41, 60)]
    for side, lo, hi in want:
        got = [n for n in sorted(pads) if pads[n]["side"] == side]
        if got != list(range(lo, hi + 1)):
            raise SystemExit(f"side {side} is not contiguous {lo}-{hi}: {got}")
        notes.append(f"{side}={hi - lo + 1}")
    flat = [n for row in INNER_ROWS for n in row]
    if sorted(flat) != list(range(41, 61)):
        raise SystemExit("INNER_ROWS does not cover pads 41-60 exactly once")
    return notes


# --------------------------------------------------------------- geometry
# PCB LAND PATTERN, in mm, centred on the land-field centroid. Corroborated
# against the public open-source footprint shipped by bitaxeorg in both
# bitaxeBonanza and bitaxeBIRDS (bitaxe.pretty/bzm2.kicad_mod): the two are
# geometrically identical, and the SatoshiStarter copy is a pure translation
# of them (single offset, zero land-size differences).
#
# This is the LAND PATTERN, not the package body. Land extent works out to
# 8.100 x 7.600 mm including land widths, against a 7.5 x 7 mm package body --
# a land pattern is normally larger than the part it seats.
PITCH = 0.615                 # peripheral pitch, uniform on both axes
COL_X = 3.6975                # E / W column land-centre offset from centre
ROW_Y = 3.3325                # N / S row land-centre offset from centre
COL_SPAN = 2.1525             # outermost E / W land centre, +/- from centre
# Exact symmetric value: 11 * 0.615 = 6.765 span, so +/-3.3825. The public
# footprints store -3.382 / +3.383, which is the same number rounded to 3 dp;
# the 1 um asymmetry that introduces is below any fab tolerance but shows up
# under rotation, so the exact value is used here.
ROW_X0, ROW_X1 = -3.3825, 3.3825   # first / last N / S land centre
LAND_COL = (0.705, 0.305)     # E / W lands: w x h
LAND_ROW = (0.305, 0.935)     # N / S lands: w x h
LAND_INNER = (0.805, 0.805)   # inner field lands
INNER_X = (-2.416, -1.208, 0.0, 1.208, 2.416)
INNER_Y = (1.965, 0.655, -0.655, -1.965)   # top row first, Y up
BODY_W, BODY_H = 7.5, 7.0     # package body, from bzm2-pinout-reference.md

# ---------------------------------------------------------------- rendering
W, H = 1180, 1530
BG = "#171a1f"
FG = "#e7ecf2"
DIM = "#98a2b0"
EDGE = "#39414d"
FONT = "Ubuntu, 'DejaVu Sans', 'Segoe UI', Helvetica, Arial, sans-serif"
HEAD = "Orbitron, Ubuntu, 'DejaVu Sans', Helvetica, Arial, sans-serif"

PAD = 24          # land square side
GAP_X = 44        # spacing along the 12-pad rows (drawing units, NOT mm)
GAP_Y = 44        # spacing along the 8-pad columns (drawing units, NOT mm)
BODY_X, BODY_Y = 348, 275   # top-left land centre; body is centred in W


def esc(s: str) -> str:
    return html.escape(s, quote=True)


_PLACED: dict[tuple[int, int], int] = {}


def land(out, x, y, n, row, w, h):
    """Place one land. x/y/w/h are already in px."""
    key = (round(x), round(y))
    if key in _PLACED:
        raise SystemExit(
            f"pad {n} collides with pad {_PLACED[key]} at {key} -- "
            "peripheral rows and columns must not share a position"
        )
    _PLACED[key] = n
    col = GROUP_COLOR[row["group"]]
    out.append(
        f'<rect x="{x - w/2:.1f}" y="{y - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" '
        f'fill="{col}" fill-opacity="0.88" stroke="{BG}" stroke-width="1"/>'
    )
    fs = 10 if min(w, h) >= 20 else 8
    out.append(
        f'<text x="{x:.1f}" y="{y + fs*0.36:.1f}" font-family="{FONT}" font-size="{fs}" '
        f'font-weight="700" fill="#12151a" text-anchor="middle">{n}</text>'
    )


def label(out, x, y, text, anchor, *, size=11, fill=FG, weight="500", rotate=None):
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
    out.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{tr}>{esc(text)}</text>'
    )


def pad_label(row: dict) -> str:
    """PINSEL-muxed pads carry both functions; everything else its name."""
    a, b = row["pinsel0_function"], row["pinsel1_function"]
    if a not in ("-", "") and row["name"] != "PINSEL":
        return f"{a} / {b}"
    return row["name"]


def render(pads: dict[int, dict]) -> str:
    o: list[str] = []
    o.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" font-family="{FONT}" role="img" '
        f'aria-label="BZM2 package pad map, 60 lands, generated from the public ballmap CSV">'
    )
    o.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    # ---- titles
    o.append(
        f'<text x="40" y="52" font-family="{HEAD}" font-size="23" font-weight="700" '
        f'fill="{FG}" letter-spacing="1.2">BZM2 PACKAGE PAD MAP</text>'
    )
    label(o, 40, 76, "60 lands - 40 peripheral + 20 inner field - top view", "start",
          size=13, fill=DIM)
    label(o, 40, 96, "Generated from references/bzm2-ballmap.csv", "start", size=11, fill=DIM)

    # ---- true-proportion placement, mm -> px, Y flipped (mm is Y-up)
    SCALE = 80.0
    CX, CY = W / 2.0, 560.0

    def PX(mm):
        return CX + mm * SCALE

    def PY(mm):
        return CY - mm * SCALE

    lc_w, lc_h = LAND_COL[0] * SCALE, LAND_COL[1] * SCALE
    lr_w, lr_h = LAND_ROW[0] * SCALE, LAND_ROW[1] * SCALE
    li_w, li_h = LAND_INNER[0] * SCALE, LAND_INNER[1] * SCALE

    # ---- package body outline (7.5 x 7.0 mm), drawn to scale inside the lands
    o.append(
        f'<rect x="{PX(-BODY_W/2):.1f}" y="{PY(BODY_H/2):.1f}" '
        f'width="{BODY_W*SCALE:.1f}" height="{BODY_H*SCALE:.1f}" rx="8" '
        f'fill="#1e232a" stroke="{EDGE}" stroke-width="2"/>'
    )
    label(o, PX(0), PY(BODY_H/2) - 12, "package body 7.5 x 7.0 mm", "middle", size=10, fill=DIM)

    # ---- peripheral walk, counterclockwise E -> N -> W -> S
    ys = [-COL_SPAN + i * PITCH for i in range(8)]          # bottom -> top
    xs = [ROW_X0 + i * PITCH for i in range(12)]            # left -> right

    for i, n in enumerate(range(1, 9)):                      # E, right column, bottom -> top
        x, y = PX(COL_X), PY(ys[i])
        land(o, x, y, n, pads[n], lc_w, lc_h)
        label(o, x + lc_w / 2 + 10, y + 4, pad_label(pads[n]), "start", size=11)
    for i, n in enumerate(range(9, 21)):                     # N, top row, right -> left
        x, y = PX(xs[11 - i]), PY(ROW_Y)
        land(o, x, y, n, pads[n], lr_w, lr_h)
        label(o, x + 4, y - lr_h / 2 - 10, pad_label(pads[n]), "start", size=10, rotate=-62)
    for i, n in enumerate(range(21, 29)):                    # W, left column, top -> bottom
        x, y = PX(-COL_X), PY(ys[7 - i])
        land(o, x, y, n, pads[n], lc_w, lc_h)
        label(o, x - lc_w / 2 - 10, y + 4, pad_label(pads[n]), "end", size=11)
    for i, n in enumerate(range(29, 41)):                    # S, bottom row, left -> right
        x, y = PX(xs[i]), PY(-ROW_Y)
        land(o, x, y, n, pads[n], lr_w, lr_h)
        label(o, x - 4, y + lr_h / 2 + 14, pad_label(pads[n]), "end", size=10, rotate=-62)

    # ---- inner land field, 5 x 4
    for r, rowvals in enumerate(INNER_ROWS):
        for c, n in enumerate(rowvals):
            land(o, PX(INNER_X[c]), PY(INNER_Y[r]), n, pads[n], li_w, li_h)
    label(o, PX(0), PY(INNER_Y[-1]) + li_h / 2 + 18, "inner land field (41-60)",
          "middle", size=10, fill=DIM)

    # ---- pin-1 marker
    o.append(
        f'<circle cx="{PX(COL_X) + 34:.1f}" cy="{PY(-COL_SPAN):.1f}" r="5" '
        f'fill="none" stroke="{DIM}" stroke-width="1.5"/>'
    )

    # ---- legend
    lx, ly = 40, 1030
    label(o, lx, ly, "LEGEND", "start", size=12, fill=FG, weight="700")
    counts: dict[str, int] = {}
    for n in pads:
        counts[pads[n]["group"]] = counts.get(pads[n]["group"], 0) + 1
    yy = ly + 22
    for key, col, desc in GROUPS:
        cnt = counts.get(key, 0)
        o.append(f'<rect x="{lx}" y="{yy - 10}" width="13" height="13" rx="2.5" fill="{col}" fill-opacity="0.85"/>')
        label(o, lx + 21, yy + 1, f"{desc}  ({cnt})", "start", size=11)
        yy += 21

    # ---- notes / gaps
    nx = 600
    ny = 1030
    label(o, nx, ny, "NOTES AND OPEN GAPS", "start", size=12, fill=FG, weight="700")
    notes = [
        ("Drawn to scale from the public open-source land pattern.", True),
        ("Peripheral pitch 0.615 mm, uniform on both axes. Lands: E/W", False),
        ("0.705 x 0.305, N/S 0.305 x 0.935, inner 0.805 x 0.805 mm.", False),
        ("Inner field pitch 1.208 mm (X) x 1.310 mm (Y).", False),
        ("", False),
        ("This is the PCB LAND PATTERN, not the package body. Land extent is", False),
        ("8.100 x 7.600 mm including land widths, around a 7.5 x 7 mm body.", False),
        ("", False),
        ("Package envelope 7.5 x 7 mm FCLGA, exposed die, per the pinout reference.", False),
        ("", False),
        ("Numbering walks counterclockwise: E(8) -> N(12) -> W(8) -> S(12),", False),
        ("then the inner field (41-60). Verified contiguous against the CSV.", False),
        ("", False),
        ("The 40 peripheral lands share no corner: the 12-land N and S rows span", False),
        ("the full width and the 8-land E and W columns sit between them.", False),
        ("", False),
        ("PINSEL-muxed pads show both functions as PINSEL=0 / PINSEL=1.", False),
        ("Pad 36 straps the orientation: float or high = 1, tie to VSS = 0.", False),
        ("", False),
        ("VDDIO appears on pads 19 and 30. On-die connectivity between them", False),
        ("is not documented; reference designs connect both.", False),
        ("", False),
        ("Pads 13 and 37 are RSVD in the vendor table. Reference designs use", False),
        ("them as the PLL decoupling point and a 0.75 V backup rail.", False),
    ]
    yy = ny + 22
    for text, strong in notes:
        if text:
            label(o, nx, yy, text, "start", size=11,
                  fill=FG if strong else DIM, weight="700" if strong else "400")
        yy += 17

    # ---- caption
    label(o, 40, H - 34,
          "Original diagram generated from public references. Pad assignments: references/bzm2-ballmap.csv. "
          "Land geometry corroborated against", "start", size=10, fill=DIM)
    label(o, 40, H - 18,
          "the public open-source footprint in bitaxeorg/bitaxeBonanza and bitaxeorg/bitaxeBIRDS. No vendor package art was traced.", "start", size=10, fill=DIM)

    o.append("</svg>")
    return "\n".join(o)



# ------------------------------------------------------- KiCad footprint
def emit_footprint(pads: dict[int, dict]) -> str:
    """Reference land pattern, generated from the same CSV + geometry.

    Pads carry their names and functions from the CSV, which neither existing
    open-source footprint does, so this is a derivative rather than a copy.
    """
    NL = chr(10)
    TAB = chr(9)
    L = []
    L.append('(footprint "BZM2-FCLGA60"')
    L.append(TAB + '(version 20240108)')
    L.append(TAB + '(generator "bzm2-hwref/scripts/generate_padmap_svg.py")')
    L.append(TAB + '(layer "F.Cu")')
    L.append(TAB + '(descr "Intel Blockscale BZM2 - 60-land FCLGA, 7.5 x 7 mm exposed die. '
             'Land pattern generated from references/bzm2-ballmap.csv; geometry corroborated '
             'against the public open-source footprint in bitaxeorg/bitaxeBonanza and '
             'bitaxeorg/bitaxeBIRDS. Original derivative, not a copy.")')
    L.append(TAB + '(tags "bzm2 blockscale fclga asic")')
    L.append(TAB + '(attr smd)')
    cw, ch = BODY_W / 2 + 0.25, BODY_H / 2 + 0.25
    L.append(TAB + f'(fp_rect (start {-cw} {-ch}) (end {cw} {ch}) '
             f'(stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))')
    L.append(TAB + f'(fp_rect (start {-BODY_W/2} {-BODY_H/2}) (end {BODY_W/2} {BODY_H/2}) '
             f'(stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))')
    L.append(TAB + f'(fp_circle (center {-BODY_W/2 - 0.5} {BODY_H/2 + 0.5}) '
             f'(end {-BODY_W/2 - 0.3} {BODY_H/2 + 0.5}) (stroke (width 0.2) (type solid)) '
             f'(fill solid) (layer "F.SilkS"))')

    def place(n, x, y, w, h):
        r = pads[n]
        ptype = "power_in" if r["group"] in ("VDD_HASH", "VSS", "VDDIO") else "bidirectional"
        # KiCad Y is down; the geometry block above is Y up
        L.append(TAB + f'(pad "{n}" smd rect (at {x:.4f} {-y:.4f}) (size {w} {h}) '
                 f'(layers "F.Cu" "F.Paste" "F.Mask")')
        L.append(TAB * 2 + f'(pinfunction "{r["name"]}")')
        L.append(TAB * 2 + f'(pintype "{ptype}")')
        L.append(TAB + ')')

    ys = [-COL_SPAN + i * PITCH for i in range(8)]
    xs = [ROW_X0 + i * PITCH for i in range(12)]
    for i, n in enumerate(range(1, 9)):
        place(n, COL_X, ys[i], *LAND_COL)
    for i, n in enumerate(range(9, 21)):
        place(n, xs[11 - i], ROW_Y, *LAND_ROW)
    for i, n in enumerate(range(21, 29)):
        place(n, -COL_X, ys[7 - i], *LAND_COL)
    for i, n in enumerate(range(29, 41)):
        place(n, xs[i], -ROW_Y, *LAND_ROW)
    for r, rowvals in enumerate(INNER_ROWS):
        for c, n in enumerate(rowvals):
            place(n, INNER_X[c], INNER_Y[r], *LAND_INNER)
    L.append(')')
    return NL.join(L) + NL


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the committed SVG differs from a fresh render")
    args = ap.parse_args()

    pads = load()
    sides = validate(pads)
    svg = render(pads)

    if args.check:
        if not SVG_PATH.exists():
            print(f"{SVG_PATH} missing", file=sys.stderr)
            return 1
        if MOD_PATH.exists() and MOD_PATH.read_text(encoding="utf-8") != emit_footprint(pads):
            print(f"{MOD_PATH} is stale -- rerun scripts/generate_padmap_svg.py", file=sys.stderr)
            return 1
        if SVG_PATH.read_text(encoding="utf-8") != svg:
            print(f"{SVG_PATH} is stale -- rerun scripts/generate_padmap_svg.py", file=sys.stderr)
            return 1
        print(f"{SVG_PATH.name} up to date ({', '.join(sides)})")
        return 0

    SVG_PATH.write_text(svg, encoding="utf-8")
    MOD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MOD_PATH.write_text(emit_footprint(pads), encoding="utf-8")
    print(f"wrote {MOD_PATH.relative_to(ROOT)}")
    counts: dict[str, int] = {}
    for n in pads:
        counts[pads[n]["group"]] = counts.get(pads[n]["group"], 0) + 1
    print(f"wrote {SVG_PATH.relative_to(ROOT)}  ({', '.join(sides)})")
    for k, _, _ in GROUPS:
        print(f"    {k:<11} {counts.get(k, 0):>2}")
    print(f"    {'TOTAL':<11} {sum(counts.values()):>2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
