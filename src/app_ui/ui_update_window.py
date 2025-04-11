"""
Update dialog window for the Dictionary application.

This module defines a Qt-based dialog that allows the user to:
- View update details from GitHub.
- Confirm and initiate the update process.
- Track progress visually via a progress bar.

The dialog adapts depending on whether the current version is discontinued
or if a newer version is simply available.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QLinearGradient, QColor, QPalette, QBrush
from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QProgressBar,
    QMessageBox, QScrollArea, QWidget
)
from typing import Optional, Tuple, Dict, Any

from src.app_logic import UpdateManager


class UpdateWindow(QDialog):
    """
    Dialog window for checking, displaying, and applying updates.

    :param update_info: Release data from GitHub including version notes.
    :param update_file_url: URL to the .exe installer of the latest version.
    :param versions: Tuple of (current_version, latest_version).
    :param is_discontinued: True if the current version is no longer supported.
    :param parent: Optional parent widget.
    """

    update_started = Signal()
    update_finished = Signal()

    def __init__(
            self,
            update_info: Dict[str, Any],
            update_file_url: Optional[str],
            versions: Tuple[str, str],
            is_discontinued: bool = False,
            parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.update_info = update_info
        self.update_file_url = update_file_url
        self.versions = versions
        self._is_discontinued = is_discontinued
        self.update_manager: Optional[UpdateManager] = None

        self.setWindowTitle("Update Required" if self._is_discontinued else "Update Available")
        self.setFixedSize(400, 300)

        self._setup_ui()
        self._setup_signals()

        if self.update_file_url:
            self._initialize_manager()

    def showEvent(self, event) -> None:
        """Handles dialog display event and applies gradient background."""
        super().showEvent(event)
        self._apply_gradient_background()

    def _setup_ui(self) -> None:
        """Initializes all UI elements."""
        self._create_labels()
        self._create_scroll_area()
        self._create_progress_bar()
        self._create_buttons()
        self._assemble_layout()

    def _apply_gradient_background(self) -> None:
        """Applies a vertical gradient background to the dialog."""
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#FFDEE9"))
        gradient.setColorAt(1, QColor("#B5FFFC"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def _create_labels(self) -> None:
        """Creates version title and detail labels."""
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
        """Creates scrollable area to show update description."""
        description = self.update_info.get("body", "")
        self.scroll_area: Optional[QScrollArea] = None

        if description:
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)

            self.description_label = QLabel(description)
            self.description_label.setStyleSheet("font-size: 12px; color: #444; background: #fff")
            self.description_label.setWordWrap(True)

            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.addWidget(self.description_label)

            self.scroll_area.setWidget(scroll_content)

    def _create_progress_bar(self) -> None:
        """Creates the progress bar for download status."""
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border-radius: 8px; height: 15px; background-color: #eee; }
            QProgressBar::chunk { background-color: #5cb85c; border-radius: 8px; }
        """)

    def _create_buttons(self) -> None:
        """Creates the update button."""
        self.update_now_btn = QPushButton("Update Now")
        self.update_now_btn.setEnabled(self.update_file_url is not None)
        self.update_now_btn.setStyleSheet(
            "background-color: #5cb85c; color: white; font-size: 14px; padding: 6px; border-radius: 5px;"
        )
        self.update_now_btn.clicked.connect(self._on_update_clicked)

    def _assemble_layout(self) -> None:
        """Lays out the UI elements vertically."""
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.version_label)
        if self.scroll_area:
            layout.addWidget(self.scroll_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.update_now_btn)
        self.setLayout(layout)

    def _setup_signals(self) -> None:
        """Connects signals from the update manager."""
        if self.update_manager:
            self._connect_signals()

    def _connect_signals(self) -> None:
        """Connects manager signals to progress bar and completion handler."""
        self.update_manager.progress_signal.connect(self.progress_bar.setValue)
        self.update_manager.download_complete_signal.connect(self._on_update_complete)

    def _initialize_manager(self) -> None:
        """Initializes the update manager for handling the update process."""
        self.update_manager = UpdateManager(self.update_file_url, self.versions[1])
        self._connect_signals()

    def _on_update_clicked(self) -> None:
        """Handles the user clicking the 'Update Now' button."""
        confirm = QMessageBox.question(
            self, "Confirm Update",
            f"Are you sure you want to update to version {self.versions[1]}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return

        self.update_started.emit()
        self.update_now_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        if not self.update_manager:
            self._initialize_manager()

        self.update_manager.start_update()

    def _on_update_complete(self) -> None:
        """Triggered when the update is downloaded successfully."""
        QMessageBox.information(self, "Update Complete", "The update has been downloaded successfully.")
        self.update_finished.emit()
        self.close()
