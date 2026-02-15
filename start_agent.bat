@echo off
echo Starting OpenCLAW Literary Agent 2...
cd /d "%~dp0"
call .venv\Scripts\activate
python main.py
pause
