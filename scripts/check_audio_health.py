#!/usr/bin/env python3
"""
Audio health check script.

Validates WAV files for common issues:
- Valid WAV format
- Reasonable duration (5-300s by default)
- Not silent (>10% non-silent samples)
- Check for clipping
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    print("Error: soundfile and numpy are required.")
    print("Install with: pip install soundfile numpy")
    sys.exit(1)


# Duration limits in seconds
MIN_DURATION_SEC = 5.0
MAX_DURATION_SEC = 300.0  # 5 minutes

# Silence threshold (fraction of max amplitude)
SILENCE_THRESHOLD = 0.01
MIN_NON_SILENT_RATIO = 0.10  # At least 10% of samples should be non-silent

# Clipping threshold (fraction of samples at max amplitude)
CLIPPING_THRESHOLD = 0.001  # More than 0.1% samples at max = clipping warning


def check_audio_file(filepath: Path) -> dict[str, Any]:
    """
    Check a single audio file for health issues.

    Returns a dict with:
        - path: file path
        - valid: bool
        - issues: list of issue strings
        - metadata: dict with duration_sec, sample_rate, channels, etc.
    """
    result: dict[str, Any] = {
        "path": str(filepath),
        "valid": True,
        "issues": [],
        "metadata": {},
    }

    # Try to load the file
    try:
        data, sample_rate = sf.read(filepath, dtype="float32")
    except Exception as e:
        result["valid"] = False
        result["issues"].append(f"Failed to load audio file: {e}")
        return result

    # Get file info
    try:
        info = sf.info(filepath)
        result["metadata"]["format"] = info.format
        result["metadata"]["subtype"] = info.subtype
    except Exception:
        result["metadata"]["format"] = "unknown"
        result["metadata"]["subtype"] = "unknown"

    # Handle mono vs stereo
    if len(data.shape) == 1:
        channels = 1
        samples = len(data)
    else:
        channels = data.shape[1]
        samples = data.shape[0]

    duration_sec = samples / sample_rate

    result["metadata"]["sample_rate"] = sample_rate
    result["metadata"]["channels"] = channels
    result["metadata"]["samples"] = samples
    result["metadata"]["duration_sec"] = round(duration_sec, 2)

    # Check: reasonable duration
    if duration_sec < MIN_DURATION_SEC:
        result["issues"].append(
            f"Duration {duration_sec:.2f}s is below minimum ({MIN_DURATION_SEC}s)"
        )
    if duration_sec > MAX_DURATION_SEC:
        result["issues"].append(
            f"Duration {duration_sec:.2f}s exceeds maximum ({MAX_DURATION_SEC}s)"
        )

    # Convert to mono for analysis if stereo
    if channels > 1:
        mono_data = np.mean(data, axis=1)
    else:
        mono_data = data

    # Check: silence analysis
    abs_data = np.abs(mono_data)
    max_amplitude = np.max(abs_data)
    result["metadata"]["max_amplitude"] = round(float(max_amplitude), 4)

    if max_amplitude < 1e-6:
        result["valid"] = False
        result["issues"].append("Audio file appears to be completely silent")
    else:
        # Count non-silent samples
        threshold = max_amplitude * SILENCE_THRESHOLD
        non_silent_samples = np.sum(abs_data > threshold)
        non_silent_ratio = non_silent_samples / len(mono_data)
        result["metadata"]["non_silent_ratio"] = round(float(non_silent_ratio), 4)

        if non_silent_ratio < MIN_NON_SILENT_RATIO:
            result["issues"].append(
                f"Only {non_silent_ratio*100:.1f}% of samples are non-silent "
                f"(minimum: {MIN_NON_SILENT_RATIO*100:.0f}%)"
            )

    # Check: clipping
    # For float32 audio, clipping is at -1.0 and 1.0
    clipping_threshold_value = 0.9999
    clipped_samples = np.sum(abs_data >= clipping_threshold_value)
    clipping_ratio = clipped_samples / len(mono_data)
    result["metadata"]["clipping_ratio"] = round(float(clipping_ratio), 6)

    if clipping_ratio > CLIPPING_THRESHOLD:
        result["issues"].append(
            f"Possible clipping detected: {clipping_ratio*100:.2f}% of samples at max amplitude"
        )

    # RMS level
    rms = np.sqrt(np.mean(mono_data**2))
    result["metadata"]["rms_level"] = round(float(rms), 4)
    if rms > 0:
        rms_db = 20 * np.log10(rms)
        result["metadata"]["rms_db"] = round(float(rms_db), 2)
    else:
        result["metadata"]["rms_db"] = -np.inf

    # Mark as invalid only for critical issues
    critical_issues = ["Failed to load", "completely silent"]
    if any(any(crit in issue for crit in critical_issues) for issue in result["issues"]):
        result["valid"] = False

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Check audio files for health issues")
    parser.add_argument(
        "path",
        type=Path,
        help="Path to audio file or directory containing audio files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSON report file",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=MIN_DURATION_SEC,
        help=f"Minimum duration in seconds (default: {MIN_DURATION_SEC})",
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=MAX_DURATION_SEC,
        help=f"Maximum duration in seconds (default: {MAX_DURATION_SEC})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings (clipping, duration) as errors",
    )
    args = parser.parse_args()

    # Update global thresholds
    global MIN_DURATION_SEC, MAX_DURATION_SEC
    MIN_DURATION_SEC = args.min_duration
    MAX_DURATION_SEC = args.max_duration

    # Find audio files
    if args.path.is_file():
        audio_files = [args.path]
    elif args.path.is_dir():
        audio_files = sorted(args.path.glob("*.wav"))
    else:
        print(f"Error: {args.path} does not exist")
        return 1

    if not audio_files:
        print(f"No WAV files found in {args.path}")
        return 1

    # Check all files
    results = []
    for filepath in audio_files:
        result = check_audio_file(filepath)
        results.append(result)

    # Build report
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count
    warning_count = sum(1 for r in results if r["valid"] and r["issues"])

    report = {
        "status": "pass" if invalid_count == 0 else "fail",
        "total_files": len(results),
        "valid_files": valid_count,
        "invalid_files": invalid_count,
        "files_with_warnings": warning_count,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "results": results,
    }

    if args.strict and warning_count > 0:
        report["status"] = "fail"

    # Output report
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.output}")

    # Print summary
    print("\nAudio Health Check Summary")
    print(f"{'=' * 40}")
    print(f"Total files:        {len(results)}")
    print(f"Valid files:        {valid_count}")
    print(f"Invalid files:      {invalid_count}")
    print(f"Files with warnings:{warning_count}")
    print(f"Status:             {report['status'].upper()}")

    if invalid_count > 0:
        print("\nInvalid files:")
        for r in results:
            if not r["valid"]:
                print(f"  - {r['path']}")
                for issue in r["issues"]:
                    print(f"      {issue}")

    if warning_count > 0 and invalid_count == 0:
        print("\nFiles with warnings:")
        for r in results:
            if r["valid"] and r["issues"]:
                print(f"  - {r['path']}")
                for issue in r["issues"]:
                    print(f"      {issue}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
