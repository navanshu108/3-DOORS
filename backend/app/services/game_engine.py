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
        level = Level(level_number=level_number, title=f"Level {level_number}")
    
    # Deterministic generation based on seed and level
    random.seed(f"{run.seed}-{level_number}")
    
    # Get puzzles across ALL levels to maximize randomness
    easy_puzzles = db.query(Puzzle).filter(Puzzle.difficulty == 'easy').all()
    hard_puzzles = db.query(Puzzle).filter(Puzzle.difficulty == 'hard').all()
    
    if not easy_puzzles or len(hard_puzzles) < 2:
        # Fallback logic if DB is empty
        easy = Puzzle(id=f"P-{level_number}-E", category="Logic", question="Is true == true?", question_type="multiple_choice", difficulty="easy", answer_data="true")
        hard1 = Puzzle(id=f"P-{level_number}-H1", category="Algorithms", question="O(n) or O(n^2)?", question_type="text", difficulty="hard", answer_data="O(n^2)")
        hard2 = Puzzle(id=f"P-{level_number}-H2", category="Mathematics", question="5 + 5?", question_type="numeric", difficulty="hard", answer_data="10")
    else:
        # We can implement probability constraints here if needed, but selecting from a large pool ensures low repetition
        easy = random.choice(easy_puzzles)
        hard1, hard2 = random.sample(hard_puzzles, 2)
        
    doors = [easy, hard1, hard2]
    random.shuffle(doors)
    
    door_views = [
        DoorView(puzzle_id=d.id, category=d.category, question=d.question, question_type=d.question_type)
        for d in doors
    ]
    
    return LevelView(level_number=level_number, title=level.title, doors=door_views)

def calculate_score_and_grade(time_taken: float, mistakes: int) -> tuple[int, str]:
    # Keeping this for attempt grade, but we use strict +3 / -1 for points now
    if time_taken <= 10.0:
        grade = "S"
    elif time_taken <= 20.0:
        grade = "A"
    elif time_taken <= 35.0:
        grade = "B"
    elif time_taken <= 60.0:
        grade = "C"
    else:
        grade = "D"
    return 3, grade # Always return 3 points for a correct answer as requested

def validate_answer(db: Session, run_id: str, puzzle_id: str, answer: str, time_taken: float) -> dict:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        return {"correct": False, "score": 0, "grade": None}
        
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    correct = False
    if puzzle:
        correct = str(puzzle.answer_data).strip().lower() == str(answer).strip().lower()
    else:
        if answer.lower() in ["true", "o(n^2)", "10", "8", "on", "32", "9", "0.72"]:
            correct = True

    score = 0
    grade = None
    if correct:
        score, grade = calculate_score_and_grade(time_taken, run.mistakes)
        run.score += score
        run.current_level += 1
    else:
        score = -1
        run.score += score
        run.mistakes += 1

    attempt = Attempt(run_id=run.id, level_id=run.current_level, puzzle_id=puzzle_id, correct=correct, time_taken=time_taken, score=score, grade=grade)
    db.add(attempt)
    db.commit()
    
    return {"correct": correct, "score": score, "grade": grade}

def abandon_door(db: Session, run_id: str) -> bool:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        return False
    
    run.score -= 1
    run.door_changes += 1
    db.commit()
    return True
