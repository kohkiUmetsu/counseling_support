# フェーズ5: 管理画面・レポート機能チケット

## 概要
生成されたスクリプトの管理・表示、品質メトリクスの可視化、成約率分析などの管理機能を実装するフェーズです。要件定義書の機能F006に対応します。

---

## チケット F5-001: スクリプト表示・管理画面（F006）
**優先度**: 高  
**見積**: 8時間  
**担当者**: フロントエンドエンジニア

### 説明
最新版スクリプトの表示と基本的な管理機能を実装する。

### 要件
- 最新版スクリプトの読みやすい表示
- フェーズ別（オープニング、ニーズ確認、提案、クロージング）の構造化表示
- Markdown形式での表示対応
- 印刷・共有機能

### 受け入れ条件
- [x] 最新スクリプトが見やすいレイアウトで表示される
- [x] フェーズごとにタブ分けまたはセクション分けされる
- [x] Markdownが適切にレンダリングされる
- [x] 印刷用レイアウトが提供される
- [x] URLで特定スクリプトを直接共有できる

### 技術詳細
```typescript
// Next.js App Router実装
// app/scripts/[id]/page.tsx - メインスクリプト表示ページ
// app/scripts/[id]/components/ - ページ専用コンポーネント
// app/components/scripts/ - 共通スクリプトコンポーネント

// ページコンポーネント (app/scripts/[id]/page.tsx)
import { Suspense } from 'react';
import { ScriptViewer } from './components/ScriptViewer';
import { ScriptViewerSkeleton } from './components/ScriptViewerSkeleton';

interface PageProps {
  params: { id: string };
  searchParams: { phase?: string };
}

export default async function ScriptViewerPage({ params, searchParams }: PageProps) {
  return (
    <div className="container mx-auto p-6">
      <Suspense fallback={<ScriptViewerSkeleton />}>
        <ScriptViewer 
          scriptId={params.id} 
          initialPhase={searchParams.phase || 'opening'}
        />
      </Suspense>
    </div>
  );
}

// クライアントコンポーネント (app/scripts/[id]/components/ScriptViewer.tsx)
'use client';

import { useState } from 'react';
import { useScript } from '@/hooks/useScript';
import { ScriptHeader } from '@/components/scripts/ScriptHeader';
import { ScriptPhaseNavigator } from '@/components/scripts/ScriptPhaseNavigator';
import { ScriptContent } from '@/components/scripts/ScriptContent';
import { ScriptActions } from '@/components/scripts/ScriptActions';

interface ScriptViewerProps {
  scriptId: string;
  initialPhase: string;
}

export function ScriptViewer({ scriptId, initialPhase }: ScriptViewerProps) {
  const [activePhase, setActivePhase] = useState(initialPhase);
  const { data: script, isLoading } = useScript(scriptId);

  if (isLoading) return <ScriptViewerSkeleton />;

  return (
    <div className="script-viewer">
      <ScriptHeader script={script} />
      <ScriptPhaseNavigator 
        phases={['opening', 'needs_assessment', 'solution_proposal', 'closing']}
        activePhase={activePhase}
        onPhaseChange={setActivePhase}
      />
      <ScriptContent 
        content={script.content[activePhase]}
        successFactors={script.success_factors}
        improvementPoints={script.improvement_points}
      />
      <ScriptActions 
        onPrint={() => window.print()}
        onShare={() => copyToClipboard(window.location.href)}
      />
    </div>
  );
}

// 使用技術
- Next.js 14+ App Router + TypeScript
- Server/Client Components分離
- react-markdown (Markdownレンダリング)
- Tailwind CSS (スタイリング)
- Suspense境界とSkeleton UI
```

---

## チケット F5-002: スクリプト履歴・バージョン管理（F006）
**優先度**: 高  
**見積**: 6時間  
**担当者**: フルスタックエンジニア

### 説明
過去のスクリプト履歴の管理と版間比較機能を実装する。

### 要件
- 履歴一覧表示（生成日時、バージョン、品質スコア）
- バージョン間の差分比較
- 特定バージョンの復元機能
- アクティブバージョンの管理

### 受け入れ条件
- [x] スクリプト履歴が時系列で表示される
- [x] 2つのバージョンを選択して差分表示できる
- [x] 過去バージョンをアクティブに戻せる
- [x] バージョン切り替えがリアルタイムで反映される
- [x] 削除防止機能が実装される

### 技術詳細
```typescript
// フロントエンドコンポーネント
- ScriptHistory: 履歴一覧表示
- VersionComparison: バージョン比較
- VersionDiff: 差分表示
- VersionManager: バージョン管理操作

// バックエンドAPI
GET /api/v1/scripts/history
GET /api/v1/scripts/compare?v1={id1}&v2={id2}
POST /api/v1/scripts/{id}/activate
DELETE /api/v1/scripts/{id}

// 差分表示ライブラリ
import { diffChars, diffWords } from 'diff';

const VersionDiff = ({ oldVersion, newVersion }) => {
  const diff = diffWords(oldVersion.content, newVersion.content);
  
  return (
    <div className="version-diff">
      {diff.map((part, index) => (
        <span 
          key={index}
          className={classNames({
            'bg-red-200': part.removed,
            'bg-green-200': part.added,
            'bg-gray-100': !part.added && !part.removed
          })}
        >
          {part.value}
        </span>
      ))}
    </div>
  );
};
```

---

## チケット F5-003: 品質メトリクス可視化ダッシュボード（F006）
**優先度**: 高  
**見積**: 10時間  
**担当者**: フロントエンドエンジニア

### 説明
スクリプト品質メトリクス（カバレッジ率、新規性、推奨信頼度）の可視化ダッシュボードを実装する。

### 要件
- カバレッジ率の視覚的表示
- 新規性スコアのトレンド表示
- 推奨信頼度の詳細内訳
- 成功パターン分析結果の可視化

### 受け入れ条件
- [x] 品質メトリクスが直感的なグラフで表示される
- [x] カバレッジ率が円グラフまたはプログレスバーで表示される
- [x] 新規性スコアの時系列変化が確認できる
- [x] 推奨信頼度の構成要素が詳細表示される
- [x] 成功パターンのクラスタリング結果が可視化される

### 技術詳細
```typescript
// 実装対象コンポーネント
- QualityMetricsDashboard: メインダッシュボード
- CoverageChart: カバレッジ率表示
- NoveltyTrendChart: 新規性スコア推移
- ReliabilityBreakdown: 信頼度内訳
- SuccessPatternClusters: クラスタリング結果可視化

// 使用ライブラリ
import { ResponsiveContainer, PieChart, Pie, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const QualityMetricsDashboard = ({ scriptId }) => {
  const { data: qualityMetrics } = useQualityMetrics(scriptId);
  
  return (
    <div className="quality-dashboard grid grid-cols-2 gap-6">
      {/* カバレッジ率 */}
      <div className="coverage-section">
        <h3>成功パターンカバレッジ</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={qualityMetrics.coverage.breakdown}
              dataKey="percentage"
              nameKey="pattern"
              cx="50%"
              cy="50%"
              outerRadius={80}
              fill="#8884d8"
              label={({ name, percentage }) => `${name}: ${percentage}%`}
            />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* 新規性トレンド */}
      <div className="novelty-section">
        <h3>新規性スコア推移</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={qualityMetrics.novelty.trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="noveltyScore" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 推奨信頼度内訳 */}
      <div className="reliability-section">
        <h3>推奨信頼度内訳</h3>
        <ReliabilityBreakdown metrics={qualityMetrics.reliability} />
      </div>

      {/* 成功パターンクラスタ */}
      <div className="clusters-section">
        <h3>成功パターン分析</h3>
        <SuccessPatternClusters clusters={qualityMetrics.successPatterns} />
      </div>
    </div>
  );
};
```

---

## チケット F5-004: 成約率推移・効果分析（F006）
**優先度**: 中  
**見積**: 7時間  
**担当者**: データアナリスト

### 説明
スクリプト導入前後の成約率推移と効果分析機能を実装する。

### 要件
- 成約率の時系列変化グラフ
- スクリプト更新時点での効果測定
- カウンセラー別・期間別の分析
- A/Bテスト結果の可視化

### 受け入れ条件
- [x] 成約率の時系列グラフが表示される
- [x] スクリプト更新タイミングがグラフ上で確認できる
- [x] カウンセラー別の成約率比較ができる
- [x] 期間指定での効果測定ができる
- [x] 統計的有意性が表示される

### 技術詳細
```typescript
// 実装対象コンポーネント
- ConversionRateAnalysis: 成約率分析メイン
- TrendChart: 推移グラフ
- EffectAnalysis: 効果測定
- CounselorComparison: カウンセラー別比較

// データ分析処理
const EffectAnalysis = ({ beforePeriod, afterPeriod }) => {
  const analysisData = useEffectAnalysis(beforePeriod, afterPeriod);
  
  return (
    <div className="effect-analysis">
      <div className="summary-stats">
        <StatCard 
          title="導入前成約率"
          value={`${analysisData.before.conversionRate.toFixed(1)}%`}
          subtext={`${analysisData.before.period}`}
        />
        <StatCard 
          title="導入後成約率"
          value={`${analysisData.after.conversionRate.toFixed(1)}%`}
          subtext={`${analysisData.after.period}`}
        />
        <StatCard 
          title="改善率"
          value={`+${analysisData.improvement.rate.toFixed(1)}%`}
          subtext={`p-value: ${analysisData.improvement.pValue.toFixed(3)}`}
          positive={analysisData.improvement.rate > 0}
        />
      </div>
      
      <div className="detailed-analysis">
        <h4>詳細分析</h4>
        <ul>
          <li>サンプル数: {analysisData.sampleSize.before} → {analysisData.sampleSize.after}</li>
          <li>信頼区間: [{analysisData.confidenceInterval.lower.toFixed(1)}%, {analysisData.confidenceInterval.upper.toFixed(1)}%]</li>
          <li>統計的有意性: {analysisData.isSignificant ? '有意' : '非有意'}</li>
        </ul>
      </div>
    </div>
  );
};
```

---

## チケット F5-005: エクスポート・ダウンロード機能（F006）
**優先度**: 中  
**見積**: 4時間  
**担当者**: フロントエンドエンジニア

### 説明
スクリプトと分析結果のエクスポート・ダウンロード機能を実装する。

### 要件
- Markdown形式でのスクリプトダウンロード
- CSV形式での分析データダウンロード
- PDF形式での印刷用レポート生成
- カスタマイズ可能なエクスポート設定

### 受け入れ条件
- [x] Markdownファイルでスクリプトをダウンロードできる
- [x] CSV形式で成約率データをダウンロードできる
- [x] PDF形式で包括的なレポートを生成できる
- [x] エクスポート内容をカスタマイズできる
- [x] ダウンロード履歴が管理される

### 技術詳細
```typescript
// 実装対象機能
- ExportManager: エクスポート管理
- MarkdownExporter: Markdownファイル生成
- CSVExporter: CSVファイル生成
- PDFReportGenerator: PDFレポート生成

// エクスポート機能の実装
import jsPDF from 'jspdf';
import 'jspdf-autotable';

class ExportManager {
  exportAsMarkdown(script) {
    const markdownContent = this.generateMarkdownContent(script);
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `counseling_script_v${script.version}_${format(new Date(), 'yyyyMMdd')}.md`;
    link.click();
    
    URL.revokeObjectURL(url);
  }
  
  exportAsCSV(analysisData) {
    const csvContent = this.generateCSVContent(analysisData);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversion_analysis_${format(new Date(), 'yyyyMMdd')}.csv`;
    link.click();
    
    URL.revokeObjectURL(url);
  }
  
  generatePDFReport(script, qualityMetrics, analysisData) {
    const pdf = new jsPDF();
    
    // タイトル
    pdf.setFontSize(18);
    pdf.text('カウンセリングスクリプト レポート', 20, 20);
    
    // スクリプト情報
    pdf.setFontSize(12);
    pdf.text(`バージョン: ${script.version}`, 20, 40);
    pdf.text(`生成日時: ${format(new Date(script.generated_at), 'yyyy/MM/dd HH:mm')}`, 20, 50);
    
    // 品質メトリクス
    pdf.autoTable({
      head: [['メトリクス', 'スコア', '詳細']],
      body: [
        ['カバレッジ率', `${qualityMetrics.coverage.rate}%`, qualityMetrics.coverage.details],
        ['新規性スコア', qualityMetrics.novelty.score, qualityMetrics.novelty.details],
        ['推奨信頼度', qualityMetrics.reliability.score, qualityMetrics.reliability.details]
      ],
      startY: 60
    });
    
    return pdf.save(`script_report_v${script.version}.pdf`);
  }
}
```

---

## チケット F5-006: 通知・アラート機能（F006）
**優先度**: 中  
**見積**: 5時間  
**担当者**: フルスタックエンジニア

### 説明
スクリプト更新、品質低下、異常値検出時の通知機能を実装する。

### 要件
- スクリプト更新完了通知
- 品質スコア低下アラート
- 成約率異常値検出通知
- 通知設定のカスタマイズ

### 受け入れ条件
- [x] スクリプト生成完了時に通知される
- [x] 品質スコアが閾値を下回った時にアラートされる
- [x] 成約率の異常値が検出された時に通知される
- [x] ユーザーが通知設定をカスタマイズできる
- [x] 通知履歴が確認できる

### 技術詳細
```typescript
// 実装対象機能
- NotificationService: 通知管理サービス
- AlertSystem: アラート管理
- NotificationSettings: 通知設定管理
- NotificationHistory: 通知履歴

// 通知システムの実装
class NotificationService {
  async sendScriptUpdateNotification(script) {
    const notification = {
      type: 'script_update',
      title: 'スクリプトが更新されました',
      message: `バージョン${script.version}のスクリプトが生成されました。`,
      data: {
        scriptId: script.id,
        version: script.version,
        qualityScore: script.quality_metrics.overall_quality
      }
    };
    
    // ブラウザ通知
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/icons/script-update.png'
      });
    }
    
    // インアプリ通知
    this.addInAppNotification(notification);
    
    // メール通知（設定に応じて）
    if (this.shouldSendEmail('script_update')) {
      await this.sendEmailNotification(notification);
    }
  }
  
  checkQualityThresholds(qualityMetrics) {
    const thresholds = this.getQualityThresholds();
    
    if (qualityMetrics.coverage.rate < thresholds.coverage.min) {
      this.sendAlert({
        type: 'quality_low',
        title: 'スクリプト品質低下アラート',
        message: `カバレッジ率が${qualityMetrics.coverage.rate}%に低下しました。`,
        severity: 'warning'
      });
    }
    
    if (qualityMetrics.reliability.score < thresholds.reliability.min) {
      this.sendAlert({
        type: 'reliability_low',
        title: '信頼度低下アラート',
        message: `推奨信頼度が${qualityMetrics.reliability.score}に低下しました。`,
        severity: 'error'
      });
    }
  }
}

// バックエンド通知API
POST /api/v1/notifications/subscribe
GET /api/v1/notifications/history
PUT /api/v1/notifications/settings
POST /api/v1/notifications/test
```


---

## フェーズ5完了条件
- [x] 全チケットが完了している
- [x] スクリプトの見やすい表示画面が動作する
- [x] 履歴管理・バージョン比較機能が正常動作する
- [x] 品質メトリクスの可視化ダッシュボードが機能する
- [x] 成約率推移・効果分析が表示される
- [x] Markdown/CSV/PDF形式でのエクスポートが可能
- [x] 通知・アラート機能が正常動作する
- [x] 全体的なユーザビリティが確保されている