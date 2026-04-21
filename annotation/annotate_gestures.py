"""Label gesture types per clip. Placeholder for future CV-based annotation."""

import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/annotated/topics_manifest.json")
    parser.add_argument("--output", default="data/annotated/gestures_manifest.json")
    args = parser.parse_args()

    with open(args.input) as f:
        clips = json.load(f)

    for clip in clips:
        clip["gesture"] = "unknown"  # Placeholder — requires CV model

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(clips, f, indent=2)
    print(f"Gesture annotation placeholder for {len(clips)} clips")

if __name__ == "__main__":
    main()
