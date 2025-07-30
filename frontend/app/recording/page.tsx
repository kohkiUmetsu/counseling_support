'use client'

import React, { useState, useCallback } from 'react';
import { AudioRecorder } from '@/app/components/audio/AudioRecorder';
import { Upload } from 'lucide-react';
import { uploadAudio } from '@/repository';

export default function RecordingPage() {
  const [recordedAudio, setRecordedAudio] = useState<{
    blob: Blob;
    url: string;
  } | null>(null);

  const handleRecordingComplete = useCallback((audioBlob: Blob, audioUrl: string) => {
    setRecordedAudio({ blob: audioBlob, url: audioUrl });
  }, []);

  const handleUpload = async () => {
    if (!recordedAudio) return;

    try {
      // Convert blob to file
      const file = new File([recordedAudio.blob], 'recording.webm', {
        type: recordedAudio.blob.type || 'audio/webm'
      });
      const data = await uploadAudio(file);
      console.log('Upload successful:', data);
      // Handle successful upload
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          音声録音
        </h1>
        <p className="mt-2 text-gray-600">
          ブラウザでカウンセリングセッションの音声を録音します
        </p>
      </div>
      
      <AudioRecorder onRecordingComplete={handleRecordingComplete} />

      {recordedAudio && (
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleUpload}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Upload size={20} />
            <span>録音をアップロード</span>
          </button>
        </div>
      )}
    </div>
  );
}