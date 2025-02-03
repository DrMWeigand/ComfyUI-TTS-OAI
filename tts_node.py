import requests
import base64
import torch
import io
import soundfile as sf
from pydub import AudioSegment
import numpy as np

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

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "process_tts"
    CATEGORY = "Text-To-Speech"
    DESCRIPTION = "Sends a TTS request to an OpenAI‑compatible API endpoint and returns audio data"

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
        
        # Get the raw audio data
        if "application/json" in content_type:
            try:
                data = response.json()
                if "file_path" in data:
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
            audio_io = io.BytesIO(audio_bytes)
            
            if response_format.lower() == 'mp3':
                # Load MP3 using pydub
                audio = AudioSegment.from_mp3(audio_io)
                # Convert to numpy array
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                # Normalize
                samples = samples / 32768.0
                # Reshape if stereo
                if audio.channels == 2:
                    samples = samples.reshape((-1, 2))
                else:
                    samples = samples.reshape((-1, 1))
                # Convert to torch tensor and transpose
                waveform = torch.from_numpy(samples).T
                sample_rate = audio.frame_rate
            else:  # wav
                # Read WAV using soundfile
                audio_io.seek(0)  # Reset buffer position
                waveform, sample_rate = sf.read(audio_io)
                # Convert to float32 if needed
                if waveform.dtype != np.float32:
                    waveform = waveform.astype(np.float32)
                # Reshape if mono
                if len(waveform.shape) == 1:
                    waveform = waveform.reshape(-1, 1)
                # Convert to torch tensor and transpose
                waveform = torch.from_numpy(waveform).T

            # Create the audio dictionary that ComfyUI expects
            audio_data = {
                "waveform": waveform,
                "sample_rate": sample_rate
            }
            
            return (audio_data,)
            
        except Exception as e:
            raise Exception(f"Failed to process audio data: {e}") 