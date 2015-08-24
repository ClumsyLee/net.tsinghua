import logging

# Used for simulation.
# TODO: Remove these lines.
from time import sleep
from random import choice

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
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
        self._status = None
        self.username = None
        self.auto_login = True
        self.manager = Manager(accounts_filename)

        # Timers.
        self.check_status_timer = QTimer(self)
        self.check_status_timer.setInterval(5000)
        self.check_status_timer.timeout.connect(self.check_status)

        # Monitor online status.
        self.network_manager = QNetworkConfigurationManager(self)
        self.network_manager.onlineStateChanged.connect(self.
                                                        online_state_changed)
        self.online_state_changed(self.connection_exists())  # Fisrt shot.

    status_changed = pyqtSignal(str)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        old_status = self._status
        self._status = new_status
        if old_status != new_status:
            logging.info('Status changed to %s', new_status)
            self.status_changed.emit(new_status)

    def online_state_changed(self, state):
        """Start/stop timer when the connection changed"""
        if state:
            logging.info('Network is up')
            self.check_status()
            self.check_status_timer.start()
        else:
            logging.info('Network is down')
            self.status = 'NO_CONNECTION'
            self.check_status_timer.stop()

    def check_status(self):
        """Check current status, take actions if needed"""
        # Refuse to do anything when there's no connections.
        if self.status == 'NO_CONNECTION':
            return

        self.update_status()

        # Actions.
        if self.auto_login and self.status == 'OFFLINE':
            self.login()

    def update_status(self):
        """Update current status"""
        logging.info('Updating status')

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

    def connection_exists(self):
        return (len(self.network_manager.
                    allConfigurations(QNetworkConfiguration.Active)) > 0)

if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    worker = Worker()

    sys.exit(app.exec_())
