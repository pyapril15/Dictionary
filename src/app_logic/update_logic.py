import threading
import requests
from PySide6.QtCore import QObject, Signal
from src.app_logic.logger import logger


class _DownloadWorker(QObject):
    """Handles the background download task for the update (runs in a thread)."""

    progress_signal = Signal(int)
    status_signal = Signal(str)
    download_complete_signal = Signal()

    def __init__(self, url: str, save_path: str):
        super().__init__()
        self._url = url
        self._save_path = save_path

    def start(self):
        threading.Thread(target=self._download_file, daemon=True).start()

    def _download_file(self):
        logger.info("Starting update download...")
        try:
            session = requests.Session()
            response = session.get(self._url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(self._save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int((downloaded / total_size) * 100)
                        self.progress_signal.emit(percent)

            logger.info("Download complete.")
            self.download_complete_signal.emit()

        except Exception as e:
            msg = f"Update failed: {str(e)}"
            logger.error(msg)
            self.status_signal.emit(msg)


class UpdateManager(QObject):
    """Manages the update process, including downloading and restart signaling."""

    progress_signal = Signal(int)
    status_signal = Signal(str)
    download_complete_signal = Signal()
    restart_signal = Signal()

    def __init__(self, update_url: str, new_version: str):
        super().__init__()
        self._update_url = update_url
        self._version = new_version
        self._filename = f"Dictionary_{new_version}.exe"
        self._worker = _DownloadWorker(update_url, self._filename)
        self._connect_signals()

    def _connect_signals(self):
        self._worker.progress_signal.connect(self.progress_signal.emit)
        self._worker.status_signal.connect(self.status_signal.emit)
        self._worker.download_complete_signal.connect(self.download_complete_signal.emit)

    def start_update(self):
        logger.info("Initiating update process...")
        self._worker.start()

    def close_application(self):
        logger.info("Emitting restart signal.")
        self.restart_signal.emit()


class GitHubUpdateChecker:
    """Checks GitHub for available application updates."""

    _owner = "pyapril15"
    _repo = "Dictionary"
    _releases_url = f"https://api.github.com/repos/{_owner}/{_repo}/releases"

    @classmethod
    def get_latest_release(cls):
        try:
            logger.info("Fetching latest release...")

            response = requests.get(cls._releases_url)
            response.raise_for_status()
            releases = response.json()

            return releases[0] if releases else None
        except requests.RequestException as e:
            logger.error(f"Failed to fetch latest release: {str(e)}")
            return None

    @classmethod
    def get_all_versions(cls):
        try:
            logger.info("Fetching all available versions...")
            response = requests.get(cls._releases_url)
            response.raise_for_status()
            return {release["tag_name"].lstrip("v") for release in response.json()}
        except requests.RequestException as e:
            logger.error(f"Error fetching versions: {str(e)}")
            return set()

    @classmethod
    def get_update_info(cls):
        try:
            release = cls.get_latest_release()
            if release:
                version = release["tag_name"].lstrip("v")
                for asset in release.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        logger.info(f"Update found for version {version}")
                        return release, asset["browser_download_url"], version
            logger.warning("No .exe asset found in any release.")
            return None, None, None
        except requests.RequestException as e:
            logger.error(f"Error retrieving update info: {str(e)}")
            return None, None, None


def check_for_updates(config, callback):
    """Checks for updates on GitHub and triggers the callback if newer version is found."""
    current_version = config.app_version
    release_info, update_url, latest_version = GitHubUpdateChecker.get_update_info()

    if not update_url:
        logger.warning("No downloadable update found.")
        return

    if latest_version and latest_version > current_version:
        logger.info(f"New version available: {latest_version}")
        callback(release_info, update_url, (current_version, latest_version))
    else:
        logger.info("You already have the latest version.")


def is_version_discontinued(config) -> bool:
    """Returns True if current version is not found in GitHub releases."""
    available_versions = GitHubUpdateChecker.get_all_versions()
    discontinued = config.app_version not in available_versions
    if discontinued:
        logger.warning(f"Version {config.app_version} is discontinued.")
    return discontinued
