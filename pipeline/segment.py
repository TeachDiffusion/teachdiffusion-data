"""Segment long videos into short training clips (5-30 seconds).

Uses scene detection + sentence boundary alignment so clips
never end mid-sentence.

Usage:
    python segment.py --input data/captioned --output data/clips
"""

import argparse
import json
import subprocess
from pathlib import Path


def detect_scenes(video_path: str, threshold: float = 27.0) -> list[float]:
    """Detect scene changes using PySceneDetect or fixed intervals as fallback."""
    try:
        from scenedetect import detect, ContentDetector
        scene_list = detect(video_path, ContentDetector(threshold=threshold))
        times = [scene[0].get_seconds() for scene in scene_list]
        if times:
            return times
    except ImportError:
        pass

    # Fallback: get video duration and split at fixed intervals
    try:
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", video_path],
            capture_output=True, text=True, timeout=30
        )
        duration = float(result.stdout.strip())
    except Exception:
        duration = 600

    return [float(t) for t in range(0, int(duration), 15)]


def align_to_sentences(
    cut_times: list[float], segments: list[dict], min_dur: float = 5.0, max_dur: float = 30.0
) -> list[tuple[float, float]]:
    """Align cut points to transcript sentence boundaries."""
    if not segments:
        # No transcript segments — use raw cut times
        clips = []
        for i in range(len(cut_times) - 1):
            start, end = cut_times[i], cut_times[i + 1]
            if min_dur <= (end - start) <= max_dur:
                clips.append((start, end))
        return clips

    # Snap each cut to the nearest sentence boundary
    sentence_ends = [seg["end"] for seg in segments]
    aligned = []

    for t in cut_times:
        closest = min(sentence_ends, key=lambda s: abs(s - t), default=t)
        if abs(closest - t) < 3.0:
            aligned.append(closest)
        else:
            aligned.append(t)

    # Build clips from aligned boundaries
    aligned = sorted(set(aligned))
    clips = []
    for i in range(len(aligned) - 1):
        start, end = aligned[i], aligned[i + 1]
        dur = end - start
        if min_dur <= dur <= max_dur:
            clips.append((start, end))
        elif dur > max_dur:
            # Split into sub-clips
            mid = start + dur / 2
            if dur / 2 >= min_dur:
                clips.append((start, mid))
                clips.append((mid, end))

    return clips


def extract_clip(video_path: str, start: float, end: float, output_path: str) -> bool:
    """Extract a clip using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", video_path,
        "-c", "copy",
        "-avoid_negative_ts", "1",
        output_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=60, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def main():
    parser = argparse.ArgumentParser(description="Segment videos into training clips")
    parser.add_argument("--input", default="data/captioned", help="Input directory")
    parser.add_argument("--output", default="data/clips", help="Output directory")
    parser.add_argument("--min_dur", type=float, default=5.0)
    parser.add_argument("--max_dur", type=float, default=30.0)
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = input_dir / "captioned_manifest.json"
    if not manifest_path.exists():
        print(f"No manifest found at {manifest_path}")
        return

    with open(manifest_path) as f:
        videos = json.load(f)

    all_clips = []
    clip_count = 0

    for video in videos:
        video_path = video["path"]
        if not Path(video_path).exists():
            continue

        print(f"Segmenting: {video_path}")
        scenes = detect_scenes(video_path)
        segments = video.get("segments", [])
        clip_ranges = align_to_sentences(scenes, segments, args.min_dur, args.max_dur)

        for start, end in clip_ranges:
            clip_name = f"clip_{clip_count:05d}.mp4"
            clip_path = str(output_dir / clip_name)

            if extract_clip(video_path, start, end, clip_path):
                # Get transcript for this time range
                clip_text = " ".join(
                    seg["text"] for seg in segments
                    if seg["start"] >= start and seg["end"] <= end + 1
                )
                all_clips.append({
                    "clip_path": clip_path,
                    "source_video": video_path,
                    "start": start,
                    "end": end,
                    "duration": end - start,
                    "transcript": clip_text.strip(),
                    "caption": video.get("caption", ""),
                })
                clip_count += 1

    manifest_out = output_dir / "clips_manifest.json"
    with open(manifest_out, "w") as f:
        json.dump(all_clips, f, indent=2)

    print(f"\nExtracted {clip_count} clips → {manifest_out}")


if __name__ == "__main__":
    main()
