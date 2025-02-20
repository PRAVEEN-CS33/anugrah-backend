import base64
import io

from .audiototext import audio2text

def base64_transcribe(base64_audio, src, dest, desc=False):
    try:
        audio_data = base64.b64decode(base64_audio)
        audio_stream = io.BytesIO(audio_data)
        path = "data/base64/temp_audio.wav"
        with open(path, "wb") as f:
            f.write(audio_stream.read())
        recognized_text = audio2text(path, src, dest, base_path="data/base64", desc=desc)

        return recognized_text
    except Exception as e:
        print(f"Error saving base64 audio: {e}")
        raise ValueError("Error processing the base64 audio.") from e