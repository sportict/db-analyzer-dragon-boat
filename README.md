# ドラゴンボート レース分析ツール - 公開フォルダ

このフォルダをWebに公開すると、URLを知っている人がブラウザから直接GPSデータを閲覧・分析できます。

## ファイル構成

```
db-analyzer-public/
├── index.html              ← 解析ツール本体
├── manifest.json           ← レース一覧データ (CSV経路、自動生成)
├── race_results.json       ← 公式タイム・着順データ (PDF解析、自動生成)
├── generate_manifest.py    ← manifest.json 生成 + xlsx→csv 変換
├── scripts/
│   └── parse_race_results.py  ← PDF → race_results.json 解析スクリプト
├── README.md
├── deploy_guide.md
└── data/                   ← GPS CSV データ
    ├── 2025-11-02/         (53レース)
    └── 2025-11-16/         (19レース)
```

## 機能

1. **GPS速度プロファイル可視化**: CSV/XLSXからスピード曲線を描画。複数レースを重ね描き比較。
2. **公式タイム表示**: race_results.jsonの公式タイム・着順を自動表示。
3. **URLパラメータ起動**: `?team=...&races=...` でチーム別カスタムURL。
4. **xlsx対応**: ブラウザ上の直接ドロップ・サーバ側自動変換の両方に対応。

## データ更新ワークフロー

### 新しい大会データを追加するとき

```bash
# 1. CSV/XLSX を所定フォルダに置く
mkdir -p data/2026-XX-XX
cp /path/to/*.csv data/2026-XX-XX/      # CSV/XLSX どちらも可

# 2. manifest.json を更新 (xlsxは自動的にcsv変換)
python3 generate_manifest.py

# 3. レース結果PDFを解析して race_results.json を更新
python3 scripts/parse_race_results.py path/to/結果.pdf -o race_results.json

# 4. Webへデプロイ (git push もしくは Netlify Drop)
```

### ファイル命名規約

`R<番号>_<クラス>_<レーン>_<チーム名>.csv|xlsx`

例:
- `R24_オープン決勝_02_魚橋水神龍会.csv`
- `R25_混合決勝_01_関西龍舟シンバ.xlsx`

この規約に従うと、ツール側で自動的に公式タイムとマッチングされます。

## URLパラメータでの呼び出し

### 公開ページ
```
https://<host>/
```

### チーム個別URL(おすすめチームと比較対象を事前ロード)
```
https://<host>/?team=魚橋水神龍会&races=data/2025-11-02/R24_オープン決勝_02_魚橋水神龍会.csv,data/2025-11-02/R24_オープン決勝_03_磯風漕友会.csv
```

| パラメータ | 役割 |
|-----------|------|
| `team` | 上部バナーに「○○向け表示」と表示 |
| `races` | カンマ区切りで CSV パス |
