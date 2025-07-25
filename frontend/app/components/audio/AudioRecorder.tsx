import React, { useState, useEffect } from 'react';
import { useMediaRecorder } from '@/features/hooks/useMediaRecorder';
import { WaveformVisualizer } from './WaveformVisualizer';
import { AudioPlayer } from './AudioPlayer';
import { RecordingControls } from './RecordingControls';
import { AlertCircle } from 'lucide-react';

interface AudioRecorderProps {
  onRecordingComplete?: (audioBlob: Blob, audioUrl: string) => void;
  maxDuration?: number; // in seconds
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  maxDuration = 3600, // 1 hour default
}) => {
  const [mediaStream, setMediaStream] = useState<MediaStream | undefined>();
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const {
    isRecording,
    isPaused,
    audioBlob,
    audioUrl,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    clearRecording,
    error,
  } = useMediaRecorder();

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isRecording && !isPaused) {
      interval = setInterval(() => {
        setRecordingDuration(prev => {
          const newDuration = prev + 1;
          if (newDuration >= maxDuration) {
            stopRecording();
          }
          return newDuration;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRecording, isPaused, maxDuration, stopRecording]);

  useEffect(() => {
    if (!isRecording) {
      setRecordingDuration(0);
    }
  }, [isRecording]);

  useEffect(() => {
    if (audioBlob && audioUrl && onRecordingComplete) {
      onRecordingComplete(audioBlob, audioUrl);
    }
  }, [audioBlob, audioUrl, onRecordingComplete]);

  const handleStartRecording = async () => {
    try {
      setPermissionError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMediaStream(stream);
      await startRecording();
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setPermissionError('Microphone access was denied. Please allow microphone access to record audio.');
        } else if (err.name === 'NotFoundError') {
          setPermissionError('No microphone found. Please connect a microphone and try again.');
        } else {
          setPermissionError(err.message);
        }
      }
    }
  };

  const handleStopRecording = () => {
    stopRecording();
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      setMediaStream(undefined);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {(error || permissionError) && (
        <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle size={20} />
          <p>{error || permissionError}</p>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-6 space-y-4">
        <div className="text-center">
          {isRecording && (
            <div className="mb-4">
              <div className="text-3xl font-mono font-bold text-red-600">
                {formatDuration(recordingDuration)}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {isPaused ? 'Paused' : 'Recording...'}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-center">
          <WaveformVisualizer
            audioStream={mediaStream}
            isActive={isRecording && !isPaused}
            width={400}
            height={120}
          />
        </div>

        <RecordingControls
          isRecording={isRecording}
          isPaused={isPaused}
          hasRecording={!!audioBlob}
          onStart={handleStartRecording}
          onStop={handleStopRecording}
          onPause={pauseRecording}
          onResume={resumeRecording}
          onClear={clearRecording}
          disabled={!!error || !!permissionError}
        />
      </div>

      {audioBlob && audioUrl && (
        <AudioPlayer
          audioBlob={audioBlob}
          audioUrl={audioUrl}
          className="mt-6"
        />
      )}
    </div>
  );
};