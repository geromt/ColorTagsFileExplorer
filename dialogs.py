import os

from PyQt5.QtGui import QPalette, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QColorDialog
from PyQt5.uic import loadUi

from edit_tags_ui import Ui_EditTagsDialog


class NewFileDialog(QDialog):
    def __init__(self, current_path, parent=None):
        super().__init__(parent)
        loadUi("ui/new-file.ui", self)

        self.current_path = current_path
        self.buttonBox.accepted.connect(self.create_new_file)

    def create_new_file(self):
        fn = self.fileNameLineEdit.text()
        root, ext = os.path.splitext(fn)
        new_path = os.path.join(self.current_path, fn) if ext else os.path.join(self.current_path, f"{fn}.txt")

        with open(new_path, "w") as f:
            f.write("")


class NewFolderDialog(QDialog):
    def __init__(self, current_path, parent=None):
        super().__init__(parent)
        loadUi("ui/new-folder.ui", self)

        self.current_path = current_path
        self.buttonBox.accepted.connect(self.create_new_folder)

    def create_new_folder(self):
        new_path = os.path.join(self.current_path, self.fileNameLineEdit.text())
        os.mkdir(new_path)


class NewColorTagDialog(QDialog):
    def __init__(self, color_tags, parent=None):
        super().__init__(parent)
        loadUi("ui/new-color-tag.ui", self)

        self.color_tags = color_tags

        self.BaseColorButton.clicked.connect(self.base_color_picker)
        self.FontColorButton.clicked.connect(self.font_color_picker)

        self.buttonBox.accepted.connect(self.create_color_tag)

    def base_color_picker(self):
        color = QColorDialog.getColor()
        new_palette = self.exampleColors.palette()
        new_palette.setColor(QPalette.Base, color)
        self.exampleColors.setPalette(new_palette)

    def font_color_picker(self):
        color = QColorDialog.getColor()
        new_palette = self.exampleColors.palette()
        new_palette.setColor(QPalette.Text, color)
        self.exampleColors.setPalette(new_palette)

    def create_color_tag(self):
        palette = self.exampleColors.palette()
        self.color_tags.append((self.tagNameLineEdit.text(),
                                palette.color(QPalette.Base),
                                palette.color(QPalette.Text)))


class EditTagsDialog(QDialog, Ui_EditTagsDialog):
    def __init__(self, color_tags, file_states, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.color_tags = color_tags
        self.file_states = file_states

        self.model = QStandardItemModel()
        self.append_items_to_model()

        self.listView.setModel(self.model)

        self.editTagButton.clicked.connect(self.edit_tag)
        self.deleteButton.clicked.connect(self.delete_tag)
        self.moveUpButton.clicked.connect(self.move_up)
        self.moveDownButton.clicked.connect(self.move_down)


    def edit_tag(self):
        print(f"Data: {self.listView.selectedIndexes()[0].data()}")

    def delete_tag(self, index):
        if len(self.listView.selectedIndexes()) == 0:
            return

        print(f"Delete item: {self.listView.selectedIndexes()[0].data()}")
        index, _ = self.listView.selectedIndexes()[0].data().split(": ")
        index = int(index)
        self.color_tags.pop(index)
        items = list(self.file_states.items())
        for k, v in items:
            if v == index:
                self.file_states.pop(k)
            elif v > index:
                self.file_states[k] = v - 1

        self.model.clear()
        self.append_items_to_model()

    def move_up(self):
        if len(self.listView.selectedIndexes()) == 0:
            return

        print(f"Move up item: {self.listView.selectedIndexes()[0].data()}")
        index, _ = self.listView.selectedIndexes()[0].data().split(": ")
        index = int(index)
        if index > 0:
            self.color_tags[index], self.color_tags[index - 1] = self.color_tags[index - 1], self.color_tags[index]
            for k, v in self.file_states.items():
                if v == index:
                    self.file_states[k] -= 1
                elif v == index - 1:
                    self.file_states[k] += 1

        self.model.clear()
        self.append_items_to_model()

    def move_down(self):
        if len(self.listView.selectedIndexes()) == 0:
            return

        print(f"Move down item: {self.listView.selectedIndexes()[0].data()}")
        index, _ = self.listView.selectedIndexes()[0].data().split(": ")
        index = int(index)
        if index > len(self.color_tags):
            self.color_tags[index], self.color_tags[index + 1] = self.color_tags[index + 1], self.color_tags[index]
            if index > 0:
                self.color_tags[index], self.color_tags[index - 1] = self.color_tags[index - 1], self.color_tags[index]
                for k, v in self.file_states.items():
                    if v == index:
                        self.file_states[k] += 1
                    elif v == index - 1:
                        self.file_states[k] -= 1

        self.model.clear()
        self.append_items_to_model()

    def append_items_to_model(self):
        for k, v in enumerate(self.color_tags):
            if k == 0:
                continue
            item = QStandardItem(f"{k}: {v[0]}")
            self.model.appendRow(item)
