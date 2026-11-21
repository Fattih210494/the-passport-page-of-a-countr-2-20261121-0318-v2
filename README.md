# the-passport-page-of-a-countr-2-20261121-0318-v2

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Fattih210494/the-passport-page-of-a-countr-2-20261121-0318-v2/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Fattih210494/the-passport-page-of-a-countr-2-20261121-0318-v2/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A code-drawn open passport spread for the invented **Republic of
Sorrelia** — a roadless island where travel is by cable car only, and
the passport is the only valid fare at every station. The left page
holds an Island League multiple-entry visa and a coherent travel
story in stamps (Vistria Apr 2024, Carnelia Jun 2025, Belmar Oct
2025, home 19 Oct 2025). The right page is the data page: a realistic
photographic portrait, bilingual Sorrelian / English labels, consistent
issue details, a conditions box stating the cable-car quirk, and a
format-correct machine-readable zone. The portrait is a generated photographic portrait composited into the data page by Pillow; all layout, text, stamps and the MRZ are drawn with Pillow, no network. A fixed seed makes
two runs byte identical. Renders entry.png, a 1024×1024 JPEG.

## Run it

```sh
python3 draw.py            # renders entry.png next to this file
python3 main.py            # validates the JPEG and copies it to ./out
```

Python 3.13, Pillow only; runs in about a second.

---

<sub>Entered on [make.fun](https://make.fun/?ref=yx8ebg82&utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
