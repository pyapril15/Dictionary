@echo off
echo ============================================
echo     Dictionary Application - Build Script
echo              Version 1.0.0
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available!
    echo Please ensure pip is installed with Python.
    echo.
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
echo This may take a few minutes for first-time installation...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies!
    echo Please check your internet connection and try again.
    echo.
    echo Trying to install core dependencies individually...
    pip install PySide6>=6.5.0
    pip install nltk>=3.8
    pip install requests>=2.28.0
    pip install pyinstaller>=6.0.0

    if errorlevel 1 (
        echo Error: Could not install core dependencies!
        pause
        exit /b 1
    )
)

echo.
echo Dependencies installed successfully!
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo Error: main.py not found!
    echo Please ensure you are running this script from the project directory.
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

REM Check if src directory exists
if not exist "src" (
    echo Error: src directory not found!
    echo Please ensure you are running this script from the project directory.
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

REM Create resources directory structure if it doesn't exist
if not exist "resources" (
    echo Creating resources directory structure...
    mkdir resources
    mkdir resources\icons
    mkdir resources\styles
    echo Please place your app_icon.ico file in resources\icons\ directory
    echo Please place your stylesheet.qss file in resources\styles\ directory
    echo.
)

if not exist "resources\icons" mkdir resources\icons
if not exist "resources\styles" mkdir resources\styles

REM Check for icon file
if not exist "resources\icons\app_icon.ico" (
    echo Warning: Icon file not found at resources\icons\app_icon.ico
    echo The executable will be built without a custom icon.
    echo You can add the icon file later and rebuild.
    echo.
)

REM Check for stylesheet
if not exist "resources\styles\stylesheet.qss" (
    echo Warning: Stylesheet not found at resources\styles\stylesheet.qss
    echo The application may not have custom styling.
    echo.
)

REM Download NLTK data
echo Downloading required NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK data downloaded successfully!')"
if errorlevel 1 (
    echo Warning: Failed to download NLTK data.
    echo NLTK data will be downloaded on first application run.
    echo.
)

REM Test the application before building
echo Testing the application...
python -c "import main; print('Application import test: OK')"
if errorlevel 1 (
    echo Error: Application failed import test!
    echo Please check for syntax errors in main.py and dependencies.
    echo.
    pause
    exit /b 1
)

echo Application test passed!
echo.

echo Cleaning previous build files...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "Dictionary.spec" del "Dictionary.spec"
echo.

echo ============================================
echo       Building Dictionary Application
echo ============================================
echo.
echo This process will:
echo • Create a standalone executable (.exe)
echo • Include all PySide6 dependencies
echo • Bundle NLTK data and models
echo • Include resources (icons, styles)
echo • Optimize for performance
echo • Create distribution files
echo.
echo Please wait... This may take 10-15 minutes
echo.

REM Build using Python setup script
python setup.py
if errorlevel 1 (
    echo.
    echo Error: Build failed!
    echo Trying alternative build method...
    echo.

    REM Alternative build using direct PyInstaller command
    if exist "resources\icons\app_icon.ico" (
        echo Building with custom icon...
        pyinstaller --onefile ^
                    --windowed ^
                    --name=Dictionary ^
                    --icon=resources/icons/app_icon.ico ^
                    --distpath=dist ^
                    --workpath=build ^
                    --clean ^
                    --noconfirm ^
                    --optimize=2 ^
                    --noupx ^
                    --hidden-import=PySide6 ^
                    --hidden-import=PySide6.QtCore ^
                    --hidden-import=PySide6.QtGui ^
                    --hidden-import=PySide6.QtWidgets ^
                    --hidden-import=shiboken6 ^
                    --hidden-import=nltk ^
                    --hidden-import=nltk.data ^
                    --hidden-import=nltk.corpus ^
                    --hidden-import=nltk.corpus.reader.wordnet ^
                    --hidden-import=nltk.tokenize ^
                    --hidden-import=requests ^
                    --hidden-import=src.app_logic.app_config ^
                    --hidden-import=src.app_logic.log ^
                    --hidden-import=src.app_services.github_service ^
                    --hidden-import=src.app_ui.main_window ^
                    --hidden-import=src.app_ui.ui_update_window ^
                    --collect-data=PySide6 ^
                    --collect-data=nltk ^
                    --add-data=resources;resources ^
                    --add-data=src;src ^
                    --exclude-module=tkinter ^
                    --exclude-module=matplotlib ^
                    main.py
    ) else (
        echo Building without custom icon...
        pyinstaller --onefile ^
                    --windowed ^
                    --name=Dictionary ^
                    --distpath=dist ^
                    --workpath=build ^
                    --clean ^
                    --noconfirm ^
                    --optimize=2 ^
                    --noupx ^
                    --hidden-import=PySide6 ^
                    --hidden-import=PySide6.QtCore ^
                    --hidden-import=PySide6.QtGui ^
                    --hidden-import=PySide6.QtWidgets ^
                    --hidden-import=shiboken6 ^
                    --hidden-import=nltk ^
                    --hidden-import=nltk.data ^
                    --hidden-import=nltk.corpus ^
                    --hidden-import=nltk.corpus.reader.wordnet ^
                    --hidden-import=nltk.tokenize ^
                    --hidden-import=requests ^
                    --hidden-import=src.app_logic.app_config ^
                    --hidden-import=src.app_logic.log ^
                    --hidden-import=src.app_services.github_service ^
                    --hidden-import=src.app_ui.main_window ^
                    --hidden-import=src.app_ui.ui_update_window ^
                    --collect-data=PySide6 ^
                    --collect-data=nltk ^
                    --add-data=resources;resources ^
                    --add-data=src;src ^
                    --exclude-module=tkinter ^
                    --exclude-module=matplotlib ^
                    main.py
    )

    if errorlevel 1 (
        echo.
        echo Error: Both build methods failed!
        echo Please check the error messages above and try the following:
        echo 1. Ensure all dependencies are installed correctly
        echo 2. Check that main.py has no syntax errors
        echo 3. Verify that PyInstaller is properly installed
        echo 4. Make sure src and resources directories exist
        echo 5. Ensure PySide6 is properly installed
        echo 6. Check that NLTK is working correctly
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo           Build Completed Successfully!
echo ============================================
echo.

REM Check if executable was created
if not exist "dist\Dictionary.exe" (
    echo Error: Executable was not created!
    echo Please check the build logs above for errors.
    echo.
    pause
    exit /b 1
)

REM Get file size
for %%A in ("dist\Dictionary.exe") do set SIZE=%%~zA
set /a SIZE_MB=%SIZE%/1024/1024

echo Build Summary:
echo • Executable: dist\Dictionary.exe
echo • File size: %SIZE_MB% MB
echo • Build date: %date% %time%
echo.

echo Distribution files created:
if exist "dist\README_DIST.txt" echo • README_DIST.txt - User documentation
if exist "dist\LICENSE.txt" echo • LICENSE.txt - License information
if exist "dist\install.bat" echo • install.bat - Optional installer script
echo.

REM Ask if user wants to test the executable
set /p test="Test the executable now? (y/n): "
if /i "%test%"=="y" (
    echo Launching Dictionary Application for testing...
    echo The application should start in a few seconds...
    echo Close it when you're satisfied with the test.
    echo.
    start "" "dist\Dictionary.exe"

    REM Wait a moment then check if it's running
    timeout /t 5 /nobreak >nul
    tasklist /FI "IMAGENAME eq Dictionary.exe" 2>NUL | find /I /N "Dictionary.exe">NUL
    if errorlevel 1 (
        echo Warning: Application may not have started correctly.
        echo Please manually test the executable in the dist folder.
    ) else (
        echo ✓ Application started successfully!
    )
    echo.
)

REM Ask about cleanup
set /p cleanup="Clean up build files? (y/n): "
if /i "%cleanup%"=="y" (
    echo Cleaning up temporary build files...
    if exist "build" rmdir /s /q "build"
    if exist "Dictionary.spec" del "Dictionary.spec"
    if exist "__pycache__" rmdir /s /q "__pycache__"
    if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
    if exist "src\app_logic\__pycache__" rmdir /s /q "src\app_logic\__pycache__"
    if exist "src\app_services\__pycache__" rmdir /s /q "src\app_services\__pycache__"
    if exist "src\app_ui\__pycache__" rmdir /s /q "src\app_ui\__pycache__"
    if exist "src\utils\__pycache__" rmdir /s /q "src\utils\__pycache__"
    echo Cleanup completed.
    echo.
)

echo ============================================
echo            Build Process Complete!
echo ============================================
echo.
echo Your Dictionary Application is ready!
echo.
echo 📁 Location: %cd%\dist\Dictionary.exe
echo 💾 Size: %SIZE_MB% MB
echo 🎯 Status: Ready for distribution
echo.
echo Distribution Options:
echo 1. Share the 'dist' folder containing all files
echo 2. Use the install.bat script for automatic installation
echo 3. Simply share the .exe file for portable use
echo.
echo Features included in your build:
echo ✓ Advanced dictionary lookup with NLTK WordNet
echo ✓ Modern PySide6 user interface
echo ✓ Auto-update functionality
echo ✓ Offline dictionary support
echo ✓ Search history and favorites
echo ✓ Comprehensive word analysis
echo ✓ Professional styling and themes
echo.
echo Technical Components:
echo ✓ PySide6 GUI framework
echo ✓ NLTK natural language processing
echo ✓ WordNet linguistic database
echo ✓ Multi-threaded operations
echo ✓ Efficient caching mechanisms
echo.
echo Next Steps:
echo • Test the executable thoroughly
echo • Verify NLTK data functionality
echo • Test auto-update features
echo • Share with users or distribute
echo • Gather feedback for improvements
echo • Consider code signing for wider distribution
echo.

REM Create a simple batch file to run the application
echo @echo off > "Run_Dictionary.bat"
echo cd /d "%~dp0" >> "Run_Dictionary.bat"
echo start "" "dist\Dictionary.exe" >> "Run_Dictionary.bat"

echo Created Run_Dictionary.bat for easy launching.
echo.

echo IMPORTANT NOTES:
echo • First run may take longer due to NLTK data setup
echo • Ensure internet connection for auto-updates
echo • Check resources folder is properly included
echo • Verify all PySide6 components are working
echo.

echo Thank you for using the Dictionary Application build system!
echo.
echo Press any key to exit...
pause >nul