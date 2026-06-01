"""Caption videos using Whisper transcription + pedagogy-aware captions.

Usage:
    python caption.py --input data/raw --output data/captioned
"""

import argparse
import json
from pathlib import Path


def transcribe_video(video_path: str) -> dict:
    """Transcribe a video using Whisper."""
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(video_path)
        return {
            "text": result["text"],
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                }
                for seg in result.get("segments", [])
            ],
            "language": result.get("language", "en"),
        }
    except ImportError:
        return {
            "text": "[Whisper not installed — install with: pip install openai-whisper]",
            "segments": [],
            "language": "en",
        }


def generate_pedagogy_caption(transcript: str, video_info: dict) -> str:
    """Generate a pedagogy-aware caption from a transcript.

    Describes the teaching content in a way that's useful for
    conditioning video generation.
    """
    title = video_info.get("title", "")
    duration = video_info.get("duration", 0)

    # Build a descriptive caption
    words = transcript.split()
    if len(words) < 10:
        return f"A math teacher explains {title}."

    # Detect math keywords for richer captions
    math_keywords = [
        "equation", "solve", "factor", "derivative", "integral", "matrix",
        "vector", "proof", "theorem", "formula", "graph", "function",
        "quadratic", "linear", "polynomial", "eigenvalue", "determinant",
    ]
    found_keywords = [kw for kw in math_keywords if kw in transcript.lower()]
    topic_hint = f" about {', '.join(found_keywords[:3])}" if found_keywords else ""

    caption = (
        f"A teacher stands in front of a whiteboard, "
        f"explaining a math concept{topic_hint}. "
        f"They speak clearly and gesture while teaching. "
        f"Duration: {duration}s."
    )
    return caption


def main():
    parser = argparse.ArgumentParser(description="Caption math teaching videos")
    parser.add_argument("--input", default="data/raw", help="Input directory with videos")
    parser.add_argument("--output", default="data/captioned", help="Output directory")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load download manifest
    manifest_path = input_dir / "download_manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            videos = json.load(f)
    else:
        videos = [
            {"path": str(p), "title": p.stem, "duration": 0}
            for p in input_dir.rglob("*.mp4")
        ]

    results = []
    for video in videos:
        video_path = video["path"]
        print(f"Captioning: {video_path}")

        transcript = transcribe_video(video_path)
        caption = generate_pedagogy_caption(transcript["text"], video)

        entry = {
            **video,
            "transcript": transcript["text"],
            "segments": transcript["segments"],
            "caption": caption,
        }
        results.append(entry)

    output_path = output_dir / "captioned_manifest.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nCaptioned {len(results)} videos → {output_path}")


if __name__ == "__main__":
    main()
