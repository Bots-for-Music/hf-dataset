#!/usr/bin/env python3
"""
MIDI health check script.

Validates MIDI files for common issues:
- Valid MIDI format
- Contains at least 1 note
- Reasonable pitch range (21-108 +/- 12 for extended range)
- Duration sanity check
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import mido
except ImportError:
    print("Error: mido is required. Install with: pip install mido")
    sys.exit(1)


# Standard piano range: A0 (21) to C8 (108)
# Extended range: allow 1 octave below and above
MIN_PITCH = 21 - 12  # 9
MAX_PITCH = 108 + 12  # 120

# Duration limits in seconds
MIN_DURATION_SEC = 1.0
MAX_DURATION_SEC = 600.0  # 10 minutes


def check_midi_file(filepath: Path) -> dict[str, Any]:
    """
    Check a single MIDI file for health issues.

    Returns a dict with:
        - path: file path
        - valid: bool
        - issues: list of issue strings
        - metadata: dict with note_count, duration_sec, pitch_range, etc.
    """
    result: dict[str, Any] = {
        "path": str(filepath),
        "valid": True,
        "issues": [],
        "metadata": {},
    }

    # Try to load the file
    try:
        mid = mido.MidiFile(filepath)
    except Exception as e:
        result["valid"] = False
        result["issues"].append(f"Failed to load MIDI file: {e}")
        return result

    # Collect all notes
    notes: list[int] = []
    total_time_ticks = 0

    for track in mid.tracks:
        track_time = 0
        for msg in track:
            track_time += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                notes.append(msg.note)
        total_time_ticks = max(total_time_ticks, track_time)

    # Calculate duration in seconds
    try:
        duration_sec = mid.length
    except Exception:
        # Fallback calculation
        duration_sec = 0.0
        if mid.ticks_per_beat > 0:
            # Default tempo is 500000 microseconds per beat
            tempo = 500000
            for track in mid.tracks:
                for msg in track:
                    if msg.type == "set_tempo":
                        tempo = msg.tempo
                        break
            duration_sec = (total_time_ticks / mid.ticks_per_beat) * (tempo / 1_000_000)

    result["metadata"]["note_count"] = len(notes)
    result["metadata"]["duration_sec"] = round(duration_sec, 2)
    result["metadata"]["track_count"] = len(mid.tracks)
    result["metadata"]["ticks_per_beat"] = mid.ticks_per_beat
    result["metadata"]["type"] = mid.type

    # Check: at least 1 note
    if len(notes) == 0:
        result["valid"] = False
        result["issues"].append("No notes found in MIDI file")
        return result

    # Pitch range analysis
    min_pitch = min(notes)
    max_pitch = max(notes)
    result["metadata"]["pitch_range"] = {"min": min_pitch, "max": max_pitch}

    # Check: reasonable pitch range
    if min_pitch < MIN_PITCH:
        result["issues"].append(f"Pitch {min_pitch} is below extended range (min: {MIN_PITCH})")
    if max_pitch > MAX_PITCH:
        result["issues"].append(f"Pitch {max_pitch} is above extended range (max: {MAX_PITCH})")

    # Check: reasonable duration
    if duration_sec < MIN_DURATION_SEC:
        result["issues"].append(
            f"Duration {duration_sec:.2f}s is below minimum ({MIN_DURATION_SEC}s)"
        )
    if duration_sec > MAX_DURATION_SEC:
        result["issues"].append(
            f"Duration {duration_sec:.2f}s exceeds maximum ({MAX_DURATION_SEC}s)"
        )

    # Mark as invalid if there are critical issues (pitch out of range is a warning)
    if any("No notes" in issue or "Failed to load" in issue for issue in result["issues"]):
        result["valid"] = False

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Check MIDI files for health issues")
    parser.add_argument(
        "path",
        type=Path,
        help="Path to MIDI file or directory containing MIDI files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSON report file",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings (pitch range) as errors",
    )
    args = parser.parse_args()

    # Find MIDI files
    if args.path.is_file():
        midi_files = [args.path]
    elif args.path.is_dir():
        midi_files = sorted(args.path.glob("*.mid"))
    else:
        print(f"Error: {args.path} does not exist")
        return 1

    if not midi_files:
        print(f"No MIDI files found in {args.path}")
        return 1

    # Check all files
    results = []
    for filepath in midi_files:
        result = check_midi_file(filepath)
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
    print("\nMIDI Health Check Summary")
    print(f"{'=' * 40}")
    print(f"Total files:        {len(results)}")
    print(f"Valid files:        {valid_count}")
    print(f"Invalid files:      {invalid_count}")
    print(f"Files with warnings:{warning_count}")
    status = str(report["status"])
    print(f"Status:             {status.upper()}")

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
