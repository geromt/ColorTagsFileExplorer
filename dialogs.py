import os

from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QDialog, QColorDialog
from PyQt5.uic import loadUi


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
        self.color_tags[len(self.color_tags)] = (self.tagNameLineEdit.text(),
                                                 palette.color(QPalette.Base),
                                                 palette.color(QPalette.Text))
