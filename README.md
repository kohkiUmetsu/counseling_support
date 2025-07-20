# 美容医療クリニック向けカウンセリングスクリプト改善AIツール

## 概要
美容医療クリニックのカウンセリング品質向上を支援するAIツールです。

## プロジェクト構造
```
/counseling_support
├── frontend/                 # Next.js App router
├── backend/                  # FastAPI (MVC構成)
├── infrastructure/           # IaC (Terraform)
├── docker-compose.yml        # ローカル開発用
├── .env                      # 共通環境変数
└── README.md
```

## 開発環境セットアップ

### 必要な環境
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### ローカル開発環境起動
```bash
# プロジェクトのクローン
git clone <repository-url>
cd counseling_support

# 環境変数の設定
cp .env.example .env
# .envファイルを適切に編集

# Docker環境の起動
docker-compose up -d

# フロントエンド (localhost:3000)
# バックエンド (localhost:8000)
# PostgreSQL (localhost:5432)
# PgVector DB (localhost:5433)
```

### APIドキュメント
バックエンド起動後、以下のURLでAPIドキュメントを確認できます：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 開発フェーズ
- [x] フェーズ1: 基盤システム構築
- [ ] フェーズ2: 音声処理機能
- [ ] フェーズ3: ベクトル検索機能
- [ ] フェーズ4: AIスクリプト生成
- [ ] フェーズ5: 管理ダッシュボード# counseling_support
