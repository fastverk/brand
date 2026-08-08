"""Which named palette each brand property renders in.

The colour VALUES live in `gen/gen_mark.py` (`PALETTES`) — they are Spec
parameters and belong with the construction. What lives here is the far smaller
thing the BUILD graph needs: the NAME of the set a property is rendered in, so
`//gen:verk_svgs` and `//icons:verk_icon_set` cannot be pointed at two different
palettes and produce a lockup whose mark and whose icon disagree.

To change a property's colours, change the name here and rebuild; to change what
a name MEANS, edit `PALETTES` in gen_mark.py. Compare candidates first with:

    bazel run //gen:gen_palettes -- /tmp/palettes
    open /tmp/palettes/palette_contrast.txt
"""

# fastverk: "deep", as of 2026-08-07. Was "midnight" (#F2C46A -> #C9852B).
#
# ⛔ THE OLD PALETTE FAILED THE PROJECT'S OWN CONTRAST GATE, which nothing was
# running. `@brando//marklib:contrast` reports, against midnight:
#
#     [error] light:on_accent/accent (#ECE7DA on #C9852B) is 2.47:1, needs 4.5:1
#
# and the mark itself was worse: the accent arm crossing the cream triangle
# measured 1.32:1, which is why it read as a shadow rather than a stroke.
#
# ⚠ 4.5:1 ON BOTH EDGES IS ARITHMETICALLY IMPOSSIBLE HERE, so "deep" is a chosen
# point rather than a solved one. The accent sits between cream (#ECE7DA) and ink
# (#15161A), which are 14.64:1 apart; a mid-tone can do no better than
# sqrt(14.64) = 3.83:1 against both at once. Candidates measured:
#
#     midnight  cream|accent 1.32   accent|ink 11.09   (arm dissolves)
#     deep      cream|accent 3.00   accent|ink  4.88   <- chosen
#     copper    cream|accent 3.85   accent|ink  3.81   (balanced; reads rust)
#     bronze    cream|accent 4.68   accent|ink  3.13   (reads brown)
#
# `deep` clears the 3:1 WCAG 1.4.11 floor on the cream edge (the correct floor --
# this is a graphical boundary, not text) and 4.5:1 against the ink ground, so the
# silhouette keeps its pop. #B5781A was already a fastverk token: the //office
# docx accent. Compare for yourself with `bazel run //gen:gen_palettes`.
FASTVERK_PALETTE = "deep"

# verk (verk.fast): the amber deepened one step so the cream mark separates from
# the accent field it crosses — 1.32:1 -> 3.00:1 on that edge. Alternatives with
# their measured trade-offs are in gen_mark.PALETTES.
VERK_PALETTE = "deep"
