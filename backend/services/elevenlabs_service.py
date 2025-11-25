from elevenlabs.client import ElevenLabs
from ..config import settings
import os
import uuid

# Initialize client
# Note: In a real async app, we might want to use the async client or run in executor
client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

class ElevenLabsService:
    def __init__(self):
        self.output_dir = "static/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_voices(self):
        try:
            response = client.voices.get_all()
            return response.voices
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []

    def generate_audio(self, text: str, voice_id: str) -> str:
        """Generate audio without timestamps (legacy method)"""
        result = self.generate_audio_with_timestamps(text, voice_id)
        return result[0] if result else ""
    
    def generate_audio_with_timestamps(self, text: str, voice_id: str) -> tuple[str, dict | None]:
        """Generate audio and return (audio_path, alignment_data)
        
        Returns:
            tuple: (audio_path, alignment_data) where alignment_data contains:
                - characters: list of characters
                - character_start_times_seconds: list of start times
                - character_end_times_seconds: list of end times
        """
        try:
            print(f"🎙️  ElevenLabs: Generating audio with timestamps for voice '{voice_id}'")
            print(f"📝 Text length: {len(text)} characters")
            
            # Generate audio with timestamps using the newer SDK method
            response = client.text_to_speech.convert_with_timestamps(
                voice_id=voice_id,
                text=text,
                model_id="eleven_turbo_v2_5"
            )
            
            # The response contains both audio_base64 and alignment data
            import base64
            audio_bytes = base64.b64decode(response.audio_base64)
            
            # Save audio to file
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            print(f"💾 Saving audio to: {filepath}")
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            
            # Extract alignment data
            alignment_data = None
            if hasattr(response, 'alignment') and response.alignment:
                alignment_data = {
                    "characters": list(response.alignment.characters),
                    "character_start_times_seconds": list(response.alignment.character_start_times_seconds),
                    "character_end_times_seconds": list(response.alignment.character_end_times_seconds)
                }
                print(f"✅ Audio saved with {len(alignment_data['characters'])} character timestamps")
            else:
                print(f"✅ Audio saved (no alignment data available)")
            
            return (f"/static/audio/{filename}", alignment_data)
            
        except Exception as e:
            print(f"❌ Error generating audio with timestamps: {e}")
            import traceback
            traceback.print_exc()
            return ("", None)

elevenlabs_service = ElevenLabsService()
