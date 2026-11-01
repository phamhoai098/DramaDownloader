"""
drama_downloader.gui
~~~~~~~~~~~~~~~~~~~~
Modern, intuitive PyQt6 Graphical User Interface for Drama Downloader.
Features:
- Dark Obsidian / Modern Cyber Theme
- Link Inspector with Auto-Platform Detection
- Multi-threaded Video & Subtitle Downloader
- Rich Thumbnail Poster Grid & Table View for Catalog Search
- Category Pills & Automatic Home Pre-load per Platform
"""

import os
import sys
import re
import time
from typing import List, Optional, Dict, Any

from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QSize,
    QTimer,
    QUrl,
)
from PyQt6.QtGui import (
    QIcon,
    QFont,
    QColor,
    QPixmap,
    QImage,
    QCursor,
    QDesktopServices,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QTextEdit,
    QFileDialog,
    QSpinBox,
    QCheckBox,
    QTabWidget,
    QFrame,
    QSplitter,
    QMessageBox,
    QComboBox,
    QScrollArea,
    QAbstractItemView,
    QStackedWidget,
    QDialog,
    QSlider,
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

import drama_downloader as dd
from drama_downloader.models import Series, Episode, CatalogItem
from drama_downloader.downloader import sanitize_filename, vtt_to_srt


# ==============================================================================
# Modern Dark QSS Theme with Vibrant Accents & High DPI Friendly Styles
# ==============================================================================
DARK_THEME_QSS = """
* {
    font-family: "Segoe UI", "SF Pro Display", "Inter", "Roboto", "Helvetica Neue", sans-serif;
    font-size: 13px;
    color: #e6edf3;
    outline: none;
}

QMainWindow, QWidget#centralWidget {
    background-color: #0b0e14;
}

QTabWidget::pane {
    border: 1px solid #1f2937;
    background-color: #0f141c;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #111827;
    color: #9ca3af;
    padding: 10px 22px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #1f2937;
    border-bottom: none;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #0f141c;
    color: #38bdf8;
    border-top: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #1a2233;
    color: #d1d5db;
}

QFrame.card {
    background-color: #131a26;
    border: 1px solid #202b3c;
    border-radius: 10px;
    padding: 12px;
}

/* Drama Poster Grid Card */
QFrame.drama-card {
    background-color: #111722;
    border: 1px solid #1e293d;
    border-radius: 10px;
}

QFrame.drama-card:hover {
    background-color: #162030;
    border: 1px solid #38bdf8;
}

/* Category Filter Pills */
QPushButton.btn-pill {
    background-color: #141c2b;
    border: 1px solid #243247;
    border-radius: 14px;
    padding: 6px 14px;
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
}

QPushButton.btn-pill:hover {
    background-color: #1c283d;
    border-color: #38bdf8;
    color: #f1f5f9;
}

QPushButton.btn-pill-active {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    border: 1px solid #38bdf8;
    border-radius: 14px;
    padding: 6px 14px;
    font-size: 12px;
    color: #ffffff;
    font-weight: bold;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #0d121c;
    border: 1px solid #283548;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f3f4f6;
    selection-background-color: #0284c7;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
    background-color: #090e17;
}

QPushButton {
    background-color: #1f293d;
    border: 1px solid #2d3b54;
    border-radius: 6px;
    color: #e5e7eb;
    font-weight: 600;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #27354f;
    border-color: #3b82f6;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #192336;
}

QPushButton:disabled {
    background-color: #121824;
    border-color: #1c2433;
    color: #4b5563;
}

QPushButton.btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    border: none;
    color: #ffffff;
    font-weight: bold;
    padding: 9px 20px;
    border-radius: 6px;
}

QPushButton.btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #3b82f6);
}

QPushButton.btn-primary:pressed {
    background: #0369a1;
}

QPushButton.btn-toggle-active {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
    color: #ffffff;
    font-weight: bold;
}

QPushButton.btn-success {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    border: none;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 24px;
    border-radius: 7px;
}

QPushButton.btn-success:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
}

QPushButton.btn-danger {
    background: #dc2626;
    border: none;
    color: #ffffff;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 7px;
}

QPushButton.btn-danger:hover {
    background: #ef4444;
}

QPushButton.btn-danger:disabled {
    background: #451a1a;
    color: #7f1d1d;
}

QTableWidget {
    background-color: #0d121c;
    border: 1px solid #1f2937;
    border-radius: 8px;
    gridline-color: #192233;
    selection-background-color: #1e3a5f;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #162030;
}

QHeaderView::section {
    background-color: #141b27;
    color: #94a3b8;
    padding: 8px 6px;
    border: none;
    border-bottom: 2px solid #233045;
    font-weight: 600;
}

QProgressBar {
    background-color: #0c1017;
    border: 1px solid #1e293b;
    border-radius: 6px;
    text-align: center;
    color: #f1f5f9;
    font-weight: 600;
    height: 18px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 5px;
}

QProgressBar.progress-sub::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #34d399);
}

QTextEdit {
    background-color: #090d14;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 8px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    color: #94a3b8;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical, QScrollBar:horizontal {
    border: none;
    background: #0b0e14;
    width: 10px;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #253349;
    min-height: 20px;
    min-width: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #3b82f6;
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
}

QCheckBox {
    spacing: 8px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1px solid #334155;
    background-color: #0f172a;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
    image: none;
}

QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #1e293b;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0284c7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #38bdf8;
    border: none;
    width: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #7dd3fc;
}
"""


# ==============================================================================
# Worker Threads for Asynchronous Execution (No GUI Freeze)
# ==============================================================================

class InspectWorker(QThread):
    """Fetches series metadata and episode list in background."""
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, target: str, platform_hint: Optional[str] = None):
        super().__init__()
        self.target = target.strip()
        self.platform_hint = platform_hint

    def run(self):
        try:
            series = dd.load_series(self.target, platform_hint=self.platform_hint)
            self.finished.emit(series)
        except Exception as e:
            self.failed.emit(str(e))


class ThumbnailLoader(QThread):
    """Loads image from URL asynchronously."""
    loaded = pyqtSignal(QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            resp = dd.http.get(self.url, timeout=10)
            if resp.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(resp.content)
                self.loaded.emit(pix)
        except Exception:
            pass


class CardImageWorker(QThread):
    """Fetches image for a catalog card asynchronously."""
    image_loaded = pyqtSignal(str, QPixmap)  # item_id, pixmap

    def __init__(self, item_id: str, url: str):
        super().__init__()
        self.item_id = item_id
        self.url = url

    def run(self):
        try:
            resp = dd.http.get(self.url, timeout=8)
            if resp.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(resp.content)
                if not pix.isNull():
                    self.image_loaded.emit(self.item_id, pix)
        except Exception:
            pass


class CatalogWorker(QThread):
    """Fetches catalog dramas from platform with category, language and query support."""
    finished = pyqtSignal(list, int)  # items, total
    failed = pyqtSignal(str)

    def __init__(self, platform_id: str, query: str = "", category: str = "", page: int = 1, language: str = "vi"):
        super().__init__()
        self.platform_id = platform_id
        self.query = query
        self.category = category
        self.page = page
        self.language = language

    def run(self):
        try:
            plat = dd.get_platform(self.platform_id)
            if not plat:
                self.failed.emit(f"Không tìm thấy nền tảng: {self.platform_id}")
                return
            res = plat.get_catalog(
                page=self.page,
                query=self.query or None,
                category=self.category or None,
                language=self.language,
            )
            self.finished.emit(res.items if res else [], res.total if res else 0)
        except Exception as e:
            self.failed.emit(str(e))



class DownloadWorker(QThread):
    """Downloads episodes sequentially while reporting live progress."""
    overall_progress = pyqtSignal(int, int)  # current_done, total_count
    episode_started = pyqtSignal(int, str)   # ep_num, title
    episode_progress = pyqtSignal(int, float, float)  # ep_num, percent, speed_mb_s
    episode_finished = pyqtSignal(int, str)  # ep_num, file_path
    episode_failed = pyqtSignal(int, str)    # ep_num, error_message
    all_finished = pyqtSignal(int, int)      # success_count, fail_count
    log_msg = pyqtSignal(str, str)           # type, text

    def __init__(
        self,
        series: Series,
        target_episodes: List[Episode],
        output_dir: str,
        save_vtt: bool = False,
        save_thumb: bool = True,
    ):
        super().__init__()
        self.series = series
        self.target_episodes = target_episodes
        self.output_dir = output_dir
        self.save_vtt = save_vtt
        self.save_thumb = save_thumb
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        total = len(self.target_episodes)
        success_count = 0
        fail_count = 0

        self.log_msg.emit(
            "info",
            f"Bắt đầu phiên tải: {self.series.name} ({total} tập được chọn) -> {self.output_dir}",
        )

        downloader = dd.DramaDownloader(
            output_dir=self.output_dir,
            save_vtt=self.save_vtt,
            save_thumb=self.save_thumb,
        )

        # Download series cover & poster
        if self.save_thumb and self.series.cover:
            series_folder = os.path.join(self.output_dir, sanitize_filename(self.series.name))
            os.makedirs(series_folder, exist_ok=True)
            cover_path = os.path.join(series_folder, "cover.jpg")
            downloader._download_image(self.series.cover, cover_path)
            poster_path = os.path.join(series_folder, "poster.jpg")
            if os.path.exists(cover_path) and not os.path.exists(poster_path):
                import shutil
                try:
                    shutil.copy2(cover_path, poster_path)
                except Exception:
                    pass
            self.log_msg.emit("info", "✔ Đã tải xong ảnh bìa series (cover.jpg & poster.jpg)")


        for idx, ep in enumerate(self.target_episodes):
            if self.is_cancelled:
                self.log_msg.emit("error", "Tiến trình tải đã bị hủy bởi người dùng!")
                break

            self.episode_started.emit(ep.num, ep.title)
            self.log_msg.emit("info", f"[{idx + 1}/{total}] Đang tải EP{ep.num:03d}: {ep.title}...")

            last_report_time = 0.0

            def on_progress(p: dd.DownloadProgress):
                nonlocal last_report_time
                if self.is_cancelled:
                    raise InterruptedError("Cancelled by user")
                now = time.time()
                if now - last_report_time >= 0.15:
                    last_report_time = now
                    speed_mb = p.speed / (1024 * 1024)
                    self.episode_progress.emit(ep.num, p.percent, speed_mb)

            try:
                out_path = downloader.download_episode(
                    episode=ep,
                    series_name=self.series.name,
                    progress_callback=on_progress,
                )
                success_count += 1
                self.episode_finished.emit(ep.num, out_path)
                self.log_msg.emit("success", f"✔ EP{ep.num:03d} hoàn tất: {os.path.basename(out_path)}")
            except InterruptedError:
                self.log_msg.emit("error", "Đã dừng phiên tải theo yêu cầu.")
                break
            except Exception as e:
                fail_count += 1
                err_str = str(e)
                self.episode_failed.emit(ep.num, err_str)
                self.log_msg.emit("error", f"✖ Lỗi tải EP{ep.num:03d}: {err_str}")

            self.overall_progress.emit(idx + 1, total)

        self.all_finished.emit(success_count, fail_count)


# ==============================================================================
# Drama Poster Card Widget (For Grid View)
# ==============================================================================

class DramaCardWidget(QFrame):
    """Interactive card displaying drama poster thumbnail, title, stats, and actions."""
    download_requested = pyqtSignal(object)
    detail_requested = pyqtSignal(object)

    def __init__(self, item: CatalogItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setProperty("class", "drama-card")
        self.setFixedWidth(200)
        self.setFixedHeight(360)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Poster Image Container (Clickable -> Opens Detail Page)
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setFixedSize(180, 240)
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumb.setStyleSheet(
            "background-color: #0b0f19; border-radius: 8px; border: 1px solid #1e293b; color: #64748b;"
        )
        self.lbl_thumb.setText("Đang tải ảnh...")
        self.lbl_thumb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.lbl_thumb.setToolTip("Nhấp vào ảnh để xem chi tiết phim và danh sách tập")
        self.lbl_thumb.mousePressEvent = lambda e: self.detail_requested.emit(self.item)
        layout.addWidget(self.lbl_thumb, alignment=Qt.AlignmentFlag.AlignCenter)

        # Badges row: Episodes + Score
        badge_row = QHBoxLayout()
        ep_lbl = QLabel(f"🎬 {item.episodes} tập")
        ep_lbl.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        badge_row.addWidget(ep_lbl)
        badge_row.addStretch()

        if item.score:
            score_lbl = QLabel(f"⭐ {item.score}")
            score_lbl.setStyleSheet("color: #fbbf24; font-weight: bold; font-size: 11px;")
            badge_row.addWidget(score_lbl)
        layout.addLayout(badge_row)

        # Title Label (Clickable -> Opens Detail Page)
        self.lbl_title = QLabel(item.name)
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setFixedHeight(34)
        self.lbl_title.setStyleSheet("font-weight: bold; color: #f1f5f9; font-size: 12px;")
        self.lbl_title.setToolTip(item.name)
        self.lbl_title.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.lbl_title.mousePressEvent = lambda e: self.detail_requested.emit(self.item)
        layout.addWidget(self.lbl_title)

        # Action Buttons Row: Detail & Download
        btn_box = QHBoxLayout()
        btn_box.setSpacing(6)

        btn_detail = QPushButton("🔍 Chi Tiết")
        btn_detail.setProperty("class", "btn-secondary")
        btn_detail.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_detail.setStyleSheet("padding: 4px 6px; font-size: 11px;")
        btn_detail.clicked.connect(lambda: self.detail_requested.emit(self.item))
        btn_box.addWidget(btn_detail)

        btn_action = QPushButton("📥 Tải Về")
        btn_action.setProperty("class", "btn-primary")
        btn_action.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_action.setStyleSheet("padding: 4px 6px; font-size: 11px;")
        btn_action.clicked.connect(lambda: self.download_requested.emit(self.item))
        btn_box.addWidget(btn_action)

        layout.addLayout(btn_box)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.detail_requested.emit(self.item)
        super().mousePressEvent(event)

    def set_thumbnail(self, pixmap: QPixmap):
        target_w, target_h = 180, 240
        scaled = pixmap.scaled(
            target_w,
            target_h,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled.width() - target_w) // 2)
        y = max(0, (scaled.height() - target_h) // 2)
        cropped = scaled.copy(x, y, target_w, target_h)
        self.lbl_thumb.setPixmap(cropped)


# ==============================================================================
# Built-in Modern Video Player Dialog (Direct Streaming)
# ==============================================================================

class DramaPlayerDialog(QDialog):
    """Modern built-in video streaming player for viewing episodes directly without downloading."""

    def __init__(self, series: Series, episodes: List[Episode], initial_index: int = 0, parent=None):
        super().__init__(parent)
        self.series = series
        self.episodes = episodes
        self.current_idx = initial_index
        self.is_user_scrubbing = False
        self.current_stream_url = ""

        self.setWindowTitle(f"▶ Xem Trực Tiếp - {self.series.name}")
        self.resize(960, 680)
        self.setMinimumSize(640, 480)
        self.setStyleSheet(DARK_THEME_QSS)

        self._init_ui()
        self._init_player()
        self._load_episode(self.current_idx)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header: Title + Episode Switcher
        header = QHBoxLayout()
        self.lbl_title = QLabel(f"🎬 {self.series.name}")
        self.lbl_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #38bdf8;")
        header.addWidget(self.lbl_title, stretch=1)

        header.addWidget(QLabel("Chọn tập:"))
        self.combo_episodes = QComboBox()
        self.combo_episodes.setFixedWidth(170)
        for ep in self.episodes:
            status = " [🔒VIP]" if ep.locked else ""
            self.combo_episodes.addItem(f"EP{ep.num:03d} - {ep.title}{status}")
        self.combo_episodes.setCurrentIndex(self.current_idx)
        self.combo_episodes.currentIndexChanged.connect(self._on_combo_episode_changed)
        header.addWidget(self.combo_episodes)

        btn_prev = QPushButton("⏮ Tập trước")
        btn_prev.setProperty("class", "btn-secondary")
        btn_prev.clicked.connect(self._play_prev)
        header.addWidget(btn_prev)

        btn_next = QPushButton("Tập sau ⏭")
        btn_next.setProperty("class", "btn-secondary")
        btn_next.clicked.connect(self._play_next)
        header.addWidget(btn_next)

        layout.addLayout(header)

        # Video Viewport
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000; border-radius: 8px;")
        layout.addWidget(self.video_widget, stretch=1)

        # Status / Alert Label
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #f87171; font-weight: bold; padding: 4px;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.hide()
        layout.addWidget(self.lbl_status)

        # Seek Bar Row
        seek_box = QHBoxLayout()
        seek_box.setSpacing(8)

        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setStyleSheet("color: #94a3b8; font-size: 11px; min-width: 90px;")
        seek_box.addWidget(self.lbl_time)

        self.slider_seek = QSlider(Qt.Orientation.Horizontal)
        self.slider_seek.setRange(0, 0)
        self.slider_seek.sliderPressed.connect(self._on_seek_pressed)
        self.slider_seek.sliderMoved.connect(self._on_seek_moved)
        self.slider_seek.sliderReleased.connect(self._on_seek_released)
        seek_box.addWidget(self.slider_seek, stretch=1)

        layout.addLayout(seek_box)

        # Control Buttons Row
        ctrl_box = QHBoxLayout()
        ctrl_box.setSpacing(8)

        self.btn_play = QPushButton("▶ Phát")
        self.btn_play.setProperty("class", "btn-primary")
        self.btn_play.setFixedWidth(90)
        self.btn_play.clicked.connect(self._toggle_playback)
        ctrl_box.addWidget(self.btn_play)

        btn_rewind = QPushButton("⏪ -10s")
        btn_rewind.clicked.connect(lambda: self._seek_relative(-10000))
        ctrl_box.addWidget(btn_rewind)

        btn_forward = QPushButton("+10s ⏩")
        btn_forward.clicked.connect(lambda: self._seek_relative(10000))
        ctrl_box.addWidget(btn_forward)

        ctrl_box.addSpacing(12)
        self.lbl_vol = QLabel("🔊")
        ctrl_box.addWidget(self.lbl_vol)

        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(100)
        self.slider_vol.setFixedWidth(90)
        self.slider_vol.valueChanged.connect(self._on_volume_changed)
        ctrl_box.addWidget(self.slider_vol)

        ctrl_box.addStretch()

        self.btn_external = QPushButton("🌐 Mở Trình Phát Ngoài")
        self.btn_external.setToolTip("Mở luồng video trực tiếp bằng trình duyệt hoặc trình phát hệ thống (VLC, Media Player...)")
        self.btn_external.clicked.connect(self._open_external_stream)
        ctrl_box.addWidget(self.btn_external)

        self.btn_copy_url = QPushButton("📋 Copy Link")
        self.btn_copy_url.clicked.connect(self._copy_stream_url)
        ctrl_box.addWidget(self.btn_copy_url)

        self.btn_fullscreen = QPushButton("⛶ Toàn Màn Hình")
        self.btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        ctrl_box.addWidget(self.btn_fullscreen)

        layout.addLayout(ctrl_box)

    def _init_player(self):
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.errorOccurred.connect(self._on_player_error)

    def _load_episode(self, index: int):
        if index < 0 or index >= len(self.episodes):
            return
        self.current_idx = index
        self.combo_episodes.blockSignals(True)
        self.combo_episodes.setCurrentIndex(index)
        self.combo_episodes.blockSignals(False)

        ep = self.episodes[index]
        self.lbl_title.setText(f"🎬 {self.series.name} • EP{ep.num:03d}: {ep.title}")

        stream_url = ep.direct_url or dd.get_video_url(ep)
        self.current_stream_url = stream_url or ""

        if not stream_url:
            self.lbl_status.setText(f"⚠️ Không tìm thấy luồng phát cho EP{ep.num:03d} (có thể tập này bị khóa VIP).")
            self.lbl_status.setStyleSheet("color: #f87171; font-weight: bold; padding: 4px;")
            self.lbl_status.show()
            self.player.stop()
            self.btn_play.setText("▶ Phát")
            self.btn_external.setEnabled(False)
            self.btn_copy_url.setEnabled(False)
            return

        self.lbl_status.hide()
        self.btn_external.setEnabled(True)
        self.btn_copy_url.setEnabled(True)
        self.player.setSource(QUrl(stream_url))
        self.player.play()
        self.btn_play.setText("⏸ Tạm Dừng")

    def _on_combo_episode_changed(self, idx: int):
        self._load_episode(idx)

    def _play_prev(self):
        if self.current_idx > 0:
            self._load_episode(self.current_idx - 1)

    def _play_next(self):
        if self.current_idx < len(self.episodes) - 1:
            self._load_episode(self.current_idx + 1)

    def _toggle_playback(self):
        state = self.player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            if not self.player.source().isValid() and self.current_stream_url:
                self.player.setSource(QUrl(self.current_stream_url))
            self.player.play()

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setText("⏸ Tạm Dừng")
        else:
            self.btn_play.setText("▶ Phát")

    def _seek_relative(self, delta_ms: int):
        pos = max(0, min(self.player.duration(), self.player.position() + delta_ms))
        self.player.setPosition(pos)

    def _on_seek_pressed(self):
        self.is_user_scrubbing = True

    def _on_seek_moved(self, pos_ms: int):
        dur_ms = self.player.duration()
        self.lbl_time.setText(f"{self._format_time(pos_ms)} / {self._format_time(dur_ms)}")

    def _on_seek_released(self):
        self.is_user_scrubbing = False
        self.player.setPosition(self.slider_seek.value())

    def _on_position_changed(self, pos_ms: int):
        if not self.is_user_scrubbing:
            self.slider_seek.setValue(pos_ms)
            dur_ms = self.player.duration()
            self.lbl_time.setText(f"{self._format_time(pos_ms)} / {self._format_time(dur_ms)}")

    def _on_duration_changed(self, dur_ms: int):
        self.slider_seek.setRange(0, dur_ms)
        pos_ms = self.player.position()
        self.lbl_time.setText(f"{self._format_time(pos_ms)} / {self._format_time(dur_ms)}")

    def _on_volume_changed(self, val: int):
        self.audio_output.setVolume(val / 100.0)
        if val == 0:
            self.lbl_vol.setText("🔇")
        elif val < 50:
            self.lbl_vol.setText("🔉")
        else:
            self.lbl_vol.setText("🔊")

    def _format_time(self, ms: int) -> str:
        s = max(0, ms // 1000)
        m = s // 60
        s = s % 60
        return f"{m:02d}:{s:02d}"

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_fullscreen.setText("⛶ Toàn Màn Hình")
        else:
            self.showFullScreen()
            self.btn_fullscreen.setText("❐ Thu Nhỏ")

    def _open_external_stream(self):
        if self.current_stream_url:
            QDesktopServices.openUrl(QUrl(self.current_stream_url))

    def _copy_stream_url(self):
        if self.current_stream_url:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(self.current_stream_url)
                self.lbl_status.setText("✔ Đã copy link stream vào Clipboard!")
                self.lbl_status.setStyleSheet("color: #34d399; font-weight: bold; padding: 4px;")
                self.lbl_status.show()
                QTimer.singleShot(2500, self.lbl_status.hide)

    def _on_player_error(self, error, error_string):
        if error != QMediaPlayer.Error.NoError:
            self.lbl_status.setText(f"⚠️ Trình phát gặp sự cố ({error_string}). Bạn có thể bấm 'Mở Trình Phát Ngoài' để xem.")
            self.lbl_status.setStyleSheet("color: #f87171; font-weight: bold; padding: 4px;")
            self.lbl_status.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self._toggle_playback()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self._toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Left:
            self._seek_relative(-10000)
        elif event.key() == Qt.Key.Key_Right:
            self._seek_relative(10000)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self.player.stop()
        super().closeEvent(event)


# ==============================================================================
# Main Application Window
# ==============================================================================

class DramaDownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drama Downloader Studio - Tải Phim Ngắn Đa Nền Tảng")
        self.setMinimumSize(1120, 800)
        self.resize(1240, 880)

        # Set Window & Taskbar Icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.current_series: Optional[Series] = None
        self.download_worker: Optional[DownloadWorker] = None
        self.inspect_worker: Optional[InspectWorker] = None
        self.catalog_worker: Optional[CatalogWorker] = None

        # Catalog State
        self.current_platform_id = "dramabox"
        self.current_category_id = "0"
        self.current_language = "vi"
        self.current_page = 1
        self.total_catalog_count = 0
        self.category_pills_map: Dict[str, QPushButton] = {}


        # Image cache & worker tracker for Grid cards
        self.pixmap_cache: Dict[str, QPixmap] = {}
        self.card_workers: List[CardImageWorker] = []
        self.card_map: Dict[str, DramaCardWidget] = {}
        self.current_catalog_items: List[CatalogItem] = []

        # Detail view state
        self.last_catalog_view_index = 0
        self.current_detail_item: Optional[CatalogItem] = None
        self.current_detail_series: Optional[Series] = None
        self.detail_inspect_worker: Optional[InspectWorker] = None
        self.detail_thumb_loader: Optional[ThumbnailLoader] = None

        self._init_ui()
        self._apply_styles()

        # Preload home catalog automatically right after startup
        QTimer.singleShot(150, self._auto_preload_catalog)

    def _apply_styles(self):
        self.setStyleSheet(DARK_THEME_QSS)

    def _init_ui(self):
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 14, 16, 14)
        root_layout.setSpacing(12)

        # Header bar
        header_widget = self._create_header_widget()
        root_layout.addWidget(header_widget)

        # Tab widget
        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs, stretch=1)

        # Tab 1: Catalog / Explore (Grid & Table with Categories)
        self.tab_catalog = QWidget()
        self._setup_catalog_tab(self.tab_catalog)
        self.tabs.addTab(self.tab_catalog, "🧭 Khám Phá & Danh Mục Phim (Catalog)")

        # Tab 2: Download by URL
        self.tab_download = QWidget()
        self._setup_download_tab(self.tab_download)
        self.tabs.addTab(self.tab_download, "📥 Tải Phim Theo Link (Downloader)")

        # Tab 3: Supported Platforms
        self.tab_platforms = QWidget()
        self._setup_platforms_tab(self.tab_platforms)
        self.tabs.addTab(self.tab_platforms, "🌐 Nền Tảng Hỗ Trợ (11+ Platforms)")

        # Bottom status bar
        self.status_label = QLabel("Sẵn sàng. Nhập liên kết hoặc ID phim để bắt đầu.")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px; padding: 4px 0px;")
        root_layout.addWidget(self.status_label)

    # --------------------------------------------------------------------------
    # Header
    # --------------------------------------------------------------------------
    def _create_header_widget(self) -> QWidget:
        header = QFrame()
        header.setProperty("class", "card")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 10, 14, 10)

        # Title & Branding
        vbox = QVBoxLayout()
        title = QLabel("🎬 DRAMA DOWNLOADER STUDIO")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px;")
        subtitle = QLabel("Tự động tải sẵn danh mục phim trang chủ • Hỗ trợ lọc theo thể loại & Poster Thumbnail")
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        vbox.addWidget(title)
        vbox.addWidget(subtitle)
        layout.addLayout(vbox, stretch=1)

        # Quick badges
        badge_box = QHBoxLayout()
        b1 = QLabel("11+ PLATFORMS")
        b1.setStyleSheet("background: #1e3a8a; color: #93c5fd; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        b2 = QLabel("AUTO-PRELOAD READY")
        b2.setStyleSheet("background: #064e3b; color: #6ee7b7; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        b3 = QLabel("CATEGORIES ENABLED")
        b3.setStyleSheet("background: #581c87; color: #d8b4fe; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        badge_box.addWidget(b1)
        badge_box.addWidget(b2)
        badge_box.addWidget(b3)
        layout.addLayout(badge_box)

        return header

    # --------------------------------------------------------------------------
    # Tab 1: Download by URL
    # --------------------------------------------------------------------------
    def _setup_download_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # URL Input Bar
        input_card = QFrame()
        input_card.setProperty("class", "card")
        in_layout = QHBoxLayout(input_card)
        in_layout.setContentsMargins(10, 10, 10, 10)
        in_layout.setSpacing(8)

        lbl = QLabel("Liên kết / ID phim:")
        lbl.setStyleSheet("font-weight: bold; color: #f1f5f9;")
        in_layout.addWidget(lbl)

        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Dán URL phim từ DramaBox, ShortMax, GoodShort, NetShort, KissKH, v.v...")
        self.input_url.returnPressed.connect(self._on_inspect_clicked)
        in_layout.addWidget(self.input_url, stretch=1)

        btn_paste = QPushButton("📋 Dán link")
        btn_paste.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_paste.clicked.connect(self._on_paste_clipboard)
        in_layout.addWidget(btn_paste)

        btn_clear = QPushButton("✖ Xóa")
        btn_clear.clicked.connect(lambda: self.input_url.clear())
        in_layout.addWidget(btn_clear)

        self.btn_inspect = QPushButton("🔍 Phân Tích Phim")
        self.btn_inspect.setProperty("class", "btn-primary")
        self.btn_inspect.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_inspect.clicked.connect(self._on_inspect_clicked)
        in_layout.addWidget(self.btn_inspect)

        layout.addWidget(input_card)

        # Splitter: Left (Metadata & Config), Right (Episode list & progress)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Series Overview Card
        self.card_series = QFrame()
        self.card_series.setProperty("class", "card")
        s_layout = QVBoxLayout(self.card_series)
        s_layout.setContentsMargins(12, 12, 12, 12)

        self.lbl_cover = QLabel()
        self.lbl_cover.setFixedSize(180, 240)
        self.lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cover.setStyleSheet("background-color: #0d121c; border: 1px dashed #334155; border-radius: 8px; color: #64748b;")
        self.lbl_cover.setText("Chưa có ảnh bìa")
        s_layout.addWidget(self.lbl_cover, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_series_title = QLabel("Tên phim: Chưa chọn")
        self.lbl_series_title.setWordWrap(True)
        self.lbl_series_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8; margin-top: 6px;")
        s_layout.addWidget(self.lbl_series_title)

        self.lbl_series_plat = QLabel("Nền tảng: ---")
        self.lbl_series_plat.setStyleSheet("color: #a5b4fc; font-weight: 600;")
        s_layout.addWidget(self.lbl_series_plat)

        self.lbl_series_stats = QLabel("Số tập: 0 | Khả dụng: 0")
        self.lbl_series_stats.setStyleSheet("color: #34d399;")
        s_layout.addWidget(self.lbl_series_stats)

        self.lbl_series_desc = QLabel("Mô tả: Chưa có dữ liệu.")
        self.lbl_series_desc.setWordWrap(True)
        self.lbl_series_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        s_layout.addWidget(self.lbl_series_desc)

        s_layout.addStretch()
        left_layout.addWidget(self.card_series, stretch=1)

        # Download Config Card
        card_config = QFrame()
        card_config.setProperty("class", "card")
        cfg_layout = QVBoxLayout(card_config)
        cfg_layout.setContentsMargins(12, 12, 12, 12)
        cfg_layout.setSpacing(8)

        cfg_title = QLabel("⚙️ Cấu Hình Tải Về")
        cfg_title.setStyleSheet("font-weight: bold; color: #e2e8f0;")
        cfg_layout.addWidget(cfg_title)

        f_row = QHBoxLayout()
        self.txt_output_dir = QLineEdit(os.path.abspath("./downloads"))
        f_row.addWidget(self.txt_output_dir, stretch=1)
        btn_browse = QPushButton("📁 Chọn")
        btn_browse.clicked.connect(self._on_browse_folder)
        f_row.addWidget(btn_browse)
        btn_open = QPushButton("📂 Mở")
        btn_open.clicked.connect(self._on_open_folder)
        f_row.addWidget(btn_open)
        cfg_layout.addLayout(f_row)

        self.chk_subtitles = QCheckBox("Tự động tải & chuyển phụ đề sang .SRT")
        self.chk_subtitles.setChecked(True)
        cfg_layout.addWidget(self.chk_subtitles)

        self.chk_save_vtt = QCheckBox("Lưu thêm tệp phụ đề gốc (.VTT)")
        self.chk_save_vtt.setChecked(False)
        cfg_layout.addWidget(self.chk_save_vtt)

        self.chk_save_thumb = QCheckBox("Tải kèm ảnh bìa & thumbnail (.jpg)")
        self.chk_save_thumb.setChecked(True)
        cfg_layout.addWidget(self.chk_save_thumb)


        self.btn_start_download = QPushButton("🚀 BẮT ĐẦU TẢI (0 tập)")
        self.btn_start_download.setProperty("class", "btn-success")
        self.btn_start_download.setEnabled(False)
        self.btn_start_download.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_start_download.clicked.connect(self._on_start_download)
        cfg_layout.addWidget(self.btn_start_download)

        self.btn_stop_download = QPushButton("⏹️ HỦY / DỪNG TẢI")
        self.btn_stop_download.setProperty("class", "btn-danger")
        self.btn_stop_download.setEnabled(False)
        self.btn_stop_download.clicked.connect(self._on_stop_download)
        cfg_layout.addWidget(self.btn_stop_download)

        left_layout.addWidget(card_config)
        splitter.addWidget(left_widget)

        # Right panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        tools_card = QFrame()
        tools_card.setProperty("class", "card")
        t_layout = QHBoxLayout(tools_card)
        t_layout.setContentsMargins(8, 8, 8, 8)
        t_layout.setSpacing(8)

        btn_sel_all = QPushButton("☑️ Chọn hết")
        btn_sel_all.clicked.connect(lambda: self._set_all_episodes_checked(True))
        t_layout.addWidget(btn_sel_all)

        btn_desel_all = QPushButton("⬜ Bỏ chọn")
        btn_desel_all.clicked.connect(lambda: self._set_all_episodes_checked(False))
        t_layout.addWidget(btn_desel_all)

        btn_sel_free = QPushButton("🔓 Chọn tập Free")
        btn_sel_free.clicked.connect(self._select_accessible_episodes_only)
        t_layout.addWidget(btn_sel_free)

        t_layout.addWidget(QLabel("| Dải tập:"))
        self.input_range = QLineEdit()
        self.input_range.setPlaceholderText("VD: 1-10, 15, 20-30")
        self.input_range.setFixedWidth(140)
        t_layout.addWidget(self.input_range)

        btn_apply_range = QPushButton("Áp dụng")
        btn_apply_range.clicked.connect(self._apply_range_selection)
        t_layout.addWidget(btn_apply_range)

        t_layout.addStretch()

        self.lbl_selected_counter = QLabel("Đã chọn: 0 tập")
        self.lbl_selected_counter.setStyleSheet("color: #38bdf8; font-weight: bold;")
        t_layout.addWidget(self.lbl_selected_counter)

        right_layout.addWidget(tools_card)

        # Episode Table
        self.table_episodes = QTableWidget()
        self.table_episodes.setColumnCount(7)
        self.table_episodes.setHorizontalHeaderLabels([
            "Chọn", "Tập #", "Tên tập", "Trạng thái", "Phụ đề", "Tiến trình", "Xem Trực Tiếp"
        ])
        self.table_episodes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_episodes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_episodes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_episodes.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_episodes.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_episodes.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table_episodes.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table_episodes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_episodes.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_episodes.itemChanged.connect(self._on_table_item_changed)
        self.table_episodes.cellDoubleClicked.connect(self._on_episode_table_double_clicked)
        right_layout.addWidget(self.table_episodes, stretch=3)

        # Progress bars
        prog_card = QFrame()
        prog_card.setProperty("class", "card")
        p_layout = QVBoxLayout(prog_card)
        p_layout.setContentsMargins(10, 8, 10, 8)
        p_layout.setSpacing(6)

        overall_box = QHBoxLayout()
        self.lbl_overall_txt = QLabel("Tổng quan: 0 / 0 tập (0%)")
        self.lbl_overall_txt.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        overall_box.addWidget(self.lbl_overall_txt)
        overall_box.addStretch()
        self.lbl_speed = QLabel("Tốc độ: 0.0 MB/s")
        self.lbl_speed.setStyleSheet("color: #34d399; font-weight: bold;")
        overall_box.addWidget(self.lbl_speed)
        p_layout.addLayout(overall_box)

        self.bar_overall = QProgressBar()
        self.bar_overall.setValue(0)
        p_layout.addWidget(self.bar_overall)

        self.lbl_curr_ep = QLabel("Tập hiện tại: Chờ...")
        self.lbl_curr_ep.setStyleSheet("color: #94a3b8; font-size: 11px;")
        p_layout.addWidget(self.lbl_curr_ep)

        self.bar_current = QProgressBar()
        self.bar_current.setProperty("class", "progress-sub")
        self.bar_current.setValue(0)
        p_layout.addWidget(self.bar_current)

        right_layout.addWidget(prog_card)

        # Logs Console
        log_header = QHBoxLayout()
        lbl_log = QLabel("📝 Nhật ký hoạt động:")
        lbl_log.setStyleSheet("font-weight: bold; color: #94a3b8;")
        log_header.addWidget(lbl_log)
        log_header.addStretch()
        btn_clear_log = QPushButton("Xóa log")
        btn_clear_log.setStyleSheet("padding: 2px 8px; font-size: 11px;")
        btn_clear_log.clicked.connect(lambda: self.txt_logs.clear())
        log_header.addWidget(btn_clear_log)
        right_layout.addLayout(log_header)

        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        self.txt_logs.setFixedHeight(120)
        right_layout.addWidget(self.txt_logs)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, stretch=1)

    # --------------------------------------------------------------------------
    # Tab 2: Catalog / Explore (Categories + Poster Grid + Table Stack)
    # --------------------------------------------------------------------------
    def _setup_catalog_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Top Controls Bar
        filter_card = QFrame()
        filter_card.setProperty("class", "card")
        f_layout = QHBoxLayout(filter_card)
        f_layout.setContentsMargins(10, 10, 10, 10)
        f_layout.setSpacing(10)

        f_layout.addWidget(QLabel("Nền tảng:"))
        self.combo_cat_plat = QComboBox()
        for p in dd.get_all_platforms():
            self.combo_cat_plat.addItem(f"{p.display_name} ({p.platform_id})", p.platform_id)
        self.combo_cat_plat.currentIndexChanged.connect(self._on_platform_changed)
        f_layout.addWidget(self.combo_cat_plat)


        f_layout.addWidget(QLabel("Phụ đề / Subtitle:"))
        self.combo_cat_lang = QComboBox()
        self.combo_cat_lang.addItem("🇻🇳 VI", "vi")
        self.combo_cat_lang.addItem("🇬🇧 EN", "en")
        self.combo_cat_lang.currentIndexChanged.connect(self._on_language_changed)
        f_layout.addWidget(self.combo_cat_lang)

        f_layout.addWidget(QLabel("Tìm tên phim:"))
        self.input_cat_query = QLineEdit()
        self.input_cat_query.setPlaceholderText("Nhập từ khóa tìm kiếm (VD: Boss, Revenge, Love)...")
        self.input_cat_query.returnPressed.connect(self._on_search_catalog)
        f_layout.addWidget(self.input_cat_query, stretch=1)


        btn_search_cat = QPushButton("🔍 Tìm Kiếm")
        btn_search_cat.setProperty("class", "btn-primary")
        btn_search_cat.clicked.connect(self._on_search_catalog)
        f_layout.addWidget(btn_search_cat)

        btn_refresh = QPushButton("🔄 Tải Lại")
        btn_refresh.clicked.connect(lambda: self._fetch_catalog(page=self.current_page))
        f_layout.addWidget(btn_refresh)

        f_layout.addWidget(QLabel("| Xem:"))
        self.btn_view_grid = QPushButton("🖼️ Lưới (Grid)")
        self.btn_view_grid.setProperty("class", "btn-toggle-active")
        self.btn_view_grid.clicked.connect(self._switch_to_grid_view)
        f_layout.addWidget(self.btn_view_grid)

        self.btn_view_table = QPushButton("📋 Bảng (Table)")
        self.btn_view_table.clicked.connect(self._switch_to_table_view)
        f_layout.addWidget(self.btn_view_table)

        layout.addWidget(filter_card)

        # 2. Category Filter Pills Bar (Horizontal Scroll Area)
        pills_card = QFrame()
        pills_card.setProperty("class", "card")
        pills_layout = QVBoxLayout(pills_card)
        pills_layout.setContentsMargins(6, 6, 6, 6)
        pills_layout.setSpacing(4)

        cat_title_row = QHBoxLayout()
        lbl_cat_title = QLabel("📂 Danh mục / Thể loại phim:")
        lbl_cat_title.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 12px;")
        cat_title_row.addWidget(lbl_cat_title)
        cat_title_row.addStretch()
        self.lbl_cat_active_name = QLabel("Đang xem: 🔥 Tất Cả")
        self.lbl_cat_active_name.setStyleSheet("color: #94a3b8; font-size: 11px;")
        cat_title_row.addWidget(self.lbl_cat_active_name)
        pills_layout.addLayout(cat_title_row)

        self.pills_scroll = QScrollArea()
        self.pills_scroll.setFixedHeight(44)
        self.pills_scroll.setWidgetResizable(True)
        self.pills_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pills_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.pills_container = QWidget()
        self.pills_hbox = QHBoxLayout(self.pills_container)
        self.pills_hbox.setContentsMargins(4, 2, 4, 2)
        self.pills_hbox.setSpacing(8)
        self.pills_hbox.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.pills_scroll.setWidget(self.pills_container)
        pills_layout.addWidget(self.pills_scroll)

        layout.addWidget(pills_card)

        # 3. Results status & Pagination Controls
        status_bar = QHBoxLayout()
        self.lbl_cat_count = QLabel("⏳ Đang nạp sẵn danh mục phim từ trang chủ...")
        self.lbl_cat_count.setStyleSheet("color: #94a3b8; font-weight: 600;")
        status_bar.addWidget(self.lbl_cat_count)
        status_bar.addStretch()

        self.btn_prev_page = QPushButton("◀ Trang trước")
        self.btn_prev_page.setEnabled(False)
        self.btn_prev_page.clicked.connect(self._on_prev_page)
        status_bar.addWidget(self.btn_prev_page)

        self.lbl_page_num = QLabel("Trang 1")
        self.lbl_page_num.setStyleSheet("font-weight: bold; color: #38bdf8; padding: 0 6px;")
        status_bar.addWidget(self.lbl_page_num)

        self.btn_next_page = QPushButton("Trang sau ▶")
        self.btn_next_page.clicked.connect(self._on_next_page)
        status_bar.addWidget(self.btn_next_page)

        layout.addLayout(status_bar)

        # 4. Stacked Widget (Page 0: Thumbnail Grid, Page 1: Compact Table)
        self.catalog_stack = QStackedWidget()

        # --- Page 0: Poster Thumbnail Grid ---
        self.scroll_grid = QScrollArea()
        self.scroll_grid.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_grid.setWidget(self.grid_container)
        self.catalog_stack.addWidget(self.scroll_grid)

        # --- Page 1: Compact Table ---
        self.table_catalog = QTableWidget()
        self.table_catalog.setColumnCount(5)
        self.table_catalog.setHorizontalHeaderLabels([
            "ID / Mã", "Tên Phim", "Số Tập", "Điểm / Thể Loại", "Hành Động"
        ])
        self.table_catalog.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_catalog.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_catalog.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_catalog.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_catalog.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_catalog.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_catalog.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_catalog.cellDoubleClicked.connect(self._on_catalog_table_double_clicked)
        self.catalog_stack.addWidget(self.table_catalog)

        # --- Page 2: Drama Detail Page (Web-like Streaming & Episode Browser) ---
        self.detail_widget = self._create_detail_widget()
        self.catalog_stack.addWidget(self.detail_widget)

        layout.addWidget(self.catalog_stack, stretch=1)

        # Initialize category pills for default platform (dramabox)
        self._populate_category_pills("dramabox")

    def _populate_category_pills(self, platform_id: str):
        """Builds horizontal category pills for the active platform."""
        # Clear existing buttons
        while self.pills_hbox.count():
            item = self.pills_hbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.category_pills_map.clear()

        plat = dd.get_platform(platform_id)
        categories = plat.get_categories(language=self.current_language) if plat else [{"id": "", "name": "🔥 Tất Cả"}]

        for idx, cat in enumerate(categories):
            cid = str(cat.get("id", ""))
            cname = cat.get("name", "")
            btn = QPushButton(cname)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            is_active = (cid == self.current_category_id) or (idx == 0 and self.current_category_id == "0")
            btn.setProperty("class", "btn-pill-active" if is_active else "btn-pill")

            btn.clicked.connect(lambda _, c_id=cid, c_name=cname: self._on_category_pill_clicked(c_id, c_name))
            self.pills_hbox.addWidget(btn)
            self.category_pills_map[cid] = btn

    def _on_language_changed(self):
        self.current_language = self.combo_cat_lang.currentData() or "vi"
        self.current_category_id = "0"
        self.current_page = 1
        self._populate_category_pills(self.current_platform_id)
        self._fetch_catalog(page=1)


    def _on_category_pill_clicked(self, cat_id: str, cat_name: str):
        if self.catalog_stack.currentIndex() == 2:
            self.catalog_stack.setCurrentIndex(self.last_catalog_view_index)
        self.current_category_id = cat_id
        self.current_page = 1
        self.lbl_cat_active_name.setText(f"Đang xem: {cat_name}")

        # Update button visual states
        for cid, btn in self.category_pills_map.items():
            active = (cid == cat_id)
            btn.setProperty("class", "btn-pill-active" if active else "btn-pill")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self._fetch_catalog(page=1)

    def _on_platform_changed(self):
        if self.catalog_stack.currentIndex() == 2:
            self.catalog_stack.setCurrentIndex(self.last_catalog_view_index)
        plat_id = self.combo_cat_plat.currentData() or self.current_platform_id
        self.current_platform_id = plat_id
        self.current_category_id = "0"
        self.current_page = 1
        self.input_cat_query.clear()
        self._populate_category_pills(plat_id)
        self._fetch_catalog(page=1)


    def _on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._fetch_catalog(page=self.current_page)

    def _on_next_page(self):
        self.current_page += 1
        self._fetch_catalog(page=self.current_page)

    def _switch_to_grid_view(self):
        self.last_catalog_view_index = 0
        self.catalog_stack.setCurrentIndex(0)
        self.btn_view_grid.setProperty("class", "btn-toggle-active")
        self.btn_view_table.setProperty("class", "")
        self.btn_view_grid.style().unpolish(self.btn_view_grid)
        self.btn_view_grid.style().polish(self.btn_view_grid)
        self.btn_view_table.style().unpolish(self.btn_view_table)
        self.btn_view_table.style().polish(self.btn_view_table)

    def _switch_to_table_view(self):
        self.last_catalog_view_index = 1
        self.catalog_stack.setCurrentIndex(1)
        self.btn_view_table.setProperty("class", "btn-toggle-active")
        self.btn_view_grid.setProperty("class", "")
        self.btn_view_grid.style().unpolish(self.btn_view_grid)
        self.btn_view_grid.style().polish(self.btn_view_grid)
        self.btn_view_table.style().unpolish(self.btn_view_table)
        self.btn_view_table.style().polish(self.btn_view_table)

    # --------------------------------------------------------------------------
    # Tab 3: Supported Platforms
    # --------------------------------------------------------------------------
    def _setup_platforms_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        intro = QLabel("Danh sách 11+ Nền Tảng Phim Ngắn OTT Được Tích Hợp Sẵn:")
        intro.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(intro)

        table_plat = QTableWidget()
        table_plat.setColumnCount(4)
        table_plat.setHorizontalHeaderLabels([
            "Mã Nền Tảng", "Tên Hiển Thị", "Cơ Chế Bóc Tách & Giải Mã", "Hỗ Trợ Phụ Đề"
        ])
        table_plat.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table_plat.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table_plat.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table_plat.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        platforms = dd.get_all_platforms()
        table_plat.setRowCount(len(platforms))

        for row, p in enumerate(platforms):
            i_id = QTableWidgetItem(p.platform_id)
            i_id.setForeground(QColor("#38bdf8"))
            table_plat.setItem(row, 0, i_id)
            table_plat.setItem(row, 1, QTableWidgetItem(p.display_name))

            mech = "Trích xuất API + Giải mã liên kết trực tiếp"
            if p.platform_id == "dramabox":
                mech = "Next.js Scrape + Chữ ký số RSA-SHA256 + Goodbos Engine Fallback"
            elif p.platform_id == "hongguo":
                mech = "Modern.js State Loader + Giải mã ByteDance Spade URL (AES-128-CBC)"
            elif p.platform_id == "kisskh":
                mech = "Multi-Mirror Resolver + PNG Stream Decryptor"
            elif p.platform_id == "shortmax":
                mech = "ShortMax Multi-Quality Stream API (1080p, 720p, 540p)"
            elif p.platform_id == "netshort":
                mech = "NetShort PlayVoucher Watch Token Resolver"
            elif p.platform_id == "freereels":
                mech = "Drakula API + Parser phụ đề đa ngôn ngữ"

            table_plat.setItem(row, 2, QTableWidgetItem(mech))

            i_sub = QTableWidgetItem("✔ Có (SRT / VTT)")
            i_sub.setForeground(QColor("#34d399"))
            table_plat.setItem(row, 3, i_sub)

        table_plat.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(table_plat, stretch=1)

        guide = QLabel(
            "💡 Hướng dẫn nhanh:\n"
            "1. Chỉ cần sao chép link tập phim hoặc trang chủ phim từ trình duyệt, bấm 'Dán link'.\n"
            "2. Bấm 'Phân Tích Phim' để hệ thống tự động bóc tách toàn bộ tập và phụ đề.\n"
            "3. Lựa chọn tập bạn muốn tải (hoặc bấm 'Chọn tập Free') rồi bấm 'BẮT ĐẦU TẢI'."
        )
        guide.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 12px; color: #cbd5e1; line-height: 1.5;")
        layout.addWidget(guide)

    # ==========================================================================
    # Logic & Event Handlers
    # ==========================================================================

    def _auto_preload_catalog(self):
        """Automatically preloads the trending home page dramas on application launch."""
        self._log("info", "Đang tự động tải trước danh mục phim trang chủ từ DramaBox...")
        self._fetch_catalog(page=1)

    def _log(self, level: str, message: str):
        colors = {
            "info": "#94a3b8",
            "success": "#34d399",
            "error": "#f87171",
            "warn": "#fbbf24",
        }
        color = colors.get(level, "#e2e8f0")
        t_str = time.strftime("%H:%M:%S")
        self.txt_logs.append(f'<span style="color: #64748b;">[{t_str}]</span> <span style="color: {color};">{message}</span>')
        self.status_label.setText(message)

    def _on_paste_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.input_url.setText(text)
            self._log("info", f"Đã dán liên kết từ bộ nhớ tạm: {text[:50]}...")
            self._on_inspect_clicked()

    def _on_browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Chọn thư mục lưu phim", self.txt_output_dir.text()
        )
        if folder:
            self.txt_output_dir.setText(os.path.abspath(folder))

    def _on_open_folder(self):
        folder = self.txt_output_dir.text()
        if self.current_series:
            series_folder = os.path.join(folder, sanitize_filename(self.current_series.name))
            if os.path.exists(series_folder):
                folder = series_folder
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _on_inspect_clicked(self):
        target = self.input_url.text().strip()
        if not target:
            QMessageBox.warning(self, "Thiếu liên kết", "Vui lòng nhập liên kết hoặc Series ID phim!")
            return

        self.btn_inspect.setEnabled(False)
        self.btn_inspect.setText("⏳ Đang phân tích...")
        self._log("info", f"Đang nhận diện nền tảng và phân tích: {target}")

        self.inspect_worker = InspectWorker(target)
        self.inspect_worker.finished.connect(self._on_inspect_success)
        self.inspect_worker.failed.connect(self._on_inspect_failed)
        self.inspect_worker.start()

    def _on_inspect_success(self, series: Series):
        self.btn_inspect.setEnabled(True)
        self.btn_inspect.setText("🔍 Phân Tích Phim")
        self.current_series = series

        self._log("success", f"✔ Phân tích thành công series: {series.name} ({series.platform.upper()})")

        self.lbl_series_title.setText(f"Tên: {series.name}")
        self.lbl_series_plat.setText(f"Nền tảng: {series.platform.upper()} (ID: {series.series_id})")
        self.lbl_series_stats.setText(f"Tổng số tập: {series.episode_count} | Khả dụng: {series.accessible_count}")
        desc = series.description.strip() if series.description else "Không có mô tả chi tiết."
        self.lbl_series_desc.setText(f"Mô tả: {desc[:250]}..." if len(desc) > 250 else f"Mô tả: {desc}")

        if series.cover:
            self.lbl_cover.setText("Đang tải ảnh...")
            self.thumb_loader = ThumbnailLoader(series.cover)
            self.thumb_loader.loaded.connect(self._on_cover_loaded)
            self.thumb_loader.start()
        else:
            self.lbl_cover.setText("Không có ảnh")

        self._populate_episodes_table(series.episodes)

    def _on_cover_loaded(self, pixmap: QPixmap):
        scaled = pixmap.scaled(
            self.lbl_cover.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_cover.setPixmap(scaled)

    def _on_inspect_failed(self, error_msg: str):
        self.btn_inspect.setEnabled(True)
        self.btn_inspect.setText("🔍 Phân Tích Phim")
        self._log("error", f"✖ Lỗi phân tích phim: {error_msg}")
        QMessageBox.critical(
            self, "Lỗi phân tích", f"Không thể lấy thông tin phim!\nChi tiết: {error_msg}"
        )

    def _populate_episodes_table(self, episodes: List[Episode]):
        self.table_episodes.blockSignals(True)
        self.table_episodes.setRowCount(len(episodes))

        for row, ep in enumerate(episodes):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Checked if not ep.locked else Qt.CheckState.Unchecked)
            self.table_episodes.setItem(row, 0, chk_item)

            ep_item = QTableWidgetItem(f"EP{ep.num:03d}")
            ep_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_episodes.setItem(row, 1, ep_item)

            title_item = QTableWidgetItem(ep.title)
            self.table_episodes.setItem(row, 2, title_item)

            status_item = QTableWidgetItem("🔓 FREE" if not ep.locked else "🔒 VIP/KHÓA")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QColor("#34d399") if not ep.locked else QColor("#f87171"))
            self.table_episodes.setItem(row, 3, status_item)

            sub_count = len(ep.subs)
            sub_text = f"✔ {sub_count} phụ đề" if sub_count > 0 else "---"
            sub_item = QTableWidgetItem(sub_text)
            sub_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_item.setForeground(QColor("#38bdf8") if sub_count > 0 else QColor("#64748b"))
            self.table_episodes.setItem(row, 4, sub_item)

            prog_item = QTableWidgetItem("Chờ tải")
            prog_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            prog_item.setForeground(QColor("#94a3b8"))
            self.table_episodes.setItem(row, 5, prog_item)

            # Column 6: Direct stream player
            btn_play = QPushButton("▶ Xem")
            btn_play.setProperty("class", "btn-secondary")
            btn_play.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if ep.locked and not ep.direct_url:
                btn_play.setText("🔒 Khóa")
                btn_play.setEnabled(False)
                btn_play.setStyleSheet("padding: 2px 8px; font-size: 11px; color: #64748b;")
            else:
                btn_play.setStyleSheet("padding: 2px 8px; font-size: 11px; font-weight: bold; color: #38bdf8;")
                btn_play.clicked.connect(lambda _, r=row: self._open_player(r))
            self.table_episodes.setCellWidget(row, 6, btn_play)

        self.table_episodes.blockSignals(False)
        self._update_selected_count()

    def _on_episode_table_double_clicked(self, row: int, column: int):
        self._open_player(row)

    def _open_player(self, episode_index: int):
        if not self.current_series or not self.current_series.episodes:
            return
        if episode_index < 0 or episode_index >= len(self.current_series.episodes):
            return
        ep = self.current_series.episodes[episode_index]
        if ep.locked and not ep.direct_url:
            QMessageBox.warning(
                self,
                "Tập VIP/Khóa",
                f"Tập {ep.num} ({ep.title}) đang bị khóa VIP bởi nền tảng nên không có luồng phát trực tiếp."
            )
            return

        dialog = DramaPlayerDialog(
            series=self.current_series,
            episodes=self.current_series.episodes,
            initial_index=episode_index,
            parent=self,
        )
        dialog.exec()

    def _on_table_item_changed(self, item: QTableWidgetItem):
        if item.column() == 0:
            self._update_selected_count()

    def _update_selected_count(self):
        selected_count = 0
        for row in range(self.table_episodes.rowCount()):
            item = self.table_episodes.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected_count += 1

        self.lbl_selected_counter.setText(f"Đã chọn: {selected_count} tập")
        self.btn_start_download.setText(f"🚀 BẮT ĐẦU TẢI ({selected_count} tập)")
        self.btn_start_download.setEnabled(selected_count > 0 and self.current_series is not None)

    def _set_all_episodes_checked(self, checked: bool):
        self.table_episodes.blockSignals(True)
        for row in range(self.table_episodes.rowCount()):
            item = self.table_episodes.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.table_episodes.blockSignals(False)
        self._update_selected_count()

    def _select_accessible_episodes_only(self):
        if not self.current_series:
            return
        self.table_episodes.blockSignals(True)
        for row, ep in enumerate(self.current_series.episodes):
            item = self.table_episodes.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked if not ep.locked else Qt.CheckState.Unchecked)
        self.table_episodes.blockSignals(False)
        self._update_selected_count()

    def _apply_range_selection(self):
        if not self.current_series:
            return
        range_str = self.input_range.text().strip()
        if not range_str:
            return
        try:
            target_nums = set(dd.cli.parse_range(range_str, len(self.current_series.episodes)))
            self.table_episodes.blockSignals(True)
            for row, ep in enumerate(self.current_series.episodes):
                item = self.table_episodes.item(row, 0)
                if item:
                    item.setCheckState(
                        Qt.CheckState.Checked if ep.num in target_nums else Qt.CheckState.Unchecked
                    )
            self.table_episodes.blockSignals(False)
            self._update_selected_count()
            self._log("info", f"Đã áp dụng dải tập: {range_str}")
        except Exception as e:
            QMessageBox.warning(self, "Sai định dạng", f"Dải tập không hợp lệ: {e}")

    # --------------------------------------------------------------------------
    # Download Execution Handlers
    # --------------------------------------------------------------------------

    def _on_start_download(self):
        if not self.current_series:
            return

        selected_eps: List[Episode] = []
        for row in range(self.table_episodes.rowCount()):
            item = self.table_episodes.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected_eps.append(self.current_series.episodes[row])

        if not selected_eps:
            QMessageBox.warning(self, "Chưa chọn tập", "Vui lòng tích chọn ít nhất 1 tập để tải!")
            return

        out_dir = self.txt_output_dir.text().strip()
        if not out_dir:
            out_dir = os.path.abspath("./downloads")

        self.btn_start_download.setEnabled(False)
        self.btn_stop_download.setEnabled(True)
        self.btn_inspect.setEnabled(False)

        self.bar_overall.setValue(0)
        self.bar_current.setValue(0)
        self.lbl_overall_txt.setText(f"Tổng quan: 0 / {len(selected_eps)} tập (0%)")

        self.download_worker = DownloadWorker(
            series=self.current_series,
            target_episodes=selected_eps,
            output_dir=out_dir,
            save_vtt=self.chk_save_vtt.isChecked(),
            save_thumb=self.chk_save_thumb.isChecked(),
        )


        self.download_worker.overall_progress.connect(self._on_overall_progress)
        self.download_worker.episode_started.connect(self._on_ep_started)
        self.download_worker.episode_progress.connect(self._on_ep_progress)
        self.download_worker.episode_finished.connect(self._on_ep_finished)
        self.download_worker.episode_failed.connect(self._on_ep_failed)
        self.download_worker.all_finished.connect(self._on_all_finished)
        self.download_worker.log_msg.connect(self._log)
        self.download_worker.start()

    def _on_stop_download(self):
        if self.download_worker:
            self.download_worker.cancel()
            self._log("warn", "Đang gửi tín hiệu dừng tiến trình tải...")
            self.btn_stop_download.setEnabled(False)

    def _on_overall_progress(self, current_done: int, total: int):
        percent = int((current_done / total) * 100) if total > 0 else 0
        self.bar_overall.setValue(percent)
        self.lbl_overall_txt.setText(f"Tổng quan: {current_done} / {total} tập ({percent}%)")

    def _on_ep_started(self, ep_num: int, title: str):
        self.lbl_curr_ep.setText(f"Đang tải: EP{ep_num:03d} - {title}")
        self.bar_current.setValue(0)
        self._update_table_ep_status(ep_num, "Đang tải...", "#38bdf8")

    def _on_ep_progress(self, ep_num: int, percent: float, speed_mb: float):
        self.bar_current.setValue(int(percent))
        self.lbl_speed.setText(f"Tốc độ: {speed_mb:.1f} MB/s")
        self._update_table_ep_status(ep_num, f"{percent:.1f}%", "#38bdf8")

    def _on_ep_finished(self, ep_num: int, file_path: str):
        self._update_table_ep_status(ep_num, "✔ Đã tải xong", "#34d399")

    def _on_ep_failed(self, ep_num: int, err_msg: str):
        self._update_table_ep_status(ep_num, "✖ Thất bại", "#f87171")

    def _update_table_ep_status(self, ep_num: int, text: str, color_hex: str):
        if not self.current_series:
            return
        for row, ep in enumerate(self.current_series.episodes):
            if ep.num == ep_num:
                item = self.table_episodes.item(row, 5)
                if item:
                    item.setText(text)
                    item.setForeground(QColor(color_hex))
                break

    def _on_all_finished(self, success_count: int, fail_count: int):
        self.btn_start_download.setEnabled(True)
        self.btn_stop_download.setEnabled(False)
        self.btn_inspect.setEnabled(True)
        self.lbl_speed.setText("Tốc độ: 0.0 MB/s")
        self.bar_current.setValue(100)

        msg = f"Tải hoàn tất: {success_count} tập thành công, {fail_count} thất bại."
        self._log("success" if fail_count == 0 else "warn", msg)

        QMessageBox.information(
            self,
            "Kết quả tải",
            f"Phiên tải đã kết thúc!\n- Thành công: {success_count} tập\n- Thất bại: {fail_count} tập\n\nBạn có thể bấm 'Mở thư mục' để xem các tập đã tải.",
        )

    # --------------------------------------------------------------------------
    # Catalog Tab Logic, Category Filtering & Poster Grid Rendering
    # --------------------------------------------------------------------------

    def _on_search_catalog(self):
        self.current_page = 1
        self._fetch_catalog(page=1)

    def _fetch_catalog(self, page: int = 1):
        plat = self.combo_cat_plat.currentData() or self.current_platform_id
        query = self.input_cat_query.text().strip()
        category = self.current_category_id


        self.current_page = page
        self.lbl_page_num.setText(f"Trang {self.current_page}")
        self.btn_prev_page.setEnabled(self.current_page > 1)

        self.lbl_cat_count.setText(f"⏳ Đang tải phim [{plat.upper()}] (Trang {self.current_page})...")
        self._log("info", f"Tra cứu catalog: {plat.upper()} | Danh mục: {category} | Trang: {page} | Từ khóa: '{query}'")

        self.catalog_worker = CatalogWorker(
            plat,
            query=query,
            category=category,
            page=page,
            language=self.current_language,
        )
        self.catalog_worker.finished.connect(self._on_catalog_loaded)
        self.catalog_worker.failed.connect(lambda e: self._log("error", f"Lỗi tra cứu catalog: {e}"))
        self.catalog_worker.start()


    def _on_catalog_loaded(self, items: List[CatalogItem], total: int):
        self.current_catalog_items = items
        self.total_catalog_count = total
        plat_name = self.combo_cat_plat.currentText().upper()

        if total > 0:
            self.lbl_cat_count.setText(f"🎉 Tìm thấy {len(items)} phim (Tổng ~{total}) từ {plat_name} - Trang {self.current_page}.")
        else:
            self.lbl_cat_count.setText(f"🎉 Hiển thị {len(items)} bộ phim từ {plat_name} - Trang {self.current_page}.")

        self._log("success", f"Đã tải {len(items)} phim từ {plat_name}.")

        # 1. Populate Poster Grid View
        self._render_poster_grid(items)

        # 2. Populate Compact Table View
        self._render_compact_table(items)

    def _render_poster_grid(self, items: List[CatalogItem]):
        self.card_map.clear()
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for w in self.card_workers:
            if w.isRunning():
                w.terminate()
        self.card_workers.clear()

        if not items:
            plat_obj = dd.get_platform(self.current_platform_id)
            p_name = plat_obj.display_name if plat_obj else self.current_platform_id
            empty_widget = QWidget()
            e_layout = QVBoxLayout(empty_widget)
            e_layout.setContentsMargins(20, 40, 20, 40)
            e_layout.setSpacing(10)
            e_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e_lbl1 = QLabel(f"🎬 Nền tảng {p_name} ({self.current_platform_id})")
            e_lbl1.setStyleSheet("color: #38bdf8; font-size: 16px; font-weight: bold;")
            e_lbl2 = QLabel("Nền tảng này hỗ trợ bóc tách & tải video trực tiếp qua liên kết tập phim (URL).\nBạn chỉ cần sao chép link phim từ web và dán vào Tab '📥 Tải Phim Theo Link' để tải trọn bộ.")
            e_lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e_lbl2.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 1.5;")
            btn_goto_dl = QPushButton("👉 Chuyển sang Tab Tải Phim Theo Link")
            btn_goto_dl.setProperty("class", "btn-primary")
            btn_goto_dl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_goto_dl.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
            e_layout.addWidget(e_lbl1, alignment=Qt.AlignmentFlag.AlignCenter)
            e_layout.addWidget(e_lbl2, alignment=Qt.AlignmentFlag.AlignCenter)
            e_layout.addWidget(btn_goto_dl, alignment=Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_widget, 0, 0, 1, 5)
            return


        columns = 5
        for idx, item in enumerate(items):
            row = idx // columns
            col = idx % columns

            card = DramaCardWidget(item)
            card.download_requested.connect(self._load_item_into_downloader)
            card.detail_requested.connect(self._show_drama_detail)
            self.grid_layout.addWidget(card, row, col)
            self.card_map[str(item.id)] = card

            cover_url = item.cover
            if cover_url:
                if cover_url in self.pixmap_cache:
                    card.set_thumbnail(self.pixmap_cache[cover_url])
                else:
                    worker = CardImageWorker(str(item.id), cover_url)
                    worker.image_loaded.connect(self._on_card_image_ready)
                    self.card_workers.append(worker)
                    worker.start()

    def _on_card_image_ready(self, item_id: str, pixmap: QPixmap):
        if item_id in self.card_map:
            card = self.card_map[item_id]
            card.set_thumbnail(pixmap)
            if card.item.cover:
                self.pixmap_cache[card.item.cover] = pixmap

    def _render_compact_table(self, items: List[CatalogItem]):
        self.table_catalog.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table_catalog.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table_catalog.setItem(row, 1, QTableWidgetItem(item.name))
            self.table_catalog.setItem(row, 2, QTableWidgetItem(f"{item.episodes} tập"))

            score = item.score or ""
            tags = ", ".join(item.tags) if item.tags else ""
            desc_tag = f"{score} | {tags}".strip(" |")
            self.table_catalog.setItem(row, 3, QTableWidgetItem(desc_tag))

            btn_box = QWidget()
            b_layout = QHBoxLayout(btn_box)
            b_layout.setContentsMargins(0, 0, 0, 0)
            b_layout.setSpacing(6)

            btn_det = QPushButton("🔍 Chi Tiết")
            btn_det.setProperty("class", "btn-secondary")
            btn_det.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_det.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_det.clicked.connect(lambda _, it=item: self._show_drama_detail(it))
            b_layout.addWidget(btn_det)

            btn_load = QPushButton("📥 Tải Về")
            btn_load.setProperty("class", "btn-primary")
            btn_load.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_load.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_load.clicked.connect(lambda _, it=item: self._load_item_into_downloader(it))
            b_layout.addWidget(btn_load)

            self.table_catalog.setCellWidget(row, 4, btn_box)

    def _on_catalog_table_double_clicked(self, row: int, col: int):
        if 0 <= row < len(self.current_catalog_items):
            self._show_drama_detail(self.current_catalog_items[row])

    # --------------------------------------------------------------------------
    # Web-Style Drama Detail View (Metadata + Live Streaming + Episode Grid)
    # --------------------------------------------------------------------------

    def _create_detail_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(10)

        # Top Navigation Bar
        nav_bar = QHBoxLayout()
        btn_back = QPushButton("⬅ Quay Lại Danh Mục")
        btn_back.setProperty("class", "btn-secondary")
        btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_back.clicked.connect(self._back_to_catalog_list)
        nav_bar.addWidget(btn_back)

        self.lbl_detail_breadcrumb = QLabel("Khám Phá > Chi Tiết Phim")
        self.lbl_detail_breadcrumb.setStyleSheet("color: #94a3b8; font-size: 12px; margin-left: 8px;")
        nav_bar.addWidget(self.lbl_detail_breadcrumb)
        nav_bar.addStretch()

        btn_load_dl = QPushButton("📥 Chuyển Sang Tab Tải Phim")
        btn_load_dl.setProperty("class", "btn-primary")
        btn_load_dl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_load_dl.clicked.connect(self._detail_send_to_downloader)
        nav_bar.addWidget(btn_load_dl)

        layout.addLayout(nav_bar)

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(6, 6, 6, 6)
        c_layout.setSpacing(14)

        # 1. Hero Card
        hero_card = QFrame()
        hero_card.setProperty("class", "card")
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(14, 14, 14, 14)
        hero_layout.setSpacing(18)

        self.lbl_detail_cover = QLabel()
        self.lbl_detail_cover.setFixedSize(180, 240)
        self.lbl_detail_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_detail_cover.setStyleSheet(
            "background-color: #0b0f19; border-radius: 8px; border: 1px solid #1e293b; color: #64748b;"
        )
        hero_layout.addWidget(self.lbl_detail_cover, alignment=Qt.AlignmentFlag.AlignTop)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        self.lbl_detail_title = QLabel("Tên Phim")
        self.lbl_detail_title.setStyleSheet("font-size: 19px; font-weight: bold; color: #38bdf8;")
        self.lbl_detail_title.setWordWrap(True)
        info_layout.addWidget(self.lbl_detail_title)

        # Badges row
        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)
        self.lbl_detail_platform = QLabel("🎬 DramaBox")
        self.lbl_detail_platform.setStyleSheet(
            "background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold;"
        )
        self.lbl_detail_episodes = QLabel("📺 0 tập")
        self.lbl_detail_episodes.setStyleSheet(
            "background: #1e293b; color: #34d399; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold;"
        )
        self.lbl_detail_score = QLabel("⭐ 9.8")
        self.lbl_detail_score.setStyleSheet(
            "background: #1e293b; color: #fbbf24; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold;"
        )
        badges_row.addWidget(self.lbl_detail_platform)
        badges_row.addWidget(self.lbl_detail_episodes)
        badges_row.addWidget(self.lbl_detail_score)
        badges_row.addStretch()
        info_layout.addLayout(badges_row)

        self.lbl_detail_tags = QLabel("Thể loại: Đang cập nhật")
        self.lbl_detail_tags.setStyleSheet("color: #94a3b8; font-size: 12px;")
        info_layout.addWidget(self.lbl_detail_tags)

        # Synopsis
        self.lbl_detail_desc = QLabel("Đang tải tóm tắt nội dung phim...")
        self.lbl_detail_desc.setWordWrap(True)
        self.lbl_detail_desc.setStyleSheet(
            "color: #cbd5e1; font-size: 13px; line-height: 1.5; padding: 4px 0;"
        )
        info_layout.addWidget(self.lbl_detail_desc)

        # Action Buttons Row
        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        self.btn_detail_play_ep1 = QPushButton("▶ Xem Ngay Tập 1")
        self.btn_detail_play_ep1.setProperty("class", "btn-primary")
        self.btn_detail_play_ep1.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_detail_play_ep1.clicked.connect(self._detail_play_first_episode)
        act_row.addWidget(self.btn_detail_play_ep1)

        self.btn_detail_open_web = QPushButton("🌐 Mở Trên Web Gốc")
        self.btn_detail_open_web.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_detail_open_web.clicked.connect(self._detail_open_web)
        act_row.addWidget(self.btn_detail_open_web)

        act_row.addStretch()
        info_layout.addLayout(act_row)

        info_layout.addStretch()
        hero_layout.addLayout(info_layout, stretch=1)
        c_layout.addWidget(hero_card)

        # 2. Episode Selection Section
        ep_card = QFrame()
        ep_card.setProperty("class", "card")
        ep_layout = QVBoxLayout(ep_card)
        ep_layout.setContentsMargins(14, 12, 14, 14)
        ep_layout.setSpacing(10)

        ep_header = QHBoxLayout()
        lbl_ep_header = QLabel("📺 Danh Sách Các Tập Phim (Bấm vào tập để xem trực tiếp):")
        lbl_ep_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #f1f5f9;")
        ep_header.addWidget(lbl_ep_header)

        self.lbl_detail_inspect_status = QLabel("⏳ Đang tải thông tin tập...")
        self.lbl_detail_inspect_status.setStyleSheet("color: #38bdf8; font-size: 12px;")
        ep_header.addWidget(self.lbl_detail_inspect_status)
        ep_header.addStretch()
        ep_layout.addLayout(ep_header)

        self.detail_episodes_container = QWidget()
        self.detail_episodes_grid = QGridLayout(self.detail_episodes_container)
        self.detail_episodes_grid.setSpacing(8)
        self.detail_episodes_grid.setContentsMargins(4, 4, 4, 4)
        self.detail_episodes_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        ep_layout.addWidget(self.detail_episodes_container)
        c_layout.addWidget(ep_card)

        c_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        return widget

    def _show_drama_detail(self, item: CatalogItem):
        # Save previous view (Grid or Table)
        curr = self.catalog_stack.currentIndex()
        if curr in (0, 1):
            self.last_catalog_view_index = curr

        self.current_detail_item = item
        self.current_detail_series = None

        plat_obj = dd.get_platform(item.platform or self.current_platform_id)
        plat_name = plat_obj.display_name if plat_obj else (item.platform or self.current_platform_id)

        self.lbl_detail_breadcrumb.setText(f"Khám Phá > {plat_name} > {item.name}")
        self.lbl_detail_title.setText(item.name)
        self.lbl_detail_platform.setText(f"🎬 {plat_name}")
        self.lbl_detail_episodes.setText(f"📺 {item.episodes} tập")
        self.lbl_detail_score.setText(f"⭐ {item.score or '9.8'}")

        tags_str = ", ".join(item.tags) if item.tags else "Đang cập nhật"
        self.lbl_detail_tags.setText(f"Thể loại: {tags_str}")

        desc_text = item.desc if item.desc else "Đang kết nối máy chủ để tải tóm tắt nội dung và danh sách các tập phim..."
        self.lbl_detail_desc.setText(desc_text)

        # Set cover image
        self._set_detail_cover(item.cover)

        # Clear existing episode buttons
        while self.detail_episodes_grid.count():
            child = self.detail_episodes_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.lbl_detail_inspect_status.setText("⏳ Đang kết nối máy chủ để nạp các tập phim & luồng xem trực tiếp...")
        self.btn_detail_play_ep1.setEnabled(False)

        # Switch to detail page (Page 2)
        self.catalog_stack.setCurrentIndex(2)

        # Fetch series details in background
        target = item.link or item.id
        if self.detail_inspect_worker and self.detail_inspect_worker.isRunning():
            self.detail_inspect_worker.terminate()
        self.detail_inspect_worker = InspectWorker(target, platform_hint=item.platform or self.current_platform_id)
        self.detail_inspect_worker.finished.connect(self._on_detail_inspect_finished)
        self.detail_inspect_worker.failed.connect(self._on_detail_inspect_failed)
        self.detail_inspect_worker.start()

    def _set_detail_cover(self, cover_url: Optional[str]):
        if not cover_url:
            self.lbl_detail_cover.setText("Không có ảnh")
            self.lbl_detail_cover.setPixmap(QPixmap())
            return

        if cover_url in self.pixmap_cache:
            self._set_detail_cover_pixmap(self.pixmap_cache[cover_url])
        else:
            self.lbl_detail_cover.setText("Đang tải ảnh...")
            self.lbl_detail_cover.setPixmap(QPixmap())
            self.detail_thumb_loader = ThumbnailLoader(cover_url)
            self.detail_thumb_loader.loaded.connect(self._on_detail_thumb_loaded)
            self.detail_thumb_loader.start()

    def _on_detail_thumb_loaded(self, pixmap: QPixmap):
        if self.current_detail_item and self.current_detail_item.cover:
            self.pixmap_cache[self.current_detail_item.cover] = pixmap
        self._set_detail_cover_pixmap(pixmap)

    def _set_detail_cover_pixmap(self, pixmap: QPixmap):
        target_w, target_h = 180, 240
        scaled = pixmap.scaled(
            target_w,
            target_h,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled.width() - target_w) // 2)
        y = max(0, (scaled.height() - target_h) // 2)
        cropped = scaled.copy(x, y, target_w, target_h)
        self.lbl_detail_cover.setPixmap(cropped)

    def _on_detail_inspect_finished(self, series: Series):
        self.current_detail_series = series
        if series.description and (not self.current_detail_item or not self.current_detail_item.desc):
            self.lbl_detail_desc.setText(series.description)

        ep_count = len(series.episodes)
        self.lbl_detail_episodes.setText(f"📺 {ep_count} tập")
        self.lbl_detail_inspect_status.setText(f"✔ Đã nạp xong {ep_count} tập (Bấm vào số tập để xem trực tiếp):")
        self.btn_detail_play_ep1.setEnabled(ep_count > 0)

        # Clear and populate grid of episode buttons
        while self.detail_episodes_grid.count():
            child = self.detail_episodes_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        cols = 10
        for idx, ep in enumerate(series.episodes):
            row = idx // cols
            col = idx % cols

            btn = QPushButton(f"Tập {ep.num}")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedSize(70, 36)

            if ep.locked and not ep.direct_url:
                btn.setText(f"Tập {ep.num} 🔒")
                btn.setStyleSheet(
                    "background: #090d16; border: 1px solid #1e293b; color: #64748b; font-size: 11px; border-radius: 6px;"
                )
                btn.setToolTip(f"Tập {ep.num}: {ep.title} (VIP / Khóa)")
            else:
                btn.setStyleSheet(
                    "background: #0f172a; border: 1px solid #0284c7; color: #38bdf8; font-weight: bold; font-size: 11px; border-radius: 6px;"
                )
                btn.setToolTip(f"Tập {ep.num}: {ep.title} (Miễn phí - Bấm để phát trực tiếp)")

            btn.clicked.connect(lambda _, ep_idx=idx: self._play_detail_episode(ep_idx))
            self.detail_episodes_grid.addWidget(btn, row, col)

    def _on_detail_inspect_failed(self, err_msg: str):
        self.lbl_detail_inspect_status.setText(f"⚠️ Không thể nạp đầy đủ danh sách tập: {err_msg}")
        self.lbl_detail_inspect_status.setStyleSheet("color: #f87171; font-size: 11px;")

    def _play_detail_episode(self, episode_index: int):
        if not self.current_detail_series or not self.current_detail_series.episodes:
            return
        if episode_index < 0 or episode_index >= len(self.current_detail_series.episodes):
            return
        ep = self.current_detail_series.episodes[episode_index]
        if ep.locked and not ep.direct_url:
            QMessageBox.warning(
                self,
                "Tập VIP/Khóa",
                f"Tập {ep.num} ({ep.title}) đang bị khóa VIP bởi nền tảng nên không có luồng phát trực tiếp."
            )
            return

        dialog = DramaPlayerDialog(
            series=self.current_detail_series,
            episodes=self.current_detail_series.episodes,
            initial_index=episode_index,
            parent=self,
        )
        dialog.exec()

    def _detail_play_first_episode(self):
        self._play_detail_episode(0)

    def _detail_send_to_downloader(self):
        if self.current_detail_item:
            self._load_item_into_downloader(self.current_detail_item)

    def _detail_open_web(self):
        url = None
        if self.current_detail_item and self.current_detail_item.link:
            url = self.current_detail_item.link
        elif self.current_detail_series and self.current_detail_series.url:
            url = self.current_detail_series.url
        if url:
            QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.information(self, "Thông báo", "Phim này không có liên kết web trực tiếp.")

    def _back_to_catalog_list(self):
        target_idx = getattr(self, "last_catalog_view_index", 0)
        self.catalog_stack.setCurrentIndex(target_idx)

    def _load_item_into_downloader(self, item: CatalogItem):
        self.tabs.setCurrentIndex(1)
        target = item.link or item.id
        self.input_url.setText(target)
        self._on_inspect_clicked()


def run_gui():
    """Application entrypoint."""
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DramaDownloader.Studio.App.1.0")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("DramaDownloader")

    icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = DramaDownloaderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
