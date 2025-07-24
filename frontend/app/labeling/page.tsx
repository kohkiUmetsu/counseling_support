import { Metadata } from 'next';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Target, Clock, CheckCircle, AlertCircle, FileText, Calendar } from 'lucide-react';

export const metadata: Metadata = {
  title: 'ラベリング | Counseling Support',
  description: '会話データの成功・失敗ラベリング',
};

// TODO: 実際のデータはAPIから取得
const mockSessions = [
  {
    id: '1',
    customerName: '山田 花子',
    counselorName: '田中 太郎',
    date: '2024-01-15 14:30',
    duration: '45分',
    status: 'completed',
    labelingStatus: 'labeled',
    result: 'success',
  },
  {
    id: '2',
    customerName: '佐藤 美咲',
    counselorName: '鈴木 一郎',
    date: '2024-01-15 15:30',
    duration: '38分',
    status: 'completed',
    labelingStatus: 'labeled',
    result: 'failure',
  },
  {
    id: '3',
    customerName: '高橋 真理',
    counselorName: '田中 太郎',
    date: '2024-01-16 10:00',
    duration: '52分',
    status: 'completed',
    labelingStatus: 'pending',
    result: null,
  },
  {
    id: '4',
    customerName: '中村 優子',
    counselorName: '山田 次郎',
    date: '2024-01-16 11:30',
    duration: '41分',
    status: 'completed',
    labelingStatus: 'pending',
    result: null,
  },
];

export default function LabelingPage() {
  const pendingCount = mockSessions.filter(s => s.labelingStatus === 'pending').length;
  const labeledCount = mockSessions.filter(s => s.labelingStatus === 'labeled').length;
  const successCount = mockSessions.filter(s => s.result === 'success').length;
  const failureCount = mockSessions.filter(s => s.result === 'failure').length;

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            ラベリング
          </h1>
          <p className="text-gray-600">
            カウンセリングセッションの成功・失敗をラベリング
          </p>
        </div>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <Clock className="h-4 w-4 mr-2 text-orange-600" />
              ラベリング待ち
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{pendingCount}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
              完了済み
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{labeledCount}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
              成功
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{successCount}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center">
              <AlertCircle className="h-4 w-4 mr-2 text-red-600" />
              失敗
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{failureCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* セッション一覧 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="h-5 w-5 mr-2" />
            セッション一覧
          </CardTitle>
          <CardDescription>
            ラベリングが必要なセッションと完了済みセッション
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockSessions.map((session) => (
              <div key={session.id} className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex-shrink-0">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    session.labelingStatus === 'pending' 
                      ? 'bg-orange-100 text-orange-600' 
                      : session.result === 'success'
                        ? 'bg-green-100 text-green-600'
                        : 'bg-red-100 text-red-600'
                  }`}>
                    {session.labelingStatus === 'pending' ? (
                      <Clock className="h-5 w-5" />
                    ) : session.result === 'success' ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      <AlertCircle className="h-5 w-5" />
                    )}
                  </div>
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h4 className="font-medium">{session.customerName}</h4>
                    <span className="text-sm text-gray-500">担当: {session.counselorName}</span>
                    {session.labelingStatus === 'pending' && (
                      <Badge variant="outline" className="text-orange-600 border-orange-600">
                        ラベリング待ち
                      </Badge>
                    )}
                    {session.labelingStatus === 'labeled' && session.result === 'success' && (
                      <Badge className="bg-green-500">成功</Badge>
                    )}
                    {session.labelingStatus === 'labeled' && session.result === 'failure' && (
                      <Badge className="bg-red-500">失敗</Badge>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {session.date}
                    </span>
                    <span className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {session.duration}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {session.labelingStatus === 'pending' ? (
                    <Link href={`/labeling/${session.id}`}>
                      <Button size="sm">
                        <Target className="h-4 w-4 mr-2" />
                        ラベリング開始
                      </Button>
                    </Link>
                  ) : (
                    <>
                      <Link href={`/labeling/${session.id}`}>
                        <Button variant="outline" size="sm">
                          <FileText className="h-4 w-4 mr-2" />
                          詳細確認
                        </Button>
                      </Link>
                      <Button variant="outline" size="sm">
                        再ラベリング
                      </Button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* ラベリング待ちがない場合 */}
          {pendingCount === 0 && (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                すべてのセッションがラベリング済みです
              </h3>
              <p className="text-gray-600">
                新しいセッションがアップロードされるまでお待ちください
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}