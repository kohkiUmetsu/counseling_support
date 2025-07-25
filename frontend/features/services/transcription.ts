import { 
  startTranscription as repoStartTranscription,
  getTranscriptionStatus as repoGetTranscriptionStatus,
  getTranscription as repoGetTranscription,
  updateTranscriptionSegment as repoUpdateTranscriptionSegment,
  TranscriptionData,
  TranscriptionStatus,
  TranscriptionSegment,
  SpeakerStats
} from '@/repository';

export type {
  TranscriptionData,
  TranscriptionStatus,
  TranscriptionSegment,
  SpeakerStats
};

export const startTranscription = repoStartTranscription;
export const getTranscriptionStatus = repoGetTranscriptionStatus;
export const getTranscription = repoGetTranscription;
export const updateTranscriptionSegment = repoUpdateTranscriptionSegment;