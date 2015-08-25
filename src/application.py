import logging

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon

from worker import Worker
import resource

STATUSES = {
'NO_CONNECTION': '无连接',
'OFFLINE': '离线',
'LOGGING_IN': '上线中…',
'ONLINE': '在线',
'UNKNOWN_ACCOUNT_ONLINE': '他人账号在线',
'LOGGING_OUT': '下线中…',
'NETWORK_ERROR': '网络错误'
}


class NetDotTsinghuaApplication(QApplication):
    """docstring for NetDotTsinghuaApplication"""
    def __init__(self, argv):
        super().__init__(argv)

        self.tray = QSystemTrayIcon(QIcon(":/icon.png"), self)
        self.tray_menu = QMenu()

        # Set up tray menu.
        self.status_action = self.tray_menu.addAction('在线 2小时43分钟 - 3.23G')
        # self.tray_menu.addAction('本次使用 3.23G').setEnabled(False)
        self.auto_manage_action = self.tray_menu.addAction('自动管理')
        self.auto_manage_action.setCheckable(True)
        self.status_action.setEnabled(False)

        self.tray_menu.addSeparator()
        self.tray_menu.addAction('lisihan13').setEnabled(False)
        self.tray_menu.addAction('已用 4.20G，上限 21.45G').setEnabled(False)
        # self.tray_menu.addAction('余额 1.45 元').setEnabled(False)
        self.tray_menu.addAction('上次更新：5分钟前').setEnabled(False)

        self.tray_menu.addSeparator()
        self.tray_menu.addAction('退出').triggered.connect(self.quit)

        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

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
        self.status_action.setText(STATUSES[status])

if __name__ == '__main__':
    import sys

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    app = NetDotTsinghuaApplication(sys.argv)

    sys.exit(app.exec())
