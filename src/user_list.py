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
        new_user = account.Account('', '')
        self.accounts.append(new_user)
        QListWidgetItem(self.account_summary(new_user), self)

        self.setCurrentRow(len(self.accounts) - 1)  # Select the new account.

    def delete_user(self):
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
