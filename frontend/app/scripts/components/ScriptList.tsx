'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';
import { 
  FileText, 
  Play, 
  Pause, 
  Eye, 
  Clock,
  CheckCircle,
  AlertCircle,
  Plus 
} from 'lucide-react';
import { getScripts, activateScript, type ImprovementScript, type ScriptsListResponse } from '@/repository/script';
import { formatDistanceToNow } from 'date-fns';
import { ja } from 'date-fns/locale';

interface ScriptListProps {
  onStatsUpdate?: (stats: {
    total: number;
    active: number;
    draft: number;
    averageQuality: number;
  }) => void;
}

export default function ScriptList({ onStatsUpdate }: ScriptListProps) {
  const [scripts, setScripts] = useState<ImprovementScript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activatingId, setActivatingId] = useState<string | null>(null);

  const fetchScripts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response: ScriptsListResponse = await getScripts({ limit: 20, offset: 0 });
      setScripts(response.scripts);
      
      // Calculate stats
      const stats = {
        total: response.total,
        active: response.scripts.filter(s => s.is_active).length,
        draft: response.scripts.filter(s => s.status === 'generating' || s.status === 'review').length,
        averageQuality: calculateAverageQuality(response.scripts)
      };
      onStatsUpdate?.(stats);
      
    } catch (err) {
      console.error('Failed to fetch scripts:', err);
      setError('スクリプトの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const calculateAverageQuality = (scripts: ImprovementScript[]): number => {
    const scriptsWithQuality = scripts.filter(s => s.quality_metrics?.overall_score);
    if (scriptsWithQuality.length === 0) return 0;
    
    const total = scriptsWithQuality.reduce((sum, s) => sum + (s.quality_metrics.overall_score || 0), 0);
    return Math.round((total / scriptsWithQuality.length) * 100) / 100;
  };

  const handleActivate = async (scriptId: string) => {
    try {
      setActivatingId(scriptId);
      await activateScript(scriptId);
      await fetchScripts(); // Refresh list
    } catch (err) {
      console.error('Failed to activate script:', err);
      setError('スクリプトの有効化に失敗しました');
    } finally {
      setActivatingId(null);
    }
  };

  useEffect(() => {
    fetchScripts();
  }, []);

  const getStatusBadge = (status: string, isActive: boolean) => {
    if (isActive) {
      return <Badge className="bg-green-100 text-green-800">アクティブ</Badge>;
    }
    
    switch (status) {
      case 'generating':
        return <Badge className="bg-blue-100 text-blue-800">生成中</Badge>;
      case 'review':
        return <Badge className="bg-orange-100 text-orange-800">レビュー待ち</Badge>;
      case 'completed':
        return <Badge className="bg-gray-100 text-gray-800">完了</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">失敗</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">{status}</Badge>;
    }
  };

  const getStatusIcon = (status: string, isActive: boolean) => {
    if (isActive) return <CheckCircle className="h-4 w-4 text-green-600" />;
    
    switch (status) {
      case 'generating':
        return <Clock className="h-4 w-4 text-blue-600 animate-spin" />;
      case 'review':
        return <AlertCircle className="h-4 w-4 text-orange-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-gray-600" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-white rounded-lg border p-6">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
              <div className="flex space-x-2">
                <div className="h-8 bg-gray-200 rounded w-16"></div>
                <div className="h-8 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">エラーが発生しました</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <Button onClick={fetchScripts}>再試行</Button>
      </div>
    );
  }

  if (scripts.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          スクリプトがありません
        </h3>
        <p className="text-gray-600 mb-4">
          最初のスクリプトを生成してみましょう
        </p>
        <Link href="/scripts/generate">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            最初のスクリプトを生成
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {scripts.map((script) => (
        <Card key={script.id} className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                {getStatusIcon(script.status, script.is_active)}
                <div className="flex-1">
                  <CardTitle className="text-lg">{script.title}</CardTitle>
                  <CardDescription className="mt-1">
                    {script.description || '説明なし'}
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusBadge(script.status, script.is_active)}
                <Badge variant="outline">v{script.version}</Badge>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="pt-0">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm text-gray-600">
              <div>
                <span className="font-medium">作成日:</span>
                <br />
                {formatDistanceToNow(new Date(script.created_at), { 
                  addSuffix: true, 
                  locale: ja 
                })}
              </div>
              
              {script.quality_metrics?.overall_score && (
                <div>
                  <span className="font-medium">品質スコア:</span>
                  <br />
                  <span className="text-purple-600 font-semibold">
                    {Math.round(script.quality_metrics.overall_score * 100)}%
                  </span>
                </div>
              )}
              
              {script.activated_at && (
                <div>
                  <span className="font-medium">有効化日:</span>
                  <br />
                  {formatDistanceToNow(new Date(script.activated_at), { 
                    addSuffix: true, 
                    locale: ja 
                  })}
                </div>
              )}
              
              <div>
                <span className="font-medium">ステータス:</span>
                <br />
                {script.status === 'generating' ? '生成中' :
                 script.status === 'review' ? 'レビュー待ち' :
                 script.status === 'completed' ? '完了' :
                 script.status === 'failed' ? '失敗' : script.status}
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                <Link href={`/scripts/${script.id}`}>
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    詳細
                  </Button>
                </Link>
                
                {script.status === 'completed' && !script.is_active && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleActivate(script.id)}
                    disabled={activatingId === script.id}
                  >
                    {activatingId === script.id ? (
                      <Clock className="h-4 w-4 mr-1 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4 mr-1" />
                    )}
                    有効化
                  </Button>
                )}
                
                {script.is_active && (
                  <Button variant="outline" size="sm" disabled>
                    <Pause className="h-4 w-4 mr-1" />
                    非有効化
                  </Button>
                )}
              </div>
              
              <div className="text-xs text-gray-500">
                ID: {script.id.slice(0, 8)}...
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}