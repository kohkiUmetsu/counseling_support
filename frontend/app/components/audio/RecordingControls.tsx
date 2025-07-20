import React from 'react';
import { Mic, Square, Pause, Play, Trash2 } from 'lucide-react';

interface RecordingControlsProps {
  isRecording: boolean;
  isPaused: boolean;
  hasRecording: boolean;
  onStart: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
  onClear: () => void;
  disabled?: boolean;
}

export const RecordingControls: React.FC<RecordingControlsProps> = ({
  isRecording,
  isPaused,
  hasRecording,
  onStart,
  onStop,
  onPause,
  onResume,
  onClear,
  disabled = false,
}) => {
  return (
    <div className="flex items-center justify-center space-x-4">
      {!isRecording && !hasRecording && (
        <button
          onClick={onStart}
          disabled={disabled}
          className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <Mic size={20} />
          <span>Start Recording</span>
        </button>
      )}

      {isRecording && (
        <>
          <button
            onClick={onStop}
            className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            <Square size={20} />
            <span>Stop</span>
          </button>

          {!isPaused ? (
            <button
              onClick={onPause}
              className="flex items-center space-x-2 px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
            >
              <Pause size={20} />
              <span>Pause</span>
            </button>
          ) : (
            <button
              onClick={onResume}
              className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <Play size={20} />
              <span>Resume</span>
            </button>
          )}
        </>
      )}

      {hasRecording && !isRecording && (
        <>
          <button
            onClick={onStart}
            className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            <Mic size={20} />
            <span>New Recording</span>
          </button>
          
          <button
            onClick={onClear}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            <Trash2 size={20} />
            <span>Clear</span>
          </button>
        </>
      )}
    </div>
  );
};