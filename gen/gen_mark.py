#!/usr/bin/env python3
"""fastverk mark — the canonical, fully-parametric construction.

ONE Spec drives everything: the golden-ratio core, the gaps, the F-arm bevel,
the perpendicular ARROW cut (anchored at a chosen "\\" midpoint), the accent
ARROW region (which inner triangle to fill), and the tertiary fill. Geometry =
shapely (exact CSG). EMISSION goes through brando's marklib (the reusable
layered-SVG / Icon-Composer convention), so the same Spec yields the flat SVG
and the Icon Composer foreground/accent/background layers.

This file is fastverk CONTENT: the geometry + palette. The reusable plumbing
(geometry->SVG path, gradients, rounded-square bg, the Canvas/Layer emit model)
lives in @brando//marklib.

CLI: `gen_mark.py <out-dir> [--prefix P] [--palette NAME] [--variant V]...`
emits every VARIANT's layered set into <out-dir> as `<prefix>_<variant>.<layer>`.
The defaults reproduce the canonical fastverk set (`fastverk_*`, "midnight").
"""
import argparse
import dataclasses
import math
import os
import sys
from dataclasses import dataclass

from shapely.affinity import rotate, translate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from marklib import Canvas, geom_to_path

R3 = math.sqrt(3)

@dataclass
class Spec:
    phi: float = 0.618           # golden-ratio conjugate (inner triangle = phi x outer)
    cut_anchor: str = "mid_lower"  # where the ⊥ cut crosses the "\": mid_lower | mid_full
    cut_out: float = 0.34        # cut extent DOWN-LEFT past the anchor (clipped flush to "\")
    cut_in: float = 0.05         # cut extent UP-RIGHT into the arrowhead (stops short of overshoot)
    arrow_region: str = "lower_inner"  # accent fill: none | lower_inner | full_inner
    arrow_with_cut: bool = True  # union the cut into the accent arrow shape
    tertiary_fill: str = "none"  # tertiary color: none | cut (top-right gap) | interior (all inner black)
    center_y: float = -0.13      # geometry y at canvas center (optical center; bbox center = -0.25)
    canvas: int = 1254
    bg: str = "#15161A"; fg: str = "#ECE7DA"; accent: str = "#F2C46A"; tertiary: str = "#4A565A"
    accent2: str = "#C9852B"     # second arrow gradient stop (bottom); "" = solid accent
    bg_round: float = 0.20

class Mark:
    RD, IN = (-0.5, -0.866), (-0.866, 0.5)        # right-leg dir, interior normal (for the bevel)

    def __init__(self, s: Spec):
        self.s = s
        self.T = 0.5 * (1 - s.phi)                 # band thickness == gap unit
        self.gap = self.T
        self.t_out = self.tri(1.0)
        self.t_in = self.tri(s.phi)
        self.ring = self.t_out.difference(self.t_in)
        self.apex_in = (0.0, -s.phi)
        self.top = s.phi * 0.5                     # inner top edge y (= top-bar bottom)
        self.h = 2 * self.T / R3                   # cut height = leg horizontal width -> base==height
        self.L = self.top - self.h                 # flush line: crossbar top == cut bottom

    # ---- core primitives ----
    @staticmethod
    def tri(r): return Polygon([(r*R3/2, r/2), (-r*R3/2, r/2), (0.0, -r)])
    def inner_x(self, y, side): return side*self.s.phi*R3/2 * (y + self.s.phi) / (self.s.phi*0.5 + self.s.phi)
    def band(self, y_top, x0, x1): return box(x0, y_top - self.T, x1, y_top)

    # ---- the shared "/" bevel line (inner-right edge offset T interior) ----
    def bevel_pt(self): return (self.s.phi*R3/2 - 0.866*self.gap, self.s.phi*0.5 + 0.5*self.gap)
    def bevel_half(self, exterior=False):          # half-plane on one side of the "/" bevel line
        pt = self.bevel_pt(); n = (-self.IN[0], -self.IN[1]) if exterior else self.IN
        a = (pt[0]+8*self.RD[0], pt[1]+8*self.RD[1]); b = (pt[0]-8*self.RD[0], pt[1]-8*self.RD[1])
        return Polygon([a, b, (b[0]+8*n[0], b[1]+8*n[1]), (a[0]+8*n[0], a[1]+8*n[1])])

    # ---- features ----
    def gap_tr(self):                              # the top-right cut: the right-leg segment of
        # height self.h, top flush with the top bar. Its "/" sides ARE the inner & outer
        # "/" edges of the triangle, and h == its horizontal base -> a base==height
        # parallelogram angled 60deg.
        return self.ring.intersection(box(0.0, self.L, 2.0, self.top))
    def top_cut(self):                             # the top-right cut as a fillable shape
        return self.gap_tr()

    def crossbar(self):                            # F small arm / ∀ bar, /-beveled right end, gap = T
        return self.band(self.L, -1.0, 2.0).intersection(self.t_out).intersection(self.bevel_half(exterior=False))

    def cut_point(self):                           # the "\" midpoint the cut passes through
        if self.s.cut_anchor == "mid_full":
            topL = (-self.s.phi*R3/2, self.s.phi*0.5)          # inner top-left vertex
        else:                                                  # mid_lower
            yt = self.L - self.T                               # F-arm bottom
            topL = (self.inner_x(yt, -1), yt)
        return ((topL[0]+self.apex_in[0])/2, (topL[1]+self.apex_in[1])/2)

    def cut(self):                                 # ⊥ slot (width gap) through the chosen midpoint:
        M = self.cut_point()                       # cut_out down-left (to the "\"), cut_in up-right
        s = box(-self.gap/2, -self.s.cut_out, self.gap/2, self.s.cut_in)
        # clip to T_OUT so the down-left end is FLUSH with the "\" (no overhang).
        return translate(rotate(s, -60, origin=(0, 0)), xoff=M[0], yoff=M[1]).intersection(self.t_out)

    def arrow(self):                               # the accent shape (or None)
        if self.s.arrow_region == "none":
            return None
        if self.s.arrow_region == "full_inner":
            region = self.t_in
        else:                                                  # lower_inner: below the F arm
            region = self.t_in.intersection(box(-2, -2, 2, self.L - self.T))
        a = unary_union([region, self.cut()]) if self.s.arrow_with_cut else region
        return a.intersection(self.t_out)          # never overhang the triangle

    def mark(self):                                # the cream F+∀+V+∃ body
        return unary_union([self.ring.difference(self.gap_tr()).difference(self.cut()), self.crossbar()])

    def tertiary_region(self):                     # the tertiary shape (or None)
        if self.s.tertiary_fill == "none":
            return None
        if self.s.tertiary_fill == "interior":     # every black space inside the triangle
            g = self.t_out.difference(self.mark())
            ar = self.arrow()
            return g.difference(ar) if ar is not None else g
        return self.top_cut()                       # "cut": just the top-right parallelogram

    # ---- transform + emit (via brando marklib) ----
    def _tf(self):
        S = self.s.canvas; scale = 0.66*S / (R3); cy = self.s.center_y
        return lambda x, y: (S/2 + x*scale, S/2 - (y - cy)*scale)

    def _d(self, g):                               # geometry -> SVG path (marklib)
        return geom_to_path(g, self._tf())

    def _canvas(self):                             # assemble the marklib Canvas for this Spec
        c = Canvas(size=self.s.canvas, tf=self._tf(), bg_round=self.s.bg_round)
        c.add_background(self.s.bg)
        tr = self.tertiary_region()
        if tr is not None:
            c.add_layer("tint", tr, self.s.tertiary)
        ar = self.arrow()
        if ar is not None:
            grad = (self.s.accent, self.s.accent2) if self.s.accent2 else None
            c.add_layer("arrow", ar, self.s.accent, gradient=grad)
        c.add_layer("mark", self.mark(), self.s.fg)
        return c

    def canvas(self):
        return self._canvas()

    def _layer(self, path, g, fill):               # one transparent-bg shape layer
        Canvas(size=self.s.canvas, tf=self._tf()).write_layer(
            path, _named_layer(g, fill))

    def render(self, path):                        # composite (tertiary UNDER, accent, fg OVER)
        self._canvas().render(path)

    def emit(self, base):                          # canonical LAYERED vectors + composite
        self._canvas().emit(base)

# brando's Layer (constructed lazily to keep the import surface small).
def _named_layer(geom, fill):
    from marklib import Layer
    return Layer(name="layer", geom=geom, fill=fill)

# The canonical family — both members share the construction; the accent/field
# colors invert between them.
VARIANTS = {
    "full":  Spec(cut_anchor="mid_full",  arrow_region="full_inner",  tertiary_fill="cut"),
    "lower": Spec(cut_anchor="mid_lower", arrow_region="lower_inner", tertiary_fill="interior"),
}

# ─── palettes ────────────────────────────────────────────────────────────────
#
# The geometry is locked; the COLOURS are Spec parameters, so a palette is a
# named override set rather than a second construction. Each entry gives the
# dark (canonical) overrides and the light-mode ones — the same two-mode axis
# `MODES` used to carry on its own, now keyed by palette so a brand property can
# pick a ramp without forking the generator.
#
# WHY THE NON-CANONICAL RAMPS EXIST. In the `full` variant the cream mark CROSSES
# the accent field (the F arm) and rings it on every side, so cream|accent is a
# real edge, not an abstraction. Measured (WCAG 2.1 relative luminance),
# cream #ECE7DA against the accent, and the accent against the ink ground:
#
#   palette     accent    cream|accent   accent|ink   reads as
#   midnight    #F2C46A       1.32:1       11.09:1    canonical; the arm dissolves
#   deep        #B5781A       3.00:1        4.86:1    amber, deepened one step
#   copper      #B05D15       3.85:1        3.81:1    warmer/redder, balanced
#   bronze      #96560D       4.68:1        3.13:1    burnt; interior wins
#
# THE TWO COLUMNS MOVE IN OPPOSITE DIRECTIONS BY CONSTRUCTION. An accent
# sandwiched between cream (L .800) and ink (L .008) can reach at most
# sqrt(14.64) = 3.83:1 on BOTH edges at once; 4.5:1 on both is unreachable, not
# merely unchosen. `copper` sits on that optimum, `deep` favours the silhouette
# (accent against ink), `bronze` the interior (cream against accent).
#
# The light-mode accent is chosen separately because there the accent sits ON
# cream rather than beside it: the canonical #E0A33E is 1.79:1 on the cream
# ground, which is why the light mark reads as a bare outline.
PALETTES = {
    # Canonical fastverk. Unchanged — this is what //gen:svgs still emits.
    "midnight": {
        "dark": {},
        "light": {"bg": "#ECE7DA", "fg": "#15161A", "accent": "#E0A33E", "accent2": "#4A565A"},
    },
    # One step down the same hue (~36°). #B5781A is already a fastverk token —
    # it is the accent //office's docx template has always used.
    "deep": {
        "dark": {"accent": "#B5781A", "accent2": "#845712"},
        "light": {"bg": "#ECE7DA", "fg": "#15161A", "accent": "#B5781A", "accent2": "#4A565A"},
    },
    # Hue shifted to ~28° and set at the balance point: equal contrast on both
    # edges of the sandwich. The largest identity move of the three.
    "copper": {
        "dark": {"accent": "#B05D15", "accent2": "#7F430F"},
        "light": {"bg": "#ECE7DA", "fg": "#15161A", "accent": "#B05D15", "accent2": "#4A565A"},
    },
    # Deep enough that cream clears WCAG AA (4.5:1) against the accent, at the
    # cost of the accent's pop against the ink ground.
    "bronze": {
        "dark": {"accent": "#96560D", "accent2": "#6B410B"},
        "light": {"bg": "#ECE7DA", "fg": "#15161A", "accent": "#96560D", "accent2": "#4A565A"},
    },
}
# NOTE the light rows above use the SAME accent as their dark row, which
# "midnight" does not: canonical light lightens the accent to #E0A33E, and that
# lands at 1.79:1 against the cream ground — the light mark's amber all but
# disappears into its own field. Holding one accent per palette fixes that and
# removes a value that had no reason to differ.

# Color modes of the CANONICAL palette. Kept as its own name because raster.py
# and the brandbook diagrams have always spelled it this way; it is now a view of
# PALETTES rather than a second place the colours are written down.
# ⚠ THE CANONICAL PALETTE IS THE DEFAULT, AND IT MUST STAY EQUAL TO
# FASTVERK_PALETTE IN gen/palette.bzl. `brand_icons` is a macro over the
# rasterizer and accepts no palette argument, so //icons:icon_set can only get
# the brand's colours by inheriting this default. Change one without the other
# and the icon and the lockup's mark silently disagree.
CANONICAL_PALETTE = "deep"

MODES = {mode: PALETTES[CANONICAL_PALETTE][mode] for mode in ("dark", "light")}

def spec_for(variant, palette=None, mode="dark"):
    palette = palette or CANONICAL_PALETTE
    """The Spec for one (geometry variant, palette, mode) — the only place the
    two axes are combined."""
    return dataclasses.replace(VARIANTS[variant], **PALETTES[palette][mode])

# Every layer file emit() can produce, per variant (for Bazel `outs` declaration).
LAYERS = ["svg", "bg.svg", "mark.svg", "arrow.svg", "tint.svg"]

def parse_args(argv=None, prog=None):
    """`<out-dir> [--prefix P] [--palette NAME] [--variant V]...` — shared with
    raster.py so both halves of the pipeline take the same flags."""
    ap = argparse.ArgumentParser(prog=prog)
    ap.add_argument("out_dir", nargs="?", default=".")
    ap.add_argument("--prefix", default="fastverk",
                    help="output filename prefix (default: fastverk)")
    ap.add_argument("--palette", default=CANONICAL_PALETTE, choices=sorted(PALETTES),
                    help="named colour set (default: midnight, the canonical one)")
    ap.add_argument("--variant", action="append", default=[], choices=sorted(VARIANTS),
                    help="geometry variant; repeatable, default all")
    args = ap.parse_args(argv)
    args.variants = args.variant or list(VARIANTS)
    return args

def main(argv=None):
    a = parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    for name in a.variants:
        base = f"{a.prefix}_{name}"
        Mark(spec_for(name, a.palette)).emit(os.path.join(a.out_dir, base))
        print(f"emit {base} [{a.palette}] -> {a.out_dir}")

if __name__ == "__main__":
    main()
