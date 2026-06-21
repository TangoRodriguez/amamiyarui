from __future__ import annotations

from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = [
    "00_INBOX/chat_logs",
    "01_CANON",
    "02_WORKING",
    "03_DATA",
    "04_MAPS",
    "05_PROMPTS",
    "06_IMAGES/01_RAW",
    "06_IMAGES/02_CANDIDATE",
    "06_IMAGES/03_SELECTED",
    "06_IMAGES/04_CANON",
    "06_IMAGES/05_REJECTED",
    "08_SCRIPTS",
]
CSV_PATH = ROOT / "03_DATA" / "image_assets.csv"
CSV_HEADERS = [
    "asset_id",
    "file_name",
    "relative_path",
    "status",
    "source_group",
    "notes",
    "created_at",
    "updated_at",
]


def ensure_csv_exists() -> None:
    if CSV_PATH.exists():
        return
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()


def main() -> int:
    print(f"[setup_check] root: {ROOT}")
    missing = []
    for rel in REQUIRED_DIRS:
        path = ROOT / rel
        if path.exists() and path.is_dir():
            print(f"  OK      {rel}")
        else:
            print(f"  MISSING {rel}")
            missing.append(rel)

    ensure_csv_exists()
    print(f"  CSV     {CSV_PATH.relative_to(ROOT)}")

    if missing:
        print("\nSome required directories are missing.")
        return 1

    print("\nsetup_check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
