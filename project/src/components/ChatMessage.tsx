import React from 'react';
import { User, Bot, ThumbsUp, ThumbsDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { VoiceResponsePlayer } from './VoiceResponsePlayer';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
  onFeedback?: (positive: boolean) => void;
  language?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  timestamp,
  onFeedback,
  language = 'en-US',
}) => {
  const [feedbackGiven, setFeedbackGiven] = React.useState(false);
  const [feedbackType, setFeedbackType] = React.useState<'positive' | 'negative' | null>(null);

  const handleFeedback = (positive: boolean) => {
    setFeedbackGiven(true);
    setFeedbackType(positive ? 'positive' : 'negative');
    onFeedback?.(positive);
  };

  return (
    <div className={cn(
      "flex gap-3 max-w-4xl mx-auto p-4",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
        isUser ? "bg-[#0071CE] text-white" : "bg-gray-100 text-gray-600"
      )}>
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      
      <div className={cn(
        "max-w-[75%] space-y-2",
        isUser ? "text-right" : "text-left"
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser 
            ? "bg-[#0071CE] text-white rounded-tr-sm" 
            : "bg-gray-100 text-gray-800 rounded-tl-sm"
        )}>
          {message}
        </div>
        
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          
          {!isUser && (
            <VoiceResponsePlayer text={message} language={language} />
          )}
          
          {!isUser && onFeedback && (
            <div className="flex items-center gap-1 ml-1">
              {!feedbackGiven && (
                <span className="text-xs text-gray-400 mr-1">Was this helpful?</span>
              )}
              <button
                onClick={() => handleFeedback(true)}
                disabled={feedbackGiven}
                className={cn(
                  "p-1 rounded hover:bg-gray-200 transition-colors",
                  feedbackGiven && feedbackType === 'positive' ? "text-green-600 bg-green-50" : "",
                  feedbackGiven && feedbackType !== 'positive' ? "opacity-50 cursor-not-allowed" : "hover:text-green-600"
                )}
                aria-label="Helpful response"
              >
                <ThumbsUp className="w-3 h-3" />
              </button>
              <button
                onClick={() => handleFeedback(false)}
                disabled={feedbackGiven}
                className={cn(
                  "p-1 rounded hover:bg-gray-200 transition-colors",
                  feedbackGiven && feedbackType === 'negative' ? "text-red-600 bg-red-50" : "",
                  feedbackGiven && feedbackType !== 'negative' ? "opacity-50 cursor-not-allowed" : "hover:text-red-600"
                )}
                aria-label="Not helpful response"
              >
                <ThumbsDown className="w-3 h-3" />
              </button>
            </div>
          )}
          
          {feedbackGiven && (
            <span className="text-xs text-gray-400 ml-2">
              Thank you for your feedback!
            </span>
          )}
        </div>
      </div>
    </div>
  );
};