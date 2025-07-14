import React from 'react';
import { User, Bot, ThumbsUp, ThumbsDown, Mic } from 'lucide-react';
import { cn } from '@/lib/utils';
import { VoiceResponsePlayer } from './VoiceResponsePlayer';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
  onFeedback?: (positive: boolean) => void;
  language?: string;
  isVoiceMessage?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  timestamp,
  onFeedback,
  language = 'en-US',
  isVoiceMessage = false,
}) => {
  const [feedbackGiven, setFeedbackGiven] = React.useState(false);
  const [feedbackType, setFeedbackType] = React.useState<'positive' | 'negative' | null>(null);

  const handleFeedback = (positive: boolean) => {
    setFeedbackGiven(true);
    setFeedbackType(positive ? 'positive' : 'negative');
    onFeedback?.(positive);
  };
  // Format message for better display - remove all markdown formatting
  const formatMessage = (text: string) => {
    if (isUser) return text; // Don't format user messages
    
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

  return (
    <div className={cn(
      "flex gap-3 max-w-4xl mx-auto px-4 py-2",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
        isUser ? "bg-[#0071CE] text-white" : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
      )}>
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      
      <div className={cn(
        "max-w-[85%] space-y-2",
        isUser ? "text-right" : "text-left"
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words",
          isUser 
            ? cn(
                "text-white rounded-tr-sm",
                isVoiceMessage 
                  ? "bg-gradient-to-r from-[#0071CE] to-[#004f91]" // Gradient for voice messages
                  : "bg-[#0071CE]" // Solid color for text messages
              )
            : "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-100 rounded-tl-sm"
        )}>
          {formatMessage(message)}
        </div>
        
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span>{timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          
          {/* Voice message indicator */}
          {isUser && isVoiceMessage && (
            <div className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500" title="Voice message">
              <Mic className="w-3 h-3" />
              <span>Voice</span>
            </div>
          )}
          
          {!isUser && (
            <VoiceResponsePlayer text={message} language={language} />
          )}
          
          {!isUser && onFeedback && (
            <div className="flex items-center gap-1 ml-1">
              {!feedbackGiven && (
                <span className="text-xs text-gray-400 dark:text-gray-500 mr-1">Was this helpful?</span>
              )}
              <button
                onClick={() => handleFeedback(true)}
                disabled={feedbackGiven}
                className={cn(
                  "p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors",
                  feedbackGiven && feedbackType === 'positive' ? "text-green-600 bg-green-50 dark:bg-green-900/30" : "",
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
                  "p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors",
                  feedbackGiven && feedbackType === 'negative' ? "text-red-600 bg-red-50 dark:bg-red-900/30" : "",
                  feedbackGiven && feedbackType !== 'negative' ? "opacity-50 cursor-not-allowed" : "hover:text-red-600"
                )}
                aria-label="Not helpful response"
              >
                <ThumbsDown className="w-3 h-3" />
              </button>
            </div>
          )}
          
          {feedbackGiven && (
            <span className="text-xs text-gray-400 dark:text-gray-500 ml-2">
              Thank you for your feedback!
            </span>
          )}
        </div>
      </div>
    </div>
  );
};