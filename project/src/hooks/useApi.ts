// Custom React hooks for API integration
import { useState, useCallback, useEffect } from 'react';
import { ApiService, ChatRequest, ChatResponse, VoiceResponse, AdminMetrics, SentimentResponse } from '../services/api';

// Hook for chat functionality
export const useChat = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);  const sendMessage = useCallback(async (request: ChatRequest): Promise<ChatResponse | null> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.sendChatMessage(request);
      return response;
    } catch (err) {
      console.error('useApi: Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { sendMessage, isLoading, error };
};

// Hook for voice functionality
export const useVoice = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadVoiceFile = useCallback(async (file: File, userId: string, language: string = 'en'): Promise<VoiceResponse | null> => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await ApiService.uploadVoiceFile(file, userId, language);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process voice file');
      return null;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const uploadVoiceStream = useCallback(async (audioData: Blob, userId: string, language: string = 'en'): Promise<VoiceResponse | null> => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await ApiService.uploadVoiceStream(audioData, userId, language);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process voice stream');
      return null;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const startLiveTranscription = useCallback(async (userId: string, language: string = 'en'): Promise<VoiceResponse | null> => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await ApiService.startLiveTranscription(userId, language);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start live transcription');
      return null;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return { uploadVoiceFile, uploadVoiceStream, startLiveTranscription, isProcessing, error };
};

// Hook for admin dashboard
export const useAdminMetrics = () => {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.getAdminMetrics();
      setMetrics(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return { metrics, isLoading, error, refetch: fetchMetrics };
};

// Hook for sentiment analysis
export const useSentiment = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeSentiment = useCallback(async (text: string): Promise<SentimentResponse | null> => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await ApiService.checkSentiment(text);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze sentiment');
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  return { analyzeSentiment, isAnalyzing, error };
};

// Hook for order status
export const useOrderStatus = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getOrderStatus = useCallback(async (userId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.getOrderStatus(userId);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get order status');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { getOrderStatus, isLoading, error };
};

// Hook for product availability
export const useProductAvailability = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkAvailability = useCallback(async (product: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.getProductAvailability(product);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check product availability');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { checkAvailability, isLoading, error };
};

// Hook for health check
export const useHealthCheck = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkHealth = useCallback(async () => {
    setIsChecking(true);
    
    try {
      await ApiService.healthCheck();
      setIsHealthy(true);
    } catch (err) {
      setIsHealthy(false);
    } finally {
      setIsChecking(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return { isHealthy, isChecking, checkHealth };
};
