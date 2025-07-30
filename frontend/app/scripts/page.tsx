'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { History, Zap } from 'lucide-react';
import ScriptList from './components/ScriptList';

export default function ScriptsPage() {
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    draft: 0,
    averageQuality: 0
  });

  const handleStatsUpdate = (newStats: typeof stats) => {
    setStats(newStats);
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            スクリプト一覧
          </h1>
          <p className="text-gray-600">
            生成されたカウンセリングスクリプトの管理
          </p>
        </div>
        <div className="flex space-x-3">
          <Link href="/scripts/generate">
            <Button>
              <Zap className="h-4 w-4 mr-2" />
              新規生成
            </Button>
          </Link>
          <Link href="/scripts/history">
            <Button variant="outline">
              <History className="h-4 w-4 mr-2" />
              履歴管理
            </Button>
          </Link>
        </div>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">総スクリプト数</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">アクティブ</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">ドラフト</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.draft}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">平均品質スコア</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {stats.averageQuality > 0 ? `${stats.averageQuality}%` : '-'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* メインコンテンツ */}
      <Card>
        <CardHeader>
          <CardTitle>最近のスクリプト</CardTitle>
          <CardDescription>
            最新の生成スクリプトと管理操作
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScriptList onStatsUpdate={handleStatsUpdate} />
        </CardContent>
      </Card>
    </div>
  );
}