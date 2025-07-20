# フェーズ1: 基盤システム構築チケット

## 概要
美容医療クリニック向けカウンセリングスクリプト改善AIツールの基盤インフラとプロジェクト構造を構築するフェーズです。

---

## チケット F1-001: プロジェクト構造セットアップ
**優先度**: 高  
**見積**: 4時間  
**担当者**: バックエンドエンジニア

### 説明
プロジェクトの基本ディレクトリ構造を作成し、開発環境を整備する。

### 要件
- 要件定義書第9章に記載されたディレクトリ構造の実装
- Next.js 14 + TypeScript (frontend)
- FastAPI + Python 3.11 (backend)
- Docker環境の構築

### 受け入れ条件
- [x] frontend/, backend/, infrastructure/ ディレクトリが作成されている
- [x] docker-compose.yml でローカル開発環境が起動する
- [x] 各サービスが正常に立ち上がることを確認

### 技術詳細
```
/counseling_support
├── frontend/                 # Next.js App router
├── backend/                  # FastAPI (MVC構成)
├── infrastructure/           # IaC (Terraform)
├── docker-compose.yml        # ローカル開発用
├── .env                      # 共通環境変数
└── README.md
```

---

## チケット F1-002: データベース設計・構築
**優先度**: 高  
**見積**: 6時間  
**担当者**: バックエンドエンジニア

### 説明
要件定義書第7章のデータモデルに基づいてデータベースを設計・構築する。

### 要件
- Amazon RDS (PostgreSQL) の構築
- Aurora PostgreSQL + pgvector の構築
- テーブル定義の実装

### 受け入れ条件
- [x] counseling_sessions テーブルが作成されている
- [x] transcriptions テーブルが作成されている
- [x] improvement_scripts テーブルが作成されている
- [x] success_conversation_vectors テーブル（pgvector対応）が作成されている
- [x] 各テーブル間のリレーションが正しく設定されている

### 技術詳細
```sql
-- 主要テーブル
- counseling_sessions: カウンセリングセッション管理
- transcriptions: 文字起こしデータ保存
- improvement_scripts: 改善スクリプト履歴
- success_conversation_vectors: ベクトル化された成功会話（pgvector）
```

---

## チケット F1-003: AWS基盤インフラ構築（Terraform）
**優先度**: 高  
**見積**: 8時間  
**担当者**: インフラエンジニア

### 説明
Terraformを使用してAWS上にインフラを構築する。

### 要件
- ECS + Fargate クラスター構築
- Application Load Balancer (ALB) 設定
- Amazon S3 バケット作成（音声ファイル保存用）
- VPC、セキュリティグループ設定

### 受け入れ条件
- [x] ECS + Fargate環境が動作している
- [x] ALBでHTTPS通信が可能
- [x] S3バケットが作成され、適切な権限設定がされている
- [x] RDS、Aurora接続が可能な状態
- [x] 開発・ステージング・本番環境の分離ができている

### 技術詳細
```
infrastructure/
├── modules/
│   ├── ecs/           # ECSクラスター設定
│   ├── rds/           # データベース設定
│   ├── s3/            # ストレージ設定
│   └── vpc/           # ネットワーク設定
├── environments/
│   ├── dev/           # 開発環境
│   ├── staging/       # ステージング環境
│   └── prod/          # 本番環境
```

---

## チケット F1-004: バックエンドAPI基盤構築
**優先度**: 高  
**見積**: 6時間  
**担当者**: バックエンドエンジニア

### 説明
FastAPIを使用してバックエンドAPIの基本構造を構築する。

### 要件
- FastAPI + SQLAlchemy + Alembic構成
- MVC設計パターンの実装
- OpenAPI仕様書自動生成
- DB接続設定

### 受け入れ条件
- [x] FastAPIアプリケーションが起動する
- [x] /docs でOpenAPI仕様書が表示される
- [x] データベース接続が正常に動作する
- [x] ヘルスチェックエンドポイントが実装されている
- [x] CORS設定が適切に行われている

### 技術詳細
```
backend/app/
├── api/            # ルーティング (Controller)
├── core/           # DB接続, 設定
├── models/         # SQLAlchemyモデル (Model)
├── schemas/        # Pydanticスキーマ (DTO)
├── services/       # ビジネスロジック (Service)
├── utils/          # 共通ユーティリティ
└── main.py         # アプリエントリポイント
```

---

## チケット F1-005: フロントエンド基盤構築
**優先度**: 高  
**見積**: 5時間  
**担当者**: フロントエンドエンジニア

### 説明
Next.js 14を使用してフロントエンドの基本構造を構築する。

### 要件
- Next.js 14 + TypeScript + Tailwind CSS
- App Router構成
- APIクライアント実装
- レイアウトコンポーネント作成

### 受け入れ条件
- [x] Next.jsアプリケーションが起動する
- [x] Tailwind CSSが適用されている
- [x] バックエンドAPIとの通信が可能
- [x] 基本的なページレイアウトが実装されている
- [x] TypeScriptの型チェックが通る

### 技術詳細
```
frontend/app/
├── components/      # 再利用可能コンポーネント
├── lib/            # APIクライアント・hooks
├── styles/         # スタイル定義
├── utils/          # ユーティリティ関数
└── pages/          # ページコンポーネント
```

---

## フェーズ1完了条件
- [x] 全チケットが完了している
- [x] ローカル開発環境でフロントエンド・バックエンドが正常動作する
- [x] AWS環境にデプロイが完了している（Terraform設定完了）
- [x] データベース接続が正常に動作している
- [x] 基本的なHTTPSでのAPI通信が可能（インフラ設定完了）