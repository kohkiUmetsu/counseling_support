import React from 'react';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface UploadProgressProps {
  progress: number;
  status: 'uploading' | 'success' | 'error' | 'idle';
  fileName?: string;
  errorMessage?: string;
}

export const UploadProgress: React.FC<UploadProgressProps> = ({
  progress,
  status,
  fileName,
  errorMessage,
}) => {
  if (status === 'idle') return null;

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">
          {fileName || 'Uploading file...'}
        </span>
        <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${
            status === 'error' ? 'bg-red-500' : 'bg-blue-500'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-3 flex items-center">
        {status === 'uploading' && (
          <>
            <Loader2 className="animate-spin h-4 w-4 text-blue-500 mr-2" />
            <span className="text-sm text-gray-600">Uploading...</span>
          </>
        )}
        
        {status === 'success' && (
          <>
            <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
            <span className="text-sm text-green-600">Upload complete!</span>
          </>
        )}
        
        {status === 'error' && (
          <>
            <XCircle className="h-4 w-4 text-red-500 mr-2" />
            <span className="text-sm text-red-600">
              {errorMessage || 'Upload failed'}
            </span>
          </>
        )}
      </div>
    </div>
  );
};