#!/usr/bin/env python3
"""Palette explorer (dev tool) — render every VARIANT across candidate palettes
as composite SVGs, for choosing the canonical fastverk colors.

CLI: `gen_palettes.py <out-dir>`.  Not wired into Bazel; the geometry is locked,
the palette is still a `Spec` parameter.
"""
import dataclasses
import os
import sys
from gen_mark import Mark, VARIANTS

# (name, bg, fg, accent, tertiary) — tertiary is MUTED so it recedes behind the accent
PALETTES = [
    ("midnight", "#15161A", "#ECE7DA", "#E0A33E", "#4A565A"),  # amber + muted slate
    ("logic",    "#0E1116", "#E8EEF4", "#4C8BF5", "#3E4564"),  # blue + muted indigo (∀∃/Lean)
    ("ember",    "#1B1410", "#F3E8D6", "#E8743A", "#6E5A44"),  # orange + muted umber
    ("forest",   "#10140E", "#E9E9D6", "#5BB873", "#555C44"),  # green + muted olive
    ("crimson",  "#141110", "#EFE7DC", "#D6452F", "#574E4A"),  # red + muted taupe
    ("mono",     "#17181C", "#ECE7DA", "#B9B0A0", "#555049"),  # warm monochrome
]

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for vname, base in VARIANTS.items():
        for pname, bg, fg, accent, tert in PALETTES:
            spec = dataclasses.replace(base, bg=bg, fg=fg, accent=accent, tertiary=tert)
            Mark(spec).render(os.path.join(out_dir, f"{vname}_{pname}.svg"))
            print(f"{vname}_{pname}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
