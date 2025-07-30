import { apiClient } from './base';

export interface ScriptGenerationRequest {
  cluster_result_id: string;
  failure_conversations: Array<{
    session_id?: string;
    conversation?: string;
    [key: string]: any;
  }>;
  title?: string;
  description?: string;
}

export interface ScriptGenerationResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface ScriptGenerationStatus {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress_percentage: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  script?: {
    id: string;
    title: string;
    description?: string;
    content: any;
    quality_metrics?: any;
    generation_metadata?: any;
  };
  error_message?: string;
}

export interface ImprovementScript {
  id: string;
  version: string;
  title: string;
  description?: string;
  content: any;
  generation_metadata?: any;
  quality_metrics?: any;
  status: string;
  is_active: boolean;
  cluster_result_id?: string;
  based_on_failure_sessions?: string[];
  created_at: string;
  updated_at: string;
  activated_at?: string;
}

export const startScriptGeneration = async (
  request: ScriptGenerationRequest
): Promise<ScriptGenerationResponse> => {
  const response = await apiClient.post('/scripts/generate', request);
  return response.data;
};

export const getScriptGenerationStatus = async (
  jobId: string
): Promise<ScriptGenerationStatus> => {
  const response = await apiClient.get(`/scripts/generate/${jobId}/status`);
  return response.data;
};

export const getScript = async (scriptId: string): Promise<ImprovementScript> => {
  const response = await apiClient.get(`/scripts/${scriptId}`);
  return response.data;
};

export const getScripts = async (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  is_active?: boolean;
}): Promise<ImprovementScript[]> => {
  const response = await apiClient.get('/scripts/', { params });
  return response.data;
};

export const updateScript = async (
  scriptId: string, 
  updates: {
    title?: string;
    description?: string;
    content?: any;
    status?: string;
  }
): Promise<ImprovementScript> => {
  const response = await apiClient.patch(`/scripts/${scriptId}`, updates);
  return response.data;
};

export const activateScript = async (scriptId: string): Promise<ImprovementScript> => {
  const response = await apiClient.post(`/scripts/${scriptId}/activate`);
  return response.data;
};

export const deactivateScript = async (scriptId: string): Promise<ImprovementScript> => {
  const response = await apiClient.post(`/scripts/${scriptId}/deactivate`);
  return response.data;
};