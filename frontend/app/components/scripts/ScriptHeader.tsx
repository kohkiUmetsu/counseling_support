'use client';

import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import { Badge } from '@/app/components/ui/badge';
import { Calendar, User, Zap, TrendingUp } from 'lucide-react';

interface Script {
  id: string;
  title: string;
  version: string;
  status: 'draft' | 'active' | 'archived';
  created_at: string;
  updated_at: string;
  quality_metrics?: {
    overall_quality: number;
    coverage?: {
      coverage_percentage: number;
    };
    novelty?: {
      novelty_score: number;
    };
    reliability?: {
      confidence_score: number;
    };
  };
  generation_metadata?: {
    generation_time: number;
    total_success_conversations: number;
    clusters_identified: number;
    representatives_selected: number;
  };
}

interface ScriptHeaderProps {
  script: Script;
}

export function ScriptHeader({ script }: ScriptHeaderProps) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-green-500">アクティブ</Badge>;
      case 'draft':
        return <Badge variant="secondary">ドラフト</Badge>;
      case 'archived':
        return <Badge variant="outline">アーカイブ</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatDateTime = (dateString: string) => {
    return format(new Date(dateString), 'yyyy年MM月dd日 HH:mm', { locale: ja });
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}分${remainingSeconds.toFixed(0)}秒`;
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-6">
        {/* タイトルとステータス */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {script.title || `スクリプト v${script.version}`}
            </h1>
            <div className="flex items-center space-x-3">
              {getStatusBadge(script.status)}
              <span className="text-sm text-gray-600">
                バージョン {script.version}
              </span>
            </div>
          </div>
          
          {script.quality_metrics && (
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">総合品質スコア</div>
              <div className="text-2xl font-bold text-blue-600">
                {(script.quality_metrics.overall_quality * 100).toFixed(1)}%
              </div>
            </div>
          )}
        </div>

        {/* メタデータ */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Calendar className="h-4 w-4" />
            <div>
              <div className="font-medium">作成日時</div>
              <div>{formatDateTime(script.created_at)}</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Calendar className="h-4 w-4" />
            <div>
              <div className="font-medium">更新日時</div>
              <div>{formatDateTime(script.updated_at)}</div>
            </div>
          </div>

          {script.generation_metadata && (
            <>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Zap className="h-4 w-4" />
                <div>
                  <div className="font-medium">生成時間</div>
                  <div>{formatDuration(script.generation_metadata.generation_time)}</div>
                </div>
              </div>

              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <TrendingUp className="h-4 w-4" />
                <div>
                  <div className="font-medium">分析データ</div>
                  <div>{script.generation_metadata.total_success_conversations}件の成功事例</div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* 生成統計サマリー */}
        {script.generation_metadata && (
          <div className="bg-gray-50 rounded-lg p-4 mt-4">
            <h3 className="text-sm font-medium text-gray-900 mb-2">生成統計</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-600">成功事例数:</span>
                <span className="ml-2 font-medium">
                  {script.generation_metadata.total_success_conversations}件
                </span>
              </div>
              <div>
                <span className="text-gray-600">クラスタ数:</span>
                <span className="ml-2 font-medium">
                  {script.generation_metadata.clusters_identified}個
                </span>
              </div>
              <div>
                <span className="text-gray-600">代表例数:</span>
                <span className="ml-2 font-medium">
                  {script.generation_metadata.representatives_selected}件
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}