import csv
import json
from pathlib import Path


def save_report_json(payload, path: Path):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_report_csv(rows, path: Path):
    fields = [
        "strength", "severity", "entropy", "length", "dictionary_match",
        "bruteforce_match", "attempts", "rate", "search_space",
        "estimated_worst_case",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
