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
- [ ] 最新スクリプトが見やすいレイアウトで表示される
- [ ] フェーズごとにタブ分けまたはセクション分けされる
- [ ] Markdownが適切にレンダリングされる
- [ ] 印刷用レイアウトが提供される
- [ ] URLで特定スクリプトを直接共有できる

### 技術詳細
```typescript
// 実装対象コンポーネント
- ScriptViewer: メインスクリプト表示
- ScriptPhaseNavigator: フェーズ間ナビゲーション
- MarkdownRenderer: Markdownレンダリング
- PrintableScript: 印刷用レイアウト

// コンポーネント構成
const ScriptViewer = () => {
  const [activePhase, setActivePhase] = useState('opening');
  const { data: script } = useScript();

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
};

// 使用技術
- React + TypeScript
- react-markdown (Markdownレンダリング)
- Tailwind CSS (スタイリング)
- React Query (データ取得)
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
- [ ] スクリプト履歴が時系列で表示される
- [ ] 2つのバージョンを選択して差分表示できる
- [ ] 過去バージョンをアクティブに戻せる
- [ ] バージョン切り替えがリアルタイムで反映される
- [ ] 削除防止機能が実装される

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
- [ ] 品質メトリクスが直感的なグラフで表示される
- [ ] カバレッジ率が円グラフまたはプログレスバーで表示される
- [ ] 新規性スコアの時系列変化が確認できる
- [ ] 推奨信頼度の構成要素が詳細表示される
- [ ] 成功パターンのクラスタリング結果が可視化される

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
- [ ] 成約率の時系列グラフが表示される
- [ ] スクリプト更新タイミングがグラフ上で確認できる
- [ ] カウンセラー別の成約率比較ができる
- [ ] 期間指定での効果測定ができる
- [ ] 統計的有意性が表示される

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
- [ ] Markdownファイルでスクリプトをダウンロードできる
- [ ] CSV形式で成約率データをダウンロードできる
- [ ] PDF形式で包括的なレポートを生成できる
- [ ] エクスポート内容をカスタマイズできる
- [ ] ダウンロード履歴が管理される

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
- [ ] スクリプト生成完了時に通知される
- [ ] 品質スコアが閾値を下回った時にアラートされる
- [ ] 成約率の異常値が検出された時に通知される
- [ ] ユーザーが通知設定をカスタマイズできる
- [ ] 通知履歴が確認できる

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

## チケット F5-007: ユーザー管理・権限制御
**優先度**: 低  
**見積**: 6時間  
**担当者**: バックエンドエンジニア

### 説明
店長・教育担当者・カウンセラー別の権限管理機能を実装する。

### 要件
- ロールベースアクセス制御
- 店長: 全機能アクセス
- 教育担当者: スクリプト管理・履歴確認
- カウンセラー: スクリプト閲覧のみ

### 受け入れ条件
- [ ] ロール別に適切な権限制御がされる
- [ ] 権限のないユーザーは機能にアクセスできない
- [ ] ロール変更が適切に反映される
- [ ] セキュリティが適切に実装される
- [ ] 監査ログが記録される

### 技術詳細
```python
# 権限管理実装
from enum import Enum
from fastapi import Depends, HTTPException

class UserRole(Enum):
    MANAGER = "manager"
    TRAINER = "trainer"  
    COUNSELOR = "counselor"

class PermissionLevel(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

# 権限マトリクス
ROLE_PERMISSIONS = {
    UserRole.MANAGER: [
        "scripts.read", "scripts.write", "scripts.admin",
        "analytics.read", "analytics.write",
        "users.read", "users.write"
    ],
    UserRole.TRAINER: [
        "scripts.read", "scripts.write",
        "analytics.read"
    ],
    UserRole.COUNSELOR: [
        "scripts.read"
    ]
}

# 権限チェックデコレータ
def require_permission(permission: str):
    def decorator(func):
        def wrapper(current_user: User = Depends(get_current_user)):
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission}"
                )
            return func(current_user)
        return wrapper
    return decorator

# API実装例
@app.post("/api/v1/scripts/generate")
@require_permission("scripts.write")
def generate_script(current_user: User = Depends(get_current_user)):
    # スクリプト生成処理
    pass
```

---

## フェーズ5完了条件
- [ ] 全チケットが完了している
- [ ] スクリプトの見やすい表示画面が動作する
- [ ] 履歴管理・バージョン比較機能が正常動作する
- [ ] 品質メトリクスの可視化ダッシュボードが機能する
- [ ] 成約率推移・効果分析が表示される
- [ ] Markdown/CSV/PDF形式でのエクスポートが可能
- [ ] 通知・アラート機能が正常動作する
- [ ] ロールベースの権限制御が機能する
- [ ] 全体的なユーザビリティが確保されている