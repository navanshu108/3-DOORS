# 3 DOORS - Hackathon Prototype

## Project Overview
3 DOORS is a competitive engineering puzzle game where players don't just solve problems—they learn to identify the smartest path under pressure. This prototype demonstrates the core game loop, including the 3-door mechanic, deterministic level generation, and scoring.

## Architecture
- **Frontend**: React, TypeScript, Tailwind CSS, Framer Motion, Vite
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (Development fallback implemented as requested)

## Quick Start (Local Development)

### 1. Backend Setup
The backend is located in the `backend/` directory and manages game state, level generation, and answer validation.
```bash
cd backend
uv sync
uv add sqlalchemy
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*(The backend will run on http://localhost:8000)*

### 2. Frontend Setup
The frontend is a React application built with Vite in the `frontend/` directory.
```bash
cd frontend
npm install
npm run dev
```
*(The frontend will run on http://localhost:5173)*

## How to play
1. Open the frontend in your browser.
2. Click **START CHALLENGE**.
3. You will be presented with 3 doors. Read the short descriptions.
4. Try to determine which door is the **EASIEST**, click it, and solve the problem in the terminal.
5. Finish all levels to get your score and efficiency metrics.

## Notes for Hackathon Demo
- The backend handles deterministic seed generation, so sharing the `RUN ID` allows for Ghost Racing.
- Answer validation is strictly server-side.
- The UI includes animations built with Framer Motion, matching the Cyberpunk Terminal theme.
