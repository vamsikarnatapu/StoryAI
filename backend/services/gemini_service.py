import google.generativeai as genai
from ..config import settings
import json

genai.configure(api_key=settings.GOOGLE_API_KEY)

class GeminiService:
    def __init__(self):
        self.text_model = genai.GenerativeModel('gemini-2.5-pro')
        
    async def generate_story(self, theme: str):
        prompt = f"""
        Write a short children's story about {theme}. 
        The story should be 3-5 pages long.
        Return ONLY a valid JSON array where each object represents a page.
        Format:
        [
            {{
                "page_number": 1,
                "text_content": "Story text for page 1...",
                "image_prompt": "A detailed description of the scene for an illustration..."
            }},
            ...
        ]
        """
        response = await self.text_model.generate_content_async(prompt)
        try:
            # Clean up potential markdown code blocks
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return []

    async def generate_image(self, prompt: str) -> str:
        # Placeholder implementation – returns a generated placeholder image URL.
        # In production replace with Nano Banana SDK call.
        safe_prompt = prompt.replace(' ', '+')
        return f"https://placehold.co/600x400?text={safe_prompt}"

gemini_service = GeminiService()
