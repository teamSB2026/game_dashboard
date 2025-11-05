# 🥤 Bridge2025 利き〇〇可視化ダッシュボード

このアプリは **Bridge2025** イベントで使用される「利き〇〇」ゲームの集計結果を可視化する Streamlit ダッシュボードです。  
各班の回答をランダム生成し、色ごとの集計とドリンク別の人気傾向をグラフで表示します。

---

## 🚀 セットアップ手順（`uv` 使用版）

### 1️⃣ `uv` のインストール（初回のみ）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> **Windows の場合：**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

### 2️⃣ プロジェクトの初期化（初回のみ）

プロジェクトディレクトリで以下を実行：
```bash
uv init
```

これで `pyproject.toml` が自動生成されます。

---

### 3️⃣ 依存関係のインストール

**方法A: requirements.txt がある場合**
```bash
uv pip install -r requirements.txt
```

**方法B: requirements.txt がない場合**
```bash
uv add streamlit pandas numpy streamlit-autorefresh altair
```

---

## 🧠 実行方法
```bash
uv run streamlit run app_tea.py
```

実行後、ターミナルに表示される URL（例：  
👉 http://localhost:8501 ）をブラウザで開くと、ダッシュボードが表示されます。

---

## 📁 ディレクトリ構成
```bash
project-root/
├── app_sport.py
├── app_tea.py          # メイン Streamlit アプリ
├── assets/
│   └── header.png      # ヘッダー画像（任意）
├── requirements.txt    # 依存関係（任意）
├── pyproject.toml      # uv管理ファイル（uv initで生成）
├── .python-version     # Pythonバージョン（uv initで生成）
└── README.md           # このファイル
```

---

## 💡 アプリの特徴

- ページは **3秒ごとに自動リフレッシュ** され、結果が動的に更新されます。  
- 集計テーブルでは各班のドリンク選択を **色分け可視化**。  
- Altair を用いた **棒グラフ可視化** により、ドリンク別の人気傾向が一目でわかります。  
- シンプルかつモダンなデザイン（CSS カスタマイズ済み）。  

---

## 📸 画面例

![alt text](assets/image.png)

---

## 📜 使用技術

- **Python 3.10+**
- **uv**（高速パッケージマネージャ）
- **Streamlit**
- **Pandas / Numpy**
- **Altair**
- **streamlit-autorefresh**

---

## 🛠️ トラブルシューティング

### `No pyproject.toml found` エラーが出た場合

プロジェクトディレクトリで以下を実行してください：
```bash
uv init
```

その後、依存関係をインストール：
```bash
uv add streamlit pandas numpy streamlit-autorefresh altair
```

### 他の環境で実行する場合

プロジェクトをクローン/ダウンロード後：
```bash
cd project-root
uv sync
uv run streamlit run app_tea.py
```

### Python バージョンを指定したい場合
```bash
uv init --python 3.10
```

---

## 🧾 ライセンス / クレジット

© Bridge 2025 利きゲーム  
Produced by Bridge Team