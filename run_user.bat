@echo off
REM run_user.bat - run a user .asm from user_programs
SET USER_DIR=user_programs

IF NOT EXIST %USER_DIR% (
  echo No user_programs directory found. Create it and place your .asm files there, or use add_program.bat to add one.
  exit /b 1
)

IF "%1" NEQ "" (
  SET FILE=%1
  IF NOT EXIST %USER_DIR%\%FILE% (
    echo File not found: %USER_DIR%\%FILE%
    exit /b 1
  )
  echo Running %USER_DIR%\%FILE%
  python %USER_DIR%\%FILE%
  EXIT /B %ERRORLEVEL%
)

echo Available user programs:
for %%f in (%USER_DIR%\*.asm) do echo  %%~nxf

set /p sel=Enter file name to run (e.g. myprog.asm): 
IF "%sel%"=="" (
  echo No selection
  exit /b 1
)
IF NOT EXIST %USER_DIR%\%sel% (
  echo File not found: %USER_DIR%\%sel%
  exit /b 1
)
echo Running %USER_DIR%\%sel%
python %USER_DIR%\%sel%
