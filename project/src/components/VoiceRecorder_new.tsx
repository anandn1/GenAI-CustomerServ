/// <reference path="../types/speech.d.ts" />
import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VoiceRecorderProps {
  onTranscription: (text: string) => void;
  onError: (error: string) => void;
  isListening: boolean;
  setIsListening: (listening: boolean) => void;
  selectedLanguage: string;
  onTranscriptUpdate?: (transcript: string) => void;
  isProcessing?: boolean;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscription,
  onError,
  isListening,
  setIsListening,
  selectedLanguage,
  onTranscriptUpdate,
  isProcessing = false,
}) => {
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  const startListening = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      onError('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = selectedLanguage;

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('');
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      setTranscript(finalTranscript + interimTranscript);
      onTranscriptUpdate?.(finalTranscript + interimTranscript);
      
      if (finalTranscript) {
        onTranscription(finalTranscript);
        stopListening();
      }
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onerror = (event: any) => {
      onError(`Speech recognition error: ${event.error}`);
      stopListening();
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [selectedLanguage, onTranscription, onError, setIsListening, onTranscriptUpdate]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, [setIsListening]);

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Live Recording Button */}
      <button
        onClick={toggleListening}
        disabled={isProcessing}
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
      
      {/* Live transcription display */}
      {isListening && (
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Volume2 className="w-4 h-4" />
            <span>Listening...</span>
          </div>
          {transcript && (
            <div className="max-w-xs text-center text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded">
              <span className="animate-pulse">"{transcript}"</span>
            </div>
          )}
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          <span>Processing...</span>
        </div>
      )}
    </div>
  );
};
