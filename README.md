# teachdiffusion-data

Dataset pipeline for [TeachDiffusion](https://github.com/TeachDiffusion/TeachDiffusion) — scrapes, captions, segments, and filters math teaching videos for training.

## Pipeline

```
YouTube (CC-licensed) → download.py → caption.py → segment.py → filter.py → build_manifest.py
```

1. **download.py** — Scrape CC-licensed math teaching videos from YouTube
2. **caption.py** — Transcribe with Whisper + generate pedagogy-aware captions
3. **segment.py** — Cut into 5-30 second clips aligned to sentence boundaries
4. **filter.py** — Quality scoring and filtering (resolution, audio, math content)
5. **build_manifest.py** — Build final training manifest with clip paths and captions

## Quick Start

```bash
# Download videos from approved channels
python pipeline/download.py --channels configs/channels.txt --output data/raw

# Transcribe and caption
python pipeline/caption.py --input data/raw --output data/captioned

# Segment into clips
python pipeline/segment.py --input data/captioned --output data/clips

# Filter for quality
python pipeline/filter.py --input data/clips --output data/filtered --min_quality 0.6

# Build manifest
python pipeline/build_manifest.py --input data/filtered --output data/manifest.json
```

## Annotation Tools

For fine-grained labeling:
- `annotation/annotate_topics.py` — Tag clips with math topics
- `annotation/annotate_gestures.py` — Label gesture types per clip
- `annotation/annotate_steps.py` — Label pedagogical step type per clip

## License

The pipeline code is Apache 2.0. Collected data follows CC-BY licensing from source channels.
