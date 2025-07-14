# API keys, Pinecone env vars, Gemini config

# Whisper Model Configuration
# Available models: tiny, base, small, medium, large
# Recommendations:
# - tiny: Real-time applications, low resource usage (~39 MB)
# - base: Balanced performance (~74 MB) 
# - small: Recommended default, good accuracy (~244 MB)
# - medium: High accuracy needs (~769 MB)
# - large: Best quality, slower processing (~1550 MB)

WHISPER_MODEL = "small"  # Default model for best balance of accuracy and speed

# Optional: Environment-specific overrides
import os
WHISPER_MODEL = os.getenv("WHISPER_MODEL", WHISPER_MODEL)
