#!/usr/bin/python3

import sys

from PyQt5.QtWidgets import QApplication

from app.src.file_explorer import FileExplorerApp

META_FILE = "../meta.json"

"""
Entry point of the application
"""


def main():
    app = QApplication(sys.argv)
    file_explorer = FileExplorerApp(META_FILE)
    file_explorer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
