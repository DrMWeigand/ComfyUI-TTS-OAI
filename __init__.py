from .tts_node import OpenAITTS

NODE_CLASS_MAPPINGS = {
    "OpenAITTS": OpenAITTS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenAITTS": "OpenAI TTS"
}

# Register the AUDIO type
EXTENSION_TYPES = {"AUDIO"}

# Display mappings for the node
NODE_DISPLAY_MAPPINGS = {
    "OpenAITTS": {
        "name": "OpenAI TTS",
        "description": "Text-to-Speech using OpenAI-compatible API.",
    },
}
