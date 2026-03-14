@echo off
echo Stopping Uncapped Production Control...
taskkill /f /fi "WINDOWTITLE eq Uncapped*" >nul 2>&1
taskkill /f /fi "IMAGENAME eq python.exe" /fi "MODULES eq uvicorn" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080.*LISTENING"') do taskkill /f /pid %%a >nul 2>&1
echo Done.
pause
