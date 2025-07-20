import React, { useState } from 'react';
import { SuccessFailureToggle } from './SuccessFailureToggle';
import { MetadataForm } from './MetadataForm';
import { updateSessionLabel } from '@/app/lib/api';
import { CheckCircle, AlertCircle } from 'lucide-react';

interface LabelingFormProps {
  sessionId: string;
  onComplete?: () => void;
}

export const LabelingForm: React.FC<LabelingFormProps> = ({
  sessionId,
  onComplete,
}) => {
  const [isSuccess, setIsSuccess] = useState<boolean | null>(null);
  const [counselorName, setCounselorName] = useState('');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isSuccess === null) {
      setError('Please select success or failure status');
      return;
    }
    
    if (!counselorName.trim()) {
      setError('Please enter counselor name');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await updateSessionLabel(sessionId, {
        isSuccess,
        counselorName: counselorName.trim(),
        comment: comment.trim() || undefined,
      });
      
      setSubmitSuccess(true);
      if (onComplete) {
        setTimeout(onComplete, 1500); // Show success message briefly before completing
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update label');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900">Label Saved Successfully!</h3>
        <p className="text-gray-600 mt-2">Session has been labeled and saved.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Label Session</h3>
        <p className="text-sm text-gray-600 mb-4">
          Session ID: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{sessionId}</span>
        </p>
      </div>

      <SuccessFailureToggle
        value={isSuccess}
        onChange={setIsSuccess}
      />

      <MetadataForm
        counselorName={counselorName}
        onCounselorNameChange={setCounselorName}
        comment={comment}
        onCommentChange={setComment}
      />

      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle size={20} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={() => {
            setIsSuccess(null);
            setCounselorName('');
            setComment('');
            setError(null);
          }}
          className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
          disabled={isSubmitting}
        >
          Clear
        </button>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          disabled={isSubmitting || isSuccess === null || !counselorName.trim()}
        >
          {isSubmitting ? 'Saving...' : 'Save Label'}
        </button>
      </div>
    </form>
  );
};