"""Generate docs/SONGS.md from the manifest, audio files, and MIDI files.

Reads data/manifests/manifest.csv, computes audio duration from WAV headers and
note count from MIDI files, extracts recording dates from filenames where
present, and writes a markdown table grouped by category.
"""

from __future__ import annotations

import csv
import re
import wave
from pathlib import Path

import mido

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "data" / "manifests" / "manifest.csv"
OUTPUT = REPO_ROOT / "docs" / "SONGS.md"

DATE_RE = re.compile(
    r"(\d{2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4})"
)


def audio_duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def midi_note_count(path: Path) -> int:
    mid = mido.MidiFile(str(path))
    count = 0
    for track in mid.tracks:
        for msg in track:
            if msg.type == "note_on" and msg.velocity > 0:
                count += 1
    return count


def fmt_duration(seconds: float) -> str:
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def category_of(row: dict) -> str:
    notes = (row.get("notes") or "").strip()
    if notes in {"archival", "processed"}:
        return notes
    if row.get("has_emotional_variations") == "True":
        return "emotional"
    return "other"


def group_of(row: dict) -> str:
    name = row["song_name"]
    if (row.get("notes") or "").strip() == "archival":
        parts = name.split("-", 2)
        if len(parts) == 3:
            return parts[2]
        return name
    return name.split("_")[0]


def performer_of(row: dict) -> str:
    if (row.get("notes") or "").strip() == "archival":
        parts = row["song_name"].split("-", 2)
        if len(parts) == 3:
            return parts[1]
    return ""


def recording_date(row: dict) -> str:
    midi_name = Path(row["midi_relpath"]).name
    m = DATE_RE.search(midi_name)
    return m.group(1) if m else ""


def build_rows() -> list[dict]:
    with MANIFEST.open() as f:
        manifest_rows = list(csv.DictReader(f))

    out: list[dict] = []
    for r in manifest_rows:
        audio = REPO_ROOT / r["audio_relpath"]
        midi = REPO_ROOT / r["midi_relpath"]
        out.append(
            {
                "file": Path(r["midi_relpath"]).stem,
                "group": group_of(r),
                "category": category_of(r),
                "emotion": (r.get("emotion") or "").strip(),
                "performer": performer_of(r),
                "duration_s": audio_duration_seconds(audio),
                "notes": midi_note_count(midi),
                "recorded": recording_date(r),
            }
        )
    return out


def render(rows: list[dict]) -> str:
    rows_sorted = sorted(
        rows,
        key=lambda x: (
            {"archival": 0, "processed": 1, "emotional": 2}.get(x["category"], 9),
            x["group"].lower(),
            x["emotion"],
            x["file"].lower(),
        ),
    )

    by_cat: dict[str, list[dict]] = {}
    for r in rows_sorted:
        by_cat.setdefault(r["category"], []).append(r)

    total_notes = sum(r["notes"] for r in rows)
    total_duration = sum(r["duration_s"] for r in rows)
    total_files = len(rows)

    cat_titles = {
        "archival": "Archival recordings",
        "processed": "Processed recordings",
        "emotional": "Emotional variants",
    }

    lines: list[str] = [
        "# Song List",
        "",
        f"Auto-generated from `data/manifests/manifest.csv`. "
        f"Regenerate with `python scripts/build_song_list.py`.",
        "",
        f"**Totals:** {total_files} pairs · "
        f"{fmt_duration(total_duration)} total audio · "
        f"{total_notes:,} annotated notes",
        "",
    ]

    for cat in ["archival", "processed", "emotional"]:
        items = by_cat.get(cat, [])
        if not items:
            continue
        cat_notes = sum(r["notes"] for r in items)
        cat_dur = sum(r["duration_s"] for r in items)
        lines += [
            f"## {cat_titles[cat]} ({len(items)} pairs · "
            f"{fmt_duration(cat_dur)} · {cat_notes:,} notes)",
            "",
        ]
        if cat == "archival":
            lines += [
                "| File | Song | Performer | Duration | Notes |",
                "|------|------|-----------|---------:|------:|",
            ]
            for r in items:
                lines.append(
                    f"| {r['file']} | {r['group']} | {r['performer']} | "
                    f"{fmt_duration(r['duration_s'])} | {r['notes']:,} |"
                )
        elif cat == "processed":
            lines += [
                "| File | Song | Recorded | Duration | Notes |",
                "|------|------|----------|---------:|------:|",
            ]
            for r in items:
                lines.append(
                    f"| {r['file']} | {r['group']} | {r['recorded']} | "
                    f"{fmt_duration(r['duration_s'])} | {r['notes']:,} |"
                )
        else:
            lines += [
                "| File | Song | Emotion | Duration | Notes |",
                "|------|------|---------|---------:|------:|",
            ]
            for r in items:
                lines.append(
                    f"| {r['file']} | {r['group']} | {r['emotion']} | "
                    f"{fmt_duration(r['duration_s'])} | {r['notes']:,} |"
                )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    rows = build_rows()
    OUTPUT.write_text(render(rows))
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
