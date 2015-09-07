import logging

from PyQt5.QtCore import QObject, QTimer

from tsinghua import Account
from config import load_config, update_config

class Worker(QObject):
    """Worker"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = load_config()
        self.account = Account(self.config['username'], self)

        # Timers.
        self.status_timer = QTimer(self)
        self.info_timer = QTimer(self)
        self.auto_manage_timer = QTimer(self)
        self.status_timer.setInterval(self.config['status_update_interval_msec'])
        self.info_timer.setInterval(self.config['info_update_interval_msec'])
        self.auto_manage_timer.setInterval(self.config['auto_manage_interval_msec'])

    def setup(self):
        """Things to set the worker up"""
        self.status_timer.timeout.connect(self.account.update_status)
        self.info_timer.timeout.connect(self.account.update_infos)
        self.auto_manage_timer.timeout.connect(self.auto_manage)

        self.status_timer.start()
        self.info_timer.start()
        self.auto_manage_timer.start()

        # Double check whether we need to do something when status changed.
        self.account.status_changed.connect(self.auto_manage)

        self.account.setup()

    def auto_manage(self):
        if not self.config['auto_manage']:
            return

        # Auto login.
        if self.account.status == 'OFFLINE':
            self.account.login()

        # TODO: Auto logout, etc.

    def auto_manage_changed(self, enable):
        logging.info('Turning auto_manage %s', 'on' if enable else 'off')
        self.config['auto_manage'] = enable
        update_config(auto_manage=enable)  # Update config.

    def username_changed(self, username):
        logging.info('Changing username from %s to %s', self.account.username,
                                                        username)

        update_config(username=username)  # Update config.

        if self.account.password is not None:
            del self.account.password  # Delete old password, if exists.

        self.account.username = username
        self.account.balance = self.account.byte = None

        self.account.update_all()
