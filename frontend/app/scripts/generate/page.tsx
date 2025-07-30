'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { LoadingSpinner } from '@/app/components/ui/LoadingSpinner';
import { Zap, Play, Brain, Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { 
  startScriptGeneration, 
  getScriptGenerationStatus,
  ScriptGenerationStatus 
} from '@/repository';
import { useRouter } from 'next/navigation';

export default function ScriptGeneratePage() {
  const router = useRouter();
  const [generating, setGenerating] = useState(false);
  const [currentJob, setCurrentJob] = useState<ScriptGenerationStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const startPolling = (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await getScriptGenerationStatus(jobId);
        setCurrentJob(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setPollingInterval(null);
          setGenerating(false);
          
          if (status.status === 'completed' && status.script) {
            // Navigate to the generated script
            router.push(`/scripts/${status.script.id}`);
          } else if (status.status === 'failed') {
            setError(status.error_message || 'スクリプト生成に失敗しました');
          }
        }
      } catch (err) {
        console.error('Status polling error:', err);
        clearInterval(interval);
        setPollingInterval(null);
        setGenerating(false);
        setError('生成状況の確認に失敗しました');
      }
    }, 2000); // Poll every 2 seconds
    
    setPollingInterval(interval);
  };

  const handleGenerateScript = async () => {
    setGenerating(true);
    setError(null);
    setCurrentJob(null);

    try {
      // For demo purposes, we'll use a dummy cluster result ID
      // In a real implementation, this would come from the clustering process
      const request = {
        cluster_result_id: '00000000-0000-0000-0000-000000000000', // Dummy ID
        failure_conversations: [], // This would be populated from actual failure data
        title: `改善スクリプト ${new Date().toLocaleDateString()}`,
        description: 'AI生成による改善スクリプト'
      };

      const response = await startScriptGeneration(request);
      
      setCurrentJob({
        job_id: response.job_id,
        status: 'pending',
        progress_percentage: 0,
        created_at: new Date().toISOString()
      });
      
      startPolling(response.job_id);
    } catch (err) {
      setGenerating(false);
      setError(err instanceof Error ? err.message : 'スクリプト生成の開始に失敗しました');
    }
  };

  const handleRetry = () => {
    setError(null);
    setCurrentJob(null);
    handleGenerateScript();
  };
  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          スクリプト生成
        </h1>
        <p className="text-gray-600">
          AIによる高品質カウンセリングスクリプトの自動生成
        </p>
      </div>

      {/* 生成プロセス概要 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-blue-600" />
            <span>生成プロセス</span>
          </CardTitle>
          <CardDescription>
            ベクトル検索・クラスタリング・GPT-4oによる高度な分析
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                1
              </div>
              <h4 className="font-medium text-sm">データ分析</h4>
              <p className="text-xs text-gray-600 mt-1">成功・失敗事例の抽出</p>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                2
              </div>
              <h4 className="font-medium text-sm">ベクトル検索</h4>
              <p className="text-xs text-gray-600 mt-1">類似成功例の発見</p>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                3
              </div>
              <h4 className="font-medium text-sm">クラスタリング</h4>
              <p className="text-xs text-gray-600 mt-1">成功パターンの分類</p>
            </div>
            
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                4
              </div>
              <h4 className="font-medium text-sm">スクリプト生成</h4>
              <p className="text-xs text-gray-600 mt-1">GPT-4oによる生成</p>
            </div>
          </div>
        </CardContent>
      </Card>


      {/* エラー表示 */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-700">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* 進行状況表示 */}
      {currentJob && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {currentJob.status === 'completed' ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : currentJob.status === 'failed' ? (
                <AlertCircle className="h-5 w-5 text-red-500" />
              ) : (
                <LoadingSpinner size="sm" />
              )}
              <span>
                {currentJob.status === 'pending' && '生成準備中'}
                {currentJob.status === 'running' && '生成中'}
                {currentJob.status === 'completed' && '生成完了'}
                {currentJob.status === 'failed' && '生成失敗'}
              </span>
            </CardTitle>
            <CardDescription>
              ジョブID: {currentJob.job_id}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 進行バー */}
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${currentJob.progress_percentage}%` }}
                />
              </div>
              <p className="text-sm text-gray-600">
                進行状況: {currentJob.progress_percentage}%
              </p>
              
              {currentJob.status === 'completed' && currentJob.script && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <p className="text-green-800 font-medium">
                    スクリプトが正常に生成されました！
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    自動的にスクリプト詳細ページに移動します...
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 実行部分 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-blue-600" />
            <span>スクリプト生成実行</span>
          </CardTitle>
          <CardDescription>
            AIスクリプト生成を開始します
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!generating && !currentJob && (
            <Alert className="mb-4">
              <Clock className="h-4 w-4" />
              <AlertDescription>
                スクリプト生成には3-5分程度かかります。ページを閉じずにお待ちください。
              </AlertDescription>
            </Alert>
          )}
          
          <div className="flex items-center justify-center space-x-4">
            {error && currentJob?.status === 'failed' ? (
              <Button size="lg" className="px-8" onClick={handleRetry}>
                <RefreshCw className="h-5 w-5 mr-2" />
                再試行
              </Button>
            ) : (
              <Button 
                size="lg" 
                className="px-8" 
                onClick={handleGenerateScript}
                disabled={generating || currentJob?.status === 'running'}
              >
                {generating || currentJob?.status === 'running' ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <Play className="h-5 w-5 mr-2" />
                )}
                {generating || currentJob?.status === 'running' ? '生成中...' : 'スクリプト生成開始'}
              </Button>
            )}
          </div>
          
          <div className="mt-6 text-center text-sm text-gray-600">
            <p>生成されたスクリプトは自動的に保存され、</p>
            <p>履歴からいつでも確認・比較できます。</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}