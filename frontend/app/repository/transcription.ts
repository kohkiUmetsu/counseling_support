import { apiRequest } from './base';

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

export interface TaskStatus {
  task_id: string;
  state: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILURE';
  progress: number;
  stage: string;
  result?: any;
  error?: string;
  traceback?: string;
}

export async function startTranscription(sessionId: string): Promise<{ task_id: string }> {
  return apiRequest<{ task_id: string }>(`/transcriptions/${sessionId}/start`, {
    method: 'POST',
  });
}

export async function getTranscriptionStatus(sessionId: string): Promise<TranscriptionStatus> {
  return apiRequest<TranscriptionStatus>(`/transcriptions/${sessionId}/status`);
}

export async function getTranscription(sessionId: string): Promise<TranscriptionData> {
  return apiRequest<TranscriptionData>(`/transcriptions/${sessionId}`);
}

export async function updateTranscriptionSegment(
  transcriptionId: string,
  segmentIndex: number,
  newText: string
): Promise<void> {
  await apiRequest(`/transcriptions/${transcriptionId}/segments/${segmentIndex}`, {
    method: 'PATCH',
    body: JSON.stringify({ new_text: newText }),
  });
}

export async function getTaskStatus(taskId: string): Promise<TaskStatus> {
  return apiRequest<TaskStatus>(`/tasks/${taskId}/status`);
}