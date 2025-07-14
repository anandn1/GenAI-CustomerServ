/// <reference path="../types/speech.d.ts" />
import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Upload, Volume2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ApiService, VoiceResponse } from '@/services/api';

interface VoiceButtonProps {
  onTranscription: (text: string) => void;
  onError: (error: string) => void;
  selectedLanguage: string;
  onVoiceResponse?: (response: VoiceResponse) => void;
  userId?: string;
  variant?: 'compact' | 'full';
  disabled?: boolean;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  onTranscription,
  onError,
  selectedLanguage,
  onVoiceResponse,
  userId = 'anonymous',
  variant = 'compact',
  disabled = false,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setRecordedBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        
        // Auto-upload in compact mode
        if (variant === 'compact') {
          await uploadBlob(audioBlob);
        }
      };

      mediaRecorder.start();
      setIsListening(true);
    } catch (error) {
      onError(`Microphone access denied: ${error}`);
    }
  }, [onError, variant]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  }, []);  const uploadBlob = useCallback(async (blob: Blob) => {
    setIsUploading(true);
    try {
      // Try using the streaming API first for better web performance
      let response;
      try {
        response = await ApiService.uploadVoiceStream(blob, userId, selectedLanguage);
      } catch (streamError) {
        // Fallback to regular file upload if streaming fails
        console.log('Streaming API failed, falling back to file upload:', streamError);
        const audioFile = new File([blob], 'recording.wav', { type: 'audio/wav' });
        response = await ApiService.uploadVoiceFile(audioFile, userId, selectedLanguage);
      }
      
      // For voice responses, we only call onVoiceResponse to handle the complete interaction
      // onTranscription is only used for showing transcription without full processing
      if (onVoiceResponse) {
        onVoiceResponse(response);
      } else {
        // Fallback to transcription only if no voice response handler
        onTranscription(response.transcript);
      }
      setRecordedBlob(null);
    } catch (error) {
      onError(`Upload failed: ${error}`);
    } finally {
      setIsUploading(false);
    }
  }, [userId, selectedLanguage, onTranscription, onVoiceResponse, onError]);
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('audio/')) {
      onError('Please select an audio file');
      return;
    }

    setIsUploading(true);
    try {
      const response = await ApiService.uploadVoiceFile(file, userId, selectedLanguage);
      
      // For voice responses, we only call onVoiceResponse to handle the complete interaction
      if (onVoiceResponse) {
        onVoiceResponse(response);
      } else {
        // Fallback to transcription only if no voice response handler
        onTranscription(response.transcript);
      }
    } catch (error) {
      onError(`Upload failed: ${error}`);
    } finally {
      setIsUploading(false);
    }
  }, [userId, selectedLanguage, onTranscription, onVoiceResponse, onError]);

  const toggleRecording = () => {
    if (isListening) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };
  if (variant === 'compact') {
    return (
      <div className="flex items-center gap-2">
        {/* Recording Button */}
        <button
          onClick={toggleRecording}
          disabled={disabled || isUploading}
          className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-200 relative",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-1",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            isListening
              ? "bg-red-500 hover:bg-red-600 text-white"
              : "bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400",
            isListening && "shadow-lg shadow-red-500/25"
          )}
          aria-label={isListening ? "Stop recording" : "Start voice recording"}
          title={isListening ? "Stop recording" : "Record voice message"}
        >
          {isUploading ? (
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          ) : isListening ? (
            <MicOff className="w-4 h-4" />
          ) : (
            <Mic className="w-4 h-4" />
          )}
          
          {isListening && (
            <div className="absolute inset-0 rounded-lg border-2 border-red-400 animate-ping opacity-75" />
          )}
        </button>

        {/* Upload Button */}
        <button
          onClick={handleUploadClick}
          disabled={disabled || isUploading || isListening}
          className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-200",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-1",
            "bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600",
            "text-gray-600 dark:text-gray-400",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
          aria-label="Upload audio file"
          title="Upload audio file"
        >
          <Upload className="w-4 h-4" />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          className="sr-only"
        />

        {/* Status Indicator - positioned to not affect button alignment */}
        {isListening && (
          <div className="flex items-center gap-1 text-xs text-red-600 dark:text-red-400 ml-1">
            <Volume2 className="w-3 h-3" />
            <span className="whitespace-nowrap">Recording...</span>
          </div>
        )}
      </div>
    );
  }
  // Full variant (original VoiceRecorder layout)
  return (
    <div className="flex flex-col items-center gap-4">
      {/* Recording Controls */}
      <div className="flex items-center justify-center gap-4">
        {/* Voice Recording Button */}
        <button
          onClick={toggleRecording}
          disabled={disabled || isUploading}
          className={cn(
            "w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 relative",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-2",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            isListening
              ? "bg-red-500 hover:bg-red-600 text-white"
              : "bg-[#0071CE] hover:bg-[#0071CE]/90 text-white",
            isListening && "shadow-lg shadow-red-500/25"
          )}
          style={{
            animation: isListening ? 'pulse 1.5s ease-in-out infinite' : 'none'
          }}
          aria-label={isListening ? "Stop recording" : "Start voice recording"}
        >
          {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
          
          {isListening && (
            <>
              {/* Pulsing ring animation */}
              <div className="absolute inset-0 rounded-full border-2 border-red-400 animate-ping opacity-75" />
              <div className="absolute inset-0 rounded-full border border-red-300 animate-pulse" />
            </>
          )}
        </button>

        {/* File Upload Button */}
        <button
          onClick={handleUploadClick}
          disabled={disabled || isUploading || isListening}
          className={cn(
            "w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200",
            "bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-2",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
          aria-label="Upload audio file"
        >
          <Upload className="w-6 h-6 text-gray-600 dark:text-gray-400" />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          className="sr-only"
        />
      </div>

      {/* Upload Recording Button (shows after recording in full mode) */}
      {recordedBlob && !isListening && variant === 'full' && (
        <div className="flex justify-center">
          <button
            onClick={() => uploadBlob(recordedBlob)}
            disabled={isUploading}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-200",
              "bg-green-500 hover:bg-green-600 text-white",
              "focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            <Volume2 className="w-5 h-5" />
            <span>Send Recording</span>
          </button>
        </div>
      )}

      {/* Status Display */}
      {isListening && (
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Volume2 className="w-4 h-4 animate-pulse" />
            <span>Recording...</span>
          </div>
        </div>
      )}

      {/* Processing indicator */}
      {isUploading && (
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          <span>Processing audio...</span>
        </div>
      )}

      {/* Instructions */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400 max-w-xs">
        <p>Click the microphone to record, or upload an audio file</p>
      </div>
    </div>
  );
};
