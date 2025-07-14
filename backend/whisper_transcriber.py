# Whisper transcription logic for voice input

import whisper
import pyaudio
import numpy as np
import time
import keyboard
import tempfile

def transcribe_live(model_name="base"):
    """
    Live speech-to-text using Whisper. Press and hold SPACE to record, release to transcribe. ESC to exit.
    Returns transcribed text each time you release SPACE.
    """
    CHUNK = 1024 # Frame Size
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000 # Whisper prefers 16000Hz

    model = whisper.load_model(model_name)


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
                result = model.transcribe(np_audio, language="en")
                print("📝", result['text'])
                yield result['text']
                recording = False
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("⏹️ Stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def transcribe_audio_file(audio_file_path, model_name="base"):
    """
    Transcribe a given audio file (wav/mp3/m4a/ogg/flac) using Whisper.
    Returns the transcribed text.
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file_path, language="en")
    return result['text']

# Remove FastAPI app and endpoint from this file. All API routes should be defined in main.py for a clean architecture.
# Only keep the core transcription functions here.

# Example usage:
# for text in transcribe_live():
#     print("Transcribed:", text)