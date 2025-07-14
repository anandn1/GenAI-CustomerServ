# Walmart Whisper - GenAI RAG Customer Support System

## Quick Start Guide

This is a complete end-to-end GenAI RAG (Retrieval-Augmented Generation) customer support system for Walmart, featuring:

- **Backend**: FastAPI with 8 comprehensive API endpoints
- **Frontend**: React with TypeScript, dark/light theme, and modern UI
- **RAG Pipeline**: Document ingestion, chunking, embedding, and Pinecone vector store
- **Voice Integration**: File upload and live transcription with Whisper
- **AI Chat**: Conversational RAG with LangChain and OpenRouter LLM integration
- **Admin Dashboard**: Real-time metrics and system monitoring

## Features

### 🔥 Complete API Integration
- ✅ Chat with RAG (`/api/chat`)
- ✅ Voice file upload and transcription (`/api/voice`)
- ✅ Live voice transcription (`/api/voice-live`)
- ✅ Document retrieval (`/api/langchain/retrieve`)
- ✅ Order status lookup (`/api/order-status/{user_id}`)
- ✅ Product availability search (`/api/product-availability`)
- ✅ Sentiment analysis (`/api/sentiment-check`)
- ✅ Admin metrics dashboard (`/api/admin/metrics`)
- ✅ Health monitoring (`/api/health`)

### 🎨 Modern UI Features
- ✅ Dark/Light theme switching
- ✅ Real-time backend health monitoring
- ✅ Voice recording with visual feedback
- ✅ File upload for audio files
- ✅ Admin dashboard with metrics
- ✅ Escalation handling for negative feedback
- ✅ Multi-language support
- ✅ Quick action buttons

### 🤖 AI & RAG Features
- ✅ Advanced RAG pipeline with Pinecone vector store
- ✅ Conversational memory with chat history
- ✅ Context-aware responses using retrieved documents
- ✅ Sentiment analysis for automatic escalation
- ✅ Person review support in responses
- ✅ OpenRouter LLM integration

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   React Frontend│◄──►│  FastAPI Backend│◄──►│   RAG Pipeline  │
│                 │    │                 │    │                 │
│  - Dark Mode    │    │  - 8 API Routes │    │  - Pinecone DB  │
│  - Voice UI     │    │  - CORS Enabled │    │  - LangChain    │
│  - Health Mon.  │    │  - File Upload  │    │  - OpenRouter   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### Environment Variables
Create a `.env` file in the root directory:

```env
# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=walmart-rag-index
PINECONE_ENVIRONMENT=us-east-1

# Optional: Other API keys
OPENAI_API_KEY=your_openai_key_here
```

### Python Dependencies
```bash
pip install -r requirements.txt
pip install python-multipart  # For file uploads
```

### Node.js Dependencies
```bash
cd project
npm install
```

## Running the System

### 1. Start Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend Server
```bash
cd project
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## API Endpoints

### Chat & Voice
- `POST /api/chat` - Send chat message and get RAG response
- `POST /api/voice` - Upload audio file for transcription and response
- `POST /api/voice-live` - Live voice transcription

### Data & Search
- `POST /api/langchain/retrieve` - Direct document retrieval
- `GET /api/order-status/{user_id}` - Get order status
- `POST /api/product-availability` - Search product availability
- `POST /api/sentiment-check` - Analyze message sentiment

### Admin & Health
- `GET /api/admin/metrics` - Get system metrics
- `GET /api/health` - Health check endpoint

## Data Pipeline Setup

### 1. Prepare Your Data
Place your documents in the `data/` folder:
- PDF files (e.g., `Walmart Policies and Guidelines.pdf`)
- Text files (e.g., `walmart_faqs.txt`)
- CSV files (e.g., `Walmart_reviews_data.csv`)

### 2. Run Data Ingestion
```bash
cd data_pipeline
python ingest_data.py
```

This will:
- Load and chunk documents
- Generate embeddings
- Upload to Pinecone vector store
- Build retrievers for RAG

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Chat Test
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "What is Walmart return policy?",
    "language": "en"
  }'
```

### 3. Frontend Features Test
1. Open http://localhost:5174
2. Toggle dark/light mode
3. Try chat functionality
4. Test voice recording
5. Upload an audio file
6. Check admin dashboard
7. Monitor health status

## Troubleshooting

### Backend Issues
- **Import Errors**: Ensure all Python dependencies are installed
- **Port 8000 in use**: Change port in uvicorn command
- **Missing API keys**: Check `.env` file configuration

### Frontend Issues
- **Port 5173/5174 in use**: Vite will automatically find next available port
- **API connection errors**: Verify backend is running on port 8000
- **Theme not persisting**: Check if localStorage is enabled

### RAG Pipeline Issues
- **Pinecone connection**: Verify API key and index name
- **No documents found**: Run data ingestion pipeline
- **LLM responses**: Check OpenRouter API key

## Project Structure

```
GenAI-CustomerServ/
├── backend/                 # FastAPI backend
│   ├── main.py             # API routes and server
│   ├── rag_chain.py        # RAG implementation
│   ├── whisper_transcriber.py # Voice processing
│   └── utils/              # Utilities and prompts
├── project/                # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── hooks/          # React hooks for API
│   │   ├── services/       # API service layer
│   │   └── App.tsx         # Main application
├── data_pipeline/          # RAG data processing
│   ├── ingest_data.py      # Data ingestion script
│   ├── embedder.py         # Pinecone integration
│   └── loaders.py          # Document loaders
├── data/                   # Source documents
└── requirements.txt        # Python dependencies
```

## Production Deployment

### Backend
- Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
- Set up proper environment variables
- Configure CORS for your domain
- Set up health checks and monitoring

### Frontend
- Build production bundle: `npm run build`
- Serve with nginx or similar
- Configure API base URL for production

### Security
- Use HTTPS in production
- Secure API keys and environment variables
- Implement proper authentication if needed
- Set up rate limiting

## Next Steps

1. **Authentication**: Add user authentication and authorization
2. **Logging**: Implement comprehensive logging and monitoring
3. **Testing**: Add unit and integration tests
4. **Deployment**: Set up CI/CD pipeline
5. **Analytics**: Add user analytics and feedback collection

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check browser console for frontend errors
4. Review backend logs for API issues

---

**Walmart Whisper** - AI-Powered Customer Support System  
Built with FastAPI, React, LangChain, Pinecone, and OpenRouter
