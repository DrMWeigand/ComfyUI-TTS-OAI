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

    # The node returns a tuple:
    #   audio_base64: a base64 encoded version of the raw audio (if returned directly)
    #   file_path: a file path where the audio is stored (if written to disk)
    RETURN_TYPES = ("STRING", "STRING")
    FUNCTION = "process_tts"
    CATEGORY = "Text-To-Speech"
    DESCRIPTION = "Sends a TTS request to an OpenAI‑compatible API endpoint and returns either base64‑encoded audio or a file path."

    def process_tts(self, text, model, voice, api_key, url, response_format, return_audio):
        # Prepare the payload as expected by the TTS API.
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "return_audio": return_audio,
            "response_format": response_format.lower()  # ensure lowercase for compatibility
        }
        # Prepare headers, adding an Authorization header if an API key is provided.
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
        
        if "application/json" in content_type:
            # The API returned a JSON response. This is expected when return_audio is false.
            try:
                data = response.json()
            except Exception as e:
                raise Exception("Failed to parse JSON response: " + str(e))
            audio_base64 = data.get("audio", "")
            file_path = data.get("file_path", "")
            return audio_base64, file_path
        elif "audio" in content_type:
            # The API returned raw binary audio. Base64-encode it for node compatibility.
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            return audio_base64, ""
        else:
            # Unexpected response type.
            raise Exception("Unexpected response Content-Type: " + content_type) 