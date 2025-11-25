from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import Story, Page, User
from ..schemas import Story as StorySchema, StoryCreate
from ..services.gemini_service import gemini_service
from ..services.elevenlabs_service import elevenlabs_service

router = APIRouter(prefix="/stories", tags=["stories"])

async def generate_story_content(story_id: int, theme: str, db: AsyncSession):
    # 1. Generate Text
    pages_data = await gemini_service.generate_story(theme)
    
    # Re-fetch story to ensure session is active
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    
    if not story:
        return

    for p_data in pages_data:
        # 2. Generate Image
        image_url = await gemini_service.generate_image(p_data.get("image_prompt", ""))
        
        # 3. Generate Audio (using a default voice for now)
        # In real app, user would select voice

        
        new_page = Page(
            story_id=story.id,
            page_number=p_data.get("page_number"),
            text_content=p_data.get("text_content"),
            image_url=image_url,
            audio_url=None  # Audio will be generated on demand via separate endpoint
        )
        db.add(new_page)
    
    await db.commit()

@router.post("/", response_model=StorySchema)
async def create_story(story_in: StoryCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Create Story record
    # For MVP, assuming user_id=1 (we haven't implemented full auth yet)
    # In real app, get current_user
    title = story_in.title or f"Story about {story_in.theme}"
    new_story = Story(title=title, theme=story_in.theme, user_id=1) 
    db.add(new_story)
    await db.commit()
    await db.refresh(new_story)
    
    # Trigger generation in background
    # Note: Passing async session to background task is tricky. 
    # Better to create new session in task or handle it carefully.
    # For this MVP, I'll run it inline to ensure it works, or use a simple await.
    # To avoid blocking, we should really use a task queue (Celery/Arq).
    # For now, let's await it to show immediate results in this demo context, 
    # or just return the empty story and let frontend poll.
    
    # Let's await it for simplicity of the "demo" feel, although it blocks.
    await generate_story_content(new_story.id, story_in.theme, db)
    
    # Refresh to get pages
    result = await db.execute(select(Story).options(selectinload(Story.pages)).where(Story.id == new_story.id))
    story = result.scalar_one()
    return story

@router.get("/", response_model=list[StorySchema])
async def list_stories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Story).options(selectinload(Story.pages)))
    stories = result.scalars().all()
    return stories

@router.get("/{story_id}", response_model=StorySchema)
async def get_story(story_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Story).options(selectinload(Story.pages)).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.post("/{story_id}/generate-audio", response_model=StorySchema)
async def generate_audio_for_story(story_id: int, db: AsyncSession = Depends(get_db)):
    """Generate audio for each page of the story using ElevenLabs.
    Returns the updated story with audio URLs.
    """
    print(f"🎵 Generating audio for story {story_id}")
    # Load story with pages
    result = await db.execute(
        select(Story).options(selectinload(Story.pages)).where(Story.id == story_id)
    )
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    print(f"📖 Story has {len(story.pages)} pages")
    # Generate audio for pages lacking audio_url
    # Using Rachel voice (ID: 21m00Tcm4TlvDq8ikWAM) - in production, this could be user-selected
    for page in story.pages:
        if not page.audio_url or page.audio_url == "":
            print(f"🔊 Generating audio for page {page.page_number}: {page.text_content[:50]}...")
            audio_path, alignment_data = elevenlabs_service.generate_audio_with_timestamps(
                page.text_content, 
                "21m00Tcm4TlvDq8ikWAM"
            )
            print(f"✅ Audio generated: {audio_path}")
            if alignment_data:
                print(f"📊 Alignment data: {len(alignment_data.get('characters', []))} characters")
            page.audio_url = audio_path
            page.alignment_data = alignment_data  # Store alignment data as JSON
            db.add(page)
        else:
            print(f"⏭️  Page {page.page_number} already has audio: {page.audio_url}")
    
    await db.commit()
    await db.refresh(story)
    print(f"✨ Audio generation complete for story {story_id}")
    return story
