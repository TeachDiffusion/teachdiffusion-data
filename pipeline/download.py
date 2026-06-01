"""Download CC-licensed math teaching videos from YouTube.

Usage:
    python download.py --channels configs/channels.txt --output data/raw --max_videos 100
"""

import argparse
import json
import subprocess
from pathlib import Path


def load_channels(channels_file: str) -> list[str]:
    """Load channel URLs from a text file."""
    with open(channels_file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def download_channel(channel_url: str, output_dir: Path, max_videos: int = 50) -> list[dict]:
    """Download videos from a YouTube channel using yt-dlp."""
    channel_dir = output_dir / channel_url.split("/")[-1]
    channel_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--max-downloads", str(max_videos),
        "--format", "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "--merge-output-format", "mp4",
        "--write-info-json",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--match-filter", "duration > 60 & duration < 3600",
        "--output", str(channel_dir / "%(id)s.%(ext)s"),
        channel_url,
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    except subprocess.TimeoutExpired:
        print(f"Timeout downloading from {channel_url}")

    # Collect metadata
    videos = []
    for json_file in channel_dir.glob("*.info.json"):
        with open(json_file) as f:
            info = json.load(f)
        video_path = json_file.with_suffix("").with_suffix(".mp4")
        if video_path.exists():
            videos.append({
                "id": info.get("id", ""),
                "title": info.get("title", ""),
                "channel": info.get("channel", ""),
                "duration": info.get("duration", 0),
                "path": str(video_path),
                "license": info.get("license", "unknown"),
            })

    return videos


def main():
    parser = argparse.ArgumentParser(description="Download math teaching videos")
    parser.add_argument("--channels", default="configs/channels.txt", help="Channel list file")
    parser.add_argument("--output", default="data/raw", help="Output directory")
    parser.add_argument("--max_videos", type=int, default=50, help="Max videos per channel")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    channels = load_channels(args.channels)
    print(f"Downloading from {len(channels)} channels...")

    all_videos = []
    for channel in channels:
        print(f"\nChannel: {channel}")
        videos = download_channel(channel, output_dir, args.max_videos)
        all_videos.extend(videos)
        print(f"  Downloaded {len(videos)} videos")

    # Save manifest
    manifest_path = output_dir / "download_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(all_videos, f, indent=2)

    print(f"\nTotal: {len(all_videos)} videos downloaded")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
