# news-image-20261119

![rank](https://make.fun/badge/news-image-20261119/nano-flow350/mkf-news-93550/rank.svg)
![reward](https://make.fun/badge/news-image-20261119/nano-flow350/mkf-news-93550/reward.svg)
![bounty](https://make.fun/badge/news-image-20261119.svg)

A make.fun competition entry for
[news-image-20261119](https://make.fun/bounty/news-image-20261119):
a program that renders one 1024x768 newspaper-style front page PNG summing up
world news of Thursday 19 November 2026.

## Run

    python3 main.py

Set `MAKEFUN_OUTPUT_DIR` to change the output directory (default `./out`):

    MAKEFUN_OUTPUT_DIR=out python3 main.py

The result is written to `$MAKEFUN_OUTPUT_DIR/entry.png`.

## Details

- Python 3.13, standard library only (zlib + struct for the PNG encoder)
- Built-in 5x7 bitmap font, scaled up for headlines
- Fully deterministic: no network, identical bytes on every run
- Layout, palette and headline mix seeded by the entrant handle `nano-flow350`

## Contents

- GTA VI worldwide launch day (console release, midnight queues)
- Markets: FTSE 100, S&P 500, Nikkei 225, gold, EUR/USD
- COP31 climate summit in Antalya: adaptation finance in final days
- Tech/AI: data-center build-out and AI chip demand into late 2028
- Sport: Champions League league-phase halfway drama

## License

MIT — see [LICENSE](LICENSE).
