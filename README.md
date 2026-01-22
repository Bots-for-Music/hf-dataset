# HF2: Hardanger Fiddle Dataset

> A dataset from the University of Oslo

A paired audio and MIDI dataset of Norwegian folk music for training audio-to-MIDI transcription models.

## Dataset Summary

- **Total pairs:** 119 audio-MIDI pairs
- **Unique songs:** 39
- **Total size:** ~970 MB
- **Audio format:** WAV
- **MIDI format:** Standard MIDI (.mid)
- **CSV ground truth:** High-precision pitch data (where available)

## Related Resources

This dataset extends the original HF1 dataset and uses the same transcription methodology.

- **HF1 Dataset**: [RITMO HF1 Database](https://www.uio.no/ritmo/english/projects/mirage/databases/hf1/) - Original 43-minute dataset with 19,734 annotated notes
- **Research Paper**: [A Dataset of Norwegian Hardanger Fiddle Recordings with Precise Annotation](https://transactions.ismir.net/articles/10.5334/tismir.139) (TISMIR)
- **Transcription Demo**: [YouTube video](https://www.youtube.com/watch?v=UCWNubM7zFU) showing the annotation process

## Dataset Contents

| Category | Songs | Pairs | Description |
|----------|-------|-------|-------------|
| Emotional variants | 20 | 100 | Each song has 5 versions: original, angry, happy, sad, tender |
| Processed recordings | 12 | 12 | Single transcriptions from recent recordings |
| Archival recordings | 7 | 7 | Historical recordings from the National Library |

**Total: 39 unique songs, 119 audio-MIDI pairs**

See [docs/FILELIST.md](docs/FILELIST.md) for the complete file list.

## Download Options

### For Public Users (Recommended)

Clone the repository, then download data from Hugging Face:

```bash
git clone https://github.com/Bots-for-Music/hf-dataset.git
cd hf-dataset
pip install huggingface_hub
huggingface-cli download Bots4M/HF2-Hardanger-fiddle-dataset --local-dir . --repo-type dataset
```

### For Developers (DVC)

Use DVC for development with write access to the data:

```bash
git clone https://github.com/Bots-for-Music/hf-dataset.git
cd hf-dataset
pip install -e ".[dev]"
dvc pull  # Requires Google account with access
```

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
│   │   ├── audio/      # 119 .wav files
│   │   ├── midi/       # 119 .mid files (primary transcriptions)
│   │   ├── csv/        # Ground truth CSV files (high-precision pitch)
│   │   ├── csv_alt/    # Alternative transcriptions
│   │   │   └── {song_name}/
│   │   │       ├── roughpitch.csv
│   │   │       └── other_version.csv
│   │   └── midi_alt/   # Alternative MIDI (from csv_alt)
│   │       └── {song_name}/
│   │           ├── roughpitch.mid
│   │           └── other_version.mid
│   └── manifests/
│       └── manifest.csv
├── scripts/
│   ├── build_manifest.py
│   ├── validate_dataset.py
│   ├── check_midi_health.py
│   ├── check_audio_health.py
│   └── csv_to_midi.py
├── tests/
│   ├── test_build_manifest.py
│   ├── test_validate_dataset.py
│   ├── test_csv_to_midi.py
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

## CSV Ground Truth Files

The MIDI files in this dataset are generated from CSV files containing high-precision pitch data. Since MIDI only supports integer pitches (0-127), the original CSV files are preserved in `data/raw/csv/` as ground truth for research purposes.

### CSV Format

| Column | Description |
|--------|-------------|
| onset | Note start time in seconds |
| offset | Note end time in seconds |
| onpitch | Pitch at note onset (float, e.g., 78.36) |
| offpitch | Pitch at note offset |
| essential | Essential note flag |
| bar | Bar number |
| upmeter | Upper meter position |
| lowmeter | Lower meter position |
| offmeter | Offset meter position |
| notetype | Note type indicator |
| alignidx | Alignment index |
| file1idx | File 1 index |
| file2idx | File 2 index |
| metralign | Metrical alignment |
| previous | Previous note index |
| next | Next note index |

### Why CSV Matters

MIDI pitches are integers, so a pitch of `78.36` becomes `78` in MIDI. For research requiring sub-semitone accuracy (microtonal analysis, pitch drift studies, etc.), use the original CSV files.

### Converting CSV to MIDI

```bash
# Convert a single file
python scripts/csv_to_midi.py input.csv -o output.mid

# Convert all CSVs in directory
python scripts/csv_to_midi.py data/raw/csv/ --midi-dir data/raw/midi/

# Auto-convert via DVC pipeline
dvc repro convert_csv
```

### Loading CSV Data

```python
import csv

def load_csv_notes(csv_path):
    """Load notes from CSV with full precision."""
    notes = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            notes.append({
                'onset': float(row['onset']),
                'offset': float(row['offset']),
                'pitch': float(row['onpitch']),  # Full precision!
            })
    return notes

# Example: compare CSV vs MIDI pitch
csv_notes = load_csv_notes('data/raw/csv/song.csv')
print(f"CSV pitch: {csv_notes[0]['pitch']:.2f}")  # e.g., 78.36
print(f"MIDI pitch: {round(csv_notes[0]['pitch'])}")  # e.g., 78
```

### Alternative Transcriptions

Some songs have multiple transcription versions (e.g., different pitch detection algorithms). These are stored separately from the primary transcriptions:

```
data/raw/csv_alt/{song_name}/version.csv  →  data/raw/midi_alt/{song_name}/version.mid
```

Alternative transcriptions are **not** included in the manifest (no audio pairing). They serve as reference for comparing transcription methods.

```bash
# Convert alternative transcriptions
python scripts/csv_to_midi.py --alternatives data/raw/csv_alt/ --midi-dir data/raw/midi_alt/

# Or via DVC pipeline
dvc repro convert_csv_alt
```

**Current alternative transcriptions:**

| Song | Version | Description |
|------|---------|-------------|
| 00058-Dahle Johannes Knutson-Tussebrureferda på Vossevangen | roughpitch.csv | Raw pitch detection (before autotuning) |

## Data Augmentation

This dataset works with [amt-augmentor](https://github.com/LarsMonstad/amt-augmentor) for augmenting audio-MIDI pairs while keeping them synchronized.

```bash
# Install amt-augmentor
pip install amt-augmentor

# Augment the dataset (time stretch, pitch shift, reverb, etc.)
amt-augment data/raw/audio/ data/raw/midi/ --output augmented/
```

The augmentor supports:
- Time stretching (tempo changes while preserving pitch)
- Pitch shifting (transposition while preserving timing)
- Reverb, filtering, gain, chorus effects
- Noise addition for robustness training

See the [amt-augmentor documentation](https://github.com/LarsMonstad/amt-augmentor) for configuration options.

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

The dataset supports three input combinations:

| Input Files | Behavior |
|-------------|----------|
| audio + csv | CSV auto-converts to MIDI |
| audio + midi | MIDI used directly |
| audio + midi + csv | MIDI used, CSV stored as reference (no overwrite) |

### Steps

1. **Copy files to data directories** (use matching base names):
   ```bash
   # Always required
   cp MySong.wav data/raw/audio/

   # Add CSV if you have high-precision ground truth
   cp MySong.csv data/raw/csv/

   # Add MIDI if you have it (or let CSV auto-convert)
   cp MySong.mid data/raw/midi/
   ```

2. **Run the pipeline**:
   ```bash
   dvc repro
   ```
   This will:
   - Convert any CSV files to MIDI (skips if MIDI already exists)
   - Rebuild the manifest
   - Validate the dataset
   - Run health checks

3. **Track and push**:
   ```bash
   dvc add data/raw
   git add data/raw.dvc data/manifests/manifest.csv
   git commit -m "Add MySong"
   dvc push && git push
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

## Releasing to Hugging Face

To publish a dataset release to Hugging Face:

```bash
# 1. Tag release
git tag dataset-v0.1.0
git push --tags
dvc push

# 2. Publish to Hugging Face
python scripts/publish_to_huggingface.py --version v0.1.0

# Or dry-run first
python scripts/publish_to_huggingface.py --version v0.1.0 --dry-run
```

The publish script includes safety checks:
- Verifies HEAD is at an exact git tag
- Verifies tag matches `--version` argument
- Warns if working tree has uncommitted changes
- Use `--force` to override warnings

## License

CC-BY-4.0

## Contributors

- [Olivier Lartillot](https://github.com/olivierlar) - University of Oslo
- [Lars Monstad](https://github.com/LarsMonstad) - University of Oslo

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{lartillot2025hf2,
  title={HF2: Hardanger Fiddle Dataset},
  author={Lartillot, Olivier and Monstad, Lars},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/datasets/Bots4M/HF2-Hardanger-fiddle-dataset},
  institution={University of Oslo}
}
```
