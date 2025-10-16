import sys
import os
import json
import shutil
import tempfile
import pygame

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
                             QLineEdit, QLabel, QHBoxLayout, QRadioButton, QButtonGroup,
                             QSlider, QMenu, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog)
from PyQt5.QtCore import Qt, QUrl, QMimeData, QTimer
from PyQt5.QtGui import QDrag, QFont, QIcon
from sample_parser import scan_folder, search_samples

class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About LMA")
        self.setFixedSize(400, 450) # Size is currently fixed.

        layout = QVBoxLayout()

        message_text = """
        <h3>LMA - Local Sample Manager v0.0.1</h3>
        
        <p> Thank you for using this sample manager tool!</p>
        <p>I aim to help musicians sort and tag their local samples fast.</p>
        <p>Should there be any questions or suggestions, let me know in the GitHub:)<br></p>
        
        <p>感谢你使用这个音频管理工具！</p>
        <p>我旨在努力为大家提供一个轻量、快速的本地音频采样检索方案。</p>
        <p>当前软件处于早期开发阶段，更多功能正在被调试与添加。</p>
        <p>使用中遇到任何问题或建议，请在GitHub告诉我:)<br></p>
        
        <p><b>Developer:</b> Zixiang Zhang</p>
        <p><b>GitHub:</b> <a href='https://github.com/Kircerta/LocalAudioSampleManager'>Kircerta/LocalAudioSampleManager</a>
        <br></p>
        
        <p>Alexxon｜2025.10.15｜Toronto, Ontario, Canada</p>
        """

        message_label = QLabel(message_text)
        message_label.setWordWrap(True)
        message_label.setOpenExternalLinks(True)

        # --- “OK” ---
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        layout.addWidget(message_label)
        layout.addStretch()
        layout.addWidget(ok_button, 0, Qt.AlignCenter)

        self.setLayout(layout)

class DraggableTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        APP_NAME = "LMA"
        APP_VERSION = "v0.0.1"
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}") #Last Updated: 2025.OCT.15

        self.setDragEnabled(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setFont(QFont("Arial", 10))

    def startDrag(self, supportedActions):
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        filename_item = self.item(row, 1)
        if not filename_item:
            return

        filepath = filename_item.data(Qt.UserRole)
        if not filepath: return

        temp_dir = tempfile.gettempdir()
        temp_copy = os.path.join(temp_dir, os.path.basename(filepath))
        shutil.copy(filepath, temp_copy)

        drag = QDrag(self)
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(temp_copy)])
        drag.setMimeData(mime)
        drag.exec_()
        QTimer.singleShot(1000, lambda: os.remove(temp_copy) if os.path.exists(temp_copy) else None)


class SampleManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon.fromTheme("folder-sound"))

        script_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_file = os.path.join(script_dir, "config.json")
        self.index_file = os.path.join(script_dir, "index.json")
        self.favorites_file = os.path.join(script_dir, "favorites.json")

        self.entries = []
        self.favorites = set()

        self.selected_folder = ''
        self.is_playing = False
        self.current_playing_file = None

        self.load_favorites()
        pygame.mixer.init()
        self.init_ui()
        self.load_previous_session()

    def show_info_dialog(self):
        dialog = InfoDialog(self)
        dialog.exec_()

    def init_ui(self):
        layout = QVBoxLayout()
        # --- Folder Selection & Rescan & About ---
        folder_layout = QHBoxLayout()

        folder_btn = QPushButton("Select Folder")
        folder_btn.clicked.connect(self.load_folder)

        rescan_btn = QPushButton("Rescan")
        rescan_btn.clicked.connect(self.rescan_current_folder)

        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_info_dialog)

        self.folder_label = QLabel("No folder selected.")

        folder_layout.addWidget(folder_btn)
        folder_layout.addWidget(rescan_btn)
        folder_layout.addWidget(about_btn)

        folder_layout.addWidget(self.folder_label, 1)
        layout.addLayout(folder_layout)

        # --- Search Inputs ---
        search_layout = QHBoxLayout()
        self.keyword_entry = QLineEdit()
        self.keyword_entry.setPlaceholderText("Keywords...")
        self.key_entry = QLineEdit()
        self.key_entry.setPlaceholderText("Key (e.g., C, Am)")
        self.bpm_from = QLineEdit()
        self.bpm_from.setPlaceholderText("BPM From")
        self.bpm_to = QLineEdit()
        self.bpm_to.setPlaceholderText("BPM To")
        search_layout.addWidget(self.keyword_entry)
        search_layout.addWidget(self.key_entry)
        search_layout.addWidget(self.bpm_from)
        search_layout.addWidget(self.bpm_to)
        layout.addLayout(search_layout)

        # --- Form Filters & Search Button ---
        bottom_search_layout = QHBoxLayout()
        self.form_filter_group = QButtonGroup(self)
        for text in ["All", "Loop", "One-shot", "Fill", "Favorite"]:
            btn = QRadioButton(text)
            if text == "All": btn.setChecked(True)
            self.form_filter_group.addButton(btn)
            bottom_search_layout.addWidget(btn)


        self.form_filter_group.buttonClicked.connect(self.update_results)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.update_results)
        bottom_search_layout.addStretch()
        bottom_search_layout.addWidget(search_btn)
        layout.addLayout(bottom_search_layout)

        # --- Connecting Enter Key ---
        self.keyword_entry.returnPressed.connect(self.update_results)
        self.key_entry.returnPressed.connect(self.update_results)
        self.bpm_from.returnPressed.connect(self.update_results)
        self.bpm_to.returnPressed.connect(self.update_results)

        # --- Results Table ---
        self.result_table = DraggableTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["★", "Filename", "Time", "Key", "BPM"])
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setColumnWidth(0, 30)
        self.result_table.setColumnWidth(2, 60)
        self.result_table.setColumnWidth(3, 60)
        self.result_table.setColumnWidth(4, 60)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.cellClicked.connect(self.handle_item_click)
        self.result_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.result_table)

        # --- Volume Control ---
        vol_layout = QHBoxLayout()
        vol_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(self.volume_slider)
        layout.addLayout(vol_layout)

        self.setLayout(layout)
        self.set_volume(self.volume_slider.value())

    def show_context_menu(self, pos):
        item = self.result_table.itemAt(pos)
        if not item: return

        filepath = self.result_table.item(item.row(), 1).data(Qt.UserRole)
        menu = QMenu()
        action_text = "Remove from collection" if filepath in self.favorites else "Add to collection"
        action = menu.addAction(action_text)
        action.triggered.connect(lambda: self.toggle_favorite(filepath))
        menu.exec_(self.result_table.mapToGlobal(pos))

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Sample Folder")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(folder)

            self.save_config()

            self.entries = scan_folder(folder)
            self.save_index()
            self.update_results()

    def rescan_current_folder(self):
        if self.selected_folder and os.path.exists(self.selected_folder):
            print(f"Rescanning folder: {self.selected_folder}")  # hint "rescanning"
            self.entries = scan_folder(self.selected_folder)
            self.save_index()
            self.update_results()
        else:
            self.load_folder()

    def update_results(self):
        keywords = self.keyword_entry.text().strip().lower().split()
        key = self.key_entry.text().strip()
        try:
            bpm_min = int(self.bpm_from.text()) if self.bpm_from.text() else None
            bpm_max = int(self.bpm_to.text()) if self.bpm_to.text() else None
        except ValueError:
            bpm_min = bpm_max = None

        selected_form = self.form_filter_group.checkedButton().text().lower()
        form = selected_form if selected_form != "all" else "all"

        self.result_table.setRowCount(0)

        source_entries = self.entries
        if selected_form == "saved":
            source_entries = [e for e in self.entries if e['path'] in self.favorites]
            results = search_samples(source_entries, keywords, bpm_min, bpm_max, key, form="all")
        else:
            results = search_samples(self.entries, keywords, bpm_min, bpm_max, key, form)

        for sample in results:
            row_position = self.result_table.rowCount()
            self.result_table.insertRow(row_position)

            fav_icon = "★" if sample['path'] in self.favorites else ""

            self.result_table.setItem(row_position, 0, QTableWidgetItem(fav_icon))
            filename_item = QTableWidgetItem(sample['filename'])
            filename_item.setData(Qt.UserRole, sample['path'])  # Store full path here
            self.result_table.setItem(row_position, 1, filename_item)
            self.result_table.setItem(row_position, 2, QTableWidgetItem(str(sample.get('time', 'N/A'))))
            self.result_table.setItem(row_position, 3, QTableWidgetItem(str(sample.get('key', '--'))))
            self.result_table.setItem(row_position, 4, QTableWidgetItem(str(sample.get('bpm', '--'))))

            self.result_table.item(row_position, 0).setTextAlignment(Qt.AlignCenter)

    def handle_item_click(self, row, column):
        filepath = self.result_table.item(row, 1).data(Qt.UserRole)
        if not os.path.isfile(filepath):
            print(f"[Error] File not found: {filepath}")
            return

        if self.current_playing_file == filepath and self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
        else:
            self.current_playing_file = filepath
            self.play_sound(filepath)

    def play_sound(self, filepath):
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            self.is_playing = True
        except pygame.error as e:
            print(f"[Playback Error] {e}")
            self.is_playing = False

    def set_volume(self, value):
        pygame.mixer.music.set_volume(value / 100.0)

    def toggle_favorite(self, filepath):
        if filepath in self.favorites:
            self.favorites.remove(filepath)
        else:
            self.favorites.add(filepath)
        self.save_favorites()
        self.update_results()

    # --- Session/Favorites Persistence ---
    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, 'r') as f: self.favorites = set(json.load(f))

    def save_favorites(self):
        with open(self.favorites_file, 'w') as f: json.dump(list(self.favorites), f)

    def load_previous_session(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self.selected_folder = config.get("last_folder", "")
            if self.selected_folder and os.path.exists(self.index_file):
                self.folder_label.setText(self.selected_folder)
                try:
                    with open(self.index_file, 'r') as idx_f:
                        self.entries = json.load(idx_f)
                    self.update_results()
                except json.JSONDecodeError:
                    print("Could not read index file. Please rescan.")
                    self.folder_label.setText(f"{self.selected_folder} (Index invalid, please rescan)")

    def save_config(self):
        with open(self.config_file, 'w') as f: json.dump({"last_folder": self.selected_folder}, f)

    def save_index(self):
        with open(self.index_file, 'w') as f: json.dump(self.entries, f)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SampleManagerApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())