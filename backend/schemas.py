from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VoiceProfileBase(BaseModel):
    name: str
    elevenlabs_voice_id: str

class VoiceProfileCreate(VoiceProfileBase):
    pass

class VoiceProfile(VoiceProfileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PageBase(BaseModel):
    page_number: int
    text_content: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    alignment_data: Optional[Any] = None

class PageCreate(PageBase):
    pass

class Page(PageBase):
    id: int
    story_id: int

    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    title: str
    theme: str

class StoryCreate(BaseModel):
    theme: str
    title: Optional[str] = None

class Story(StoryBase):
    id: int
    user_id: int
    created_at: datetime
    pages: List[Page] = []

    class Config:
        from_attributes = True
