from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "03_DATA" / "image_assets.csv"
IMAGE_ROOT = ROOT / "06_IMAGES"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
VALID_STATUS = {"RAW", "CANDIDATE", "SELECTED", "CANON", "REJECTED"}
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


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def to_posix_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def infer_status(rel_path: str) -> str:
    p = rel_path.lower()
    if "06_images/04_canon/" in p:
        return "CANON"
    if "06_images/03_selected/" in p:
        return "SELECTED"
    if "06_images/02_candidate/" in p:
        return "CANDIDATE"
    if "06_images/99_rejected/" in p:
        return "REJECTED"
    return "RAW"


def infer_source_group(rel_path: str) -> str:
    parts = rel_path.split("/")
    if len(parts) >= 4 and parts[0] == "06_IMAGES" and parts[1] == "01_RAW":
        return parts[3] if parts[2] == "キャラクター画像" else parts[2]
    if len(parts) >= 3 and parts[0] == "06_IMAGES":
        return parts[2]
    return "unknown"


def is_registry_target(rel_path: str) -> bool:
    p = rel_path.lower()
    if "06_images/00_reference/" in p:
        return False
    return True


def make_asset_id(rel_path: str) -> str:
    digest = hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:10].upper()
    return f"ASSET-{digest}"


def load_rows() -> dict[str, dict[str, str]]:
    if not CSV_PATH.exists():
        return {}

    rows: dict[str, dict[str, str]] = {}
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = (row.get("relative_path") or "").strip()
            if not rel:
                continue
            rows[rel] = row
    return rows


def write_rows(rows: list[dict[str, str]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if not IMAGE_ROOT.exists():
        print(f"image root not found: {IMAGE_ROOT}")
        return 1

    existing = load_rows()
    created = 0
    updated = 0
    timestamp = now_iso()

    images = sorted(
        p for p in IMAGE_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    managed_images = 0

    for image_path in images:
        rel = to_posix_relative(image_path)
        if not is_registry_target(rel):
            continue

        managed_images += 1

        status = infer_status(rel)
        source_group = infer_source_group(rel)

        if rel in existing:
            row = existing[rel]
            changed = False

            if not row.get("asset_id"):
                row["asset_id"] = make_asset_id(rel)
                changed = True

            current_status = (row.get("status") or "").strip()
            if current_status not in VALID_STATUS:
                row["status"] = status
                changed = True
            elif status != "RAW" and current_status != status:
                row["status"] = status
                changed = True

            if row.get("file_name") != image_path.name:
                row["file_name"] = image_path.name
                changed = True

            if row.get("file_path") != rel:
                row["file_path"] = rel
                changed = True

            if (row.get("needs_review") or "").strip().lower() not in {"true", "false"}:
                row["needs_review"] = "false"
                changed = True

            if row.get("source_group") != source_group:
                row["source_group"] = source_group
                changed = True

            if changed:
                row["updated_at"] = timestamp
                updated += 1
            continue

        existing[rel] = {
            "asset_id": make_asset_id(rel),
            "file_name": image_path.name,
            "file_path": rel,
            "relative_path": rel,
            "status": status,
            "needs_review": "false",
            "source_group": source_group,
            "notes": "",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        created += 1

    rows_out = sorted(existing.values(), key=lambda r: (r["status"], r["asset_id"]))
    write_rows(rows_out)

    print(f"registered images: {managed_images}")
    print(f"created rows: {created}")
    print(f"updated rows: {updated}")
    print(f"csv: {CSV_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
