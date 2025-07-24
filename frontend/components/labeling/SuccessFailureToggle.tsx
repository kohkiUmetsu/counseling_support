import React from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface SuccessFailureToggleProps {
  value: boolean | null;
  onChange: (value: boolean) => void;
}

export const SuccessFailureToggle: React.FC<SuccessFailureToggleProps> = ({
  value,
  onChange,
}) => {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Session Outcome <span className="text-red-500">*</span>
      </label>
      <div className="flex space-x-4">
        <button
          type="button"
          onClick={() => onChange(true)}
          className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg border-2 transition-all ${
            value === true
              ? 'border-green-500 bg-green-50 text-green-700'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          <ThumbsUp size={20} />
          <span className="font-medium">Success</span>
        </button>
        
        <button
          type="button"
          onClick={() => onChange(false)}
          className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg border-2 transition-all ${
            value === false
              ? 'border-red-500 bg-red-50 text-red-700'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          <ThumbsDown size={20} />
          <span className="font-medium">Failure</span>
        </button>
      </div>
    </div>
  );
};