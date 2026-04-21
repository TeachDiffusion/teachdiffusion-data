"""Build final training manifest from filtered clips.

Combines clip paths, captions, and metadata into the format
expected by the training pipeline.

Usage:
    python build_manifest.py --input data/filtered --output data/manifest.json
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build training manifest")
    parser.add_argument("--input", default="data/filtered")
    parser.add_argument("--output", default="data/manifest.json")
    args = parser.parse_args()

    input_dir = Path(args.input)
    manifest_path = input_dir / "filtered_manifest.json"

    if not manifest_path.exists():
        print(f"No filtered manifest at {manifest_path}")
        return

    with open(manifest_path) as f:
        clips = json.load(f)

    # Build training-ready manifest
    training_entries = []
    for clip in clips:
        entry = {
            "video_path": clip["clip_path"],
            "caption": clip.get("caption", ""),
            "transcript": clip.get("transcript", ""),
            "duration": clip.get("duration", 0),
            "quality_score": clip.get("quality_score", 0),
        }
        training_entries.append(entry)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(training_entries, f, indent=2)

    print(f"Training manifest: {len(training_entries)} entries → {output_path}")


if __name__ == "__main__":
    main()
