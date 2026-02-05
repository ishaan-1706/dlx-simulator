@echo off
REM remove_program.bat - archive or remove sample programs
SET USER_DIR=user_programs

IF "%1"=="" (
  echo Usage: %~nx0 filename.asm ^| --all
  exit /b 2
)

IF "%1"=="--all" (
  echo Permanently deleting all .asm files in %USER_DIR%
  del /q %USER_DIR%\*.asm 2>nul || echo No files to delete
  echo Done.
  exit /b 0
)

IF NOT EXIST %USER_DIR%\%1 (
  echo File not found: %USER_DIR%\%1
  exit /b 1
)

del /q %USER_DIR%\%1
echo Deleted %USER_DIR%\%1
