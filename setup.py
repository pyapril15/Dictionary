"""
Setup script for building the Dictionary Application executable
Author: Dictionary Team
Version: 1.0.0
"""

import os
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__


def build_executable():
    """Build the executable using PyInstaller"""

    # Application information
    APP_NAME = 'Dictionary'
    APP_VERSION = '1.0.0'
    APP_DESCRIPTION = 'Advanced Dictionary Application with NLTK Support'
    APP_AUTHOR = 'Dictionary Team'

    # Define the build arguments
    args = [
        '--onefile',  # Create a one-file bundled executable
        '--windowed',  # Hide console window (GUI app)
        '--name=' + APP_NAME,  # Name of the executable
        '--distpath=dist',  # Output directory
        '--workpath=build',  # Temporary build directory
        '--specpath=.',  # Spec file location
        '--clean',  # Clean PyInstaller cache
        '--noconfirm',  # Replace output directory without asking
        '--optimize=2',  # Optimize bytecode
        '--noupx',  # Don't use UPX compression

        # Icon (if available)
        '--icon=resources/icons/app_icon.ico',

        # Hidden imports for PySide6
        '--hidden-import=PySide6',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=shiboken6',

        # Hidden imports for NLTK and corpus data
        '--hidden-import=nltk',
        '--hidden-import=nltk.data',
        '--hidden-import=nltk.downloader',
        '--hidden-import=nltk.corpus',
        '--hidden-import=nltk.corpus.reader.api',
        '--hidden-import=nltk.corpus.reader.wordnet',
        '--hidden-import=nltk.tokenize',
        '--hidden-import=nltk.tokenize.punkt',

        # Application modules
        '--hidden-import=src.app_logic.app_config',
        '--hidden-import=src.app_logic.log',
        '--hidden-import=src.app_services.github_service',
        '--hidden-import=src.app_ui.main_window',
        '--hidden-import=src.app_ui.ui_update_window',
        '--hidden-import=src.utils',

        # Other dependencies
        '--hidden-import=requests',
        '--hidden-import=json',
        '--hidden-import=subprocess',
        '--hidden-import=pathlib',
        '--hidden-import=typing',

        # Collect data for PySide6
        '--collect-data=PySide6',

        # Collect NLTK data
        '--collect-data=nltk',

        # Add data files
        '--add-data=resources;resources',
        '--add-data=src;src',

        # Exclude unnecessary modules
        '--exclude-module=tkinter',
        '--exclude-module=_tkinter',
        '--exclude-module=matplotlib',

        # Main Python file
        'main.py'
    ]

    print("=" * 60)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print("=" * 60)
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print()

    try:
        # Check if icon exists
        icon_path = 'resources/icons/app_icon.ico'
        if not os.path.exists(icon_path):
            print("Warning: Icon file not found. Building without icon.")
            # Remove icon argument
            args = [arg for arg in args if not arg.startswith('--icon=')]
        else:
            print(f"Using icon: {icon_path}")

        # Check for required directories
        required_dirs = ['src', 'resources']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                print(f"Warning: Required directory '{dir_name}' not found!")

        # Run PyInstaller
        print("Starting build process...")
        PyInstaller.__main__.run(args)

        print()
        print("=" * 60)
        print("Build completed successfully!")
        print("=" * 60)
        print(f"Executable location: {os.path.abspath('dist/' + APP_NAME + '.exe')}")

        # Create distribution files
        create_distribution_files(APP_NAME, APP_VERSION, APP_AUTHOR)

        print("\nDistribution files created successfully!")
        print("\nYour Dictionary Application is ready to distribute!")

    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


def create_distribution_files(app_name, app_version, app_author):
    """Create additional distribution files"""

    # Create README for distribution
    dist_readme = f"""Dictionary Application - Distribution Package

Application: {app_name}
Version: {app_version}
Author: {app_author}
Build Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FEATURES:
✓ Advanced Dictionary Lookup
✓ NLTK WordNet Integration
✓ Modern PySide6 Interface
✓ Auto-Update Functionality
✓ Comprehensive Word Definitions
✓ Synonyms and Antonyms
✓ Word Etymology and Usage
✓ Search History
✓ Offline Dictionary Support
✓ Professional UI Design

CONTENTS:
- {app_name}.exe         : Main application executable
- README_DIST.txt        : This file
- LICENSE.txt            : License information
- User_Guide.pdf         : Detailed user manual (if available)

SYSTEM REQUIREMENTS:
- Windows 7/8/10/11 (64-bit recommended)
- Minimum 4GB RAM
- 200MB free disk space
- Internet connection (for updates and online features)

INSTALLATION:
1. Simply run {app_name}.exe
2. No additional installation required
3. Application will create config files automatically
4. NLTK data will be downloaded on first use if needed

FIRST TIME SETUP:
1. Launch the application
2. Allow NLTK data download if prompted
3. Configure preferences in Settings
4. Start using the dictionary features

FEATURES OVERVIEW:

📚 DICTIONARY LOOKUP:
• Comprehensive word definitions using NLTK WordNet
• Multiple meaning support
• Part of speech classification
• Pronunciation guides
• Word usage examples

🔍 ADVANCED SEARCH:
• Real-time search suggestions
• Fuzzy matching for misspelled words
• Search history with favorites
• Quick lookup shortcuts
• Advanced filtering options

🎨 USER INTERFACE:
• Modern PySide6-based GUI
• Customizable themes and styles
• Responsive design
• Keyboard shortcuts
• Context menus and tooltips

🔄 AUTO-UPDATE:
• Automatic update checking
• Seamless update installation
• Version compatibility checking
• Rollback support if needed

📊 WORD ANALYSIS:
• Synonyms and antonyms
• Word frequency analysis
• Etymology and word origins
• Related words and phrases
• Usage statistics

💾 DATA MANAGEMENT:
• Offline dictionary cache
• Search history persistence
• Custom word lists
• Export/import functionality
• Backup and restore

TECHNICAL FEATURES:
• Built with PySide6 for modern UI
• NLTK integration for linguistic analysis
• Efficient caching mechanisms
• Multi-threaded operations
• Error handling and logging

NLTK COMPONENTS:
This application uses the following NLTK resources:
• WordNet corpus for definitions
• Punkt tokenizer for text processing
• Various linguistic databases
• Synonym and antonym databases

USAGE TIPS:
• Use Ctrl+F for quick search
• Right-click for context options
• Press F1 for help
• Use arrow keys to navigate results
• Double-click words for instant lookup

PERFORMANCE:
• Fast startup time
• Efficient memory usage
• Responsive UI even with large datasets
• Optimized for daily use

SUPPORT:
For technical support or feature requests:
• Email: support@example.com
• GitHub: https://github.com/dictionary-app
• Documentation: Built-in help system

COPYRIGHT:
© 2025 {app_author}. All rights reserved.
Licensed under MIT License - see LICENSE.txt for details.

DISCLAIMER:
This software uses NLTK and WordNet data.
Dictionary definitions are provided for educational purposes.
Always verify important definitions with authoritative sources.
"""

    try:
        with open('dist/README_DIST.txt', 'w', encoding='utf-8') as f:
            f.write(dist_readme)
    except Exception as e:
        print(f"Warning: Could not create dist README: {e}")

    # Copy additional files to dist
    files_to_copy = [
        ('LICENSE', 'LICENSE.txt'),
        ('README.md', 'README.md'),
        ('latest_version.md', 'latest_version.md'),
    ]

    for src, dst in files_to_copy:
        try:
            if os.path.exists(src):
                shutil.copy2(src, f'dist/{dst}')
        except Exception as e:
            print(f"Warning: Could not copy {src}: {e}")

    # Create a simple installer batch file
    installer_content = f"""@echo off
echo ============================================
echo     Dictionary Application Installer
echo ============================================
echo.

echo Installing Dictionary Application...
echo.

set INSTALL_DIR=%PROGRAMFILES%\\Dictionary Application

echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copying application files...
copy "{app_name}.exe" "%INSTALL_DIR%\\"
copy "README_DIST.txt" "%INSTALL_DIR%\\"
copy "LICENSE.txt" "%INSTALL_DIR%\\"

echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\Dictionary Application.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\{app_name}.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Dictionary Application - Advanced Word Lookup Tool" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Creating start menu entry...
set START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
if not exist "%START_MENU%\\Dictionary Application" mkdir "%START_MENU%\\Dictionary Application"

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateStartMenu.vbs
echo sLinkFile = "%START_MENU%\\Dictionary Application\\Dictionary Application.lnk" >> CreateStartMenu.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateStartMenu.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\{app_name}.exe" >> CreateStartMenu.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateStartMenu.vbs
echo oLink.Description = "Dictionary Application" >> CreateStartMenu.vbs
echo oLink.Save >> CreateStartMenu.vbs
cscript CreateStartMenu.vbs
del CreateStartMenu.vbs

echo.
echo ============================================
echo     Installation Completed Successfully!
echo ============================================
echo.
echo Dictionary Application has been installed to:
echo %INSTALL_DIR%
echo.
echo Shortcuts created:
echo • Desktop shortcut
echo • Start Menu entry
echo.
echo You can now launch the application from:
echo 1. Desktop shortcut
echo 2. Start Menu → Dictionary Application
echo 3. Direct execution from: %INSTALL_DIR%
echo.

set /p launch="Launch Dictionary Application now? (y/n): "
if /i "%launch%"=="y" (
    echo Launching Dictionary Application...
    start "" "%INSTALL_DIR%\\{app_name}.exe"
)

echo.
echo Thank you for using Dictionary Application!
echo.
pause
"""

    try:
        with open('dist/install.bat', 'w') as f:
            f.write(installer_content)
        print("Installer script created: dist/install.bat")
    except Exception as e:
        print(f"Warning: Could not create installer script: {e}")


def clean_build_files():
    """Clean up build files"""
    dirs_to_remove = ['build', '__pycache__']
    files_to_remove = ['Dictionary.spec']

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Cleaned up: {dir_name}")
            except Exception as e:
                print(f"Warning: Could not remove {dir_name}: {e}")

    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"Cleaned up: {file_name}")
            except Exception as e:
                print(f"Warning: Could not remove {file_name}: {e}")


def download_nltk_data():
    """Download required NLTK data"""
    print("\nDownloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('stopwords')
        print("NLTK data downloaded successfully!")
    except Exception as e:
        print(f"Warning: Could not download NLTK data: {e}")
        print("NLTK data will be downloaded on first run.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Build Dictionary Application executable')
    parser.add_argument('--clean', action='store_true', help='Clean build files after building')
    parser.add_argument('--test', action='store_true', help='Test the built executable')
    parser.add_argument('--nltk', action='store_true', help='Download NLTK data before building')

    args = parser.parse_args()

    # Check if required files exist
    if not os.path.exists('main.py'):
        print("Error: main.py not found!")
        print("Please ensure you are running this script from the project directory.")
        sys.exit(1)

    # Check for required directories
    if not os.path.exists('src'):
        print("Error: src directory not found!")
        print("Please ensure you are running this script from the project directory.")
        sys.exit(1)

    # Download NLTK data if requested
    if args.nltk:
        download_nltk_data()

    # Check for resources directory
    if not os.path.exists('resources'):
        print("Warning: resources directory not found. Creating resources structure...")
        os.makedirs('resources/icons', exist_ok=True)
        os.makedirs('resources/styles', exist_ok=True)
        print("Please place your app_icon.ico file in resources/icons/ directory")
        print("Please place your stylesheet.qss file in resources/styles/ directory")

    # Build the executable
    build_executable()

    # Test the executable if requested
    if args.test:
        print("\nTesting the executable...")
        try:
            import subprocess

            exe_path = 'dist/Dictionary.exe'
            if os.path.exists(exe_path):
                print(f"Launching {exe_path} for testing...")
                subprocess.Popen([exe_path])
                print("Executable launched successfully!")
            else:
                print("Error: Executable not found for testing.")
        except Exception as e:
            print(f"Error testing executable: {e}")

    # Clean up if requested
    if args.clean:
        print("\nCleaning up build files...")
        clean_build_files()

    print("\n" + "=" * 60)
    print("Build process completed!")
    print("=" * 60)
    print("\nFiles created in 'dist' directory:")
    print("• Dictionary.exe - Main application")
    print("• README_DIST.txt - User documentation")
    print("• LICENSE.txt - License information")
    print("• install.bat - Optional installer script")
    print("\nYour Dictionary Application is ready for distribution!")