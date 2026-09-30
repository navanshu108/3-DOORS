import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

# Backend Core Files
write_file('backend/app/core/config.py', """
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "3 DOORS"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./3doors.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-for-hackathon-demo")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"

settings = Settings()
""")

write_file('backend/app/core/database.py', """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite fallback for local development if PostgreSQL is unavailable
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

write_file('backend/app/models/domain.py', """
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True) # Nullable for guest
    is_guest = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True, index=True)
    level_number = Column(Integer, unique=True, index=True)
    chapter = Column(String)
    title = Column(String)

class Puzzle(Base):
    __tablename__ = "puzzles"
    id = Column(String, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"))
    category = Column(String)
    question = Column(Text)
    question_type = Column(String) # 'text', 'numeric', 'multiple_choice'
    difficulty = Column(String) # 'easy', 'hard'
    answer_data = Column(String) # Store securely
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Run(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    seed = Column(String)
    current_level = Column(Integer, default=1)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_time = Column(Float, default=0.0)
    mistakes = Column(Integer, default=0)
    efficiency = Column(Float, default=0.0)
    status = Column(String, default="active") # active, completed, failed

class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    puzzle_id = Column(String, ForeignKey("puzzles.id"))
    correct = Column(Boolean)
    time_taken = Column(Float)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class LeaderboardRecord(Base):
    __tablename__ = "leaderboard_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    run_id = Column(String, ForeignKey("runs.id"))
    total_time = Column(Float)
    mistakes = Column(Integer)
    accuracy = Column(Float)
    efficiency = Column(Float)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
""")

write_file('backend/app/schemas/schemas.py', """
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RunCreate(BaseModel):
    user_id: int
    seed: Optional[str] = None

class AnswerSubmit(BaseModel):
    puzzle_id: str
    answer: str
    time_taken: float

class DoorView(BaseModel):
    puzzle_id: str
    category: str
    question: str
    question_type: str

class LevelView(BaseModel):
    level_number: int
    title: str
    doors: List[DoorView]

class RunState(BaseModel):
    run_id: str
    current_level: int
    mistakes: int
    status: str
""")

write_file('backend/app/services/game_engine.py', """
import random
import uuid
from sqlalchemy.orm import Session
from app.models.domain import Run, Level, Puzzle, Attempt
from app.schemas.schemas import LevelView, DoorView

def create_run(db: Session, user_id: int, seed: str = None) -> Run:
    if not seed:
        seed = str(random.randint(100000, 999999))
    run_id = f"RUN-{uuid.uuid4().hex[:6].upper()}"
    run = Run(id=run_id, user_id=user_id, seed=seed)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def generate_level(db: Session, run: Run, level_number: int) -> LevelView:
    level = db.query(Level).filter(Level.level_number == level_number).first()
    if not level:
        # Fallback level for prototype
        level = Level(level_number=level_number, title=f"Level {level_number}")
    
    # Deterministic generation based on seed and level
    random.seed(f"{run.seed}-{level_number}")
    
    # Get puzzles
    easy_puzzles = db.query(Puzzle).filter(Puzzle.difficulty == 'easy', Puzzle.level_id == level.id).all()
    hard_puzzles = db.query(Puzzle).filter(Puzzle.difficulty == 'hard', Puzzle.level_id == level.id).all()
    
    if not easy_puzzles or len(hard_puzzles) < 2:
        # Fallback logic if DB is empty
        easy = Puzzle(id=f"P-{level_number}-E", category="Logic", question="Is true == true?", question_type="multiple_choice", difficulty="easy", answer_data="true")
        hard1 = Puzzle(id=f"P-{level_number}-H1", category="Algorithms", question="O(n) or O(n^2)?", question_type="text", difficulty="hard", answer_data="O(n^2)")
        hard2 = Puzzle(id=f"P-{level_number}-H2", category="Mathematics", question="5 + 5?", question_type="numeric", difficulty="hard", answer_data="10")
    else:
        easy = random.choice(easy_puzzles)
        hard1, hard2 = random.sample(hard_puzzles, 2)
        
    doors = [easy, hard1, hard2]
    random.shuffle(doors)
    
    door_views = [
        DoorView(puzzle_id=d.id, category=d.category, question=d.question, question_type=d.question_type)
        for d in doors
    ]
    
    return LevelView(level_number=level_number, title=level.title, doors=door_views)

def validate_answer(db: Session, run_id: str, puzzle_id: str, answer: str, time_taken: float) -> bool:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        return False
        
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    # Simple fallback check
    correct = False
    if puzzle:
        correct = str(puzzle.answer_data).strip().lower() == str(answer).strip().lower()
    else:
        if answer.lower() in ["true", "o(n^2)", "10", "8", "on", "32", "9", "0.72"]: # tutorial answers
            correct = True

    attempt = Attempt(run_id=run.id, level_id=run.current_level, puzzle_id=puzzle_id, correct=correct, time_taken=time_taken)
    db.add(attempt)
    
    if not correct:
        run.mistakes += 1
    else:
        run.current_level += 1
        
    db.commit()
    return correct
""")

write_file('backend/app/routers/game.py', """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RunCreate, RunState, LevelView, AnswerSubmit
from app.services import game_engine
from app.models.domain import Run, User

router = APIRouter()

@router.post("/runs")
def start_run(req: RunCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        # Auto-create guest for demo
        user = User(id=req.user_id, username=f"Guest_{req.user_id}", is_guest=True)
        db.add(user)
        db.commit()
    run = game_engine.create_run(db, req.user_id, req.seed)
    return {"run_id": run.id, "seed": run.seed}

@router.get("/runs/{run_id}/level")
def get_current_level(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    level_view = game_engine.generate_level(db, run, run.current_level)
    return level_view

@router.post("/runs/{run_id}/attempt")
def submit_attempt(run_id: str, req: AnswerSubmit, db: Session = Depends(get_db)):
    is_correct = game_engine.validate_answer(db, run_id, req.puzzle_id, req.answer, req.time_taken)
    run = db.query(Run).filter(Run.id == run_id).first()
    return {
        "correct": is_correct,
        "run_state": {
            "current_level": run.current_level,
            "mistakes": run.mistakes,
            "status": run.status
        }
    }
""")

write_file('backend/app/main.py', """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import game
from app.core.database import engine, Base
from app.models import domain

Base.metadata.create_all(bind=engine)

app = FastAPI(title="3 DOORS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
""")

print("Backend scaffolded successfully")
