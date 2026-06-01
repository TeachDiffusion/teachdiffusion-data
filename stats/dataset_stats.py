"""Generate dataset statistics."""

import argparse
import json
from collections import Counter
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to manifest JSON")
    args = parser.parse_args()

    with open(args.input) as f:
        clips = json.load(f)

    total = len(clips)
    durations = [c.get("duration", 0) for c in clips]
    topics = Counter(c.get("topic", "unknown") for c in clips)

    print(f"Total clips: {total}")
    print(f"Total duration: {sum(durations)/60:.1f} minutes")
    print(f"Avg clip duration: {sum(durations)/max(total,1):.1f}s")
    print(f"Min/Max duration: {min(durations, default=0):.1f}s / {max(durations, default=0):.1f}s")
    print(f"\nTopics: {dict(topics.most_common())}")

if __name__ == "__main__":
    main()
