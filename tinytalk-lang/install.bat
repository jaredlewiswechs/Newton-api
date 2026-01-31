@echo off
echo TinyTalk Language Installer for Windows
echo ========================================
echo.

REM Check for GCC (MinGW)
where gcc >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: GCC not found
    echo.
    echo Please install MinGW-w64:
    echo 1. Download from: https://www.mingw-w64.org/downloads/
    echo 2. Or install via Chocolatey: choco install mingw
    echo 3. Add to PATH and restart this script
    pause
    exit /b 1
)

REM Check for Make
where make >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Make not found
    echo Install via: choco install make
    pause
    exit /b 1
)

REM Build
echo Building TinyTalk...
make clean
make

if %errorlevel% equ 0 (
    echo.
    echo ✓ Build successful!
    echo ✓ Binary: %cd%\tinytalk.exe
    echo.
    echo Testing installation...
    if exist examples\hello_world.tt (
        tinytalk.exe run examples\hello_world.tt
    ) else (
        echo Warning: examples\hello_world.tt not found, skipping test
        echo Installation complete, but test file missing
    )
    echo.
    echo To use anywhere, add this folder to your PATH:
    echo   setx PATH "%%PATH%%;%cd%"
) else (
    echo.
    echo ✗ Build failed
    pause
    exit /b 1
)

pause
