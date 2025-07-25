import { apiClient } from './base';

export interface TranscriptionSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker: 'counselor' | 'client';
  speaker_confidence?: number;
  is_edited?: boolean;
  original_text?: string;
}

export interface SpeakerStats {
  counselor: {
    total_time: number;
    segment_count: number;
    percentage: number;
  };
  client: {
    total_time: number;
    segment_count: number;
    percentage: number;
  };
}

export interface TranscriptionData {
  transcription_id: string;
  session_id: string;
  full_text: string;
  language: string;
  duration: number;
  segments: TranscriptionSegment[];
  speaker_stats: SpeakerStats;
  processing_time: number;
  created_at: string;
  updated_at: string;
}

export interface TranscriptionStatus {
  session_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  transcription_id?: string;
  processing_time?: number;
  language?: string;
  duration?: number;
  speaker_stats?: SpeakerStats;
}


export async function startTranscription(sessionId: string): Promise<{ transcription_id: string; status: string }> {
  const response = await apiClient.post<{ transcription_id: string; status: string }>(`/transcriptions/${sessionId}/start`);
  return response.data;
}

export async function getTranscriptionStatus(sessionId: string): Promise<TranscriptionStatus> {
  const response = await apiClient.get<TranscriptionStatus>(`/transcriptions/${sessionId}/status`);
  return response.data;
}

export async function getTranscription(sessionId: string): Promise<TranscriptionData> {
  const response = await apiClient.get<TranscriptionData>(`/transcriptions/${sessionId}`);
  return response.data;
}

export async function updateTranscriptionSegment(
  transcriptionId: string,
  segmentIndex: number,
  newText: string
): Promise<void> {
  await apiClient.patch<void>(`/transcriptions/${transcriptionId}/segments/${segmentIndex}`, {
    new_text: newText,
  });
}

