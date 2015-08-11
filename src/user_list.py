from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
import account

class UserList(QListWidget):
    """User list"""
    def __init__(self, parent=None, filename='accounts.yml'):
        super(UserList, self).__init__(parent)
        self.filename = filename
        self.accounts = []
        self.dirty = False

        self.load()

    dirty_changed = pyqtSignal(bool)

    def __getitem__(self, index):
       return self.accounts[index]

    def set_dirty(self, dirty):
        was_dirty = self.dirty
        self.dirty = dirty
        if was_dirty != dirty:
            self.dirty_changed.emit(dirty)

    def save(self):
        account.save(self.accounts, self.filename)
        self.set_dirty(False)

    def load(self):
        self.accounts = account.load(self.filename)
        if len(self.accounts):
            for acc in self.accounts:
                QListWidgetItem(self.account_summary(acc), self)
            self.setCurrentRow(0)  # Select first.

        self.set_dirty(False)

    def add_account(self, username):
        if not username:  # Not empty.
            return False

        for row, acc in enumerate(self.accounts):  # Not existed.
            if acc.username == username:
                self.setCurrentRow(row)  # Focus on the existed account.
                return False

        acc = account.Account(username, '')
        self.accounts.append(acc)
        QListWidgetItem(self.account_summary(acc), self)
        self.setCurrentRow(len(self.accounts) - 1)  # Select the new account.

        self.set_dirty(True)
        return True

    def delete_account(self):
        row = self.currentRow()
        if row >= 0:
            self.takeItem(row)
            del self.accounts[row]
            self.set_dirty(True)

    def current_account(self):
        row = self.currentRow()
        return self.accounts[row] if row >= 0 else None

    def set_password(self, password, is_md5=False):
        """Set the password of the current account"""
        row = self.currentRow()
        if row >= 0:
            self.accounts[row].set_password(password, is_md5)
            self.set_dirty(True)

    def check(self):
        """Check the current account"""
        row = self.currentRow()
        if row >= 0:
            result = self.accounts[row].check()
            if result:
                self.update_summary()
                self.set_dirty(True)
        else:
            result = False

        return result

    def update_summary(self):
        """Update the summary of the current account"""
        acc = self.current_account()
        if acc:
            new_summary = self.account_summary(acc)
            self.currentItem().setText(new_summary)

    def account_summary(self, acc):
        if acc.valid:
            return ('{username} - {name}\n'
                    '      {balance} 元\n'
                    '      {ipv4_byte} B').format(username=acc.username,
                                                  **acc.infos)
        else:
            return ('{} -\n'
                    '      -\n'
                    '      -').format(acc.username)
