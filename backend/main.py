from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import shutil
import tempfile

from rag_chain import get_smart_answer, conversational_rag_chain
from whisper_transcriber import transcribe_audio_file, transcribe_web_audio, transcribe_audio_buffer
from config import WHISPER_MODEL

app = FastAPI(title="Walmart Whisper Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    chat_history: Optional[List[dict]] = None
    language: Optional[str] = "en"

class VoiceRequest(BaseModel):
    user_id: str
    language: Optional[str] = "en"

class SentimentRequest(BaseModel):
    text: str

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    try:
        chat_history = req.chat_history or []
        answer, sources, category, new_history = get_smart_answer(req.message, chat_history)
        
        # Properly serialize chat history
        serialized_history = []
        for msg in new_history:
            if hasattr(msg, 'content'):
                # LangChain message object
                serialized_history.append({
                    "content": msg.content,
                    "type": msg.__class__.__name__.lower().replace('message', ''),
                    "additional_kwargs": getattr(msg, 'additional_kwargs', {}),
                    "response_metadata": getattr(msg, 'response_metadata', {}),
                    "name": getattr(msg, 'name', None),
                    "id": getattr(msg, 'id', None),
                    "example": getattr(msg, 'example', False)
                })
            elif isinstance(msg, dict):
                # Already a dictionary
                serialized_history.append(msg)
            else:
                # Fallback - convert to string
                serialized_history.append({
                    "content": str(msg),
                    "type": "unknown"
                })
        
        return {
            "answer": answer,
            "sources": [s.page_content if hasattr(s, 'page_content') else str(s) for s in sources],
            "category": category,
            "chat_history": serialized_history
        }
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        return {
            "answer": "I encountered an error processing your request. Please try again.",
            "sources": [],
            "category": "error",
            "chat_history": req.chat_history or []
        }

@app.post("/api/voice")
def voice_file_endpoint(file: UploadFile = File(...), user_id: str = Form(...), language: str = Form("en")):
    """
    Accepts an audio file upload and returns the Whisper transcription and RAG answer.
    Supports multiple languages for transcription.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Convert language format (e.g., 'en-US' -> 'en') and handle auto-detection
        whisper_language = None
        if language and language != "auto":
            whisper_language = language.split('-')[0]  # Convert 'en-US' to 'en'
            # Validate language code
            supported_languages = [
                'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'tr', 'ru', 
                'ja', 'ko', 'zh', 'ar', 'hi', 'th', 'sv', 'da', 'no', 'fi'
            ]
            if whisper_language not in supported_languages:
                whisper_language = None  # Fall back to auto-detection        # Transcribe with language parameter - using configured model for better accuracy
        transcript = transcribe_audio_file(tmp_path, model_name=WHISPER_MODEL, language=whisper_language)
        
        # Add language context to transcript for better RAG processing
        if language and language != "en" and language != "auto":
            language_map = {
                "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
                "pt": "Portuguese", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
                "ar": "Arabic", "hi": "Hindi", "nl": "Dutch", "pl": "Polish",
                "tr": "Turkish", "ru": "Russian", "th": "Thai", "sv": "Swedish",
                "da": "Danish", "no": "Norwegian", "fi": "Finnish"
            }
            language_name = language_map.get(language.split('-')[0], language)
            formatted_transcript = f"[Language: {language_name}] {transcript}"
        else:
            formatted_transcript = transcript
        
        # Get RAG answer
        answer, sources, category, new_history = get_smart_answer(formatted_transcript, [])
        
        # Clean up temporary file
        os.remove(tmp_path)
        
        # Properly serialize chat history
        serialized_history = []
        for msg in new_history:
            if hasattr(msg, 'content'):
                serialized_history.append({
                    "content": msg.content,
                    "type": msg.__class__.__name__.lower().replace('message', ''),
                    "additional_kwargs": getattr(msg, 'additional_kwargs', {}),
                    "response_metadata": getattr(msg, 'response_metadata', {}),
                    "name": getattr(msg, 'name', None),
                    "id": getattr(msg, 'id', None),
                    "example": getattr(msg, 'example', False)
                })
            elif isinstance(msg, dict):
                serialized_history.append(msg)
            else:
                serialized_history.append({
                    "content": str(msg),
                    "type": "unknown"
                })
        
        return {
            "transcript": transcript,
            "answer": answer,
            "sources": [s.page_content if hasattr(s, 'page_content') else str(s) for s in sources],
            "category": category,
            "chat_history": serialized_history
        }
    except Exception as e:
        print(f"Error in voice_file_endpoint: {e}")
        if 'tmp_path' in locals():
            try:
                os.remove(tmp_path)
            except:
                pass
        return {
            "transcript": "",
            "answer": "I encountered an error processing your voice message. Please try again.",
            "sources": [],
            "category": "error",
            "chat_history": []
        }

@app.post("/api/voice-live")
def voice_live_endpoint(user_id: str = Form(...), language: str = Form("en")):
    """
    Live voice transcription endpoint - Note: This endpoint is deprecated for web use.
    For web applications, use /api/voice with file uploads instead.
    This endpoint is kept for backward compatibility but not recommended for production web use.
    """
    return {
        "transcript": "",
        "answer": "Live voice transcription is not supported in web environments. Please use the file upload method instead.",
        "sources": [],
        "category": "info",
        "chat_history": [],
        "message": "Use /api/voice endpoint with audio file upload for web-based voice transcription."
    }

@app.post("/api/voice-stream")
def voice_stream_endpoint(audio_data: UploadFile = File(...), user_id: str = Form(...), language: str = Form("en")):
    """
    Stream audio data for real-time transcription (optimized for web applications).
    Accepts raw audio data chunks and returns transcription.
    """
    try:
        # Read audio data from upload
        audio_bytes = audio_data.file.read()
        
        # Convert language format and handle auto-detection
        whisper_language = None
        if language and language != "auto":
            whisper_language = language.split('-')[0]  # Convert 'en-US' to 'en'
            # Validate language code
            supported_languages = [
                'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'tr', 'ru', 
                'ja', 'ko', 'zh', 'ar', 'hi', 'th', 'sv', 'da', 'no', 'fi'
            ]
            if whisper_language not in supported_languages:
                whisper_language = None  # Fall back to auto-detection        # Use the web audio transcription function - using configured model for better accuracy
        transcript = transcribe_web_audio(audio_bytes, model_name=WHISPER_MODEL, language=whisper_language)
        
        # Add language context to transcript for better RAG processing
        if language and language != "en" and language != "auto":
            language_map = {
                "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
                "pt": "Portuguese", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
                "ar": "Arabic", "hi": "Hindi", "nl": "Dutch", "pl": "Polish",
                "tr": "Turkish", "ru": "Russian", "th": "Thai", "sv": "Swedish",
                "da": "Danish", "no": "Norwegian", "fi": "Finnish"
            }
            language_name = language_map.get(language.split('-')[0], language)
            formatted_transcript = f"[Language: {language_name}] {transcript}"
        else:
            formatted_transcript = transcript
        
        # Get RAG answer
        answer, sources, category, new_history = get_smart_answer(formatted_transcript, [])
        
        # Properly serialize chat history
        serialized_history = []
        for msg in new_history:
            if hasattr(msg, 'content'):
                serialized_history.append({
                    "content": msg.content,
                    "type": msg.__class__.__name__.lower().replace('message', ''),
                    "additional_kwargs": getattr(msg, 'additional_kwargs', {}),
                    "response_metadata": getattr(msg, 'response_metadata', {}),
                    "name": getattr(msg, 'name', None),
                    "id": getattr(msg, 'id', None),
                    "example": getattr(msg, 'example', False)
                })
            elif isinstance(msg, dict):
                serialized_history.append(msg)
            else:
                serialized_history.append({
                    "content": str(msg),
                    "type": "unknown"
                })
        
        return {
            "transcript": transcript,
            "answer": answer,
            "sources": [s.page_content if hasattr(s, 'page_content') else str(s) for s in sources],
            "category": category,
            "chat_history": serialized_history
        }
    except Exception as e:
        print(f"Error in voice_stream_endpoint: {e}")
        return {
            "transcript": "",
            "answer": "I encountered an error processing the audio stream. Please try again.",
            "sources": [],
            "category": "error",
            "chat_history": []
        }

@app.post("/api/langchain/retrieve")
def retrieve_endpoint(query: str):
    docs = conversational_rag_chain.retriever.invoke(query)
    return {"documents": [d.page_content for d in docs]}

@app.get("/api/order-status/{user_id}")
def order_status(user_id: str):
    return {"user_id": user_id, "order_status": "Delivered", "order_id": str(uuid.uuid4())}

@app.get("/api/product-availability")
def product_availability(product: str):
    return {"product": product, "available": True, "stores": ["Walmart Supercenter #123", "Walmart Neighborhood Market #456"]}

@app.post("/api/sentiment-check")
def sentiment_check(req: SentimentRequest):
    from rag_chain import evaluate_with_llm
    passed, justification = evaluate_with_llm(req.text, req.text, "Detect negative sentiment")
    return {"sentiment": "negative" if not passed else "neutral", "justification": justification}

@app.get("/api/admin/metrics")
def admin_metrics():
    return {
        "total_chats": 1234,
        "escalations": 12,
        "avg_response_time": 1.2,
        "active_sessions": 42
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "whisper_model": WHISPER_MODEL}

@app.get("/api/whisper/models")
def get_whisper_models():
    """Get available Whisper models and their characteristics"""
    from whisper_transcriber import list_available_models, get_recommended_model
    return {
        "current_model": WHISPER_MODEL,
        "available_models": list_available_models(),
        "recommendations": {
            "realtime": get_recommended_model("realtime"),
            "fast": get_recommended_model("fast"), 
            "default": get_recommended_model("default"),
            "quality": get_recommended_model("quality"),
            "best": get_recommended_model("best")
        }
    }
