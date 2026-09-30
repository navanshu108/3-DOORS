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
    door_changes = Column(Integer, default=0)
    efficiency = Column(Float, default=0.0)
    score = Column(Integer, default=0)
    status = Column(String, default="active") # active, completed, failed

class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    puzzle_id = Column(String, ForeignKey("puzzles.id"))
    correct = Column(Boolean)
    time_taken = Column(Float)
    score = Column(Integer, default=0)
    grade = Column(String, nullable=True)
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
