@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
python .\app.py

REM Optional: pause the window so it doesn't close immediately
pause
