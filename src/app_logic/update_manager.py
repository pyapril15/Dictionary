"""
Module that handles update download logic and signaling using PySide6's signal-slot mechanism.
"""

import threading
import requests

from PySide6.QtCore import QObject, Signal
from src.app_logic import Log


class _DownloadWorker(QObject):
    """
    Handles the background download task for the update (runs in a thread).

    Emits:
        progress_signal (int): Download progress as a percentage.
        status_signal (str): Status messages for UI feedback.
        download_complete_signal: Triggered when download finishes.
    """

    progress_signal = Signal(int)
    status_signal = Signal(str)
    download_complete_signal = Signal()

    def __init__(self, url: str, save_path: str) -> None:
        """
        Initialize the worker with the download URL and destination file path.

        Args:
            url (str): The URL to download the update from.
            save_path (str): The file path where the update will be saved.
        """
        super().__init__()
        self._url: str = url
        self._save_path: str = save_path

    def start(self) -> None:
        """
        Start the download in a background thread.
        """
        threading.Thread(target=self._download_file, daemon=True).start()

    def _download_file(self) -> None:
        """
        Internal: Handles file download and emits progress signals.
        """
        Log.info("Starting update download...")
        try:
            session = requests.Session()
            response = session.get(self._url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(self._save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int((downloaded / total_size) * 100)
                        self.progress_signal.emit(percent)

            Log.info("Download complete.")
            self.download_complete_signal.emit()

        except Exception as e:
            msg = f"Update failed: {str(e)}"
            Log.error(msg)
            self.status_signal.emit(msg)


class UpdateManager(QObject):
    """
    Manages the update process, including file download and restart signaling.

    Emits:
        progress_signal (int): Download progress as a percentage.
        status_signal (str): Status messages for the user.
        download_complete_signal: Triggered when the download finishes.
        restart_signal: Emitted when the app should restart post-update.
    """

    progress_signal = Signal(int)
    status_signal = Signal(str)
    download_complete_signal = Signal()
    restart_signal = Signal()

    def __init__(self, update_url: str, new_version: str) -> None:
        """
        Initialize the update manager with the update URL and version info.

        Args:
            update_url (str): The URL to download the new version.
            new_version (str): Version number for naming the downloaded file.
        """
        super().__init__()
        self._update_url: str = update_url
        self._version: str = new_version
        self._filename: str = f"Dictionary_{new_version}.exe"
        self._worker: _DownloadWorker = _DownloadWorker(update_url, self._filename)
        self._connect_signals()

    def _connect_signals(self) -> None:
        """
        Private: Wire signals from worker to external listeners.
        """
        self._worker.progress_signal.connect(self.progress_signal.emit)
        self._worker.status_signal.connect(self.status_signal.emit)
        self._worker.download_complete_signal.connect(self.download_complete_signal.emit)

    def start_update(self) -> None:
        """
        Begin the update download process.
        """
        Log.info("Initiating update process...")
        self._worker.start()

    def close_application(self) -> None:
        """
        Emit signal to trigger application restart.
        """
        Log.info("Emitting restart signal.")
        self.restart_signal.emit()
