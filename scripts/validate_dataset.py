#!/usr/bin/env python3
"""Validate dataset manifest and file integrity."""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path


def sha256_file(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    root = Path(__file__).parent.parent
    manifest_path = root / 'data' / 'manifests' / 'manifest.csv'
    report_path = root / 'reports' / 'validate.json'

    # Initialize report
    report = {
        'status': 'pass',
        'total_pairs': 0,
        'unique_songs': 0,
        'songs_with_variations': 0,
        'songs_without_variations': 0,
        'missing_files': [],
        'checksum_mismatches': [],
        'duplicate_ids': [],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    # Read manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    report['total_pairs'] = len(rows)

    # Track unique songs and IDs
    song_names = set()
    songs_with_variations = set()
    songs_without_variations = set()
    seen_ids = set()

    for row in rows:
        # Check for duplicate IDs
        if row['id'] in seen_ids:
            report['duplicate_ids'].append(row['id'])
            report['status'] = 'fail'
        seen_ids.add(row['id'])

        # Track songs
        song_name = row['song_name']
        song_names.add(song_name)
        if row['has_emotional_variations'] == 'True':
            songs_with_variations.add(song_name)
        else:
            songs_without_variations.add(song_name)

        # Check audio file exists
        audio_path = root / row['audio_relpath']
        if not audio_path.exists():
            report['missing_files'].append(row['audio_relpath'])
            report['status'] = 'fail'
        else:
            # Verify checksum
            computed = sha256_file(audio_path)
            if computed != row['audio_sha256']:
                report['checksum_mismatches'].append({
                    'file': row['audio_relpath'],
                    'expected': row['audio_sha256'],
                    'actual': computed
                })
                report['status'] = 'fail'

        # Check MIDI file exists
        midi_path = root / row['midi_relpath']
        if not midi_path.exists():
            report['missing_files'].append(row['midi_relpath'])
            report['status'] = 'fail'
        else:
            # Verify checksum
            computed = sha256_file(midi_path)
            if computed != row['midi_sha256']:
                report['checksum_mismatches'].append({
                    'file': row['midi_relpath'],
                    'expected': row['midi_sha256'],
                    'actual': computed
                })
                report['status'] = 'fail'

    report['unique_songs'] = len(song_names)
    report['songs_with_variations'] = len(songs_with_variations)
    report['songs_without_variations'] = len(songs_without_variations)

    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"Validation {'PASSED' if report['status'] == 'pass' else 'FAILED'}")
    print(f"Total pairs: {report['total_pairs']}")
    print(f"Unique songs: {report['unique_songs']}")
    print(f"Songs with variations: {report['songs_with_variations']}")
    print(f"Songs without variations: {report['songs_without_variations']}")

    if report['missing_files']:
        print(f"Missing files: {len(report['missing_files'])}")
    if report['checksum_mismatches']:
        print(f"Checksum mismatches: {len(report['checksum_mismatches'])}")
    if report['duplicate_ids']:
        print(f"Duplicate IDs: {len(report['duplicate_ids'])}")

    print(f"\nReport written to {report_path}")

    # Exit with appropriate code
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    exit(main())
