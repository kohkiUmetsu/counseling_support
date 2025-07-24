'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface ScriptContentProps {
  phase: string;
  content?: string;
  successFactors?: string[];
  improvementPoints?: string[];
}

const PHASE_LABELS: Record<string, string> = {
  opening: 'オープニング',
  needs_assessment: 'ニーズ確認',
  solution_proposal: 'ソリューション提案',
  closing: 'クロージング'
};

export function ScriptContent({ 
  phase, 
  content, 
  successFactors = [], 
  improvementPoints = [] 
}: ScriptContentProps) {
  const [activeTab, setActiveTab] = useState('script');

  if (!content) {
    return (
      <div className="bg-white rounded-lg border p-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            このフェーズのスクリプトコンテンツがありません。
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {PHASE_LABELS[phase] || phase}フェーズ
          </h2>
          <p className="text-sm text-gray-600">
            カウンセリングの{PHASE_LABELS[phase]?.toLowerCase()}で使用するスクリプトです
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="script">スクリプト</TabsTrigger>
            <TabsTrigger value="success-factors">成功要因</TabsTrigger>
            <TabsTrigger value="improvements">改善ポイント</TabsTrigger>
          </TabsList>

          <TabsContent value="script" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <span>推奨スクリプト</span>
                  <Badge variant="outline" className="text-xs">
                    AI生成
                  </Badge>
                </CardTitle>
                <CardDescription>
                  成功事例分析に基づいて生成された推奨スクリプトです
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
                      ul: ({ children }) => <ul className="mb-4 pl-6 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="mb-4 pl-6 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="text-gray-700">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                      em: ({ children }) => <em className="italic text-gray-700">{children}</em>,
                      h3: ({ children }) => <h3 className="text-lg font-semibold text-gray-900 mt-6 mb-3">{children}</h3>,
                      h4: ({ children }) => <h4 className="text-base font-medium text-gray-900 mt-4 mb-2">{children}</h4>,
                    }}
                  >
                    {content}
                  </ReactMarkdown>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="success-factors" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>成功要因</span>
                </CardTitle>
                <CardDescription>
                  このフェーズで重要な成功要因とポイント
                </CardDescription>
              </CardHeader>
              <CardContent>
                {successFactors.length > 0 ? (
                  <div className="space-y-3">
                    {successFactors.map((factor, index) => (
                      <div 
                        key={index}
                        className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-200"
                      >
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700 leading-relaxed">
                          {factor}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      このフェーズの成功要因データがありません。
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="improvements" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  <span>改善ポイント</span>
                </CardTitle>
                <CardDescription>
                  失敗事例から学んだ改善すべきポイント
                </CardDescription>
              </CardHeader>
              <CardContent>
                {improvementPoints.length > 0 ? (
                  <div className="space-y-3">
                    {improvementPoints.map((point, index) => (
                      <div 
                        key={index}
                        className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                      >
                        <Lightbulb className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700 leading-relaxed">
                          {point}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      このフェーズの改善ポイントデータがありません。
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* 印刷用スタイル */}
        <style jsx global>{`
          @media print {
            .prose {
              font-size: 12pt;
              line-height: 1.5;
            }
            .prose p {
              margin-bottom: 8pt;
            }
            .prose ul, .prose ol {
              margin-bottom: 8pt;
            }
            .prose h3 {
              font-size: 14pt;
              margin-top: 16pt;
              margin-bottom: 8pt;
            }
            .prose h4 {
              font-size: 12pt;
              margin-top: 12pt;
              margin-bottom: 6pt;
            }
          }
        `}</style>
      </div>
    </div>
  );
}