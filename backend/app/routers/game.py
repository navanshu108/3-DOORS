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

@router.get("/puzzles/{puzzle_id}")
def get_puzzle(puzzle_id: str, db: Session = Depends(get_db)):
    from app.models.domain import Puzzle
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return {
        "id": puzzle.id,
        "category": puzzle.category,
        "question": puzzle.question
    }

@router.post("/runs/{run_id}/attempt")
def submit_attempt(run_id: str, req: AnswerSubmit, db: Session = Depends(get_db)):
    result = game_engine.validate_answer(db, run_id, req.puzzle_id, req.answer, req.time_taken)
    run = db.query(Run).filter(Run.id == run_id).first()
    return {
        "correct": result["correct"],
        "score_earned": result["score"],
        "grade": result["grade"],
        "run_state": {
            "current_level": run.current_level,
            "mistakes": run.mistakes,
            "door_changes": run.door_changes,
            "score": run.score,
            "status": run.status
        }
    }

@router.post("/runs/{run_id}/abandon")
def abandon_door(run_id: str, db: Session = Depends(get_db)):
    success = game_engine.abandon_door(db, run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")
    run = db.query(Run).filter(Run.id == run_id).first()
    return {
        "run_state": {
            "current_level": run.current_level,
            "mistakes": run.mistakes,
            "door_changes": run.door_changes,
            "score": run.score,
            "status": run.status
        }
    }
