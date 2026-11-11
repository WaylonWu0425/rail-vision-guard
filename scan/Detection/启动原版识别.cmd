@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
  "%LOCALAPPDATA%\Python\bin\python.exe" original_recognition.py
) else (
  py -3 original_recognition.py
)
pause
