import logging
import yaml

# Used for simulation.
# TODO: Remove these lines.
from time import sleep
from random import choice

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, QFileSystemWatcher
from PyQt5.QtNetwork import QNetworkConfigurationManager, QNetworkConfiguration

from tsinghua_account import TsinghuaAccount

CONFIG_FILENAME = 'config.yml'

class Worker(QObject):
    """Worker"""
    def __init__(self, parent=None, config_filename=CONFIG_FILENAME):
        super().__init__(parent)

        # Possible statuses:
        #     NO_CONNECTION
        #     OFFLINE
        #     LOGGING_IN
        #     ONLINE
        #     UNKNOWN_ACCOUNT_ONLINE
        #     LOGGING_OUT
        #     NETWORK_ERROR
        self._status = 'NO_CONNECTION'
        self.session = None

        self.config_filename = config_filename
        self.config = None
        self.load_config()

        self.account = TsinghuaAccount(self.config['username'])

        # Timers.
        self.check_status_timer = QTimer(self)
        self.check_status_timer.setInterval(
            self.config['check_status_interval_msec'])

        # Watchers.
        self.network_manager = QNetworkConfigurationManager(self)
        self.file_system_watcher = QFileSystemWatcher([config_filename], self)

    status_changed = pyqtSignal(str)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        old_status = self._status
        self._status = new_status
        if old_status != new_status:
            if old_status == 'NO_CONNECTION':
                logging.info('Network is up')
            elif new_status == 'NO_CONNECTION':
                logging.info('Network is down')

            logging.info('Status changed to %s', new_status)
            self.status_changed.emit(new_status)
        else:
            logging.debug('Status remains %s', new_status)

    def load_config(self):
        if self.config:
            logging.info('Reloading configuration file.')
        self.config = yaml.load(open(self.config_filename, encoding='utf-8'))

    def app_started(self):
        """Things to do when the app has started"""
        self.check_status_timer.timeout.connect(self.check_status)
        self.check_status_timer.start()

        self.network_manager.onlineStateChanged.connect(self.check_status)
        self.file_system_watcher.fileChanged.connect(self.load_config)

        self.check_status()  # Initial check.

    def check_status(self):
        """Check current status, take actions if needed"""
        self.update_status()

        # Actions.
        if self.config['auto_login'] and self.status == 'OFFLINE':
            self.login()

    def update_status(self):
        """Update current status"""
        logging.debug('Updating status')

        try:
            if not self.network_manager.isOnline():
                self.status = 'NO_CONNECTION'
            else:
                session = self.account.status()
                if session:  # Online now.
                    self.session = session
                    if session[0] == self.account.username:
                        self.status = 'ONLINE'
                    else:
                        self.status = 'UNKNOWN_ACCOUNT_ONLINE'
                else:
                    self.status = 'OFFLINE'
        except ConnectionError as e:
            logging.error('Failed to update status: %s', e)
            self.status = 'NETWORK_ERROR'

    def login(self):
        self.status = 'LOGGING_IN'
        self.account.login()  # TODO: More attempts?
        self.update_status()

    def logout(self):
        self.status = 'LOGGING_OUT'
        self.account.logout()  # TODO: More attempts?
        self.update_status()
