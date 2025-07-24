import { Metadata } from 'next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Zap, Settings, Play, Brain, TrendingUp, Clock } from 'lucide-react';

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

      {/* 生成設定 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>生成設定</span>
            </CardTitle>
            <CardDescription>
              スクリプト生成のパラメータ設定
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                分析期間
              </label>
              <select className="w-full p-2 border border-gray-300 rounded-md">
                <option>過去3ヶ月</option>
                <option>過去6ヶ月</option>
                <option>過去1年</option>
                <option>全期間</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                成約率フィルター
              </label>
              <select className="w-full p-2 border border-gray-300 rounded-md">
                <option>60%以上</option>
                <option>70%以上</option>
                <option>80%以上</option>
                <option>90%以上</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                重点改善エリア
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" defaultChecked />
                  <span className="text-sm">オープニング</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" defaultChecked />
                  <span className="text-sm">ニーズ確認</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" defaultChecked />
                  <span className="text-sm">ソリューション提案</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" defaultChecked />
                  <span className="text-sm">クロージング</span>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>期待される効果</span>
            </CardTitle>
            <CardDescription>
              生成されるスクリプトの期待効果
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm font-medium">成約率向上</span>
                <span className="text-sm text-green-600 font-bold">+15-25%</span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-sm font-medium">品質スコア</span>
                <span className="text-sm text-blue-600 font-bold">85%以上</span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="text-sm font-medium">カバレッジ率</span>
                <span className="text-sm text-purple-600 font-bold">90%以上</span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                <span className="text-sm font-medium">生成時間</span>
                <span className="text-sm text-orange-600 font-bold">3-5分</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

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