import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileAudio, X } from 'lucide-react';

interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  acceptedFormats?: string[];
  maxSize?: number; // in bytes
  selectedFile?: File | null;
  onClearFile?: () => void;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileSelect,
  acceptedFormats = ['.webm', '.mp3', '.wav', '.m4a'],
  maxSize = 500 * 1024 * 1024, // 500MB
  selectedFile,
  onClearFile,
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'audio/*': acceptedFormats,
    },
    maxSize,
    maxFiles: 1,
  });

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return Math.round(bytes / 1024) + ' KB';
    else return Math.round(bytes / 1048576) + ' MB';
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            {isDragActive
              ? 'Drop the audio file here'
              : 'Drag & drop an audio file here, or click to select'}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Supported formats: {acceptedFormats.join(', ')}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Maximum file size: {formatFileSize(maxSize)}
          </p>
        </div>
      ) : (
        <div className="border border-gray-300 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileAudio className="h-10 w-10 text-blue-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
            {onClearFile && (
              <button
                onClick={onClearFile}
                className="p-1 rounded-full hover:bg-gray-100"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            )}
          </div>
        </div>
      )}

      {fileRejections.length > 0 && (
        <div className="mt-2 text-sm text-red-600">
          {fileRejections[0].errors.map((error, index) => (
            <p key={index}>{error.message}</p>
          ))}
        </div>
      )}
    </div>
  );
};