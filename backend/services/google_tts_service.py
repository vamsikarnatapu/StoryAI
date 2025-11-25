import os
import uuid
from google.cloud import texttospeech
from ..config import settings

# Ensure output directory exists
AUDIO_DIR = 'static/audio'
os.makedirs(AUDIO_DIR, exist_ok=True)

class GoogleTTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        # Default voice parameters; can be customized later
        self.voice = texttospeech.VoiceSelectionParams(
            language_code='en-US',
            name='en-US-Wavenet-D'
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

    def synthesize(self, text: str) -> str:
        """Generate speech audio for the given text and return a URL path.

        The audio file is saved under `static/audio` and the returned path is
        suitable for serving via FastAPI's StaticFiles mount.
        """
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config
        )
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        with open(filepath, "wb") as out:
            out.write(response.audio_content)
        return f"/static/audio/{filename}"

google_tts_service = GoogleTTSService()
