'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { 
  ArrowLeft, 
  Calendar,
  CheckCircle,
  Clock,
  AlertCircle,
  Play,
  FileText
} from 'lucide-react';
import { getScript, activateScript, type ImprovementScript } from '@/repository/script';
import { formatDistanceToNow } from 'date-fns';
import { ja } from 'date-fns/locale';
import ReactMarkdown from 'react-markdown';

interface PageProps {
  params: { id: string };
}

export default function ScriptDetailPage({ params }: PageProps) {
  const [script, setScript] = useState<ImprovementScript | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activating, setActivating] = useState(false);

  const fetchScript = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getScript(params.id);
      console.log(data);
      setScript(data);
    } catch (err) {
      console.error('Failed to fetch script:', err);
      setError('スクリプトの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async () => {
    if (!script) return;
    
    try {
      setActivating(true);
      await activateScript(script.id);
      await fetchScript(); // Refresh script data
    } catch (err) {
      console.error('Failed to activate script:', err);
      setError('スクリプトの有効化に失敗しました');
    } finally {
      setActivating(false);
    }
  };

  useEffect(() => {
    fetchScript();
  }, [params.id]);

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
    if (isActive) return <CheckCircle className="h-5 w-5 text-green-600" />;
    
    switch (status) {
      case 'generating':
        return <Clock className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'review':
        return <AlertCircle className="h-5 w-5 text-orange-600" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-gray-600" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <FileText className="h-5 w-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="bg-white rounded-lg border p-6">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
            <div className="bg-white rounded-lg border p-6">
              <div className="h-40 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-6">
          <div className="max-w-2xl mx-auto">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <div className="mt-4">
              <Link href="/scripts">
                <Button variant="outline">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  スクリプト一覧に戻る
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!script) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-6">
          <div className="max-w-2xl mx-auto">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>指定されたスクリプトが見つかりません</AlertDescription>
            </Alert>
            <div className="mt-4">
              <Link href="/scripts">
                <Button variant="outline">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  スクリプト一覧に戻る
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <Link href="/scripts">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                スクリプト一覧に戻る
              </Button>
            </Link>
            
            {script.status === 'completed' && !script.is_active && (
              <Button 
                onClick={handleActivate}
                disabled={activating}
              >
                {activating ? (
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Play className="h-4 w-4 mr-2" />
                )}
                有効化
              </Button>
            )}
          </div>

          {/* Script Header */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getStatusIcon(script.status, script.is_active)}
                  <div>
                    <CardTitle className="text-xl">{script.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {script.description}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusBadge(script.status, script.is_active)}
                  <Badge variant="outline">v{script.version}</Badge>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">作成日</span>
                  <div className="font-medium">
                    {formatDistanceToNow(new Date(script.created_at), { 
                      addSuffix: true, 
                      locale: ja 
                    })}
                  </div>
                </div>
                
                <div>
                  <span className="text-gray-500">最終更新</span>
                  <div className="font-medium">
                    {formatDistanceToNow(new Date(script.updated_at), { 
                      addSuffix: true, 
                      locale: ja 
                    })}
                  </div>
                </div>
                
                {script.quality_metrics?.overall_score && (
                  <div>
                    <span className="text-gray-500">品質スコア</span>
                    <div className="font-medium text-purple-600">
                      {Math.round(script.quality_metrics.overall_score * 100)}%
                    </div>
                  </div>
                )}
                
                {script.activated_at && (
                  <div>
                    <span className="text-gray-500">有効化日</span>
                    <div className="font-medium">
                      {formatDistanceToNow(new Date(script.activated_at), { 
                        addSuffix: true, 
                        locale: ja 
                      })}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Script Content */}
          {script.content?.raw_content && (
            <Card>
              <CardHeader>
                <CardTitle>生成されたスクリプト</CardTitle>
                <CardDescription>
                  AI分析に基づいて生成されたカウンセリングスクリプトです
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      h2: ({ children }) => <h2 className="text-xl font-bold text-gray-900 mt-8 mb-4 border-b pb-2">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-3">{children}</h3>,
                      h4: ({ children }) => <h4 className="text-base font-medium text-gray-900 mt-4 mb-2">{children}</h4>,
                      p: ({ children }) => <p className="mb-4 leading-relaxed text-gray-700">{children}</p>,
                      ul: ({ children }) => <ul className="mb-4 pl-6 space-y-1 list-disc">{children}</ul>,
                      ol: ({ children }) => <ol className="mb-4 pl-6 space-y-1 list-decimal">{children}</ol>,
                      li: ({ children }) => <li className="text-gray-700">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                      blockquote: ({ children }) => <blockquote className="border-l-4 border-blue-200 pl-4 py-2 my-4 bg-blue-50 italic text-gray-700">{children}</blockquote>,
                    }}
                  >
                    {script.content.raw_content}
                  </ReactMarkdown>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quality Metrics */}
          {script.quality_metrics && (
            <Card>
              <CardHeader>
                <CardTitle>品質メトリクス</CardTitle>
                <CardDescription>
                  生成されたスクリプトの品質分析結果
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {Math.round(script.quality_metrics.overall_quality * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">総合品質</div>
                  </div>
                  
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {Math.round(script.quality_metrics.structure_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">構造スコア</div>
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {Math.round(script.quality_metrics.completeness_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">完全性</div>
                  </div>
                  
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {Math.round(script.quality_metrics.actionability_score * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">実用性</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Generation Metadata */}
          {script.generation_metadata && (
            <Card>
              <CardHeader>
                <CardTitle>生成情報</CardTitle>
                <CardDescription>
                  このスクリプトの生成に関する詳細情報
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  {script.generation_metadata.model && (
                    <div>
                      <span className="text-gray-500">使用モデル</span>
                      <div className="font-medium">{script.generation_metadata.model}</div>
                    </div>
                  )}
                  
                  {script.generation_metadata.processing_time && (
                    <div>
                      <span className="text-gray-500">処理時間</span>
                      <div className="font-medium">
                        {Math.round(script.generation_metadata.processing_time)}秒
                      </div>
                    </div>
                  )}
                  
                  {script.generation_metadata.cost_estimate && (
                    <div>
                      <span className="text-gray-500">推定コスト</span>
                      <div className="font-medium">
                        ${script.generation_metadata.cost_estimate.toFixed(4)}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}