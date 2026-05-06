@echo off
echo ==========================================
echo   DEMARRAGE : STUDENT PERFORMANCE PIPELINE
echo ==========================================

start "BACKEND - Flask" cmd /k "cd server && .\venv\Scripts\python.exe app.py"
ping 127.0.0.1 -n 6 > nul
start "FRONTEND - Vite" cmd /k "cd client && npm run dev"

echo.
echo Serveurs lances ! 
echo PC: http://localhost:5173
echo Mobile: http://100.97.112.89:5173
echo.
pause
