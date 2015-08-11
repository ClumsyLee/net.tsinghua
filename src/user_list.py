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
        return True

    def delete_account(self):
        row = self.currentRow()
        if row >= 0:
            self.takeItem(row)
            del self.accounts[row]

    def current_account(self):
        row = self.currentRow()
        return self.accounts[row] if row >= 0 else None

    def update_current_row(self):
        new_summary = self.account_summary(self.current_account())
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
