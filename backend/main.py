from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import shutil
import tempfile

from backend.rag_chain import get_smart_answer, conversational_rag_chain
from backend.whisper_transcriber import transcribe_audio_file, transcribe_live

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
    chat_history = req.chat_history or []
    answer, sources, category, new_history = get_smart_answer(req.message, chat_history)
    return {
        "answer": answer,
        "sources": [s.page_content for s in sources],
        "category": category,
        "chat_history": [m.dict() if hasattr(m, 'dict') else str(m) for m in new_history]
    }

@app.post("/api/voice")
def voice_file_endpoint(file: UploadFile = File(...), user_id: str = Form(...), language: str = Form("en")):
    """
    Accepts an audio file upload and returns the Whisper transcription and RAG answer.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    transcript = transcribe_audio_file(tmp_path, model_name="base")
    answer, sources, category, new_history = get_smart_answer(transcript, [])
    os.remove(tmp_path)
    return {
        "transcript": transcript,
        "answer": answer,
        "sources": [s.page_content for s in sources],
        "category": category,
        "chat_history": [m.dict() if hasattr(m, 'dict') else str(m) for m in new_history]
    }

@app.post("/api/voice-live")
def voice_live_endpoint(user_id: str = Form(...), language: str = Form("en")):
    """
    Starts a live Whisper transcription session (for desktop/CLI use). Returns the first transcribed text and RAG answer.
    """
    # This is a blocking call and suitable for CLI/desktop, not web. For web, use websockets or streaming.
    gen = transcribe_live(model_name="base")
    transcript = next(gen)
    answer, sources, category, new_history = get_smart_answer(transcript, [])
    return {
        "transcript": transcript,
        "answer": answer,
        "sources": [s.page_content for s in sources],
        "category": category,
        "chat_history": [m.dict() if hasattr(m, 'dict') else str(m) for m in new_history]
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
    from backend.rag_chain import evaluate_with_llm
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
    return {"status": "ok"}
