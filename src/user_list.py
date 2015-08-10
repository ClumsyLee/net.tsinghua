from PyQt5.QtWidgets import QListWidget, QListWidgetItem
import account

class UserList(QListWidget):
    """User list"""
    def __init__(self, parent=None, filename='accounts.yml'):
        super(UserList, self).__init__(parent)
        self.filename = filename
        self.accounts = []

        self.load()

    def __getitem__(self, index):
       return self.accounts[index]

    def save(self):
        account.save(self.accounts, self.filename)

    def load(self):
        self.accounts = account.load(self.filename)
        if len(self.accounts):
            for acc in self.accounts:
                QListWidgetItem(self.account_summary(acc), self)
            self.setCurrentRow(0)  # Select first.

    def add_user(self):
        pass

    def delete_user(self):
        pass

    def account_summary(self, acc):
        return "{}".format(acc.username)
