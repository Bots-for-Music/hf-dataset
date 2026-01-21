# Norwegian Folk Music Audio-MIDI Dataset

A paired audio and MIDI dataset of Norwegian folk music for training audio-to-MIDI transcription models.

## Dataset Summary

- **Total pairs:** 119 audio-MIDI pairs
- **Unique songs:** 39
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

## Song List

### Songs with Emotional Variations (20 songs, 100 pairs)

Each song has 5 variants: `angry`, `happy`, `sad`, `tender`, and `original`.

| # | Song Name |
|---|-----------|
| 1 | Fuglesangen |
| 2 | Godvaersdagen |
| 3 | GroHolto |
| 4 | Haslebuskane |
| 5 | Havbrusen |
| 6 | IvarJorde |
| 7 | Klunkelatten |
| 8 | Kongelatten |
| 9 | Langaakern |
| 10 | LattenSomBedOmNoko |
| 11 | Perigarden |
| 12 | SigneUladalen |
| 13 | Silkjegulen |
| 14 | Solmoy |
| 15 | Spretten |
| 16 | Strandaspringar |
| 17 | Tjednbalen |
| 18 | Toingen |
| 19 | Valdresspringar |
| 20 | Vossarull |

### Processed Recordings (12 pairs)

Single recordings without emotional variations.

| # | Song Name |
|---|-----------|
| 1 | Baggen |
| 2 | Baustadtoppen |
| 3 | Den_eldste |
| 4 | Goffala_tten |
| 5 | Kaatereiar |
| 6 | Leinen |
| 7 | Mandagsmorgon |
| 8 | Myregutspringar |
| 9 | Peisestugu |
| 10 | Rande-Ambjor2 |
| 11 | StoreDekken |
| 12 | Vrengja |

### Archival Recordings (7 pairs)

Historical recordings from Norwegian folk music archives.

| # | Song Name |
|---|-----------|
| 1 | 00058-Dahle Johannes Knutson-Tussebrureferda på Vossevangen |
| 2 | 00106-Furholt Otto-Fiskaren |
| 3 | 00108-Furholt Otto-Sordølen |
| 4 | 00365-Berge Per Olsson-Salmastubben |
| 5 | 00379-Berge Per Olsson-Skarsnuten |
| 6 | 01267-Ørpen Truls Gunnarson-Springar fra Krødsherad |
| 7 | 01309-Ørpen Truls Gunnarson-Springar |

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
