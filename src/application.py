from datetime import datetime, timedelta
import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon

from tsinghua import Account
from worker import Worker
from config import load_config, save_config, AccountSettingDialog
import resource

STATUS_STR = {
'UNKNOWN': '未知',
'OFFLINE': '离线',
'ONLINE': '在线',
'OTHERS_ACCOUNT_ONLINE': '他人账号在线',
'ERROR': '网络错误',
'NO_CONNECTION': '无连接'
}

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

def _usage_str(byte):
    if byte is None:
        return '未知'
    elif byte < int(10e3):
        return '{}B'.format(byte)
    elif byte < int(10e6):
        return '{:.2f}K'.format(byte / 10e3)
    elif byte < int(10e9):
        return '{:.2fM}'.format(byte / 10e6)
    else:
        return '{:.2fG}'.format(byte / 10e9)

def _balance_str(balance):
    if balance is None:
        return '未知'
    else:
        return '{:.2f}元'.format(balance)

class SessionMenu(QMenu):
    """Session menu"""
    logged_out = pyqtSignal()

    def __init__(self, session):
        super().__init__()
        self.session = session

        self.addAction(session.ip)
        self.start_time = self.addAction('')
        self.update_time()
        self.addAction('下线').toggled.connect(self.logout)

        self.aboutToShow.connect(self.update_time)

    def logout(self):
        try:
            self.session.logout()
            self.logged_out.emit()
        except ConnectionError:
            pass

    def update_time(self):
        self.start_time.setText(_time_passed_str(self.session.start_time) +
                                '上线')


class NetDotTsinghuaApplication(QApplication):
    """NetDotTsinghuaApplication"""
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)  # Run without windows.
        self.account_setting_dialog = None

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        config = self.worker.config
        acc = self.worker.account

        # Set up tray menu.
        self.tray = QSystemTrayIcon(QIcon(":/icon.png"), self)
        self.tray_menu = QMenu()

        # Status section.
        self.status_action = self.add_unabled_action()
        self.status_changed(self.worker.account.status)

        # Account info section.
        self.tray_menu.addSeparator()
        self.username_action = self.add_unabled_action()
        self.usage_action = self.add_unabled_action()
        self.balance_action = self.add_unabled_action()
        self.refresh_username(config['username'])
        self.refresh_account_info(None, None)

        # Sessions section.
        self.sessions = []
        self.session_actions = []

        self.tray_menu.addSeparator()
        self.sessions_title_action = self.add_unabled_action()
        self.last_check_action = self.add_unabled_action()
        self.refresh_sessions([])

        self.last_check = None
        self.tray_menu.aboutToShow.connect(self.update_time)

        # Config section.
        self.tray_menu.addSeparator()
        self.auto_manage_action = self.tray_menu.addAction('自动管理')
        self.auto_manage_action.setCheckable(config['auto_manage'])
        self.auto_manage_action.toggled.connect(self.worker.auto_manage_changed)

        self.account_setting_action = self.tray_menu.addAction('账户设置')
        self.account_setting_action.triggered.connect(self.account_setting)

        # Quit.
        self.tray_menu.addSeparator()
        self.tray_menu.addAction('退出').triggered.connect(self.quit)

        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

        # Connect signals.
        self.start_worker.connect(self.worker.setup)
        self.username_changed.connect(self.refresh_username)
        self.username_changed.connect(self.worker.username_changed)

        acc.status_changed.connect(self.status_changed)
        acc.info_updated.connect(self.refresh_account_info)
        acc.current_session_updated.connect(self.status_changed)
        acc.sessions_updated.connect(self.refresh_sessions)

    start_worker = pyqtSignal()
    username_changed = pyqtSignal(str)

    def add_unabled_action(self, text=''):
        action = self.tray_menu.addAction(text)
        action.setEnabled(False)
        return action

    def exec(self):
        self.worker_thread.start()
        self.start_worker.emit()  # Start timers & check status.
        return super().exec()

    def status_changed(self, status):
        logging.debug('Refreshing status in the menu')

        self.status_action.setText(STATUS_STR[status])

        if status == 'ONLINE':
            self.tray.showMessage('当前在线', '本人账户在线')
        elif status == 'OTHERS_ACCOUNT_ONLINE':
            self.tray.showMessage('当前在线', '他人账户在线')
        elif status == 'OFFLINE':
            self.tray.showMessage('当前离线', '可以登录校园网')

    def refresh_username(self, username):
        logging.debug('Refreshing username in the menu')
        if username is None:
            self.username_action.setText('未设置用户')
            self.usage_action.setVisible(False)
            self.balance_action.setVisible(False)
        else:
            self.username_action.setText(username)
            self.usage_action.setVisible(True)
            self.balance_action.setVisible(True)

    def refresh_account_info(self, balance, byte):
        logging.debug('Refreshing account info section in the menu')

        self.usage_action.setText('本月流量：{}'.format(_usage_str(byte)))
        self.balance_action.setText('当前余额：{}'.format(_balance_str(balance)))

    def refresh_sessions(self, sessions):
        logging.debug('Refreshing sessions section in the menu')

        self.sessions = sessions
        self.last_check = datetime.now()

        if len(sessions):
            self.sessions_title_action.setText('当前在线')
        else:
            self.sessions_title_action.setText('无设备在线')

        new_actions = []
        for session in sessions:
            menu = SessionMenu(session)
            menu.setText(session.device_name)
            # Update infos if logged out.
            menu.logged_out.connect(self.worker.account.update_infos)
            new_actions.append(menu)

        # Remove old actions & add new actions.
        for action in self.session_actions:
            self.tray_menu.removeAction(action)

        self.tray_menu.insertActions(self.last_check_action, new_actions)
        self.session_actions = new_actions

    def update_time(self):
        self.last_check_action.setText(
            '上次更新：{}'.format(_time_passed_str(self.last_check)))

    @pyqtSlot()
    def account_setting(self):
        if self.account_setting_dialog is None:
            self.account_setting_dialog = AccountSettingDialog()
            existed = False
        else:
            existed = True

        dialog = self.account_setting_dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

        if existed:  # Avoid multiple dialogs.
            return

        if dialog.exec():
            username = dialog.username.text()
            # Set password if needed.
            if username:
                acc = Account(username)
                acc.password = dialog.password.text()

            # If username changed, emit signal and clear current account info.
            if username != self.worker.account.username:
                self.username_changed.emit(username)
                self.refresh_account_info(None, None)

        self.account_setting_dialog = None

if __name__ == '__main__':
    import sys

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    app = NetDotTsinghuaApplication(sys.argv)

    sys.exit(app.exec())
