#!/usr/bin/python3

import json
import os.path
import subprocess
import sys

from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QColor, QContextMenuEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QListView, QStyledItemDelegate
from main_window_ui import Ui_MainWindow

META_FILE = "meta.json"


class FileExplorerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.current_path = os.path.expanduser("~")  # Get the user's home path on Linux/Windows
        print(self.current_path)

        self.file_states = {}
        if os.path.exists(META_FILE):
            with open(META_FILE, "r") as f:
                self.file_states = json.loads(f.read())

        self.setWindowTitle("Color Tag File Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.file_model = QFileSystemModel()
        self.list_selection_model = QItemSelectionModel(self.file_model)

        self.init_ui()

    def init_ui(self):
        self.file_model.setRootPath(self.current_path)

        self.folderUpButton.clicked.connect(self.go_folder_up)

        self.listView.setModel(self.file_model)
        self.listView.setRootIndex(self.file_model.index(self.current_path))
        self.listView.doubleClicked.connect(self.open_file)

        self.listView.setDragEnabled(True)
        self.listView.setDragDropMode(QListView.DragOnly)
        self.listView.setSelectionMode(QListView.ExtendedSelection)
        self.listView.setDefaultDropAction(Qt.MoveAction)
        self.listView.setDropIndicatorShown(True)

        self.listView.setSelectionModel(self.list_selection_model)

        delegate = ColorDelegate(self.list_selection_model,
                                 self.file_model,
                                 self.listView,
                                 self.current_path,
                                 self.file_states)
        self.listView.setItemDelegate(delegate)

    def closeEvent(self, event):
        print("Close button or Alt+F4 was pressed.")

        with open(META_FILE, "w") as f:
            json.dump(self.file_states, f, indent=2)

        event.accept()

    def open_file(self, index):
        print(f"Opening file: {index.data()}")

        item_text = index.data()
        new_path = os.path.join(self.current_path, item_text)

        if os.path.isfile(new_path):
            if sys.platform == "win32":
                os.startfile(new_path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, new_path])
        else:
            self.listView.setRootIndex(self.file_model.index(new_path))
            self.current_path = new_path

    def go_folder_up(self):
        self.current_path = os.path.dirname(self.current_path)
        self.listView.setRootIndex(self.file_model.index(self.current_path))


class ColorDelegate(QStyledItemDelegate):
    def __init__(self, selection_model, model, view, current_path, file_states, parent=None):
        super().__init__(parent)
        self.selection_model = selection_model
        self.model = model
        self.view = view
        self.current_path = current_path
        self.file_states = file_states

        self.special_item_index = None
        self.normal_color = QColor(Qt.white)
        self.special_color = QColor(Qt.yellow)  # Change this to the desired color
        self.special_color2 = QColor(Qt.red)

    def set_special_item(self, index):
        self.special_item_index = index

    def paint(self, painter, option, index):
        full_path = os.path.join(self.current_path, index.data())

        if full_path in self.file_states:
            painter.save()
            if self.file_states[full_path] == 1:
                painter.fillRect(option.rect, self.special_color)
            elif self.file_states[full_path] == 2:
                painter.fillRect(option.rect, self.special_color2)
            elif self.file_states[full_path] == 0:
                painter.fillRect(option.rect, self.normal_color)
            painter.restore()

        super().paint(painter, option, index)

        if index == self.special_item_index:
            painter.save()
            painter.setPen(Qt.black)
            painter.restore()

    def createEditor(self, parent, option, index):
        return None

    def update_index_value(self, index):
        full_path = os.path.join(self.current_path, index.data())
        if full_path not in self.file_states:
            self.file_states[full_path] = 1
        else:
            self.file_states[full_path] = (self.file_states[full_path] + 1) % 3

    def editorEvent(self, event, model, option, index):
        if event.type() == QContextMenuEvent.MouseButtonRelease and event.button() == Qt.RightButton:
            self.set_special_item(index)
            self.selection_model.clearSelection()
            self.update_index_value(index)
            return True
        return False


def main():
    app = QApplication(sys.argv)
    file_explorer = FileExplorerApp()
    file_explorer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
