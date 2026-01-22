#!/usr/bin/env python3
"""Publish dataset release to Hugging Face Hub.

Standalone script - not part of the dataset package.

Requirements:
    pip install huggingface_hub

Usage:
    python scripts/publish_to_huggingface.py --version v0.1.0
    python scripts/publish_to_huggingface.py --version v0.1.0 --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ID = "Bots4M/HF2-Hardanger-fiddle-dataset"

HF_YAML_METADATA = """---
license: cc-by-4.0
language:
  - "no"
tags:
  - automatic-music-transcription
  - audio-to-midi
  - hardanger-fiddle
  - norwegian-folk-music
size_categories:
  - n<1K
---

"""


def get_git_tag() -> str | None:
    """Get exact tag at HEAD, or None if not on a tag."""
    result = subprocess.run(
        ["git", "describe", "--tags", "--exact-match"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def is_working_tree_clean() -> bool:
    """Check if git working tree is clean."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    return len(result.stdout.strip()) == 0


def publish(version: str, dry_run: bool = False, force: bool = False) -> None:
    """Export and upload dataset to Hugging Face."""

    # Safety checks
    git_tag = get_git_tag()
    if git_tag is None:
        print("WARNING: HEAD is not at an exact tag!")
        print("         Run: git tag <version> && git checkout <version>")
        if not force:
            print("         Use --force to publish anyway.")
            sys.exit(1)
    elif git_tag != version and f"dataset-{version}" != git_tag:
        print(f"ERROR: Tag mismatch! HEAD is at '{git_tag}' but --version is '{version}'")
        sys.exit(1)

    if not is_working_tree_clean():
        print("WARNING: Working tree has uncommitted changes!")
        if not force:
            print("         Commit or stash changes, or use --force to publish anyway.")
            sys.exit(1)

    # Import here so script shows helpful error if not installed
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        print("       Run: pip install huggingface_hub")
        sys.exit(1)

    # Create clean export (no .dvc internals)
    with tempfile.TemporaryDirectory() as tmp:
        export_dir = Path(tmp)

        print(f"Exporting data to {export_dir}...")
        shutil.copytree("data/raw", export_dir / "data" / "raw")
        shutil.copytree("data/manifests", export_dir / "data" / "manifests")

        # Add HF YAML metadata to README for HuggingFace
        with open("README.md", "r") as f:
            readme_content = f.read()
        with open(export_dir / "README.md", "w") as f:
            f.write(HF_YAML_METADATA + readme_content)

        if dry_run:
            print(f"[DRY RUN] Would upload to {REPO_ID}")
            print(f"          Version: {version}")
            print(f"          Files: {list((export_dir / 'data' / 'raw').iterdir())[:5]}...")
            return

        # Upload to HF
        print(f"Uploading to {REPO_ID}...")
        api = HfApi()
        api.upload_folder(
            repo_id=REPO_ID,
            repo_type="dataset",
            folder_path=str(export_dir),
            commit_message=f"Release {version}",
        )
        print(f"Published {version} to https://huggingface.co/datasets/{REPO_ID}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish dataset to Hugging Face")
    parser.add_argument("--version", required=True, help="Version tag (e.g., v0.1.0)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded")
    parser.add_argument("--force", action="store_true", help="Publish even with warnings")
    args = parser.parse_args()

    publish(args.version, args.dry_run, args.force)


if __name__ == "__main__":
    main()
