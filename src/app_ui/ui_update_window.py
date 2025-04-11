import requests
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QLinearGradient, QColor, QPalette, QBrush
from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QProgressBar,
    QMessageBox, QScrollArea, QWidget
)
from src.app_logic.update_logic import UpdateManager


class UpdateWindow(QDialog):
    """Dialog window for checking, displaying, and applying updates."""

    update_started = Signal()
    update_finished = Signal()

    def __init__(self, update_info, update_file_url, versions, is_discontinued=False, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.update_file_url = update_file_url
        self.versions = versions
        self._is_discontinued = is_discontinued
        self.update_manager = None

        self.setWindowTitle("Update Required" if self._is_discontinued else "Update Available")
        self.setFixedSize(400, 300)

        self._setup_ui()
        self._setup_signals()

        if self.update_file_url:
            self._initialize_manager()

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_gradient_background()

    def _setup_ui(self):
        self._create_labels()
        self._create_scroll_area()
        self._create_progress_bar()
        self._create_buttons()
        self._assemble_layout()

    def _apply_gradient_background(self):
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#FFDEE9"))
        gradient.setColorAt(1, QColor("#B5FFFC"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def _create_labels(self):
        title = "Update Required" if self._is_discontinued else "Update Available"
        version_text = (
            f"Current Version: {self.versions[0]}\nLatest Version: {self.versions[1]}"
            if self.update_file_url else f"This version{(self.versions[0])} is discontinued. Please update."
        )
        self.title_label = QLabel(title, alignment=Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        self.version_label = QLabel(version_text, alignment=Qt.AlignCenter)
        self.version_label.setStyleSheet("font-size: 14px; color: #555;")

    def _create_scroll_area(self):
        description = self.update_info.get("body", "")
        self.scroll_area = None

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

    def _create_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border-radius: 8px; height: 15px; background-color: #eee; }
            QProgressBar::chunk { background-color: #5cb85c; border-radius: 8px; }
        """)

    def _create_buttons(self):
        self.update_now_btn = QPushButton("Update Now")
        self.update_now_btn.setEnabled(self.update_file_url is not None)
        self.update_now_btn.setStyleSheet(
            "background-color: #5cb85c; color: white; font-size: 14px; padding: 6px; border-radius: 5px;"
        )
        self.update_now_btn.clicked.connect(self._on_update_clicked)

    def _assemble_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.version_label)
        if self.scroll_area:
            layout.addWidget(self.scroll_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.update_now_btn)
        self.setLayout(layout)

    def _setup_signals(self):
        if self.update_manager:
            self._connect_signals()

    def _connect_signals(self):
        self.update_manager.progress_signal.connect(self.progress_bar.setValue)
        self.update_manager.download_complete_signal.connect(self._on_update_complete)

    def _initialize_manager(self):
        self.update_manager = UpdateManager(self.update_file_url, self.versions[1])
        self._connect_signals()

    def _on_update_clicked(self):
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

    def _on_update_complete(self):
        QMessageBox.information(self, "Update Complete", "The update has been downloaded successfully.")
        self.update_finished.emit()
        self.close()
