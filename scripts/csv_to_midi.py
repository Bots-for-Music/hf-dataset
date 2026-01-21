#!/usr/bin/env python3
"""Convert CSV note files to MIDI format.

CSV files contain high-precision pitch data (float values) that cannot be
fully represented in MIDI (integer pitches only). The original CSV files
are kept as ground truth reference for research purposes.

CSV format expected columns:
    - onset: Note start time in seconds
    - offset: Note end time in seconds
    - onpitch: Pitch value (float, will be rounded to nearest integer for MIDI)

Additional columns (preserved in CSV but not in MIDI):
    - offpitch, essential, bar, upmeter, lowmeter, offmeter, notetype,
      alignidx, file1idx, file2idx, metralign, previous, next
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

try:
    import pretty_midi
except ImportError:
    print("Error: pretty_midi is required. Install with: pip install pretty_midi")
    sys.exit(1)


def csv_to_midi(input_csv: Path, output_midi: Path, velocity: int = 100) -> int:
    """Convert a CSV note file to MIDI format.

    Args:
        input_csv: Path to input CSV file
        output_midi: Path to output MIDI file
        velocity: MIDI velocity for all notes (default: 100)

    Returns:
        Number of notes converted
    """
    midi_data = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano

    note_count = 0
    with open(input_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pitch = round(float(row["onpitch"]))
            # Clamp pitch to valid MIDI range (0-127)
            pitch = max(0, min(127, pitch))

            note = pretty_midi.Note(
                velocity=velocity,
                pitch=pitch,
                start=float(row["onset"]),
                end=float(row["offset"]),
            )
            instrument.notes.append(note)
            note_count += 1

    midi_data.instruments.append(instrument)
    midi_data.write(str(output_midi))
    return note_count


def process_directory(csv_dir: Path, midi_dir: Path, force: bool = False) -> dict[str, int]:
    """Convert all CSV files in a directory to MIDI.

    Args:
        csv_dir: Directory containing CSV files
        midi_dir: Directory for output MIDI files
        force: Overwrite existing MIDI files

    Returns:
        Dictionary mapping filenames to note counts
    """
    results: dict[str, int] = {}
    midi_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(csv_dir.glob("*.csv"))
    for csv_path in csv_files:
        midi_path = midi_dir / csv_path.with_suffix(".mid").name

        if midi_path.exists() and not force:
            print(f"Skipping {csv_path.name} (MIDI exists, use --force to overwrite)")
            continue

        try:
            note_count = csv_to_midi(csv_path, midi_path)
            results[csv_path.name] = note_count
            print(f"Converted {csv_path.name} -> {midi_path.name} ({note_count} notes)")
        except Exception as e:
            print(f"Error converting {csv_path.name}: {e}")
            results[csv_path.name] = -1

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert CSV note files to MIDI format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Convert a single file
    python csv_to_midi.py input.csv -o output.mid

    # Convert all CSVs in a directory
    python csv_to_midi.py data/raw/csv/ --midi-dir data/raw/midi/

    # Force overwrite existing files
    python csv_to_midi.py data/raw/csv/ --midi-dir data/raw/midi/ --force
        """,
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input CSV file or directory containing CSV files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output MIDI file (for single file conversion)",
    )
    parser.add_argument(
        "--midi-dir",
        type=Path,
        help="Output directory for MIDI files (for directory conversion)",
    )
    parser.add_argument(
        "--velocity",
        type=int,
        default=100,
        help="MIDI velocity for all notes (default: 100)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing MIDI files",
    )

    args = parser.parse_args()

    if args.input.is_file():
        # Single file conversion
        if args.output is None:
            args.output = args.input.with_suffix(".mid")

        if args.output.exists() and not args.force:
            print(f"Error: {args.output} exists. Use --force to overwrite.")
            sys.exit(1)

        note_count = csv_to_midi(args.input, args.output, args.velocity)
        print(f"Converted {args.input} -> {args.output} ({note_count} notes)")

    elif args.input.is_dir():
        # Directory conversion
        if args.midi_dir is None:
            print("Error: --midi-dir required for directory conversion")
            sys.exit(1)

        results = process_directory(args.input, args.midi_dir, args.force)
        successful = sum(1 for v in results.values() if v >= 0)
        print(f"\nConverted {successful}/{len(results)} files")

    else:
        print(f"Error: {args.input} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
