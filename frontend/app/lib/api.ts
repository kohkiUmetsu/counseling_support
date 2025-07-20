import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface CounselingSession {
  id: number;
  counselor_name: string;
  client_age?: number;
  client_gender?: string;
  treatment_type?: string;
  session_duration_minutes?: number;
  session_date: string;
  audio_file_path?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CounselingSessionCreate {
  counselor_name: string;
  client_age?: number;
  client_gender?: string;
  treatment_type?: string;
  session_duration_minutes?: number;
}

export interface Transcription {
  id: number;
  session_id: number;
  speaker?: string;
  start_time?: number;
  end_time?: number;
  text_content: string;
  confidence_score?: number;
  created_at: string;
}

export interface ImprovementScript {
  id: number;
  session_id: number;
  original_section: string;
  improved_section: string;
  improvement_reason?: string;
  ai_model_used?: string;
  improvement_score?: number;
  created_at: string;
}

// API Functions
export const counselingApi = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Sessions
  getSessions: () => api.get<CounselingSession[]>('/counseling/sessions'),
  getSession: (id: number) => api.get<CounselingSession>(`/counseling/sessions/${id}`),
  createSession: (data: CounselingSessionCreate) => 
    api.post<CounselingSession>('/counseling/sessions', data),
  updateSession: (id: number, data: Partial<CounselingSessionCreate>) => 
    api.put<CounselingSession>(`/counseling/sessions/${id}`, data),
  deleteSession: (id: number) => api.delete(`/counseling/sessions/${id}`),

  // Transcriptions
  getTranscriptions: (sessionId: number) => 
    api.get<Transcription[]>(`/counseling/sessions/${sessionId}/transcriptions`),
  createTranscription: (sessionId: number, data: {
    speaker?: string;
    start_time?: number;
    end_time?: number;
    text_content: string;
    confidence_score?: number;
  }) => api.post<Transcription>(`/counseling/sessions/${sessionId}/transcriptions`, data),

  // Improvement Scripts
  getImprovements: (sessionId: number) => 
    api.get<ImprovementScript[]>(`/counseling/sessions/${sessionId}/improvements`),
  createImprovement: (sessionId: number, data: {
    original_section: string;
    improved_section: string;
    improvement_reason?: string;
    ai_model_used?: string;
    improvement_score?: number;
  }) => api.post<ImprovementScript>(`/counseling/sessions/${sessionId}/improvements`, data),
};