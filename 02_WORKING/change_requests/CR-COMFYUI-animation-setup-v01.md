# CR-COMFYUI-animation-setup-v01

## 目的

『雨宮類は最適解を知らない』の短尺アニメ制作に向けて、ローカル ComfyUI 環境の準備を半自動化する。

この変更では、GitHub Copilot に以下を整備させる。

- ComfyUI custom nodes の導入スクリプト
- モデル配置フォルダの作成補助
- モデル容量・配置先チェックリスト
- 1枚絵からの顔アニメーション用の最初の実験導線

巨大モデルや出力動画は Git に入れない。

## 既存リポジトリ構造との接続

このリポジトリは、すでに以下のような制作管理構造を持つ。

- `00_INBOX/`: 取り込み前の素材やログ
- `01_CANON/`: 世界観・キャラ・ビジュアルスタイル
- `03_DATA/`: CSV / YAML 管理データ
- `06_IMAGES/`: 画像アセット
- `08_SCRIPTS/`: 制作用スクリプト
- `10_STORIES/`: 各話脚本

今回の ComfyUI 周りは `08_SCRIPTS/comfyui_setup/` に置く。

## Copilot にやってほしいこと

### 1. スクリプトの安全性確認

`08_SCRIPTS/comfyui_setup/install_custom_nodes.ps1` を確認し、以下を満たすよう改善する。

- `-ComfyUIRoot` を指定できる
- `COMFYUI_ROOT` 環境変数も使える
- Windows portable ComfyUI の `python_embeded/python.exe` を検出できる
- `custom_nodes` がなければ作る
- 既存ノードがあれば `git pull --ff-only` にする
- `requirements.txt` がある場合のみ pip install
- エラー時にどのノードで失敗したか分かる

### 2. 導入対象 custom nodes

最低限、以下を対象にする。

- `ComfyUI-Manager`
- `ComfyUI-VideoHelperSuite`
- `ComfyUI-KJNodes`
- `ComfyUI-LivePortraitKJ`
- `comfyui_controlnet_aux`
- `ComfyUI_IPAdapter_plus`
- `ComfyUI-AnimateDiff-Evolved`
- `ComfyUI-Advanced-ControlNet`
- `ComfyUI-Impact-Pack`
- `ComfyUI-Custom-Scripts`

### 3. モデル配置補助

`models_manifest.json` と `prepare_model_folders.ps1` を確認し、以下の tier を使えるようにする。

- `minimal`: LivePortrait 顔アニメ
- `identity`: IPAdapter による顔・絵柄固定
- `control`: OpenPose / Canny / Lineart 等の制御
- `motion`: AnimateDiff の短尺動画
- `all`: 非商用制限が強いものを除く全部

モデル本体の自動大量ダウンロードはしない。
ソースページと配置先だけを明確に出す。

### 4. .gitignore の安全性

以下が除外されているか確認する。

- `.safetensors`
- `.ckpt`
- `.pth`
- `.pt`
- `.bin`
- `.onnx`
- `.torchscript`
- `.mp4`, `.mov`, `.webm`, `.avi`
- `local_comfyui/`
- `ComfyUI_windows_portable/`

### 5. 最初のチュートリアル導線

README に以下のチュートリアルを入れる。

#### T01: まばたきテスト

- 入力: 正面寄りキャラ画像
- driving video: 自撮り 5 秒
- 目的: まばたき、軽い口、首の微動

#### T02: 雨宮 6 秒テスト

- 0〜2秒: 雨宮が作文を見る
- 2〜4秒: 「この作文、うますぎるんじゃない」
- 4〜6秒: 思考文字を AE で重ねる

## 容量見積もり

README には以下を記載する。

| 段階 | 目的 | 追加容量目安 |
|---|---|---:|
| minimal | LivePortrait 顔アニメ | 約 2〜3 GB |
| identity | IPAdapter + CLIP Vision | 約 5〜6 GB |
| control | ControlNet + preprocessor | 約 8〜12 GB |
| motion | AnimateDiff motion module | 約 10〜15 GB |
| 余裕込み | キャッシュ・出力・複数モデル | 30〜50 GB |

作業ドライブは最低 60GB、快適には 100GB 以上を推奨。

## 完了条件

- `install_custom_nodes.ps1` が構文的に読める
- `prepare_model_folders.ps1` が manifest を読んでフォルダ作成できる
- README を見れば、ユーザーが手作業でノード配置・モデル配置に進める
- 巨大バイナリが Git に入っていない
