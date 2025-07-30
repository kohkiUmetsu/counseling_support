# インフラ構成変更デプロイ手順

## 変更内容サマリー

### 🎯 主な変更
1. **RDSをパブリックサブネットに移動** - 直接外部アクセス可能に
2. **Bastionホストの削除** - 不要になったため完全除去
3. **セキュリティグループの更新** - 開発環境でのみ全世界からのRDSアクセスを許可

### 📋 変更されたファイル
- `modules/rds/main.tf` - RDS設定の変更
- `modules/rds/variables.tf` - 変数追加・削除
- `environments/dev/main.tf` - モジュール呼び出し更新
- `environments/dev/variables.tf` - 不要変数削除

## デプロイ手順

### 1. 事前準備
```bash
cd /Users/kohkiumetsu/Desktop/Niflo/counseling_support/infrastructure/environments/dev
```

### 2. 現在の状態確認
```bash
terraform plan
```

### 3. 変更の適用
```bash
# 段階的に適用することを推奨
terraform apply -target="module.rds"
```

### 4. 完全適用
```bash
terraform apply
```

### 5. 状態確認
```bash
# RDSエンドポイントを確認
terraform output
```

## 変更後の接続方法

### バックエンドからの接続
```bash
# .envファイルのDATABASE_URLはそのまま使用可能
# RDSが新しくパブリックIPを取得するため、DNS名での接続継続
```

### 直接接続テスト
```bash
# PostgreSQLクライアントで直接接続確認
psql "postgresql://counseling_user:G3modmesi@[NEW_RDS_ENDPOINT]:5432/counseling_db"
```

## ⚠️ 重要な注意事項

### セキュリティ
- **開発環境のみ**: 全世界からのアクセスを許可（0.0.0.0/0）
- **本番環境**: 必ず特定IPアドレスに制限する
- **パスワード**: 現在平文保存 - AWS Secrets Manager移行を検討

### コスト影響
- **削減**: Bastionホスト（EC2インスタンス）削除により月額約$10-15削減
- **変更なし**: RDS自体のコストは変わらず

### 可用性
- **向上**: Bastionホスト経由の単一障害点を除去
- **簡素化**: 接続パスが短縮され、トラブルシューティングが容易

## ロールバック手順（必要時）

```bash
# 変更前の状態に戻す場合
git checkout HEAD~1 -- .
terraform plan
terraform apply
```

## 検証項目

### ✅ デプロイ後チェックリスト
- [ ] RDSインスタンスがパブリックIPを取得
- [ ] セキュリティグループで5432ポートが開放
- [ ] バックエンドアプリケーションからの接続成功
- [ ] Bastionホストリソースの完全削除確認
- [ ] 不要なセキュリティグループの削除確認

### 🔧 接続テスト
```bash
# 1. ネットワーク接続確認
nc -zv [NEW_RDS_ENDPOINT] 5432

# 2. データベース接続確認
psql "postgresql://counseling_user:G3modmesi@[NEW_RDS_ENDPOINT]:5432/counseling_db" -c "SELECT version();"

# 3. バックエンドサーバー起動確認
cd /Users/kohkiumetsu/Desktop/Niflo/counseling_support/backend
python main.py
```

## 次回の改善項目

1. **Secrets Manager導入** - パスワード管理の改善
2. **本番環境設定** - prod/staging環境の構築
3. **監視・アラート** - RDS監視の強化
4. **バックアップ戦略** - 自動バックアップとリストア手順の整備