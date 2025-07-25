import { apiClient } from './base';

export interface SessionData {
  id: string;
  fileUrl: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  duration?: number;
  isSuccess?: boolean;
  counselorName?: string;
  comment?: string;
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
  const response = await apiClient.patch<SessionData>(`/sessions/${sessionId}/label`, data);
  return response.data;
}

export async function getSessionAudio(sessionId: string) {
  const response = await apiClient.get(`/sessions/${sessionId}/audio`, {
    responseType: 'blob',
  });
  return response;
}