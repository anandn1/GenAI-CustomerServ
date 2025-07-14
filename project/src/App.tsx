import { useState, useCallback, useEffect } from 'react';
import { ChatHistory } from './components/ChatHistory';
import { ChatInput } from './components/ChatInput';
import { VoiceButton } from './components/VoiceButton';
import { LiveVoiceMode } from './components/LiveVoiceMode';
import { LanguageSelector } from './components/LanguageSelector';
import { EscalationBanner } from './components/EscalationBanner';
import { QuickActions } from './components/QuickActions';
import { AdminDashboard } from './components/AdminDashboard';
import { MessageSquare, Mic, Sparkles, BarChart3, Moon, Sun, Wifi, WifiOff, Radio } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useChat, useVoice, useSentiment, useHealthCheck } from './hooks/useApi';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isVoiceMessage?: boolean;
}

type Mode = 'chat' | 'voice' | 'live-voice';
type Theme = 'light' | 'dark';

function App() {
  // Core state
  const [messages, setMessages] = useState<Message[]>([]);  const [mode, setMode] = useState<Mode>('chat');
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [error, setError] = useState('');

  // Enhanced UX state
  const [showEscalation, setShowEscalation] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);  const [theme, setTheme] = useState<Theme>('light');
  const [negativeFeedbackCount, setNegativeFeedbackCount] = useState(0);
  const [totalInteractions, setTotalInteractions] = useState(0);
  const [userId] = useState(() => `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [chatHistory, setChatHistory] = useState<any[]>([]);  // API hooks
  const { sendMessage, isLoading: isChatLoading, error: chatError } = useChat();
  const { error: voiceError } = useVoice();
  const { analyzeSentiment } = useSentiment();
  const { isHealthy, isChecking } = useHealthCheck();

  // Theme toggle handler
  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark');
    }
  }, []);

  // Unified error state
  useEffect(() => {
    if (chatError) setError(chatError);
    if (voiceError) setError(voiceError);
  }, [chatError, voiceError]);
  const addMessage = useCallback((text: string, isUser: boolean, isVoiceMessage = false) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser,
      timestamp: new Date(),
      isVoiceMessage,
    };
    setMessages(prev => [...prev, newMessage]);
    setTotalInteractions(prev => prev + 1);
  }, []);const handleAIResponse = useCallback(async (userMessage: string) => {
    // Hide quick actions after first interaction
    if (showQuickActions && messages.length === 0) {
      setShowQuickActions(false);
    }
    
    try {
      const response = await sendMessage({
        user_id: userId,
        message: userMessage,
        chat_history: chatHistory,
        language: selectedLanguage.split('-')[0], // Convert 'en-US' to 'en'
      });
      
      if (response && response.answer) {
        addMessage(response.answer, false);
        setChatHistory(response.chat_history || []);
        
        // Check sentiment for escalation
        const sentiment = await analyzeSentiment(userMessage);
        if (sentiment && sentiment.sentiment === 'negative') {
          setNegativeFeedbackCount(prev => {
            const newCount = prev + 1;
            if (newCount >= 2) {
              setShowEscalation(true);
            }
            return newCount;
          });
        }
      } else {
        setError('Received empty response from AI. Please try again.');
      }
    } catch (err) {
      console.error('Error in handleAIResponse:', err);
      setError('Failed to get response from AI. Please try again.');
    }
  }, [addMessage, messages.length, showQuickActions, sendMessage, userId, chatHistory, selectedLanguage, analyzeSentiment]);
  const handleSendMessage = useCallback((message: string) => {
    if (!message.trim()) return;
    
    // Clear any previous errors
    setError('');
    
    addMessage(message, true);
    handleAIResponse(message);
  }, [addMessage, handleAIResponse]);  const handleVoiceTranscription = useCallback(async (text: string) => {
    // This function is now mainly used for fallback scenarios where only transcription is available
    // The main voice flow uses handleVoiceResponse which includes both transcript and answer
    if (text.trim()) {
      addMessage(text, true);
      handleAIResponse(text);
    }
  }, [addMessage, handleAIResponse]);
  const handleVoiceError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    setTimeout(() => setError(''), 5000);
  }, []);  const handleVoiceResponse = useCallback((response: any) => {
    // Add the user's voice transcript to the chat first
    if (response.transcript && response.transcript.trim()) {
      addMessage(response.transcript, true, true); // true for isVoiceMessage
    }
    
    // Then add the AI's response to the chat
    if (response.answer && response.answer.trim()) {
      addMessage(response.answer, false);
    }
    
    // Update chat history
    setChatHistory(response.chat_history);
    
    // Check sentiment for escalation if needed
    if (response.category === 'negative') {
      setNegativeFeedbackCount(prev => {
        const newCount = prev + 1;
        if (newCount >= 2) {
          setShowEscalation(true);
        }
        return newCount;
      });
    }
  }, [addMessage]);

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
    <div className={cn("min-h-screen flex flex-col", theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50') + ' ' + (theme === 'dark' ? 'dark' : '')}>
      {/* Header */}
      <header className={cn("border-b px-4 py-3", theme === 'dark' ? 'bg-gray-950 border-gray-800' : 'bg-white border-gray-200')}>
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#0071CE] rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className={cn("text-xl font-semibold", theme === 'dark' ? 'text-gray-100' : 'text-gray-800')}>Walmart Whisper</h1>
              <p className={cn("text-sm", theme === 'dark' ? 'text-gray-400' : 'text-gray-600')}>AI Assistant</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Health Status Indicator */}
            <div className="flex items-center gap-1">
              {isHealthy ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-red-500" />
              )}
              <span className={cn("text-xs", theme === 'dark' ? 'text-gray-400' : 'text-gray-600')}>
                {isChecking ? 'Checking...' : isHealthy ? 'Online' : 'Offline'}
              </span>
            </div>
            
            <button
              onClick={() => setShowAdminDashboard(true)}
              className={cn(
                'p-2 rounded-lg transition-colors',
                theme === 'dark' ? 'text-gray-400 hover:text-blue-300 hover:bg-gray-800' : 'text-gray-600 hover:text-[#0071CE] hover:bg-gray-100'
              )}
              aria-label="Open admin dashboard"
            >
              <BarChart3 className="w-5 h-5" />
            </button>
            
            <button
              onClick={toggleTheme}
              className={cn(
                'p-2 rounded-lg border transition-colors',
                theme === 'dark' ? 'bg-gray-800 border-gray-700 text-yellow-300 hover:bg-gray-700' : 'bg-gray-100 border-gray-200 text-gray-700 hover:bg-gray-200'
              )}
              aria-label="Toggle dark mode"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            
            <LanguageSelector 
              selectedLanguage={selectedLanguage} 
              onLanguageChange={setSelectedLanguage} 
            />
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className={cn("border-l-4 p-4 mx-4 mt-4 rounded", theme === 'dark' ? 'bg-red-900 border-red-700' : 'bg-red-50 border-red-400')}>
          <div className="flex">
            <div className="ml-3">
              <p className={cn("text-sm", theme === 'dark' ? 'text-red-200' : 'text-red-700')}>{error}</p>
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
      />      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full min-h-0">
        {/* Chat History */}
        <div className="flex-1 min-h-0 px-4 overflow-hidden">
          <ChatHistory
            messages={messages}
            isLoading={isChatLoading}
            onMessageFeedback={handleMessageFeedback}
            selectedLanguage={selectedLanguage}
          />
        </div>        {/* Mode Toggle */}
        <div className={cn("px-4 py-3 border-t", theme === 'dark' ? 'bg-gray-950 border-gray-800' : 'bg-white border-gray-200')}>
          <div className="flex items-center justify-center gap-2 mb-4">
            <button
              onClick={() => setMode('chat')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                mode === 'chat'
                  ? 'bg-[#0071CE] text-white'
                  : (theme === 'dark' ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')
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
                  ? 'bg-[#0071CE] text-white'
                  : (theme === 'dark' ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')
              )}
            >
              <Mic className="w-4 h-4" />
              Voice Mode
            </button>

            <button
              onClick={() => setMode('live-voice')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                mode === 'live-voice'
                  ? 'bg-[#0071CE] text-white'
                  : (theme === 'dark' ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')
              )}
            >
              <Radio className="w-4 h-4" />
              Live Voice
            </button>
          </div>{/* Input Area */}
          <div className="flex items-end gap-4">
            {mode === 'chat' ? (
              <div className="flex-1">
                <ChatInput
                  onSendMessage={handleSendMessage}
                  isLoading={isChatLoading}
                  placeholder="Ask a question or type your message..."
                  onVoiceTranscription={handleVoiceTranscription}
                  onVoiceError={handleVoiceError}
                  onVoiceResponse={handleVoiceResponse}
                  selectedLanguage={selectedLanguage}
                  userId={userId}
                />
              </div>
            ) : mode === 'voice' ? (
              <div className="flex-1 flex justify-center items-end">
                <VoiceButton
                  variant="full"
                  onTranscription={handleVoiceTranscription}
                  onError={handleVoiceError}
                  onVoiceResponse={handleVoiceResponse}
                  selectedLanguage={selectedLanguage}
                  userId={userId}
                />
              </div>
            ) : (
              <div className="flex-1">
                <LiveVoiceMode
                  selectedLanguage={selectedLanguage}
                  userId={userId}
                  onClose={() => setMode('chat')}
                  onTranscript={(text) => {
                    addMessage(text, true, true);
                  }}
                  onResponse={(response) => {
                    handleVoiceResponse(response);
                  }}
                />
              </div>
            )}
          </div>
        </div>      </main>

      {/* Footer */}
      <footer className={cn("border-t px-4 py-3 text-center", theme === 'dark' ? 'bg-gray-950 border-gray-800' : 'bg-white border-gray-200')}>
        <p className={cn("text-xs", theme === 'dark' ? 'text-gray-500' : 'text-gray-500')}>
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
