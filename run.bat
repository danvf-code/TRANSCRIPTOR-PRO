@echo off
cd /d %~dp0
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
if not exist .env (
  copy .env.example .env
  notepad .env
)
start http://localhost:8000
uvicorn app.main:app
