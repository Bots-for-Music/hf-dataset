"""Pytest configuration and fixtures for hf-dataset tests."""

import csv
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Add scripts directory to path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return REPO_ROOT


@pytest.fixture
def data_dir(repo_root: Path) -> Path:
    """Return the data directory path."""
    return repo_root / "data"


@pytest.fixture
def audio_dir(data_dir: Path) -> Path:
    """Return the audio directory path."""
    return data_dir / "raw" / "audio"


@pytest.fixture
def midi_dir(data_dir: Path) -> Path:
    """Return the MIDI directory path."""
    return data_dir / "raw" / "midi"


@pytest.fixture
def manifest_path(data_dir: Path) -> Path:
    """Return the manifest file path."""
    return data_dir / "manifests" / "manifest.csv"


@pytest.fixture
def data_available(audio_dir: Path, midi_dir: Path) -> bool:
    """Check if dataset files are available (for integration tests)."""
    if not audio_dir.exists() or not midi_dir.exists():
        return False
    audio_files = list(audio_dir.glob("*.wav"))
    midi_files = list(midi_dir.glob("*.mid"))
    return len(audio_files) > 0 and len(midi_files) > 0


@pytest.fixture
def manifest_rows(manifest_path: Path) -> list[dict[str, str]]:
    """Load manifest rows if available."""
    if not manifest_path.exists():
        pytest.skip("Manifest not available")
    with open(manifest_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_manifest_content() -> str:
    """Return sample manifest CSV content for testing."""
    return """id,song_name,audio_relpath,midi_relpath,audio_sha256,midi_sha256,audio_ext,midi_ext,has_emotional_variations,emotion,notes
abc123,TestSong,data/raw/audio/TestSong_happy.wav,data/raw/midi/TestSong_happy.mid,sha256audio,sha256midi,.wav,.mid,True,happy,
def456,TestSong,data/raw/audio/TestSong_sad.wav,data/raw/midi/TestSong_sad.mid,sha256audio2,sha256midi2,.wav,.mid,True,sad,
ghi789,ArchivalSong,data/raw/audio/00001-Artist-Song.wav,data/raw/midi/00001-Artist-Song.mid,sha256audio3,sha256midi3,.wav,.mid,False,,archival"""


@pytest.fixture
def sample_manifest_path(temp_dir: Path, sample_manifest_content: str) -> Path:
    """Create a sample manifest file in temp directory."""
    manifest_path = temp_dir / "manifest.csv"
    manifest_path.write_text(sample_manifest_content)
    return manifest_path
