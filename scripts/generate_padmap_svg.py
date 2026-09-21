#!/usr/bin/env python3
"""Generate a schematic pad-map SVG from references/bzm2-ballmap.csv.

Source of truth: the CSV pad/name/side columns. Layout is schematic (not a fab
drawing): no invented pitch or land size. Numbering walk E→N→W→S then inner C
matches the pinout reference description.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "references" / "bzm2-ballmap.csv"
OUT_PATH = ROOT / "drawings" / "pinout" / "bzm2-padmap.svg"

# Charcoal + teal visual language (site theme tokens)
BG = "#12171c"
PANEL = "#1a2228"
INK = "#d6dde3"
MUTED = "#7a8792"
TEAL = "#2dd4bf"
TEAL_DIM = "#1FA6A0"
LINE = "#3a4650"
CHARCOAL = "#1a1917"

# Function-group fills (legend keys)
GROUP_COLORS = {
    "VDD_HASH": "#1a3a36",
    "VSS": "#2a2f35",
    "VDDIO": "#1e3a4a",
    "VDDINT": "#2a3a1e",
    "RSVD": "#3a2a1e",
    "PINSEL_MUX": "#1e2a3a",
    "CLOCK": "#2a1e3a",
    "JTAG": "#3a1e2a",
    "STRAP": "#2a2a1e",
    "OTHER": "#252a30",
}
GROUP_STROKE = {
    "VDD_HASH": TEAL,
    "VSS": "#556069",
    "VDDIO": "#60a5fa",
    "VDDINT": "#a3e635",
    "RSVD": "#E86A2B",
    "PINSEL_MUX": TEAL_DIM,
    "CLOCK": "#c084fc",
    "JTAG": "#f472b6",
    "STRAP": "#fbbf24",
    "OTHER": LINE,
}

PINSEL_MUX_PADS = {15, 16, 17, 18, 31, 32, 33, 34}
CLOCK_PADS = {20, 29, 38}
JTAG_PADS = {9, 10, 11, 39, 40}
STRAP_PADS = {36}


def classify(pad: dict) -> str:
    n = int(pad["pad"])
    name = pad["name"]
    vd = pad["voltage_domain"]
    if n in PINSEL_MUX_PADS:
        return "PINSEL_MUX"
    if n in CLOCK_PADS:
        return "CLOCK"
    if n in JTAG_PADS:
        return "JTAG"
    if n in STRAP_PADS:
        return "STRAP"
    if name == "VDD" or "VDD_HASH" in vd:
        return "VDD_HASH"
    if name == "VSS":
        return "VSS"
    if name == "VDDIO" or "VDDIO" in vd:
        return "VDDIO"
    if name.startswith("VDDINT"):
        return "VDDINT"
    if name == "RSVD":
        return "RSVD"
    return "OTHER"


def short_label(pad: dict) -> str:
    name = pad["name"]
    # Prefer CSV name; truncate long mux names for pad face
    if len(name) <= 8:
        return name
    aliases = {
        "TRIP_RX_OUT": "TRX_O",
        "TX_RESET_OUT": "TXRO",
        "RESET_TX_IN": "RTXI",
        "RX_TRIP_IN": "RXTI",
        "REFCLKOUT2": "CLKO2",
        "REFCLKOUT1": "CLKO1",
        "REFCLKIN": "CLKIN",
        "RX_TRIP_OUT": "RXTO",
        "RESET_TX_OUT": "RTXO",
        "TX_RESET_IN": "TXRI",
        "TRIP_RX_IN": "TRXI",
        "VDDINT_1": "VINT1",
        "VDDINT_2": "VINT2",
    }
    return aliases.get(name, name[:6])


def load_pads(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 60:
        raise SystemExit(f"expected 60 pads, got {len(rows)}")
    return rows


def peripheral_positions(W: float, H: float, margin: float, pad_w: float, pad_h: float):
    """Schematic positions for pads 1-40: E→N→W→S walk (counterclockwise)."""
    # Usable inner rectangle for pad centers
    left = margin
    right = W - margin
    top = margin + 28  # room for title
    bottom = H - margin - 110  # room for legend/caption
    # East (1-8): right column, bottom→top
    e_count = 8
    n_count = 12
    w_count = 8
    s_count = 12
    pos = {}
    for i in range(e_count):
        pad = i + 1
        y = bottom - (i + 0.5) * (bottom - top) / e_count
        pos[pad] = (right, y)
    for i in range(n_count):
        pad = 9 + i
        x = right - (i + 0.5) * (right - left) / n_count
        pos[pad] = (x, top)
    for i in range(w_count):
        pad = 21 + i
        y = top + (i + 0.5) * (bottom - top) / w_count
        pos[pad] = (left, y)
    for i in range(s_count):
        pad = 29 + i
        x = left + (i + 0.5) * (right - left) / s_count
        pos[pad] = (x, bottom)
    return pos, (left, top, right, bottom)


def inner_positions(bbox, cols=4, rows=5):
    """Pads 41-60 as a 4×5 schematic land field (L→R, T→B). Not a fab pitch."""
    left, top, right, bottom = bbox
    # Shrink toward center
    inset_x = (right - left) * 0.22
    inset_y = (bottom - top) * 0.22
    il, it, ir, ib = left + inset_x, top + inset_y, right - inset_x, bottom - inset_y
    pos = {}
    for i in range(20):
        pad = 41 + i
        c = i % cols
        r = i // cols
        x = il + (c + 0.5) * (ir - il) / cols
        y = it + (r + 0.5) * (ib - it) / rows
        pos[pad] = (x, y)
    return pos


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render(pads: list[dict]) -> str:
    W, H = 920, 780
    pad_w, pad_h = 52, 28
    margin = 70
    by_id = {int(p["pad"]): p for p in pads}
    peri, bbox = peripheral_positions(W, H, margin, pad_w, pad_h)
    inner = inner_positions(bbox)
    positions = {**peri, **inner}

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"',
        '     aria-label="BZM2 60-pad schematic pad map from public ballmap CSV">',
        "  <title>BZM2 package pad map (schematic from public ballmap)</title>",
        "  <desc>Original schematic pad map generated from references/bzm2-ballmap.csv. "
        "Not a fab drawing; no invented pitch or land size. Caption cites pinout reference.</desc>",
        f'  <rect width="{W}" height="{H}" fill="{BG}"/>',
        f'  <rect x="24" y="24" width="{W-48}" height="{H-48}" rx="10" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>',
        f'  <text x="{W/2}" y="52" text-anchor="middle" fill="{MUTED}" font-family="Orbitron,sans-serif" '
        f'font-size="11" font-weight="600" letter-spacing="0.12em">BZM2 · 7.5 × 7 mm FCLGA · 60 LANDS (SCHEMATIC)</text>',
        f'  <text x="{W/2}" y="70" text-anchor="middle" fill="{TEAL}" font-family="Ubuntu,sans-serif" font-size="11">'
        "Top view · numbering E→N→W→S then inner field (CSV side column)</text>",
    ]

    # Package outline box
    left, top, right, bottom = bbox
    parts.append(
        f'  <rect x="{left-36}" y="{top-22}" width="{(right-left)+72}" height="{(bottom-top)+44}" '
        f'rx="8" fill="none" stroke="{LINE}" stroke-width="1.2" stroke-dasharray="6 4"/>'
    )
    for label, x, y in (("E", right + 48, (top + bottom) / 2), ("N", (left + right) / 2, top - 36),
                        ("W", left - 48, (top + bottom) / 2), ("S", (left + right) / 2, bottom + 40)):
        parts.append(
            f'  <text x="{x}" y="{y}" text-anchor="middle" fill="{MUTED}" '
            f'font-family="Orbitron,sans-serif" font-size="10" font-weight="600">{label}</text>'
        )

    for pad_id in range(1, 61):
        p = by_id[pad_id]
        x, y = positions[pad_id]
        grp = classify(p)
        fill = GROUP_COLORS[grp]
        stroke = GROUP_STROKE[grp]
        label = short_label(p)
        # Inner pads slightly smaller
        pw, ph = (pad_w - 6, pad_h - 4) if pad_id >= 41 else (pad_w, pad_h)
        parts.append(f'  <g id="pad-{pad_id}">')
        parts.append(
            f'    <rect x="{x - pw/2:.1f}" y="{y - ph/2:.1f}" width="{pw}" height="{ph}" rx="3" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
        )
        parts.append(
            f'    <text x="{x:.1f}" y="{y - 3:.1f}" text-anchor="middle" fill="{MUTED}" '
            f'font-family="JetBrains Mono,monospace" font-size="8">{pad_id}</text>'
        )
        parts.append(
            f'    <text x="{x:.1f}" y="{y + 10:.1f}" text-anchor="middle" fill="{INK}" '
            f'font-family="JetBrains Mono,monospace" font-size="8" font-weight="600">{esc(label)}</text>'
        )
        parts.append("  </g>")

    # Legend
    legend_y = H - 96
    legend_items = [
        ("VDD_HASH", "VDD / VDD_HASH"),
        ("VSS", "VSS"),
        ("VDDIO", "VDDIO 1.2 V"),
        ("VDDINT", "VDDINT mid-ref"),
        ("RSVD", "RSVD (VDDPLL / VDD_P75)"),
        ("PINSEL_MUX", "PINSEL-mux UART/reset/trip"),
        ("CLOCK", "Clocks"),
        ("JTAG", "JTAG"),
        ("STRAP", "PINSEL strap"),
    ]
    parts.append(f'  <text x="48" y="{legend_y}" fill="{MUTED}" font-family="Orbitron,sans-serif" font-size="9" letter-spacing="0.1em">LEGEND</text>')
    lx = 48
    ly = legend_y + 18
    for i, (key, label) in enumerate(legend_items):
        if i == 5:
            lx = 48
            ly += 22
        parts.append(
            f'  <rect x="{lx}" y="{ly - 10}" width="14" height="14" rx="2" fill="{GROUP_COLORS[key]}" stroke="{GROUP_STROKE[key]}" stroke-width="1"/>'
        )
        parts.append(
            f'  <text x="{lx + 20}" y="{ly + 1}" fill="{INK}" font-family="Ubuntu,sans-serif" font-size="11">{esc(label)}</text>'
        )
        lx += 168 if key != "PINSEL_MUX" else 220

    parts.append(
        f'  <text x="{W/2}" y="{H - 28}" text-anchor="middle" fill="{MUTED}" font-family="Ubuntu,sans-serif" font-size="10">'
        "Caption: schematic pad map from public references/bzm2-ballmap.csv + bzm2-pinout-reference.md — "
        "not a fab drawing; original diagram from public references.</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    # Allow running from a checkout where CSV is at repo-root references/
    csv_path = CSV_PATH
    if not csv_path.exists():
        alt = Path("references/bzm2-ballmap.csv")
        csv_path = alt if alt.exists() else CSV_PATH
    pads = load_pads(csv_path)
    out = OUT_PATH
    if not out.parent.exists():
        out = Path("drawings/pinout/bzm2-padmap.svg")
        out.parent.mkdir(parents=True, exist_ok=True)
    svg = render(pads)
    out.write_text(svg)
    print(f"wrote {out} ({len(pads)} pads)")


if __name__ == "__main__":
    main()
