import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PySide6.QtGui import QFont

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 13))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())