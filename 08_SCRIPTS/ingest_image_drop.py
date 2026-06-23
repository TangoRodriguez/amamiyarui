from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DROP_ROOT = ROOT / "00_INBOX" / "image_drop"
RAW_ROOT = ROOT / "06_IMAGES" / "01_RAW"
CSV_PATH = ROOT / "03_DATA" / "image_assets.csv"

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

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}

CHARACTER_BASES = {
    "雨宮類": "CH-RUI",
    "黒瀬型": "CH-KUROSE",
    "日向真帆": "CH-MAHO",
    "小森陸": "CH-RIKU",
    "佐倉律": "CH-RITSU",
    "光田芽衣": "CH-MEI",
    "雨宮晴臣": "AD-HARUOMI",
    "桐谷澪": "AD-KIRITANI",
    "宇佐美遥": "AD-USAMI",
    "相良朔": "AD-SAGARA",
}

LOCATION_BASES = {
    "雨宮修理研究所": "BG-AMAMIYA-REPAIRLAB",
    "生徒会室": "BG-SUIREI-STUDENTCOUNCIL",
    "水杜中央駅前": "BG-MZM-STATION-FRONT",
    "水杜川": "BG-MZM-RIVER-WALK",
    "水杜市スマート共生課": "BG-CITYHALL-SMARTDESK",
    "白ヶ瀬団地": "BG-SHIRAGASE-DANCHI",
    "白庭計画事務室": "BG-HAKUNIWA-OFFICE",
    "翠嶺高校保健室": "BG-SUIREI-INFIRMARY",
    "星原こども発達センター": "BG-HOSHIHARA-EXT",
    "月ノ丘ニュータウン": "BG-TSUKINOOKA-STREET",
    "黒瀬家_リビング": "BG-KUROSE-LIVING",
}

VIEW_TOKENS = {
    "三面図": "3VIEW",
    "表情集": "EXPRESSION",
    "ポーズ集": "POSE",
}

TYPE_TO_SOURCE_GROUP = {
    "character": "character",
    "character_revision": "character_revision",
    "background": "background",
    "location_reference": "location_reference",
    "map_reference": "map_reference",
    "prop": "prop",
    "unknown": "unknown",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_rows() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        return []

    rows: list[dict[str, str]] = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {key: (row.get(key) or "").strip() for key in CSV_HEADERS}
            if not normalized["file_path"] and normalized["relative_path"]:
                normalized["file_path"] = normalized["relative_path"]
            if not normalized["relative_path"] and normalized["file_path"]:
                normalized["relative_path"] = normalized["file_path"]
            rows.append(normalized)
    return rows


def write_rows(rows: list[dict[str, str]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def infer_asset_type(drop_path: Path) -> str:
    if not drop_path.parts:
        return "unknown"
    top = drop_path.parts[0]
    return top if top in TYPE_TO_SOURCE_GROUP else "unknown"


def infer_subject_name(asset_type: str, source_name: str) -> str:
    if asset_type in {"character", "character_revision"}:
        return source_name.split("_")[0]
    return source_name


def infer_view_token(file_stem: str) -> str:
    for key, token in VIEW_TOKENS.items():
        if key in file_stem:
            return token
    return "ART"


def next_version(base_id: str, existing_rows: list[dict[str, str]]) -> str:
    pattern = re.compile(rf"^{re.escape(base_id)}-v(\d+)$")
    highest = 0
    for row in existing_rows:
        asset_id = (row.get("asset_id") or "").strip()
        match = pattern.match(asset_id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{base_id}-v{highest + 1:02d}"


def make_hash_id(prefix: str, text: str, existing_rows: list[dict[str, str]]) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8].upper()
    base = f"{prefix}-{digest}"
    return next_version(base, existing_rows)


def infer_asset_id(asset_type: str, source_name: str, file_stem: str, existing_rows: list[dict[str, str]]) -> str:
    if asset_type in {"character", "character_revision"}:
        subject = infer_subject_name(asset_type, source_name)
        base = CHARACTER_BASES.get(subject)
        if base:
            view = infer_view_token(file_stem)
            return next_version(f"{base}-{view}", existing_rows)
        return make_hash_id("CH-DROP", f"{source_name}:{file_stem}", existing_rows)

    if asset_type in {"background", "location_reference"}:
        base = LOCATION_BASES.get(source_name) or LOCATION_BASES.get(file_stem)
        if base:
            return next_version(base, existing_rows)
        return make_hash_id("BG-DROP", f"{source_name}:{file_stem}", existing_rows)

    if asset_type == "map_reference":
        return make_hash_id("MAP-DROP", f"{source_name}:{file_stem}", existing_rows)

    if asset_type == "prop":
        return make_hash_id("PROP-DROP", f"{source_name}:{file_stem}", existing_rows)

    return make_hash_id("DROP", f"{source_name}:{file_stem}", existing_rows)


def unique_destination_name(dest_dir: Path, original_name: str) -> tuple[str, int]:
    candidate = original_name
    renamed = 0
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    version = 2

    while (dest_dir / candidate).exists():
        candidate = f"{stem}_v{version:02d}{suffix}"
        renamed += 1
        version += 1

    return candidate, renamed


def iter_drop_images() -> list[Path]:
    if not DROP_ROOT.exists():
        return []
    return sorted(p for p in DROP_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)


def main() -> int:
    if not DROP_ROOT.exists():
        print(f"image_drop not found: {DROP_ROOT}")
        return 1

    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    existing_rows = load_rows()
    rows_by_asset_id = {row["asset_id"]: row for row in existing_rows if row.get("asset_id")}
    timestamp = now_iso()

    copied = 0
    renamed = 0

    for source_path in iter_drop_images():
        rel_drop = source_path.relative_to(DROP_ROOT)
        asset_type = infer_asset_type(rel_drop)
        source_name = rel_drop.parts[1] if len(rel_drop.parts) > 1 else rel_drop.stem
        final_file_name, rename_count = unique_destination_name(RAW_ROOT, source_path.name)
        renamed += rename_count
        destination = RAW_ROOT / final_file_name

        shutil.copy2(source_path, destination)
        copied += 1

        final_stem = Path(final_file_name).stem
        asset_id = infer_asset_id(asset_type, source_name, final_stem, existing_rows)
        while asset_id in rows_by_asset_id:
            asset_id = infer_asset_id(asset_type, source_name, f"{final_stem}_retry", existing_rows)

        row = {
            "asset_id": asset_id,
            "file_name": final_file_name,
            "file_path": destination.relative_to(ROOT).as_posix(),
            "relative_path": destination.relative_to(ROOT).as_posix(),
            "status": "RAW",
            "needs_review": "true",
            "source_group": TYPE_TO_SOURCE_GROUP.get(asset_type, asset_type),
            "notes": f"ingested from 00_INBOX/image_drop/{rel_drop.as_posix()}",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        existing_rows.append(row)
        rows_by_asset_id[asset_id] = row

    existing_rows.sort(key=lambda r: ((r.get("status") or ""), (r.get("asset_id") or ""), (r.get("file_path") or "")))
    write_rows(existing_rows)

    print(f"copied: {copied}")
    print(f"duplicate_avoided: {renamed}")
    print(f"csv: {CSV_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
