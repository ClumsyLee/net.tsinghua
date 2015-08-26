from copy import deepcopy
import logging
import yaml

# Used for simulation.
# TODO: Remove these lines.
from time import sleep
from random import choice

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, QFileSystemWatcher
from PyQt5.QtNetwork import QNetworkConfigurationManager, QNetworkConfiguration

from tsinghua_account import TsinghuaAccount, AbstractAccount

CONFIG_FILENAME = 'config.yml'

class Worker(QObject):
    """Worker"""
    def __init__(self, parent=None, config_filename=CONFIG_FILENAME,
                 account_class=TsinghuaAccount):
        super().__init__(parent)

        # Possible statuses:
        #     NO_CONNECTION
        #     OFFLINE
        #     LOGGING_IN
        #     ONLINE
        #     UNKNOWN_ACCOUNT_ONLINE
        #     LOGGING_OUT
        #     NETWORK_ERROR
        self.config_filename = config_filename
        self.account_class = account_class

        self.config = None
        self._status = 'NO_CONNECTION'
        self.session = None

        # Timers.
        self.check_status_timer = QTimer(self)
        self.check_account_info_timer = QTimer(self)

        # Watchers.
        self.network_manager = QNetworkConfigurationManager(self)
        self.file_system_watcher = QFileSystemWatcher([config_filename], self)

        self.load_config()  # Load configurations at last.
        self.account = account_class(self.config['username'])

    status_changed = pyqtSignal(str)
    account_info_changed = pyqtSignal(AbstractAccount)
    config_reloaded = pyqtSignal(dict)

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
        self.config = yaml.load(open(self.config_filename, encoding='utf-8'))

        # Apply configs.
        self.check_status_timer.setInterval(
            self.config['check_status_interval_msec'])
        self.check_account_info_timer.setInterval(
            self.config['check_account_info_interval_msec'])

    def reload_config(self):
        logging.info('Reloading configuration file')
        self.load_config()
        self.config_reloaded.emit(deepcopy(self.config))

        # Check for user change.
        if self.account.username != self.config['username']:
            logging.info('Username changed from {} to {}'
                         .format(self.account.username,
                                 self.config['username']))
            self.account = self.account_class(self.config['username'])
            # Emit the bare account immediately for a quick response.
            self.account_info_changed.emit(deepcopy(self.account))
            self.update_account_info()

    def app_started(self):
        """Things to do when the app has started"""
        self.check_status_timer.timeout.connect(self.check_status)
        self.check_status_timer.start()
        self.check_account_info_timer.timeout.connect(self.update_account_info)
        self.check_account_info_timer.start()

        self.network_manager.onlineStateChanged.connect(self.check_status)
        self.file_system_watcher.fileChanged.connect(self.reload_config)

        # Initial check.
        self.check_status()
        self.update_account_info()

    def check_status(self):
        """Check current status, take actions if needed"""
        self.update_status()

        # Actions.
        if self.config['auto_manage'] and self.status == 'OFFLINE':
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

    def update_account_info(self):
        logging.debug('Updating account info')
        if self.network_manager.isOnline() and self.account.update():
            self.account_info_changed.emit(deepcopy(self.account))
            logging.info('Account info updated')

    def login(self):
        self.status = 'LOGGING_IN'
        self.account.login()  # TODO: More attempts?
        self.update_status()

    def logout(self):
        self.status = 'LOGGING_OUT'
        self.account.logout()  # TODO: More attempts?
        self.update_status()
