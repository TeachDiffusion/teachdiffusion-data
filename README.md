<p align="center">
  <img src="https://raw.githubusercontent.com/TeachDiffusion/.github/main/assets/teachdiffusion_logo.svg" alt="TeachDiffusion" width="280"/>
</p>

<h1 align="center">teachdiffusion-data</h1>

<p align="center">
  Dataset pipeline — scrape, caption, segment, and filter math-teaching videos for training.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
</p>

> For project mission, the full 8-layer architecture, sibling repositories, and roadmap, see the [TeachDiffusion organization profile](https://github.com/TeachDiffusion).

---

## About this repo

This repo produces the **training dataset** consumed by [`teachdiffusion-training`](https://github.com/TeachDiffusion/teachdiffusion-training). It does not train anything itself and is not imported by the core package — its only output is a curated manifest of math-teaching video clips with pedagogy-aware captions.

## Pipeline

```
YouTube (CC-licensed) → download → caption → segment → filter → build_manifest
```

| Stage | Script | What it does |
|---|---|---|
| Download | [`pipeline/download.py`](pipeline/download.py) | Pull CC-licensed videos from approved channels |
| Caption | [`pipeline/caption.py`](pipeline/caption.py) | Whisper transcripts + pedagogy-aware captions |
| Segment | [`pipeline/segment.py`](pipeline/segment.py) | Cut 5–30s clips aligned to sentence boundaries |
| Filter | [`pipeline/filter.py`](pipeline/filter.py) | Quality scoring (resolution, audio, math content) |
| Manifest | [`pipeline/build_manifest.py`](pipeline/build_manifest.py) | Assemble final training manifest |

### Run end-to-end

```bash
python pipeline/download.py       --channels configs/channels.txt --output data/raw
python pipeline/caption.py        --input data/raw       --output data/captioned
python pipeline/segment.py        --input data/captioned --output data/clips
python pipeline/filter.py         --input data/clips     --output data/filtered --min_quality 0.6
python pipeline/build_manifest.py --input data/filtered  --output data/manifest.json
```

## Annotation

Fine-grained labels on top of the auto-captions:

- [`annotation/annotate_topics.py`](annotation/annotate_topics.py) — math topic tags
- [`annotation/annotate_gestures.py`](annotation/annotate_gestures.py) — gesture type per clip
- [`annotation/annotate_steps.py`](annotation/annotate_steps.py) — pedagogical step type per clip

Schema and labelling conventions are in [`docs/annotation_guide.md`](docs/annotation_guide.md). Dataset characteristics, splits, and intended use are in [`docs/dataset_card.md`](docs/dataset_card.md).

## Configs

- [`configs/channels.txt`](configs/channels.txt) — approved CC-licensed source channels
- [`configs/filter_config.yaml`](configs/filter_config.yaml) — quality thresholds and filtering rules

## Stats

```bash
python stats/dataset_stats.py --manifest data/manifest.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Pipeline code: Apache 2.0. Collected data follows the CC-BY licensing of the source channels — see [`docs/dataset_card.md`](docs/dataset_card.md) for per-clip provenance.
