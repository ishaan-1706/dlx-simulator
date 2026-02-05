@echo off
REM add_program.bat - copy a user .asm into tests\sample_programs
IF "%1"=="" (
  echo Usage: %~nx0 C:\path\to\your_program.asm [optional-destination-name.asm]
  exit /b 2
)
SET SRC=%~1
IF NOT EXIST "%SRC%" (
  echo Source file not found: %SRC%
  exit /b 1
)
IF "%2"=="" (
  SET DEST_NAME=%~nx1
) ELSE (
  SET DEST_NAME=%2
)
SET DEST_DIR=user_programs
IF NOT EXIST %DEST_DIR% mkdir %DEST_DIR%
copy "%SRC%" "%DEST_DIR%\%DEST_NAME%"
echo Copied %SRC% -> %DEST_DIR%\%DEST_NAME%
echo You can run it with: run_user.bat %DEST_NAME% or: python %DEST_DIR%\%DEST_NAME%
