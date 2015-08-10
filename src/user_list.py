from PyQt5.QtWidgets import QListWidget
import account

class UserList(QListWidget):
    """User list"""
    def __init__(self, parent=None, filename='accounts.yml'):
        super(UserList, self).__init__(parent)
        self.filename = filename
        self.accounts = []

        self.load()

    def save(self):
        account.save(self.accounts, self.filename)

    def load(self):
        self.accounts = account.load(self.filename)

    def add_user(self):
        pass

    def delete_user(self):
        pass
