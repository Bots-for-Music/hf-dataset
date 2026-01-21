# Norwegian Folk Music Audio-MIDI Dataset

A paired audio and MIDI dataset of Norwegian folk music for training audio-to-MIDI transcription models.

## Dataset Summary

- **Total pairs:** 118 audio-MIDI pairs
- **Unique songs:** 38
- **Total size:** ~970 MB
- **Audio format:** WAV
- **MIDI format:** Standard MIDI (.mid)

## Quick Start

### Download and Install

```bash
# Clone the repository
git clone https://github.com/Bots-for-Music/hf-dataset.git
cd hf-dataset

# Install dependencies (including dev tools)
pip install -e ".[dev]"

# Pull data from DVC remote (~970MB from Google Drive)
dvc pull
```

### Verify Installation

```bash
# Run validation
python scripts/validate_dataset.py

# Check reports
cat reports/validate.json | python -m json.tool
```

## Dataset Structure

```
hf-dataset/
├── data/
│   ├── raw/
│   │   ├── audio/    # 118 .wav files
│   │   └── midi/     # 118 .mid files
│   └── manifests/
│       └── manifest.csv
├── scripts/
│   ├── build_manifest.py
│   ├── validate_dataset.py
│   ├── check_midi_health.py
│   └── check_audio_health.py
├── tests/
│   ├── test_build_manifest.py
│   ├── test_validate_dataset.py
│   └── test_integration.py
├── reports/
│   ├── validate.json
│   ├── midi_health.json
│   └── audio_health.json
├── .github/workflows/
│   └── ci.yaml
├── dvc.yaml
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

## File Categories

### Songs with Emotional Variations (20 songs, 100 pairs)

These songs have 5 variants each: `angry`, `happy`, `sad`, `tender`, and `original`:

Fuglesangen, Godvaersdagen, GroHolto, Haslebuskane, Havbrusen, IvarJorde, Klunkelatten, Kongelatten, Langaakern, LattenSomBedOmNoko, Perigarden, Silkjegulen, Solmoy, Strandaspringar, Tjednbalen, Toingen, Valdresspringar, Vossarull, SigneUladalen, Spretten

### Songs without Emotional Variations (18 pairs)

**Processed recordings (12):**
Baggen, Baustadtoppen, Den_eldste, Goffala_tten, Kaatereiar, Leinen, Mandagsmorgon, Myregutspringar, Peisestugu, Rande-Ambjor2, StoreDekken, Vrengja

**Archival recordings (6):**
Historical recordings from Norwegian folk music archives.

## Manifest Columns

| Column | Description |
|--------|-------------|
| id | SHA256 hash of audio:midi path pair (deterministic) |
| song_name | Base song name |
| audio_relpath | Relative path to audio file |
| midi_relpath | Relative path to MIDI file |
| audio_sha256 | Audio file checksum |
| midi_sha256 | MIDI file checksum |
| audio_ext | `.wav` |
| midi_ext | `.mid` |
| has_emotional_variations | Boolean - true if song has emotional variants |
| emotion | Emotion tag if present (angry, happy, sad, tender, original) |
| notes | `archival`, `processed`, or empty |

## Python Usage Examples

### Loading the Manifest

```python
import csv
from pathlib import Path

# Load manifest
with open('data/manifests/manifest.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total pairs: {len(rows)}")
print(f"Unique songs: {len(set(r['song_name'] for r in rows))}")
```

### Loading Audio/MIDI Pairs

```python
import soundfile as sf
import mido

def load_pair(row, repo_root='.'):
    """Load an audio/MIDI pair from a manifest row."""
    audio_path = Path(repo_root) / row['audio_relpath']
    midi_path = Path(repo_root) / row['midi_relpath']

    # Load audio
    audio, sr = sf.read(audio_path)

    # Load MIDI
    midi = mido.MidiFile(midi_path)

    return audio, sr, midi

# Example: load first pair
audio, sr, midi = load_pair(rows[0])
print(f"Audio: {len(audio)/sr:.2f}s at {sr}Hz")
print(f"MIDI: {len(midi.tracks)} tracks, {midi.length:.2f}s")
```

### Filtering by Emotion

```python
# Get all 'happy' variants
happy_rows = [r for r in rows if r['emotion'] == 'happy']
print(f"Happy variants: {len(happy_rows)}")

# Get all original recordings
originals = [r for r in rows if r['emotion'] == 'original']
print(f"Original recordings: {len(originals)}")
```

### Creating Train/Val/Test Splits

```python
import random

# Get unique song names
song_names = list(set(r['song_name'] for r in rows))
random.shuffle(song_names)

# Split by song (80/10/10)
n = len(song_names)
train_songs = set(song_names[:int(0.8 * n)])
val_songs = set(song_names[int(0.8 * n):int(0.9 * n)])
test_songs = set(song_names[int(0.9 * n):])

# Create splits
train_rows = [r for r in rows if r['song_name'] in train_songs]
val_rows = [r for r in rows if r['song_name'] in val_songs]
test_rows = [r for r in rows if r['song_name'] in test_songs]

print(f"Train: {len(train_rows)} pairs from {len(train_songs)} songs")
print(f"Val: {len(val_rows)} pairs from {len(val_songs)} songs")
print(f"Test: {len(test_rows)} pairs from {len(test_songs)} songs")
```

## How to Add a New Song

1. **Prepare files**: Ensure WAV and MIDI files have matching base names (e.g., `MySong_happy.wav` and `MySong_happy.mid`)

2. **Copy files to data directories**:
   ```bash
   cp MySong_happy.wav data/raw/audio/
   cp MySong_happy.mid data/raw/midi/
   ```

3. **Run health checks on new files**:
   ```bash
   python scripts/check_audio_health.py data/raw/audio/MySong_happy.wav
   python scripts/check_midi_health.py data/raw/midi/MySong_happy.mid
   ```

4. **Rebuild manifest**:
   ```bash
   dvc repro build_manifest
   ```

5. **Validate dataset**:
   ```bash
   dvc repro validate
   ```

6. **Track with DVC**:
   ```bash
   dvc add data/raw
   ```

7. **Commit and push**:
   ```bash
   git add data/raw.dvc data/manifests/manifest.csv
   git commit -m "Add MySong_happy"
   dvc push
   git push
   ```

## Running the DVC Pipeline

```bash
# Run the full pipeline (build manifest + validate + health checks)
dvc repro

# Or run individual stages
dvc repro build_manifest
dvc repro validate
dvc repro check_midi
dvc repro check_audio
```

## Health Checks

### MIDI Health Check

```bash
python scripts/check_midi_health.py data/raw/midi/ -o reports/midi_health.json
```

Validates:
- Valid MIDI format
- Contains at least 1 note
- Reasonable pitch range (21-108 +/- 12)
- Duration sanity check

### Audio Health Check

```bash
python scripts/check_audio_health.py data/raw/audio/ -o reports/audio_health.json
```

Validates:
- Valid WAV format
- Reasonable duration (5-300s)
- Not silent (>10% non-silent samples)
- Clipping detection

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/ --ignore=tests/test_integration.py -v

# Run all tests (requires data)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html
```

### Linting and Type Checking

```bash
# Run linter
ruff check scripts/ tests/

# Run formatter
ruff format scripts/ tests/

# Run type checker
mypy scripts/
```

## Train/Val/Test Splits

Splits are not baked into the manifest. Determine splits at training time based on your needs. Recommended approach: split by song name (not by individual pairs) to prevent data leakage.

## License

Contact the dataset maintainers for licensing information.

## Citation

If you use this dataset, please cite appropriately.
