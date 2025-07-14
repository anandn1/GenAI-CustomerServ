// API service for Walmart Whisper backend integration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatRequest {
  user_id: string;
  message: string;
  chat_history?: any[];
  language?: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  category: string;
  chat_history: any[];
}

export interface VoiceResponse {
  transcript: string;
  answer: string;
  sources: string[];
  category: string;
  chat_history: any[];
}

export interface AdminMetrics {
  total_chats: number;
  escalations: number;
  avg_response_time: number;
  active_sessions: number;
}

export interface SentimentResponse {
  sentiment: string;
  justification: string;
}

export class ApiService {
  private static baseUrl = API_BASE_URL;

  // Helper function to format message with language context
  private static formatMessageWithLanguage(message: string, language?: string): string {
    if (!language || language === 'en-US' || language === 'en') {
      return message;
    }

    const languageMap: { [key: string]: string } = {
      'es-ES': 'Spanish',
      'fr-FR': 'French',
      'de-DE': 'German',
      'it-IT': 'Italian',
      'pt-BR': 'Portuguese',
      'zh-CN': 'Chinese',
      'ja-JP': 'Japanese',
      'ko-KR': 'Korean',
      'ar-SA': 'Arabic',
      'hi-IN': 'Hindi'
    };

    const languageName = languageMap[language] || language;
    return `[Language: ${languageName}] ${message}`;
  }  // Chat API
  static async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    // Format the message with language context
    const formattedRequest = {
      ...request,
      message: this.formatMessageWithLanguage(request.message, request.language)
    };

    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formattedRequest),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Chat API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data;
  }

  // Voice file upload API
  static async uploadVoiceFile(file: File, userId: string, language: string = 'en'): Promise<VoiceResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('language', language);

    const response = await fetch(`${this.baseUrl}/api/voice`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Voice API error: ${response.status}`);
    }

    return response.json();
  }

  // Live voice transcription API (for desktop/CLI)
  static async startLiveTranscription(userId: string, language: string = 'en'): Promise<VoiceResponse> {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('language', language);

    const response = await fetch(`${this.baseUrl}/api/voice-live`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Live voice API error: ${response.status}`);
    }

    return response.json();
  }

  // Direct document retrieval API
  static async retrieveDocuments(query: string): Promise<{ documents: string[] }> {
    const response = await fetch(`${this.baseUrl}/api/langchain/retrieve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Retrieve API error: ${response.status}`);
    }

    return response.json();
  }

  // Mock order status API
  static async getOrderStatus(userId: string): Promise<{ user_id: string; order_status: string; order_id: string }> {
    const response = await fetch(`${this.baseUrl}/api/order-status/${userId}`);

    if (!response.ok) {
      throw new Error(`Order status API error: ${response.status}`);
    }

    return response.json();
  }

  // Mock product availability API
  static async getProductAvailability(product: string): Promise<{ product: string; available: boolean; stores: string[] }> {
    const params = new URLSearchParams({ product });
    const response = await fetch(`${this.baseUrl}/api/product-availability?${params}`);

    if (!response.ok) {
      throw new Error(`Product availability API error: ${response.status}`);
    }

    return response.json();
  }

  // Sentiment check API
  static async checkSentiment(text: string): Promise<SentimentResponse> {
    const response = await fetch(`${this.baseUrl}/api/sentiment-check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Sentiment API error: ${response.status}`);
    }

    return response.json();
  }

  // Admin metrics API
  static async getAdminMetrics(): Promise<AdminMetrics> {
    const response = await fetch(`${this.baseUrl}/api/admin/metrics`);

    if (!response.ok) {
      throw new Error(`Admin metrics API error: ${response.status}`);
    }

    return response.json();
  }

  // Health check API
  static async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);

    if (!response.ok) {
      throw new Error(`Health check API error: ${response.status}`);
    }

    return response.json();
  }

  // Voice streaming API (optimized for web)
  static async uploadVoiceStream(audioData: Blob, userId: string, language: string = 'en'): Promise<VoiceResponse> {
    const formData = new FormData();
    formData.append('audio_data', audioData, 'audio.wav');
    formData.append('user_id', userId);
    formData.append('language', language);

    const response = await fetch(`${this.baseUrl}/api/voice-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Voice stream API error: ${response.status}`);
    }

    return response.json();
  }
}
