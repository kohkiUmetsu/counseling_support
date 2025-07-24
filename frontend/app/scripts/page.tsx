import { Suspense } from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, FileText, History, Zap } from 'lucide-react';

export const metadata: Metadata = {
  title: 'スクリプト一覧 | Counseling Support',
  description: '生成されたカウンセリングスクリプトの一覧と管理',
};

// TODO: スクリプト一覧コンポーネントを実装
function ScriptListSkeleton() {
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

export default function ScriptsPage() {
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
            <div className="text-2xl font-bold text-blue-600">12</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">アクティブ</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">1</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">ドラフト</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">3</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">平均品質スコア</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">85.2%</div>
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
          <Suspense fallback={<ScriptListSkeleton />}>
            {/* TODO: 実際のスクリプト一覧データを表示 */}
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                スクリプトデータを読み込み中
              </h3>
              <p className="text-gray-600 mb-4">
                APIからスクリプトデータを取得しています
              </p>
              <Link href="/scripts/generate">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  最初のスクリプトを生成
                </Button>
              </Link>
            </div>
          </Suspense>
        </CardContent>
      </Card>
    </div>
  );
}