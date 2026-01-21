#!/usr/bin/env python3
"""Build manifest.csv from raw audio/MIDI pairs."""

import csv
import hashlib
import re
from pathlib import Path
from typing import Optional

# Known emotions used in the dataset
EMOTIONS = ["angry", "happy", "sad", "tender", "original", "original1"]

# Songs known to have emotional variations (20 songs)
SONGS_WITH_VARIATIONS = {
    "Fuglesangen",
    "Godvaersdagen",
    "GroHolto",
    "Haslebuskane",
    "Havbrusen",
    "IvarJorde",
    "Klunkelatten",
    "Kongelatten",
    "Langaakern",
    "LattenSomBedOmNoko",
    "Perigarden",
    "Silkjegulen",
    "Solmoy",
    "Strandaspringar",
    "Tjednbalen",
    "Toingen",
    "Valdresspringar",
    "Vossarull",
    "SigneUladalen",
    "Spretten",
}


def sha256_file(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(s: str) -> str:
    """Compute SHA256 hash of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def extract_song_name(filename: str) -> str:
    """
    Extract the base song name from a filename.

    Handles patterns like:
    - Fuglesangen_angry.wav -> Fuglesangen
    - Baggen_happy_torr_02-Dec-2024_09-04-07_..._cleaned.wav -> Baggen
    - 00106-Furholt Otto-Fiskaren.wav -> 00106-Furholt Otto-Fiskaren
    """
    # Remove extension
    name = Path(filename).stem

    # For archival files (starting with numbers like 00106-...)
    if re.match(r"^\d{4,5}-", name):
        return name

    # For processed files with timestamps and _cleaned suffix
    # Pattern: SongName_emotion_torr_..._cleaned or SongName_original_torr_..._cleaned
    if "_torr_" in name or "_cleaned" in name:
        # Extract the part before _emotion_ or _original_
        parts = name.split("_")
        return parts[0]

    # For simple emotional variants: SongName_emotion
    for emotion in EMOTIONS:
        suffix = f"_{emotion}"
        if name.endswith(suffix):
            return name[: -len(suffix)]

    return name


def extract_emotion(filename: str) -> Optional[str]:
    """
    Extract emotion tag from filename if present.

    Returns: 'angry', 'happy', 'sad', 'tender', 'original', or None
    """
    name = Path(filename).stem

    # For archival files, no emotion
    if re.match(r"^\d{4,5}-", name):
        return None

    # Check for emotion patterns
    for emotion in EMOTIONS:
        # Handle _original1 as 'original'
        if emotion == "original1":
            if f"_{emotion}" in name:
                return "original"
        elif f"_{emotion}" in name:
            return emotion

    return None


def main():
    root = Path(__file__).parent.parent
    audio_dir = root / "data" / "raw" / "audio"
    midi_dir = root / "data" / "raw" / "midi"
    manifest_path = root / "data" / "manifests" / "manifest.csv"

    # Get all audio files
    audio_files = sorted(audio_dir.glob("*.wav"))

    rows = []
    for audio_path in audio_files:
        basename = audio_path.stem
        midi_path = midi_dir / f"{basename}.mid"

        if not midi_path.exists():
            print(f"Warning: No MIDI file for {audio_path.name}")
            continue

        # Relative paths from repo root
        audio_relpath = f"data/raw/audio/{audio_path.name}"
        midi_relpath = f"data/raw/midi/{midi_path.name}"

        # Generate deterministic ID
        id_string = f"{audio_relpath}:{midi_relpath}"
        row_id = sha256_string(id_string)

        # Extract metadata
        song_name = extract_song_name(audio_path.name)
        emotion = extract_emotion(audio_path.name)
        has_variations = song_name in SONGS_WITH_VARIATIONS

        # Compute checksums
        audio_sha256 = sha256_file(audio_path)
        midi_sha256 = sha256_file(midi_path)

        # Determine notes
        notes = ""
        if re.match(r"^\d{4,5}-", song_name):
            notes = "archival"
        elif "_cleaned" in audio_path.name or "_torr_" in audio_path.name:
            notes = "processed"

        rows.append(
            {
                "id": row_id,
                "song_name": song_name,
                "audio_relpath": audio_relpath,
                "midi_relpath": midi_relpath,
                "audio_sha256": audio_sha256,
                "midi_sha256": midi_sha256,
                "audio_ext": ".wav",
                "midi_ext": ".mid",
                "has_emotional_variations": has_variations,
                "emotion": emotion if emotion else "",
                "notes": notes,
            }
        )

    # Write CSV
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id",
            "song_name",
            "audio_relpath",
            "midi_relpath",
            "audio_sha256",
            "midi_sha256",
            "audio_ext",
            "midi_ext",
            "has_emotional_variations",
            "emotion",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Manifest written to {manifest_path}")
    print(f"Total pairs: {len(rows)}")
    print(f"Unique songs: {len({r['song_name'] for r in rows})}")
    print(f"Songs with variations: {sum(1 for r in rows if r['has_emotional_variations'])}")


if __name__ == "__main__":
    main()
