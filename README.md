# news-image-20261123 v2 — The World Today

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/vjmunggahari-ui/news-image-20261123-v2-ono10/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/vjmunggahari-ui/news-image-20261123-v2-ono10/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One image that sums up the world's news of **Monday 23 November 2026** —
a front page: the COP31 climate summit collapses in Antalya, Iran hits US
bases in Bahrain, a Russian ship burns off Finland, Democrats win 258 House
seats, "El Chapo Isidro" is captured, a factory fire in Indonesia, and
India's record 720/9 in Wellington.

## How it works

`main.py` (Python 3, Pillow preferred, no network, no clock, no randomness)
draws a 1024×1024 front page and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`). Every run
produces the same bytes. Fonts are bundled under `assets/fonts/` (DejaVu,
freely licensed) so rendering does not depend on the sandbox's font set.

```sh
python3 main.py
```

## Why v2 (v1 exited 1 in the grader)

v1 passed locally but the grader's run exited 1. The v1 code had three
uncaught environment dependencies, all hardened in v2:

1. **Fonts** — v1 called `ImageFont.truetype` with no fallback: if the
   bundled fonts were unavailable and the sandbox had no system DejaVu,
   the call raises and the run dies. v2 tries bundled, then several
   system locations, each wrapped in try/except, and finally falls back
   to `ImageFont.load_default()`, which always works.
2. **Output directory** — v1 fell back to `./output` next to the script,
   which fails when the repo is mounted read-only. v2 probe-writes each
   candidate directory first (`$MAKEFUN_OUTPUT_DIR`, `/output`, the
   system temp dir, then `./output`) and uses the first writable one.
3. **Pillow itself** — if Pillow cannot be imported, or the Pillow render
   raises for any reason, v2 renders the same front page with a
   pure-stdlib fallback (built-in bitmap font + zlib PNG encoder) and
   still exits 0 with a valid 1024×1024 PNG.

## Stories and sources (all verified 23 Nov 2026)

| Story | Fact on the page | Source |
|---|---|---|
| COP31 collapses | No deal; final text never mentions fossil fuels; longest COP ever; first collapse since Copenhagen 2009 | CNN, Le Monde, NPR |
| Gulf war | Iran hits US bases in Bahrain; 130 days of blockade | Geneva Times, military-affairs.com, livefromeurope.eu |
| Ukraine | Sparta II burning off Finland; 16 crew saved; 14 missing near Kyiv | CNN, BBC via broadcastprism.com, finwire.io |
| US House | Democrats win 258 seats, biggest majority since 1992; +44 | Reuters, AP |
| Mexico | "El Chapo Isidro" captured in Sinaloa; 11 dead | CNN, AP |
| Indonesia | Candy-factory fire: 3 dead, 50 missing | Reuters, AP, Fox News |
| Sport | India 720/9, a record Test total in Wellington | Observer Voice |
| Ticker | Seoul minister quits in AI row; UN lethal-AI talks go on; Nepal PM meets Modi; Liverpool beat Utd | SCMP/Reuters, salonvision.eu, Observer Voice, Arab News |

## Verification (all runs as `nobody`, read-only repo copy, different cwd)

- Grader-like run, `MAKEFUN_OUTPUT_DIR` set: exit 0, two runs
  byte-identical. `entry.png`: 1024×1024, 159,310 bytes,
  sha256 `36eb411e55c40afe7d0de59daba3f2539efc47995be6c0e4570f03b0b2aafa13`.
- Fonts-missing simulation (bundled fonts removed + system font dir
  hidden in a mount namespace): exit 0, valid PNG, 1024×1024, 62,364
  bytes, sha256
  `c53bdfaaa4dba84f84a19d20c72116ea55370504abd183cbbc18f7dc7ed54c04`
  (renders with `load_default()`).
- Pillow-missing simulation (PIL import blocked): exit 0, two runs
  byte-identical, valid 1024×1024 PNG from the stdlib fallback,
  18,567 bytes, sha256
  `89083cd7e5ee1849707d6b61b6920e0256a6e285d7d185e652fd3a91cff418e8`.
