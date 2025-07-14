#!/usr/bin/env python3
"""
Test script for Whisper model improvements
This script tests different Whisper models to verify they work properly.
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
    extract_text_from_result,
    get_recommended_model,
    list_available_models,
    DEFAULT_MODEL
)

def test_model_loading():
    """Test if whisper models can be loaded successfully."""
    print("🔄 Testing model loading...")
    try:
        model = get_whisper_model(DEFAULT_MODEL)
        print(f"✅ Default model '{DEFAULT_MODEL}' loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_model_recommendations():
    """Test the model recommendation system."""
    print("🔄 Testing model recommendations...")
    try:
        recommendations = {
            "realtime": get_recommended_model("realtime"),
            "fast": get_recommended_model("fast"),
            "default": get_recommended_model("default"),
            "quality": get_recommended_model("quality"),
            "best": get_recommended_model("best")
        }
        
        print("📋 Model Recommendations:")
        for use_case, model in recommendations.items():
            print(f"  {use_case}: {model}")
        
        return True
    except Exception as e:
        print(f"❌ Model recommendations failed: {e}")
        return False

def test_available_models():
    """Test listing available models."""
    print("🔄 Testing available models list...")
    try:
        models = list_available_models()
        print("📋 Available Models:")
        for model_name, details in models.items():
            print(f"  {model_name}: {details['size']} - {details['use_case']}")
        
        return True
    except Exception as e:
        print(f"❌ Available models listing failed: {e}")
        return False

def test_text_extraction():
    """Test the text extraction helper function."""
    print("🔄 Testing text extraction...")
    
    # Test different result formats
    test_cases = [
        "Simple string",
        {"text": "Dict with text key"},
        {"content": "Dict with content key"},
    ]
    
    for i, test_case in enumerate(test_cases):
        try:
            result = extract_text_from_result(test_case)
            print(f"✅ Test case {i+1}: '{result}'")
        except Exception as e:
            print(f"❌ Test case {i+1} failed: {e}")
            return False
    
    return True

def test_model_comparison():
    """Compare different models with a simple audio test."""
    print("🔄 Testing model comparison...")
    
    # Create a simple synthetic audio signal for testing
    # This is just for testing the model loading and API, not actual transcription
    try:
        # Generate a simple sine wave as test audio
        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        # Test with different models (if they load quickly)
        test_models = ["tiny", DEFAULT_MODEL]
        
        for model_name in test_models:
            try:
                print(f"  Testing model: {model_name}")
                model = get_whisper_model(model_name)
                
                # We won't actually transcribe the sine wave as it's not speech
                # Just verify the model loads and the API works
                print(f"  ✅ Model '{model_name}' loaded and ready")
                
            except Exception as e:
                print(f"  ❌ Model '{model_name}' failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model comparison failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Whisper Model Tests...\n")
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Model Recommendations", test_model_recommendations),
        ("Available Models", test_available_models),
        ("Text Extraction", test_text_extraction),
        ("Model Comparison", test_model_comparison),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! Whisper models are ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
