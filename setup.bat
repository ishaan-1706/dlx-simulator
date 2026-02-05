@echo off
REM setup.bat - Windows quick setup for DLX simulator
SET VENV_DIR=sim_venv
echo Creating virtual environment in %VENV_DIR%...
python -m venv %VENV_DIR%
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat
echo Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete. To run the simulator:
echo   call %VENV_DIR%\Scripts\activate.bat
echo   python main.py tests\sample_programs\simple_branch.asm
echo.
echo If you need a single-click run of a sample, try: run_sample.py
pause
