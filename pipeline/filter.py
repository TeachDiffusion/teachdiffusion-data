"""Quality filtering for training clips.

Scores each clip on: transcript quality, video quality, duration.
Rejects clips below threshold.

Usage:
    python filter.py --input data/clips --output data/filtered --min_quality 0.6
"""

import argparse
import json
import shutil
from pathlib import Path

MATH_VOCABULARY = {
    "equation", "solve", "factor", "derivative", "integral", "matrix",
    "vector", "proof", "theorem", "formula", "graph", "function",
    "quadratic", "linear", "polynomial", "eigenvalue", "determinant",
    "limit", "continuous", "slope", "tangent", "area", "volume",
    "angle", "triangle", "circle", "sine", "cosine", "logarithm",
    "exponent", "fraction", "numerator", "denominator", "variable",
    "coefficient", "constant", "zero", "root", "solution", "equal",
    "plus", "minus", "multiply", "divide", "squared", "cubed",
}

TEACHING_LANGUAGE = {
    "let's", "notice", "remember", "think about", "consider",
    "for example", "in other words", "step", "first", "next",
    "so we", "that means", "because", "therefore", "thus",
    "can you see", "the key idea", "watch what happens",
    "try", "practice", "let me show", "look at",
}


def score_transcript(transcript: str) -> float:
    """Score transcript for math teaching content (0-1)."""
    if not transcript or len(transcript.strip()) < 20:
        return 0.0

    words = transcript.lower().split()
    word_count = len(words)
    if word_count < 5:
        return 0.1

    math_hits = sum(1 for w in words if w in MATH_VOCABULARY)
    math_score = min(1.0, math_hits / max(word_count * 0.05, 1))

    teach_hits = sum(1 for phrase in TEACHING_LANGUAGE if phrase in transcript.lower())
    teach_score = min(1.0, teach_hits / 3)

    length_score = min(1.0, word_count / 30)

    return 0.4 * math_score + 0.3 * teach_score + 0.3 * length_score


def score_clip(clip: dict) -> float:
    """Score a clip overall (0-1)."""
    transcript_score = score_transcript(clip.get("transcript", ""))

    duration = clip.get("duration", 0)
    if duration < 3 or duration > 60:
        duration_score = 0.2
    elif 5 <= duration <= 30:
        duration_score = 1.0
    else:
        duration_score = 0.6

    return 0.7 * transcript_score + 0.3 * duration_score


def main():
    parser = argparse.ArgumentParser(description="Filter clips by quality")
    parser.add_argument("--input", default="data/clips", help="Input directory")
    parser.add_argument("--output", default="data/filtered", help="Output directory")
    parser.add_argument("--min_quality", type=float, default=0.6, help="Minimum quality score")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = input_dir / "clips_manifest.json"
    if not manifest_path.exists():
        print(f"No manifest at {manifest_path}")
        return

    with open(manifest_path) as f:
        clips = json.load(f)

    accepted = []
    rejected = 0

    for clip in clips:
        score = score_clip(clip)
        clip["quality_score"] = round(score, 3)

        if score >= args.min_quality:
            # Copy clip to output
            src = Path(clip["clip_path"])
            if src.exists():
                dst = output_dir / src.name
                shutil.copy2(src, dst)
                clip["clip_path"] = str(dst)
            accepted.append(clip)
        else:
            rejected += 1

    manifest_out = output_dir / "filtered_manifest.json"
    with open(manifest_out, "w") as f:
        json.dump(accepted, f, indent=2)

    print(f"Accepted: {len(accepted)} | Rejected: {rejected} | Threshold: {args.min_quality}")
    print(f"Manifest: {manifest_out}")


if __name__ == "__main__":
    main()
