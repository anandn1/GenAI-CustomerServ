import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  placeholder = "Ask a question or type your message...",
  disabled = false,
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

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          className={cn(
            "w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:border-transparent",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "min-h-[52px] max-h-32 text-sm leading-relaxed"
          )}
          rows={1}
          style={{ height: 'auto' }}
        />
        
        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className={cn(
            "absolute right-2 bottom-2 w-8 h-8 rounded-lg flex items-center justify-center transition-all",
            "focus:outline-none focus:ring-2 focus:ring-[#0071CE] focus:ring-offset-1",
            message.trim() && !isLoading && !disabled
              ? "bg-[#0071CE] text-white hover:bg-[#0071CE]/90"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          )}
          aria-label="Send message"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>
    </form>
  );
};