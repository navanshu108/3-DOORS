from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.domain import Level, Puzzle
import random

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # We drop all rows to allow a clean re-seed
        db.query(Puzzle).delete()
        db.query(Level).delete()
        db.commit()

        print("Seeding database with 5 levels and 10 questions per door...")

        categories = ["Programming", "Logic", "Mathematics", "Systems", "Algorithms"]
        
        levels = []
        for i in range(1, 6):
            levels.append(Level(level_number=i, chapter="Foundation" if i < 3 else "Advanced", title=f"Level {i}"))
        
        db.add_all(levels)
        db.commit()

        puzzles = []
        # Generate 10 Easy and 20 Hard puzzles per level
        for i in range(1, 6):
            level_id = levels[i-1].id
            for j in range(10):
                cat = random.choice(categories)
                puzzles.append(Puzzle(
                    id=f"P-{i}-E{j}",
                    level_id=level_id,
                    category=cat,
                    question=f"EASY PUZZLE [{cat}]: What is {j} + {i}?",
                    question_type="text",
                    difficulty="easy",
                    answer_data=str(j + i)
                ))
            
            for j in range(20):
                cat = random.choice(categories)
                puzzles.append(Puzzle(
                    id=f"P-{i}-H{j}",
                    level_id=level_id,
                    category=cat,
                    question=f"HARD PUZZLE [{cat}]: If x={j} and y={i}, what is x * y?",
                    question_type="text",
                    difficulty="hard",
                    answer_data=str(j * i)
                ))
                
        db.add_all(puzzles)
        db.commit()
        print("Database seeded with 150 puzzles total (10 per door type per level).")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
