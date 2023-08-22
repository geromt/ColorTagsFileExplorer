#!/usr/bin/python3

import json
import os.path
import shutil
import subprocess
import sys

from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QColor, QContextMenuEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QListView, QStyledItemDelegate

from main_window_ui import Ui_MainWindow
from dialogs import EditTagsDialog, NewColorTagDialog, NewFileDialog, NewFolderDialog

META_FILE = "meta.json"


class FileExplorerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # It's a dictionary so that we can modify its value and all the classes can see the current value
        self.current_path = {"path": os.path.expanduser("~")}
        print(self.current_path["path"])

        self.file_states = {}
        self.color_tags = []
        if os.path.exists(META_FILE):
            with open(META_FILE, "r") as f:
                meta_data = json.loads(f.read())
                self.file_states = meta_data["file-states"]
                tags_data = meta_data["color-tags"]
                for v in tags_data:
                    self.color_tags.append((v[0], QColor(v[1]), QColor(v[2])))
        else:
            self.color_tags = [("normal tag", QColor(Qt.white), QColor(Qt.black)),
                               ("special tag", QColor(Qt.yellow), QColor(Qt.black)),
                               ("urgent tag", QColor(Qt.red), QColor(Qt.white))]

        self.setWindowTitle("Color Tag File Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.file_model = QFileSystemModel()
        self.list_selection_model = QItemSelectionModel(self.file_model)

        self.clipboard_items = []
        self.was_cut_selected = False

        self.last_filter = -1

        self.init_ui()

    def init_ui(self):
        self.file_model.setRootPath(self.current_path["path"])

        self.actionNew_File.triggered.connect(self.open_new_file_dialog)
        self.actionNew_Folder_2.triggered.connect(self.open_new_folder_dialog)

        self.actionCopy.triggered.connect(self.copy_items)
        self.actionCut.triggered.connect(self.cut_items)
        self.actionPaste.triggered.connect(self.paste_items)
        self.actionDelete.triggered.connect(self.delete_items)
        self.actionSelect_All.triggered.connect(self.listView.selectAll)

        self.refresh_filter_menu()

        self.actionAdd_new_tag.triggered.connect(self.open_new_color_tag_dialog)
        self.actionEdit_tag.triggered.connect(self.open_edit_tags_dialog)

        self.folderUpButton.clicked.connect(self.go_folder_up)

        self.listView.setModel(self.file_model)
        self.listView.setRootIndex(self.file_model.index(self.current_path["path"]))
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
                                 self.file_states,
                                 self.color_tags)
        self.listView.setItemDelegate(delegate)

    def refresh_filter_menu(self):
        self.menuFilter.clear()
        for k, v in enumerate(self.color_tags):
            action = self.menuFilter.addAction(v[0])
            action.triggered.connect(lambda _, i=k: self.filter_tag(i))

    def closeEvent(self, event):
        print("Close button or Alt+F4 was pressed.")

        with open(META_FILE, "w") as f:
            serializable_tags = []
            for v in self.color_tags:
                serializable_tags.append((v[0], v[1].name(), v[2].name()))

            data = {"file-states": self.file_states,
                    "color-tags": serializable_tags}
            json.dump(data, f, indent=2)

        event.accept()

    def open_file(self, index):
        print(f"Opening file: {index.data()}")

        item_text = index.data()
        new_path = os.path.join(self.current_path["path"], item_text)

        if os.path.isfile(new_path):
            if sys.platform == "win32":
                os.startfile(new_path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, new_path])
        else:
            self.listView.setRootIndex(self.file_model.index(new_path))
            self.current_path["path"] = new_path

    def go_folder_up(self):
        self.current_path["path"] = os.path.dirname(self.current_path["path"])
        self.listView.setRootIndex(self.file_model.index(self.current_path["path"]))

    def open_new_file_dialog(self):
        dialog = NewFileDialog(self.current_path["path"], self)
        dialog.exec()

    def open_new_folder_dialog(self):
        dialog = NewFolderDialog(self.current_path["path"], self)
        dialog.exec()

    def copy_items(self):
        self.clipboard_items = [os.path.join(self.current_path["path"], index.data()) for index in self.listView.selectedIndexes()]

    def cut_items(self):
        self.copy_items()
        self.was_cut_selected = True

    def paste_items(self):
        if self.was_cut_selected:
            for path in self.clipboard_items:
                shutil.move(path, self.current_path["path"])
            self.was_cut_selected = False
        else:
            for path in self.clipboard_items:
                # Only copies files
                if os.path.isfile(path):
                    shutil.copy(path, self.current_path["path"])

        self.clipboard_items = []

    def delete_items(self):
        for item in self.listView.selectedIndexes():
            new_path = os.path.join(self.current_path["path"], item.data())
            if os.path.isfile(new_path):
                os.remove(new_path)
            elif os.path.isdir(new_path):
                os.removedirs(new_path)

    def open_new_color_tag_dialog(self):
        dialog = NewColorTagDialog(self.color_tags, self)
        dialog.exec()
        self.refresh_filter_menu()

    def open_edit_tags_dialog(self):
        dialog = EditTagsDialog(self.color_tags, self.file_states, self)
        dialog.exec()
        self.refresh_filter_menu()

    def filter_tag(self, index):
        print(f"Filter index: {index}")

        for file in os.listdir(self.current_path["path"]):
            path = os.path.join(self.current_path["path"], file)
            file_id = self.file_model.index(path)
            if self.last_filter == index:
                self.listView.setRowHidden(file_id.row(), False)
                continue

            if (path not in self.file_states and index != 0) or (path in self.file_states and self.file_states[path] != index):
                self.listView.setRowHidden(file_id.row(), True)
                print(f"Oculta {path} row {file_id.row()}")
            else:
                self.listView.setRowHidden(file_id.row(), False)

        self.last_filter = index


class ColorDelegate(QStyledItemDelegate):
    def __init__(self, selection_model, model, view, current_path, file_states, color_tags, parent=None):
        super().__init__(parent)
        self.selection_model = selection_model
        self.model = model
        self.view = view
        self.current_path = current_path
        self.file_states = file_states
        self.color_tags = color_tags

        self.special_item_index = None

    def set_special_item(self, index):
        self.special_item_index = index

    def paint(self, painter, option, index):
        full_path = os.path.join(self.current_path["path"], index.data())

        if full_path in self.file_states:
            painter.save()
            painter.fillRect(option.rect, self.color_tags[self.file_states[full_path]][1])
            painter.setPen(self.color_tags[self.file_states[full_path]][2])

            icon = self.model.fileIcon(index)
            rect_width_minus_icon = option.rect.width() - icon.actualSize(option.rect.size()).width()
            icon_rect = option.rect.adjusted(0, 0, -rect_width_minus_icon, 0)
            icon.paint(painter, icon_rect)

            text_rect = option.rect.adjusted(icon.actualSize(option.rect.size()).width() + 5, 0, 0, 0)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, index.data(Qt.DisplayRole))
            painter.restore()
        else:
            super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        return None

    def update_index_value(self, index):
        full_path = os.path.join(self.current_path["path"], index.data())
        if full_path not in self.file_states:
            self.file_states[full_path] = 1
        else:
            self.file_states[full_path] = (self.file_states[full_path] + 1) % len(self.color_tags)

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
