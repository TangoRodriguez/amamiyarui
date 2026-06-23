# 制作管理Bible

## 画像レイヤーの運用
- `00_INBOX/image_drop` はユーザーが自由に画像を投げ込む入口。
- `RAW` は登録済み・未評価の素材。
- `CANDIDATE` は候補。
- `SELECTED` は採用候補。
- `CANON` は正史。
- `REFERENCE` は生成時参照用コピーであり、正史とは限らない。
- `SUPERSEDED` は旧正史。
- `REJECTED` は没。

## 画像管理の流れ
1. 画像を `00_INBOX/image_drop` に投入する。
2. `08_SCRIPTS/ingest_image_drop.py` で `06_IMAGES/01_RAW` と `03_DATA/image_assets.csv` に反映する。
3. 必要に応じて `08_SCRIPTS/promote_asset.py` で `CANDIDATE` / `SELECTED` / `CANON` / `SUPERSEDED` / `REJECTED` に昇格・退避する。
4. 生成時に必要なものだけ `06_IMAGES/00_REFERENCE` にコピーして使う。

## 正史管理
- `03_DATA/canon_registry.yaml` は現時点で有効な正史を記録する。
- `03_DATA/asset_versions.csv` は各 entity の current / previous / candidate / selected を整理する。
- 正史化の際は、旧Canonを即時削除せず `SUPERSEDED` として残す。
