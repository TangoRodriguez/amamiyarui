# ComfyUI animation setup for 『雨宮類は最適解を知らない』

このフォルダは、ローカル ComfyUI で雨宮類の短尺アニメ制作を試すためのセットアップ指示です。

目的は、GitHub Copilot に「コード・フォルダ・チェックリスト整備」をさせ、巨大モデルの取得やノード配置はユーザーが手作業で確認しながら行える状態まで持っていくことです。

## 前提

- Windows
- RTX 4070 Laptop / VRAM 8GB 想定
- ComfyUI はすでに導入済み
- Premiere Pro / After Effects で仕上げる
- まずは 1 枚絵から 3〜6 秒の顔アニメを作る

## 推奨ルート

1. LivePortrait: まばたき・口・顔・上半身の微動
2. IPAdapter: 雨宮、真帆、小森の顔・絵柄の一貫性維持
3. ControlNet preprocessors: 自撮り動画から OpenPose / DWPose / Canny / Lineart を取る
4. AnimateDiff: LivePortrait では足りない 1〜3 秒の大きめの動き用

## 実行順

### 1. Custom nodes を入れる

```powershell
powershell -ExecutionPolicy Bypass -File .\08_SCRIPTS\comfyui_setup\install_custom_nodes.ps1 -ComfyUIRoot "D:\AI\ComfyUI_windows_portable\ComfyUI"
```

ComfyUI の場所が違う場合は `-ComfyUIRoot` を変更してください。

### 2. モデル配置フォルダを作る

最小構成:

```powershell
powershell -ExecutionPolicy Bypass -File .\08_SCRIPTS\comfyui_setup\prepare_model_folders.ps1 -ComfyUIRoot "D:\AI\ComfyUI_windows_portable\ComfyUI" -Tier minimal
```

IPAdapter まで:

```powershell
powershell -ExecutionPolicy Bypass -File .\08_SCRIPTS\comfyui_setup\prepare_model_folders.ps1 -ComfyUIRoot "D:\AI\ComfyUI_windows_portable\ComfyUI" -Tier identity
```

OpenPose / ControlNet まで:

```powershell
powershell -ExecutionPolicy Bypass -File .\08_SCRIPTS\comfyui_setup\prepare_model_folders.ps1 -ComfyUIRoot "D:\AI\ComfyUI_windows_portable\ComfyUI" -Tier control
```

AnimateDiff まで:

```powershell
powershell -ExecutionPolicy Bypass -File .\08_SCRIPTS\comfyui_setup\prepare_model_folders.ps1 -ComfyUIRoot "D:\AI\ComfyUI_windows_portable\ComfyUI" -Tier motion
```

### 3. モデル本体を手動配置

`models_manifest.json` の `source_page` を開き、上流のライセンス・モデルカードを確認してから、`target_dir` に配置してください。

巨大モデルは Git に入れないでください。`.gitignore` に safetensors / ckpt / pth / pt / bin / onnx 等の除外を追加済みです。

## 容量目安

| 段階 | 目的 | 追加容量目安 |
|---|---|---:|
| minimal | LivePortrait 顔アニメ | 約 2〜3 GB |
| identity | IPAdapter + CLIP Vision | 約 5〜6 GB |
| control | ControlNet + preprocessor | 約 8〜12 GB |
| motion | AnimateDiff motion module | 約 10〜15 GB |
| 余裕込み | キャッシュ・出力・複数モデル | 30〜50 GB |

ComfyUI 本体、Python、既存 checkpoint、出力動画まで含めるなら、作業ドライブには **最低 60GB、快適には 100GB 以上** 空けるのがおすすめです。

## 最初のチュートリアル

### T01: 1枚絵からまばたき

素材:

- 小森または雨宮の正面寄り画像
- 自撮り 5 秒動画: 正面、まばたき 2 回、軽い口の動き

狙い:

- 顔が別人化しない
- 目が自然に閉じる
- 口が壊れない

### T02: 雨宮 6 秒テスト

構成:

1. 0〜2秒: 雨宮が作文を見る。軽くまばたき。
2. 2〜4秒: 「この作文、うますぎるんじゃない」
3. 4〜6秒: 目線を上げる。AE で思考文字を重ねる。

成功条件:

- 口パクは完璧でなくてよい
- 目線と表情が自然
- Premiere で声・紙音・テロップが合う

## 注意

- 4070 Laptop では、いきなり長尺・高解像度動画生成をしない。
- 最初は 512〜768px 幅、3〜6 秒、低 motion でテストする。
- 日本語文字は ComfyUI に描かせず、Premiere / After Effects で後乗せする。
- 商用利用予定があるなら、InsightFace など非商用制限のある部品は避ける。
