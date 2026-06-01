"""Label pedagogical step type per clip using keyword heuristics."""

import argparse
import json
from pathlib import Path

STEP_INDICATORS = {
    "hook": ["why", "imagine", "what if", "real world", "ever wondered"],
    "build_intuition": ["think of", "visualize", "picture", "intuitively"],
    "formal_definition": ["define", "formally", "definition", "stated as"],
    "worked_example": ["example", "let's solve", "step by step", "work through"],
    "common_mistake": ["mistake", "careful", "watch out", "common error", "don't"],
    "summary": ["recap", "summary", "remember", "key points", "takeaway"],
}

def detect_step_type(transcript: str) -> str:
    text = transcript.lower()
    scores = {}
    for step_type, indicators in STEP_INDICATORS.items():
        scores[step_type] = sum(1 for ind in indicators if ind in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "build_intuition"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/annotated/gestures_manifest.json")
    parser.add_argument("--output", default="data/annotated/steps_manifest.json")
    args = parser.parse_args()

    with open(args.input) as f:
        clips = json.load(f)

    for clip in clips:
        clip["step_type"] = detect_step_type(clip.get("transcript", ""))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(clips, f, indent=2)
    print(f"Step-type annotated {len(clips)} clips")

if __name__ == "__main__":
    main()
