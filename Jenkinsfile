pipeline {
	agent any

    environment {
		PROJECT_NAME = "Dictionary"
        VERSION = "v1.0.0"
        REPO = "pyapril15/${PROJECT_NAME}"

        BUILD_DIR = "dist"
        EXE_NAME = "${PROJECT_NAME}.exe"
        BUILD_PATH = "${BUILD_DIR}/${EXE_NAME}"

        RELEASE_NAME = "Dictionary ${VERSION}"
        RELEASE_FILENAME = "release.json"
        RELEASE_NOTES_MD = "latest_version.md"

        GITHUB_API_URL = "https://api.github.com/repos/${REPO}/releases"
        VENV_DIR = ".venv"
    }

    stages {

		stage('Checkout') {
			steps {
				echo "Checking out branch..."
                checkout scm
            }
        }

        stage('Setup Virtual Env') {
			steps {
				echo "Setting up venv..."
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
			steps {
				echo "Installing requirements..."
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Build EXE') {
			steps {
				echo "Compiling executable..."
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    pyinstaller --clean Dictionary.spec
                '''
            }
        }

        stage('Git Tag & Push') {
			steps {
				echo "Tagging ${VERSION}..."
                withCredentials([string(credentialsId: 'GITHUB_TOKEN', variable: 'github-token')]) {
					bat '''
                        git config user.name "pyapril15"
                        git config user.email "praveen885127@gmail.com"
                        git remote set-url origin https://%github-token%@github.com/%REPO%.git
                        git fetch --tags
                        git tag -d %VERSION% 2>NUL
                        git tag %VERSION%
                        git push origin %VERSION%
                    '''
                }
            }
        }

        stage('GitHub Release') {
			steps {
				echo "Creating GitHub release using latest_version.md..."
                withCredentials([string(credentialsId: 'GITHUB_TOKEN', variable: 'github-token')]) {
					bat '''
                        setlocal EnableDelayedExpansion
                        set "BODY="
                        for /F "usebackq delims=" %%A in ("%RELEASE_NOTES_MD%") do (
                            set "LINE=%%A"
                            set "LINE=!LINE:\"=\\\"!"
                            set "BODY=!BODY!!LINE!\\n"
                        )

                        (
                            echo {
                            echo   "tag_name": "%VERSION%",
                            echo   "name": "%RELEASE_NAME%",
                            echo   "body": "!BODY!",
                            echo   "draft": false,
                            echo   "prerelease": false
                            echo }
                        ) > %RELEASE_FILENAME%

                        curl -s -X POST %GITHUB_API_URL% ^
                             -H "Authorization: token %github-token%" ^
                             -H "Accept: application/vnd.github.v3+json" ^
                             -d @%RELEASE_FILENAME% ^
                             -o response.json
                    '''
                }
            }
        }

        stage('Upload .exe') {
			steps {
				echo "Uploading .exe to GitHub release..."
                withCredentials([string(credentialsId: 'GITHUB_TOKEN', variable: 'github-token')]) {
					bat '''
                        for /F "tokens=* delims=" %%A in ('powershell -Command "(Get-Content response.json | ConvertFrom-Json).upload_url"') do (
                            set "UPLOAD_URL=%%A"
                        )

                        setlocal enabledelayedexpansion
                        set "UPLOAD_URL=!UPLOAD_URL:{?name,label}=!"

                        if not exist %BUILD_PATH% (
                            echoERROR: Executable not found!
                            exit /b 1
                        )

                        echo Uploading to !UPLOAD_URL!
                        curl -s -X POST "!UPLOAD_URL!?name=%EXE_NAME%" ^
                             -H "Authorization: token %github-token%" ^
                             -H "Content-Type: application/octet-stream" ^
                             --data-binary "@%BUILD_PATH%"
                    '''
                }
            }
        }

        stage('Merge to main & Cleanup') {
			steps {
				echo "Merging build → main and deleting build branch..."
                withCredentials([string(credentialsId: 'GITHUB_TOKEN', variable: 'github-token')]) {
					bat '''
                        REM Ensure we have both branches locally
                        git fetch origin main
                        git fetch origin build

                        REM Checkout main branch and pull latest
                        git checkout main
                        git pull origin main

                        REM Merge build into main
                        git merge origin/build --no-ff -m "Auto-merged build → main(Jenkins)"

                        REM Push updated main
                        git push origin main

                        REM Delete remote build branch only if merge succeeded
                        git push origin --delete build || echo "Could not delete build branch"
                    '''
			}
		}
}
    }

    post {
        success {
            echo "Build and release successful! Ready for safe merge to main."
        }
        failure {
            echo "Build failed. Check logs before merging."
        }
        cleanup {
            echo "Cleaning up virtual environment..."
            bat 'rmdir /S /Q %VENV_DIR%'
        }
    }
}
