import { Suspense } from 'react';
import { Metadata } from 'next';
import { ScriptViewer } from './components/ScriptViewer';
import { ScriptViewerSkeleton } from './components/ScriptViewerSkeleton';

interface PageProps {
  params: { id: string };
  searchParams: { phase?: string };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  return {
    title: `スクリプト詳細 | Counseling Support`,
    description: 'カウンセリングスクリプトの詳細表示ページ',
  };
}

export default async function ScriptViewerPage({ params, searchParams }: PageProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6">
        <Suspense fallback={<ScriptViewerSkeleton />}>
          <ScriptViewer 
            scriptId={params.id} 
            initialPhase={searchParams.phase || 'opening'}
          />
        </Suspense>
      </div>
    </div>
  );
}