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
│   │   ├── audio/    # 119 .wav files
│   │   └── midi/     # 119 .mid files
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

## Complete File List

All 119 audio-MIDI pairs in the dataset (sorted alphabetically):

| Audio File | MIDI File |
|------------|-----------|
| 00058-Dahle Johannes Knutson-Tussebrureferda på Vossevangen.wav | 00058-Dahle Johannes Knutson-Tussebrureferda på Vossevangen.mid |
| 00106-Furholt Otto-Fiskaren.wav | 00106-Furholt Otto-Fiskaren.mid |
| 00108-Furholt Otto-Sordølen.wav | 00108-Furholt Otto-Sordølen.mid |
| 00365-Berge Per Olsson-Salmastubben.wav | 00365-Berge Per Olsson-Salmastubben.mid |
| 00379-Berge Per Olsson-Skarsnuten.wav | 00379-Berge Per Olsson-Skarsnuten.mid |
| 01267-Ørpen Truls Gunnarson-Springar fra Krødsherad.wav | 01267-Ørpen Truls Gunnarson-Springar fra Krødsherad.mid |
| 01309-Ørpen Truls Gunnarson-Springar.wav | 01309-Ørpen Truls Gunnarson-Springar.mid |
| Baggen_happy_torr_02-Dec-2024_09-04-07_02-Dec-2024_09-37-47_02-Dec-2024_13-40-54.mid_cleaned.wav | Baggen_happy_torr_02-Dec-2024_09-04-07_02-Dec-2024_09-37-47_02-Dec-2024_13-40-54.mid_cleaned.mid |
| Baustadtoppen_original_torr_05-Dec-2024_13-12-57_05-Dec-2024_15-03-52.mid_cleaned.wav | Baustadtoppen_original_torr_05-Dec-2024_13-12-57_05-Dec-2024_15-03-52.mid_cleaned.mid |
| Den_eldste_original_torr_filtered_unghosted_06-Jan-2025_16-55-57.mid_cleaned.wav | Den_eldste_original_torr_filtered_unghosted_06-Jan-2025_16-55-57.mid_cleaned.mid |
| Fuglesangen_angry.wav | Fuglesangen_angry.mid |
| Fuglesangen_happy.wav | Fuglesangen_happy.mid |
| Fuglesangen_original1.wav | Fuglesangen_original1.mid |
| Fuglesangen_sad.wav | Fuglesangen_sad.mid |
| Fuglesangen_tender.wav | Fuglesangen_tender.mid |
| Godvaersdagen_angry.wav | Godvaersdagen_angry.mid |
| Godvaersdagen_happy.wav | Godvaersdagen_happy.mid |
| Godvaersdagen_original1.wav | Godvaersdagen_original1.mid |
| Godvaersdagen_sad.wav | Godvaersdagen_sad.mid |
| Godvaersdagen_tender.wav | Godvaersdagen_tender.mid |
| Goffala_tten_original_torr_fil_tered_02-Jan-2025_14-31-49.mid_cleaned.wav | Goffala_tten_original_torr_fil_tered_02-Jan-2025_14-31-49.mid_cleaned.mid |
| GroHolto_angry.wav | GroHolto_angry.mid |
| GroHolto_happy.wav | GroHolto_happy.mid |
| GroHolto_original1.wav | GroHolto_original1.mid |
| GroHolto_sad.wav | GroHolto_sad.mid |
| GroHolto_tender.wav | GroHolto_tender.mid |
| Haslebuskane_angry.wav | Haslebuskane_angry.mid |
| Haslebuskane_happy.wav | Haslebuskane_happy.mid |
| Haslebuskane_original1.wav | Haslebuskane_original1.mid |
| Haslebuskane_sad.wav | Haslebuskane_sad.mid |
| Haslebuskane_tender.wav | Haslebuskane_tender.mid |
| Havbrusen_angry.wav | Havbrusen_angry.mid |
| Havbrusen_happy.wav | Havbrusen_happy.mid |
| Havbrusen_original1.wav | Havbrusen_original1.mid |
| Havbrusen_sad.wav | Havbrusen_sad.mid |
| Havbrusen_tender.wav | Havbrusen_tender.mid |
| IvarJorde_angry.wav | IvarJorde_angry.mid |
| IvarJorde_happy.wav | IvarJorde_happy.mid |
| IvarJorde_original1.wav | IvarJorde_original1.mid |
| IvarJorde_sad.wav | IvarJorde_sad.mid |
| IvarJorde_tender.wav | IvarJorde_tender.mid |
| Kaatereiar_original_torr_filtered_04-Jan-2025_11-37-24.mid_cleaned.wav | Kaatereiar_original_torr_filtered_04-Jan-2025_11-37-24.mid_cleaned.mid |
| Klunkelatten_angry.wav | Klunkelatten_angry.mid |
| Klunkelatten_happy.wav | Klunkelatten_happy.mid |
| Klunkelatten_original1.wav | Klunkelatten_original1.mid |
| Klunkelatten_sad.wav | Klunkelatten_sad.mid |
| Klunkelatten_tender.wav | Klunkelatten_tender.mid |
| Kongelatten_angry.wav | Kongelatten_angry.mid |
| Kongelatten_happy.wav | Kongelatten_happy.mid |
| Kongelatten_original1.wav | Kongelatten_original1.mid |
| Kongelatten_sad.wav | Kongelatten_sad.mid |
| Kongelatten_tender.wav | Kongelatten_tender.mid |
| Langaakern_angry.wav | Langaakern_angry.mid |
| Langaakern_happy.wav | Langaakern_happy.mid |
| Langaakern_original1.wav | Langaakern_original1.mid |
| Langaakern_sad.wav | Langaakern_sad.mid |
| Langaakern_tender.wav | Langaakern_tender.mid |
| LattenSomBedOmNoko_angry.wav | LattenSomBedOmNoko_angry.mid |
| LattenSomBedOmNoko_happy.wav | LattenSomBedOmNoko_happy.mid |
| LattenSomBedOmNoko_original1.wav | LattenSomBedOmNoko_original1.mid |
| LattenSomBedOmNoko_sad.wav | LattenSomBedOmNoko_sad.mid |
| LattenSomBedOmNoko_tender.wav | LattenSomBedOmNoko_tender.mid |
| Leinen_original_torr_filtered_04-Jan-2025_16-31-37.mid_cleaned.wav | Leinen_original_torr_filtered_04-Jan-2025_16-31-37.mid_cleaned.mid |
| Mandagsmorgon_original_torr_filtered_06-Jan-2025_10-42-50.mid_cleaned.wav | Mandagsmorgon_original_torr_filtered_06-Jan-2025_10-42-50.mid_cleaned.mid |
| Myregutspringar_original_torr_filtered_06-Jan-2025_12-15-36.mid_cleaned.wav | Myregutspringar_original_torr_filtered_06-Jan-2025_12-15-36.mid_cleaned.mid |
| Peisestugu_original_torr_filtered_06-Jan-2025_13-43-39.mid_cleaned.wav | Peisestugu_original_torr_filtered_06-Jan-2025_13-43-39.mid_cleaned.mid |
| Perigarden_angry.wav | Perigarden_angry.mid |
| Perigarden_happy.wav | Perigarden_happy.mid |
| Perigarden_original1.wav | Perigarden_original1.mid |
| Perigarden_sad.wav | Perigarden_sad.mid |
| Perigarden_tender.wav | Perigarden_tender.mid |
| Rande-Ambjor2_original_torr_filtered_06-Jan-2025_14-25-35.mid_cleaned_half.wav | Rande-Ambjor2_original_torr_filtered_06-Jan-2025_14-25-35.mid_cleaned_half.mid |
| SigneUladalen_angry.wav | SigneUladalen_angry.mid |
| SigneUladalen_happy.wav | SigneUladalen_happy.mid |
| SigneUladalen_original.wav | SigneUladalen_original.mid |
| SigneUladalen_sad.wav | SigneUladalen_sad.mid |
| SigneUladalen_tender.wav | SigneUladalen_tender.mid |
| Silkjegulen_angry.wav | Silkjegulen_angry.mid |
| Silkjegulen_happy.wav | Silkjegulen_happy.mid |
| Silkjegulen_original1.wav | Silkjegulen_original1.mid |
| Silkjegulen_sad.wav | Silkjegulen_sad.mid |
| Silkjegulen_tender.wav | Silkjegulen_tender.mid |
| Solmoy_angry.wav | Solmoy_angry.mid |
| Solmoy_happy.wav | Solmoy_happy.mid |
| Solmoy_original1.wav | Solmoy_original1.mid |
| Solmoy_sad.wav | Solmoy_sad.mid |
| Solmoy_tender.wav | Solmoy_tender.mid |
| Spretten_angry.wav | Spretten_angry.mid |
| Spretten_happy.wav | Spretten_happy.mid |
| Spretten_original.wav | Spretten_original.mid |
| Spretten_sad.wav | Spretten_sad.mid |
| Spretten_tender.wav | Spretten_tender.mid |
| StoreDekken_original_torr_filtered_06-Jan-2025_15-27-22.mid_cleaned_half.wav | StoreDekken_original_torr_filtered_06-Jan-2025_15-27-22.mid_cleaned_half.mid |
| Strandaspringar_angry.wav | Strandaspringar_angry.mid |
| Strandaspringar_happy.wav | Strandaspringar_happy.mid |
| Strandaspringar_original1.wav | Strandaspringar_original1.mid |
| Strandaspringar_sad.wav | Strandaspringar_sad.mid |
| Strandaspringar_tender.wav | Strandaspringar_tender.mid |
| Tjednbalen_angry.wav | Tjednbalen_angry.mid |
| Tjednbalen_happy.wav | Tjednbalen_happy.mid |
| Tjednbalen_original1.wav | Tjednbalen_original1.mid |
| Tjednbalen_sad.wav | Tjednbalen_sad.mid |
| Tjednbalen_tender.wav | Tjednbalen_tender.mid |
| Toingen_angry.wav | Toingen_angry.mid |
| Toingen_happy.wav | Toingen_happy.mid |
| Toingen_original1.wav | Toingen_original1.mid |
| Toingen_sad.wav | Toingen_sad.mid |
| Toingen_tender.wav | Toingen_tender.mid |
| Valdresspringar_angry.wav | Valdresspringar_angry.mid |
| Valdresspringar_happy.wav | Valdresspringar_happy.mid |
| Valdresspringar_original1.wav | Valdresspringar_original1.mid |
| Valdresspringar_sad.wav | Valdresspringar_sad.mid |
| Valdresspringar_tender.wav | Valdresspringar_tender.mid |
| Vossarull_angry.wav | Vossarull_angry.mid |
| Vossarull_happy.wav | Vossarull_happy.mid |
| Vossarull_original1.wav | Vossarull_original1.mid |
| Vossarull_sad.wav | Vossarull_sad.mid |
| Vossarull_tender.wav | Vossarull_tender.mid |
| Vrengja_original_torr_filtered_07-Jan-2025_15-43-25.mid_cleaned.wav | Vrengja_original_torr_filtered_07-Jan-2025_15-43-25.mid_cleaned.mid |

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
