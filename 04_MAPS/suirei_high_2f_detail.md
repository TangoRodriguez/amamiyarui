# 翠嶺高校2F詳細マップ

VS Code の Markdown Preview Mermaid Support で確認するためのMarkdown版です。  
元のMermaidソースは `04_MAPS/suirei_high_2f_detail.mmd` です。

```mermaid
flowchart LR
  subgraph A棟2F
    A2A[2年A組<br/>黒瀬型]
    A2B[2年B組<br/>雨宮類・日向真帆・小森陸・佐倉律]
    A2C[2年C組<br/>光田芽衣]
    STAFF[学年教員スペース]
    ROOF[屋上前階段]
    AHALL[A棟廊下]
    COURT[中庭]
    WALK[渡り廊下]
  end

  subgraph B棟2F
    LIB[図書室]
    READ[閲覧スペース]
    SC[生徒会室]
    CONF[小会議室]
    ELINE[東門・研究センター方面導線]
    BHALL[B棟廊下]
  end

  A2A --- AHALL
  A2B --- AHALL
  A2C --- AHALL
  STAFF --- AHALL
  A2B --- ROOF
  A2B --- COURT
  COURT --- WALK
  AHALL --- WALK
  WALK --- BHALL
  BHALL --- LIB
  LIB --- READ
  BHALL --- SC
  SC --- CONF
  BHALL --- ELINE
  A2B -.近接.-> A2A
  A2B -.近接.-> A2C
  LIB -.安全地帯.-> A2B
  SC -.拠点.-> A2A
```

## 読み方

- A棟2Fは、日常・教室・すれ違いの軸。
- B棟2Fは、図書室と生徒会室が並ぶ思想対比の軸。
- 2年B組から屋上前階段へ近く、雨宮と黒瀬の思想対話に使いやすい。
- 2年A組と2年B組は隣接し、黒瀬と雨宮が毎日すれ違える。
- B棟廊下の先に東門・研究センター方面導線があり、白庭計画側へ接続する。
