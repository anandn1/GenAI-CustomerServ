/// <reference path="../types/speech.d.ts" />
import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Upload, Volume2, FileAudio } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ApiService, VoiceResponse } from '@/services/api';

interface VoiceRecorderProps {
  onTranscription: (text: string) => void;
  onError: (error: string) => void;
  isListening: boolean;
  setIsListening: (listening: boolean) => void;
  selectedLanguage: string;
  onTranscriptUpdate?: (transcript: string) => void;
  isProcessing?: boolean;
  onVoiceResponse?: (response: VoiceResponse) => void;
  userId?: string;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscription,
  onError,
  isListening,
  setIsListening,
  selectedLanguage,
  onTranscriptUpdate,
  isProcessing = false,
  onVoiceResponse,
  userId = 'anonymous',
}) => {
  const [transcript, setTranscript] = useState('');
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
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

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setRecordedBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsListening(true);
      setTranscript('Recording...');
      onTranscriptUpdate?.('Recording...');
    } catch (error) {
      onError(`Microphone access denied: ${error}`);
    }
  }, [setIsListening, onError, onTranscriptUpdate]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsListening(false);
      setTranscript('');
    }
  }, [setIsListening]);

  const uploadRecording = useCallback(async () => {
    if (!recordedBlob) {
      onError('No recording to upload');
      return;
    }

    setIsUploading(true);
    try {
      const audioFile = new File([recordedBlob], 'recording.wav', { type: 'audio/wav' });
      const response = await ApiService.uploadVoiceFile(audioFile, userId, selectedLanguage);
      
      onTranscription(response.transcript);
      onVoiceResponse?.(response);
      setRecordedBlob(null); // Clear the recording
    } catch (error) {
      onError(`Upload failed: ${error}`);
    } finally {
      setIsUploading(false);
    }
  }, [recordedBlob, userId, selectedLanguage, onTranscription, onVoiceResponse, onError]);

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
      onTranscription(response.transcript);
      onVoiceResponse?.(response);
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
  return (
    <div className="flex flex-col items-center gap-4">
      {/* Recording Controls */}
      <div className="flex items-center gap-4">
        {/* Voice Recording Button */}
        <button
          onClick={toggleRecording}
          disabled={isProcessing || isUploading}
          className={cn(
            "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 relative",
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
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          
          {isListening && (
            <>
              {/* Pulsing ring animation */}
              <div className="absolute inset-0 rounded-full border-2 border-red-400 animate-ping opacity-75" />
              <div className="absolute inset-0 rounded-full border border-red-300 animate-pulse" />
            </>
          )}
        </button>

        {/* File Upload Button */}
        <label className={cn(
          "w-12 h-12 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200",
          "bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600",
          "focus-within:ring-2 focus-within:ring-[#0071CE] focus-within:ring-offset-2",
          (isProcessing || isUploading) && "opacity-50 cursor-not-allowed"
        )}>
          <Upload className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            disabled={isProcessing || isUploading}
            className="sr-only"
            aria-label="Upload audio file"
          />
        </label>
      </div>

      {/* Upload Recording Button (shows after recording) */}
      {recordedBlob && !isListening && (
        <button
          onClick={uploadRecording}
          disabled={isUploading}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200",
            "bg-green-500 hover:bg-green-600 text-white",
            "focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <FileAudio className="w-4 h-4" />
          <span>Upload Recording</span>
        </button>
      )}

      {/* Status Display */}
      {isListening && (
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Volume2 className="w-4 h-4" />
            <span>Recording...</span>
          </div>
          {transcript && transcript !== 'Recording...' && (
            <div className="max-w-xs text-center text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded">
              <span className="animate-pulse">"{transcript}"</span>
            </div>
          )}
        </div>
      )}

      {/* Processing indicator */}
      {(isProcessing || isUploading) && (
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          <span>{isUploading ? 'Uploading...' : 'Processing...'}</span>
        </div>
      )}

      {/* Instructions */}
      <div className="text-center text-xs text-gray-500 dark:text-gray-400 max-w-xs">
        <p>Click the microphone to record, or upload an audio file</p>
      </div>
    </div>
  );
};
