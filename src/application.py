from datetime import datetime, timedelta
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

GB = 1024**3

def _time_passed_str(t):
    if t is None:
        return '从未'

    delta = datetime.today() - t

    if delta < timedelta(minutes=1):
        return '刚刚'
    if delta < timedelta(hours=1):
        return '{}分钟前'.format(delta // timedelta(minutes=1))
    if delta < timedelta(days=1):
        return '{}小时前'.format(delta // timedelta(hours=1))

    return '{}天前'.format(delta.days)


class NetDotTsinghuaApplication(QApplication):
    """docstring for NetDotTsinghuaApplication"""
    def __init__(self, argv):
        super().__init__(argv)

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # Set up tray menu.
        self.tray = QSystemTrayIcon(QIcon(":/icon.png"), self)
        self.tray_menu = QMenu()

        # Config section.
        self.status_action = self.add_unabled_action('无连接')
        self.auto_manage_action = self.tray_menu.addAction('自动管理')
        self.auto_manage_action.setCheckable(True)
        self.config_reloaded(self.worker.config)

        # Account info section.
        self.tray_menu.addSeparator()
        self.username_action = self.add_unabled_action()
        self.usage_action = self.add_unabled_action()
        self.last_check_action = self.add_unabled_action()
        self.refresh_account_info(self.worker.account)

        self.tray_menu.addSeparator()
        self.tray_menu.addAction('退出').triggered.connect(self.quit)

        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

        self.app_started.connect(self.worker.app_started)
        self.worker.status_changed.connect(self.status_changed)
        self.worker.account_info_changed.connect(self.refresh_account_info)
        self.worker.config_reloaded.connect(self.config_reloaded)

    app_started = pyqtSignal()

    def add_unabled_action(self, text=''):
        action = self.tray_menu.addAction(text)
        action.setEnabled(False)
        return action

    def exec(self):
        self.worker_thread.start()
        self.app_started.emit()  # Start timers & check status.
        return super().exec()

    def status_changed(self, status):
        self.status_action.setText(STATUSES[status])

    def refresh_account_info(self, acc):
        self.username_action.setText(acc.username)

        if acc.last_check is None:
            self.usage_action.setVisible(False)
        else:
            self.usage_action.setVisible(True)
            if acc.byte is None:
                text = '用户名 / 密码错误'
            else:
                text = '已用 {:.1f}G，上限 {:.1f}G'.format(acc.byte / GB,
                                                         acc.max_byte / GB)
            self.usage_action.setText(text)

        self.last_check_action.setText(
            '上次更新：{}'.format(_time_passed_str(acc.last_check)))

    def config_reloaded(self, config):
        self.auto_manage_action.setChecked(config['auto_manage'])

if __name__ == '__main__':
    import sys

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    app = NetDotTsinghuaApplication(sys.argv)

    sys.exit(app.exec())
