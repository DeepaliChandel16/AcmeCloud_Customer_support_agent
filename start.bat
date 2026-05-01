@echo off
echo Starting AcmeCloud Support Agent...

powershell -Command "if (!(Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Host 'ERROR: Ollama is not installed or not in PATH.'; exit 1 }"
if %errorlevel% neq 0 exit /b 1

powershell -Command "if (!(Get-Process -Name ollama -ErrorAction SilentlyContinue)) { Write-Host 'Starting Ollama...'; Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden; Start-Sleep 3 } else { Write-Host 'Ollama is already running.' }"

echo Launching Streamlit app (logs visible in this window)...
cd /d "%~dp0"
start "AcmeCloud Logs" cmd /k "python -m streamlit run src/ui/app.py --server.port 8501"
powershell -Command "Start-Sleep 5; Start-Process 'http://localhost:8501'"
echo App is running at http://localhost:8501
echo Live logs are visible in the "AcmeCloud Logs" window.

if "%1"=="--devui" (
    echo.
    echo Starting DevUI debug server on port 8080...
    start "DevUI" cmd /k "python devui_server.py"
    powershell -Command "Start-Sleep 3; Start-Process 'http://localhost:8080'"
    echo DevUI is running at http://localhost:8080
)
