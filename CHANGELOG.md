# Changelog

All notable changes to this dataset will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-01-21

### Added
- `pyproject.toml` for package configuration and dependencies
- MIDI health check script (`scripts/check_midi_health.py`)
  - Validates MIDI format, note count, pitch range, and duration
  - Generates JSON health reports
- Audio health check script (`scripts/check_audio_health.py`)
  - Validates WAV format, duration, silence detection, and clipping
  - Generates JSON health reports
- Test infrastructure with pytest
  - Unit tests for `build_manifest.py` functions
  - Unit tests for `validate_dataset.py` functions
  - Integration tests for full dataset validation
  - Fixtures in `conftest.py` for test utilities
- GitHub Actions CI workflow (`.github/workflows/ci.yaml`)
  - Linting with ruff
  - Type checking with mypy
  - Unit tests on every PR
  - Full validation on merge to main
- DVC pipeline stages for health checks (`check_midi`, `check_audio`)

### Changed
- Enhanced README with:
  - Quick start guide with download instructions
  - Python usage examples (loading manifest, audio/MIDI pairs, filtering)
  - Guide for adding new songs
  - Health check documentation
  - Development instructions (testing, linting)
- Updated dataset structure documentation

## [0.1.0] - 2026-01-21

### Added
- Initial dataset version
- 118 audio-MIDI pairs from Norwegian folk music
- 20 songs with emotional variations (angry, happy, sad, tender, original)
- 18 songs without emotional variations (12 processed, 6 archival)
- Manifest with checksums and metadata
- DVC pipeline for reproducible builds
- Validation script with integrity checks
