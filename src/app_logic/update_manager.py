"""
update_manager.py

Handles application update logic using threaded downloads and PySide6 signals.
Implements complete OOP principles: abstraction, encapsulation, modularity, separation of concerns.
Integrates dedicated logger ('update') via LoggerManager for traceable diagnostics.
"""

import threading
from abc import ABC, abstractmethod

import requests
from PySide6.QtCore import Signal

from src.app_logic.log import Log


# ============================
# Abstract Classes
# ============================

class AbstractDownloadWorker(ABC):
    """
    Abstract base class for a download worker.

    Defines the interface for downloading update files.
    """

    def __init__(self, url: str, save_path: str) -> None:
        """
        Initialize with download URL and destination path.

        Args:
            url (str): URL to download the update from.
            save_path (str): Path to save the downloaded file.
        """
        super().__init__()
        self._url: str = url
        self._save_path: str = save_path

    @abstractmethod
    def start(self) -> None:
        """Start the download process."""
        pass

    @abstractmethod
    def _download_file(self) -> None:
        """Internal method that handles file downloading."""
        pass


class AbstractUpdateManager(ABC):
    """
    Abstract interface for update managers that coordinate update logic.
    """

    def __init__(self, update_url: str, version: str) -> None:
        """
        Args:
            update_url (str): URL for downloading the update.
            version (str): Version number for the update.
        """
        super().__init__()
        self._update_url: str = update_url
        self._version: str = version
        self._filename: str = f"Dictionary_{version}.exe"

    @abstractmethod
    def start_update(self) -> None:
        """Initiate the update process."""
        pass

    @abstractmethod
    def close_application(self) -> None:
        """Emit signal to restart or exit the application after update."""
        pass


# ============================
# Concrete Implementations
# ============================

class DownloadWorker(AbstractDownloadWorker):
    """
    Concrete worker class responsible for downloading update files using threading.

    Signals:
        progress_signal (int): Emits the download progress percentage.
        status_signal (str): Emits informational or error status messages.
        download_complete_signal (): Emits when download completes successfully.
    """

    progress_signal = Signal(int)
    status_signal = Signal(str)
    download_complete_signal = Signal()

    def __init__(self, url: str, save_path: str, log: Log) -> None:
        """
        Initialize the download worker.

        Args:
            url (str): File URL to download.
            save_path (str): Local file path to save the downloaded file.
            log (Log): Logger container with domain-specific loggers.
        """
        super().__init__(url, save_path)
        self._logger = log.update
        self._logger.debug("DownloadWorker initialized.")

    def start(self) -> None:
        """
        Start the download in a background daemon thread.
        """
        self._logger.info("Launching download thread.")
        try:
            thread = threading.Thread(target=self._download_file, daemon=True)
            thread.start()
        except Exception as e:
            self._logger.critical(f"Failed to start download thread: {e}")
            self.status_signal.emit(f"Thread start error: {e}")

    def _download_file(self) -> None:
        """
        Perform the download operation, emitting progress and handling errors.
        """
        self._logger.info(f"Connecting to {self._url}")
        try:
            response = requests.get(self._url, stream=True, timeout=15)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            if total_size == 0:
                raise ValueError("Download failed: No content received.")

            downloaded = 0
            with open(self._save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        progress = int((downloaded / total_size) * 100)
                        self.progress_signal.emit(progress)

            self._logger.info(f"Download completed: {self._save_path}")
            self.download_complete_signal.emit()

        except requests.RequestException as re:
            self._logger.error(f"Request error during download: {re}")
            self.status_signal.emit(f"Network error: {re}")
        except Exception as e:
            self._logger.critical(f"Unexpected download error: {e}")
            self.status_signal.emit(f"Download failed: {e}")


class UpdateManager(AbstractUpdateManager):
    """
    Concrete class to manage update lifecycle.

    Handles the orchestration of downloading updates and restarting the app.

    Signals:
        progress_signal (int): Emits current download progress.
        status_signal (str): Emits status or error messages.
        download_complete_signal (): Emits when download finishes.
        restart_signal (): Emits to indicate the app should restart.
    """

    progress_signal = Signal(int)
    status_signal = Signal(str)
    download_complete_signal = Signal()
    restart_signal = Signal()

    def __init__(self, update_url: str, version: str, log: Log) -> None:
        """
        Initialize the update manager.

        Args:
            update_url (str): URL from which to download the update.
            version (str): Target version to be downloaded.
            log (Log): Logger container with scoped loggers.
        """
        super().__init__(update_url, version)
        self._logger = log.update
        self._logger.info(f"Initializing UpdateManager for version {version}")

        try:
            self._worker = DownloadWorker(update_url, self._filename, log)
            self._connect_signals()
        except Exception as e:
            self._logger.critical(f"Error setting up update components: {e}")
            raise

    def _connect_signals(self) -> None:
        """
        Connect internal worker signals to external interface signals.
        """
        try:
            self._worker.progress_signal.connect(self.progress_signal.emit)
            self._worker.status_signal.connect(self.status_signal.emit)
            self._worker.download_complete_signal.connect(self.download_complete_signal.emit)
            self._logger.debug("DownloadWorker signals connected to UpdateManager.")
        except Exception as e:
            self._logger.error(f"Signal connection failed: {e}")

    def start_update(self) -> None:
        """
        Begin the download process using the worker.
        """
        self._logger.info("Starting update process.")
        try:
            self._worker.start()
        except Exception as e:
            self._logger.error(f"Error starting update: {e}")
            self.status_signal.emit(f"Update start failed: {e}")

    def close_application(self) -> None:
        """
        Emit a signal to trigger application shutdown and restart.
        """
        self._logger.info("Triggering restart signal.")
        try:
            self.restart_signal.emit()
        except Exception as e:
            self._logger.error(f"Failed to emit restart signal: {e}")
