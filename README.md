# brand

The fastverk visual identity, generated from one parametric source.

The mark plays off **F**, **V**, the down-triangle **∀** (universal quantifier)
and the horizontal arms **∃/E** — fitting, since Lean (and its quantifiers) does
a lot of the work. It's a deliberate, methodical construction on the unit circle
and the golden ratio (φ = 0.618), not a hand-traced drawing.

## The construction (one `Spec`)

`gen/gen_mark.py` builds the mark by exact boolean CSG (shapely):

1. Equilateral triangle on the unit circle, apex down → `T_OUT`.
2. Copy scaled to circumradius φ → `T_IN`. `RING = T_OUT − T_IN`.
3. Band thickness `T = ½(1−φ)` is the one gap/stroke unit.
4. `gap_tr` — the top-right cut: the right-leg segment whose height equals its
   own base (the leg's horizontal width `2T/√3`) → a 60° parallelogram; its "/"
   sides are the triangle's inner & outer "/". The flush line `L` derives from
   it (crossbar-top == cut-bottom, cut-top == top-bar-bottom).
5. `crossbar` — the F arm / ∀ bar / ∃ stroke, with a "/" beveled right end.
6. `cut` — a ⊥ arrow cut through a chosen "\" midpoint (`mid_lower` | `mid_full`).
7. `arrow` — the accent region (`lower_inner` | `full_inner`), unioned with the cut.
8. `tertiary` — `cut` (top-right gap) or `interior` (all inner negative space).

### The family

Both members share the construction; the accent/field colors invert:

| variant | accent | tertiary | reads as |
|---------|--------|----------|----------|
| `full`  | full inner triangle | top-right cut | F+V on an accent field (heraldic; large sizes) |
| `lower` | contained arrow under the F arm | whole interior | accent arrow on a muted field (mark-like; small sizes) |

## Build

Everything is hermetic — the generator runs in-build (shapely/svgwrite wheels):

```sh
bazel build //gen:svgs        # canonical layered SVGs, both variants
bazel build //icons:all       # per-platform rasters + .icns/.ico/favicon
bazel build //brandbook:brandbook   # the brand guidelines PDF
```

Each variant emits Icon-Composer-ready layers: `.bg.svg`, `.tint.svg`,
`.arrow.svg`, `.mark.svg`, and a composite `.svg`.

## Palette

Deferred — the geometry is locked; colors are `Spec` parameters
(`bg/fg/accent/tertiary`). `gen/gen_palettes.py` explores candidates.
