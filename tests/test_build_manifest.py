"""Unit tests for build_manifest.py functions."""

import pytest

# Import functions from build_manifest
from build_manifest import extract_emotion, extract_song_name, sha256_string


class TestExtractSongName:
    """Test song name extraction from various filename patterns."""

    def test_simple_emotion_suffix(self) -> None:
        """Test extraction from simple emotion-suffixed filenames."""
        assert extract_song_name("Fuglesangen_angry.wav") == "Fuglesangen"
        assert extract_song_name("Fuglesangen_happy.wav") == "Fuglesangen"
        assert extract_song_name("Fuglesangen_sad.wav") == "Fuglesangen"
        assert extract_song_name("Fuglesangen_tender.wav") == "Fuglesangen"
        assert extract_song_name("Fuglesangen_original.wav") == "Fuglesangen"

    def test_original1_variant(self) -> None:
        """Test extraction from original1 variant filenames."""
        assert extract_song_name("Fuglesangen_original1.wav") == "Fuglesangen"
        assert extract_song_name("GroHolto_original1.mid") == "GroHolto"

    def test_processed_with_timestamp(self) -> None:
        """Test extraction from processed filenames with timestamps."""
        name = "Baggen_happy_torr_02-Dec-2024_09-04-07_02-Dec-2024_09-37-47_02-Dec-2024_13-40-54.mid_cleaned.wav"
        assert extract_song_name(name) == "Baggen"

        name = "Baustadtoppen_original_torr_05-Dec-2024_13-12-57_05-Dec-2024_15-03-52.mid_cleaned.wav"
        assert extract_song_name(name) == "Baustadtoppen"

    def test_archival_with_number_prefix(self) -> None:
        """Test extraction from archival filenames with number prefix."""
        assert extract_song_name("00106-Furholt Otto-Fiskaren.wav") == "00106-Furholt Otto-Fiskaren"
        assert extract_song_name("00108-Furholt Otto-Sordølen.wav") == "00108-Furholt Otto-Sordølen"
        assert extract_song_name("01267-Ørpen Truls Gunnarson-Springar fra Krødsherad.wav") == "01267-Ørpen Truls Gunnarson-Springar fra Krødsherad"

    def test_cleaned_suffix(self) -> None:
        """Test extraction from filenames with _cleaned suffix."""
        name = "Peisestugu_original_torr_filtered_06-Jan-2025_13-43-39.mid_cleaned.wav"
        assert extract_song_name(name) == "Peisestugu"

    def test_mid_extension(self) -> None:
        """Test that extraction works for both .wav and .mid extensions."""
        assert extract_song_name("Solmoy_tender.mid") == "Solmoy"
        assert extract_song_name("Solmoy_tender.wav") == "Solmoy"


class TestExtractEmotion:
    """Test emotion tag extraction from filenames."""

    def test_angry_emotion(self) -> None:
        """Test extraction of angry emotion."""
        assert extract_emotion("Fuglesangen_angry.wav") == "angry"
        assert extract_emotion("GroHolto_angry.mid") == "angry"

    def test_happy_emotion(self) -> None:
        """Test extraction of happy emotion."""
        assert extract_emotion("Fuglesangen_happy.wav") == "happy"
        assert extract_emotion("Baggen_happy_torr_02-Dec-2024.mid_cleaned.wav") == "happy"

    def test_sad_emotion(self) -> None:
        """Test extraction of sad emotion."""
        assert extract_emotion("Solmoy_sad.wav") == "sad"

    def test_tender_emotion(self) -> None:
        """Test extraction of tender emotion."""
        assert extract_emotion("GroHolto_tender.mid") == "tender"

    def test_original_emotion(self) -> None:
        """Test extraction of original emotion."""
        assert extract_emotion("Spretten_original.wav") == "original"

    def test_original1_maps_to_original(self) -> None:
        """Test that original1 maps to 'original'."""
        assert extract_emotion("Fuglesangen_original1.wav") == "original"
        assert extract_emotion("GroHolto_original1.mid") == "original"

    def test_archival_no_emotion(self) -> None:
        """Test that archival files return None."""
        assert extract_emotion("00106-Furholt Otto-Fiskaren.wav") is None
        assert extract_emotion("00108-Furholt Otto-Sordølen.mid") is None

    def test_processed_with_emotion(self) -> None:
        """Test processed files with emotion in path."""
        name = "Baustadtoppen_original_torr_05-Dec-2024_13-12-57.mid_cleaned.wav"
        assert extract_emotion(name) == "original"


class TestSha256String:
    """Test SHA256 string hashing function."""

    def test_consistent_hash(self) -> None:
        """Test that same input produces same hash."""
        input_str = "data/raw/audio/test.wav:data/raw/midi/test.mid"
        hash1 = sha256_string(input_str)
        hash2 = sha256_string(input_str)
        assert hash1 == hash2

    def test_different_input_different_hash(self) -> None:
        """Test that different inputs produce different hashes."""
        hash1 = sha256_string("input1")
        hash2 = sha256_string("input2")
        assert hash1 != hash2

    def test_hash_format(self) -> None:
        """Test that hash is valid hex string of correct length."""
        result = sha256_string("test")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_empty_string(self) -> None:
        """Test hashing empty string."""
        result = sha256_string("")
        assert len(result) == 64
        # SHA256 of empty string is known
        assert result == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_unicode_handling(self) -> None:
        """Test that unicode characters are handled correctly."""
        result = sha256_string("Sordølen")
        assert len(result) == 64
