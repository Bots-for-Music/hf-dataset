"""Tests for csv_to_midi.py conversion script."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from csv_to_midi import csv_to_midi, process_alternatives, process_directory


@pytest.fixture
def valid_csv(tmp_path: Path) -> Path:
    """Create a valid CSV file with note data."""
    csv_path = tmp_path / "test_song.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["onset", "offset", "onpitch", "offpitch", "essential"])
        writer.writerow([0.0, 0.5, 60.0, 60.0, 1.0])  # Middle C
        writer.writerow([0.5, 1.0, 64.5, 64.5, 1.0])  # E4 (will round to 65)
        writer.writerow([1.0, 1.5, 67.8, 67.8, 1.0])  # G4 (will round to 68)
    return csv_path


@pytest.fixture
def csv_with_float_pitches(tmp_path: Path) -> Path:
    """Create a CSV with high-precision float pitches."""
    csv_path = tmp_path / "float_pitches.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["onset", "offset", "onpitch"])
        writer.writerow([0.0, 0.5, 60.25])  # Should round to 60
        writer.writerow([0.5, 1.0, 60.75])  # Should round to 61
        writer.writerow([1.0, 1.5, 78.36])  # Should round to 78
    return csv_path


@pytest.fixture
def csv_with_extreme_pitches(tmp_path: Path) -> Path:
    """Create a CSV with pitches outside MIDI range."""
    csv_path = tmp_path / "extreme_pitches.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["onset", "offset", "onpitch"])
        writer.writerow([0.0, 0.5, -5.0])  # Below 0, should clamp to 0
        writer.writerow([0.5, 1.0, 150.0])  # Above 127, should clamp to 127
        writer.writerow([1.0, 1.5, 64.0])  # Normal pitch
    return csv_path


@pytest.fixture
def empty_csv(tmp_path: Path) -> Path:
    """Create an empty CSV file (headers only)."""
    csv_path = tmp_path / "empty.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["onset", "offset", "onpitch"])
    return csv_path


@pytest.fixture
def invalid_csv_missing_columns(tmp_path: Path) -> Path:
    """Create a CSV missing required columns."""
    csv_path = tmp_path / "invalid.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start", "end", "pitch"])  # Wrong column names
        writer.writerow([0.0, 0.5, 60.0])
    return csv_path


class TestCsvToMidi:
    """Tests for csv_to_midi function."""

    def test_basic_conversion(self, valid_csv: Path, tmp_path: Path) -> None:
        """Test basic CSV to MIDI conversion."""
        midi_path = tmp_path / "output.mid"
        note_count = csv_to_midi(valid_csv, midi_path)

        assert note_count == 3
        assert midi_path.exists()
        assert midi_path.stat().st_size > 0

    def test_float_pitch_rounding(self, csv_with_float_pitches: Path, tmp_path: Path) -> None:
        """Test that float pitches are correctly rounded."""
        midi_path = tmp_path / "output.mid"
        note_count = csv_to_midi(csv_with_float_pitches, midi_path)

        assert note_count == 3
        assert midi_path.exists()

        # Verify pitches by reading back the MIDI
        import pretty_midi

        midi = pretty_midi.PrettyMIDI(str(midi_path))
        notes = midi.instruments[0].notes
        pitches = sorted([n.pitch for n in notes])

        assert pitches == [60, 61, 78]  # Rounded values

    def test_extreme_pitch_clamping(self, csv_with_extreme_pitches: Path, tmp_path: Path) -> None:
        """Test that extreme pitches are clamped to valid MIDI range."""
        midi_path = tmp_path / "output.mid"
        note_count = csv_to_midi(csv_with_extreme_pitches, midi_path)

        assert note_count == 3
        assert midi_path.exists()

        import pretty_midi

        midi = pretty_midi.PrettyMIDI(str(midi_path))
        notes = midi.instruments[0].notes
        pitches = sorted([n.pitch for n in notes])

        assert pitches == [0, 64, 127]  # Clamped values

    def test_empty_csv(self, empty_csv: Path, tmp_path: Path) -> None:
        """Test conversion of empty CSV (headers only)."""
        midi_path = tmp_path / "output.mid"
        note_count = csv_to_midi(empty_csv, midi_path)

        assert note_count == 0
        assert midi_path.exists()

    def test_invalid_csv_raises_error(
        self, invalid_csv_missing_columns: Path, tmp_path: Path
    ) -> None:
        """Test that invalid CSV raises KeyError for missing columns."""
        midi_path = tmp_path / "output.mid"

        with pytest.raises(KeyError):
            csv_to_midi(invalid_csv_missing_columns, midi_path)

    def test_custom_velocity(self, valid_csv: Path, tmp_path: Path) -> None:
        """Test conversion with custom velocity."""
        midi_path = tmp_path / "output.mid"
        note_count = csv_to_midi(valid_csv, midi_path, velocity=80)

        assert note_count == 3

        import pretty_midi

        midi = pretty_midi.PrettyMIDI(str(midi_path))
        notes = midi.instruments[0].notes

        for note in notes:
            assert note.velocity == 80

    def test_timing_preserved(self, valid_csv: Path, tmp_path: Path) -> None:
        """Test that note timing is preserved in conversion."""
        midi_path = tmp_path / "output.mid"
        csv_to_midi(valid_csv, midi_path)

        import pretty_midi

        midi = pretty_midi.PrettyMIDI(str(midi_path))
        notes = sorted(midi.instruments[0].notes, key=lambda n: n.start)

        assert abs(notes[0].start - 0.0) < 0.001
        assert abs(notes[0].end - 0.5) < 0.001
        assert abs(notes[1].start - 0.5) < 0.001
        assert abs(notes[2].end - 1.5) < 0.001


class TestProcessDirectory:
    """Tests for process_directory function."""

    def test_convert_multiple_files(self, tmp_path: Path) -> None:
        """Test converting multiple CSV files in a directory."""
        csv_dir = tmp_path / "csv"
        midi_dir = tmp_path / "midi"
        csv_dir.mkdir()

        # Create two CSV files
        for name in ["song1", "song2"]:
            csv_path = csv_dir / f"{name}.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["onset", "offset", "onpitch"])
                writer.writerow([0.0, 1.0, 60.0])

        results = process_directory(csv_dir, midi_dir)

        assert len(results) == 2
        assert results["song1.csv"] == 1
        assert results["song2.csv"] == 1
        assert (midi_dir / "song1.mid").exists()
        assert (midi_dir / "song2.mid").exists()

    def test_skip_existing_midi(self, tmp_path: Path) -> None:
        """Test that existing MIDI files are not overwritten without --force."""
        csv_dir = tmp_path / "csv"
        midi_dir = tmp_path / "midi"
        csv_dir.mkdir()
        midi_dir.mkdir()

        # Create CSV file
        csv_path = csv_dir / "existing.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["onset", "offset", "onpitch"])
            writer.writerow([0.0, 1.0, 60.0])

        # Create existing MIDI file with known content
        midi_path = midi_dir / "existing.mid"
        midi_path.write_text("original content")
        original_content = midi_path.read_text()

        # Process without force
        results = process_directory(csv_dir, midi_dir, force=False)

        # Should skip and MIDI content unchanged
        assert len(results) == 0
        assert midi_path.read_text() == original_content

    def test_force_overwrite(self, tmp_path: Path) -> None:
        """Test that --force overwrites existing MIDI files."""
        csv_dir = tmp_path / "csv"
        midi_dir = tmp_path / "midi"
        csv_dir.mkdir()
        midi_dir.mkdir()

        # Create CSV file
        csv_path = csv_dir / "existing.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["onset", "offset", "onpitch"])
            writer.writerow([0.0, 1.0, 60.0])

        # Create existing MIDI file
        midi_path = midi_dir / "existing.mid"
        midi_path.write_text("original content")

        # Process with force
        results = process_directory(csv_dir, midi_dir, force=True)

        # Should convert and overwrite
        assert results["existing.csv"] == 1
        assert midi_path.read_bytes() != b"original content"

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Test processing an empty directory."""
        csv_dir = tmp_path / "csv"
        midi_dir = tmp_path / "midi"
        csv_dir.mkdir()

        results = process_directory(csv_dir, midi_dir)

        assert len(results) == 0
        assert midi_dir.exists()


class TestProcessAlternatives:
    """Tests for process_alternatives function."""

    def test_convert_alternatives(self, tmp_path: Path) -> None:
        """Test converting alternative transcriptions in song subdirectories."""
        csv_alt_dir = tmp_path / "csv_alt"
        midi_alt_dir = tmp_path / "midi_alt"

        # Create song directory with multiple versions
        song_dir = csv_alt_dir / "MySong"
        song_dir.mkdir(parents=True)

        for version in ["roughpitch", "autotuned"]:
            csv_path = song_dir / f"{version}.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["onset", "offset", "onpitch"])
                writer.writerow([0.0, 1.0, 60.0])

        results = process_alternatives(csv_alt_dir, midi_alt_dir)

        assert len(results) == 2
        assert results["MySong/roughpitch.csv"] == 1
        assert results["MySong/autotuned.csv"] == 1
        assert (midi_alt_dir / "MySong" / "roughpitch.mid").exists()
        assert (midi_alt_dir / "MySong" / "autotuned.mid").exists()

    def test_multiple_songs(self, tmp_path: Path) -> None:
        """Test converting alternatives for multiple songs."""
        csv_alt_dir = tmp_path / "csv_alt"
        midi_alt_dir = tmp_path / "midi_alt"

        # Create two song directories
        for song in ["Song1", "Song2"]:
            song_dir = csv_alt_dir / song
            song_dir.mkdir(parents=True)
            csv_path = song_dir / "version1.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["onset", "offset", "onpitch"])
                writer.writerow([0.0, 1.0, 60.0])

        results = process_alternatives(csv_alt_dir, midi_alt_dir)

        assert len(results) == 2
        assert (midi_alt_dir / "Song1" / "version1.mid").exists()
        assert (midi_alt_dir / "Song2" / "version1.mid").exists()

    def test_skip_existing_midi(self, tmp_path: Path) -> None:
        """Test that existing alternative MIDIs are not overwritten."""
        csv_alt_dir = tmp_path / "csv_alt"
        midi_alt_dir = tmp_path / "midi_alt"

        # Create song directory with CSV
        song_dir = csv_alt_dir / "MySong"
        song_dir.mkdir(parents=True)
        csv_path = song_dir / "version.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["onset", "offset", "onpitch"])
            writer.writerow([0.0, 1.0, 60.0])

        # Create existing MIDI
        midi_song_dir = midi_alt_dir / "MySong"
        midi_song_dir.mkdir(parents=True)
        midi_path = midi_song_dir / "version.mid"
        midi_path.write_text("original")

        results = process_alternatives(csv_alt_dir, midi_alt_dir, force=False)

        assert len(results) == 0
        assert midi_path.read_text() == "original"

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test that nonexistent csv_alt directory returns empty results."""
        csv_alt_dir = tmp_path / "nonexistent"
        midi_alt_dir = tmp_path / "midi_alt"

        results = process_alternatives(csv_alt_dir, midi_alt_dir)

        assert len(results) == 0

    def test_ignores_files_in_root(self, tmp_path: Path) -> None:
        """Test that CSV files directly in csv_alt (not in subdirs) are ignored."""
        csv_alt_dir = tmp_path / "csv_alt"
        midi_alt_dir = tmp_path / "midi_alt"
        csv_alt_dir.mkdir()

        # Create CSV directly in csv_alt (should be ignored)
        csv_path = csv_alt_dir / "orphan.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["onset", "offset", "onpitch"])
            writer.writerow([0.0, 1.0, 60.0])

        results = process_alternatives(csv_alt_dir, midi_alt_dir)

        assert len(results) == 0
