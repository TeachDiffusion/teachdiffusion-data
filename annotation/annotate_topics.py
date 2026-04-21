"""Tag clips with math topic labels using keyword matching + Claude API."""

import argparse
import json
from pathlib import Path

TOPIC_KEYWORDS = {
    "algebra": ["equation", "solve", "variable", "factor", "quadratic", "linear"],
    "calculus": ["derivative", "integral", "limit", "differentiate", "antiderivative"],
    "geometry": ["triangle", "circle", "angle", "area", "perimeter", "polygon"],
    "linear_algebra": ["matrix", "vector", "eigenvalue", "determinant", "transformation"],
    "trigonometry": ["sine", "cosine", "tangent", "unit circle", "radian"],
    "probability": ["probability", "random", "expected", "combination", "permutation"],
}

def detect_topic(transcript: str) -> str:
    text = transcript.lower()
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        scores[topic] = sum(1 for kw in keywords if kw in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general_math"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/filtered/filtered_manifest.json")
    parser.add_argument("--output", default="data/annotated/topics_manifest.json")
    args = parser.parse_args()

    with open(args.input) as f:
        clips = json.load(f)

    for clip in clips:
        clip["topic"] = detect_topic(clip.get("transcript", ""))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(clips, f, indent=2)
    print(f"Annotated {len(clips)} clips with topics")

if __name__ == "__main__":
    main()
