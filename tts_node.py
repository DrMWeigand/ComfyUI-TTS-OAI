import requests
import base64

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
                "response_format": (
                    "ENUM",
                    {
                        "choices": ["mp3", "wav"],
                        "default": "mp3",
                        "label": "Response Format (mp3/wav)"
                    }
                ),
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
        
        audio_data = {
            "format": response_format,
            "data": None,
            "path": None
        }

        if "application/json" in content_type:
            try:
                data = response.json()
                if "file_path" in data:
                    audio_data["path"] = data["file_path"]
                elif "audio" in data:
                    audio_data["data"] = data["audio"]
            except Exception as e:
                raise Exception("Failed to parse JSON response: " + str(e))
        elif "audio" in content_type:
            audio_data["data"] = base64.b64encode(response.content).decode("utf-8")
        else:
            raise Exception("Unexpected response Content-Type: " + content_type)

        return (audio_data,) 