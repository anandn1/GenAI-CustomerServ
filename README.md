# Walmart Whisper - GenAI RAG Customer Support System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white)](https://python.langchain.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-000000?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/)

## 🚀 Complete End-to-End RAG Customer Support System

A production-ready AI-powered customer support system built for Walmart, featuring advanced RAG (Retrieval-Augmented Generation), voice integration, real-time chat, and comprehensive admin dashboard.

### ✅ **FULLY INTEGRATED & WORKING**

## 🔥 Key Features

### 🤖 AI & RAG Pipeline
- **Advanced RAG Implementation** with LangChain and Pinecone vector store
- **Conversational Memory** - Chat history awareness
- **Context-Aware Responses** using retrieved documents
- **Smart Document Chunking** for optimal retrieval
- **OpenRouter LLM Integration** for high-quality responses

### 🎙️ Voice Integration
- **File Upload Transcription** - Upload audio files for processing
- **Live Voice Recording** - Real-time speech recognition
- **Multi-Language Support** - English, Spanish, French, German, etc.
- **Whisper AI Integration** for accurate transcription

### 🌐 Modern Web Interface
- **Dark/Light Theme** - Toggle with beautiful animations
- **Real-Time Health Monitoring** - Backend connection status
- **Voice UI** - Visual feedback during recording
- **Admin Dashboard** - System metrics and analytics
- **Responsive Design** - Works on desktop and mobile

### 🔧 Production-Ready Backend
- **8 Comprehensive API Endpoints**
- **FastAPI with Auto-Generated Docs**
- **CORS Enabled** for frontend integration
- **File Upload Support** with validation
- **Error Handling** and health checks

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   React Frontend│◄──►│  FastAPI Backend│◄──►│   RAG Pipeline  │
│                 │    │                 │    │                 │
│  • Dark Mode    │    │  • 8 API Routes │    │  • Pinecone DB  │
│  • Voice UI     │    │  • CORS Enabled │    │  • LangChain    │
│  • Health Mon.  │    │  • File Upload  │    │  • OpenRouter   │
│  • TypeScript   │    │  • Auto Docs    │    │  • Embeddings   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenRouter API Key
- Pinecone API Key

### 1️⃣ Environment Setup
Create `.env` file:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=walmart-rag-index
PINECONE_ENVIRONMENT=us-east-1
```

### 2️⃣ Install Dependencies
```bash
# Backend
pip install -r requirements.txt
pip install python-multipart

# Frontend
cd project && npm install
```

### 3️⃣ Start Development Servers

**Option A: Use PowerShell Script (Recommended)**
```powershell
.\start-dev.ps1
```

**Option B: Manual Start**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd project
npm run dev
```

### 4️⃣ Access Application
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📡 API Endpoints

### Chat & Voice
- `POST /api/chat` - RAG-powered chat responses
- `POST /api/voice` - Audio file transcription + RAG
- `POST /api/voice-live` - Live voice transcription

### Data & Search  
- `POST /api/langchain/retrieve` - Direct document retrieval
- `GET /api/order-status/{user_id}` - Order status lookup
- `POST /api/product-availability` - Product search
- `POST /api/sentiment-check` - Sentiment analysis

### Admin & Monitoring
- `GET /api/admin/metrics` - System metrics dashboard
- `GET /api/health` - Health check endpoint

## 🧪 Test the Integration

### Health Check
```bash
curl http://localhost:8000/api/health
# Response: {"status":"ok"}
```

### Chat Test
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user", 
    "message": "What is Walmart return policy?",
    "language": "en"
  }'
```

### Frontend Features
1. 🌐 Open http://localhost:5174
2. 🌙 Toggle dark/light mode  
3. 💬 Test chat functionality
4. 🎙️ Try voice recording
5. 📁 Upload audio files
6. 📊 Check admin dashboard
7. 🏥 Monitor health status

## 📂 Project Structure

```
GenAI-CustomerServ/
├── 🔧 backend/                 # FastAPI Backend
│   ├── main.py                # API routes & server
│   ├── rag_chain.py           # RAG implementation  
│   ├── whisper_transcriber.py # Voice processing
│   └── utils/                 # Prompts & utilities
├── 🎨 project/                # React Frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── hooks/             # API React hooks
│   │   ├── services/          # API service layer
│   │   └── App.tsx            # Main application
├── 🔄 data_pipeline/          # RAG Data Processing
│   ├── ingest_data.py         # Data ingestion
│   ├── embedder.py            # Pinecone integration
│   └── loaders.py             # Document loaders
├── 📄 data/                   # Source documents
├── 🚀 start-dev.ps1           # Development startup
└── 📚 SETUP_GUIDE.md          # Detailed setup guide
```

## 🎯 Completed Features

### ✅ Backend Integration
- [x] FastAPI server with 8 API endpoints
- [x] RAG chain with conversational memory
- [x] Pinecone vector store integration
- [x] Voice transcription (file + live)
- [x] CORS configuration
- [x] Auto-generated API documentation
- [x] Health monitoring
- [x] Error handling

### ✅ Frontend Integration  
- [x] React TypeScript application
- [x] Dark/light theme switching
- [x] Voice recorder with file upload
- [x] Real-time health monitoring
- [x] API service layer with hooks
- [x] Admin dashboard with metrics
- [x] Escalation handling
- [x] Multi-language support

### ✅ RAG Pipeline
- [x] Document loading (PDF, TXT, CSV)
- [x] Smart chunking strategies
- [x] Embedding generation
- [x] Pinecone vector store
- [x] Context-aware retrieval
- [x] Conversational memory
- [x] OpenRouter LLM integration

## 🔄 Recent Updates

- **✅ API Integration Complete**: All 8 endpoints integrated and tested
- **✅ Dark Mode Added**: Beautiful theme switching with CSS variables
- **✅ Voice Upload**: File upload support added to VoiceRecorder component
- **✅ Health Monitoring**: Real-time backend connection status
- **✅ Error Handling**: Unified error states across all API calls
- **✅ Environment Config**: Proper .env setup for API URLs

## 🚀 Production Ready

This system is production-ready with:
- Comprehensive error handling
- Health monitoring
- Scalable architecture
- Security best practices
- Documentation
- Easy deployment

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Detailed setup instructions
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation
- **Demo Script** - Step-by-step usage examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Walmart Whisper** - Next-Generation AI Customer Support  
*Powered by FastAPI • React • LangChain • Pinecone • OpenRouter*
