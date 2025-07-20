# Next.js App Router 移行記録

## 移行概要

React Router (Pages Router) から Next.js 14 App Router への完全移行を実施しました。

## 主な変更点

### 1. プロジェクト構造変更

**Before (React Router)**:
```
frontend/src/
├── App.tsx
├── pages/
│   ├── RecordingPage.tsx
│   ├── UploadPage.tsx
│   ├── LabelingPage.tsx
│   └── TranscriptionPage.tsx
└── components/
```

**After (Next.js App Router)**:
```
frontend/src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── loading.tsx
│   ├── error.tsx
│   ├── not-found.tsx
│   ├── globals.css
│   ├── upload/page.tsx
│   ├── recording/page.tsx
│   ├── labeling/[sessionId]/page.tsx
│   ├── transcription/[sessionId]/page.tsx
│   └── api/
│       ├── sessions/
│       └── transcriptions/
└── components/
```

### 2. ページコンポーネント変換

- **Client Components**: すべてのページで `'use client'` ディレクティブを追加
- **Dynamic Routes**: `[sessionId]` フォルダ形式でパラメータルートを実装
- **Navigation**: `useRouter` (next/navigation) と `useParams` に変更
- **Link Components**: React Router の `Link` から Next.js の `Link` に変更

### 3. API Routes実装

Next.js App Router のAPI routesを実装し、バックエンドへのプロキシ機能を追加:

- `/api/sessions/upload` - ファイルアップロード
- `/api/sessions/[sessionId]` - セッション取得・更新
- `/api/transcriptions/[sessionId]/start` - 文字起こし開始
- `/api/transcriptions/[sessionId]` - 文字起こし取得
- `/api/transcriptions/[sessionId]/status` - 状況確認

### 4. 設定ファイル

**追加したファイル**:
- `next.config.js` - Next.js設定とプロキシ設定
- `tailwind.config.js` - Tailwind CSS設定
- `postcss.config.js` - PostCSS設定
- `tsconfig.json` - TypeScript設定（パスエイリアス含む）
- `.env.local` / `.env.example` - 環境変数設定

### 5. レイアウト・エラーハンドリング

**実装した特殊ファイル**:
- `layout.tsx` - 共通レイアウトとナビゲーション
- `loading.tsx` - ローディング状態
- `error.tsx` - エラー境界
- `not-found.tsx` - 404ページ

### 6. バックエンド調整

**CORS設定更新**:
```python
allow_origins=[
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]
```

## 技術的改善点

### パフォーマンス
- **Server-Side Rendering**: 初期ページロードの高速化
- **Static Generation**: 可能な部分での静的生成
- **Code Splitting**: 自動的なコード分割

### 開発体験
- **Type Safety**: TypeScriptとの統合強化
- **Path Aliases**: `@/` でのimport簡略化
- **Hot Reload**: より高速な開発時リロード

### SEO・メタデータ
- **Metadata API**: ページごとのSEO最適化
- **structured data**: 検索エンジン対応

## 環境変数

```env
# Next.js環境変数
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1

# API routes用
BACKEND_URL=http://localhost:8000
```

## 起動手順

1. 依存関係インストール:
```bash
cd frontend
npm install
```

2. 開発サーバー起動:
```bash
npm run dev
```

3. 本番ビルド:
```bash
npm run build
npm start
```

## 削除したファイル

- `src/App.tsx` - App Routerでは不要
- `src/pages/` - App Router形式に変換
- React Router関連の設定

## 注意点

- **Client Components**: インタラクティブなコンポーネントには `'use client'` が必要
- **WebSocket**: クライアントサイドでのみ動作
- **API呼び出し**: 環境変数の変更（`REACT_APP_` → `NEXT_PUBLIC_`）

## 今後の拡張可能性

- **Middleware**: 認証やリダイレクト処理
- **Server Actions**: フォーム処理の簡素化
- **Static Generation**: キャッシュ戦略の最適化
- **Edge Runtime**: エッジでの高速処理

移行により、より高いパフォーマンスと開発体験を実現し、Next.js 14の最新機能を活用できるようになりました。