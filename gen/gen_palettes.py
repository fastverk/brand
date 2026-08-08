#!/usr/bin/env python3
"""Palette previews + the measured contrast report behind them.

The geometry is locked; the palette is a `Spec` parameter. This renders every
VARIANT in every named palette (`gen_mark.PALETTES`) as a composite SVG and a
512px PNG, and writes `palette_contrast.txt` — the WCAG 2.1 ratio of every edge
the mark actually has, so a palette is chosen from numbers rather than from
looking at it on one monitor.

It reads `gen_mark.PALETTES` instead of carrying its own list: the previous
version kept a second table of candidate colours here, which is the same
duplication the variant/layer flags exist to remove.

THE EDGES THAT MATTER, and why the accent cannot win both:

  fg|accent    the cream mark crosses and rings the accent field (`full`)
  fg|accent2   same edge, at the bottom of the arrow gradient
  accent|bg    the mark's silhouette — the cut slot reaches the ink ground
  fg|bg        the mark against the ground (never in question: 14.64:1)

`fg|accent` and `accent|bg` are the SAME degree of freedom pulling opposite ways.
With cream at L .800 and ink at L .008 the best an accent between them can do is
sqrt(14.64) = 3.83:1 on both at once, so 4.5:1 on both is unreachable rather than
merely unchosen. `palette_contrast.txt` prints the ceiling next to the numbers.

CLI: gen_palettes.py <out-dir> [--size N]
"""
import argparse
import os

from gen_mark import PALETTES, VARIANTS, Mark, spec_for
from raster import raster

# Kept from the pre-0.3 explorer: the HUE candidates the canonical palette was
# chosen from. Not a contrast study — a hue study, and still the right starting
# point if the brand ever moves off amber. Rendered only with --hues.
HUE_CANDIDATES = [
    ("midnight", "#15161A", "#ECE7DA", "#E0A33E", "#4A565A"),  # amber + muted slate
    ("logic",    "#0E1116", "#E8EEF4", "#4C8BF5", "#3E4564"),  # blue + muted indigo (∀∃/Lean)
    ("ember",    "#1B1410", "#F3E8D6", "#E8743A", "#6E5A44"),  # orange + muted umber
    ("forest",   "#10140E", "#E9E9D6", "#5BB873", "#555C44"),  # green + muted olive
    ("crimson",  "#141110", "#EFE7DC", "#D6452F", "#574E4A"),  # red + muted taupe
    ("mono",     "#17181C", "#ECE7DA", "#B9B0A0", "#555049"),  # warm monochrome
]


# ── WCAG 2.1 (stdlib only; brando's marklib.palette gates a SKIN, which is a
# Theme's role pairs — these are a MARK's geometric edges, which no Theme names).
def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexs):
    h = hexs.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


# (label, fg role, bg role, floor, what the edge is). The floors are WCAG 1.4.11
# (3:1, non-text boundaries) — none of these edges is text. `tertiary` carries no
# floor: the top-right cut is DESIGNED to recede, and holding it to 3:1 would be
# the "gate that fails everything" mistake.
EDGES = (
    ("fg|accent ", "fg", "accent", 3.0, "the mark crossing/ringing the accent field"),
    ("fg|accent2", "fg", "accent2", 3.0, "same edge at the gradient's far stop"),
    ("accent|bg ", "accent", "bg", 3.0, "the mark's silhouette against the ground"),
    ("fg|bg     ", "fg", "bg", 4.5, "the mark against the ground"),
    ("tert|bg   ", "tertiary", "bg", None, "the top-right cut (deliberately recessive)"),
)


def report(fh):
    fh.write("fastverk mark — measured edge contrast (WCAG 2.1 relative luminance)\n")
    fh.write("floors: 4.5:1 text (AA) / 3.0:1 non-text boundaries (1.4.11)\n\n")
    for pname in PALETTES:
        for mode in ("dark", "light"):
            s = spec_for("full", pname, mode)
            ceiling = ratio(s.fg, s.bg) ** 0.5
            fh.write("%-9s %-5s  bg %s  fg %s  accent %s -> %s\n"
                     % (pname, mode, s.bg, s.fg, s.accent, s.accent2 or "(solid)"))
            fh.write("          ceiling for an accent between fg and bg: %.2f:1\n" % ceiling)
            for label, fg_role, bg_role, floor, what in EDGES:
                fg, bg = getattr(s, fg_role), getattr(s, bg_role)
                if not fg or not bg:
                    continue
                r = ratio(fg, bg)
                verdict = "-- " if floor is None else ("ok " if r >= floor else "UNDER")
                fh.write("          %s %s|%s %6.2f:1 (floor %s) %s %s\n"
                         % (label, fg, bg, r,
                            "n/a" if floor is None else "%.1f" % floor, verdict, what))
            fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", nargs="?", default=".")
    ap.add_argument("--size", type=int, default=512, help="preview PNG edge, px")
    ap.add_argument("--hues", action="store_true",
                    help="also render the legacy HUE_CANDIDATES study")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    for pname in PALETTES:
        for vname in VARIANTS:
            for mode in ("dark", "light"):
                spec = spec_for(vname, pname, mode)
                stem = os.path.join(a.out_dir, f"palette_{pname}_{vname}_{mode}")
                Mark(spec).render(stem + ".svg")
                raster(spec, a.size).save(stem + ".png")
                print(f"palette_{pname}_{vname}_{mode}")

    with open(os.path.join(a.out_dir, "palette_contrast.txt"), "w") as fh:
        report(fh)
    print("palette_contrast.txt")

    if a.hues:
        import dataclasses
        for vname, base in VARIANTS.items():
            for pname, bg, fg, accent, tert in HUE_CANDIDATES:
                spec = dataclasses.replace(base, bg=bg, fg=fg, accent=accent, tertiary=tert)
                Mark(spec).render(os.path.join(a.out_dir, f"hue_{pname}_{vname}.svg"))
                print(f"hue_{pname}_{vname}")


if __name__ == "__main__":
    main()
