@echo off
setlocal

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not available in PATH.
    exit /b 1
)

echo [2/3] Installing/Updating PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    exit /b 1
)

echo [3/3] Building EXE...
python -m PyInstaller --noconfirm --onefile --windowed --name Calculator gui_calculator.py
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo.
echo Done. EXE created at: dist\Calculator.exe
endlocal
