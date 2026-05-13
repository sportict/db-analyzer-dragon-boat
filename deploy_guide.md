# デプロイ手順書 ― ドラゴンボート レース分析ツール

このツールは静的Webサイトなので、HTML/CSVファイルを置けるホスティングならどこでも動きます。本書では **GitHub Pages**(推奨)と **Netlify Drop**(超簡単版)の2通りを説明します。

---

## 推奨: GitHub Pages

**所要時間** 約15分(初回のみ。以降のデータ更新は1〜2分)
**費用** 無料(月10万人アクセスまで)
**URL例** `https://k-murata.github.io/db-analyzer/`

### 手順1. GitHubアカウント作成 (5分)

1. https://github.com を開く
2. 「Sign up」から無料アカウント作成
3. メール認証を完了

### 手順2. リポジトリ作成 (3分)

1. GitHubトップ右上の「+」→「New repository」
2. リポジトリ名: `db-analyzer` (お好みで)
3. 「Public」を選択
4. 「Add a README file」にチェック
5. 「Create repository」をクリック

### 手順3. ファイルをアップロード (5分)

1. リポジトリ画面で「Add file」→「Upload files」
2. このフォルダ(`db-analyzer-public`)の中身を **すべて** ドラッグ&ドロップ
   - `index.html`、`manifest.json`、`README.md`、`generate_manifest.py`、`data/` フォルダ全体
3. 下の「Commit changes」をクリック

### 手順4. GitHub Pagesを有効化 (2分)

1. リポジトリ画面 → 上部「Settings」タブ
2. 左サイドバー「Pages」をクリック
3. 「Branch」セクションで `main` を選択、フォルダは `/ (root)` のまま「Save」
4. 1〜2分待つと、ページ上部に公開URLが表示される
   - 例: `https://<あなたのID>.github.io/db-analyzer/`

### 手順5. 動作確認

公開URLにアクセス。「📁 大会別レース一覧」が表示されればOK。

### データを更新するとき

**GUI(ブラウザ)で**: リポジトリ画面で `data/<日付>/` を開き、「Add file → Upload files」でCSVを追加 → コミット。`manifest.json` も同じ要領で差し替え。

**自動化したい場合**: ローカルにGitをインストールし、`git clone`して `generate_manifest.py` を実行して `git push`。

---

## お手軽版: Netlify Drop

**所要時間** 3分
**費用** 無料(月100GB帯域まで)
**URL例** `https://practical-mendel-abc123.netlify.app/` (ランダム)

### 手順

1. https://app.netlify.com/drop を開く(アカウント不要、初回のみ作成画面)
2. このフォルダ(`db-analyzer-public`)をブラウザにドラッグ&ドロップ
3. 数秒で公開URLが発行される
4. URLをコピーして配布

### 注意点
- URLは初期はランダム文字列。後で「Site settings → Change site name」で好きな名前に変更可
- データを更新するときは、変更後のフォルダを **もう一度ドラッグ&ドロップ**(同じサイトに上書きしたい場合は管理画面から)

---

## チーム個別URL の作り方

公開URLが `https://<host>/` だとして、チームへ送るリンクは:

```
https://<host>/?team=魚橋水神龍会&races=data/2025-11-02/R24_オープン決勝_02_魚橋水神龍会.csv,data/2025-11-02/R24_オープン決勝_03_磯風漕友会.csv
```

| パラメータ | 役割 |
|-----------|------|
| `team` | 上部バナーに「○○向け表示」と表示。タイトルバーにも反映 |
| `races` | カンマ区切りで CSV のパス。複数指定で重ね描き |

**実用例: チーム別URLをまとめて生成する**

Excelで以下のような表を作って、URLをコピペで配布:

| チーム | 比較対象 | URL |
|--------|----------|-----|
| 魚橋水神龍会 | bp, 磯風漕友会 | https://.../?team=魚橋水神龍会&races=data/2025-11-02/R24_オープン決勝_02_魚橋水神龍会.csv,data/2025-11-02/R24_オープン決勝_03_磯風漕友会.csv,data/2025-11-02/R24_オープン決勝_04_bp.csv |
| bp | 上位2チーム | https://.../?team=bp&races=... |

---

## トラブルシューティング

- **「📁 大会別レース一覧」が表示されない** → `manifest.json` の配置を確認。`index.html` と同じ階層に必要。
- **レースを選んでも CSV が読めない** → ブラウザの開発者ツール (F12) でNetworkタブを確認。ファイル名にスペースや日本語が含まれている場合、URLエンコードの問題で読めないことがある。その場合 GitHub Pages 経由ならOK、ローカル file:// では制約あり。
- **ローカルでテストしたい** → `cd db-analyzer-public && python3 -m http.server 8000` で `http://localhost:8000/` にアクセス。

---

## プライバシーに関する注意

GitHub Pages も Netlify も基本は **誰でもURLを知っていればアクセス可能**。次のいずれかでアクセス制限が必要な場合は別途検討:

1. GitHub Pro($4/月)+ Private Pages
2. Netlify の Password Protection ($19/月)
3. ベーシック認証つきレンタルサーバ

ただし大会結果は元々公開情報のため、現実的には公開で問題ないと判断。
