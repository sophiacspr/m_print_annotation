#!/usr/bin/env python3

import re
from pathlib import Path

INPUT_FILE = Path("list.txt")
OUTPUT_FILE = Path("a1_regex")

# Zahl + Leerraum + Ausdruck, dann nächste Spalte
LINE_RE = re.compile(r"^\s*\d+\s+(.+?)(?=\s{2,}|\t)")

def extract_expression(line):
    line = line.rstrip("\n")
    if not line.strip():
        return None

    # bevorzugt: tab-separiert
    if "\t" in line:
        parts = line.split("\t")
        if len(parts) < 2:
            return None
        expr = parts[1].strip()
    else:
        m = LINE_RE.match(line)
        if not m:
            return None
        expr = m.group(1).strip()

    # alles nach erstem Komma weg
    expr = expr.split(",", 1)[0].strip()

    return expr if expr else None


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError("list.txt nicht gefunden")

    expressions = []
    for line in INPUT_FILE.read_text(encoding="utf-8").splitlines():
        expr = extract_expression(line)
        if expr is not None:
            expressions.append(expr)

    result = "|".join(expressions)
    OUTPUT_FILE.write_text(result, encoding="utf-8")

    print(f"{len(expressions)} Ausdrücke nach a1_regex geschrieben")


if __name__ == "__main__":
    main()
