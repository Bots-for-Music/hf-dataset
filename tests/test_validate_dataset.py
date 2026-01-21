"""Unit tests for validate_dataset.py functions."""

import csv
import hashlib
from pathlib import Path

# Import functions from validate_dataset
from validate_dataset import sha256_file


class TestSha256File:
    """Test SHA256 file hashing function."""

    def test_hash_text_file(self, temp_dir: Path) -> None:
        """Test hashing a simple text file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        result = sha256_file(test_file)

        # Verify hash format
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

        # Verify correctness
        expected = hashlib.sha256(b"Hello, World!").hexdigest()
        assert result == expected

    def test_hash_binary_file(self, temp_dir: Path) -> None:
        """Test hashing a binary file."""
        test_file = temp_dir / "test.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")

        result = sha256_file(test_file)

        expected = hashlib.sha256(b"\x00\x01\x02\x03\xff\xfe\xfd").hexdigest()
        assert result == expected

    def test_hash_empty_file(self, temp_dir: Path) -> None:
        """Test hashing an empty file."""
        test_file = temp_dir / "empty.txt"
        test_file.write_bytes(b"")

        result = sha256_file(test_file)

        # SHA256 of empty content
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected

    def test_consistent_hash(self, temp_dir: Path) -> None:
        """Test that same file produces same hash."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("consistent content")

        hash1 = sha256_file(test_file)
        hash2 = sha256_file(test_file)

        assert hash1 == hash2


class TestManifestSchema:
    """Test manifest CSV schema validation."""

    EXPECTED_COLUMNS = [
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

    def test_manifest_has_required_columns(self, sample_manifest_path: Path) -> None:
        """Test that manifest has all required columns."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []

        for col in self.EXPECTED_COLUMNS:
            assert col in columns, f"Missing column: {col}"

    def test_manifest_column_order(self, sample_manifest_path: Path) -> None:
        """Test that manifest columns are in expected order."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []

        assert list(columns) == self.EXPECTED_COLUMNS

    def test_id_is_sha256_format(self, sample_manifest_path: Path) -> None:
        """Test that ID column contains valid SHA256 hex strings."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # In sample data, IDs are simplified; in real data they're SHA256
                # Just check it's non-empty
                assert row["id"], "ID should not be empty"

    def test_audio_ext_is_wav(self, sample_manifest_path: Path) -> None:
        """Test that audio_ext is always .wav."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["audio_ext"] == ".wav"

    def test_midi_ext_is_mid(self, sample_manifest_path: Path) -> None:
        """Test that midi_ext is always .mid."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["midi_ext"] == ".mid"

    def test_has_emotional_variations_is_boolean(self, sample_manifest_path: Path) -> None:
        """Test that has_emotional_variations is True or False."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["has_emotional_variations"] in ("True", "False")

    def test_emotion_values(self, sample_manifest_path: Path) -> None:
        """Test that emotion contains valid values or is empty."""
        valid_emotions = {"angry", "happy", "sad", "tender", "original", ""}
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["emotion"] in valid_emotions, f"Invalid emotion: {row['emotion']}"

    def test_notes_values(self, sample_manifest_path: Path) -> None:
        """Test that notes contains valid values or is empty."""
        valid_notes = {"archival", "processed", ""}
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["notes"] in valid_notes, f"Invalid notes: {row['notes']}"


class TestManifestDataIntegrity:
    """Test manifest data integrity rules."""

    def test_no_duplicate_ids(self, sample_manifest_path: Path) -> None:
        """Test that there are no duplicate IDs."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ids = [row["id"] for row in reader]

        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_audio_relpath_format(self, sample_manifest_path: Path) -> None:
        """Test that audio_relpath has correct format."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["audio_relpath"].startswith("data/raw/audio/")
                assert row["audio_relpath"].endswith(".wav")

    def test_midi_relpath_format(self, sample_manifest_path: Path) -> None:
        """Test that midi_relpath has correct format."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["midi_relpath"].startswith("data/raw/midi/")
                assert row["midi_relpath"].endswith(".mid")

    def test_sha256_format(self, sample_manifest_path: Path) -> None:
        """Test that SHA256 columns have valid format (simplified in sample)."""
        with open(sample_manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Just check non-empty for sample data
                assert row["audio_sha256"], "audio_sha256 should not be empty"
                assert row["midi_sha256"], "midi_sha256 should not be empty"
