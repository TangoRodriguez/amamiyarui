# 翠嶺高校2F生成画像レビュー v01

## 対象画像

| 想定asset_id | 元ファイル名 | 想定配置 | 初期status | 判定 |
|---|---|---|---|---|
| MAP-SRH-2F-v01 | 水杜県立翠嶺高等学校2Fフロアマップ.png | 00_INBOX/image_drop/map_reference/ | RAW → CANDIDATE | かなり良い。構造把握用の基準候補 |
| BG-SRH-A2-HALLWAY-v01 | 翠嶺高校2F廊下・A棟側.png | 00_INBOX/image_drop/background/ | RAW → CANDIDATE | 良い。A棟2Fの基準背景候補 |
| BG-SRH-B2-LIB-SC-HALLWAY-v01 | B棟2F・図書室前と生徒会室前の廊下.png | 00_INBOX/image_drop/background/ | RAW → CANDIDATE | 良い。B棟2Fの思想対比背景候補 |

## 画像別レビュー

### MAP-SRH-2F-v01

良い点:
- A棟2FとB棟2Fの関係が一枚で分かる。
- 2年B組、2年A組、2年C組、学年教員スペース、図書室、閲覧スペース、小会議室、生徒会室が視覚的に整理されている。
- A棟とB棟を中庭と渡り廊下でつなぐ構造が見やすい。
- 色分けにより、教室エリア、共用・学習エリア、生徒自治・会議エリアが分かりやすい。

修正点:
- 生成文字が多いため、最終版では文字を後から手作業で入れるか、図面として整える。
- 2年B組と2年A組の隣接関係は良いが、教室順を最終Canonにする前に再確認する。
- 屋上前階段が左端にあるのは良いが、思想対話の定番ショット用に別途背景化が必要。

次アクション:
- CANDIDATEとして登録。
- 04_MAPS/suirei_high_2f_detail.md と 03_DATA/suirei_high_2f.yaml の視覚対応版として扱う。
- まだCANONにはしない。

### BG-SRH-A2-HALLWAY-v01

良い点:
- 2年A組と2年B組が隣接していることが直感的に分かる。
- 夕方の光、木製扉、掲示物、階段導線があり、学校の日常感が強い。
- 右側の支援・アプリ系ポスターによって、普通の学校に制度の気配が混ざる構図になっている。

修正点:
- 文字が読める／崩れたラベルがあるため、最終背景では文字を抽象化する。
- 2年B組の表示がかなり明確なので、作品設定資料では良いが本編背景ではラベルを弱める。
- キャラ設定画との線密度は比較的近いが、やや背景美術として綺麗すぎるため、少し生活感を足す余地あり。

次アクション:
- CANDIDATEとして登録。
- 2年A組・2年B組の距離感を示す基準背景候補にする。

### BG-SRH-B2-LIB-SC-HALLWAY-v01

良い点:
- 左側に図書室、右側に資料・管理系の部屋があり、図書室側の温かさと管理側の緊張感が同時に出ている。
- 夕方の中庭・渡り廊下が奥に見え、A棟とB棟の接続が感じられる。
- 図書室側の暖色光と、右側の資料・タブレット・掲示板の制度感が対比になっている。

修正点:
- 生徒会室の存在が少し抽象的で、右側が資料室にも見える。次版では生徒会室の拠点性を少し強める。
- 全体がやや暗く、B棟の静けさとしては良いが、図書室側の安全地帯感をもう少し出してもよい。
- 文字は抽象化する。

次アクション:
- CANDIDATEとして登録。
- B棟2Fの基準背景候補にする。

## 登録時の推奨手順

1. 3枚を以下へ配置する。
   - MAP画像: `00_INBOX/image_drop/map_reference/`
   - A棟廊下: `00_INBOX/image_drop/background/`
   - B棟廊下: `00_INBOX/image_drop/background/`

2. 取り込みを実行する。

```bash
python 08_SCRIPTS/ingest_image_drop.py
```

3. 生成されたasset_idを確認し、必要なら以下のasset_idへ整理する。
   - `MAP-SRH-2F-v01`
   - `BG-SRH-A2-HALLWAY-v01`
   - `BG-SRH-B2-LIB-SC-HALLWAY-v01`

4. 良さそうならCANDIDATEへ昇格する。

```bash
python 08_SCRIPTS/promote_asset.py <asset_id> CANDIDATE
```

## 総合判断

3枚とも方向性は良い。  
ただし、現段階ではすべてCANDIDATE止まりが妥当。  
特にMAP画像は世界構築の理解にはかなり有効だが、Canon化する前にMarkdown/Mermaid/YAMLとの整合を確認する。
