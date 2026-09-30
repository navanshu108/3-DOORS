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
