#!/usr/bin/env python3
"""fastverk mark — the canonical, fully-parametric construction.

ONE Spec drives everything: the golden-ratio core, the gaps, the F-arm bevel,
the perpendicular ARROW cut (anchored at a chosen "\" midpoint), the accent
ARROW region (which inner triangle to fill), and the tertiary fill. Geometry =
shapely (exact CSG); emission = svgwrite, as canonical LAYERS
(bg / tint / arrow / mark) + a composite — so the same Spec yields the flat SVG
and the Icon Composer foreground/accent/background layers.

CLI: `gen_mark.py <out-dir>` emits every VARIANT's layered set into <out-dir>.
"""
import math
import os
import sys
from dataclasses import dataclass
import svgwrite
from shapely.geometry import Polygon, box
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

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

    # ---- transform + emit ----
    def _tf(self):
        S = self.s.canvas; scale = 0.66*S / (R3); cy = self.s.center_y
        return lambda x, y: (S/2 + x*scale, S/2 - (y - cy)*scale)
    def _d(self, g):
        tf = self._tf()
        if g.geom_type in ("MultiPolygon", "GeometryCollection"):
            polys = [x for x in g.geoms if x.geom_type == "Polygon"]
        else:
            polys = [g]
        out = []
        for p in polys:
            for r in [p.exterior, *p.interiors]:
                out.append("M " + " L ".join(f"{a:.2f},{b:.2f}" for a, b in (tf(x, y) for x, y in r.coords)) + " Z")
        return " ".join(out)

    def render(self, path):                        # composite (tertiary UNDER, accent, fg OVER)
        S = self.s.canvas; d = svgwrite.Drawing(path, size=(S, S), viewBox=f"0 0 {S} {S}")
        d.add(d.rect(insert=(0, 0), size=(S, S), rx=self.s.bg_round*S, ry=self.s.bg_round*S, fill=self.s.bg))
        tr = self.tertiary_region()
        if tr is not None:
            d.add(d.path(d=self._d(tr), fill=self.s.tertiary)).update({"fill-rule": "evenodd"})
        ar = self.arrow()
        if ar is not None:
            fill = self.s.accent
            if self.s.accent2:  # vertical linear gradient over the arrow (accent -> accent2)
                g = d.linearGradient(start=(0, 0), end=(0, 1), id="arrowgrad")
                g.add_stop_color(0, self.s.accent)
                g.add_stop_color(1, self.s.accent2)
                d.defs.add(g)
                fill = "url(#arrowgrad)"
            d.add(d.path(d=self._d(ar), fill=fill)).update({"fill-rule": "evenodd"})
        d.add(d.path(d=self._d(self.mark()), fill=self.s.fg)).update({"fill-rule": "evenodd"})
        d.save()

    def _layer(self, path, g, fill):               # one transparent-bg shape layer
        S = self.s.canvas; d = svgwrite.Drawing(path, size=(S, S), viewBox=f"0 0 {S} {S}")
        d.add(d.path(d=self._d(g), fill=fill)).update({"fill-rule": "evenodd"}); d.save()

    def emit(self, base):                          # canonical LAYERED vectors + composite
        S = self.s.canvas                          # bg / tint / arrow / mark = Icon Composer layers
        bg = svgwrite.Drawing(base + ".bg.svg", size=(S, S), viewBox=f"0 0 {S} {S}")
        bg.add(bg.rect(insert=(0, 0), size=(S, S), rx=self.s.bg_round*S, ry=self.s.bg_round*S, fill=self.s.bg)); bg.save()
        self._layer(base + ".mark.svg", self.mark(), self.s.fg)
        ar = self.arrow()
        if ar is not None: self._layer(base + ".arrow.svg", ar, self.s.accent)
        tr = self.tertiary_region()
        if tr is not None: self._layer(base + ".tint.svg", tr, self.s.tertiary)
        self.render(base + ".svg")                 # composite for web / README / tray

# The canonical family — both members share the construction; the accent/field
# colors invert between them.
VARIANTS = {
    "full":  Spec(cut_anchor="mid_full",  arrow_region="full_inner",  tertiary_fill="cut"),
    "lower": Spec(cut_anchor="mid_lower", arrow_region="lower_inner", tertiary_fill="interior"),
}

# Color modes (palette + arrow gradient). dark = mono-amber, light = amber-slate.
MODES = {
    "dark":  {},  # the Spec defaults: mono-amber gradient on midnight
    "light": {"bg": "#ECE7DA", "fg": "#15161A", "accent": "#E0A33E", "accent2": "#4A565A"},
}

# Every layer file emit() can produce, per variant (for Bazel `outs` declaration).
LAYERS = ["svg", "bg.svg", "mark.svg", "arrow.svg", "tint.svg"]

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in VARIANTS.items():
        Mark(spec).emit(os.path.join(out_dir, f"fastverk_{name}"))
        print(f"emit fastverk_{name} -> {out_dir}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
