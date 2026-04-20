@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ======================================
echo Building Windows executable for main.py
echo ======================================

for %%I in ("%~dp0..") do (
    set "REPO_ROOT=%%~fI"
    set "APP_NAME=%%~nxI"
)
cd /d "%REPO_ROOT%"

set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo Virtual environment not found. Falling back to system Python.
    set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in this environment.
    exit /b 1
)

set "DIST_DIR=%REPO_ROOT%\dist"
set "BUILD_DIR=%REPO_ROOT%\build"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

echo.
echo Checking build dependencies...
"%PYTHON_EXE%" -c "import PyInstaller, setuptools, wheel" >nul 2>&1
if errorlevel 1 (
    echo Build dependencies are missing. Attempting installation...
    "%PYTHON_EXE%" -m pip install pyinstaller setuptools wheel
    if errorlevel 1 (
        echo ERROR: Failed to install required build dependencies.
        exit /b 1
    )
) else (
    echo Required build dependencies are already installed.
)

if exist "%REPO_ROOT%\requirements.txt" (
    echo Installing application dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install -r "%REPO_ROOT%\requirements.txt"
    if errorlevel 1 (
        echo ERROR: Failed to install application dependencies.
        exit /b 1
    )
) else (
    echo No requirements.txt found. Continuing with the current environment.
)

echo.
echo Cleaning previous executable...
if exist "%DIST_DIR%\%APP_NAME%.exe" del /f /q "%DIST_DIR%\%APP_NAME%.exe" >nul 2>&1

echo.
echo Running PyInstaller...
"%PYTHON_EXE%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --name "%APP_NAME%" ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_DIR%" ^
    --specpath "%BUILD_DIR%" ^
    --paths "%REPO_ROOT%\src" ^
    --collect-submodules paf ^
    --hidden-import paf.modules.factory_template.simulated ^
    --add-data "%REPO_ROOT%\src\paf\modules\webserver\www\index.html;paf\modules\webserver\www" ^
    --add-data "%REPO_ROOT%\src\paf\modules\webserver\www\styles.css;paf\modules\webserver\www" ^
    --add-data "%REPO_ROOT%\src\paf\modules\webserver\www\app.js;paf\modules\webserver\www" ^
    "%REPO_ROOT%\src\main.py"

if errorlevel 1 (
    echo ERROR: Build failed.
    exit /b 1
)

if exist "%DIST_DIR%\%APP_NAME%.exe" (
    echo.
    echo Build completed successfully.
    echo Executable created at:
    echo %DIST_DIR%\%APP_NAME%.exe
    exit /b 0
)

echo ERROR: Build finished but %APP_NAME%.exe was not found in the dist folder.
exit /b 1
