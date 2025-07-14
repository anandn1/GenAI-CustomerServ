import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { VoiceButton } from './VoiceButton';
import { VoiceResponse } from '@/services/api';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  disabled?: boolean;
  // Voice props
  onVoiceTranscription?: (text: string) => void;
  onVoiceError?: (error: string) => void;
  onVoiceResponse?: (response: VoiceResponse) => void;
  selectedLanguage?: string;
  userId?: string;
  showVoiceButton?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  placeholder = "Ask a question or type your message...",
  disabled = false,
  onVoiceTranscription,
  onVoiceError = () => {},
  onVoiceResponse,
  selectedLanguage = 'en-US',
  userId = 'anonymous',
  showVoiceButton = true,
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleVoiceTranscription = (text: string) => {
    // For pure transcription (without full voice response), set the message
    // This is mainly for fallback scenarios
    setMessage(text);
    if (onVoiceTranscription) {
      onVoiceTranscription(text);
    }
  };

  const handleVoiceResponse = (response: VoiceResponse) => {
    // Voice response includes the complete interaction, no need to set input text
    if (onVoiceResponse) {
      onVoiceResponse(response);
    }
  };

  return (
    <div className="flex gap-3 items-end">
      <form onSubmit={handleSubmit} className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          className={cn(
            "w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-xl resize-none",
            "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:border-transparent",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "min-h-[52px] max-h-32 text-sm leading-relaxed"
          )}
          rows={1}
          style={{ height: 'auto' }}
        />
        
        <button
          type="submit"
          onClick={handleSubmit}
          disabled={!message.trim() || isLoading || disabled}
          className={cn(
            "absolute right-2 bottom-2 w-8 h-8 rounded-lg flex items-center justify-center transition-all",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-1",
            message.trim() && !isLoading && !disabled
              ? "bg-[#0071CE] text-white hover:bg-[#0071CE]/90"
              : "bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed"
          )}
          aria-label="Send message"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </form>

      {/* Voice Button - aligned to bottom */}
      {showVoiceButton && (
        <div className="flex items-end pb-2">
          <VoiceButton
            onTranscription={handleVoiceTranscription}
            onError={onVoiceError}
            onVoiceResponse={handleVoiceResponse}
            selectedLanguage={selectedLanguage}
            userId={userId}
            variant="compact"
            disabled={disabled || isLoading}
          />
        </div>
      )}
    </div>
  );
};