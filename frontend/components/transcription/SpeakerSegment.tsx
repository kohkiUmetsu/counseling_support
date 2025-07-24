import React from 'react';
import { User, UserCheck, Clock, Edit3 } from 'lucide-react';

interface TranscriptionSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker: 'counselor' | 'client';
  speaker_confidence?: number;
  is_edited?: boolean;
  original_text?: string;
}

interface SpeakerSegmentProps {
  segment: TranscriptionSegment;
  isActive?: boolean;
  onClick?: () => void;
  onEdit?: () => void;
}

export const SpeakerSegment: React.FC<SpeakerSegmentProps> = ({
  segment,
  isActive = false,
  onClick,
  onEdit,
}) => {
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getSpeakerColor = (speaker: string) => {
    return speaker === 'counselor' 
      ? 'bg-blue-50 border-blue-200 text-blue-800'
      : 'bg-green-50 border-green-200 text-green-800';
  };

  const getSpeakerIcon = (speaker: string) => {
    return speaker === 'counselor' ? UserCheck : User;
  };

  const SpeakerIcon = getSpeakerIcon(segment.speaker);

  return (
    <div
      className={`border rounded-lg p-4 transition-all cursor-pointer group ${
        getSpeakerColor(segment.speaker)
      } ${
        isActive ? 'ring-2 ring-blue-400 shadow-md' : 'hover:shadow-sm'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          <SpeakerIcon size={20} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold capitalize">
                {segment.speaker}
              </span>
              {segment.speaker_confidence && (
                <span className="text-xs text-gray-600">
                  ({Math.round(segment.speaker_confidence * 100)}%)
                </span>
              )}
              {segment.is_edited && (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
                  Edited
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 text-xs text-gray-600">
                <Clock size={12} />
                <span>
                  {formatTime(segment.start)} - {formatTime(segment.end)}
                </span>
              </div>
              {onEdit && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit();
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-white/50 transition-opacity"
                  title="Edit segment"
                >
                  <Edit3 size={14} />
                </button>
              )}
            </div>
          </div>
          
          <p className="text-gray-800 leading-relaxed">
            {segment.text}
          </p>
          
          {segment.is_edited && segment.original_text && (
            <details className="mt-2">
              <summary className="text-xs text-gray-500 cursor-pointer">
                Show original text
              </summary>
              <p className="text-xs text-gray-600 mt-1 italic">
                {segment.original_text}
              </p>
            </details>
          )}
        </div>
      </div>
    </div>
  );
};