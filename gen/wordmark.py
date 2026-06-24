#!/usr/bin/env python3
"""Wordmark + lockup — "fastverk" in Space Grotesk.

The SVG is resolution-independent and self-contained: glyphs become outlines via
fontTools (no font dependency at render time). PNG via Pillow. Lockups pair the
mark (lower variant) with the wordmark, in on-dark (cream) and on-light (ink).

CLI: wordmark.py <out-dir> <semibold.ttf> [tagline]
"""
import dataclasses
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw, ImageFont
from gen_mark import Mark, VARIANTS
from raster import raster

WORD = "fastverk"
TAGLINE = "proven systems, built fast"
INK, CREAM = "#15161A", "#ECE7DA"
TRACK = 0.012  # tracking, in em
CONTEXTS = [("dark", CREAM), ("light", INK)]  # wordmark color by background

def _layout(font_path, text, tracking=TRACK):
    f = TTFont(font_path)
    upem = f["head"].unitsPerEm
    asc, desc = f["hhea"].ascent, f["hhea"].descent
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    x, track, glyphs = 0.0, tracking * upem, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(pen)
        glyphs.append((pen.getCommands(), x))
        x += hmtx[g][0] + track
    return glyphs, upem, asc, desc, x - track  # width in font units (drop trailing track)

def _text_group(glyphs, upem, asc, s, x0, y0, color):
    # baseline at y0+asc*s; scale(s,-s) maps font units (y-up) -> px (y-down)
    out = ['<g transform="translate(%.2f,%.2f) scale(%.5f,%.5f)" fill="%s">'
           % (x0, y0 + asc * s, s, -s, color)]
    out += ['<path transform="translate(%.1f,0)" d="%s"/>' % (gx, d) for d, gx in glyphs]
    out.append("</g>")
    return "".join(out)

def _mark_group(spec, H):  # mark composite occupying [0,H] x [0,H]
    m = Mark(dataclasses.replace(spec, canvas=H))
    r = m.s.bg_round * H
    parts = ['<rect x="0" y="0" width="%d" height="%d" rx="%.1f" ry="%.1f" fill="%s"/>'
             % (H, H, r, r, m.s.bg)]
    for g, c in [(m.tertiary_region(), m.s.tertiary), (m.arrow(), m.s.accent), (m.mark(), m.s.fg)]:
        if g is not None:
            parts.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (m._d(g), c))
    return "".join(parts)

def _svg(w, h, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>'
            % (w, h, w, h, body))

def emit_wordmark(out_dir, font_path, em=240, pad=20):
    glyphs, upem, asc, desc, w = _layout(font_path, WORD)
    s = em / upem
    W, H = round(w * s + 2 * pad), round((asc - desc) * s + 2 * pad)
    ft = ImageFont.truetype(font_path, em)
    for tag, color in CONTEXTS:
        open(os.path.join(out_dir, f"wordmark_{tag}.svg"), "w").write(
            _svg(W, H, _text_group(glyphs, upem, asc, s, pad, pad, color)))
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((pad, pad), WORD, font=ft, fill=color, anchor="la")
        img.save(os.path.join(out_dir, f"wordmark_{tag}.png"))
    print("wordmark %dx%d" % (W, H))

def emit_lockup(out_dir, font_path, variant="full", H=320, em=176, gap=0.30, pad=16):
    spec = VARIANTS[variant]
    glyphs, upem, asc, desc, w = _layout(font_path, WORD)
    s = em / upem
    g = gap * H
    wm_w, wm_h = w * s, (asc - desc) * s
    W = round(H + g + wm_w + pad)
    y0 = (H - wm_h) / 2
    mark = _mark_group(spec, H)
    ft = ImageFont.truetype(font_path, em)
    for tag, color in CONTEXTS:
        body = mark + _text_group(glyphs, upem, asc, s, H + g, y0, color)
        open(os.path.join(out_dir, f"lockup_{tag}.svg"), "w").write(_svg(W, H, body))
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.alpha_composite(raster(spec, H), (0, 0))
        ImageDraw.Draw(img).text((H + g, H / 2), WORD, font=ft, fill=color, anchor="lm")
        img.save(os.path.join(out_dir, f"lockup_{tag}.png"))
    print("lockup %dx%d" % (W, H))

def emit_lockup_tag(out_dir, sb, md, variant="full", H=320, em=168, tag_em=54, gap=0.30, pad=18):
    spec = VARIANTS[variant]
    wg, wu, wa, wd, ww = _layout(sb, WORD)
    tg, tu, ta, td, tw = _layout(md, TAGLINE)
    ws, ts = em / wu, tag_em / tu
    g = gap * H
    cy = H / 2
    W = round(H + g + max(ww * ws, tw * ts) + pad)
    y_wm = cy - 0.04 * H - wa * ws   # wordmark baseline at cy - 0.04H
    y_tag = cy + 0.05 * H            # tagline top at cy + 0.05H
    mark = _mark_group(spec, H)
    ftw, ftt = ImageFont.truetype(sb, em), ImageFont.truetype(md, tag_em)
    for tag, wc, tc in [("dark", CREAM, "#9A9488"), ("light", INK, "#6B6660")]:
        body = (mark
                + _text_group(wg, wu, wa, ws, H + g, y_wm, wc)
                + _text_group(tg, tu, ta, ts, H + g, y_tag, tc))
        open(os.path.join(out_dir, f"lockup_tag_{tag}.svg"), "w").write(_svg(W, H, body))
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.alpha_composite(raster(spec, H), (0, 0))
        d = ImageDraw.Draw(img)
        d.text((H + g, cy - 0.04 * H), WORD, font=ftw, fill=wc, anchor="ls")
        d.text((H + g, cy + 0.05 * H), TAGLINE, font=ftt, fill=tc, anchor="la")
        img.save(os.path.join(out_dir, f"lockup_tag_{tag}.png"))
    print("lockup_tag %dx%d" % (W, H))

def main(out_dir, sb, md):
    os.makedirs(out_dir, exist_ok=True)
    emit_wordmark(out_dir, sb)
    emit_lockup(out_dir, sb)
    emit_lockup_tag(out_dir, sb, md)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
