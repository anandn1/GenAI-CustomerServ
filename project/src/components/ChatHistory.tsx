import React, { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isVoiceMessage?: boolean;
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
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="text-center max-w-lg mx-auto">
          <div className="w-20 h-20 bg-[#0071CE] rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <span className="text-3xl text-white">💬</span>
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-4">
            Welcome to Walmart Whisper
          </h2>
          <p className="text-gray-600 dark:text-gray-300 text-base leading-relaxed mb-6">
            I'm here to help you with your questions. You can type your message below or use the microphone button to speak.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-center text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>AI Assistant Ready</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Voice & Text Support</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="space-y-4 py-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.text}
            isUser={message.isUser}
            timestamp={message.timestamp}
            language={selectedLanguage}
            isVoiceMessage={message.isVoiceMessage}
            onFeedback={message.isUser ? undefined : (positive) => onMessageFeedback(message.id, positive)}
          />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        <div ref={bottomRef} />
      </div>
    </div>
  );
};