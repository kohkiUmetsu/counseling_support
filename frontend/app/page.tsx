'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Upload,
  Target,
  Zap,
  FileText,
  ArrowRight,
  CheckCircle,
  Star,
  Mic
} from 'lucide-react';

const features = [
  {
    title: 'データアップロード',
    description: '会話データのアップロードと前処理',
    href: '/upload',
    icon: Upload,
    status: 'completed',
    phase: 'フェーズ1',
  },
  {
    title: '録音',
    description: '会話の録音と音声データ管理',
    href: '/recording',
    icon: Mic,
    status: 'completed',
    phase: 'フェーズ1',
  },
  {
    title: 'ラベリング',
    description: '成功・失敗の手動ラベリング',
    href: '/labeling',
    icon: Target,
    status: 'completed',
    phase: 'フェーズ2',
  },
  {
    title: 'スクリプト生成',
    description: 'AIによる改善スクリプト生成',
    href: '/scripts/generate',
    icon: Zap,
    status: 'completed',
    phase: 'フェーズ4',
  },
  {
    title: 'スクリプト管理',
    description: 'スクリプトの表示・管理',
    href: '/scripts',
    icon: FileText,
    status: 'completed',
    phase: 'フェーズ5',
  },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'completed':
      return <Badge className="bg-green-500 hover:bg-green-600">完了</Badge>;
    case 'available':
      return <Badge variant="outline">利用可能</Badge>;
    default:
      return <Badge variant="secondary">開発中</Badge>;
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    case 'available':
      return <Star className="h-5 w-5 text-blue-600" />;
    default:
      return null;
  }
};

export default function Home() {
  return (
    <div className="space-y-8">
      {/* ヘッダー */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Counseling Support
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          美容脱毛業界特化 AIカウンセリングスクリプト生成システム
        </p>
        <p className="text-lg text-gray-500">
          ベクトル検索・クラスタリング・GPT-4oによる高品質スクリプト生成
        </p>
      </div>

      {/* システム概要 */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold">3</div>
            <div className="text-blue-100">実装フェーズ</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">5</div>
            <div className="text-blue-100">主要機能</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">MVP</div>
            <div className="text-blue-100">開発ステータス</div>
          </div>
        </div>
      </div>

      {/* 機能一覧 */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">機能一覧</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card key={feature.href} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <feature.icon className="h-8 w-8 text-blue-600" />
                  {getStatusIcon(feature.status)}
                </div>
                <CardTitle className="flex items-center justify-between">
                  <span>{feature.title}</span>
                  {getStatusBadge(feature.status)}
                </CardTitle>
                <CardDescription>{feature.description}</CardDescription>
                <div className="text-xs text-gray-500">{feature.phase}</div>
              </CardHeader>
              <CardContent>
                <Link href={feature.href}>
                  <Button 
                    className="w-full" 
                    variant={feature.status === 'completed' ? 'default' : 'outline'}
                  >
                    <span>開く</span>
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* 推奨ワークフロー */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">推奨ワークフロー</h2>
        <Card>
          <CardHeader>
            <CardTitle>スクリプト生成・改善のステップ</CardTitle>
            <CardDescription>
              効果的なスクリプト生成のための推奨手順
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">データアップロード</h4>
                  <p className="text-sm text-gray-600">会話データをシステムに取り込む</p>
                </div>
                <Link href="/upload">
                  <Button size="sm" variant="outline">開始</Button>
                </Link>
              </div>

              <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">ラベリング</h4>
                  <p className="text-sm text-gray-600">成功・失敗の判定とメタデータ付与</p>
                </div>
                <Link href="/labeling">
                  <Button size="sm" variant="outline">実行</Button>
                </Link>
              </div>

              <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">スクリプト生成</h4>
                  <p className="text-sm text-gray-600">AIによる改善スクリプト自動生成</p>
                </div>
                <Link href="/scripts/generate">
                  <Button size="sm">生成開始</Button>
                </Link>
              </div>

            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}