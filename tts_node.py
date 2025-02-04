import requests
import base64
import os
import tempfile
import uuid
import io
from pydub import AudioSegment
import numpy as np
import torch  # Needed to convert numpy data to torch tensor
import torchaudio

class OpenAITTS:
    # You may choose to set a default here, but we'll override it with the file's sample rate.
    DEFAULT_SAMPLE_RATE = 24000  

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Hello world", "label": "Text"}),
                "model": ("STRING", {"default": "default_tts_model", "label": "Model"}),
                "voice": ("STRING", {"default": "af_sky", "label": "Voice"}),
                "api_key": ("STRING", {"default": "", "label": "API Key"}),
                "url": ("STRING", {
                    "default": "http://localhost:3001/v1/audio/speech",
                    "label": "TTS Endpoint URL"
                }),
                "response_format": ("STRING", {
                    "default": "mp3",
                    "label": "Audio Format (mp3/wav)"
                })
            }
        }

    # Return an AUDIO type (a dictionary with waveform and sample_rate)
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "process_tts"
    CATEGORY = "Text-To-Speech"
    DESCRIPTION = "Sends a TTS request to an OpenAI‑compatible API endpoint and returns an audio dictionary"

    def process_tts(self, text, model, voice, api_key, url, response_format):
        # Prepare the payload as expected by the TTS API.
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "return_audio": True,
            "response_format": response_format.lower()
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
        except Exception as e:
            raise Exception(f"Failed to send request: {e}")

        if response.status_code != 200:
            raise Exception(f"TTS API returned status code {response.status_code}: {response.text}")

        content_type = response.headers.get("Content-Type", "")
        
        # Get the raw audio data from the response.
        if "application/json" in content_type:
            try:
                data = response.json()
                if "file_path" in data:
                    audio_bytes = open(data["file_path"], "rb").read()
                elif "audio" in data:
                    audio_bytes = base64.b64decode(data["audio"])
                else:
                    raise Exception("No audio data in response")
            except Exception as e:
                raise Exception("Failed to parse JSON response: " + str(e))
        else:
            audio_bytes = response.content

        try:
            # Create a BytesIO buffer with the audio data
            audio_buffer = io.BytesIO(audio_bytes)
            
            # Load audio using torchaudio
            waveform, sample_rate = torchaudio.load(
                audio_buffer,
                format=response_format.lower()
            )
            
            # Debug info
            print(f"Loaded audio: shape={waveform.shape}, sample_rate={sample_rate}")
            
            # Add batch dimension if not present
            if waveform.dim() == 2:
                waveform = waveform.unsqueeze(0)
            
            # Create the audio dictionary
            audio_data = {
                "waveform": waveform,
                "sample_rate": sample_rate
            }
            
            return (audio_data,)
            
        except Exception as e:
            raise Exception(f"Failed to process audio data: {e}") 