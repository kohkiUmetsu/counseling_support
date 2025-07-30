'use client'

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { LabelingForm } from '@/app/components/labeling/LabelingForm';
import { AudioPlayer } from '@/app/components/audio/AudioPlayer';
import { getSession } from '@/repository';
import { SessionData } from '@/repository';
import { LoadingSpinner } from '@/app/components/ui/LoadingSpinner';
import { getTranscriptionStatus, getTranscription } from '@/repository';
import { TranscriptionViewer } from '@/app/components/transcription/TranscriptionViewer';
import { CheckCircle2 } from 'lucide-react';


export default function LabelingPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  
  const [session, setSession] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [transcriptionData, setTranscriptionData] = useState<any>(null);
  const [transcriptionStatus, setTranscriptionStatus] = useState<any>(null);

  useEffect(() => {
    if (!sessionId) {
      setError('セッションIDが指定されていません');
      setLoading(false);
      return;
    }

    fetchSession();
  }, [sessionId]);

  const fetchSession = async () => {
    try {
      const data = await getSession(sessionId);
      setSession(data);
      
      // 文字起こし状態もチェック
      try {
        const status = await getTranscriptionStatus(sessionId);
        setTranscriptionStatus(status);
        
        if (status.status === 'completed' && status.transcription_id) {
          const transcription = await getTranscription(sessionId);
          setTranscriptionData(transcription);
        }
      } catch (err) {
        console.log('文字起こしデータはまだありません');
      }
    } catch (err) {
      setError('セッションデータの読み込みに失敗しました');
      console.error('Error fetching session:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLabelingComplete = () => {
    router.push(`/transcription/${sessionId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error || 'セッションが見つかりません'}</p>
      </div>
    );
  }

  // Create blob from file URL for audio player
  const audioBlob = new Blob([], { type: session.file_type });
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          セッションラベリング
        </h1>
        <p className="mt-2 text-gray-600">
          アップロードされた音声セッションに成功/失敗のラベルを付けてください
        </p>
      </div>

      {/* 文字起こし完了時は結果を表示 */}
      {transcriptionData && transcriptionStatus?.status === 'completed' ? (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <div>
              <h3 className="font-semibold text-green-800">文字起こし完了</h3>
              <p className="text-sm text-green-600">
                処理時間: {transcriptionStatus.processing_time?.toFixed(1)}秒 | 
                言語: {transcriptionStatus.language} | 
                長さ: {transcriptionStatus.duration ? `${Math.floor(transcriptionStatus.duration / 60)}:${Math.floor(transcriptionStatus.duration % 60).toString().padStart(2, '0')}` : '不明'}
              </p>
            </div>
          </div>

          <TranscriptionViewer
            transcriptionId={transcriptionData.transcription_id}
            sessionId={transcriptionData.session_id}
            fullText={transcriptionData.full_text}
            segments={transcriptionData.segments}
            audioUrl={session.file_url}
            onSegmentUpdate={() => {}}
            isEditable={false}
          />
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">セッション音声</h2>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                <p><strong>ファイル名:</strong> {session.file_name}</p>
                <p><strong>サイズ:</strong> {(session.file_size / 1024 / 1024).toFixed(2)} MB</p>
                {session.duration && (
                  <p><strong>長さ:</strong> {Math.floor(session.duration / 60)}:{Math.floor(session.duration % 60).toString().padStart(2, '0')}</p>
                )}
              </div>
              
              <AudioPlayer
                audioUrl={session.file_url}
                audioBlob={audioBlob}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <LabelingForm
              sessionId={sessionId}
              onComplete={handleLabelingComplete}
            />
          </div>
        </div>
      )}
    </div>
  );
}