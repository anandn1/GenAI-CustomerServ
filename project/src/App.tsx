import React, { useState, useCallback } from 'react';
import { ChatHistory } from './components/ChatHistory';
import { ChatInput } from './components/ChatInput';
import { VoiceRecorder } from './components/VoiceRecorder';
import { LanguageSelector } from './components/LanguageSelector';
import { EscalationBanner } from './components/EscalationBanner';
import { QuickActions } from './components/QuickActions';
import { AdminDashboard } from './components/AdminDashboard';
import { MessageSquare, Mic, Sparkles, BarChart3, Moon, Sun } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

type Mode = 'chat' | 'voice';

function App() {
  // Core state
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<Mode>('chat');
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState('');

  // Enhanced UX state
  const [showEscalation, setShowEscalation] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [negativeFeedbackCount, setNegativeFeedbackCount] = useState(0);
  const [totalInteractions, setTotalInteractions] = useState(0);

  const addMessage = useCallback((text: string, isUser: boolean) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    setTotalInteractions(prev => prev + 1);
  }, []);

  const simulateAIResponse = useCallback(async (userMessage: string) => {
    setIsLoading(true);
    
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    // Hide quick actions after first interaction
    if (showQuickActions && messages.length === 0) {
      setShowQuickActions(false);
    }
    
    const responses = [
      "I'd be happy to help you with that! Let me check our current inventory and policies for you.",
      "That's a great question! Based on Walmart's current offerings, here's what I can tell you...",
      "I understand your concern. Let me provide you with the most up-to-date information about this.",
      "Thank you for choosing Walmart! I can help you find exactly what you're looking for.",
      "I'll connect you with the right information. Here's what I found about your inquiry...",
    ];
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    addMessage(randomResponse, false);
    setIsLoading(false);
  }, [addMessage, messages.length, showQuickActions]);

  const handleSendMessage = useCallback((message: string) => {
    if (!message.trim()) return;
    
    addMessage(message, true);
    simulateAIResponse(message);
  }, [addMessage, simulateAIResponse]);

  const handleVoiceTranscription = useCallback((text: string) => {
    if (text.trim()) {
      handleSendMessage(text);
    }
  }, [handleSendMessage]);

  const handleVoiceError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    setTimeout(() => setError(''), 5000);
  }, []);

  const handleMessageFeedback = useCallback((messageId: string, positive: boolean) => {
    if (!positive) {
      setNegativeFeedbackCount(prev => {
        const newCount = prev + 1;
        // Trigger escalation after 2 negative feedbacks
        if (newCount >= 2) {
          setShowEscalation(true);
        }
        return newCount;
      });
    }
    console.log(`Message ${messageId} feedback: ${positive ? 'positive' : 'negative'}`);
  }, []);

  const handleQuickAction = useCallback((query: string) => {
    handleSendMessage(query);
    setShowQuickActions(false);
  }, [handleSendMessage]);

  const mockAdminStats = {
    totalChats: totalInteractions,
    activeUsers: 24,
    avgResponseTime: '1.2s',
    satisfactionRate: Math.max(60, 100 - (negativeFeedbackCount * 20)),
    escalations: negativeFeedbackCount,
    topLanguages: [{ lang: 'English', count: 45 }, { lang: 'Spanish', count: 23 }]
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#0071CE] rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">Walmart Whisper</h1>
              <p className="text-sm text-gray-600">AI Assistant</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowAdminDashboard(true)}
              className="p-2 text-gray-600 hover:text-[#0071CE] hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Open admin dashboard"
            >
              <BarChart3 className="w-5 h-5" />
            </button>
            
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 text-gray-600 hover:text-[#0071CE] hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            
            <LanguageSelector selectedLanguage={selectedLanguage} onLanguageChange={setSelectedLanguage} />
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-4 mt-4 rounded">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Escalation Banner */}
      <EscalationBanner
        isVisible={showEscalation}
        onClose={() => setShowEscalation(false)}
      />

      {/* Quick Actions */}
      <QuickActions
        isVisible={showQuickActions && messages.length === 0}
        onActionClick={handleQuickAction}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Chat History */}
        <div className="flex-1 min-h-0">
          <ChatHistory
            messages={messages}
            isLoading={isLoading}
            onMessageFeedback={handleMessageFeedback}
            selectedLanguage={selectedLanguage}
          />
        </div>

        {/* Mode Toggle */}
        <div className="px-4 py-3 border-t border-gray-200 bg-white">
          <div className="flex items-center justify-center gap-2 mb-4">
            <button
              onClick={() => setMode('chat')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                mode === 'chat'
                  ? "bg-[#0071CE] text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              <MessageSquare className="w-4 h-4" />
              Chat Mode
            </button>
            
            <button
              onClick={() => setMode('voice')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                mode === 'voice'
                  ? "bg-[#0071CE] text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              <Mic className="w-4 h-4" />
              Voice Mode
            </button>
          </div>

          {/* Input Area */}
          <div className="flex items-center gap-4">
            {mode === 'chat' ? (
              <div className="flex-1">
                <ChatInput
                  onSendMessage={handleSendMessage}
                  isLoading={isLoading}
                  placeholder="Ask a question or type your message..."
                />
              </div>
            ) : (
              <div className="flex-1 flex justify-center">
                <VoiceRecorder
                  onTranscription={handleVoiceTranscription}
                  onError={handleVoiceError}
                  isListening={isListening}
                  setIsListening={setIsListening}
                  selectedLanguage={selectedLanguage}
                  onTranscriptUpdate={setCurrentTranscript}
                  onTranscriptUpdate={setCurrentTranscript}
                />
              </div>
            )}
            
            {mode === 'chat' && (
              <VoiceRecorder
                onTranscription={handleVoiceTranscription}
                onError={handleVoiceError}
                isListening={isListening}
                setIsListening={setIsListening}
                selectedLanguage={selectedLanguage}
              />
            )}
          </div>
        </div>
      </main>

      {/* Real-time Transcription Display */}
      {isListening && currentTranscript && (
        <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-white border border-gray-200 rounded-lg shadow-lg p-3 max-w-md mx-4 z-10">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-xs font-medium text-gray-600">Live Transcription</span>
          </div>
          <p className="text-sm text-gray-800">"{currentTranscript}"</p>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-4 py-3 text-center">
        <p className="text-xs text-gray-500">
          Walmart Whisper - AI Assistant • Powered by advanced language models
        </p>
      </footer>

      {/* Admin Dashboard Modal */}
      <AdminDashboard
        isVisible={showAdminDashboard}
        onClose={() => setShowAdminDashboard(false)}
        stats={mockAdminStats}
      />
    </div>
  );
}

export default App;