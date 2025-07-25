import { 
  startTranscription as repoStartTranscription,
  getTranscriptionStatus as repoGetTranscriptionStatus,
  getTranscription as repoGetTranscription,
  updateTranscriptionSegment as repoUpdateTranscriptionSegment,
  getTaskStatus as repoGetTaskStatus,
  TranscriptionData,
  TranscriptionStatus,
  TranscriptionSegment,
  SpeakerStats,
  TaskStatus
} from '@/repository';

export type {
  TranscriptionData,
  TranscriptionStatus,
  TranscriptionSegment,
  SpeakerStats,
  TaskStatus
};

export const startTranscription = repoStartTranscription;
export const getTranscriptionStatus = repoGetTranscriptionStatus;
export const getTranscription = repoGetTranscription;
export const updateTranscriptionSegment = repoUpdateTranscriptionSegment;
export const getTaskStatus = repoGetTaskStatus;

// Polling helper for task status
export const pollTaskStatus = (
  taskId: string,
  onUpdate: (status: TaskStatus) => void,
  interval: number = 2000
): () => void => {
  const poll = async () => {
    try {
      const status = await getTaskStatus(taskId);
      onUpdate(status);
      
      if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
        clearInterval(intervalId);
      }
    } catch (error) {
      console.error('Error polling task status:', error);
    }
  };

  const intervalId = setInterval(poll, interval);
  poll(); // Initial call

  // Return cleanup function
  return () => clearInterval(intervalId);
};