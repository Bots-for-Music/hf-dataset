"""Integration tests for hf-dataset.

These tests require the actual dataset files to be present.
They are skipped if data is not available.
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
class TestManifestIntegrity:
    """Integration tests for manifest integrity."""

    def test_manifest_exists(self, manifest_path: Path, data_available: bool) -> None:
        """Test that manifest file exists."""
        if not data_available:
            pytest.skip("Dataset files not available")
        assert manifest_path.exists(), f"Manifest not found at {manifest_path}"

    def test_manifest_row_count(
        self, manifest_path: Path, manifest_rows: list[dict[str, str]], data_available: bool
    ) -> None:
        """Test that manifest has expected number of rows (118)."""
        if not data_available:
            pytest.skip("Dataset files not available")
        assert len(manifest_rows) == 118, f"Expected 118 rows, got {len(manifest_rows)}"

    def test_no_duplicate_ids(
        self, manifest_rows: list[dict[str, str]], data_available: bool
    ) -> None:
        """Test that there are no duplicate IDs in manifest."""
        if not data_available:
            pytest.skip("Dataset files not available")
        ids = [row["id"] for row in manifest_rows]
        duplicates = [id for id in ids if ids.count(id) > 1]
        assert len(duplicates) == 0, f"Duplicate IDs found: {set(duplicates)}"

    def test_unique_song_count(
        self, manifest_rows: list[dict[str, str]], data_available: bool
    ) -> None:
        """Test that there are 38 unique songs."""
        if not data_available:
            pytest.skip("Dataset files not available")
        song_names = {row["song_name"] for row in manifest_rows}
        assert len(song_names) == 38, f"Expected 38 unique songs, got {len(song_names)}"


@pytest.mark.integration
class TestFileExistence:
    """Integration tests for file existence."""

    def test_all_audio_files_exist(
        self,
        repo_root: Path,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that all audio files referenced in manifest exist."""
        if not data_available:
            pytest.skip("Dataset files not available")
        missing = []
        for row in manifest_rows:
            audio_path = repo_root / row["audio_relpath"]
            if not audio_path.exists():
                missing.append(row["audio_relpath"])
        assert len(missing) == 0, f"Missing audio files: {missing}"

    def test_all_midi_files_exist(
        self,
        repo_root: Path,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that all MIDI files referenced in manifest exist."""
        if not data_available:
            pytest.skip("Dataset files not available")
        missing = []
        for row in manifest_rows:
            midi_path = repo_root / row["midi_relpath"]
            if not midi_path.exists():
                missing.append(row["midi_relpath"])
        assert len(missing) == 0, f"Missing MIDI files: {missing}"

    def test_audio_midi_pairs_match(
        self,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that audio and MIDI files have matching base names."""
        if not data_available:
            pytest.skip("Dataset files not available")
        for row in manifest_rows:
            audio_stem = Path(row["audio_relpath"]).stem
            midi_stem = Path(row["midi_relpath"]).stem
            assert (
                audio_stem == midi_stem
            ), f"Mismatched stems: audio={audio_stem}, midi={midi_stem}"


@pytest.mark.integration
class TestValidationScript:
    """Integration tests for validation script."""

    def test_validation_script_passes(self, repo_root: Path, data_available: bool) -> None:
        """Test that validate_dataset.py passes when data is available."""
        if not data_available:
            pytest.skip("Dataset files not available")

        script_path = repo_root / "scripts" / "validate_dataset.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert (
            result.returncode == 0
        ), f"Validation failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
class TestEmotionalVariations:
    """Integration tests for emotional variations."""

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

    EMOTIONS = {"angry", "happy", "sad", "tender", "original"}

    def test_songs_with_variations_have_all_emotions(
        self,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that songs with variations have all 5 emotion variants."""
        if not data_available:
            pytest.skip("Dataset files not available")

        # Group by song name
        song_emotions: dict[str, set[str]] = {}
        for row in manifest_rows:
            if row["has_emotional_variations"] == "True":
                song_name = row["song_name"]
                emotion = row["emotion"]
                if song_name not in song_emotions:
                    song_emotions[song_name] = set()
                if emotion:
                    song_emotions[song_name].add(emotion)

        for song_name, emotions in song_emotions.items():
            assert emotions == self.EMOTIONS, (
                f"Song {song_name} missing emotions. " f"Has: {emotions}, Expected: {self.EMOTIONS}"
            )

    def test_correct_songs_marked_with_variations(
        self,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that correct songs are marked as having variations."""
        if not data_available:
            pytest.skip("Dataset files not available")

        for row in manifest_rows:
            song_name = row["song_name"]
            has_variations = row["has_emotional_variations"] == "True"

            if song_name in self.SONGS_WITH_VARIATIONS:
                assert has_variations, f"Song {song_name} should have has_emotional_variations=True"


@pytest.mark.integration
class TestArchivalRecordings:
    """Integration tests for archival recordings."""

    def test_archival_recordings_have_notes(
        self,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that archival recordings have notes='archival'."""
        if not data_available:
            pytest.skip("Dataset files not available")

        for row in manifest_rows:
            # Archival files start with 5-digit numbers
            if row["song_name"].startswith(("00", "01")):
                assert (
                    row["notes"] == "archival"
                ), f"Archival recording {row['song_name']} should have notes='archival'"

    def test_archival_recordings_no_emotion(
        self,
        manifest_rows: list[dict[str, str]],
        data_available: bool,
    ) -> None:
        """Test that archival recordings have no emotion tag."""
        if not data_available:
            pytest.skip("Dataset files not available")

        for row in manifest_rows:
            if row["notes"] == "archival":
                assert (
                    row["emotion"] == ""
                ), f"Archival recording {row['song_name']} should have no emotion"
