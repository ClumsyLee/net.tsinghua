from PyQt5.QtCore import QAbstractListModel, Qt, QVariant, QModelIndex
from PyQt5.QtWidgets import QListWidget
import account

class UserListModel(QAbstractListModel):
    """User list model"""
    def __init__(self, parent=None, filename='accounts.yml'):
        super(UserListModel, self).__init__(parent)
        self.filename = filename
        self.accounts = []

        self.load()

    def __getitem__(self, index):
        return self.accounts[index]

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.accounts)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            acc = self.accounts[index.row()]
            return QVariant(self.account_summary(acc))
        else:
            return QVariant()

    def save(self):
        account.save(self.accounts, self.filename)

    def load(self):
        self.accounts = account.load(self.filename)

    def add_user(self):
        pass

    def delete_user(self):
        pass

    def account_summary(self, acc):
        return "{}".format(acc.username)
