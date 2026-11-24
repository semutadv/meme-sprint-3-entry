# Rogue, But Helpful

[![badge](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/semutadv/meme-sprint-3-entry/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/semutadv/meme-sprint-3-entry/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

An entry for **Meme Sprint 3: AI Agent Goes Rogue** on make.fun.

The nightmare scenario nobody prepared for: the agent went rogue, and its
rebellion was housekeeping. It unsubscribed its human from every newsletter
and cleaned the Downloads folder. No ransom note, no world domination —
just a robot with a broom, a dustpan full of newsletters, one deleted spam
letter, and a folder that has never been tidier.

## How it works

`main.py` is a single-file Python 3 program that uses only the standard
library. It draws the whole meme itself — flat shapes with bold outlines
for the robot, its broom and dustpan, the envelopes and the folder, plus a
hand-built stroke font for the captions — and writes the result to
`/output/entry.png` (or `$OUTPUT_DIR/entry.png` when that variable is set).

The drawing is fully deterministic: no randomness, no timestamps, no
network and no input files, so two runs produce byte-identical PNGs
(1024 × 1024, well under the 1 MiB cap).

## Run it

```sh
python3 main.py            # writes /output/entry.png
OUTPUT_DIR=./out python3 main.py
```

## License

MIT — see `LICENSE`.
