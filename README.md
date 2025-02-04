# ComfyUI-TTS-OAI-API

A custom [ComfyUI](https://github.com/comfyanonymous/ComfyUI) node for interfacing with an OpenAI‑compatible TTS API endpoint. This node is designed to produce audio output in either MP3 or WAV format and includes support for voice combining using comma-separated voice identifiers.

> **Note:** This project is best used in conjunction with a self-hosted TTS endpoint. We recommend using the [Kokoros](https://github.com/DrMWeigand/Kokoros) project, which provides an easily deployable OpenAI‑compatible TTS API. Follow the instructions in the Kokoros repository to set up your own endpoint.

## Features

- **OpenAI-Compatible TTS:** Send text to a self-hosted (or remote) TTS endpoint that conforms to OpenAI’s API format.
- **Audio Format Options:** Currently supports only **mp3** and **wav** formats.
- **Voice Combining:** The `voice` parameter accepts a single voice identifier or multiple identifiers (separated by commas) for voice blending.
- **Direct Audio Integration:** Returns an audio dictionary containing the waveform tensor and sample rate for seamless integration with other ComfyUI audio processing nodes.

## Requirements

- **Python Dependencies:**  
  - `torch`
  - `torchaudio`
  - `pydub`
  - `numpy`
  - `requests`
  
  You can install these via pip:
  
  ```bash
  pip install torch torchaudio pydub numpy requests
  ```

- **FFmpeg:**  
  [pydub](https://github.com/jiaaro/pydub) requires FFmpeg to be installed on your system. Follow the [FFmpeg installation guide](https://ffmpeg.org/download.html) for your platform.

## Installation

1. Place the `tts_node.py` file (and the accompanying `__init__.py`) into your ComfyUI custom nodes directory.
2. Ensure that the dependencies from the **Requirements** section are installed.
3. Configure your `pyproject.toml` as needed (example provided in the repository).

## Usage

1. **Configuration:**  
   Launch ComfyUI and open your node editor. Your new node, **OpenAI TTS**, should appear (with the display name "ComfyUI-TTS-OAI-API").

2. **Parameters:**  
   - **text:**  
     The text string you wish to convert to speech.
     
   - **model:**  
     Specify the TTS model identifier as required by your endpoint.
     
   - **voice:**  
     A string representing the desired voice. You may provide a single identifier (default is `"af_sky"`) or a comma-separated list (e.g., `"voice1,voice2"`) to combine voices.  
     
     > **Voice Combining:** The endpoint supports voice blending by reading multiple voice IDs. Only the MP3 and WAV formats are supported. Ensure that you only use these two formats in the `response_format` parameter.
     
   - **api_key:**  
     Your API key for authorization, if required.
     
   - **url:**  
     The URL endpoint for your TTS service. For a self-hosted solution, you can set it to something like:  
     `http://localhost:3001/v1/audio/speech`
     
   - **response_format:**  
     Specify the output format: either `"mp3"` or `"wav"`.
     
   - **return_audio:**  
     Boolean flag to indicate whether to directly return the audio (as an internal AUDIO type) or to write the audio to disk.

3. **Connecting in ComfyUI:**  
   Once configured, connect the output of the **OpenAI TTS** node to an audio preview or processing node. The output is an AUDIO dictionary with the following keys:
   - `waveform`: A torch tensor containing the audio samples (normalized to the range [-1, 1]).
   - `sample_rate`: The sample rate at which the audio was produced (as reported by the endpoint).

## Self-Hosting with Kokoros

For those who wish to self-host an OpenAI‑compatible TTS endpoint:

- **Kokoros Project:**  
  Check out the [Kokoros repository](https://github.com/DrMWeigand/Kokoros) for a full implementation of a self-hosted TTS endpoint written in Rust. The project provides all necessary instructions to deploy your own API endpoint.
  
- **Endpoint URL:**  
  After setting up Kokoros, update the `url` parameter in the **OpenAI TTS** node with your server’s address (e.g., `http://<your-server-ip>:3001/v1/audio/speech`).

## Example

Below is an example configuration for the node using the Kokoros server:

- **text:** `"Hello, world!"`
- **model:** `"default_tts_model"`
- **voice:** `"af_sky"`
- **api_key:** `""` (or your valid API key)
- **url:** `"http://localhost:3001/v1/audio/speech"`
- **response_format:** `"mp3"`
- **return_audio:** `True`

This setup sends the text to your TTS endpoint. The endpoint returns an audio file in MP3 format, which is then processed into an audio waveform, ready for playback or further processing in ComfyUI.

## License

This project is licensed under the terms defined in the `LICENSE` file.

## Contributing

Contributions, improvements, and bug fixes are welcome - please submit pull requests or open issues on GitHub.

## Acknowledgements

- [Kokoros](https://github.com/DrMWeigand/Kokoros) by DrMWeigand – for providing a self-hosted OpenAI-compatible TTS endpoint solution.
- The ComfyUI community for creating an extensible framework that makes custom node integration simple.
- Open-source libraries such as Torch, torchaudio, and pydub.
