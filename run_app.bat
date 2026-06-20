@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo Ambiente virtual nao encontrado. Crie com: py -m venv .venv
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
streamlit run app.py
pause
