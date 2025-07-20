import React, { useState } from 'react';
import { SpeakerSegment } from './SpeakerSegment';
import { TimestampPlayer } from './TimestampPlayer';
import { TranscriptionEditor } from './TranscriptionEditor';
import { Play, Pause, Edit3, Save, X } from 'lucide-react';

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

interface TranscriptionViewerProps {
  transcriptionId: string;
  sessionId: string;
  fullText: string;
  segments: TranscriptionSegment[];
  audioUrl: string;
  onSegmentUpdate?: (segmentIndex: number, newText: string) => void;
  isEditable?: boolean;
}

export const TranscriptionViewer: React.FC<TranscriptionViewerProps> = ({
  transcriptionId,
  sessionId,
  fullText,
  segments,
  audioUrl,
  onSegmentUpdate,
  isEditable = true,
}) => {
  const [editingSegment, setEditingSegment] = useState<number | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [viewMode, setViewMode] = useState<'segments' | 'full'>('segments');

  const handleSegmentClick = (startTime: number) => {
    // Jump to specific time in audio player
    setCurrentTime(startTime);
  };

  const handleEditStart = (segmentIndex: number) => {
    setEditingSegment(segmentIndex);
  };

  const handleEditSave = (segmentIndex: number, newText: string) => {
    if (onSegmentUpdate) {
      onSegmentUpdate(segmentIndex, newText);
    }
    setEditingSegment(null);
  };

  const handleEditCancel = () => {
    setEditingSegment(null);
  };

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getSpeakerStats = () => {
    const stats = { counselor: 0, client: 0 };
    segments.forEach(segment => {
      stats[segment.speaker] += segment.end - segment.start;
    });
    const total = stats.counselor + stats.client;
    return {
      counselor: total > 0 ? Math.round((stats.counselor / total) * 100) : 0,
      client: total > 0 ? Math.round((stats.client / total) * 100) : 0,
    };
  };

  const speakerStats = getSpeakerStats();

  return (
    <div className="space-y-6">
      {/* Audio Player */}
      <TimestampPlayer
        audioUrl={audioUrl}
        currentTime={currentTime}
        onTimeUpdate={setCurrentTime}
        onPlayStateChange={setIsPlaying}
        segments={segments}
      />

      {/* Speaker Statistics */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-semibold mb-3">Speaking Time Distribution</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-600">Counselor</span>
            <span className="text-sm font-medium">{speakerStats.counselor}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: `${speakerStats.counselor}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-green-600">Client</span>
            <span className="text-sm font-medium">{speakerStats.client}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${speakerStats.client}%` }}
            />
          </div>
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setViewMode('segments')}
          className={`px-3 py-1 rounded ${
            viewMode === 'segments'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700'
          }`}
        >
          Segments
        </button>
        <button
          onClick={() => setViewMode('full')}
          className={`px-3 py-1 rounded ${
            viewMode === 'full'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700'
          }`}
        >
          Full Text
        </button>
      </div>

      {/* Transcription Content */}
      {viewMode === 'segments' ? (
        <div className="space-y-2">
          {segments.map((segment, index) => (
            <div key={segment.id || index} className="group">
              {editingSegment === index ? (
                <TranscriptionEditor
                  initialText={segment.text}
                  onSave={(newText) => handleEditSave(index, newText)}
                  onCancel={handleEditCancel}
                />
              ) : (
                <SpeakerSegment
                  segment={segment}
                  isActive={currentTime >= segment.start && currentTime <= segment.end}
                  onClick={() => handleSegmentClick(segment.start)}
                  onEdit={isEditable ? () => handleEditStart(index) : undefined}
                />
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-semibold mb-4">Full Transcription</h3>
          <div className="prose max-w-none">
            <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
              {fullText}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};