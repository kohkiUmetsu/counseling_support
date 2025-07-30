import React, { useState, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { 
  Loader2, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  RefreshCw,
  Wifi,
  WifiOff 
} from 'lucide-react';

interface ProcessingStatusProps {
  sessionId: string;
  onProcessingComplete?: (data: any) => void;
  onError?: (error: string) => void;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  sessionId,
  onProcessingComplete,
  onError,
}) => {
  const [status, setStatus] = useState<string>('pending');
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<string>('');
  const [details, setDetails] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const {
    isConnected,
    lastMessage,
    reconnectAttempts,
    connect,
  } = useWebSocket({
    sessionId,
    enabled: true,
    onMessage: (message) => {
      switch (message.type) {
        case 'progress_update':
          setProgress(message.progress || 0);
          setStage(message.stage || '');
          setDetails(message.details || '');
          setStatus('processing');
          break;
          
        case 'transcription_update':
          setStatus(message.status || 'unknown');
          if (message.status === 'completed' && onProcessingComplete) {
            onProcessingComplete(message.data);
          }
          break;
          
        case 'error':
          setError(message.error || 'Unknown error occurred');
          setStatus('failed');
          if (onError) {
            onError(message.error || 'Unknown error occurred');
          }
          break;
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
  });

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="animate-spin h-6 w-6 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />;
      default:
        return <AlertTriangle className="h-6 w-6 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'bg-blue-50 border-blue-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStageDescription = (stage: string) => {
    const descriptions = {
      'initializing': 'Preparing transcription...',
      'downloading_audio': 'Downloading audio file...',
      'transcribing': 'Converting speech to text...',
      'speaker_diarization': 'Identifying speakers...',
      'saving_results': 'Saving transcription...',
      'completed': 'Transcription completed!',
    };
    return descriptions[stage as keyof typeof descriptions] || stage;
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    setError(null);
    setStatus('pending');
    setProgress(0);
    setStage('');
    setDetails('');
    // You would trigger a retry API call here
  };

  if (status === 'pending') {
    return null; // Don't show anything until processing starts
  }

  return (
    <div className={`rounded-lg border p-4 ${getStatusColor()}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          {getStatusIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold capitalize">
              {status === 'processing' ? 'Processing' : status}
            </h3>
            
            <div className="flex items-center space-x-2">
              {/* WebSocket Connection Status */}
              <div className="flex items-center space-x-1 text-xs">
                {isConnected ? (
                  <>
                    <Wifi className="h-3 w-3 text-green-500" />
                    <span className="text-green-600">Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3 w-3 text-red-500" />
                    <span className="text-red-600">
                      {reconnectAttempts > 0 ? `Reconnecting... (${reconnectAttempts})` : 'Disconnected'}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          {status === 'processing' && (
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>{getStageDescription(stage)}</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
              
              {details && (
                <p className="text-sm text-gray-600">{details}</p>
              )}
            </div>
          )}

          {status === 'completed' && (
            <p className="text-green-700">
              Your audio has been successfully transcribed and is ready for review.
            </p>
          )}

          {status === 'failed' && (
            <div className="space-y-3">
              <p className="text-red-700">
                {error || 'An error occurred during processing.'}
              </p>
              
              <button
                onClick={handleRetry}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Retry Processing</span>
              </button>
              
              {retryCount > 0 && (
                <p className="text-xs text-gray-500">
                  Retry attempts: {retryCount}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};