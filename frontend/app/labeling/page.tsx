'use client'

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Target, Clock, CheckCircle, AlertCircle, FileText, Calendar } from 'lucide-react';
import { getSessions, SessionData } from '@/repository';
import { LoadingSpinner } from '@/app/components/ui/LoadingSpinner';

export default function LabelingPage() {
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (err) {
      setError('セッションデータの読み込みに失敗しました');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const pendingCount = sessions.filter(s => !s.is_success && s.is_success !== false).length;
  const labeledCount = sessions.filter(s => s.is_success !== null && s.is_success !== undefined).length;
  const successCount = sessions.filter(s => s.is_success === true).length;
  const failureCount = sessions.filter(s => s.is_success === false).length;

  const formatDate = (dateString?: string) => {
    if (!dateString) return '日時不明';
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '不明';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}分${remainingSeconds}秒`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

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
        <Button onClick={fetchSessions} variant="outline">
          更新
        </Button>
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
            {sessions.map((session) => {
              const isLabeled = session.is_success !== null && session.is_success !== undefined;
              
              return (
                <div key={session.id} className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex-shrink-0">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      !isLabeled
                        ? 'bg-orange-100 text-orange-600' 
                        : session.is_success
                          ? 'bg-green-100 text-green-600'
                          : 'bg-red-100 text-red-600'
                    }`}>
                      {!isLabeled ? (
                        <Clock className="h-5 w-5" />
                      ) : session.is_success ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <AlertCircle className="h-5 w-5" />
                      )}
                    </div>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-medium">{session.file_name}</h4>
                      {session.counselor_name && (
                        <span className="text-sm text-gray-500">担当: {session.counselor_name}</span>
                      )}
                      {!isLabeled && (
                        <Badge variant="outline" className="text-orange-600 border-orange-600">
                          ラベリング待ち
                        </Badge>
                      )}
                      {isLabeled && session.is_success && (
                        <Badge className="bg-green-500">成功</Badge>
                      )}
                      {isLabeled && !session.is_success && (
                        <Badge className="bg-red-500">失敗</Badge>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(session.created_at)}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatDuration(session.duration)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {!isLabeled ? (
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
                        <Link href={`/labeling/${session.id}`}>
                          <Button variant="outline" size="sm">
                            再ラベリング
                          </Button>
                        </Link>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* セッションがない場合 */}
          {sessions.length === 0 && (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                セッションがありません
              </h3>
              <p className="text-gray-600">
                音声ファイルをアップロードしてください
              </p>
              <Link href="/upload">
                <Button className="mt-4">
                  アップロードページへ
                </Button>
              </Link>
            </div>
          )}

          {/* ラベリング待ちがない場合 */}
          {sessions.length > 0 && pendingCount === 0 && (
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