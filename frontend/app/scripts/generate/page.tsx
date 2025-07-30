import { Metadata } from 'next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Zap, Play, Brain, Clock } from 'lucide-react';

export const metadata: Metadata = {
  title: 'スクリプト生成 | Counseling Support',
  description: 'AIによるカウンセリングスクリプト生成',
};

export default function ScriptGeneratePage() {
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


      {/* 実行部分 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-blue-600" />
            <span>スクリプト生成実行</span>
          </CardTitle>
          <CardDescription>
            設定に基づいてAIスクリプト生成を開始します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert className="mb-4">
            <Clock className="h-4 w-4" />
            <AlertDescription>
              スクリプト生成には3-5分程度かかります。ページを閉じずにお待ちください。
            </AlertDescription>
          </Alert>
          
          <div className="flex items-center justify-center space-x-4">
            <Button size="lg" className="px-8">
              <Play className="h-5 w-5 mr-2" />
              スクリプト生成開始
            </Button>
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