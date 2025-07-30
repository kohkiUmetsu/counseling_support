'use client';

import { useState } from 'react';
import { useScript } from '@/hooks/useScript';
import { ScriptHeader } from '@/app/components/scripts/ScriptHeader';
import { ScriptPhaseNavigator } from '@/app/components/scripts/ScriptPhaseNavigator';
import { ScriptContent } from '@/app/components/scripts/ScriptContent';
import { ScriptActions } from '@/app/components/scripts/ScriptActions';
import { ScriptViewerSkeleton } from './ScriptViewerSkeleton';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { AlertCircle } from 'lucide-react';

interface ScriptViewerProps {
  scriptId: string;
  initialPhase: string;
}

const SCRIPT_PHASES = [
  { id: 'opening', label: 'オープニング', description: '最初の挨拶・アイスブレイク' },
  { id: 'needs_assessment', label: 'ニーズ確認', description: '顧客の要望・課題の把握' },
  { id: 'solution_proposal', label: 'ソリューション提案', description: '最適なプランの提案' },
  { id: 'closing', label: 'クロージング', description: '契約締結・次のステップ' }
] as const;

export function ScriptViewer({ scriptId, initialPhase }: ScriptViewerProps) {
  const [activePhase, setActivePhase] = useState(initialPhase);
  const { data: script, isLoading, error } = useScript(scriptId);

  if (isLoading) {
    return <ScriptViewerSkeleton />;
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            スクリプトの読み込みに失敗しました。{error.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!script) {
    return (
      <div className="max-w-4xl mx-auto">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            指定されたスクリプトが見つかりません。
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const handlePhaseChange = (phase: string) => {
    setActivePhase(phase);
    // URL更新（履歴に残さず）
    const url = new URL(window.location.href);
    url.searchParams.set('phase', phase);
    window.history.replaceState(null, '', url.toString());
  };

  const handlePrint = () => {
    // 印刷用スタイルを適用してから印刷
    document.body.classList.add('print-mode');
    window.print();
    document.body.classList.remove('print-mode');
  };

  const handleShare = async () => {
    const shareUrl = window.location.href;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${script.title} - フェーズ: ${SCRIPT_PHASES.find(p => p.id === activePhase)?.label}`,
          text: 'カウンセリングスクリプトを共有します',
          url: shareUrl,
        });
      } catch {
        console.log('Share cancelled');
      }
    } else {
      // フォールバック: クリップボードにコピー
      try {
        await navigator.clipboard.writeText(shareUrl);
        // TODO: トーストメッセージ表示
        alert('URLをクリップボードにコピーしました');
      } catch (error) {
        console.error('Failed to copy URL:', error);
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* ヘッダー */}
      <ScriptHeader script={script} />
      
      {/* フェーズナビゲーター */}
      <ScriptPhaseNavigator 
        phases={SCRIPT_PHASES}
        activePhase={activePhase}
        onPhaseChange={handlePhaseChange}
      />
      
      {/* メインコンテンツ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* スクリプトコンテンツ */}
        <div className="lg:col-span-2">
          <ScriptContent 
            phase={activePhase}
            content={script.content?.[activePhase as keyof typeof script.content]}
            successFactors={script.success_factors}
            improvementPoints={script.improvement_points}
          />
        </div>
        
        {/* サイドバー：品質メトリクスとアクション */}
        <div className="space-y-4">
          {/* 品質メトリクス */}
          {script.quality_metrics && (
            <div className="bg-white rounded-lg border p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                品質メトリクス
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">総合品質</span>
                  <span className="text-sm font-medium">
                    {(script.quality_metrics.overall_quality * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">カバレッジ率</span>
                  <span className="text-sm font-medium">
                    {(script.quality_metrics.coverage?.coverage_percentage || 0).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">新規性スコア</span>
                  <span className="text-sm font-medium">
                    {(script.quality_metrics.novelty?.novelty_score || 0).toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">信頼度</span>
                  <span className="text-sm font-medium">
                    {(script.quality_metrics.reliability?.confidence_score || 0).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          {/* アクション */}
          <ScriptActions 
            onPrint={handlePrint}
            onShare={handleShare}
            script={script}
          />
        </div>
      </div>
    </div>
  );
}