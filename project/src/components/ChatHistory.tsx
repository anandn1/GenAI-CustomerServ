import React, { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatHistoryProps {
  messages: Message[];
  isLoading: boolean;
  onMessageFeedback: (messageId: string, positive: boolean) => void;
  selectedLanguage: string;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({
  messages,
  isLoading,
  onMessageFeedback,
  selectedLanguage,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="w-16 h-16 bg-[#0071CE] rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl text-white">💬</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to Walmart Whisper</h2>
          <p className="text-gray-600 text-sm leading-relaxed">
            I'm here to help you with your questions. You can type your message below or use the microphone button to speak.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="space-y-2">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.text}
            isUser={message.isUser}
            timestamp={message.timestamp}
            language={selectedLanguage}
            onFeedback={message.isUser ? undefined : (positive) => onMessageFeedback(message.id, positive)}
          />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        <div ref={bottomRef} />
      </div>
    </div>
  );
};