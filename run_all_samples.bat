@echo off
REM Run all sample .asm programs sequentially (Windows)
SET SAMP_DIR=tests\sample_programs
SET VENV_DIR=sim_venv

IF EXIST %VENV_DIR%\Scripts\activate.bat (
  echo Activating virtual environment %VENV_DIR%
  call %VENV_DIR%\Scripts\activate.bat
)

IF NOT EXIST %SAMP_DIR% (
  echo Sample programs directory not found: %SAMP_DIR%
  exit /b 1
)

for %%f in (%SAMP_DIR%\*.asm) do (
  echo.
  echo ===== Running: %%~nxf =====
  python main.py "%%f"
  echo ===== Finished: %%~nxf =====
)

echo All sample programs executed.
