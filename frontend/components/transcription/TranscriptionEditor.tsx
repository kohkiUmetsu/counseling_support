import React, { useState, useRef, useEffect } from 'react';
import { Save, X } from 'lucide-react';

interface TranscriptionEditorProps {
  initialText: string;
  onSave: (newText: string) => void;
  onCancel: () => void;
}

export const TranscriptionEditor: React.FC<TranscriptionEditorProps> = ({
  initialText,
  onSave,
  onCancel,
}) => {
  const [text, setText] = useState(initialText);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Focus and select text when editor opens
    if (textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, []);

  const handleSave = () => {
    const trimmedText = text.trim();
    if (trimmedText && trimmedText !== initialText) {
      onSave(trimmedText);
    } else {
      onCancel();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onCancel();
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [text]);

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Edit Transcription Segment
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleSave}
              className="flex items-center space-x-1 px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition-colors text-sm"
              title="Save (Ctrl+Enter)"
            >
              <Save size={14} />
              <span>Save</span>
            </button>
            <button
              onClick={onCancel}
              className="flex items-center space-x-1 px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors text-sm"
              title="Cancel (Esc)"
            >
              <X size={14} />
              <span>Cancel</span>
            </button>
          </div>
        </div>
        
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none overflow-hidden"
          placeholder="Enter transcription text..."
          rows={1}
        />
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>
            Press Ctrl+Enter to save, Esc to cancel
          </span>
          <span>
            {text.length} characters
          </span>
        </div>
      </div>
    </div>
  );
};