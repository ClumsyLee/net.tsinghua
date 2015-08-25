import logging

# Used for simulation.
# TODO: Remove these lines.
from time import sleep
from random import choice

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QThread
from PyQt5.QtNetwork import QNetworkConfigurationManager, QNetworkConfiguration

from manager import Manager

ACCOUNTS_FILENAME = 'accounts.yml'

class Worker(QObject):
    """Worker"""
    def __init__(self, parent=None, accounts_filename=ACCOUNTS_FILENAME):
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
        self.username = None
        self.auto_login = True
        self.manager = Manager(accounts_filename)

        # Timers.
        self.check_status_timer = QTimer(self)
        self.check_status_timer.setInterval(5000)

        # Monitor online status.
        self.network_manager = QNetworkConfigurationManager(self)

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

    def app_started(self):
        """Things to do when the app has started"""
        self.check_status_timer.timeout.connect(self.check_status)
        self.check_status_timer.start()
        self.network_manager.onlineStateChanged.connect(self.check_status)

        self.check_status()  # Initial check.

    def check_status(self):
        """Check current status, take actions if needed"""
        self.update_status()

        # Actions.
        if self.auto_login and self.status == 'OFFLINE':
            self.login()

    def update_status(self):
        """Update current status"""
        logging.debug('Updating status')

        if not self.network_manager.isOnline():
            self.status = 'NO_CONNECTION'
            return

        # TODO: Implement.
        sleep(1)
        self.status = choice(['OFFLINE', 'ONLINE', 'UNKNOWN_ACCOUNT_ONLINE',
                              'NETWORK_ERROR'])

    def login(self):
        self.status = 'LOGGING_IN'
        self.manager.login()
        self.update_status()

    def logout(self):
        self.status = 'LOGGING_OUT'
        self.manager.logout()
        self.update_status()
