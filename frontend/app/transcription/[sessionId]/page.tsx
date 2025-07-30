'use client'

import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { TranscriptionViewer } from '@/app/components/transcription/TranscriptionViewer';
import { ProcessingStatus } from '@/app/components/notifications/ProcessingStatus';
import { LoadingSpinner } from '@/app/components/ui/LoadingSpinner';
import { 
  getTranscription, 
  getTranscriptionStatus, 
  startTranscription, 
  updateTranscriptionSegment,
  TranscriptionData,
  TranscriptionStatus
} from '@/repository';
import { AlertCircle, Play, RefreshCw } from 'lucide-react';
import { Button } from '@/app/components/ui/button';

export default function TranscriptionPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  
  const [transcription, setTranscription] = useState<TranscriptionData | null>(null);
  const [status, setStatus] = useState<TranscriptionStatus | null>(null);
  // const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const fetchTranscription = useCallback(async () => {
    if (!sessionId) return;

    try {
      const transcriptionData = await getTranscription(sessionId);
      setTranscription(transcriptionData);
    } catch (err) {
      setError('文字起こしデータの読み込みに失敗しました');
      console.error('Error fetching transcription:', err);
    }
  }, [sessionId]);

  const fetchTranscriptionStatus = useCallback(async () => {
    if (!sessionId) return;

    try {
      const statusData = await getTranscriptionStatus(sessionId);
      setStatus(statusData);

      if (statusData.status === 'completed' && statusData.transcription_id) {
        await fetchTranscription();
      }
    } catch (err) {
      setError('文字起こし状況の読み込みに失敗しました');
      console.error('Error fetching status:', err);
    } finally {
      setLoading(false);
    }
  }, [sessionId, fetchTranscription]);

  useEffect(() => {
    if (!sessionId) {
      setError('セッションIDが指定されていません');
      setLoading(false);
      return;
    }

    fetchTranscriptionStatus();
  }, [sessionId, fetchTranscriptionStatus]);

  const handleStartTranscription = async () => {
    if (!sessionId) return;

    setStarting(true);
    setError(null);

    try {
      await startTranscription(sessionId);
      
      // Update local status to processing
      setStatus(prev => prev ? { ...prev, status: 'processing' } : null);
      
      // Refresh status after starting
      setTimeout(() => {
        fetchTranscriptionStatus();
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '文字起こしの開始に失敗しました');
    } finally {
      setStarting(false);
    }
  };

  const handleSegmentUpdate = async (segmentIndex: number, newText: string) => {
    if (!transcription) return;

    try {
      await updateTranscriptionSegment(transcription.transcription_id, segmentIndex, newText);
      
      // Update local state
      const updatedSegments = [...transcription.segments];
      if (!updatedSegments[segmentIndex].original_text) {
        updatedSegments[segmentIndex].original_text = updatedSegments[segmentIndex].text;
      }
      updatedSegments[segmentIndex].text = newText;
      updatedSegments[segmentIndex].is_edited = true;

      setTranscription({
        ...transcription,
        segments: updatedSegments
      });
    } catch (err) {
      console.error('Error updating segment:', err);
      alert('セグメントの更新に失敗しました');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
        <AlertCircle className="h-5 w-5 text-red-500" />
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          音声文字起こし
        </h1>
        <p className="mt-2 text-gray-600">
          セッション音声の自動文字起こしと編集
        </p>
      </div>

      {/* Status Section */}
      {status && (
        <div className="mb-8">
          {status.status === 'pending' && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
              <h2 className="text-xl font-semibold mb-4">文字起こし準備完了</h2>
              <p className="text-gray-600 mb-4">
                セッションID: <span className="font-mono">{sessionId}</span>
              </p>
              <Button
                onClick={handleStartTranscription}
                disabled={starting}
                className="mx-auto"
              >
                {starting ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <Play className="h-5 w-5 mr-2" />
                )}
                {starting ? '開始中...' : '文字起こし開始'}
              </Button>
            </div>
          )}

          {status.status === 'processing' && (
            <ProcessingStatus
              sessionId={sessionId}
              onProcessingComplete={() => {
                fetchTranscriptionStatus();
              }}
              onError={(error) => {
                setError(error);
              }}
            />
          )}

          {status.status === 'failed' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <AlertCircle className="h-6 w-6 text-red-500" />
                <h2 className="text-xl font-semibold text-red-800">文字起こし失敗</h2>
              </div>
              <p className="text-red-600 mb-4">
                文字起こし処理でエラーが発生しました。再試行してください。
              </p>
              <Button
                onClick={handleStartTranscription}
                disabled={starting}
                variant="secondary"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                再試行
              </Button>
            </div>
          )}

          {status.status === 'completed' && status.speaker_stats && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-green-800">文字起こし完了</h3>
                  <p className="text-sm text-green-600">
                    処理時間: {status.processing_time?.toFixed(1)}秒 | 
                    言語: {status.language} | 
                    長さ: {status.duration ? `${Math.floor(status.duration / 60)}:${Math.floor(status.duration % 60).toString().padStart(2, '0')}` : '不明'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Transcription Viewer */}
      {transcription && (
        <TranscriptionViewer
          transcriptionId={transcription.transcription_id}
          sessionId={transcription.session_id}
          fullText={transcription.full_text}
          segments={transcription.segments}
          audioUrl={`${process.env.NEXT_PUBLIC_API_URL}/sessions/${sessionId}/audio`}
          onSegmentUpdate={handleSegmentUpdate}
          isEditable={true}
        />
      )}
    </div>
  );
}