#!/usr/bin/env python3
"""
Test script for openai-whisper integration
This script tests the whisper functions to ensure they work properly.
"""

import os
import sys
import tempfile
import numpy as np
from whisper_transcriber import (
    get_whisper_model, 
    transcribe_audio_file, 
    transcribe_web_audio,
    transcribe_audio_buffer,
    extract_text_from_result
)

def test_model_loading():
    """Test if whisper models can be loaded successfully."""
    print("🔄 Testing model loading...")
    try:
        model = get_whisper_model("base")
        print("✅ Base model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_text_extraction():
    """Test the text extraction helper function."""
    print("🔄 Testing text extraction...")
    
    # Test different result formats
    test_cases = [
        "Simple string",
        {"text": "Dict with text key"},
        {"transcription": "Dict with transcription key"},
    ]
    
    for i, test_case in enumerate(test_cases):
        try:
            result = extract_text_from_result(test_case)
            print(f"✅ Test case {i+1}: {result}")
        except Exception as e:
            print(f"❌ Test case {i+1} failed: {e}")
            return False
    
    return True

def test_audio_buffer_processing():
    """Test audio buffer processing with dummy data."""
    print("🔄 Testing audio buffer processing...")
    
    try:
        # Create dummy audio data (1 second of silence at 16kHz)
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        
        # Generate a simple sine wave for testing
        frequency = 440.0  # A4 note
        t = np.linspace(0, duration, samples, False)
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32) * 0.1
        
        # Test with numpy array
        result = transcribe_audio_buffer(audio_data, model_name="base", language="en")
        print(f"✅ Audio buffer processing successful: {result[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Audio buffer processing failed: {e}")
        return False

def test_file_transcription():
    """Test file-based transcription with a dummy audio file."""
    print("🔄 Testing file transcription...")
    
    try:
        # Create a temporary WAV file with dummy data
        import wave
        
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        
        # Generate a simple sine wave
        frequency = 440.0  # A4 note
        t = np.linspace(0, duration, samples, False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit integers
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            with wave.open(tmp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            # Test transcription
            result = transcribe_audio_file(tmp_file.name, model_name="base", language="en")
            print(f"✅ File transcription successful: {result[:50]}...")
            
            # Clean up
            os.unlink(tmp_file.name)
            return True
            
    except Exception as e:
        print(f"❌ File transcription failed: {e}")
        return False

def test_web_audio_processing():
    """Test web audio processing with dummy data."""
    print("🔄 Testing web audio processing...")
    
    try:
        # Create dummy audio bytes
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        
        # Generate a simple sine wave
        frequency = 440.0  # A4 note
        t = np.linspace(0, duration, samples, False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Convert to bytes (simulating web upload)
        audio_int16 = (audio_data * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        result = transcribe_web_audio(audio_bytes, model_name="base", language="en")
        print(f"✅ Web audio processing successful: {result[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Web audio processing failed: {e}")
        return False

def test_multilingual_support():
    """Test multilingual support with different language codes."""
    print("🔄 Testing multilingual support...")
    
    languages_to_test = ['en', 'es', 'fr', 'de', None]  # None = auto-detect
    
    for lang in languages_to_test:
        try:
            # Create dummy audio data
            sample_rate = 16000
            duration = 0.5
            samples = int(sample_rate * duration)
            
            frequency = 440.0
            t = np.linspace(0, duration, samples, False)
            audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32) * 0.1
            
            result = transcribe_audio_buffer(audio_data, model_name="base", language=lang)
            lang_str = lang if lang else "auto-detect"
            print(f"✅ Language {lang_str}: {result[:30]}...")
            
        except Exception as e:
            print(f"❌ Language {lang_str} failed: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting whisper-cpp-python integration tests...\n")
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Text Extraction", test_text_extraction),
        ("Audio Buffer Processing", test_audio_buffer_processing),
        ("File Transcription", test_file_transcription),
        ("Web Audio Processing", test_web_audio_processing),
        ("Multilingual Support", test_multilingual_support),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! whisper-cpp-python integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
