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

## Properties

`fastverk` is the reference property. `verk` is the same identity for
**`verk.fast`** — a domain hack, since host + TLD read as "fastverk" backwards.
It is the same construction and the same generator; the word is short and the
amber is deepened (below).

```sh
bazel build //gen:verk_svgs           # verk_full.svg, verk_lower.svg + layers
bazel build //icons:verk_icon_set     # verk_*.png / .icns / .ico
bazel build //wordmark/verk:wordmark_set   # the "verk" wordmark + lockups
bazel build //skins:verk              # the verk meridian skin
```

Nothing about the verk mark is hand-drawn or hand-recolored: `--prefix` and
`--palette` are generator flags, `word` is a field in
`wordmark/verk/wordmark.json`, and the palette NAME lives once in
`gen/palette.bzl` so the SVG set and the icon set cannot drift apart.

## Palette

The geometry is locked; colors are `Spec` parameters
(`bg/fg/accent/accent2/tertiary`), grouped into named sets in `gen_mark.PALETTES`.
`gen/gen_palettes.py` renders every set and writes `palette_contrast.txt`, the
measured WCAG ratio of each edge the mark actually has:

```sh
bazel run //gen:gen_palettes -- /tmp/palettes
```

The canonical tokens (the "deep" palette, canonical since 2026-08-07 — it was
"midnight", `#F2C46A` → `#C9852B`) are:

| token | hex | role |
|---|---|---|
| ink | `#15161A` | ground |
| ink-2 | `#1c1e24` | raised surface |
| cream | `#ECE7DA` | foreground |
| amber | `#B5781A` | accent |
| amber-deep | `#845712` | accent (gradient end / pressed) |
| muted | `#9A9488` | meta text |

In the **light** skin the accent is `#96560D` rather than the canonical amber:
there it is real text on the cream ground and has to clear 4.5:1, which `#B5781A`
(3.00:1 on cream) does not. See `skins/fastverk.textpb`.

### The amber sits between cream and ink, and cannot clear both

In the `full` variant the cream mark **crosses** the accent field (the F arm) and
rings it on every side, so cream|amber is a real edge. The old canonical amber
(`#F2C46A`) measured **1.32:1** against cream — the arm dissolved into the field
it crosses — while measuring 11.09:1 against the ink ground. Those two move in
opposite directions
by construction: with cream at L .800 and ink at L .008, an accent between them
tops out at √14.64 = **3.83:1 on both edges at once**. 4.5:1 on both is
unreachable, not merely unchosen.

| palette | accent | cream \| accent | accent \| ink |
|---|---|---|---|
| `midnight` (was canonical) | `#F2C46A` | 1.32:1 | 11.09:1 |
| `deep` (canonical, and verk) | `#B5781A` | 3.00:1 | 4.88:1 |
| `copper` | `#B05D15` | 3.85:1 | 3.81:1 |
| `bronze` | `#96560D` | 4.68:1 | 3.13:1 |

`deep` clears the 3:1 WCAG 1.4.11 floor on the cream edge — the correct floor for
a graphical boundary rather than text — and 4.5:1 against the ink ground, so the
silhouette keeps its pop.

`//skins:fastverk_contrast` and `//skins:verk_contrast` run brando's WCAG gate
over both skins, and both **pass**. The gate used to be off for fastverk exactly
because fastverk failed it — `light:on_accent/accent (#ECE7DA on #C9852B) is
2.47:1, needs 4.5:1`, the weak white-on-amber the brand carried in production.
The light skin's accent is now `#96560D` (4.68:1 on cream), so there is no longer
a reason to leave the canonical brand ungated.

## Skin (`skins/`)

The brand identity is also published as a **meridian skin** — a
`meridian.theme.v1.Theme` that drives every meridian renderer (web console,
SwiftUI app, JavaFX desktop, ratatui TUI) from one source, so the brand reads
identically on every surface.

`skins/fastverk.textpb` authors the Theme once (the tokens above), validated
against meridian's `theme.proto` at build time. `//skins` emits both wire forms:

```sh
bazel build //skins:fastverk_binpb   # fastverk.binpb — native decoders (TUI/Swift/JavaFX)
bazel build //skins:fastverk_json    # fastverk.json  — web `applyTheme(skin, mode)`
bazel build //skins:fastverk         # both, as a stageable filegroup
```

`fastverk.binpb` is produced by `protoc --encode` (which also validates the
textproto against the schema); `fastverk.json` is the proto3-JSON twin
(snake_case field names matching meridian's `theme/web/theme.ts`). Brand depends
on meridian only for the schema — it pulls no renderer code, and meridian itself
stays brand-neutral.
