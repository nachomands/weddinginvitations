import sys
from pathlib import Path

# Add the parent directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from Emperor.ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())