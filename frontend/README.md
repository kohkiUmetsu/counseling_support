# Counseling Support System - Frontend

Next.js App Router を使用したフロントエンドアプリケーション

## セットアップ

1. 依存関係のインストール
```bash
npm install
```

2. 環境変数の設定
```bash
cp .env.example .env.local
```

3. 開発サーバーの起動
```bash
npm run dev
```

## 主要な機能

- **音声録音**: ブラウザでの音声録音とリアルタイム波形表示
- **ファイルアップロード**: ドラッグ&ドロップ対応の音声ファイルアップロード
- **ラベリング**: セッションの成功/失敗ラベル付け
- **文字起こし**: OpenAI Whisperを使用した自動文字起こし
- **データ管理**: 話者分離とタイムスタンプ付きの文字起こし表示・編集

## ページ構成

- `/`: ホームページ（アップロードページにリダイレクト）
- `/upload`: 音声ファイルアップロード
- `/recording`: ブラウザ音声録音
- `/labeling/[sessionId]`: セッションラベリング
- `/transcription/[sessionId]`: 文字起こし表示・編集

## 技術スタック

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **API Client**: Axios
- **WebSocket**: Native WebSocket API
- **Icons**: Lucide React

## 開発時の注意点

- バックエンドAPIは `http://localhost:8000` で起動している必要があります
- WebSocket接続は `ws://localhost:8000/api/v1/ws/{sessionId}` で行います
- API routes は `/api/*` パスでNext.jsのプロキシ機能を使用できます