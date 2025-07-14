import React, { useState, useRef } from 'react';
import { Volume2, Pause } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VoiceResponsePlayerProps {
  text: string;
  language: string;
}

export const VoiceResponsePlayer: React.FC<VoiceResponsePlayerProps> = ({
  text,
  language,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  React.useEffect(() => {
    if (!('speechSynthesis' in window)) {
      setIsSupported(false);
    }
  }, []);

  const handlePlayPause = () => {
    if (!isSupported) return;

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language;
      utterance.rate = 0.9;
      utterance.pitch = 1;
      
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      
      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
  };

  if (!isSupported) return null;

  return (
    <button
      onClick={handlePlayPause}
      className={cn(
        "p-1 rounded hover:bg-gray-200 transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-1",
        isPlaying ? "text-[#0071CE]" : "text-gray-500 hover:text-gray-700"
      )}
      aria-label={isPlaying ? "Stop voice playback" : "Play voice response"}
      title={isPlaying ? "Stop voice playback" : "Play voice response"}
    >
      {isPlaying ? (
        <Pause className="w-3 h-3" />
      ) : (
        <Volume2 className="w-3 h-3" />
      )}
    </button>
  );
};