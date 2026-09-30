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
    door_changes: int
    score: int
    status: str

class AttemptResponse(BaseModel):
    correct: bool
    score_earned: int
    grade: Optional[str] = None
    run_state: RunState
