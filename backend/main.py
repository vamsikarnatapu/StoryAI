from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import stories
from .database import engine, Base, AsyncSessionLocal
from .models import User
from sqlalchemy import select

app = FastAPI(title="MyStory AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(stories.router)

@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create dummy user
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == 1))
        user = result.scalar_one_or_none()
        if not user:
            new_user = User(email="test@example.com", hashed_password="hashed_secret")
            db.add(new_user)
            await db.commit()

@app.get("/")
async def root():
    return {"message": "Welcome to MyStory AI API"}
