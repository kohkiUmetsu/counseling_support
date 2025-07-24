import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, SkipBack, SkipForward } from 'lucide-react';

interface TranscriptionSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker: 'counselor' | 'client';
}

interface TimestampPlayerProps {
  audioUrl: string;
  currentTime: number;
  onTimeUpdate: (time: number) => void;
  onPlayStateChange: (isPlaying: boolean) => void;
  segments: TranscriptionSegment[];
}

export const TimestampPlayer: React.FC<TimestampPlayerProps> = ({
  audioUrl,
  currentTime,
  onTimeUpdate,
  onPlayStateChange,
  segments,
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleTimeUpdate = () => {
      onTimeUpdate(audio.currentTime);
    };

    const handlePlay = () => {
      setIsPlaying(true);
      onPlayStateChange(true);
    };

    const handlePause = () => {
      setIsPlaying(false);
      onPlayStateChange(false);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      onPlayStateChange(false);
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [onTimeUpdate, onPlayStateChange]);

  const togglePlayPause = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  const seekTo = (time: number) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = time;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    seekTo(newTime);
  };

  const skipBackward = () => {
    seekTo(Math.max(0, currentTime - 10));
  };

  const skipForward = () => {
    seekTo(Math.min(duration, currentTime + 10));
  };

  const resetAudio = () => {
    seekTo(0);
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
    }
  };

  const changePlaybackRate = (rate: number) => {
    setPlaybackRate(rate);
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getCurrentSegment = () => {
    return segments.find(segment => 
      currentTime >= segment.start && currentTime <= segment.end
    );
  };

  const currentSegment = getCurrentSegment();

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <audio ref={audioRef} src={audioUrl} />
      
      {/* Current Segment Display */}
      {currentSegment && (
        <div className="mb-4 p-3 bg-gray-50 rounded border-l-4 border-blue-500">
          <div className="flex items-center justify-between mb-1">
            <span className={`text-sm font-semibold capitalize ${
              currentSegment.speaker === 'counselor' ? 'text-blue-600' : 'text-green-600'
            }`}>
              {currentSegment.speaker}
            </span>
            <span className="text-xs text-gray-500">
              {formatTime(currentSegment.start)} - {formatTime(currentSegment.end)}
            </span>
          </div>
          <p className="text-sm text-gray-800">{currentSegment.text}</p>
        </div>
      )}

      {/* Playback Controls */}
      <div className="flex items-center space-x-3 mb-4">
        <button
          onClick={skipBackward}
          className="p-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
          title="Skip back 10 seconds"
        >
          <SkipBack size={20} />
        </button>

        <button
          onClick={togglePlayPause}
          className="p-3 rounded-full bg-blue-500 text-white hover:bg-blue-600 transition-colors"
        >
          {isPlaying ? <Pause size={24} /> : <Play size={24} />}
        </button>

        <button
          onClick={skipForward}
          className="p-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
          title="Skip forward 10 seconds"
        >
          <SkipForward size={20} />
        </button>

        <button
          onClick={resetAudio}
          className="p-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
          title="Reset to beginning"
        >
          <RotateCcw size={20} />
        </button>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <input
          type="range"
          min="0"
          max={duration}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-sm text-gray-600 mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Playback Speed */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Speed:</span>
          {[0.5, 0.75, 1, 1.25, 1.5, 2].map(rate => (
            <button
              key={rate}
              onClick={() => changePlaybackRate(rate)}
              className={`px-2 py-1 text-xs rounded ${
                playbackRate === rate
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {rate}x
            </button>
          ))}
        </div>

        <div className="text-sm text-gray-600">
          Segment {segments.findIndex(s => s === currentSegment) + 1} of {segments.length}
        </div>
      </div>
    </div>
  );
};