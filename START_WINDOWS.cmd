@echo off
cd /d "%~dp0"
py -3.12 --version >nul 2>&1
if errorlevel 1 (
 python run_inventory.py %*
) else (
 py -3.12 run_inventory.py %*
)
pause


