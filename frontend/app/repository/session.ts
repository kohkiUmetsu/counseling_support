import { apiRequest, uploadRequest, streamRequest } from './base';

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
  
  return uploadRequest<UploadResponse>('/sessions/upload', formData, onProgress);
}

export async function getSession(sessionId: string): Promise<SessionData> {
  return apiRequest<SessionData>(`/sessions/${sessionId}`);
}

export async function updateSessionLabel(
  sessionId: string,
  data: {
    isSuccess: boolean;
    counselorName?: string;
    comment?: string;
  }
): Promise<SessionData> {
  return apiRequest<SessionData>(`/sessions/${sessionId}/label`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function getSessionAudio(sessionId: string): Promise<Response> {
  return streamRequest(`/sessions/${sessionId}/audio`);
}