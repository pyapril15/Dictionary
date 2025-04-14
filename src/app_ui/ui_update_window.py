"""
Update dialog window for the Dictionary application.

This module provides a Qt-based update dialog that:
- Notifies the user of available updates.
- Displays update details.
- Handles the update download process via UpdateManager.
- Uses a progress bar to show real-time progress.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QLinearGradient, QColor, QPalette, QBrush
from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QProgressBar,
    QMessageBox, QScrollArea, QWidget
)

from src.app_logic.log import Log
from src.app_logic.update_manager import UpdateManager
from src.utils.meta import MetaQObjectABC


class AbstractUpdateWindow(QDialog, ABC, metaclass=MetaQObjectABC):
    """
    Abstract base class for the update dialog window.
    Defines the structure and required methods for UI setup and signal handling.
    """

    update_started = Signal()
    update_finished = Signal()

    def __init__(
            self,
            update_info: Dict[str, Any],
            update_file_url: Optional[str],
            versions: Tuple[str, str],
            log: Log,
            is_discontinued: bool = False,
            parent: Optional[QWidget] = None
    ) -> None:
        """
        Initialize the abstract dialog window.

        Args:
            update_info (dict): Metadata about the update (title, body).
            update_file_url (str | None): Direct download URL of the update file.
            versions (tuple): Tuple of (current_version, latest_version).
            is_discontinued (bool): If True, forces the update dialog to block the user.
            parent (QWidget | None): Optional parent QWidget.
        """
        super().__init__(parent)
        self.update_info = update_info
        self.update_file_url = update_file_url
        self.versions = versions
        self._log = log
        self._is_discontinued = is_discontinued
        self.update_manager: Optional[UpdateManager] = None

        self.setWindowTitle("Update Required" if self._is_discontinued else "Update Available")
        self.setFixedSize(400, 300)

        self._init_ui()
        self._init_signals()

        if self.update_file_url:
            self._init_update_manager()

    def showEvent(self, event) -> None:
        """Apply gradient background when the dialog is shown."""
        super().showEvent(event)
        self._apply_gradient_background()

    def _init_ui(self) -> None:
        """Initialize UI components (implemented by subclasses)."""
        self._create_labels()
        self._create_scroll_area()
        self._create_progress_bar()
        self._create_buttons()
        self._assemble_layout()

    def _init_signals(self) -> None:
        """Setup signals between update manager and UI."""
        if self.update_manager:
            self._connect_signals()

    def _init_update_manager(self) -> None:
        """Initialize the UpdateManager if a valid URL is provided."""
        self.update_manager = UpdateManager(self.update_file_url, self.versions[1], self._log)
        self._connect_signals()

    def _apply_gradient_background(self) -> None:
        """Apply a vertical color gradient background to the dialog."""
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#FFDEE9"))
        gradient.setColorAt(1, QColor("#B5FFFC"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    @abstractmethod
    def _create_labels(self) -> None:
        """Create title and version information labels."""
        pass

    @abstractmethod
    def _create_scroll_area(self) -> None:
        """Create scrollable area to show update description."""
        pass

    @abstractmethod
    def _create_progress_bar(self) -> None:
        """Create and style the update progress bar."""
        pass

    @abstractmethod
    def _create_buttons(self) -> None:
        """Create and style buttons for update interaction."""
        pass

    @abstractmethod
    def _assemble_layout(self) -> None:
        """Assemble all UI components into the layout."""
        pass

    @abstractmethod
    def _connect_signals(self) -> None:
        """Connect update manager signals to UI elements."""
        pass


class UpdateWindow(AbstractUpdateWindow):
    """
    Concrete implementation of the update dialog.
    Handles user interaction, update logic, and UI rendering.
    """

    def __init__(self, update_info: Dict[str, Any], update_file_url: Optional[str], versions: Tuple[str, str],
                 is_discontinued: bool, log: Log):
        super().__init__(update_info, update_file_url, versions, log, is_discontinued)

        self._log_update = log.update

    def _create_labels(self) -> None:
        """Create title and version info labels with styling."""
        title = "Update Required" if self._is_discontinued else "Update Available"
        version_text = (
            f"This version {self.versions[0]} is discontinued. Please update."
            if self._is_discontinued else f"Current Version: {self.versions[0]}\nLatest Version: {self.versions[1]}"
        )

        self.title_label = QLabel(title, alignment=Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        self.version_label = QLabel(version_text, alignment=Qt.AlignCenter)
        self.version_label.setStyleSheet("font-size: 14px; color: #555;")

    def _create_scroll_area(self) -> None:
        """Create scrollable description area from update_info['body']."""
        description = self.update_info.get("body", "")
        self.scroll_area: Optional[QScrollArea] = None

        if description:
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)

            self.description_label = QLabel(description)
            self.description_label.setStyleSheet("font-size: 12px; color: #444; background: #fff;")
            self.description_label.setWordWrap(True)

            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.addWidget(self.description_label)

            self.scroll_area.setWidget(scroll_content)

    def _create_progress_bar(self) -> None:
        """Create and style a horizontal progress bar for downloads."""
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border-radius: 8px; height: 15px; background-color: #eee; }
            QProgressBar::chunk { background-color: #5cb85c; border-radius: 8px; }
        """)

    def _create_buttons(self) -> None:
        """Create the 'Update Now' button with styling and logic."""
        self.update_now_btn = QPushButton("Update Now")
        self.update_now_btn.setEnabled(self.update_file_url is not None)
        self.update_now_btn.setStyleSheet(
            "background-color: #5cb85c; color: white; font-size: 14px; padding: 6px; border-radius: 5px;"
        )
        self.update_now_btn.clicked.connect(self._on_update_clicked)

    def _assemble_layout(self) -> None:
        """Add all widgets into a vertical layout for the dialog."""
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.version_label)
        if self.scroll_area:
            layout.addWidget(self.scroll_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.update_now_btn)
        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Link progress and completion signals from UpdateManager."""
        if self.update_manager:
            self.update_manager.progress_signal.connect(self.progress_bar.setValue)
            self.update_manager.download_complete_signal.connect(self._on_update_complete)

    def _on_update_clicked(self) -> None:
        """
        Handle the 'Update Now' button click.

        Shows confirmation dialog and initiates the update process.
        """
        try:
            self._log_update.info("User clicked 'Update Now'.")
            confirm = QMessageBox.question(
                self, "Confirm Update",
                f"Are you sure you want to update to version {self.versions[1]}?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.No:
                self._log_update.info("User declined update.")
                return

            self.update_started.emit()
            self.update_now_btn.setEnabled(False)
            self.progress_bar.setValue(0)

            if not self.update_manager:
                self._init_update_manager()

            self.update_manager.start_update()
            self._log_update.info("Update process started.")
        except Exception as e:
            self._log_update.exception("Error on update button click: %s", e)
            QMessageBox.critical(self, "Update Error", "An error occurred while starting the update.")

    def _on_update_complete(self) -> None:
        """
        Handle completion of the update process.

        Closes the dialog and notifies the user.
        """
        try:
            self._log_update.info("Update download complete.")
            QMessageBox.information(self, "Update Complete", "The update has been downloaded successfully.")
            self.update_finished.emit()
            self.close()
        except Exception as e:
            self._log_update.exception("Error completing update: %s", e)
            QMessageBox.critical(self, "Error", "An error occurred after the update completed.")
