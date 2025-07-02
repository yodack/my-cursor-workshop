# Cursor AI トラブルシューティングガイド

## 概要

このドキュメントは、修正前のルールで作業中の Cursor AI が正しく動作するための具体的な指示集です。
特に api/ui/ ディレクトリでの相対インポートエラーを回避し、Cloud Run デプロイを成功させるための対処法を提供します。

## 背景

プロジェクトルールが更新され、api/ui/ 内では絶対インポート（`from models import ProductModel`）を使用することになりました。
しかし、修正前のルールで作業中の Cursor AI は相対インポート（`from .models import ProductModel`）を使用する可能性があります。
これは Cloud Run 環境でのデプロイ失敗の原因となります。

## プロジェクト構造の理解不足対策

### 🏗️ プロジェクト構造の明確化指示

Cursor AI がプロジェクト構造を理解できていない場合は、以下を指示してください。

```text
このプロジェクトの構造を理解してください：

📁 プロジェクト構造:
cursor-workshop-template/
├── pyproject.toml          # 統合依存関係管理（開発・テスト・デプロイ）
├── api/                    # FastAPI マイクロサービス
│   ├── main.py             # FastAPI アプリケーション
│   ├── models.py           # データモデル（Pydantic）
│   └── storage.py          # ビジネスロジック
├── ui/                     # Streamlit マイクロサービス  
│   └── main.py             # Streamlit アプリケーション
└── tests/                  # テストコード
    ├── api/                # API テスト
    └── ui/                 # UI テスト

🎯 重要な設計原則:
1. api/ と ui/ は独立したマイクロサービス
2. 各サービスは個別に Cloud Run にデプロイ
3. サービス間通信は HTTP API 経由のみ
4. api/ 内では絶対インポート（from models import ProductModel）
5. ui/ から api/ モジュールの直接インポートは禁止

🔧 開発環境:
- ルートの pyproject.toml で全依存関係を管理
- uv を使用（pip は使用禁止）
- テストは常にプロジェクトルートから実行
```

### 🚨 よくある構造理解ミス

#### ミス1: モノリス構造として扱う

**間違った理解:**

```python
# ❌ 間違い：api から ui を直接呼び出し
from ui.main import render_page
```

**正しい指示:**

```text
api/ と ui/ は完全に独立したサービスです。
- api/ は REST API のみを提供
- ui/ は API を HTTP で呼び出してデータを取得
- 相互の直接インポートは禁止
```

#### ミス2: ネストした構造として扱う

**間違った理解:**

```python
# ❌ 間違い：パッケージ名付きインポート
from api.models import ProductModel
from ui.components import Header
```

**正しい指示:**

```text
api/ ディレクトリ内では絶対インポートを使用:
- ✅ 正しい: from models import ProductModel
- ❌ 間違い: from api.models import ProductModel

ui/ ディレクトリ内でも同様:
- ✅ 正しい: from utils import format_price
- ❌ 間違い: from ui.utils import format_price
```

#### ミス3: 共有コードの誤解

**間違った理解:**

```python
# ❌ 間違い：共有モデルの直接インポート
from api.models import ProductModel  # UI から
```

**正しい指示:**

```text
共有データ構造が必要な場合:
1. API でデータ形式を定義
2. UI では API レスポンスを JSON として処理
3. 必要に応じて UI 側で独自の型定義を作成

例:
# api/models.py
class ProductModel(BaseModel):
    id: int
    name: str
    price: float

# ui/main.py  
response = requests.get(f"{API_URL}/items/1")
product_data = response.json()  # dict として処理
```

### 📋 プロジェクト構造確認チェックリスト

Cursor AI に以下を確認させてください。

```text
プロジェクト構造の理解度チェック:

□ api/ ディレクトリの役割を理解している
  - FastAPI アプリケーション
  - 独立したマイクロサービス
  - 絶対インポートの使用

□ ui/ ディレクトリの役割を理解している  
  - Streamlit アプリケーション
  - API を HTTP で呼び出し
  - 独立したマイクロサービス

□ tests/ ディレクトリの役割を理解している
  - プロジェクトルートから実行
  - api/ と ui/ を外部からテスト
  - 統合テスト環境

□ デプロイ構造を理解している
  - api/ → Cloud Run サービス1
  - ui/ → Cloud Run サービス2  
  - 個別スケーリング可能

理解できていない場合は、再度プロジェクト構造を説明してください。
```

## API開発時のトラブルシューティング

### 🚨 緊急指示：絶対インポートの強制

Cursor AI に以下を指示してください。

```text
API開発では、api/ディレクトリ内のモジュール間インポートは必ず絶対インポートを使用してください。

正しい例:
from models import ProductModel
from storage import InMemoryStorage

絶対に使用禁止:
from .models import ProductModel      # 相対インポート
from api.models import ProductModel   # パッケージ名付き

理由: Cloud Run環境では相対インポートが失敗するため、絶対インポートが必須です。
```

### FastAPI アプリケーション作成時の指示

```text
api/main.py を作成する際は、以下のインポート形式を厳守してください。

from fastapi import FastAPI
from fastapi import HTTPException, status
from models import ProductModel     # ← 必ず絶対インポート
from storage import InMemoryStorage # ← 必ず絶対インポート

app = FastAPI(title="商品管理API")
storage = InMemoryStorage()
```

### 相対インポートエラーの緊急修正

#### 自動修正コマンド（VS Code/Cursor）

1. **検索・置換を開く**: `Ctrl+Shift+H` (Windows/Linux) または `Cmd+Shift+H` (Mac)

2. **一括置換パターン**:

   ```regex
   置換対象: from \.([a-zA-Z_][a-zA-Z0-9_]*)
   置換後: from $1
   正規表現: ON
   ```

3. **個別置換パターン**:

   ```text
   from .models → from models
   from .storage → from storage
   from .utils → from utils
   from api.models → from models
   from api.storage → from storage
   ```

#### 手動修正チェックリスト

api/ ディレクトリ内の全 .py ファイルで以下を確認してください。

- [ ] `from .` で始まるインポートがない
- [ ] `from api.` で始まるインポートがない
- [ ] すべてのローカルモジュールが絶対インポートになっている

## Cloud Run デプロイ時のトラブルシューティング

### デプロイ前必須チェックリスト

Cursor AI に以下の作業を指示してください。

```text
Cloud Run デプロイ前に以下を必ず実行してください。

1. api/__init__.py の作成（空ファイルでOK）:
touch api/__init__.py

2. requirements.txt の生成:
uv pip compile pyproject.toml --extra api -o api/requirements.txt

3. Procfile の作成:
echo 'web: gunicorn --bind 0.0.0.0:$PORT --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker main:app' > api/Procfile

4. インポートの最終確認:
api/ディレクトリ内のすべての .py ファイルで相対インポートがないことを確認してください。
```

### ImportError 対処法

#### エラー: `ImportError: attempted relative import with no known parent package`

**原因**: 相対インポートが使用されている  
**解決法**:

```text
以下の修正を即座に実行してください。

1. エラーが発生したファイルを開く
2. すべての "from ." を "from " に変更（ピリオドを削除）
3. "from api." で始まるインポートを "from " に変更
4. ファイルを保存して再度テスト実行
```

#### エラー: `ModuleNotFoundError: No module named 'models'`

**原因**: `__init__.py` が不足している  
**解決法**:

```bash
以下を実行してください:
touch api/__init__.py

そして以下で動作確認:
cd api && python -c "import models; print('OK')"
```

### デプロイ失敗の診断手順

#### 1. ローカル環境での事前確認

```bash
# api/ ディレクトリで動作確認
cd api
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 別ターミナルでテスト
curl http://localhost:8000/health
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"test","price":100}'
```

#### 2. Cloud Run ログの確認

```bash
# デプロイ後のログ確認
gcloud logs read --service=your-service-name --limit=50
```

よくあるエラーパターンは次のとおりです。

- `ImportError`: インポート問題
- `Container failed to start`: Procfile の問題
- `Port binding error`: ポート設定の問題

## Web UI 開発時のトラブルシューティング

### Streamlit アプリケーション作成時の指示

```text
ui/main.py を作成する際のインポートルール:

✅ 外部ライブラリ:
import streamlit as st
import requests
import json

✅ API との通信:
API_URL = "http://localhost:8000"  # 開発環境
# 本番環境では環境変数を使用:
# API_URL = os.getenv("API_URL", "https://your-api-url")

❌ 禁止事項:
# api/ディレクトリのモジュールを直接インポートしない
# from api.models import ProductModel  # これは禁止
# from models import ProductModel      # これも禁止

理由: UIとAPIは独立したマイクロサービスとして動作します。
API との通信は HTTP リクエスト経由で行ってください。
```

## 緊急対処法とテンプレート

### 🆘 緊急時の包括的な修正手順

既に相対インポートでコードが書かれている場合は、次の手順を実行してください。

```bash
# 1. api/ ディレクトリに移動
cd api

# 2. 相対インポートを一括修正（Linux/Mac）
find . -name "*.py" -exec sed -i 's/from \./from /g' {} \;
find . -name "*.py" -exec sed -i 's/from api\./from /g' {} \;

# 3. Windows の場合（PowerShell）
Get-ChildItem -Path . -Filter "*.py" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'from \.', 'from ' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace 'from api\.', 'from ' | Set-Content $_.FullName
}

# 4. 動作確認
python -m pytest  # テストが通ることを確認
uv run uvicorn main:app --reload  # アプリが起動することを確認
```

### Cursor AI への具体的指示テンプレート

#### API開発開始時

```text
これからFastAPIアプリケーションを開発します。重要な制約があります。

絶対遵守事項:
- api/ディレクトリ内では絶対インポートのみ使用
- 例: from models import ProductModel
- 禁止: from .models import ProductModel
- 禁止: from api.models import ProductModel

この制約は Cloud Run デプロイ時のエラー回避のため必須です。
すべてのコードでこのルールを厳守してください。
```

#### Cloud Run デプロイ前

```text
Cloud Run デプロイを実行します。デプロイ前に以下を確認してください。

1. api/__init__.py が存在する（空ファイルでOK）
2. api/requirements.txt が最新である
3. api/Procfile が正しい
4. api/ 内のすべての .py ファイルで絶対インポートを使用している

これらの確認後、デプロイを実行してください。
```

#### UI開発開始時

```text
Streamlit アプリケーションを開発します。重要事項：

- api/ディレクトリのモジュールを直接インポートしない
- APIとの通信はHTTPリクエスト（requests/httpx）を使用
- 独立したマイクロサービスとして設計

例:
✅ response = requests.get(f"{API_URL}/items/1")
❌ from api.models import ProductModel
```

## よくある質問と回答

### Q: なぜ相対インポートが禁止なのでしょうか

A: Cloud Run 環境では api/ ディレクトリの内容が直接 /app にデプロイされます。
このため、相対インポートは実行時に失敗します。絶対インポートを使用することで、
ローカル開発環境とクラウド環境の両方で動作するコードになります。

### Q: api/models.py を ui/ から使用したいのですが

A: 直接インポートではなく、API エンドポイント経由でデータを取得してください。
これにより、各サービスが独立し、個別にスケールできる
マイクロサービス アーキテクチャを実現できます。

### Q: テストコードではどうすべきでしょうか

A: テストコードは tests/ ディレクトリにあり、api/ 外部から api/ モジュールをテストするため、以下のようにインポートします。

```python
# tests/api/test_main.py
from httpx import ASGITransport, AsyncClient
from api.main import app  # これは正しい（外部からのインポート）
```

### Q: 既存コードの修正が大変

A: 検索・置換機能を使用すれば一括修正可能です。VS Code/Cursor で
`Ctrl+Shift+H` を開き、正規表現モードで
`from \.([a-zA-Z_][a-zA-Z0-9_]*)` を `from $1` に置換してください。

## まとめ

- API 開発では絶対インポートを厳守
- デプロイ前には必須ファイルを確認
- エラー時には相対インポートを一括修正
- UI 開発では HTTP 通信で API と連携
- 緊急時にはこのドキュメントの指示を Cursor AI にコピー&ペースト

このガイドに従うことで、Cursor AI が古いルールで作業している場合でも、
適切に動作させることができます。
