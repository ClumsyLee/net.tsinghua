import logging

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon

from worker import Worker

class NetDotTsinghuaApplication(QApplication):
    """docstring for NetDotTsinghuaApplication"""
    def __init__(self, argv):
        super().__init__(argv)

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.app_started.connect(self.worker.app_started)
        self.worker.status_changed.connect(self.status_changed)

    app_started = pyqtSignal()

    def exec(self):
        self.worker_thread.start()
        self.app_started.emit()  # Start timers & check status.
        return super().exec()

    def status_changed(self, status):
        print('Status changed to', status, 'in the GUI thread')

if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = NetDotTsinghuaApplication(sys.argv)

    # tray = QSystemTrayIcon(QIcon(":/icon.jpg"), self)
    # tray_menu = QMenu(self)
    # tray_menu.addAction('hello 世界').setEnabled(False)
    # tray.setContextMenu(self.tray_menu)
    # tray.show()

    sys.exit(app.exec())
