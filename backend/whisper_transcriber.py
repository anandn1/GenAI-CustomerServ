# Whisper transcription logic for voice input using openai-whisper

import whisper
import pyaudio
import numpy as np
import time
import keyboard
import tempfile
import os

# Whisper model initialization cache to avoid reloading
_model_cache = {}

# Whisper model configurations
WHISPER_MODELS = {
    "tiny": {"size": "~39 MB", "speed": "~32x", "accuracy": "Basic", "use_case": "Real-time, low resource"},
    "base": {"size": "~74 MB", "speed": "~16x", "accuracy": "Good", "use_case": "Balanced performance"},
    "small": {"size": "~244 MB", "speed": "~6x", "accuracy": "Better", "use_case": "Recommended default"},
    "medium": {"size": "~769 MB", "speed": "~2x", "accuracy": "High", "use_case": "High accuracy needs"},
    "large": {"size": "~1550 MB", "speed": "~1x", "accuracy": "Highest", "use_case": "Best quality, slower"}
}

# Default model - using 'small' for better accuracy while maintaining reasonable speed
DEFAULT_MODEL = "small"

def get_whisper_model(model_name=DEFAULT_MODEL):
    """
    Get or create a whisper model with caching to improve performance.
    
    Args:
        model_name: Whisper model to use (tiny, base, small, medium, large)
                   Default is 'small' for optimal balance of accuracy and speed
    """
    if model_name not in _model_cache:
        try:
            print(f"Loading Whisper model '{model_name}' ({WHISPER_MODELS.get(model_name, {}).get('size', 'unknown size')})...")
            _model_cache[model_name] = whisper.load_model(model_name)
            print(f"✅ Model '{model_name}' loaded successfully")
        except Exception as e:
            print(f"Error loading whisper model '{model_name}': {e}")
            # Fallback to base model if specific model fails
            if model_name != "base":
                print("Falling back to base model...")
                _model_cache[model_name] = whisper.load_model("base")
            else:
                raise e
    return _model_cache[model_name]

def get_recommended_model(use_case="default"):
    """
    Get recommended Whisper model based on use case.
    
    Args:
        use_case: "realtime" for fast processing, "default" for balanced, "quality" for best accuracy
        
    Returns:
        Recommended model name
    """
    recommendations = {
        "realtime": "tiny",     # Fastest, for real-time applications
        "fast": "base",         # Good balance of speed and accuracy
        "default": "small",     # Recommended default
        "quality": "medium",    # High accuracy
        "best": "large"         # Best quality, slowest
    }
    return recommendations.get(use_case, "small")

def list_available_models():
    """
    List all available Whisper models with their characteristics.
    
    Returns:
        Dictionary of model information
    """
    return WHISPER_MODELS

def extract_text_from_result(result):
    """
    Helper function to extract text from whisper result.
    """
    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        return result.get('text', '')
    elif hasattr(result, 'text'):
        return result.text
    else:
        return str(result)

def transcribe_live(model_name=DEFAULT_MODEL, language=None):
    """
    Live speech-to-text using Whisper. Press and hold SPACE to record, release to transcribe. ESC to exit.
    Returns transcribed text each time you release SPACE.
    
    Note: This function is for CLI/desktop use only. For web applications, use transcribe_audio_file with uploaded files.
    
    Args:
        model_name: Whisper model to use (tiny, base, small, medium, large)
                   Default is 'small' for optimal balance of accuracy and speed
        language: Language code (e.g., 'en', 'es', 'fr', 'de', etc.) or None for auto-detection
    """
    CHUNK = 1024 # Frame Size
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000 # Whisper prefers 16000Hz

    # Initialize whisper model
    model = get_whisper_model(model_name)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("🎤 Press and hold SPACE to talk. Release to transcribe. Press ESC to exit.")
    frames = []
    recording = False
    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("⏹️ Stopped.")
                break
            if keyboard.is_pressed('space'):
                if not recording:
                    print("🎙️ Recording...")
                    frames = []
                    recording = True
                data = stream.read(CHUNK)
                frames.append(data)           
            elif recording:
                print("⏱️ Processing...")
                audio_data = b''.join(frames)
                np_audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Use specified language or auto-detect
                options = {"language": language} if language else {}
                result = model.transcribe(np_audio, **options)
                    
                # Extract text from result
                text = extract_text_from_result(result)
                print("📝", text)
                yield text
                recording = False
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("⏹️ Stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def transcribe_audio_buffer(audio_buffer, model_name=DEFAULT_MODEL, language=None, sample_rate=16000):
    """
    Transcribe audio data from a buffer (suitable for web applications).
    
    Args:
        audio_buffer: Raw audio data as bytes or numpy array
        model_name: Whisper model to use (tiny, base, small, medium, large)
                   Default is 'small' for optimal balance of accuracy and speed
        language: Language code (e.g., 'en', 'es', 'fr', 'de', etc.) or None for auto-detection
        sample_rate: Audio sample rate (default: 16000 Hz)
        
    Returns:
        The transcribed text.
    """
    try:
        # Initialize whisper model
        model = get_whisper_model(model_name)
        
        # Convert audio buffer to numpy array if it's bytes
        if isinstance(audio_buffer, bytes):
            np_audio = np.frombuffer(audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
        elif isinstance(audio_buffer, np.ndarray):
            # Ensure it's in the right format
            if audio_buffer.dtype != np.float32:
                np_audio = audio_buffer.astype(np.float32)
                if np_audio.max() > 1.0:  # If it's not normalized
                    np_audio = np_audio / 32768.0
            else:
                np_audio = audio_buffer
        else:
            raise ValueError("audio_buffer must be bytes or numpy array")
        
        # Use specified language or auto-detect
        options = {"language": language} if language else {}
        result = model.transcribe(np_audio, **options)
            
        # Extract text from result
        text = extract_text_from_result(result)
        return text
            
    except Exception as e:
        print(f"Error in transcribe_audio_buffer: {e}")
        return "Error: Could not transcribe audio buffer."

def transcribe_web_audio(audio_data, model_name=DEFAULT_MODEL, language=None):
    """
    Transcribe audio data from web applications (WebRTC, MediaRecorder, etc.).
    
    Args:
        audio_data: Audio data as bytes (from web upload)
        model_name: Whisper model to use (tiny, base, small, medium, large)
                   Default is 'small' for optimal balance of accuracy and speed
        language: Language code (e.g., 'en', 'es', 'fr', 'de', etc.) or None for auto-detection
        
    Returns:
        The transcribed text.
    """
    try:
        # Create a temporary file for the audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        # Use the file-based transcription
        result = transcribe_audio_file(tmp_path, model_name, language)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        print(f"Error in transcribe_web_audio: {e}")
        return "Error: Could not transcribe web audio."

def transcribe_audio_file(audio_file_path, model_name=DEFAULT_MODEL, language=None):
    """
    Transcribe a given audio file (wav/mp3/m4a/ogg/flac) using Whisper.
    
    Args:
        audio_file_path: Path to the audio file
        model_name: Whisper model to use (tiny, base, small, medium, large)
                   Default is 'small' for optimal balance of accuracy and speed
        language: Language code (e.g., 'en', 'es', 'fr', 'de', etc.) or None for auto-detection
        
    Returns:
        The transcribed text.
    """
    try:
        # Initialize whisper model
        model = get_whisper_model(model_name)
        
        # Use specified language or auto-detect
        options = {"language": language} if language else {}
        result = model.transcribe(audio_file_path, **options)
        
        # Extract text from result
        text = extract_text_from_result(result)
        return text
            
    except Exception as e:
        print(f"Error in transcribe_audio_file: {e}")
        return "Error: Could not transcribe audio file."

# Remove FastAPI app and endpoint from this file. All API routes should be defined in main.py for a clean architecture.
# Only keep the core transcription functions here.

# Example usage:
# for text in transcribe_live():
#     print("Transcribed:", text)