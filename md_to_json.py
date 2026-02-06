#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _make_document(md_path: Path, schema_version: int = 2) -> Dict[str, Any]:
    """
    Build the JSON structure from a single .md file.

    Args:
        md_path: Path to the markdown file.
        schema_version: Schema version to store in the JSON.

    Returns:
        A dict that can be serialized to valid JSON.
    """
    # Read as UTF-8 (common for markdown). If your files are not UTF-8, adjust here.
    text = md_path.read_text(encoding="utf-8")

    # Keep the filename without extension as file_name
    file_name = md_path.stem

    # Output JSON path: same directory, same stem, .json extension
    out_path = md_path.with_suffix(".json")

    doc: Dict[str, Any] = {
        "document_type": "annotation",
        "file_path": str(out_path),
        "file_name": file_name,
        "meta_tags": {},
        "tags": [],
        "schema_version": schema_version,
        "plain_text": text,
    }
    return doc


def _write_json(doc: Dict[str, Any], out_path: Path) -> None:
    """
    Write JSON with correct escaping (including newlines) via json.dump.

    Args:
        doc: The document dict to serialize.
        out_path: Where to write the JSON.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ensure_ascii=False keeps umlauts readable; json handles escaping of control chars/newlines.
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=4)


def convert_directory(directory: Path, schema_version: int = 2) -> int:
    """
    Convert all .md files in a flat directory (no recursion) to .json.

    Args:
        directory: Directory containing .md files.
        schema_version: Schema version to store in the JSON.

    Returns:
        Number of converted files.
    """
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"Not a directory: {directory}")

    md_files = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".md")

    count = 0
    for md_path in md_files:
        out_path = md_path.with_suffix(".json")
        doc = _make_document(md_path=md_path, schema_version=schema_version)
        _write_json(doc=doc, out_path=out_path)
        count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert all .md files in a directory to annotation JSON files (schema_version=2)."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the directory containing .md files (flat, no recursion).",
    )
    parser.add_argument(
        "--schema-version",
        type=int,
        default=2,
        help="Schema version to write into JSON (default: 2).",
    )
    args = parser.parse_args()

    directory = Path(args.directory).expanduser().resolve()
    n = convert_directory(directory=directory, schema_version=args.schema_version)
    print(f"Converted {n} file(s) in: {directory}")


if __name__ == "__main__":
    main()
