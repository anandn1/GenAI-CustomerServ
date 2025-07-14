import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Settings, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ApiService, VoiceResponse } from '@/services/api';

interface LiveVoiceModeProps {
  selectedLanguage: string;
  userId: string;
  onClose: () => void;
  onTranscript?: (text: string) => void;
  onResponse?: (response: VoiceResponse) => void;
}

export const LiveVoiceMode: React.FC<LiveVoiceModeProps> = ({
  selectedLanguage,
  userId,
  onClose,
  onTranscript,
  onResponse,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [lastResponse, setLastResponse] = useState('');
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [error, setError] = useState('');
  const [voiceSettings, setVoiceSettings] = useState({
    rate: 0.9,
    pitch: 1.0,
    volume: 0.8,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopListening();
      stopSpeaking();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startListening = useCallback(async () => {
    try {
      // Stop any current speech
      stopSpeaking();

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
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
        await processAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsListening(true);
      setCurrentTranscript('Listening...');
      setError('');
    } catch (error) {
      setError(`Microphone access denied: ${error}`);
    }
  }, []);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsListening(false);
      setCurrentTranscript('Processing...');
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  const processAudio = useCallback(async (audioBlob: Blob) => {
    setIsProcessing(true);
    try {
      // Try streaming API first, fallback to file upload
      let response: VoiceResponse;
      try {
        response = await ApiService.uploadVoiceStream(audioBlob, userId, selectedLanguage);
      } catch (streamError) {
        console.log('Streaming API failed, using file upload:', streamError);
        const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
        response = await ApiService.uploadVoiceFile(audioFile, userId, selectedLanguage);
      }

      setCurrentTranscript(response.transcript);
      setLastResponse(response.answer);
      
      // Call callbacks
      onTranscript?.(response.transcript);
      onResponse?.(response);      // Speak the response if TTS is enabled
      if (ttsEnabled && response.answer) {
        speakText(formatResponse(response.answer));
      }

    } catch (error) {
      setError(`Failed to process audio: ${error}`);
      setCurrentTranscript('');
    } finally {
      setIsProcessing(false);
    }
  }, [userId, selectedLanguage, ttsEnabled, onTranscript, onResponse]);

  const speakText = useCallback((text: string) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported');
      return;
    }

    // Stop any current speech
    stopSpeaking();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = selectedLanguage;
    utterance.rate = voiceSettings.rate;
    utterance.pitch = voiceSettings.pitch;
    utterance.volume = voiceSettings.volume;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [selectedLanguage, voiceSettings]);
  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, []);

  // Format response text to remove markdown
  const formatResponse = (text: string) => {
    return text
      // Remove all markdown formatting
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
      .replace(/\*(.*?)\*/g, '$1') // Remove italics
      .replace(/#{1,6}\s*(.*?)(?=\n|$)/g, '$1') // Remove headers
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links, keep text
      .replace(/`([^`]+)`/g, '$1') // Remove code formatting
      .replace(/```[\s\S]*?```/g, '') // Remove code blocks
      .replace(/^\s*[-*+]\s+/gm, '• ') // Convert bullet points to simple bullets
      .replace(/^\s*(\d+)\.\s+/gm, '$1. ') // Keep numbered lists clean
      .replace(/^\s*>\s+/gm, '') // Remove blockquotes
      .replace(/---+/g, '──────────────────────────') // Convert dividers to simple lines
      .replace(/\n{3,}/g, '\n\n') // Remove excessive line breaks
      .trim();
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4 shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
            Live Voice Chat
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status Display */}
        <div className="text-center mb-6">
          <div className={cn(
            "w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4 transition-all duration-300",
            isListening ? "bg-red-500 animate-pulse shadow-lg shadow-red-500/25" :
            isSpeaking ? "bg-blue-500 animate-pulse shadow-lg shadow-blue-500/25" :
            isProcessing ? "bg-yellow-500 animate-spin" :
            "bg-gray-200 dark:bg-gray-700"
          )}>
            {isListening ? <Mic className="w-8 h-8 text-white" /> :
             isSpeaking ? <Volume2 className="w-8 h-8 text-white" /> :
             isProcessing ? <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" /> :
             <Mic className="w-8 h-8 text-gray-400" />}
          </div>

          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {isListening ? "Listening..." :
             isSpeaking ? "Speaking..." :
             isProcessing ? "Processing..." :
             "Ready to listen"}
          </div>

          {/* Transcript Display */}
          {currentTranscript && (
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mb-4 text-sm">
              <div className="font-medium text-gray-700 dark:text-gray-300 mb-1">You said:</div>
              <div className="text-gray-600 dark:text-gray-400">{currentTranscript}</div>
            </div>
          )}          {/* Response Display */}
          {lastResponse && (
            <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-3 mb-4 text-sm">
              <div className="font-medium text-blue-700 dark:text-blue-300 mb-1">AI Response:</div>
              <div className="text-blue-600 dark:text-blue-400 whitespace-pre-wrap">{formatResponse(lastResponse)}</div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/30 rounded-lg p-3 mb-4 text-sm">
              <div className="text-red-600 dark:text-red-400">{error}</div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 mb-6">
          {/* Main Listen Button */}
          <button
            onClick={toggleListening}
            disabled={isProcessing || isSpeaking}
            className={cn(
              "w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200",
              "focus:outline-none focus:ring-2 focus:ring-offset-2",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              isListening
                ? "bg-red-500 hover:bg-red-600 text-white focus:ring-red-500"
                : "bg-[#0071CE] hover:bg-[#0071CE]/90 text-white focus:ring-[#0071CE]"
            )}
          >
            {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
          </button>

          {/* TTS Toggle */}
          <button
            onClick={() => setTtsEnabled(!ttsEnabled)}
            className={cn(
              "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200",
              "focus:outline-none focus:ring-2 focus:ring-offset-2",
              ttsEnabled
                ? "bg-green-500 hover:bg-green-600 text-white focus:ring-green-500"
                : "bg-gray-300 hover:bg-gray-400 text-gray-600 focus:ring-gray-300"
            )}
            title={ttsEnabled ? "Disable voice responses" : "Enable voice responses"}
          >
            {ttsEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>

          {/* Stop Speaking Button */}
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              className="w-12 h-12 rounded-full flex items-center justify-center bg-orange-500 hover:bg-orange-600 text-white transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
              title="Stop speaking"
            >
              <VolumeX className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Voice Settings */}
        <div className="border-t dark:border-gray-700 pt-4">
          <div className="flex items-center gap-2 mb-3 text-sm text-gray-600 dark:text-gray-400">
            <Settings className="w-4 h-4" />
            <span>Voice Settings</span>
          </div>
          
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Speed</label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={voiceSettings.rate}
                onChange={(e) => setVoiceSettings(prev => ({ ...prev, rate: parseFloat(e.target.value) }))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Volume</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={voiceSettings.volume}
                onChange={(e) => setVoiceSettings(prev => ({ ...prev, volume: parseFloat(e.target.value) }))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-4">
          <p>Click the microphone to start talking. Release to get AI response.</p>
          <p>Toggle the speaker icon to enable/disable voice replies.</p>
        </div>
      </div>
    </div>
  );
};
