from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "03_DATA" / "image_assets.csv"

STATUS_TO_DIR = {
    "RAW": ROOT / "06_IMAGES" / "01_RAW",
    "CANDIDATE": ROOT / "06_IMAGES" / "02_CANDIDATE",
    "SELECTED": ROOT / "06_IMAGES" / "03_SELECTED",
    "CANON": ROOT / "06_IMAGES" / "04_CANON",
    "SUPERSEDED": ROOT / "06_IMAGES" / "05_SUPERSEDED",
    "REJECTED": ROOT / "06_IMAGES" / "99_REJECTED",
}

VALID_STATUS = set(STATUS_TO_DIR)
CSV_HEADERS = [
    "asset_id",
    "file_name",
    "file_path",
    "relative_path",
    "status",
    "needs_review",
    "source_group",
    "notes",
    "created_at",
    "updated_at",
]

CANON_HINTS = {
    "CH-RUI": "CH-RUI-3VIEW-v01",
    "CH-KUROSE": "CH-KUROSE-3VIEW-v01",
    "CH-MAHO": "CH-MAHO-3VIEW-v01",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_rows() -> list[dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [{key: (row.get(key) or "").strip() for key in CSV_HEADERS} for row in reader]


def write_rows(rows: list[dict[str, str]]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def unique_destination_name(dest_dir: Path, original_name: str) -> str:
    candidate = original_name
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    version = 2
    while (dest_dir / candidate).exists():
        candidate = f"{stem}_v{version:02d}{suffix}"
        version += 1
    return candidate


def infer_entity_id(asset_id: str, file_name: str) -> str:
    if asset_id.startswith("CH-RUI"):
        return "CH-RUI"
    if asset_id.startswith("CH-KUROSE"):
        return "CH-KUROSE"
    if asset_id.startswith("CH-MAHO"):
        return "CH-MAHO"
    if asset_id.startswith("CH-"):
        base = asset_id.rsplit("-v", 1)[0]
        for token in ("-3VIEW", "-EXPRESSION", "-POSE"):
            if base.endswith(token):
                return base[: -len(token)]
        return base
    return Path(file_name).stem


def print_canon_update_candidates(row: dict[str, str], target_status: str) -> None:
    if target_status != "CANON":
        return
    entity_id = infer_entity_id(row["asset_id"], row["file_name"])
    current_canon = CANON_HINTS.get(entity_id)
    print("canon_registry.yaml update candidate:")
    print(f"  entity_id: {entity_id}")
    print(f"  current_canon: {current_canon or 'null'}")
    print(f"  proposed_canon: {row['asset_id']}")
    if current_canon and current_canon != row["asset_id"]:
        print(f"  previous_canon_retained: {current_canon}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Move an asset into a status folder and update image_assets.csv.")
    parser.add_argument("asset_id", help="Asset ID to move")
    parser.add_argument("target_status", help="RAW/CANDIDATE/SELECTED/CANON/SUPERSEDED/REJECTED")
    args = parser.parse_args()

    target_status = args.target_status.upper().strip()
    if target_status not in VALID_STATUS:
        print(f"invalid target_status: {args.target_status}")
        return 1

    rows = load_rows()
    row = next((r for r in rows if r.get("asset_id") == args.asset_id), None)
    if row is None:
        print(f"asset_id not found: {args.asset_id}")
        return 1

    source_rel = row.get("file_path") or row.get("relative_path")
    if not source_rel:
        print(f"missing file path for asset_id: {args.asset_id}")
        return 1

    source_path = ROOT / source_rel
    if not source_path.exists():
        print(f"source file not found: {source_path}")
        return 1

    target_dir = STATUS_TO_DIR[target_status]
    target_dir.mkdir(parents=True, exist_ok=True)
    final_name = unique_destination_name(target_dir, source_path.name)
    target_path = target_dir / final_name

    if source_path.resolve() != target_path.resolve():
        shutil.move(str(source_path), str(target_path))

    row["file_name"] = final_name
    row["file_path"] = target_path.relative_to(ROOT).as_posix()
    row["relative_path"] = target_path.relative_to(ROOT).as_posix()
    row["status"] = target_status
    row["updated_at"] = now_iso()

    write_rows(rows)
    print(f"moved asset: {args.asset_id}")
    print(f"status: {target_status}")
    print(f"file_path: {row['file_path']}")
    print_canon_update_candidates(row, target_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
