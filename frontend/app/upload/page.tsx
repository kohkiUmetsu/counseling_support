'use client'

import React, { useState } from 'react';
import { FileDropzone } from '@/app/components/upload/FileDropzone';
import { UploadProgress } from '@/app/components/upload/UploadProgress';
import { uploadAudio } from '@/app/lib/api';
import { Upload } from 'lucide-react';
import Link from 'next/link';

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<
    'idle' | 'uploading' | 'success' | 'error'
  >('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setUploadStatus('idle');
    setUploadProgress(0);
    setErrorMessage('');
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setUploadStatus('idle');
    setUploadProgress(0);
    setErrorMessage('');
    setSessionId('');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploadStatus('uploading');
      setUploadProgress(0);

      const response = await uploadAudio(selectedFile, (progress) => {
        setUploadProgress(progress);
      });

      setSessionId(response.sessionId);
      setUploadStatus('success');
      
      console.log('Upload successful:', response);
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(
        error instanceof Error ? error.message : 'Upload failed'
      );
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          音声ファイルアップロード
        </h1>
        <p className="mt-2 text-gray-600">
          カウンセリングセッションの音声ファイルをアップロードして文字起こしを開始します
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <FileDropzone
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
          onClearFile={handleClearFile}
        />

        {selectedFile && uploadStatus === 'idle' && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={handleUpload}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Upload size={20} />
              <span>アップロード開始</span>
            </button>
          </div>
        )}

        <UploadProgress
          progress={uploadProgress}
          status={uploadStatus}
          fileName={selectedFile?.name}
          errorMessage={errorMessage}
        />

        {uploadStatus === 'success' && sessionId && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">
              セッションID: <span className="font-mono">{sessionId}</span>
            </p>
            <p className="text-sm text-green-600 mt-1">
              音声ファイルが正常にアップロードされました。ラベリングを行ってください。
            </p>
            <div className="mt-4">
              <Link
                href={`/labeling/${sessionId}`}
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                ラベリングに進む
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}