'use client';

import { useState, useEffect } from 'react';
import { Button } from './components/ui/Button';
import { LoadingSpinner } from './components/ui/LoadingSpinner';
import { counselingApi } from './lib/api';

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<{
    status: string;
    message: string;
    timestamp: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await counselingApi.healthCheck();
        setHealthStatus(response.data as { status: string; message: string; timestamp: string });
      } catch (error) {
        console.error('Health check failed:', error);
        setHealthStatus({
          status: 'error',
          message: 'バックエンドAPIに接続できません',
          timestamp: new Date().toISOString(),
        });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          カウンセリング支援ツール
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          美容医療クリニック向けカウンセリングスクリプト改善AIツール
        </p>
      </div>

      {/* Health Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          システム状態
        </h2>
        {loading ? (
          <div className="flex items-center space-x-2">
            <LoadingSpinner size="sm" />
            <span className="text-gray-600">接続確認中...</span>
          </div>
        ) : healthStatus ? (
          <div
            className={`p-4 rounded-md ${
              healthStatus.status === 'healthy'
                ? 'bg-green-50 text-green-800'
                : 'bg-red-50 text-red-800'
            }`}
          >
            <p className="font-medium">
              {healthStatus.status === 'healthy' ? '✅ 正常' : '❌ エラー'}
            </p>
            <p className="text-sm mt-1">{healthStatus.message}</p>
          </div>
        ) : null}
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">
            セッション管理
          </h3>
          <p className="mt-2 text-gray-600">
            カウンセリングセッションの作成・管理
          </p>
          <Button className="mt-4" size="sm">
            セッション一覧
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">
            音声文字起こし
          </h3>
          <p className="mt-2 text-gray-600">
            音声ファイルからテキストへの変換
          </p>
          <Button className="mt-4" size="sm" variant="secondary">
            開発予定
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">
            スクリプト改善
          </h3>
          <p className="mt-2 text-gray-600">
            AIによるカウンセリングスクリプトの改善提案
          </p>
          <Button className="mt-4" size="sm" variant="secondary">
            開発予定
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">
            成功事例検索
          </h3>
          <p className="mt-2 text-gray-600">
            ベクトル検索による成功事例の抽出
          </p>
          <Button className="mt-4" size="sm" variant="secondary">
            開発予定
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">
            分析ダッシュボード
          </h3>
          <p className="mt-2 text-gray-600">
            カウンセリング品質の分析と可視化
          </p>
          <Button className="mt-4" size="sm" variant="secondary">
            開発予定
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">
            設定管理
          </h3>
          <p className="mt-2 text-gray-600">
            システム設定とユーザー管理
          </p>
          <Button className="mt-4" size="sm" variant="secondary">
            開発予定
          </Button>
        </div>
      </div>
    </div>
  );
}