import sys

from PyQt6 import QtWidgets
import pyqtgraph as pg

from ui import MainWindow

APP_VERSION = "v1.0.1"

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set the default background and foreground color to white and black
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    
    main_window = MainWindow(APP_VERSION)
    main_window.show()
    
    sys.exit(app.exec())