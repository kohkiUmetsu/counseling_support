import React from 'react';
import { User, MessageSquare } from 'lucide-react';

interface MetadataFormProps {
  counselorName: string;
  onCounselorNameChange: (value: string) => void;
  comment: string;
  onCommentChange: (value: string) => void;
}

export const MetadataForm: React.FC<MetadataFormProps> = ({
  counselorName,
  onCounselorNameChange,
  comment,
  onCommentChange,
}) => {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="counselor-name" className="block text-sm font-medium text-gray-700 mb-1">
          <span className="flex items-center space-x-1">
            <User size={16} />
            <span>カウンセラー名 <span className="text-red-500">*</span></span>
          </span>
        </label>
        <input
          type="text"
          id="counselor-name"
          value={counselorName}
          onChange={(e) => onCounselorNameChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="カウンセラー名を入力してください"
          required
        />
      </div>

      <div>
        <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-1">
          <span className="flex items-center space-x-1">
            <MessageSquare size={16} />
            <span>コメント（任意）</span>
          </span>
        </label>
        <textarea
          id="comment"
          value={comment}
          onChange={(e) => onCommentChange(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          placeholder="このセッションに関する関連する注記や観察事項を追加してください..."
        />
        <p className="text-xs text-gray-500 mt-1">
          {comment.length}/500 文字
        </p>
      </div>
    </div>
  );
};