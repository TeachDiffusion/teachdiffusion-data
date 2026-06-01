"""End-to-end tests for pipeline/build_manifest.py.

The script is CLI-only (no exported functions to import directly), so we
exercise it via subprocess with a temporary input/output dir.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def run_build_manifest(input_dir: Path, output_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            "pipeline/build_manifest.py",
            "--input",
            str(input_dir),
            "--output",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_transforms_filtered_clips_into_training_entries(tmp_path):
    # Arrange — write a fake filtered_manifest.json.
    input_dir = tmp_path / "filtered"
    input_dir.mkdir()
    fake = [
        {
            "clip_path": "/data/clip_001.mp4",
            "caption": "Solving a quadratic by factoring",
            "transcript": "let's factor x squared plus 5x plus 6",
            "duration": 12.5,
            "quality_score": 0.78,
            "extra_field": "should be dropped",
        },
        {
            "clip_path": "/data/clip_002.mp4",
            "caption": "Computing a derivative",
            "transcript": "the derivative of x squared is 2x",
            "duration": 18.2,
            "quality_score": 0.82,
        },
    ]
    (input_dir / "filtered_manifest.json").write_text(json.dumps(fake))
    output_path = tmp_path / "manifest.json"

    # Act
    result = run_build_manifest(input_dir, output_path)

    # Assert — script succeeded.
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert output_path.exists()

    # The output shape matches the training-entry schema.
    written = json.loads(output_path.read_text())
    assert len(written) == 2

    entry = written[0]
    assert entry["video_path"] == "/data/clip_001.mp4"
    assert entry["caption"] == "Solving a quadratic by factoring"
    assert entry["transcript"] == "let's factor x squared plus 5x plus 6"
    assert entry["duration"] == 12.5
    assert entry["quality_score"] == 0.78
    # Untyped extras are not propagated.
    assert "extra_field" not in entry


def test_optional_fields_default_to_safe_values(tmp_path):
    """When a clip is missing caption/transcript/duration/quality_score they
    should default to empty string / 0 rather than crash."""
    input_dir = tmp_path / "filtered"
    input_dir.mkdir()
    sparse = [{"clip_path": "/data/clip.mp4"}]  # everything else missing
    (input_dir / "filtered_manifest.json").write_text(json.dumps(sparse))
    output_path = tmp_path / "manifest.json"

    result = run_build_manifest(input_dir, output_path)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    written = json.loads(output_path.read_text())
    assert len(written) == 1
    entry = written[0]
    assert entry["video_path"] == "/data/clip.mp4"
    assert entry["caption"] == ""
    assert entry["transcript"] == ""
    assert entry["duration"] == 0
    assert entry["quality_score"] == 0


def test_missing_input_manifest_exits_cleanly(tmp_path):
    """When filtered_manifest.json doesn't exist the script should print a
    message and exit 0 without creating an output file."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    output_path = tmp_path / "manifest.json"

    result = run_build_manifest(empty_dir, output_path)
    assert result.returncode == 0
    assert "No filtered manifest" in result.stdout
    assert not output_path.exists()


def test_empty_manifest_produces_empty_output(tmp_path):
    input_dir = tmp_path / "filtered"
    input_dir.mkdir()
    (input_dir / "filtered_manifest.json").write_text("[]")
    output_path = tmp_path / "manifest.json"

    result = run_build_manifest(input_dir, output_path)
    assert result.returncode == 0

    assert output_path.exists()
    assert json.loads(output_path.read_text()) == []
