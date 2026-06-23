from __future__ import annotations

import csv
import hashlib
from collections import Counter
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
    parts = rel_path.split("/")
    if "06_images/00_reference/" in p:
        return False
    if len(parts) >= 2 and parts[0] == "06_IMAGES" and parts[1] == "01_RAW":
        # Only top-level RAW files are managed; nested source dumps stay out of the registry.
        return len(parts) == 3
    return True


def make_asset_id(rel_path: str) -> str:
    digest = hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:10].upper()
    return f"ASSET-{digest}"


def load_rows() -> dict[str, dict[str, str]]:
    if not CSV_PATH.exists():
        return []

    rows: list[dict[str, str]] = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized: dict[str, str] = {}
            for k in CSV_HEADERS:
                normalized[k] = (row.get(k) or "").strip()
            if not normalized["relative_path"] and normalized["file_path"]:
                normalized["relative_path"] = normalized["file_path"]
            if not normalized["file_path"] and normalized["relative_path"]:
                normalized["file_path"] = normalized["relative_path"]
            rows.append(normalized)
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

    existing_rows = [
        r
        for r in load_rows()
        if is_registry_target((r.get("file_path") or r.get("relative_path") or "").strip())
    ]
    created = 0
    updated = 0
    timestamp = now_iso()

    images = sorted(
        p for p in IMAGE_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    managed_images = 0

    rows_by_path: dict[str, dict[str, str]] = {}
    rows_by_asset_id: dict[str, dict[str, str]] = {}
    rows_by_file_name: dict[str, list[dict[str, str]]] = {}

    for row in existing_rows:
        rel = (row.get("relative_path") or "").strip()
        fp = (row.get("file_path") or "").strip()
        aid = (row.get("asset_id") or "").strip()
        fname = (row.get("file_name") or "").strip()

        if rel:
            rows_by_path[rel] = row
        if fp:
            rows_by_path[fp] = row
        if aid and aid not in rows_by_asset_id:
            rows_by_asset_id[aid] = row
        if fname:
            rows_by_file_name.setdefault(fname, []).append(row)

    matched_ids: set[int] = set()

    for image_path in images:
        rel = to_posix_relative(image_path)
        if not is_registry_target(rel):
            continue

        managed_images += 1

        status = infer_status(rel)
        source_group = infer_source_group(rel)

        row: dict[str, str] | None = None

        if rel in rows_by_path:
            row = rows_by_path[rel]
        else:
            stem = image_path.stem.strip()
            if stem in rows_by_asset_id:
                row = rows_by_asset_id[stem]

        if row is None:
            # Prefer matching by file_name to keep the same row when images are moved across status folders.
            same_name_rows = rows_by_file_name.get(image_path.name, [])
            if len(same_name_rows) == 1:
                row = same_name_rows[0]

        if row is not None:
            matched_ids.add(id(row))
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

            if row.get("relative_path") != rel:
                row["relative_path"] = rel
                changed = True

            if row.get("source_group") != source_group:
                row["source_group"] = source_group
                changed = True

            if changed:
                row["updated_at"] = timestamp
                updated += 1
            continue

        new_row = {
            "asset_id": make_asset_id(rel),
            "file_name": image_path.name,
            "file_path": rel,
            "relative_path": rel,
            "status": status,
            "needs_review": "",
            "source_group": source_group,
            "notes": "",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        existing_rows.append(new_row)
        rows_by_path[rel] = new_row
        rows_by_asset_id[new_row["asset_id"]] = new_row
        rows_by_file_name.setdefault(image_path.name, []).append(new_row)
        created += 1

    # needs_review is true only when the same file_name appears multiple times.
    name_counts = Counter((r.get("file_name") or "").strip() for r in existing_rows if (r.get("file_name") or "").strip())
    for row in existing_rows:
        fname = (row.get("file_name") or "").strip()
        row["needs_review"] = "true" if fname and name_counts[fname] > 1 else "false"

    rows_out = sorted(existing_rows, key=lambda r: ((r.get("status") or ""), (r.get("asset_id") or ""), (r.get("file_path") or "")))
    write_rows(rows_out)

    print(f"registered images: {managed_images}")
    print(f"created rows: {created}")
    print(f"updated rows: {updated}")
    print(f"csv: {CSV_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
