# Norwegian Folk Music Audio-MIDI Dataset

A paired audio and MIDI dataset of Norwegian folk music for training audio-to-MIDI transcription models.

## Dataset Summary

- **Total pairs:** 118 audio-MIDI pairs
- **Unique songs:** 38
- **Total size:** ~970 MB
- **Audio format:** WAV
- **MIDI format:** Standard MIDI (.mid)

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
│   └── validate_dataset.py
├── reports/
│   └── validate.json
├── dvc.yaml
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

## Usage

### Prerequisites

- Python 3.8+
- DVC (`pip install dvc`)

### Getting the Data

```bash
# Clone the repository
git clone <repository-url>
cd hf-dataset

# Pull data from DVC remote
dvc pull
```

### Reproducing the Pipeline

```bash
# Run the full pipeline (build manifest + validate)
dvc repro

# Or run individual stages
dvc repro build_manifest
dvc repro validate
```

### Validation

```bash
# Run validation
python3 scripts/validate_dataset.py

# Check validation report
cat reports/validate.json
```

## Train/Val/Test Splits

Splits are not baked into the manifest. Determine splits at training time based on your needs. Recommended approach: split by song name (not by individual pairs) to prevent data leakage.

## License

Contact the dataset maintainers for licensing information.

## Citation

If you use this dataset, please cite appropriately.
