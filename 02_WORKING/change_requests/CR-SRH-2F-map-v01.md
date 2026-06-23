# CR-SRH-2F-map-v01

## 目的
翠嶺高校2階の詳細配置を固定し、日常の移動・視線・対話の発生位置を安定させる。  
雨宮・真帆・黒瀬の距離感、図書室と生徒会室の対比、屋上前階段の思想対話導線を再現可能にする。

## 参照するCanon
- 01_CANON/02_suirei_high_school.md
- 03_DATA/characters.yaml
- 03_DATA/locations.yaml
- 03_DATA/suirei_high_2f.yaml
- 00_INBOX/chat_logs/GPTとの会話/翠嶺高校全体マップ

## 必須配置
- A棟2F
  - 2年A組
  - 2年B組
  - 2年C組
  - 学年教員スペース
  - 屋上前階段
  - A棟廊下
  - 渡り廊下
  - 中庭

- B棟2F
  - 図書室
  - 生徒会室
  - 閲覧スペース
  - 小会議室
  - 東門・研究センター方面導線
  - 渡り廊下

## 配置思想
2年A組と2年B組は隣接させる。  
雨宮と黒瀬は毎日廊下ですれ違えるが、同じ教室ではない距離にする。  
図書室と生徒会室は同じB棟2Fに置く。  
同じフロアに「人を理解しようとする空間」と「人を整理しようとする空間」が並ぶ構図にする。  
屋上前階段は2年B組から近く、雨宮と黒瀬の思想対話に使いやすい場所にする。  
東側には研究センター方面の外部連携導線を残す。

## 変えてはいけないこと
- 雨宮たちは2年B組。
- 黒瀬は2年A組。
- 図書室は雨宮・真帆側の安全地帯。
- 生徒会室は黒瀬側の拠点。
- 東側には研究センター方面の外部連携導線を残す。
- 中庭はA棟とB棟の視線が抜ける余白として扱う。

## 出力予定
- 04_MAPS/suirei_high_2f_detail.mmd
- 03_DATA/suirei_high_2f.yaml
- 05_PROMPTS/map/prompt_MAP-SRH-2F-v01.md
- 05_PROMPTS/background/prompt_BG-SRH-A2-HALLWAY-v01.md
- 05_PROMPTS/background/prompt_BG-SRH-B2-LIB-SC-HALLWAY-v01.md