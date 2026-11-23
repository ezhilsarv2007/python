@echo off
setlocal
cd /d "%~dp0"

echo ====================================================================
echo Starting Software Release Risk Scoring System...
echo ====================================================================

if exist "%~dp0.venv\Scripts\python.exe" goto use_venv
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 goto use_py
if exist "C:\Users\EZHIL\AppData\Roaming\uv\python\cpython-3.14.3-windows-x86_64-none\python.exe" goto use_uv_python
goto use_default_python

:use_venv
echo [INFO] Running with project virtual environment (.venv)
"%~dp0.venv\Scripts\python.exe" app.py
goto done

:use_py
echo [INFO] Running with Python Launcher (py)
py app.py
goto done

:use_uv_python
echo [INFO] Running with Python 3.14
"C:\Users\EZHIL\AppData\Roaming\uv\python\cpython-3.14.3-windows-x86_64-none\python.exe" app.py
goto done

:use_default_python
echo [INFO] Running with default python
python app.py
goto done

:done
pause
endlocal
