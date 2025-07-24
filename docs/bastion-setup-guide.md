# Bastion Host Setup Guide

## 概要

このガイドでは、ECSタスクでマイグレーション後のデータベースを確認するため、EC2踏み台サーバー経由でRDSに接続する方法を説明します。

## 構成

- **EC2 Bastion Host**: パブリックサブネットに配置
- **RDS PostgreSQL**: プライベートサブネットに配置（Main DB + Vector DB）
- **Security Groups**: 踏み台からRDSへの接続を許可

## セットアップ手順

### 1. SSHキーペアの作成

```bash
# AWSコンソールまたはCLIでキーペアを作成
aws ec2 create-key-pair --key-name counseling-support-dev-key --query 'KeyMaterial' --output text > ~/.ssh/counseling-support-dev-key.pem
chmod 400 ~/.ssh/counseling-support-dev-key.pem
```

### 2. Terraformでインフラを構築

```bash
cd infrastructure/environments/dev

# 初期化
terraform init

# プラン確認
terraform plan

# 適用
terraform apply
```

### 3. 踏み台サーバーのIPアドレス取得

```bash
terraform output bastion_public_ip
```

## 接続方法

### 方法1: ヘルパースクリプトを使用（推奨）

```bash
# セットアップ情報を表示
./scripts/connect-bastion.sh setup

# 踏み台サーバーにSSH接続
BASTION_IP=<取得したIP> ./scripts/connect-bastion.sh ssh

# メインデータベースに接続
BASTION_IP=<取得したIP> ./scripts/connect-bastion.sh db-main

# ベクターデータベースに接続
BASTION_IP=<取得したIP> ./scripts/connect-bastion.sh db-vector
```

### 方法2: 直接SSH接続

```bash
# 踏み台サーバーに接続
ssh -i ~/.ssh/counseling-support-dev-key.pem ec2-user@<BASTION_IP>

# 踏み台サーバー上でデータベース接続スクリプトを実行
./connect-db.sh
```

## データベース接続情報

踏み台サーバー上の`connect-db.sh`スクリプトは以下の接続先を提供します：

1. **Main Database**
   - Host: RDS PostgreSQL endpoint
   - Database: counseling_db
   - User: counseling_user

2. **Vector Database**
   - Host: Aurora PostgreSQL endpoint
   - Database: counseling_vector_db
   - User: vector_user

## よく使用するSQLコマンド

### データベースの確認
```sql
-- データベース一覧
\l

-- テーブル一覧
\dt

-- テーブル構造確認
\d table_name

-- マイグレーション状態確認
SELECT * FROM alembic_version;
```

### データ確認
```sql
-- ユーザーテーブル
SELECT id, username, email, created_at FROM users LIMIT 10;

-- セッションテーブル
SELECT id, user_id, created_at, status FROM counseling_sessions LIMIT 10;

-- ベクターデータ（Vector DBの場合）
SELECT id, content, vector IS NOT NULL as has_vector FROM embeddings LIMIT 10;
```

## トラブルシューティング

### 接続エラーの場合

1. **SSH接続できない**
   - セキュリティグループで22番ポートが開いているか確認
   - SSHキーのパスとパーミッションを確認

2. **データベース接続できない**
   - RDSのセキュリティグループで踏み台からの5432番ポート接続が許可されているか確認
   - データベースのエンドポイントが正しいか確認

3. **パスワードが不明**
   ```bash
   # Terraform変数を確認
   terraform output -json | grep password
   ```

### セキュリティグループの確認

```bash
# 踏み台のセキュリティグループ
aws ec2 describe-security-groups --filters "Name=group-name,Values=*bastion*"

# RDSのセキュリティグループ
aws ec2 describe-security-groups --filters "Name=group-name,Values=*rds*"
```

## セキュリティ考慮事項

- 踏み台サーバーは開発環境でのみ使用
- 本番環境では必要に応じてSSM Session Managerを使用を検討
- 定期的なセキュリティアップデートの実施
- 不要な場合は踏み台サーバーを停止

## 清理

開発終了後は以下でリソースを削除できます：

```bash
cd infrastructure/environments/dev
terraform destroy
```