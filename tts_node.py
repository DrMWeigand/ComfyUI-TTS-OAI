import requests
import base64
import os
import tempfile
import uuid
import io
from pydub import AudioSegment
import numpy as np
import torch  # Needed to convert numpy data to torch tensor

class OpenAITTS:
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
                }),
                "return_audio": ("BOOLEAN", {
                    "default": True,
                    "label": "Return Audio Directly (True) or Write to Disk (False)"
                })
            }
        }

    # We now return an AUDIO type (a dictionary with waveform and sample_rate)
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "process_tts"
    CATEGORY = "Text-To-Speech"
    DESCRIPTION = "Sends a TTS request to an OpenAI‑compatible API endpoint and returns an audio dictionary"

    def process_tts(self, text, model, voice, api_key, url, response_format, return_audio):
        # Prepare the payload as expected by the TTS API.
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "return_audio": return_audio,
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
                    # If the API already saved the file, load its bytes.
                    with open(data["file_path"], "rb") as f:
                        audio_bytes = f.read()
                elif "audio" in data:
                    audio_bytes = base64.b64decode(data["audio"])
                else:
                    raise Exception("No audio data in response")
            except Exception as e:
                raise Exception("Failed to parse JSON response: " + str(e))
        else:
            audio_bytes = response.content

        try:
            # Process the audio in memory
            audio_io = io.BytesIO(audio_bytes)
            # Load the audio using pydub
            segment = AudioSegment.from_file(audio_io, format=response_format.lower())
            
            # Get raw audio data as array of samples
            samples = segment.get_array_of_samples()
            
            # Convert to tensor and reshape
            waveform = torch.tensor(samples, dtype=torch.float32)
            # Normalize to [-1, 1]
            waveform = waveform / (1 << (8 * segment.sample_width - 1))
            
            # Reshape for mono/stereo
            if segment.channels == 1:
                waveform = waveform.view(1, -1)  # mono: (1, samples)
            else:
                waveform = waveform.view(segment.channels, -1)  # stereo: (2, samples)
            
            # Create the audio dictionary that matches the example code's format
            audio_data = {
                "waveform": waveform.unsqueeze(0),  # Add batch dimension: (1, channels, samples)
                "sample_rate": segment.frame_rate
            }
            
            return (audio_data,)
            
        except Exception as e:
            raise Exception(f"Failed to process audio data: {e}") 