"""
Whisper-based voice transcription service using OpenAI Whisper.
This version uses the official openai-whisper library which is more reliable on Windows.
"""

import os
import whisper
import torch
from typing import Optional, Union
import tempfile
import logging

logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
_models = {}

def get_whisper_model(model_name: str = "base"):
    """
    Load and cache a Whisper model.
    
    Args:
        model_name: Model size ('tiny', 'base', 'small', 'medium', 'large')
    
    Returns:
        Loaded Whisper model
    """
    if model_name not in _models:
        try:
            logger.info(f"Loading Whisper model: {model_name}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _models[model_name] = whisper.load_model(model_name, device=device)
            logger.info(f"Model {model_name} loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model {model_name}: {e}")
            raise
    
    return _models[model_name]

def transcribe_audio_file(
    audio_file_path: str, 
    model_name: str = "base", 
    language: Optional[str] = None
) -> str:
    """
    Transcribe an audio file using Whisper.
    
    Args:
        audio_file_path: Path to the audio file
        model_name: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        language: Language code (e.g., 'en', 'es', 'hi', 'fr') or None for auto-detection
    
    Returns:
        Transcribed text
    """
    try:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        model = get_whisper_model(model_name)
        
        # Transcribe with language parameter
        if language:
            logger.info(f"Transcribing with language: {language}")
            result = model.transcribe(audio_file_path, language=language)
        else:
            logger.info("Transcribing with auto-detection")
            result = model.transcribe(audio_file_path)
        
        # Extract text from result
        if isinstance(result, dict) and 'text' in result:
            text = result['text'].strip()
            logger.info(f"Transcription successful: {len(text)} characters")
            return text
        else:
            logger.error(f"Unexpected result format: {type(result)}")
            return ""
            
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

def transcribe_audio_bytes(
    audio_bytes: bytes, 
    model_name: str = "base", 
    language: Optional[str] = None,
    file_extension: str = "wav"
) -> str:
    """
    Transcribe audio from bytes data.
    
    Args:
        audio_bytes: Raw audio data
        model_name: Whisper model size
        language: Language code or None for auto-detection
        file_extension: Audio file format extension
    
    Returns:
        Transcribed text
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe the temporary file
            return transcribe_audio_file(temp_file_path, model_name, language)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Failed to transcribe audio bytes: {e}")
        raise

# Language mapping for frontend compatibility
SUPPORTED_LANGUAGES = {
    'en': 'en',      # English
    'es': 'es',      # Spanish
    'fr': 'fr',      # French
    'de': 'de',      # German
    'it': 'it',      # Italian
    'pt': 'pt',      # Portuguese
    'ru': 'ru',      # Russian
    'ja': 'ja',      # Japanese
    'ko': 'ko',      # Korean
    'zh': 'zh',      # Chinese
    'hi': 'hi',      # Hindi
    'ar': 'ar',      # Arabic
    'tr': 'tr',      # Turkish
    'pl': 'pl',      # Polish
    'nl': 'nl',      # Dutch
    'sv': 'sv',      # Swedish
    'da': 'da',      # Danish
    'no': 'no',      # Norwegian
    'fi': 'fi',      # Finnish
}

def get_supported_languages():
    """Get list of supported language codes."""
    return list(SUPPORTED_LANGUAGES.keys())

def normalize_language_code(lang_code: str) -> Optional[str]:
    """
    Normalize language code to Whisper format.
    
    Args:
        lang_code: Language code (e.g., 'en-US', 'hi-IN', 'es-ES')
    
    Returns:
        Normalized language code or None if not supported
    """
    if not lang_code:
        return None
    
    # Extract base language code
    base_lang = lang_code.split('-')[0].lower()
    return SUPPORTED_LANGUAGES.get(base_lang)

# Web-friendly functions for FastAPI integration

async def transcribe_uploaded_file(
    file_content: bytes,
    filename: str,
    model_name: str = "base",
    language: Optional[str] = None
) -> str:
    """
    Async wrapper for transcribing uploaded files.
    """
    try:
        # Extract file extension
        file_ext = filename.split('.')[-1].lower() if '.' in filename else 'wav'
        
        # Normalize language
        normalized_lang = normalize_language_code(language) if language else None
        
        # Transcribe
        return transcribe_audio_bytes(
            audio_bytes=file_content,
            model_name=model_name,
            language=normalized_lang,
            file_extension=file_ext
        )
    except Exception as e:
        logger.error(f"Failed to transcribe uploaded file {filename}: {e}")
        raise

async def transcribe_stream_chunk(
    audio_chunk: bytes,
    model_name: str = "base",
    language: Optional[str] = None
) -> str:
    """
    Transcribe a chunk of streaming audio data.
    """
    try:
        normalized_lang = normalize_language_code(language) if language else None
        return transcribe_audio_bytes(
            audio_bytes=audio_chunk,
            model_name=model_name,
            language=normalized_lang,
            file_extension="wav"
        )
    except Exception as e:
        logger.error(f"Failed to transcribe audio stream: {e}")
        raise
