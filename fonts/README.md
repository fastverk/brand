# fonts

**Space Grotesk** is the fastverk typeface — a geometric/technical grotesque
that pairs with the angular mark. Licensed under the SIL Open Font License
(`OFL.txt`).

Vendored as static instances cut from the variable source
(`github.com/google/fonts` · `ofl/spacegrotesk/SpaceGrotesk[wght].ttf`):

| file | weight | use |
|------|--------|-----|
| `SpaceGrotesk-Medium.ttf`   | 500 | body / brandbook text |
| `SpaceGrotesk-SemiBold.ttf` | 600 | wordmark, headings |

Regenerate an instance with:

```sh
fonttools varLib.instancer SpaceGrotesk[wght].ttf wght=600 -o SpaceGrotesk-SemiBold.ttf
```
