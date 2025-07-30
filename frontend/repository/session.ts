import { apiClient } from './base';

export interface SessionData {
  id: string;
  file_url: string;
  file_name: string;
  file_size: number;
  file_type: string;
  duration?: number;
  is_success?: boolean;
  counselor_name?: string;
  comment?: string;
  transcription_status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface UploadResponse {
  session_id: string;
  message: string;
}

export async function uploadAudio(
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('audio', file);
  
  const config = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    ...(onProgress && {
      onUploadProgress: (progressEvent: { loaded: number; total?: number }) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          onProgress(progress);
        }
      },
    }),
  };
  
  const response = await apiClient.post<UploadResponse>('/sessions/upload', formData, config);
  
  return response.data;
}

export async function getSession(sessionId: string): Promise<SessionData> {
  const response = await apiClient.get<SessionData>(`/sessions/${sessionId}`);
  return response.data;
}

export async function updateSessionLabel(
  sessionId: string,
  data: {
    isSuccess: boolean;
    counselorName?: string;
    comment?: string;
  }
): Promise<SessionData> {
  const payload = {
    is_success: data.isSuccess,
    counselor_name: data.counselorName,
    comment: data.comment
  };
  
  console.log('Sending payload:', payload);
  
  const response = await apiClient.patch<SessionData>(`/sessions/${sessionId}/label`, payload);
  return response.data;
}

export async function getSessionAudio(sessionId: string) {
  const response = await apiClient.get(`/sessions/${sessionId}/audio`, {
    responseType: 'blob',
  });
  return response;
}

export async function getSessions(skip: number = 0, limit: number = 100): Promise<SessionData[]> {
  const response = await apiClient.get<SessionData[]>(`/sessions`, {
    params: { skip, limit }
  });
  return response.data;
}